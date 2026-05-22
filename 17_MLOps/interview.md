# MLOps — Interview Prep

```
MLOps — Easy Interview Topics
├── MLOps Foundations
│   ├── Definition: DevOps principles applied to ML lifecycle
│   ├── Goal: reliable, reproducible, continuously deliverable ML systems
│   └── Key difference from DevOps: data + model are additional artifacts
├── Training vs Inference
│   ├── Training: batch, GPU-intensive, produces model artifact
│   └── Inference: real-time or batch, latency-critical, serves predictions
├── Reproducibility
│   ├── Pin library versions (requirements.txt, conda env)
│   ├── Version training data (DVC, Delta Lake snapshots)
│   ├── Log hyperparameters + random seeds in experiment tracker
│   └── Store commit hash with every training run
├── Experiment Tracking (MLflow)
│   ├── Log: params, metrics, artifacts per run
│   ├── Compare runs: find best hyperparameter combination
│   └── MLflow UI: visual comparison of experiments
├── Feature Store
│   ├── Problem: duplicated feature computation across teams
│   ├── Offline store: S3/BigQuery — for training
│   ├── Online store: Redis/DynamoDB — for real-time inference
│   └── Point-in-time join: only use features available at prediction time
├── Model Registry
│   ├── Versioned catalog of trained models
│   ├── Staging workflow: None → Staging → Production → Archived
│   └── Model card: description, metrics, intended use, limitations
├── Data Drift
│   ├── Data drift: input distribution P(X) changes
│   ├── Concept drift: P(Y|X) changes — world changes
│   ├── Proxy metrics: confidence distribution, output entropy
│   └── Delayed labels: ground truth takes days/weeks to arrive
├── Model Deployment Strategies
│   ├── Shadow: challenger logs predictions, not returned to users
│   ├── Canary: small % live traffic to challenger
│   ├── A/B testing: statistical significance before full rollout
│   └── Blue/Green: full traffic swap with instant rollback
└── CI/CT/CD/CM Pipelines
    ├── CI: test code and validate features
    ├── CT: automated retrain on trigger (drift, schedule, data volume)
    ├── CD: deploy new model version to serving infra
    └── CM: drift detection + label monitoring + alerting
```

### First Principles

- ML systems have three artifacts (code, data, model) vs software's one (code) — all three must be versioned or the system is not reproducible.
- Models are not static: data distributions shift over time, causing model predictions to degrade — monitoring model behavior is mandatory, not optional.
- Experiment tracking is not optional at team scale: without it, you cannot reproduce a good result, explain a regression, or compare two approaches scientifically.
- Feature stores exist because feature computation is expensive and error-prone — centralize it once, serve everywhere, prevent training-serving skew.
- The staged deployment pattern (shadow → canary → A/B → production) exists to validate model quality with real traffic before committing to a full rollout.

## Easy

**1. What is MLOps?**

MLOps applies DevOps principles to machine learning systems. It covers the full lifecycle: data preparation, model training, evaluation, deployment, monitoring, and retraining. The goal is to make ML systems reliable, reproducible, and continuously deliverable — not just one-off research experiments.

**2. What is the difference between model training and model inference?**

Training is a batch process that learns model parameters from historical data — typically run on GPU clusters, takes hours to days, and produces a model artifact. Inference is the real-time or batch process that applies the trained model to new inputs to generate predictions — latency-critical, often serving thousands of requests per second.

**3. What is a model artifact?**

A model artifact is the serialized output of training: the learned weights, model architecture definition, preprocessing transformations, and associated metadata. Stored in formats like pickle, ONNX, SavedModel (TensorFlow), or TorchScript. The artifact is versioned and promoted through environments (dev → staging → production).

**4. Why is reproducibility important in ML and how do you achieve it?**

Without reproducibility, you can't debug degraded models, audit predictions, or safely retrain. Achieve it by: pinning library versions (requirements.txt or conda env), versioning training data with DVC or Delta Lake snapshots, logging all hyperparameters and random seeds in an experiment tracker (MLflow, W&B), and storing the exact commit hash used for each training run.

**5. What is experiment tracking and why does it matter?**

Experiment tracking records the inputs (dataset version, hyperparameters, code commit) and outputs (metrics, artifacts) of every training run. Without it, you can't compare runs, reproduce the best model, or audit what was tried. Tools: MLflow Tracking, Weights & Biases, Neptune.

**6. What is a model registry?**

A model registry is a versioned catalog of trained models with their metadata (training metrics, dataset versions, framework). It provides staging workflows (Staging → Production), enables comparison between candidate versions, and serves as the promotion gate before models reach production. MLflow Model Registry, W&B Model Registry, Sagemaker Model Registry.

**7. What is DVC and what problem does it solve?**

DVC (Data Version Control) extends Git to version large binary files (datasets, model artifacts) by storing pointers in Git while the data itself lives in remote storage (S3, GCS, Azure Blob). This means experiments are reproducible — you can checkout a commit and reproduce the exact dataset + code used for a run.

**8. What is a feature store?**

A feature store is a centralized system for storing, computing, and serving ML features. It has two stores: an offline store (columnar, historical, for training — Parquet/Delta Lake) and an online store (low-latency key-value, for inference — Redis, DynamoDB). Feature stores prevent training-serving skew and enable feature reuse across teams.

**9. What is training-serving skew?**

Training-serving skew is when the feature values seen during training differ from those seen at inference time. Common causes: different preprocessing code paths between training and serving, using aggregates in training that can't be computed in real-time, or stale feature values in the online store. The fix is to compute features from a single feature store code path used for both.

**10. What is label leakage?**

Label leakage occurs when features include information derived from the target variable — either directly or through a proxy. Example: using a claim approval timestamp to predict claim approval. The model learns a spuriously perfect signal and fails in production. Prevention: strict temporal ordering — features must only include data available before the prediction point.

**11. What is the difference between CI, CT, and CD in MLOps?**

- **CI (Continuous Integration):** Test data schemas, unit test feature transformations, lint model training code on each commit.
- **CT (Continuous Training):** Automatically retrain the model when new data arrives or drift is detected, evaluate against validation metrics.
- **CD (Continuous Delivery/Deployment):** Automatically promote and deploy the new model if it passes evaluation gates.

**12. What is the difference between batch, online, and async inference?**

- **Batch:** Run predictions on a large dataset at scheduled intervals. High throughput, latency doesn't matter. Used for weekly scoring jobs.
- **Online (real-time):** Serve predictions via HTTP API synchronously. Latency-critical (< 100ms). Used for recommendation engines, fraud detection.
- **Async:** Client submits a job and polls for results or receives a callback. Used for heavy inference (video analysis, LLMs) where immediate response isn't possible.

**13. What is a shadow deployment for ML models?**

A shadow deployment runs the new model in parallel with the existing production model. Production traffic is duplicated — the challenger model receives all requests but its predictions are logged, not returned to users. This lets you evaluate real-world performance and latency without any user impact before promoting the model.

**14. What is A/B testing for models?**

A/B testing routes a percentage of live traffic to the challenger model. Users in bucket A receive predictions from the current model; users in bucket B receive predictions from the challenger. Statistical significance tests determine if the challenger's business metrics (click-through rate, conversion) are meaningfully different before full rollout.

**15. What is data drift?**

Data drift (covariate shift) is when the distribution of input features changes between training time and serving time. Example: a credit model trained in 2023 sees different income distributions after economic changes in 2024. Detected by comparing feature distributions (KL divergence, PSI, K-S test) between a reference window and the current serving distribution.

**16. What is concept drift?**

Concept drift is when the relationship between inputs and the target variable changes over time — the world changes, not just the data. A fraud detection model trained on pre-pandemic patterns may become less accurate as attacker behavior evolves. Unlike data drift, concept drift can only be detected when ground truth labels become available (often delayed).

**17. How do you run GPU workloads in Kubernetes?**

Install the NVIDIA device plugin DaemonSet, which exposes GPUs as `nvidia.com/gpu` resources. Request GPUs in pod specs: `resources: limits: nvidia.com/gpu: 1`. For multi-GPU workloads use node pools with GPU instances and taint them to prevent CPU-only workloads from landing there. Use `toleration` + `nodeSelector` to target the correct pool.

**18. What is model lineage?**

Model lineage is the traceable record of a model's provenance: which dataset version was used, what code and hyperparameters produced it, which experiments preceded it, and which production endpoints are running it. Lineage enables audit (regulatory compliance), debugging (trace a degraded model to a bad data batch), and reproducibility.

**19. What is the difference between LLMOps and traditional MLOps?**

Traditional MLOps focuses on structured ML pipelines — tabular data, defined training loops, deterministic evaluation. LLMOps deals with: prompt version management, LLM output evaluation (non-deterministic), RAG pipeline orchestration, token cost optimization, latency management for long generation, and safety/content policy evaluation. LLMs rarely require retraining — most iteration happens at the prompt and retrieval level.

**20. What is a model card?**

A model card is structured documentation for a model: intended use cases, performance metrics across demographic groups, known limitations, evaluation datasets, and ethical considerations. Google published the model card framework. Required for regulatory compliance and responsible AI deployment.

**21. What is Kubeflow?**

Kubeflow is a Kubernetes-native MLOps platform. It provides: Pipelines (KFP) for orchestrating ML workflows as DAGs, KServe for model serving, Katib for hyperparameter tuning, and Notebooks for managed Jupyter environments. It runs entirely on Kubernetes and integrates with cloud-managed Kubernetes services.

**22. How does Apache Airflow fit into MLOps?**

Airflow orchestrates data engineering and ML workflows as DAGs (Directed Acyclic Graphs). A typical ML DAG: extract data → validate schema → compute features → trigger training → evaluate → conditionally deploy. Airflow handles scheduling, retry logic, and dependency management. It's better for data engineering pipelines than ML-specific orchestration (Kubeflow Pipelines handles training DAGs better).

