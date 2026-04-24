## Medium

**26. Design a continuous training pipeline with automated model promotion.**

Pipeline stages:
1. **Trigger:** New data batch lands in S3/GCS, or drift detected, or scheduled interval.
2. **Data validation:** Great Expectations checks schema, null rates, distribution against a baseline. Fail fast if data quality is below threshold.
3. **Feature engineering:** Run feature computation using Spark or Beam — write to offline store.
4. **Training:** Launch training job (Kubernetes Job, SageMaker Training, Vertex AI). Log all hyperparameters, dataset version, and commit hash to MLflow.
5. **Evaluation:** Compute business metrics (AUC, precision-recall) on a held-out evaluation set. Compare against the production model's last recorded metrics.
6. **Promotion gate:** If the challenger improves by > threshold (e.g., +1% AUC) and passes all data quality checks, automatically register the model in the Model Registry with status `Staging`.
7. **Deploy to staging:** GitOps commit updates the staging environment's model reference. Canary testing runs for 24h.
8. **Production promotion:** Approved via CI gate or auto-approved if canary metrics are clean.

**27. How do you version and manage Jupyter notebooks in a team environment?**

Notebooks are notoriously bad for version control — cell outputs, metadata, and execution order create massive diffs. Solutions:
- **nbstripout:** Git pre-commit hook that strips outputs and metadata before committing. Diffs are clean; outputs are reproduced on execution.
- **Jupytext:** Automatically pairs notebooks with `.py` or `.md` versions using percentage format. Commit the text version; generate the notebook from it.
- **Refactor to modules:** Production logic should live in `.py` modules, not notebooks. Notebooks become thin orchestration layers that call importable functions.

**28. What is Feast and how does it work architecturally?**

Feast is an open-source feature store with two planes:
- **Offline store:** A columnar store (Parquet files, BigQuery, Redshift) containing historical feature values. Used for training data generation with point-in-time correct joins.
- **Online store:** A low-latency key-value store (Redis, DynamoDB) containing the latest feature values for each entity. Used during inference — a single lookup by entity ID returns all features in < 10ms.
- **Materialization:** A job that reads from the offline store and writes the latest values to the online store. Can be scheduled or triggered on feature updates.
- **Feature views:** Define features, their sources, and TTLs in Python. Teams register feature views and share them — a fraud team's `user_transaction_features` is reusable by the risk team.

**29. What is point-in-time correctness in feature stores?**

When building training datasets, each training example must only use feature values that were available at the time of the label — not future values. Without point-in-time joins, you inadvertently include future information, causing label leakage. Feast's `get_historical_features()` performs a time-travel join: for each entity+timestamp in the training dataset, it looks up the feature values from the offline store that were valid at that specific timestamp.

**30. How does the MLflow Model Registry staging workflow operate?**

Models transition through stages: `None` → `Staging` → `Production` → `Archived`. Transitions can be manual (UI, API) or automated (CI/CD pipeline comparing metrics). MLflow 2.x introduced aliases (`@champion`, `@challenger`) replacing stages for more flexible workflow. In practice: the CT pipeline registers a new model version and sets it to `Staging`. A validation job loads the model, runs it against a test set, and if metrics pass, transitions it to `Production`. The serving infrastructure reads the `Production` alias and hot-reloads without downtime.

**31. How do you implement a shadow deployment for a new ML model?**

1. Deploy the challenger model as a separate Kubernetes Deployment with its own Service.
2. In the application or API gateway (Istio, Envoy, Kong), configure traffic mirroring: all production requests are duplicated and sent to the challenger service. The challenger's response is discarded.
3. Log challenger predictions, latency, and errors to a separate metrics namespace.
4. After 24-48 hours, compare challenger metrics against production: accuracy (if labels available), latency percentiles, error rates, prediction distribution.
5. If metrics are acceptable, route 5% live traffic to challenger (canary), monitor, then graduate to full production.

