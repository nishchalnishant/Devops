# MLOps Interview Questions (Medium)

These questions focus on practical MLOps design, delivery, observability, and platform operations.

## ML Pipelines & Reproducibility

**1. How would you design a basic MLOps pipeline from data to deployment?**

I would separate the flow into data validation, feature preparation, training, evaluation, model registration, approval, deployment, and monitoring. I would also capture lineage across code, data version, model artifact, and environment.

**2. How do you make a training run reproducible?**

Version the code, training data, feature definitions, hyperparameters, environment, and final model artifact. Without all of those, you can reproduce only part of the run.

**3. How do you decide when a model is ready for promotion from staging to production?**

I would require offline evaluation thresholds, validation checks, lineage completeness, and a deployment strategy such as shadow or canary. The decision should include both technical and business metrics.

**4. What is the role of CI in MLOps if the model is trained later?**

CI still validates the code, tests feature transformations, checks schemas, runs quality gates, and ensures pipeline definitions are valid. It reduces the chance of broken training or serving logic before retraining happens.

**5. What triggers a continuous training pipeline?**

Typical triggers include a schedule, new data arrival, detected drift, business KPI degradation, or a manual approval from a model owner.

**6. How do you implement a Continuous Training (CT) pipeline with automated promotion?**

CT pipeline stages:
1. **Trigger:** New data batch arrives in S3 (event-driven via S3 notification → Lambda/EventBridge → pipeline trigger) OR scheduled cron, OR detected data drift above threshold.
2. **Data validation:** Great Expectations checks schema, null rates, and statistical properties of the new training data. Fail the pipeline if validation fails.
3. **Feature engineering:** Extract and transform features (or materialize via Feature Store).
4. **Training:** Submit training job to Kubernetes (Kubeflow Training Operator, Argo Workflows, or SageMaker). Log all params/metrics to MLflow.
5. **Evaluation:** Compare challenger model metrics against current production champion on a held-out evaluation set. If challenger is worse, abort.
6. **Validation gates:** Human review for high-risk models, automated A/B test setup, bias evaluation (Fairlearn), security scan (adversarial robustness check).
7. **Promotion:** Update model registry: `mlflow models transition-model-version-stage --name fraud_model --version 12 --stage Production`. Update serving config in GitOps repo (ArgoCD deploys new serving configuration pointing to model version 12).

**7. How do you version control a Jupyter Notebook in a team setting?**

Options from worst to best:
- **Git raw nbformat:** Works but diffs are JSON noise (output cells, execution counts). Barely acceptable for solo work.
- **nbstripout:** Pre-commit hook that strips outputs before committing. Cleaner diffs but loses output history.
- **Jupytext:** Syncs notebooks to light Python scripts (`.py`) or MyST markdown in parallel. The `.py` file is committed — clean diffs, proper code review. Notebook is regenerated from the script.
- **Promote to modules:** For production-bound code, extract functions into proper Python modules. Notebook becomes a thin orchestration wrapper that imports from `src/`. The modules are tested, versioned, and reusable.

## Data & Feature Engineering

**8. How do you prevent training-serving skew?**

Use shared feature definitions, a feature store, or a common transformation library for both training and inference. I also validate example payloads and compare offline and online feature distributions.

**9. When is a feature store worth introducing?**

A feature store is useful when multiple models share features, online and offline consistency matters, or teams are repeatedly rebuilding the same feature logic.

**10. How do you handle schema changes in upstream data sources?**

I add schema validation, contract checks, and backward-compatible evolution rules. Breaking changes should fail fast before they poison training or live inference.

**11. How do you validate data quality before training?**

I would check schema, null rates, range violations, cardinality changes, duplicates, freshness, and label availability. Data validation should be a gated pipeline step, not a manual afterthought.

**12. How do you deal with stale features in an online prediction system?**

I would monitor feature freshness, timestamp lag, cache behavior, and fallback logic. Some systems should fail closed, while others may need a degraded-mode prediction path.