**23. What are the four components of MLflow?**

- **MLflow Tracking:** Log and query experiment runs (parameters, metrics, artifacts).
- **MLflow Projects:** Package ML code in a reproducible format (conda env + entry point).
- **MLflow Models:** Standard model packaging format with multiple deployment flavors (Python function, ONNX, TensorFlow, PyTorch).
- **MLflow Model Registry:** Versioned catalog with staging workflow and annotations.

**24. What is hyperparameter tuning and what approaches exist?**

Hyperparameters are set before training (learning rate, depth, regularization) — unlike parameters, they aren't learned by gradient descent. Tuning approaches: Grid Search (exhaustive), Random Search (random samples, surprisingly effective), Bayesian Optimization (models the objective function to select next configuration, more sample-efficient), and Population-Based Training (evolutionary, good for deep learning). Tools: Optuna, Ray Tune, Katib.

**25. What is model explainability and why does it matter?**

Model explainability provides insight into why a model made a specific prediction. SHAP (SHapley Additive exPlanations) computes the contribution of each feature to a prediction using game theory. LIME approximates the model locally with an interpretable surrogate. Required for: regulatory compliance (GDPR right-to-explanation), debugging predictions, detecting bias, and building user trust.

***

### System Design Perspective

**ML System for a New Product Feature (End-to-End)**
1. Data layer: raw events in Kafka → Spark streaming job → Delta Lake table (versioned, queryable).
2. Feature layer: Feast feature store; offline store backed by BigQuery for training; online store backed by Redis for inference.
3. Training layer: MLflow Tracking for experiment management; Kubeflow Pipeline for automation; model registered in MLflow Model Registry.
4. Serving layer: KServe on Kubernetes; REST endpoint with < 50ms P99 SLO; HPA scaling based on requests/second.
5. Monitoring layer: Evidently AI for weekly drift reports; Prometheus for latency/error rate; alert on PSI > 0.2.

**Reproducibility Design**
- All training runs reference: data version (DVC tag or Delta Lake snapshot), code commit SHA, hyperparameter values, random seeds — store all in MLflow.
- Containerize the training job (Dockerfile with pinned dependencies) so the exact environment is reproducible months later.

**A/B Test Statistical Design**
- Pre-compute required sample size: `n = (z_α + z_β)² * 2σ² / δ²`; for 80% power and 5% significance, typically ~3000 samples per variant for a 2% effect size.
- Run the test for at least one full business cycle (7 days minimum) to account for day-of-week effects before declaring significance.


```
MLOps — Medium Interview Topics
├── Continuous Training Pipeline Design
│   ├── Trigger: new data, drift detected, schedule, business KPI drop
│   ├── Data validation: Great Expectations checks schema + distribution
│   ├── Feature engineering: Spark/Beam → offline feature store
│   ├── Training: K8s Job / SageMaker / Vertex AI + MLflow logging
│   ├── Evaluation: compare challenger vs champion metrics
│   ├── Promotion gate: +1% AUC threshold → register in staging
│   └── Deploy: GitOps commit → ArgoCD → canary test → production
├── Notebook Version Control
│   ├── nbstripout: strip outputs before commit
│   ├── Jupytext: pair notebook with .py file for clean diffs
│   └── Refactor: production logic lives in .py modules, not notebooks
├── Training-Serving Skew Prevention
│   ├── Shared feature computation library (not duplicated code)
│   ├── Feature store: same features at training and serving time
│   ├── Schema validation at serving: fail on unexpected feature types
│   └── Shadow deployment: compare offline vs online feature values
├── Model Performance Monitoring
│   ├── PSI: Population Stability Index — distribution shift metric
│   ├── KS test, Jensen-Shannon, Wasserstein: statistical drift tests
│   ├── Delayed label problem: proxy metrics for monitoring
│   └── Evidently AI / WhyLabs / Arize AI: monitoring platforms
├── Distributed Training
│   ├── Data parallelism: PyTorch DDP — replicate model, split data
│   ├── ZeRO optimizer: shard optimizer states across GPUs
│   ├── Gradient checkpointing: recompute activations to save memory
│   ├── Gradient accumulation: simulate large batch size on small GPU
│   └── Kubeflow Training Operator: PyTorchJob / TFJob on K8s
├── LLM Evaluation
│   ├── RAGAS: faithfulness, answer_relevancy, context_precision
│   ├── BLEU / ROUGE: reference-based text similarity metrics
│   ├── Human evaluation: side-by-side preference scoring
│   └── LLM-as-judge: GPT-4 or Claude evaluating model outputs
├── Model Governance
│   ├── Model card: training data, metrics, limitations, intended use
│   ├── ML-BOM (ML Bill of Materials): data provenance + dependencies
│   ├── SR 11-7: regulatory model risk management (financial services)
│   └── GDPR: right-to-explanation requires explainable predictions
└── Kubeflow vs SageMaker vs Vertex AI
    ├── Kubeflow: open-source, K8s-native, highest flexibility, highest ops burden
    ├── SageMaker: AWS-managed, deep AWS integration, least flexibility
    └── Vertex AI: GCP-managed, AutoML, Workbench, Feature Store built-in
```

### First Principles

- Continuous Training requires more gates than CI/CD: code passing tests is not sufficient — the model must also outperform the production champion on a held-out evaluation set.
- Training-serving skew is the most common silent failure in ML production: fix it at the architecture level with a shared feature computation library, not with post-hoc debugging.
- Distributed training is a memory management problem: ZeRO, gradient checkpointing, and gradient accumulation are all techniques to fit more model into available GPU memory.
- Model governance is not optional: regulatory requirements (SR 11-7, GDPR), fairness requirements, and model risk management require documented provenance of every production model.
- Monitoring delayed labels with proxy metrics (confidence, entropy) is imperfect but essential — you cannot wait weeks for ground truth when models serve real-time predictions.

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

***


***

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

***

### System Design Perspective

**CT Pipeline Architecture (Production)**
- Orchestration: Kubeflow Pipelines or Airflow DAG; triggered via event (S3 event notification, Kafka message, drift alert webhook).
- Validation gate: Great Expectations suite runs before training; if data quality < threshold, pipeline aborts and pages on-call — never train on corrupt data.
- Evaluation gate: challenger model evaluated on a time-bounded holdout set (last N days, not random split) — random splits can introduce temporal leakage.
- Promotion strategy: auto-promote if challenger > champion by > threshold AND shadow deployment metrics are clean for 24h; require human approval for > 5% accuracy improvement (unusual changes warrant review).

**Feature Store Architecture**
- Write path: Spark/Beam job computes features → writes to offline store (S3 Parquet + Delta Lake) → materialization job pushes latest values to online store (Redis).
- Read path (training): point-in-time join at the training entity's event timestamp — prevents future data leakage.
- Read path (serving): online store lookup by entity ID, P99 < 5ms SLO; fallback to default value if feature is stale (TTL exceeded).
- Freshness monitoring: alert if materialization job is > 2x its expected latency — stale online features are a silent correctness bug.

**Multi-Model Serving Platform**
- Model router: classify incoming request by type → route to appropriate serving backend (small model for simple queries, large model for complex, specialized model for domain-specific).
- Resource isolation: each model runs in a separate K8s pod with dedicated GPU/CPU limits — noisy-neighbor prevention.
- A/B framework: Istio VirtualService + header-based routing; log model version with every prediction for post-hoc analysis.


```
MLOps — Hard Interview Topics
├── Multi-Region ML Inference at Scale
│   ├── Global entry: Route53 / Cloudflare latency-based routing
│   ├── Regional serving: KServe / Triton on EKS/GKE
│   ├── Online features: regional Redis clusters (P99 < 5ms)
│   ├── Model artifacts: replicate to regional S3/GCS buckets
│   ├── Canary: Istio VirtualService weighted routing
│   └── KEDA: autoscale on RPS Prometheus metric
├── Fault-Tolerant Distributed Training
│   ├── Kubeflow Training Operator: PyTorchJob / TFJob
│   ├── Checkpointing: save to S3 every N steps; resume on failure
│   ├── PyTorch Elastic (torchrun): handle worker failure gracefully
│   ├── Spot instances: 60-80% savings; 2-minute preemption window
│   └── Gradient checkpointing + ZeRO Stage 3: memory optimization
├── ML Platform Architecture
│   ├── Data: Delta Lake / Iceberg on S3; Great Expectations validation
│   ├── Features: Feast/Tecton; offline BigQuery + online Redis
│   ├── Training: Kubeflow Pipelines; MLflow experiment tracking
│   ├── Registry: MLflow Model Registry with aliases (@champion, @challenger)
│   └── Serving: KServe for standard; vLLM for LLMs; Triton for GPU batch
├── LLM Production Engineering
│   ├── vLLM PagedAttention: non-contiguous KV cache blocks
│   ├── Continuous batching: process tokens from multiple requests simultaneously
│   ├── Model parallelism: Tensor (layer split) + Pipeline (stage split)
│   ├── TTFT / TPOT / TPS: key LLM serving latency metrics
│   └── Semantic caching: cache responses for similar queries
├── RAG Pipeline Engineering
│   ├── Indexing: chunk → embed → vector DB (Pinecone, Weaviate, Qdrant)
│   ├── Retrieval: ANN search → cross-encoder reranking → top-k
│   ├── RAGAS evaluation: faithfulness + answer_relevancy + context metrics
│   └── Chunking strategies: fixed-size, semantic, recursive character
├── Advanced GPU Infrastructure
│   ├── ZeRO stages: Stage 1 (optimizer), Stage 2 (+gradients), Stage 3 (+params)
│   ├── MIG: Multi-Instance GPU partitioning for A100/H100
│   ├── InfiniBand: high-bandwidth GPU-to-GPU for Tensor Parallelism
│   └── Gradient accumulation: simulate large batch size on small GPU
└── ML Platform Playbook
    ├── Incident triage: platform health vs model correctness separation
    ├── Shadow deployment: safe challenger evaluation without user impact
    ├── Rollback: revert model registry version + GitOps commit
    └── Responsible AI: fairness (demographic parity, equalized odds), SHAP
```