**32. What is PSI and how do you use it for drift detection?**

PSI (Population Stability Index) measures how much the distribution of a variable has shifted between a reference dataset and the current serving data:

```
PSI = Σ (Actual% - Expected%) × ln(Actual% / Expected%)
```

Thresholds: PSI < 0.1 (negligible shift), 0.1–0.2 (moderate, investigate), > 0.2 (significant shift, retrain). PSI is widely used in financial services. Applied per-feature on numeric variables (binned) and categorical variables (per-category). Higher PSI in important features correlates with model degradation.

**33. What is the difference between data drift and concept drift?**

- **Data drift (covariate shift):** P(X) changes — input feature distributions shift (seasonal patterns, demographic shifts, new product categories). Detected by comparing feature distributions between reference and current windows without needing labels.
- **Concept drift:** P(Y|X) changes — the underlying relationship between features and target changes (fraud patterns evolve, user behavior changes). Only detectable when ground truth labels are available, which may be days or weeks delayed (feedback delay problem).

**34. How do you handle the delayed label problem in production ML monitoring?**

For many problems, ground truth labels arrive days or weeks after prediction (loan default, churn). Strategies:
1. **Proxy metrics:** Monitor model output distribution shifts as early warning signals (if the model suddenly predicts more fraudulent transactions, investigate even before labels arrive).
2. **Early feedback sampling:** For slow-feedback labels, collect a random sample of predictions and expedite human labeling.
3. **Delayed evaluation pipeline:** Set up a pipeline that joins predictions with labels as they arrive and continuously updates AUC/precision-recall metrics in a dashboard.
4. **Segment by cohort:** Track performance by prediction cohort date so you can compare day-30 metrics across cohorts.

**35. How do you integrate Evidently AI for ML monitoring?**

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset

report = Report(metrics=[DataDriftPreset(), ClassificationPreset()])
report.run(reference_data=training_df, current_data=production_df)
report.save_html("drift_report.html")
```

Evidently generates drift reports comparing reference and current data. Integrate into the pipeline: run the report daily on a rolling window of serving data against the training baseline. Extract JSON metrics to push to Grafana. Set alert thresholds: if `dataset_drift` is True or drift share > 50%, trigger a retraining pipeline and create a Jira ticket.

**36. What is GPU MIG and when do you use it?**

MIG (Multi-Instance GPU) partitions an A100 or H100 into isolated, fixed-size GPU slices (e.g., 7x 1g.10gb instances from one A100). Each slice has dedicated compute, memory, and cache — fully isolated. Use MIG when: running multiple small inference workloads on a single GPU (each model gets a dedicated slice, preventing noisy neighbor issues), or for multi-tenant inference platforms where isolation is required. Exposed to Kubernetes via the NVIDIA device plugin with `nvidia.com/mig-1g.10gb` resource type.

**37. How does KEDA enable autoscaling for ML inference workloads?**

KEDA (Kubernetes Event-Driven Autoscaler) scales pods based on external metrics beyond CPU/memory. For ML inference: configure a KEDA `ScaledObject` targeting an inference deployment with triggers from:
- **Queue length:** Scale up model serving pods when SQS/RabbitMQ queue depth exceeds a threshold (batch inference).
- **Prometheus:** Scale based on `requests_per_second` or `p99_latency_seconds` scraped from the inference server.
- **Cron:** Scale to zero during off-hours for non-production inference endpoints.

KEDA handles scaling from zero (no cost when idle) to many replicas without modifying the Kubernetes HPA.

**38. How do you optimize inference latency for a deep learning model?**

Multi-lever approach:
1. **Quantization:** Convert FP32 weights to INT8 or FP16 using TensorRT or PyTorch's `torch.quantization`. 2-4x speedup with minimal accuracy loss.
2. **Dynamic batching:** Batch multiple concurrent requests together (Triton Inference Server's dynamic batching). Amortizes memory transfers across requests.
3. **TensorRT compilation:** Compile the model graph to optimized CUDA kernels for the specific GPU hardware.
4. **KV cache tuning:** For LLMs, tune the KV cache size and use paged attention (vLLM) to maximize throughput.
5. **Hardware:** Move from T4 to A10G for general inference; A100/H100 for large models with tensor parallelism.
6. **Model distillation:** Train a smaller student model to mimic the teacher model's outputs — smaller model, lower latency.

**39. What are the three distributed training paradigms?**

- **Data parallelism:** Each worker holds the full model; data is split across workers. Gradients are synchronized via all-reduce (NCCL). Simple, scales well for models that fit on one GPU.
- **Tensor parallelism:** A single layer's weight matrix is split across multiple GPUs (each GPU computes part of the matrix multiply). Used when a single layer is too large for one GPU's memory.
- **Pipeline parallelism:** Different model layers run on different GPUs in a pipeline fashion. GPU 1 runs layers 1-12; GPU 2 runs layers 13-24. Micro-batching reduces pipeline bubble time.

Most large model training combines all three (3D parallelism).

**40. How do you implement RBAC for ML artifacts?**

In MLflow with an enterprise auth layer (or Databricks Unity Catalog): define groups (`data-scientists`, `ml-engineers`, `model-approvers`). Apply permissions:
- `data-scientists`: Can create experiments, log runs, register models to `None` stage.
- `ml-engineers`: Can transition models to `Staging`, read all experiments.
- `model-approvers`: Can transition models to `Production` or `Archived`.

In feature stores (Feast, Tecton): apply row-level access control so a team can only read their own feature views. Apply namespace-level Kubernetes RBAC to ML serving namespaces so only CI/CD service accounts can update InferenceServices.

**41. What is model bias and how do you detect and mitigate it?**

Model bias is systematic unfairness in predictions across demographic groups. Detection: compute fairness metrics (demographic parity, equalized odds, disparate impact) separately for each subgroup using libraries like Fairlearn or AIF360. If error rates differ significantly by race, gender, or age, the model is biased.

Mitigation:
- **Pre-processing:** Re-sample or re-weight training data to balance representation.
- **In-processing:** Add fairness constraints to the training objective.
- **Post-processing:** Adjust decision thresholds per group to equalize error rates.

Fairness constraints often trade off accuracy — document the tradeoff explicitly in the model card.

**42. What is an ML-BOM and how does it differ from a software SBOM?**

An ML-BOM (Machine Learning Bill of Materials) extends the software SBOM concept to ML artifacts. A software SBOM lists code dependencies and their CVEs. An ML-BOM additionally captures: training datasets (name, version, hash, license), pretrained base models used (origin, version), preprocessing code, feature engineering logic, and evaluation datasets. ML-BOMs are required for ML systems in regulated industries (financial services, healthcare) to enable auditability of predictions and compliance with model risk management guidelines (SR 11-7, EU AI Act).

**43. How do you handle GDPR compliance in an ML system?**

1. **Data minimization:** Only collect and store features necessary for the model. PII fields not needed for prediction should not be ingested.
2. **Purpose limitation:** Document in the model card that data is only used for the declared purpose.
3. **Right to erasure:** Implement a subject erasure pipeline — when a user requests deletion, remove their records from training datasets, retrain or verify that the model is not memorizing their data, and delete their features from the feature store.
4. **Right to explanation:** For automated decisions, provide SHAP-based explanations of what features drove the prediction.
5. **Data residency:** Ensure training data for EU residents never leaves EU regions. Use region-locked storage and training compute.

---


---

**44. How do you implement a model promotion gate in a CI/CD pipeline?**

A promotion gate is an automated check that blocks a model from advancing to production unless it clears quantitative thresholds:

```python
# evaluation_gate.py — run after training, before registry promotion
import mlflow

client = mlflow.MlflowClient()
run = client.get_run(run_id)