**13. How do you handle experiment reproducibility in a team environment?**

Reproducibility requires controlling all sources of randomness and versioning all inputs:
- **Code:** Git commit SHA is logged with every training run.
- **Data:** DVC data version or dataset snapshot S3 path with version ID is logged.
- **Environment:** Docker image SHA or conda environment YAML is locked and logged.
- **Random seeds:** Set `torch.manual_seed`, `numpy.random.seed`, `random.seed` explicitly and log the seed value.
- **Hyperparameters:** All training configurations logged to MLflow/W&B as run parameters.
- **Hardware determinism:** NVIDIA's `CUBLAS_WORKSPACE_CONFIG=:4096:8` and `torch.use_deterministic_algorithms(True)` for reproducible GPU operations (at some performance cost).

## Feast (Feature Store)

**14. Walk through the architecture of Feast as a Feature Store.**

Feast has four main components:
- **Feature Repository:** A Git repo containing Python feature definitions (`FeatureView`, `Entity`, `FeatureService`) that declare what data to materialize and how to serve it.
- **Offline Store:** A data warehouse (BigQuery, Snowflake, Redshift, Spark) that stores historical feature values. Used for generating training datasets via point-in-time correct joins.
- **Online Store:** A low-latency key-value store (Redis, DynamoDB, Bigtable) storing the latest feature values per entity. Used at serving time for real-time lookups.
- **Materialization:** `feast materialize` runs batch jobs that extract recent feature values from the offline store and push them to the online store, keeping online features fresh.

**15. What is point-in-time correctness in feature serving and why is it critical?**

Point-in-time correctness ensures that when generating a training dataset, the feature values used for each training example reflect what was available at the timestamp of that example — not future data. Without it, you get data leakage: the model trains on features that include information from after the event it is predicting. Example: predicting loan default using a customer's credit score as of the application date, not today's credit score. Feast achieves this with `get_historical_features()` which performs point-in-time joins against the offline store.

**16. How do you handle feature freshness requirements that differ across models?**

Different models have different freshness SLAs:
- A fraud detection model may need features updated every 5 minutes (near-real-time).
- A recommendation model may be fine with daily features.

Feature freshness is configured in the `FeatureView` definition with a `ttl` (time-to-live). Real-time features use a streaming ingestion pipeline (Kafka → Flink/Spark Streaming → Online Store) rather than batch materialization. Monitoring: alert when the latest feature timestamp in the online store exceeds the model's declared `ttl`, as stale features can cause silent model degradation.

**17. What is a Feature Service and why is it useful?**

A Feature Service groups a set of features from multiple `FeatureView`s into a named, versioned artifact that a model consumes. Example: `checkout_model_v2` Feature Service combines `user_features`, `session_features`, and `item_features` views. Benefits: (1) the model's feature dependencies are explicit and version-controlled, (2) the serving layer knows exactly which features to retrieve for a given model without the serving code needing to know feature view internals, (3) you can compare which Feature Service version a model was trained on vs. what it is served at inference time.

**18. How do you prevent feature drift between training and serving in a Feature Store?**

Key controls:
- **Single transformation logic:** All feature transformations are defined once in the Feature Store's transformation layer (using `OnDemandFeatureView` in Feast or feature transforms in Tecton) — the same code path runs during training data generation and online serving.
- **Feature statistics logging:** Log the distribution of features served online and compare daily against training distribution baselines using KL divergence or PSI (Population Stability Index).
- **Schema validation:** Use Great Expectations or Deequ to validate that incoming raw data matches expected schema, range, and null rate before materialization.
- **Parity tests:** Run the model on a held-out set using both training-time feature extraction and online serving feature extraction; compare predictions — divergence indicates skew.

## MLflow

**19. What is MLflow Model Registry and how does it support staging workflows?**