### First Principles

- At 100K req/sec, latency is determined by the bottleneck: feature retrieval, model inference, or network — profile each independently.
- Distributed training is a memory problem first: ZeRO stages, gradient checkpointing, and MIG are all memory management strategies.
- LLM serving differs fundamentally from standard ML: memory (KV cache) is the bottleneck, not compute — optimizing KV cache utilization (PagedAttention, continuous batching) is the primary scaling lever.
- RAG quality is retrieval quality: a great LLM with poor retrieval produces confident-sounding wrong answers — invest in reranking and RAGAS evaluation.
- Fault tolerance in distributed training requires checkpointing: the cost of losing a 24-hour training run on Spot preemption is the cost of not implementing checkpointing.
- Responsible AI is not optional: fairness metrics, SHAP explainability, and model cards are required for regulated industries and increasingly expected everywhere.

## Hard

**44. Design a multi-region ML inference platform serving 100K requests/second.**

Architecture:

1. **Global entry point:** AWS Route 53 / Cloudflare with latency-based routing. Requests routed to the nearest active region.
2. **Model serving layer:** KServe or Triton Inference Server running on EKS/GKE in three regions (us-east-1, eu-west-1, ap-southeast-1). GPU node pools with Karpenter for right-sized autoscaling.
3. **Feature retrieval:** Regional Redis clusters for online feature store — features pre-materialized per entity. P99 feature lookup < 5ms.
4. **Model artifacts:** Replicate model artifacts to regional S3/GCS buckets. Model serving pods pull from the regional bucket on startup — no cross-region pulls.
5. **Canary routing:** Istio VirtualService with weighted routing for gradual rollout. Shadow mode for model candidates.
6. **Autoscaling:** KEDA scaling based on requests-per-second Prometheus metric. Pre-scale on predicted traffic spikes using scheduled ScaledObjects.
7. **Model consistency:** All regions run the same model version. Model promotion via GitOps — a single git commit updates the model version in all regions via ArgoCD ApplicationSets.

**45. How do you run fault-tolerant distributed training on Kubernetes?**

1. **Operator:** Use Kubeflow Training Operator (PyTorchJob, TFJob) — it manages replica coordination and restarts failed workers.
2. **Checkpointing:** Save model checkpoints to shared storage (NFS or S3) every N steps. On worker restart, the job resumes from the last checkpoint — not from scratch.
3. **Elastic training:** PyTorch Elastic (`torchrun`) handles worker failures gracefully. If one of 8 workers dies, training continues with 7 workers at reduced throughput rather than failing completely.
4. **Spot instances:** Use GPU Spot instances for 60-80% cost savings. Configure preemption tolerance: save a checkpoint when a Spot interruption notice arrives (2-minute window). On reschedule, resume from the checkpoint.
5. **Monitoring:** Export training metrics (loss, throughput, GPU utilization) to Prometheus. Alert if GPU utilization drops below 70% (indicates a bottleneck — data loading, CPU preprocessing, or communication overhead).

**46. Explain the ZeRO optimizer stages and when to use each.**

ZeRO (Zero Redundancy Optimizer) reduces GPU memory by partitioning optimizer state, gradients, and parameters across data-parallel workers:

- **Stage 1:** Partition optimizer state across GPUs. Each GPU stores only 1/N of the optimizer state. Memory reduction: ~4x for Adam optimizer. Trivial to enable.
- **Stage 2:** Partition gradients + optimizer state. After backward pass, gradients are reduced and each GPU retains only its shard. Memory reduction: ~8x. Slight communication overhead.
- **Stage 3:** Partition parameters + gradients + optimizer state. Full parameter sharding — parameters are gathered just-in-time for forward/backward. Memory reduction: ~linear with N GPUs. Enables training models that don't fit on a single node. Communication overhead is highest. Use for models > 10B parameters.

Implemented via DeepSpeed (Microsoft) or FSDP (PyTorch native). ZeRO-3 + Offload also offloads optimizer state to CPU RAM for extreme memory savings.

**47. How does vLLM's PagedAttention work and why does it matter?**

Standard LLM inference pre-allocates a contiguous KV cache buffer per sequence based on maximum sequence length. This causes two problems: most sequences are shorter than max length (internal fragmentation wastes GPU memory), and sequences can't be easily shared (duplicate prompts waste memory).

PagedAttention stores KV cache in non-contiguous blocks (pages), inspired by virtual memory paging. Each block holds K and V vectors for a fixed number of tokens. A block table maps logical positions to physical blocks. Benefits:
- **Memory efficiency:** Near-zero internal fragmentation — blocks are allocated as tokens are generated.
- **Prefix caching:** Multiple requests with the same system prompt share the physical blocks for that prefix — memory is not duplicated.
- **Higher throughput:** Better memory utilization means more concurrent requests fit in GPU memory, increasing throughput 2-4x over naive implementations.

**48. Design a cost-optimal LLM serving system for 10 million requests per day.**

At 10M requests/day (~116 req/s average), cost optimization is critical:

1. **Request routing by complexity:** Use a classifier to route simple requests to a smaller, cheaper model (Llama-3-8B) and complex requests to a larger model (GPT-4, Llama-3-70B). 70-80% of requests typically qualify for the smaller model.
2. **Semantic caching:** Cache responses for semantically similar queries using embedding similarity (Redis + pgvector). Cache hit rate of 20-30% is common, directly reducing model calls.
3. **Batching:** vLLM's continuous batching maximizes GPU utilization by filling batches with in-flight requests rather than waiting for a full batch.
4. **Quantization:** Serve with AWQ INT4 quantization — 4x memory reduction, 2x throughput improvement, < 1% quality degradation for most tasks.
5. **Spot instances:** Run LLM inference on spot instances with graceful request replay on interruption (requests are stateless, retry is safe).
6. **Auto-scaling:** KEDA scaling based on queue depth. Scale to near-zero during low-traffic hours (2am-6am) for non-SLA-bound requests.

**49. Design a Triton Inference Server deployment with dynamic batching.**

```
# model_config.pbtxt
name: "bert_classifier"
platform: "onnxruntime_onnx"
input [{ name: "input_ids" data_type: TYPE_INT64 dims: [-1, 128] }]
output [{ name: "logits" data_type: TYPE_FP32 dims: [-1, 2] }]

dynamic_batching {
  preferred_batch_size: [8, 16, 32]
  max_queue_delay_microseconds: 5000
}

instance_group [{ count: 2 kind: KIND_GPU }]
```

Dynamic batching collects requests arriving within `max_queue_delay_microseconds` (5ms) and forms a batch up to `preferred_batch_size`. Two GPU instances run in parallel. Deploy with: `helm install triton nvidia/triton-inference-server --set model_repository=s3://models/`. Expose via Kubernetes Service; use KEDA to scale replicas based on `nv_inference_queue_duration_ms` Prometheus metric.

**50. Design a RAG pipeline and identify its failure modes.**

Architecture:
1. **Ingestion:** Documents → chunk (512 tokens, 50 overlap) → embed (OpenAI/E5/BGE) → store in vector DB (Pinecone, Weaviate, pgvector) with metadata.
2. **Query:** User query → embed → ANN search (top-k=5) → rerank (Cohere Reranker, cross-encoder) → context assembly → LLM prompt → response.
3. **Evaluation:** RAGAS metrics on a golden QA dataset; Prometheus latency tracking per pipeline stage.

Failure modes:
- **Retrieval failures:** Wrong chunks retrieved (poor embedding model, chunking too large/small, semantic gap between query and document). Fix: hybrid search (BM25 + vector), reranking.
- **Lost-in-the-middle:** LLM ignores context in the middle of a long prompt. Fix: order retrieved chunks by relevance (most relevant first/last), limit context window.
- **Hallucination:** LLM generates information not in retrieved context. Fix: citation prompting ("only answer from context"), faithfulness evaluation with RAGAS.
- **Stale knowledge:** Vector DB contains outdated documents. Fix: re-ingestion pipeline with document versioning and deletion of outdated chunks.
- **Latency:** Embedding + retrieval + LLM in sequence. Fix: cache embeddings for common queries, async retrieval where possible.

**51. What are RAGAS evaluation metrics and how do you use them?**

RAGAS (Retrieval Augmented Generation Assessment) provides four LLM-evaluated metrics:

- **Faithfulness:** Are all claims in the answer supported by the retrieved context? (Hallucination detection)
- **Answer Relevancy:** How relevant is the answer to the question? (LLM rates on 0-1 scale)
- **Context Precision:** Do the retrieved chunks contain only relevant information? (Precision of retrieval)
- **Context Recall:** Are all answer-relevant facts present in the retrieved chunks? (Coverage of retrieval)

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