challenger_auc = float(run.data.metrics["auc_val"])
challenger_psi  = float(run.data.metrics["psi_max"])

# Load champion's last recorded metric
champion = client.get_model_version_by_alias("fraud-detector", "champion")
champion_auc = float(client.get_run(champion.run_id).data.metrics["auc_val"])

# Gate conditions
assert challenger_auc >= champion_auc - 0.005, "AUC regression > 0.5%"
assert challenger_psi < 0.2, "Input drift too high — feature pipeline suspect"
assert challenger_auc >= 0.88, "Below absolute minimum AUC"

# Promote
client.set_registered_model_alias("fraud-detector", "challenger", run.info.run_id)
```

In the CI pipeline: if `evaluation_gate.py` exits non-zero, the promotion step is skipped and the champion continues serving. Alert the ML team via Slack/PagerDuty.

**45. How do you handle model cold start latency in a Kubernetes serving environment?**

Cold start occurs when a pod starts and must download + load model weights before serving traffic. For large models (2-70 GB), this can take minutes.

Mitigation strategies:
1. **Pre-pull images**: DaemonSet to pull the inference container image on all GPU nodes before a rollout
2. **Warm pool**: Keep a minimum replica count > 0 (never scale to zero for latency-critical models)
3. **Init containers**: Download model weights from S3 into a shared `emptyDir` volume before the serving container starts — model loading and network download happen in parallel with cluster scheduling
4. **Model caching on node**: Use a persistent volume or node-local cache so weights survive pod restarts on the same node
5. **KServe storage initializer**: Runs as an init container, downloads weights from S3/GCS before the predictor starts

```yaml
spec:
  initContainers:
  - name: model-downloader
    image: amazon/aws-cli
    command: ["aws", "s3", "cp", "s3://models/fraud/v12/", "/mnt/model/", "--recursive"]
    volumeMounts:
    - mountPath: /mnt/model
      name: model-cache
  containers:
  - name: predictor
    volumeMounts:
    - mountPath: /mnt/model
      name: model-cache
```

**46. What is the difference between online evaluation and offline evaluation for ML models?**

| | Offline Evaluation | Online Evaluation |
|---|---|---|
| Data | Held-out test set from historical data | Live production traffic |
| Labels | Available immediately | May be delayed (days/weeks) |
| Speed | Fast (minutes) | Slow (requires observation period) |
| Signal | Measures model quality on a snapshot | Measures real-world business impact |
| Limitation | Test set may not match production distribution | Requires A/B infrastructure |
| Tools | sklearn metrics, RAGAS | Evidently, Prometheus, A/B framework |

Offline: AUC, F1, RMSE on test set. Online: business KPIs (click-through, conversion, fraud catch rate) on live traffic. Both are required — offline catches regressions before deployment; online validates that offline improvements translate to real-world value.

**47. How do you implement safe model rollback in a production ML system?**

```python
# GitOps-style: serving config stored in Git
# Rollback = revert the serving config commit

# Step 1: identify champion alias in registry
client = mlflow.MlflowClient()
champion = client.get_model_version_by_alias("fraud-detector", "champion")

# Step 2: check what's serving
current_serving_version = get_deployment_model_version("fraud-detector-svc")

if current_serving_version != champion.version:
    # Step 3: revert deployment config
    patch_kserve_isvc("fraud-detector", model_uri=champion.source)
    # Step 4: record the rollback event
    client.set_tag(champion.run_id, "rollback_at", datetime.utcnow().isoformat())
    notify_oncall("Rolled back fraud-detector to v" + champion.version)