MLflow Model Registry provides:
- **Versioning:** Each time a model is logged and registered, it gets an auto-incremented version number.
- **Stage transitions:** Versions move through: `None → Staging → Production → Archived`. Transitions can require approvals via webhooks.
- **Aliases (MLflow 2.x):** Named pointers to versions (e.g., `champion` → version 12, `challenger` → version 13) that decouple serving configuration from version numbers.
- **Webhooks:** Trigger downstream actions on stage transitions (e.g., when a version moves to Production, trigger a GitOps PR updating the serving configuration's model URI).

**20. How do you handle model rollback in a production MLOps platform?**

Rollback procedure:
1. **Detection:** Monitoring alert fires (error rate increase, prediction distribution shift, business KPI degradation).
2. **Decision:** On-call confirms rollback is needed. Check if the previous champion model is still available in the registry and serving infrastructure.
3. **Execution:** Update serving config to point to the previous model version URI (MLflow registry path or S3 path). In GitOps: open a hotfix PR updating `model-serving/values.yaml` with the previous model version, merge, ArgoCD deploys within seconds.
4. **Verification:** Confirm prediction distribution returns to baseline. Check that error rate normalizes.
5. **Post-mortem:** Investigate what caused the new model to fail — evaluation gap? Data issue? Feature distribution change? Update the validation gate to catch the issue in future promotions.

## Model Serving & Deployment

**21. When would you choose batch inference instead of online inference?**

Use batch inference when latency is not user-facing and throughput or cost efficiency matters more than real-time response, such as nightly scoring or scheduled recommendations.

**22. When is async inference the right design?**

Async inference is useful when the request takes too long for a synchronous API but still needs a request-response workflow through queues, callbacks, or status polling.

**23. How do you deploy a new model safely?**

I prefer a rollout path such as shadow, canary, or champion-challenger. The model should promote only after both serving health and prediction-quality signals look acceptable.

**24. How do you choose between KServe, Triton, and a custom API container?**

I choose based on model framework support, scaling needs, batching needs, GPU use, routing complexity, and the team's operational maturity. The best tool depends on whether the main problem is standardized serving, high-performance inference, or custom business logic.

**25. Why might a custom serving container still be necessary even with a model-serving framework?**

Some use cases need custom preprocessing, postprocessing, feature lookups, or business-specific routing that off-the-shelf serving frameworks do not handle cleanly.

**26. How do you design a shadow deployment for ML model evaluation?**

Shadow (mirror) deployment architecture:
1. A traffic-splitting layer (Istio VirtualService, Nginx, or Envoy) receives all production requests.
2. 100% of requests are served by the production model (responses returned to users normally).
3. Simultaneously, a copy of each request is sent to the shadow model (the new version). Shadow model responses are logged but NOT returned to users.
4. A comparison job periodically queries both logs and computes: prediction agreement rate, distribution similarity, latency comparison, and identifies specific cases where predictions differ.
5. Based on shadow results, decide whether to proceed with canary or A/B test. No user impact — the shadow model can fail without affecting production.

## Observability & Monitoring

**27. How do you monitor drift when labels arrive hours or days later?**

I use proxy metrics such as confidence shifts, output distribution changes, feature distribution drift, and business KPI proxies until labeled feedback becomes available.

**28. What metrics would you put on a dashboard for a production inference service?**

Latency, throughput, error rate, autoscaling state, model version, feature freshness, confidence distribution, drift metrics, and a business KPI such as conversion or fraud catch rate.

**29. How do you know whether a bad result comes from the model or the platform?**

I first separate serving health from prediction correctness. If the endpoint is healthy, I validate payload schema, feature generation, model version, and drift before blaming compute or networking.

**30. Why are business metrics important in MLOps monitoring?**

Because a model can be technically available and still damage outcomes such as revenue, fraud detection, approval quality, or user engagement.

**31. How do you reduce alert fatigue in MLOps systems?**

I avoid paging on every metric anomaly. I separate infrastructure alerts from model-quality alerts, route them to the right owners, and page only on user-impacting or policy-impacting conditions.

**32. What is Population Stability Index (PSI) and how do you use it to detect drift?**

PSI measures how much a variable's distribution has shifted between two datasets (training vs. current production). Calculation: divide the distribution into bins, compute the proportion in each bin for both datasets, then sum `(P_new - P_old) × ln(P_new / P_old)` across bins. Interpretation: PSI < 0.1 = negligible drift (monitor only), 0.1–0.25 = moderate drift (investigate), >0.25 = major shift (retrain likely needed). PSI is widely used in financial ML for regulatory monitoring of scorecard models.

**33. What is the difference between data drift and concept drift?**

- **Data drift (covariate shift):** The distribution of input features `P(X)` changes but the relationship between inputs and outputs `P(Y|X)` remains the same. Example: the age distribution of users shifts because the product acquired an older demographic. The model still correctly predicts behavior for a given age — but the mix of ages being served has changed.
- **Concept drift:** The relationship `P(Y|X)` changes — the same inputs now lead to different outcomes. Example: user purchasing behavior for a given product category changes due to economic conditions. The model's predictions become systematically wrong even for inputs with unchanged feature values. Concept drift requires retraining; data drift may only require recalibration or feature distribution adjustment.

**34. What is the delayed label problem and how do you handle it?**

Delayed labels occur when ground truth feedback for a prediction arrives long after the prediction is made. Example: a model predicts whether a loan will default — the outcome is known only after 12 months. Strategies:
- **Proxy metrics:** Use early signals correlated with the outcome (30-day delinquency as a proxy for 12-month default).
- **Cohort analysis:** Track prediction cohorts and compute accuracy as labels arrive for each cohort.
- **Input data drift monitoring:** Monitor whether the input feature distribution has drifted from training as a leading indicator of model degradation.

## Evidently AI

**35. What is Evidently AI and how do you integrate it into an ML monitoring pipeline?**

Evidently AI is an open-source library for ML model and data monitoring. It generates reports and test suites comparing a reference dataset (training or baseline) against a current dataset (recent production data). Integration:
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset

report = Report(metrics=[DataDriftPreset(), ClassificationPreset()])
report.run(reference_data=train_df, current_data=production_df)
report.save_html("monitoring_report.html")
```
In a production pipeline, run Evidently as a scheduled Airflow/Kubeflow task, save JSON results, and post metrics to Prometheus (via a custom exporter) so Grafana alerts fire when drift thresholds are exceeded.

**36. How do you implement a model monitoring dashboard in Grafana for ML workloads?**

Architecture:
1. **Metrics source:** A custom Prometheus exporter running alongside the model server that computes and exposes metrics: prediction count, prediction distribution (histograms by class or value buckets), feature statistics (mean, P50, P95 per feature), latency, and error rate.
2. **Drift metrics:** A scheduled job (Airflow/cron) runs Evidently AI comparisons and writes PSI and KL divergence scores to a Prometheus Pushgateway.
3. **Grafana panels:** Prediction volume over time, prediction distribution heatmap, feature drift PSI per feature (with color-coded thresholds), model latency P50/P95/P99, error rate, and an "alerts" panel showing active Prometheus alerts.
4. **Alerting:** Prometheus rules fire when: PSI > 0.25 for any feature, prediction error rate > 2%, P99 latency > 500ms. Routes to PagerDuty for production models.

## Kubernetes & GPU Management

**37. How do you manage GPU workloads in Kubernetes efficiently?**

Use node pools dedicated to GPU workloads, device plugins, taints and tolerations, proper resource requests, and autoscaling policies that respect cost and startup time.

**38. Why is checkpointing important for long-running training jobs?**

Because training jobs may be interrupted by failures or spot instance eviction. Checkpoints allow resuming progress instead of restarting from zero.

**39. How do you decide between CPU and GPU inference?**

I compare latency targets, model size, throughput needs, and cost. Some lighter models run cheaply and well on CPU, while larger deep-learning models need GPU for acceptable latency.

**40. What does model batching trade off in inference?**

Batching can improve throughput and GPU efficiency, but it may increase individual request latency if not tuned carefully.

**41. How do you prevent expensive GPU nodes from running ordinary workloads?**

Use taints, tolerations, node selectors, quotas, and admission rules so only approved ML workloads can consume GPU capacity.

**42. How do you schedule GPU jobs in Kubernetes with resource isolation?**

GPU allocation in Kubernetes:
- **Device Plugin:** NVIDIA device plugin (`k8s-device-plugin`) runs as a DaemonSet on GPU nodes and exposes `nvidia.com/gpu` as an extended resource.
- **Resource requests:** Pods request GPUs via `resources.limits: nvidia.com/gpu: 1` — Kubernetes ensures only one pod receives a given physical GPU.
- **Node taints:** GPU nodes have `taint: nvidia.com/gpu=true:NoSchedule` — only pods with the matching toleration are scheduled there.
- **MIG (Multi-Instance GPU):** NVIDIA A100/H100 supports partitioning one physical GPU into isolated slices (e.g., `1g.5gb`, `3g.20gb`). Each slice has dedicated memory and compute, enabling multi-tenant GPU sharing with hardware isolation.
- **Time-slicing:** For development workloads, the GPU can be time-sliced to allow multiple pods to share a GPU without memory isolation.

**43. What is KEDA and how does it help ML inference workloads?**

KEDA (Kubernetes Event-Driven Autoscaler) scales Kubernetes workloads based on external event metrics beyond CPU/memory. For ML inference:
- Scale model serving pods based on message queue depth (requests waiting in SQS, Kafka, RabbitMQ) — when a batch of inference requests arrives, KEDA scales pods immediately rather than waiting for CPU% to rise.
- Scale GPU training jobs from 0 to N based on a training queue (e.g., `pending_training_jobs > 0` triggers scaling from zero).
- Scale-to-zero for development/staging model servers during off-hours to eliminate GPU cost.

**44. How do you optimize inference latency for a large transformer model?**

Layered optimization approach:
1. **Quantization:** Convert FP32 weights to INT8 or FP16 — reduces memory bandwidth pressure, often 2x speedup with <1% accuracy loss on most tasks.
2. **Batching:** Serve multiple requests together in one forward pass — GPU utilization increases dramatically. Dynamic batching (TensorRT, Triton) groups requests arriving within a latency window.
3. **Model compilation:** TorchScript, ONNX Runtime, or TensorRT compilation optimizes the computation graph for the target hardware.
4. **KV cache:** For transformer decoding, cache key-value pairs from previous tokens to avoid recomputation.
5. **Speculative decoding:** Use a small draft model to propose tokens; the large model verifies multiple tokens in parallel — 2-3x throughput improvement for autoregressive generation.
6. **Hardware:** Use instances with NVLink for multi-GPU serving, maximize GPU memory with the largest available GPU per model.

**45. What is distributed training and when do you need it?**

Distributed training splits model training across multiple GPUs or nodes. You need it when: the model is too large to fit in one GPU's memory, or the training data is so large that single-GPU training would take weeks. Two primary paradigms:
- **Data parallelism:** Each GPU holds a full copy of the model and processes a different mini-batch. Gradients are synchronized (AllReduce) across GPUs after each step. Works well when the model fits in one GPU. Framework: PyTorch DDP, Horovod.
- **Model parallelism (tensor/pipeline):** The model itself is split across GPUs because it's too large for one. Tensor parallelism splits individual layers across GPUs (Megatron-LM). Pipeline parallelism stages the model layers across GPUs with micro-batching to overlap computation.

## Security, Governance & Compliance

**46. How do you secure model and dataset access in an MLOps platform?**

Use role-based access, short-lived credentials, audit trails, and separate permissions for data access, model promotion, and production deployment.

**47. What should be reviewed before approving a model for production in a regulated environment?**

Lineage, evaluation results, data source approval, explainability needs, monitoring plan, rollback path, and who approved the release.

**48. How do you handle secrets in training and inference pipelines?**

Never hardcode them in notebooks or pipeline code. Use a secret manager or platform-native secret store with role-based access and auditability.

**49. Why does MLOps need stronger lineage than many traditional applications?**

Because model behavior depends on data and experiments, not just code. When something goes wrong, you need to trace the exact training inputs and promotion path.

**50. How do you implement role-based access control for ML artifacts?**

RBAC for ML artifacts requires protecting: experiment data, training datasets, model weights, and inference logs. Implementation:
- **MLflow:** Configure MLflow server with OIDC authentication. Use group-based permissions: data scientists have `read/write` on experiments in their team namespace; only MLOps engineers have `edit` on Production stage transitions.
- **S3/Azure Blob:** IAM policies restrict dataset bucket access by role. Training accounts have write access; serving accounts have read-only access to model artifact buckets.
- **Model Registry:** Tag-based access in SageMaker Model Registry or MLflow with policy enforcement.
- **Audit logging:** Every model version transition, dataset access, and serving config change is logged with actor identity and timestamp for compliance.

**51. What is a data lineage graph and what tools generate it?**

A data lineage graph tracks the complete provenance of a dataset or model: which raw sources were used, what transformations were applied, which intermediate datasets were produced, and which models were trained on which dataset versions. Tools: OpenLineage (open standard for lineage events), Marquez (OpenLineage server and UI), Apache Atlas, dbt Lineage. In MLOps, lineage connects: raw data source → feature pipeline → training dataset → model version → serving endpoint.

**52. How do you ensure GDPR compliance in an ML training pipeline?**

Key requirements and technical controls:
- **Right to erasure:** Implement a data erasure pipeline that removes user records from all training datasets and raw storage on deletion request. If the model was trained on their data, schedule a retrain after the erasure batch completes. Log the erasure event with a timestamp for audit.
- **Data minimization:** Feature engineering pipelines drop PII columns before storing in the Feature Store or training datasets.
- **Consent tracking:** Training data is tagged with consent scope. Pipelines validate that training data consent scope includes the model's use case before ingesting.
- **Encryption at rest and transit:** All datasets and model artifacts encrypted. Access logs maintained.

**53. What is model bias and how do you detect and mitigate it?**

Model bias occurs when a model produces systematically unfair outcomes for specific demographic groups. Detection:
- **Fairness metrics:** Measure disparate impact (ratio of favorable outcome rates between groups should be >0.8), equalized odds (true positive rate and false positive rate equal across groups), demographic parity.
- **Sliced evaluation:** Compute accuracy, precision, and recall separately for each demographic slice using Fairlearn or What-If Tool.

Mitigation:
- **Pre-processing:** Re-sample training data to balance representation, or apply reweighting to underrepresented groups.
- **In-processing:** Fairness-constrained training (add fairness regularization terms to the loss function).
- **Post-processing:** Calibrate prediction thresholds separately per group to equalize false positive rates.

**54. What is an ML Bill of Materials (ML-BOM) and how does it differ from a software SBOM?**

A standard SBOM lists software packages and their versions. An ML-BOM extends this to capture ML-specific inputs: training data version and source, feature engineering code version, pre-trained model or foundation model used (with version), hyperparameters, evaluation dataset, and known limitations. The ML-BOM is critical for supply chain security, regulatory audits, and reproducibility. Tools: ML Metadata (MLMD, part of TFX), MLflow run artifacts, custom registry metadata schemas.

## Infrastructure & Platform

**55. How would you integrate Terraform into an MLOps platform?**

I would use Terraform to provision the infrastructure layer such as networks, clusters, storage, IAM, and registries, while model-specific delivery happens through pipelines and serving frameworks.