result = evaluate(
    dataset,  # questions, answers, contexts, ground_truths
    metrics=[faithfulness, answer_relevancy, context_precision]
)
```

Run RAGAS on a golden evaluation dataset (100-500 curated QA pairs) after each RAG pipeline change. Alert if faithfulness drops below 0.85.

**52. Design a model governance framework for a regulated financial services ML system.**

Governance requirements under SR 11-7 (Federal Reserve Model Risk Management):

1. **Model inventory:** Every model in production registered in a central catalog with: business purpose, owner, risk tier, training data, performance metrics, validation status.
2. **Independent validation:** Model risk team validates all Tier 1 models (high-impact) annually. Validation includes: conceptual soundness review, data quality assessment, back-testing on out-of-time samples, sensitivity analysis.
3. **Change management:** Every model update (retraining, threshold change, feature addition) triggers a change ticket. Minor updates (same architecture, new data): expedited review. Major updates (new architecture, new features): full validation cycle.
4. **Ongoing monitoring:** Automated monthly reports showing PSI per feature, AUC trend, demographic fairness metrics. Breach of monitoring thresholds triggers mandatory review.
5. **Explainability:** All credit decisions must provide SHAP-based explanations. Adverse action notices link to feature contributions.
6. **Audit trail:** Immutable logs of all model versions deployed, predictions made, and data used. Retained for 7 years.

**53. How do you implement online learning for streaming data?**

Online learning updates model parameters incrementally as each new data point arrives, rather than batch retraining:

1. **River library:** Python library for streaming ML — incremental learning algorithms (Hoeffding Trees, SGD classifiers, online gradient boosting) that update with each new sample.
2. **Micro-batch retraining:** For deep learning, accumulate mini-batches from the stream and run gradient updates every N examples. Use Adam with a low learning rate to prevent catastrophic forgetting.
3. **Concept drift detection:** ADWIN (Adaptive Windowing) or DDM (Drift Detection Method) monitors model error rate in real-time. When drift is detected, reset or retrain from a recent window.
4. **Architecture:** Kafka stream → Flink/Spark Streaming consumer → online model updates → publish new model weights to Redis → serving layer picks up updated weights.

Caveat: online learning is complex and prone to instability. For most production systems, frequent batch retraining (hourly/daily) achieves similar results with simpler failure modes.

**54. How do you implement multi-region model serving with GDPR data residency?**

GDPR requires that EU citizen data not be processed outside the EU. For ML serving:

1. **Data classification:** Tag each inference request with the user's data residency region at the API gateway.
2. **Region-pinned routing:** EU-tagged requests are hard-routed to EU inference clusters. Route 53 / Cloudflare geo-restrictions prevent accidental cross-region traffic.
3. **Separate feature stores:** EU feature store (eu-west-1) holds EU user features. Non-EU feature store (us-east-1) holds other users. No cross-region feature lookups.
4. **Model artifacts:** The same model binary can be replicated globally (model weights contain no user data). Only inference inputs and outputs must respect residency.
5. **Logging:** Inference logs for EU users must be stored in EU-region log buckets. Logging pipeline routes based on user region tag.
6. **Audit:** Monthly compliance report showing zero cross-region data transfers for tagged EU requests. Verified by VPC Flow Logs analysis.

**55. How do you profile and resolve GPU-bound vs CPU-bound training bottlenecks?**

Use PyTorch Profiler or NVIDIA Nsight:

```python
with torch.profiler.profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    with_stack=True
) as prof:
    train_one_step()
print(prof.key_averages().table(sort_by="cuda_time_total"))
```

**GPU-bound signs:** High CUDA kernel time, GPU utilization consistently > 90%, CPU sits idle waiting for GPU. Fix: larger batch sizes, tensor parallelism across GPUs.

**CPU-bound (data loading) signs:** Low GPU utilization (< 50%), DataLoader `collate_fn` or preprocessing is the bottleneck. Fix: increase `num_workers` in DataLoader, pin memory (`pin_memory=True`), prefetch data, move preprocessing to GPU with NVIDIA DALI.

**CPU-bound (communication) signs:** NCCL all-reduce dominates in multi-GPU training. Fix: gradient compression, increase batch size to reduce all-reduce frequency, use faster interconnect (NVLink vs PCIe).

**56. What is gradient checkpointing and when do you use it?**

Normally, the forward pass stores all intermediate activations in GPU memory for use during backpropagation. For large models, this can consume more memory than the parameters themselves.

Gradient checkpointing trades compute for memory: during the forward pass, only a subset of activations are stored (checkpoints). During backpropagation, the non-stored activations are recomputed from the nearest checkpoint. Memory usage drops from O(n_layers) to O(√n_layers), at the cost of ~30% increased training time.

Enable in PyTorch: `torch.utils.checkpoint.checkpoint(layer, input)` or in Hugging Face Transformers: `model.gradient_checkpointing_enable()`. Used when training large models (> 7B parameters) on limited GPU memory.
# MLOps Interview Playbook

Use this file for MLOps, ML platform, ML infrastructure, inference platform, and model-serving interviews.

### What Interviewers Are Really Testing

### 1. Reproducibility

In MLOps, a deployment is not just code. A strong answer shows that you understand versioning across:

- code
- data
- features
- model artifacts
- configuration

### 2. Training Versus Inference

Interviewers want to know that you understand the difference between:

- offline training workloads
- batch inference
- real-time inference
- asynchronous scoring

Each one has different latency, cost, autoscaling, and observability requirements.

### 3. Data And Feature Discipline

Many MLOps failures are not "server down" failures. They are:

- schema mismatch
- feature skew
- stale features
- label leakage
- data drift

You should be able to talk about these as production risks, not just data science details.

### 4. Safe Model Delivery

A good MLOps engineer knows how to move a model safely from experiment to production:

- experiment tracking
- registry promotion
- validation gates
- shadow deployment
- canary rollout
- rollback

### 5. Platform And Cost Awareness

Senior MLOps answers should include:

- GPU scheduling
- autoscaling and queueing
- checkpointing long jobs
- spot or preemptible trade-offs
- throughput versus latency
- cost per training run or cost per inference

### 6. Monitoring Beyond Uptime

In traditional DevOps, `200 OK` might mean success. In MLOps, a service can be technically healthy and still wrong. You should discuss:

- drift
- confidence distribution
- feature null rates
- data freshness
- business KPI impact
- delayed ground truth

### A Strong MLOps Answer Framework

For most interview questions, use this structure:

1. Identify whether the problem is in data, training, model, serving, or platform.
2. Clarify the artifact versions involved: code, data, features, model, config.
3. Explain how you would validate correctness before optimizing performance.
4. Talk about safe rollout, rollback, and observability.
5. Close with reproducibility and prevention controls.

Example:

> I would first separate platform health from model correctness. If the endpoint is healthy but predictions are wrong, I would validate input schema, feature transformation parity, model version, and registry lineage before changing infrastructure.

### What You Should Know By Topic

### Lifecycle And Artifacts

- code, data, features, model, and metadata as first-class artifacts
- experiment tracking
- registry promotion and approval
- lineage from training run to production endpoint

### Data And Feature Management

- data validation gates
- feature stores
- offline versus online features
- training-serving skew
- schema evolution and contracts

### Pipelines

- CI for code and tests
- CT for retraining
- CD for model serving
- pipeline orchestration tools such as Kubeflow, Airflow, or MLflow workflows

### Serving Patterns

- batch inference
- online inference
- async inference
- A/B testing, shadow, canary, champion-challenger
- REST or gRPC serving

### Platform And Infrastructure

- Kubernetes scheduling
- GPU nodes and device plugins
- autoscaling
- model loading and cold start behavior
- storage for datasets, features, and model artifacts

### Observability

- service latency, throughput, error rate
- drift and freshness metrics
- confidence score shifts
- online versus offline evaluation
- feedback loops and delayed labels

### Security And Governance

- PII handling
- secrets and credentials
- access to datasets and models
- audit trail for promotion and rollback
- approval gates for regulated environments

### LLMOps As An Advanced Specialization

For modern MLOps interviews, it also helps to mention:

- prompt and evaluation versioning
- retrieval pipeline quality
- token cost controls
- guardrails and fallback models
- latency and throughput trade-offs for large models

### Must-Know Commands And Checks

### DVC

- `dvc add <path>`
- `dvc push`
- `dvc pull`
- `dvc status`
- `dvc repro`

### MLflow

- `mlflow ui`
- `mlflow models serve -m <model_uri>`
- run metadata, params, metrics, and model registry stages

### Kubernetes And GPU Checks

- `kubectl get pods`
- `kubectl describe pod <name>`
- `kubectl logs <pod>`
- `kubectl describe node <name>`
- `kubectl get events --sort-by=.lastTimestamp`
- `nvidia-smi`

### Serving Validation

- `curl` a sample payload against the inference endpoint
- compare expected features and payload schema
- inspect model version, registry stage, and serving config

### High-Value Scenarios To Practice

### Wrong Predictions With `200 OK`

Mention:

- input schema validation
- feature parity between training and serving
- model version and registry lineage
- stale or missing features

### Data Drift Or Concept Drift

Mention:

- statistical comparison against training baseline
- delayed-label problem
- proxy metrics such as confidence or output distribution
- retraining trigger rules

### GPU Pods Stuck In `Pending`

Mention:

- device plugin health
- available GPU capacity
- taints and tolerations
- driver and CUDA compatibility

### Latency Spike After A New Model Release

Mention:

- model size or cold start
- batch size and concurrency
- CPU versus GPU inference choice
- canary rollback or traffic shift

### Expensive Training Jobs

Mention:

- spot or preemptible workers
- checkpointing
- data locality
- artifact caching
- experiment pruning

### Strong Signals In Senior MLOps Answers

- You distinguish platform health from model quality.
- You talk about lineage and reproducibility without being prompted.
- You mention rollout safety and rollback for models, not just services.
- You connect data quality and feature quality to production risk.
- You think about cost, GPU utilization, and throughput, not just model accuracy.

### Common Weak Signals

- Treating MLOps as ordinary CI/CD with a notebook attached
- Ignoring data versioning
- Saying the model is fine because the endpoint returned `200`
- Recommending retraining without defining a trigger or validation gate
- Ignoring feature skew and delayed labels

### Final Revision Checklist

- I can explain the difference between DevOps and MLOps.
- I can explain reproducibility across code, data, features, and model versions.
- I can explain model registry, feature store, experiment tracking, and drift.
- I can discuss batch, online, and async inference trade-offs.
- I can explain safe rollout patterns for new models.
- I can troubleshoot wrong predictions even when infrastructure is healthy.
- I can discuss GPU scheduling, latency, and cost trade-offs at a senior level.

***

**57. Design a platform for fine-tuning and serving open-source LLMs at scale.**

Architecture for an internal LLM fine-tuning and serving platform supporting 20 teams:

**Fine-tuning layer:**
- Job submission via a REST API or GitOps: team pushes a `finetune.yaml` with base model, dataset path, LoRA config, resource request
- Kubernetes operator (custom or Kubeflow PyTorchJob) schedules training on GPU node pool
- Parameter-Efficient Fine-Tuning (PEFT) with LoRA: only adapter weights are trained — base model is frozen. Adapter size: ~50-200 MB vs 14 GB for full 7B model weights
- Distributed training with DeepSpeed ZeRO-2 for 7B-70B models
- Experiment tracking: all runs logged to MLflow with base model version, dataset version (DVC), LoRA rank/alpha, evaluation metrics (perplexity, task-specific benchmarks)
- Artifacts: save adapter weights to S3 with SHA256 hash; register in model registry

**Serving layer:**
- LoRA adapter hot-swap on vLLM: load base model once, swap adapter per-request using `--enable-lora` flag
- Multiple teams share one base model instance — reduces GPU memory from N×14GB to 14GB + N×200MB
- Per-team routing at the API gateway: `X-Model-Adapter: team-a-v3` header routes to the correct adapter
- Autoscaling: KEDA on queue depth; pre-warm adapters during business hours

**Governance:**
- Model card required before promotion to production
- Red-teaming: automated safety evaluation pipeline before each adapter promotion
- Cost allocation: GPU-hours per team per adapter, billed monthly

**58. How do you implement end-to-end ML lineage from raw data to production prediction?**

Lineage traces every production prediction back to: the raw data record, the feature computation, the model version, the hyperparameters, and the code commit.

Implementation using ML Metadata (MLMD) or MLflow:

```python
with mlflow.start_run() as run:
    # Log all upstream pointers
    mlflow.log_param("dataset_version", "s3://data/train_v42.parquet")
    mlflow.log_param("feature_view_version", "user_features_v7")
    mlflow.log_param("git_commit", subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip())
    mlflow.log_param("data_validation_run_id", validation_run_id)
    mlflow.set_tag("base_model", "xgboost-3.0.0")

    # Train
    model = train(X_train, y_train, params)
    mlflow.xgboost.log_model(model, "model",
        registered_model_name="fraud-detector")