```

Rollback checklist:
- Does the previous model version's artifact still exist in S3? (verify before initiating rollback)
- Are the previous version's features still materialized in the online store?
- Is the rollback captured as a registry event for the audit trail?
- Does the rollback update the canary traffic split back to 100/0?

**48. What is the difference between Kubeflow Pipelines and Apache Airflow for ML workflows?**

| | Kubeflow Pipelines (KFP) | Apache Airflow |
|---|---|---|
| Native ML support | First-class (artifacts, lineage, component caching) | Generic DAG — no native ML concepts |
| Execution model | Each step = Kubernetes pod (isolated, reproducible) | Tasks run on workers (shared environment) |
| Artifact tracking | Built-in (MLMD) | External (MLflow, S3) |
| Caching | Automatic component output caching | No built-in caching |
| Learning curve | Steeper (Kubernetes) | Lower (Python DAGs) |
| Best for | ML training + evaluation + promotion pipelines | Data engineering, ETL, scheduling |

Use KFP when: the pipeline produces ML artifacts, you need reproducibility, or you're already on Kubernetes. Use Airflow when: the pipeline is mostly data transformation, you need rich scheduling, or the team is unfamiliar with Kubernetes.

**49. How do you design a feature pipeline for low-latency online serving?**

Requirements: feature lookup at inference time must be < 10ms P99.

Architecture:
```
Batch/streaming source (Kafka, BigQuery)
           │
     Feature computation (Spark / Flink)
           │
    Offline store (Parquet/Delta Lake)   ──► Training
           │
    Materialization job (Feast / Tecton)
           │
    Online store (Redis / DynamoDB)      ──► Inference API
```

Design decisions for low latency:
- **Redis Cluster**: Use Redis with read replicas in the same AZ as inference pods. Pipeline multiple feature lookups in a single MGET/HGETALL call.
- **Entity encoding**: Encode entity IDs as compact binary keys. Avoid string concatenation at request time.
- **Feature pre-computation**: Compute expensive aggregates (7-day rolling counts) in batch; serve pre-computed values, not real-time computation.
- **TTL**: Set per-feature TTL matching the feature's natural staleness (e.g., session features: 30 minutes; user demographics: 7 days). Stale features are better than slow features for most use cases.
- **Connection pooling**: Reuse Redis connections across requests. Each cold connection adds 2-5ms.

**50. How do you monitor prediction confidence in production?**

Confidence monitoring detects silent model failures — the model serves a prediction but is uncertain.

```python
# Log confidence distribution metrics
from prometheus_client import Histogram

CONFIDENCE_HISTOGRAM = Histogram(
    "model_prediction_confidence",
    "Distribution of model output confidence",
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

def predict(request):
    proba = model.predict_proba(request.features)
    confidence = proba.max(axis=1)
    CONFIDENCE_HISTOGRAM.observe(confidence[0])

    if confidence[0] < CONFIDENCE_THRESHOLD:
        # Route to human review or fallback model
        return fallback_predict(request)
    return {"label": proba.argmax(), "confidence": float(confidence[0])}
```

Alert on:
- Median confidence drops > 10% from baseline (model uncertain about typical inputs)
- P5 confidence drops near 0.5 (model essentially random for some inputs)
- Confidence distribution bimodal shift (model highly confident but wrong — indicates distribution shift)

**51. What is Continuous Training (CT) and how do you decide when to trigger it?**

CT is the automated pipeline that detects a retraining signal, retrains the model, evaluates it, and promotes it if it passes gates — without human intervention.

Trigger conditions (choose based on business context):

| Trigger | Condition | When to Use |
|---------|-----------|-------------|
| Schedule | Weekly/daily cron | Slowly evolving data, low label delay |
| Data volume | New data batch > N rows | High-volume systems with fresh labels |
| Drift threshold | PSI > 0.2 on key feature | Rapid covariate shift |
| Performance degradation | Rolling AUC drops > X% | When labels are available with short delay |
| Business KPI | CTR drops > Y% week-over-week | When business signal is the most reliable |

Avoid triggering CT on every data update — it wastes compute and can cause instability if new data is temporarily corrupted. Set a minimum training frequency (e.g., no more than once per day) and a minimum data volume requirement.

