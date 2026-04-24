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