# At prediction time, log which model version served the request
prediction_log = {
    "request_id": str(uuid.uuid4()),
    "model_version": "fraud-detector/v12",
    "mlflow_run_id": "abc123",
    "feature_view_version": "user_features_v7",
    "dataset_version": "train_v42",
    "prediction": 0.97,
    "timestamp": datetime.utcnow().isoformat()
}
```

Full lineage query: "Which predictions were made by a model trained on data_batch_v41?" → query prediction logs by `mlflow_run_id` → look up run's `dataset_version` parameter → join.

**59. How do you design an ML platform for regulated financial services (model risk management)?**

SR 11-7 (Federal Reserve) and OCC guidance require:

**Model inventory and tiering:**
- Tier 1 (high-impact, e.g., credit decisions, AML): full independent validation annually, mandatory challenge before deployment
- Tier 2 (medium-impact): streamlined validation, monitoring triggers mandatory re-validation
- Tier 3 (low-impact): self-validation with documentation

**Platform controls to enforce SR 11-7:**
```
Developer trains model
         │
         ▼
Automated checks: data quality, bias metrics, back-test on out-of-time sample
         │
         ▼
Model Risk team review (mandatory for Tier 1) — separate system access
         │
         ▼
Model committee approval (audit trail in JIRA + model registry tag)
         │
         ▼
Production deployment with immutable artifact ID in serving config
         │
         ▼
Monthly monitoring report (PSI, AUC trend, fairness metrics) → MRM team
```

**Immutable audit trail:**
- All model promotions captured as signed events (Git commit + registry metadata)
- Prediction logs retained 7 years (S3 Glacier for cost)
- SHAP explanations stored per-prediction for credit decisions
- Zero-delete policy on training datasets used for production models

**60. Design a streaming feature computation pipeline for a fraud detection system with < 50ms end-to-end SLO.**

The full path: transaction event received → features computed → model scores → decision returned in < 50ms.

Budget allocation:
- Network + deserialization: ~2ms
- Feature lookup (online store): ~5ms
- Feature computation (real-time aggregates): ~8ms
- Model inference: ~15ms
- Serialization + network return: ~5ms
- Buffer: ~15ms

**Architecture:**

```
Transaction event (Kafka)
        │
        ├──► Flink streaming job (real-time feature computation)
        │    - user_tx_count_1min: sliding window count
        │    - user_avg_amount_5min: sliding window average
        │    - merchant_velocity_1min: keyed by merchant_id
        │    Writes to Redis (sub-millisecond, atomic INCR/ZADD)
        │
        └──► Scoring API (receives same event via Kafka or direct HTTP)
             - Reads precomputed features from Redis (HGETALL: ~3ms)
             - Reads static features (user profile, device history) from Redis (~2ms)
             - Runs XGBoost or neural network model (~10ms on CPU)
             - Returns {score, explanation} to caller
```

**Critical design choices:**
- Use Redis HGETALL to retrieve all entity features in one round-trip — not N individual GETs
- Flink computes aggregates ahead of the scoring request (pre-compute, not on-demand) — eliminates real-time computation from the critical path
- Feature schema validated via schema registry (Avro/Protobuf) — type mismatch fails fast at ingest, not at inference
- Circuit breaker: if Redis P99 > 15ms, serve with stale features (< 30s old) rather than blocking the request

**61. What are the key differences between transformer decoder-only and encoder-decoder architectures and when do you use each in production?**

| | Decoder-only (GPT, Llama) | Encoder-Decoder (T5, BART) |
|---|---|---|
| Architecture | Causal self-attention; predicts next token | Separate encoder (bidirectional) + decoder (causal) |
| Use cases | Text generation, chat, code | Translation, summarization, QA |
| Inference mode | Autoregressive generation | Encode once, decode iteratively |
| KV cache | Grows with sequence length | Encoder KV cache is fixed per prompt |
| Serving complexity | PagedAttention / continuous batching | Two-phase: encode (parallelizable) + decode |
| Fine-tuning | LoRA on Q/K/V projections | LoRA on encoder + decoder |

**Production preference:** Decoder-only (Llama, Mistral, Qwen) dominates for most production LLM use cases because: instruction tuning is mature, community tooling (vLLM, TGI, Ollama) is optimized for decoder-only, and multi-task capability reduces the need for task-specific models.

**Encoder-decoder still preferred for:** multilingual translation (NLLB, mBART), structured extraction with a fixed output schema (T5 fine-tuned for JSON extraction), and tasks where bidirectional context on the input is critical.

**62. How do you implement a model evaluation framework that detects silent failures?**

Silent failures: the endpoint returns 200, predictions look plausible, but accuracy has degraded — nobody notices until the business KPI moves.

**Multi-layer detection:**

```python
# Layer 1: Statistical process control on confidence distribution
import numpy as np
from scipy import stats

def detect_confidence_shift(reference_confidence, current_confidence):
    stat, pvalue = stats.ks_2samp(reference_confidence, current_confidence)
    return pvalue < 0.05  # distribution has shifted

# Layer 2: Output distribution monitoring
def check_label_distribution_shift(reference_labels, current_predicted_labels):
    ref_pct = np.bincount(reference_labels) / len(reference_labels)
    cur_pct = np.bincount(current_predicted_labels) / len(current_predicted_labels)
    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct + 1e-8))
    return psi > 0.1  # output distribution shifted

# Layer 3: Delayed label evaluation (runs when labels arrive)
def evaluate_on_cohort(cohort_date, predictions_df, labels_df):
    joined = predictions_df.join(labels_df, on="request_id")
    auc = roc_auc_score(joined["label"], joined["score"])
    log_metric(f"auc_cohort_{cohort_date}", auc)
    if auc < MINIMUM_AUC:
        trigger_alert("AUC below minimum on cohort " + cohort_date)

# Layer 4: Proxy metric monitoring (business signal, no labels needed)
def monitor_proxy_metrics():
    # For fraud: approval rate should be stable
    # For recommendation: CTR should be stable
    # For credit: default rate should be predictable
    current_approval_rate = compute_approval_rate(last_24h_predictions)
    if abs(current_approval_rate - BASELINE_APPROVAL_RATE) > 0.05:
        alert("Approval rate shifted 5% — investigate model or input data")
```

**63. How does gradient accumulation work and when is it preferable to increasing batch size?**

In standard training, gradients are computed for a batch of N samples, then optimizer.step() updates weights. With gradient accumulation, you simulate a large batch by accumulating gradients over K smaller batches before calling optimizer.step():

```python
optimizer.zero_grad()
for i, (inputs, labels) in enumerate(dataloader):
    outputs = model(inputs)
    loss = criterion(outputs, labels) / accumulation_steps  # scale loss
    loss.backward()  # accumulate gradients

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()  # update once every K batches
        optimizer.zero_grad()
```

**When to use gradient accumulation over larger batch size:**
- GPU memory is the constraint, not compute — accumulation uses constant memory regardless of effective batch size
- Using very large batches (> 32K tokens for LLMs) requires learning rate warmup and scaling — accumulation is simpler
- Multi-node synchronization is expensive — accumulation reduces all-reduce frequency

**Tradeoffs:**
- Batch norm statistics are computed per micro-batch, not per accumulated batch — use Layer Norm for LLMs (no batch norm)
- Throughput is identical to a single large batch on the same hardware
- Wall-clock time per optimizer step increases linearly with accumulation steps

***

### System Design Perspective

**Inference Platform Cost Optimization**
- Right-size GPU instances: profile model inference requirements (memory, compute) — don't use A100 80GB for a 500M parameter model that fits on a T4 16GB.
- Spot instances for training, on-demand for inference: spot preemption is acceptable for training (checkpoint + resume); serving requires on-demand reliability.
- Request batching: Triton's dynamic batching groups concurrent requests into a single inference call — improves GPU utilization from 30% to 80%+ under load.
- Model quantization: INT8 quantization reduces model memory by 2x and increases throughput by 1.5–2x with minimal accuracy loss for most production models.

**ML Platform Observability Stack**
- Infrastructure layer: Prometheus + Grafana for GPU utilization, memory, pod restarts, node failures.
- Model serving layer: DCGM Exporter for GPU metrics; custom metrics for request queue depth, batch size, model version in use.
- Model quality layer: Evidently AI for drift; custom PSI metric exporter to Prometheus; Grafana panel showing PSI over time per feature.
- Business layer: prediction volume, model-attributed revenue, cost per prediction — joined with business metrics in a unified dashboard.

**LLM Fine-Tuning Architecture**
- PEFT / LoRA: train only a small adapter (< 1% of parameters) instead of full fine-tuning — reduces training cost by 10-100x.
- DPO (Direct Preference Optimization): fine-tune on human preference data without a separate reward model — simpler than RLHF.
- Evaluation: domain-specific benchmark suite + RAGAS for RAG tasks + human preference evaluation — automated evals are proxies, not ground truth.
- Serving fine-tuned model: base model on shared GPU; LoRA adapter loaded per tenant — enables multi-tenant fine-tuning without duplicating the base model.


## Hard (continued) — Training-Serving Skew, GPU Fragmentation, Feature Store PIT Correctness, LLM Cost Optimization, A/B Testing Rigor & Drift Detection

**Q: How do you detect and prevent training-serving skew in a production ML system at scale?**

A: Training-serving skew is the silent killer: the model was trained on correctly computed features, but at serving time the feature pipeline produces different values — the model sees a distribution it has never trained on. Unlike data drift (detectable via statistics), skew is a logic bug that can persist undetected for months while model quality degrades invisibly.

**Root causes and detection signals:**

| Cause | Detection Method |
|-------|-----------------|
| Separate training vs. serving feature code | Shadow comparison: compute features both ways at serve time |
| Schema evolution (new default values) | Schema validation at serving before inference |
| Time zone handling inconsistency | Unit tests with fixed timestamps |
| Feature normalization applied in training but not serving | Validation via Great Expectations on live feature stream |
| Categorical encoding mismatch (LabelEncoder fitted on old data) | Monitor OOV (out-of-vocabulary) rate in categorical features |

**Shadow feature comparison (primary detection):**

```python
def predict_with_skew_detection(entity_id: str, request_time: float):
    # Serving path (what model actually sees)
    serving_features = feature_store.get_online_features(entity_id)

    # Training path (gold standard, computed independently)
    training_features = compute_training_pipeline_features(entity_id, request_time)

    # Log both to BigQuery for offline comparison
    log_feature_pair({
        "entity_id": entity_id,
        "request_time": request_time,
        "serving_features": serving_features,
        "training_features": training_features,
        "prediction": model.predict(serving_features),
    })

    return model.predict(serving_features)

# Daily batch job — compute KS statistic per feature
def detect_skew():
    for feature_name in all_features:
        serving_vals = load_log("serving_features", feature_name)
        training_vals = load_log("training_features", feature_name)
        ks_stat, pval = ks_2samp(serving_vals, training_vals)
        if ks_stat > 0.15:
            alert(f"Skew detected in {feature_name}: KS={ks_stat:.3f}")
```

**Schema validation at inference time:**

```python
from great_expectations.core import ExpectationSuite

suite = ExpectationSuite("serving_features_v2")
# Expectations from training data profile
# e.g., user_age in [0, 120], purchase_count >= 0, country in known_set

def validate_before_predict(features: dict) -> dict:
    result = ge_context.validate(features, expectation_suite=suite)
    if not result.success:
        failed = [r["expectation_config"]["expectation_type"]
                  for r in result.results if not r["success"]]
        prometheus.counter("feature_validation_failure", labels={"reason": str(failed)})
        return fallback_model.predict(features)  # Safe fallback
    return model.predict(features)
```

**Prevention at architecture level:**

The only reliable prevention is a **single feature computation library** used by both training and serving pipelines. No duplication, no divergence:

```python
# Shared library: feature_lib/user_features.py
def compute_user_recency(user_id: str, as_of_time: datetime) -> float:
    """Single implementation used at training AND serving time."""
    last_event = event_store.get_latest_before(user_id, as_of_time)
    if last_event is None:
        return -1.0  # Consistent sentinel for missing data
    return (as_of_time - last_event.timestamp).total_seconds() / 86400
```

Import this in both the offline training pipeline and the online serving handler — never re-implement the logic.

**Monitoring SLA:** Any feature with KS-statistic > 0.15 between serving and training paths triggers P2 alert within 24 hours. Zero tolerance for features where serving value is consistently outside the training distribution.

---

**Q: How do you architect a Kubernetes GPU cluster to keep fragmentation below 10% for multi-tenant ML training jobs?**

A: GPU fragmentation occurs when a job claims GPUs on a node, leaving the remaining GPUs idle because no other job fits. On an 8-GPU node with a 4-GPU job, 4 GPUs are wasted if the remaining capacity doesn't match any pending job's request. At scale (hundreds of nodes), fragmentation of 15–20% translates to millions of dollars in wasted compute per year.

**Fragmentation measurement:**

```python
def compute_fragmentation_rate(nodes, pending_pods):
    total_gpu_capacity = sum(n.gpu_capacity for n in nodes)
    wasted_gpus = 0

    for node in nodes:
        available = node.gpu_capacity - node.gpu_allocated
        if available == 0:
            continue
        # Wasted if no pending pod can fit in the remaining space
        can_pack = any(p.gpu_request <= available for p in pending_pods)
        if not can_pack:
            wasted_gpus += available

    fragmentation_rate = wasted_gpus / total_gpu_capacity
    prometheus.gauge("gpu_fragmentation_rate", fragmentation_rate)
    return fragmentation_rate
```

**Architecture to minimize fragmentation:**

**1. Workload-specific node pools by GPU multiplicity:**

```bash
# Training pool: 8-GPU nodes (DDP jobs request 4 or 8 GPUs)
gcloud container node-pools create training-pool \
  --cluster=ml-cluster \
  --machine-type=a2-highgpu-8g \
  --accelerator=type=nvidia-tesla-a100,count=8 \
  --num-nodes=10

# Serving pool: 1-GPU nodes (inference pods request 1 GPU)
gcloud container node-pools create serving-pool \
  --cluster=ml-cluster \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --num-nodes=20
```

Separation prevents a 1-GPU inference pod from stranding 7 GPUs on an 8-GPU training node.

**2. Bin-packing scheduler configuration:**

```yaml
# kube-scheduler config: prefer bin-packing over spreading
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
  - schedulerName: default-scheduler
    pluginConfig:
      - name: NodeResourcesFit
        args:
          scoringStrategy:
            type: MostAllocated    # Fill nodes before using new ones
            resources:
              - name: nvidia.com/gpu
                weight: 10         # GPU bin-packing weighted highest
              - name: cpu
                weight: 1
              - name: memory
                weight: 1
```

**3. Karpenter for right-sized node provisioning:**

```yaml
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: training-pool
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: nvidia.com/gpu-memory
          operator: In
          values: ["40Gi", "80Gi"]
      nodeClassRef:
        name: gpu-nodeclass
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s    # Repack within 30 seconds of job completion
```

`WhenUnderutilized` + `consolidateAfter: 30s` is the key setting: when a training job finishes, Karpenter immediately evicts and reschedules remaining pods to pack the remaining nodes, then terminates the now-empty node.

**4. Descheduling for fragmentation recovery:**

```yaml
# Descheduler: detect and fix fragmented nodes
apiVersion: descheduler.alpha.kubernetes.io/v1alpha2
kind: DeschedulerPolicy
profiles:
  - name: gpu-consolidation
    pluginConfig:
      - name: LowNodeUtilization
        args:
          thresholds:
            nvidia.com/gpu: 25    # Node < 25% GPU utilized → evict pods
          targetThresholds:
            nvidia.com/gpu: 75    # Target: 75% GPU utilization
    plugins:
      balance:
        enabled: [LowNodeUtilization]
```

**5. Enforcement: reject GPU requests that don't align to pool sizes:**

```python
# Admission webhook: reject jobs requesting non-standard GPU counts
VALID_GPU_COUNTS = {1, 2, 4, 8}  # Align to node GPU counts

def validate_gpu_request(pod_spec):
    requested = sum(
        int(c.resources.requests.get("nvidia.com/gpu", 0))
        for c in pod_spec.containers
    )
    if requested not in VALID_GPU_COUNTS and requested != 0:
        return {"allowed": False,
                "reason": f"GPU request {requested} not in {VALID_GPU_COUNTS}. "
                          f"Use 1, 2, 4, or 8 GPUs to minimize fragmentation."}
    return {"allowed": True}
```

**Target SLA:** < 10% fragmentation rate (measured hourly). Alert at > 15%. At 30 nodes × 8 GPUs = 240 GPUs, 10% fragmentation = 24 wasted GPUs = ~$2,400/day at A100 spot pricing.

---

**Q: Explain point-in-time (PIT) correctness in a feature store. How do you guarantee it for 100M+ entities without full table scans?**

A: Point-in-time correctness means: when building a training dataset, each training example uses only feature values that were available at the label's event time. Violating this leaks future information into training, producing a model that appears to perform well offline but fails in production (label leakage).

**The naive implementation (wrong and slow):**

```sql
-- For each (entity, label_timestamp), find the latest feature value <= label_timestamp
-- This is O(entities × history_rows) — kills BigQuery at 100M entities
SELECT e.entity_id, e.label_timestamp, f.feature_value
FROM events e
LEFT JOIN feature_history f
  ON e.entity_id = f.entity_id
  AND f.feature_timestamp = (
    SELECT MAX(feature_timestamp)
    FROM feature_history
    WHERE entity_id = e.entity_id
      AND feature_timestamp <= e.label_timestamp
  )
```

At 100M entities × 30 days of history, this is 3B row join — hours of compute and thousands of dollars per training run.

**Optimized approach: partitioned point-in-time snapshots:**

Store features as hourly or daily snapshots partitioned by date. At PIT join time, only read the partition closest to each label timestamp:

```python
def get_pit_features_optimized(
    entity_df: pd.DataFrame,  # Columns: entity_id, label_timestamp
    feature_view: str,
    offline_store_path: str,
) -> pd.DataFrame:
    """
    For each entity+timestamp, read only the snapshot from that day.
    Avoids full table scans.
    """
    entity_df["snapshot_date"] = pd.to_datetime(
        entity_df["label_timestamp"]
    ).dt.date

    results = []
    for date, group in entity_df.groupby("snapshot_date"):
        # Read only that day's snapshot partition
        snapshot = pd.read_parquet(
            f"{offline_store_path}/{feature_view}/date={date}/",
            filters=[("entity_id", "in", group["entity_id"].tolist())]
        )
        # PIT join: each entity gets the snapshot from their label date
        merged = group.merge(snapshot, on="entity_id", how="left")
        results.append(merged)

    return pd.concat(results, ignore_index=True)
```

**Feast PIT join (production usage):**

```python
from feast import FeatureStore

fs = FeatureStore(repo_path=".")

# Entity dataframe with timestamps — Feast handles PIT correctness internally
entity_df = pd.DataFrame({
    "user_id":  ["u001", "u002", "u003"],
    "event_timestamp": [
        datetime(2024, 1, 15, 13, 0),   # PIT: features as of this timestamp
        datetime(2024, 1, 10, 9, 30),
        datetime(2024, 1, 20, 22, 0),
    ],
    "label": [1, 0, 1],
})

training_df = fs.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_profile:account_age_days",
        "user_activity:txn_count_7d",
        "user_risk:fraud_score_30d",
    ],
).to_df()
# Feast uses Spark or BigQuery ASOF joins — no future data leakage guaranteed
```

**Handling out-of-order streaming features:**

For streaming features (e.g., `txn_count_5min` computed in Flink), events arrive out-of-order. Use watermarks to prevent future-value writes:

```python
class FeatureStoreWriter:
    def write_feature(self, entity_id: str, feature_value: float,
                      event_time: datetime):
        # Reject writes for events older than watermark
        current_watermark = self.get_watermark(entity_id)
        if event_time < current_watermark - timedelta(minutes=10):
            metrics.counter("late_arrival_rejected")
            return  # Don't overwrite newer value with old one

        self.store.put(entity_id, feature_value, event_time)
        self.advance_watermark(entity_id, event_time)
```

**PIT correctness monitoring:**

```python
def verify_pit_correctness(training_df: pd.DataFrame) -> dict:
    """After building training dataset, verify no future leakage."""
    violations = (
        training_df["feature_timestamp"] > training_df["label_timestamp"]
    ).sum()
    pct_violations = violations / len(training_df)

    if pct_violations > 1e-5:  # Tolerance: 1 in 100K
        alert(f"PIT violations: {pct_violations:.2%} of training examples")
        raise ValueError("Training dataset has PIT violations — aborting training")

    return {"violations": violations, "total": len(training_df), "clean": True}
```

**SLA:** Zero PIT violations (strict). Every training run is gated by `verify_pit_correctness()`. A single PIT violation aborts training and pages the ML platform team.

---

**Q: How do you reduce LLM API costs by 70%+ without degrading user experience? Walk through a concrete architecture.**

A: At 10M LLM calls/day, cost optimization is the highest-leverage MLOps problem. The key insight is that most requests fall into repeatable patterns — same question, same context — and can be served from cache or routed to cheaper models.

**Four-layer cost optimization stack:**

**Layer 1 — Semantic caching (25–35% cost reduction):**

```python
from sentence_transformers import SentenceTransformer
import psycopg2, numpy as np

encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def semantic_cache_lookup(query: str, similarity_threshold: float = 0.97):
    embedding = encoder.encode(query)

    # pgvector ANN search — sub-millisecond for 10M cached queries
    cursor.execute("""
        SELECT response_text, 1 - (embedding <=> %s::vector) AS similarity
        FROM llm_cache
        WHERE created_at > NOW() - INTERVAL '7 days'
        ORDER BY embedding <=> %s::vector
        LIMIT 1
    """, (embedding.tolist(), embedding.tolist()))

    row = cursor.fetchone()
    if row and row["similarity"] >= similarity_threshold:
        prometheus.counter("cache_hit")
        return row["response_text"]  # Skip LLM call entirely

    return None  # Cache miss

def get_response(query: str) -> str:
    cached = semantic_cache_lookup(query)
    if cached:
        return cached

    response = call_llm(query)
    store_in_cache(query, response, encoder.encode(query))
    return response
```

Expected hit rate: 20–30% on support/Q&A workloads. 30% hit rate × $0.50/1K tokens × 10M calls = $150K/month saved.

**Layer 2 — Model routing by complexity (40% cost reduction):**

```python
# Lightweight classifier trained on golden examples
from sklearn.linear_model import LogisticRegression

def route_to_model(query: str) -> str:
    """
    Simple queries → 8B model ($0.07/1M tokens)
    Complex queries → 70B model ($0.50/1M tokens)
    """
    complexity_score = complexity_classifier.predict_proba([query])[0][1]

    if complexity_score < 0.3:
        return "llama-3-8b"    # 7x cheaper
    elif complexity_score < 0.7:
        return "llama-3-70b"
    else:
        return "gpt-4o"        # Only for most complex

model = route_to_model(user_query)
response = llm_client.generate(query=user_query, model=model)
```

Routing 70% of traffic to 8B model: 0.7 × (1 - 0.07/0.50) = 0.7 × 86% = 60% cost reduction on routed traffic.

**Layer 3 — Prompt caching for repeated system contexts (40% reduction on amortized tokens):**

```python
# Anthropic API: cache large system prompts
response = anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=500,
    system=[
        {
            "type": "text",
            "text": LARGE_SYSTEM_PROMPT,      # 50K tokens of FAQ + policy
            "cache_control": {"type": "ephemeral"}  # Cache for 5 minutes
        }
    ],
    messages=[{"role": "user", "content": user_query}]
)

# First call: charged full 50K tokens
# Calls 2-N within 5 min: 50K tokens at 10% of normal cost (cache read)
# 90% token cost reduction on system prompt across all calls in 5-min window
```

**Layer 4 — Speculative decoding for throughput (20% latency reduction, indirect cost saving):**

```python
# vLLM speculative decoding: draft model generates tokens, main model verifies
engine = AsyncLLMEngine.from_engine_args(EngineArgs(
    model="meta-llama/Llama-3-70B-Instruct",
    speculative_model="meta-llama/Llama-3-8B-Instruct",  # Draft model
    num_speculative_tokens=5,   # Generate 5 tokens speculatively, verify in parallel
    use_v2_block_manager=True,
))
# Result: 1.5-2x throughput increase → same compute serves more requests
```

**Combined impact (10M calls/day, avg 500 tokens/call, $0.50/1M tokens):**

| Optimization | Reduction | Daily Savings |
|-------------|-----------|--------------|
| Semantic cache (30% hit) | 30% of calls skipped | $750/day |
| Model routing (70% to 8B) | 60% cheaper on routed | $1,260/day |
| Prompt caching (50K sys prompt) | 40% on system tokens | $300/day |
| **Total** | **~72% cost reduction** | **~$2,310/day = $843K/year** |

**Token budget enforcement per tenant:**

```python
def enforce_budget(tenant_id: str, estimated_tokens: int) -> str:
    used = redis.incrby(f"tokens:{tenant_id}:{current_month()}", estimated_tokens)
    budget = get_monthly_budget(tenant_id)  # e.g., 10M tokens

    if used > budget * 1.1:    # Hard stop at 110% of budget
        raise BudgetExceeded(f"Tenant {tenant_id} exceeded monthly token budget")
    elif used > budget * 0.9:   # Soft limit: downgrade model at 90%
        return "llama-3-8b"     # Force cheaper model

    return get_preferred_model(tenant_id)
```

---

**Q: Your A/B test for a new recommendation model shows early positive results after 2 days. How do you decide whether to ship it?**

A: "Early positive results" is the most common cause of A/B test failures. The temptation to peek and ship early inflates false positive rates dramatically — checking daily at α=0.05 yields a 40% false positive rate by day 5, not 5%.

**Pre-test requirements (must complete before starting):**

```python
from statsmodels.stats.power import NormalIndPower
import numpy as np

def calculate_required_sample_size(
    baseline_metric=0.12,        # Current CTR/conversion rate
    minimum_detectable_effect=0.005,  # Want to detect 0.5% absolute lift
    alpha=0.05,                  # False positive rate
    power=0.80,                  # 80% chance to detect real effect
) -> int:
    analysis = NormalIndPower()
    # Effect size in standard deviation units
    effect_size = minimum_detectable_effect / np.sqrt(
        baseline_metric * (1 - baseline_metric)
    )
    n = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)
    return int(np.ceil(n))

# e.g., 3,800 users per variant — must reach this before evaluating
n_required = calculate_required_sample_size()
print(f"Required: {n_required:,} per variant. Run until both variants hit this.")
```

**Answering "can we ship after 2 days?":**

```python
def should_ship(variant_a, variant_b, days_running: int, n_required: int) -> dict:
    current_n = min(variant_a["users"], variant_b["users"])

    # 1. Sample size check (hard gate)
    if current_n < n_required:
        return {
            "decision": "WAIT",
            "reason": f"Need {n_required:,} users per variant, have {current_n:,}",
            "eta_days": (n_required - current_n) / (current_n / days_running),
        }

    # 2. Statistical significance with Bonferroni correction
    # (correct for multiple interim checks — each peek costs alpha budget)
    n_peeks = 3  # Pre-committed interim check points
    alpha_adjusted = 0.05 / n_peeks  # = 0.0167

    from scipy.stats import chi2_contingency
    table = np.array([
        [variant_b["conversions"], variant_b["users"] - variant_b["conversions"]],
        [variant_a["conversions"], variant_a["users"] - variant_a["conversions"]],
    ])
    chi2, pval, _, _ = chi2_contingency(table)

    rate_a = variant_a["conversions"] / variant_a["users"]
    rate_b = variant_b["conversions"] / variant_b["users"]
    relative_lift = (rate_b - rate_a) / rate_a

    if pval >= alpha_adjusted:
        return {"decision": "WAIT", "reason": f"Not significant (p={pval:.4f} > {alpha_adjusted})"}

    # 3. Business significance check (avoid shipping noise)
    if relative_lift < 0.02:  # < 2% relative lift is noise, not signal
        return {"decision": "WAIT", "reason": f"Lift {relative_lift:.1%} below business threshold"}

    # 4. Run for at least one full business cycle
    if days_running < 7:
        return {
            "decision": "WAIT",
            "reason": f"Only {days_running} days — need 7 for weekly cycle (weekend vs. weekday users differ)"
        }

    return {
        "decision": "SHIP",
        "pval": pval,
        "lift": f"{relative_lift:.1%}",
        "confidence": f"{(1-pval)*100:.1f}%",
    }
```

**If business pressure requires early decision — use Bayesian sequential testing:**

```python
from scipy.stats import beta as beta_dist

def bayesian_decision(variant_a, variant_b, rope_width=0.001) -> dict:
    """
    Bayesian approach: can peek anytime without alpha inflation.
    Decision: ship when P(B > A) > 0.95 (strong evidence).
    """
    # Beta posteriors with uniform prior
    alpha_a = 1 + variant_a["conversions"]
    beta_a = 1 + variant_a["users"] - variant_a["conversions"]
    alpha_b = 1 + variant_b["conversions"]
    beta_b = 1 + variant_b["users"] - variant_b["conversions"]

    # Monte Carlo comparison
    samples_a = beta_dist.rvs(alpha_a, beta_a, size=100_000)
    samples_b = beta_dist.rvs(alpha_b, beta_b, size=100_000)

    prob_b_better = (samples_b > samples_a).mean()
    expected_lift = (samples_b - samples_a).mean()

    if prob_b_better > 0.95:
        return {"decision": "SHIP", "prob_b_better": prob_b_better, "expected_lift": expected_lift}
    elif prob_b_better < 0.05:
        return {"decision": "KEEP_CONTROL", "prob_b_better": prob_b_better}
    else:
        return {"decision": "CONTINUE", "prob_b_better": prob_b_better}
```

**The answer for the 2-day scenario:**

Almost certainly WAIT — unless you pre-committed to a Bayesian sequential test with `P(B>A) > 0.95` as the stopping rule AND have reached that threshold. Frequentist tests require minimum sample size + 7-day run. The 2-day result is likely due to novelty effect (users engage with new recommendations because they're unfamiliar, not because they're better).

---

**Q: How do you implement automated retraining triggered by drift detection in production — including preventing false retraining loops?**

A: Automated retraining is easy to implement incorrectly: a naive system retriggers training on every drift alert, wastes compute, and can create feedback loops (model trained on drifted data generates predictions that cause more drift). Good drift-triggered retraining requires multi-layer detection, cool-down periods, and quality gates.

**Multi-layer drift detection (fast to slow):**

```python
class DriftDetectionPipeline:

    def detect_input_drift(self, reference_data, current_window) -> dict:
        """Layer 1: Statistical drift on input features (fast, label-free)."""
        drifted_features = []
        for feature in numerical_features:
            psi = self.compute_psi(reference_data[feature], current_window[feature])
            if psi > 0.2:
                drifted_features.append({"feature": feature, "psi": psi})
        return {"drifted_features": drifted_features,
                "drift_score": len(drifted_features) / len(numerical_features)}

    def detect_prediction_drift(self, reference_preds, current_preds) -> dict:
        """Layer 2: Output distribution shift (fast, always available)."""
        psi = self.compute_psi(reference_preds, current_preds)
        ks_stat, _ = ks_2samp(reference_preds, current_preds)
        return {"psi": psi, "ks": ks_stat, "drifted": psi > 0.2}

    def detect_concept_drift(self, cohort_date: str) -> dict:
        """Layer 3: AUC degradation when labels arrive (slow, 1-7 day delay)."""
        preds = load_predictions(cohort_date)
        labels = load_labels(cohort_date)   # May not be available yet
        if labels is None:
            return {"available": False}

        cohort_auc = roc_auc_score(labels, preds["probability"])
        baseline_auc = 0.91  # From last training run
        degradation = baseline_auc - cohort_auc
        return {"auc": cohort_auc, "degradation": degradation,
                "drifted": degradation > 0.02}

    def compute_psi(self, reference, current, bins=10) -> float:
        ref_pct, _ = np.histogram(reference, bins=bins, density=True)
        cur_pct, _ = np.histogram(current, bins=bins, density=True)
        ref_pct = (ref_pct + 1e-10) / (ref_pct + 1e-10).sum()
        cur_pct = (cur_pct + 1e-10) / (cur_pct + 1e-10).sum()
        return np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
```

**Retraining decision logic with cool-down:**

```python
import redis

r = redis.Redis()
COOLDOWN_SECONDS = 7 * 24 * 3600  # 7-day cool-down between retrains

def should_retrain(model_name: str, drift_signals: dict) -> tuple[bool, str]:
    # Cool-down guard: prevent retraining more than once per week
    last_retrain_key = f"last_retrain:{model_name}"
    last_retrain = r.get(last_retrain_key)
    if last_retrain:
        elapsed = time.time() - float(last_retrain)
        if elapsed < COOLDOWN_SECONDS:
            return False, f"Cool-down active ({elapsed/86400:.1f}d since last retrain)"

    # Threshold logic: require multiple signals, not just one
    triggers = []
    if drift_signals["input_drift"]["drift_score"] > 0.3:       # > 30% features drifted
        triggers.append("input_drift")
    if drift_signals["prediction_drift"]["psi"] > 0.25:
        triggers.append("prediction_drift")
    if drift_signals["concept_drift"].get("degradation", 0) > 0.02:
        triggers.append("concept_drift")
    if drift_signals.get("new_data_volume", 0) > 500_000:       # 500K new labeled examples
        triggers.append("data_volume")

    # Require at least 2 independent signals to avoid false triggers
    if len(triggers) >= 2:
        r.set(last_retrain_key, time.time(), ex=COOLDOWN_SECONDS + 86400)
        return True, f"Triggered by: {', '.join(triggers)}"

    return False, f"Only {len(triggers)} signal(s): {triggers} (need ≥ 2)"

# Airflow DAG: daily check
should_train, reason = should_retrain("purchase_propensity", drift_signals)
if should_train:
    trigger_training_pipeline(reason=reason)
    log_to_mlflow({"trigger_reason": reason, "drift_signals": drift_signals})
else:
    log_to_mlflow({"skipped_reason": reason})
```

**Quality gate (prevent feedback loops):**

```python
def promotion_gate(challenger_run_id: str, champion_run_id: str) -> bool:
    """
    New model must beat champion by a meaningful margin.
    Prevents drift-trained model from becoming the new champion
    if it just learned the drifted distribution.
    """
    challenger_auc = mlflow.get_metric(challenger_run_id, "auc_test")
    champion_auc   = mlflow.get_metric(champion_run_id,   "auc_test")

    # Also evaluate on a held-out "golden" dataset with known distribution
    challenger_golden = mlflow.get_metric(challenger_run_id, "auc_golden_set")
    champion_golden   = mlflow.get_metric(champion_run_id,   "auc_golden_set")

    # Must improve on test set AND not degrade on golden set
    if challenger_auc > champion_auc - 0.005 and challenger_golden >= champion_golden - 0.01:
        promote(challenger_run_id)
        return True
    else:
        alert(f"Challenger failed gate: test AUC={challenger_auc:.4f} "
              f"(champion={champion_auc:.4f}), golden AUC={challenger_golden:.4f}")
        return False
```

The "golden set" — a frozen, balanced, labeled dataset maintained separately from the live data stream — is the critical safeguard. Even if the live distribution has drifted, the model must still perform on the golden distribution, preventing it from overfitting to transient drift.

**Monitoring retraining health:**

| Metric | Alert Threshold | Meaning |
|--------|----------------|---------|
| `days_since_last_retrain` | > 60 days | Model may be stale |
| `retraining_frequency_7d` | > 3 per week | Possible false trigger loop |
| `promotion_gate_pass_rate` | < 50% over 30 days | Training pipeline quality issue |
| `golden_set_auc_trend` | Decreasing > 0.01/month | Genuine concept drift requiring data strategy review |
