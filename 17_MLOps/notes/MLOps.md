# MLOps — Machine Learning Operations

```
MLOps — Machine Learning Operations (Overview)
├── Why MLOps Exists
│   ├── Traditional software: deterministic — same code → same output
│   ├── ML: non-deterministic — model behavior changes with data
│   └── Three artifacts: Code + Data + Model (all must be versioned)
├── The Four Pipelines
│   ├── CI: test code + validate features + lint pipelines
│   ├── CT (Continuous Training): data trigger → train → evaluate → promote
│   ├── CD: deploy new model version to serving infrastructure
│   └── CM (Continuous Monitoring): drift + label monitoring + alerting
├── Feature Stores
│   ├── Offline store: S3/BigQuery — training, point-in-time join
│   ├── Online store: Redis/DynamoDB — inference, P99 < 5ms
│   ├── Materialization: batch job pushes offline → online
│   └── Prevents training-serving skew via shared computation library
├── Continuous Training Pipelines
│   ├── Triggers: schedule, drift threshold, data volume, business KPI
│   ├── Validation gate: Great Expectations before training
│   ├── Evaluation gate: champion vs challenger comparison
│   └── Delayed label handling: proxy metrics for monitoring
├── Model Serving
│   ├── Synchronous REST: low-latency, user-facing
│   ├── Async batch: throughput-optimized, non-latency-critical
│   ├── Streaming: Kafka-triggered inference
│   └── Shadow/Canary/A/B/Blue-Green: progressive rollout strategies
├── Model Registry & Experiment Tracking
│   ├── MLflow: 4 components — Tracking, Projects, Models, Registry
│   ├── W&B: collaborative experiment tracking + sweeps
│   ├── Staging workflow: None → Staging → Production → Archived
│   └── Model aliases: @champion, @challenger (MLflow 2.x)
├── Drift & Monitoring
│   ├── Data drift (covariate shift): P(X) changes
│   ├── Concept drift: P(Y|X) changes — world changes, not data
│   ├── PSI thresholds: < 0.1 OK, 0.1–0.2 monitor, > 0.2 retrain
│   └── Evidently AI, WhyLabs, Arize AI: monitoring platforms
├── LLMOps
│   ├── vLLM: PagedAttention + continuous batching
│   ├── RAG: chunk → embed → vector DB → retrieve → rerank → LLM
│   ├── RAGAS: faithfulness, answer_relevancy, context_precision
│   └── TTFT, TPOT, TPS: key LLM serving metrics
├── Responsible AI
│   ├── Fairness: demographic parity, equalized odds
│   ├── Explainability: SHAP, LIME, Fairlearn
│   ├── Governance: SR 11-7, ML-BOM, GDPR right-to-explanation
│   └── Model cards: training data, metrics, limitations, intended use
└── GPU Infrastructure
    ├── ZeRO stages: optimizer (S1) + gradients (S2) + params (S3)
    ├── MIG: partition A100/H100 into isolated GPU instances
    ├── InfiniBand: high-bandwidth GPU-to-GPU for Tensor Parallelism
    └── Gradient checkpointing + accumulation: memory optimization
```

## First Principles

- MLOps exists because ML adds two new dimensions to software operations: data as a first-class versioned artifact, and model behavior that changes over time without code changes.
- The four pipelines (CI, CT, CD, CM) together form the production ML lifecycle — omitting any one creates a gap that causes silent failures.
- Feature stores solve the coordination problem: multiple teams need the same features computed correctly — centralize once, serve everywhere, prevent skew.
- Monitoring must cover infrastructure AND model quality — a model can be "serving" while producing degraded predictions; infrastructure metrics alone won't catch this.
- Responsible AI is an engineering requirement: fairness metrics, explainability, and model cards are required for regulated industries and increasingly expected across all production ML systems.

## Why MLOps Exists: The Production ML Problem

Traditional software deployment follows a deterministic path: code is written, tested, and deployed. The same code always produces the same output. Machine learning breaks this model entirely.

**The Three Artifacts of MLOps:**

```
Traditional DevOps:  Code → Build → Deploy → Monitor
                     (deterministic)

MLOps:               Code + Data + Model → Train → Validate → Deploy → Monitor
                     (non-deterministic — model behavior changes with data)
```

**Why ML in Production is Hard:**

1. **Two types of drift:**
   - *Data Drift:* Input data distribution changes (e.g., users shift from desktop to mobile)
   - *Concept Drift:* The relationship between input and output changes (e.g., consumer behavior post-pandemic)

2. **Delayed feedback loops:** In production, you might not know if a prediction was correct for days or weeks (e.g., did this loan default?)

3. **Resource intensity:** Training requires GPUs/TPUs, often for days. Inference needs low-latency GPU access for LLMs.

4. **Reproducibility crisis:** Without proper tooling, you cannot recreate "that model that worked last Tuesday" because it depended on a specific data snapshot, random seed, and hyperparameter combination.

MLOps solves these problems by extending DevOps practices to handle **data versioning**, **model registries**, **continuous training pipelines**, and **drift monitoring**.

***

## The Intersection of Three Worlds

MLOps sits at the intersection of:

| Discipline | Contribution to MLOps |
|------------|----------------------|
| **Machine Learning** | Model design, feature engineering, hyperparameter tuning, evaluation metrics |
| **DevOps** | CI/CD pipelines, infrastructure as code, monitoring, incident response |
| **Data Engineering** | Data pipelines, feature stores, data quality, schema management |

For a DevOps/SRE engineer, you are not expected to build models, but you **are** expected to build the infrastructure that makes ML reproducible, scalable, and observable.

***

## The MLOps Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    MLOPS LIFECYCLE                               │
│                                                                  │
│  Design → Experimentation → Training → Validation → Deployment  │
│     ▲                                                      │    │
│     └────────────────── Monitoring ────────────────────────┘    │
│                                                                  │
│  Four Continuous Pipelines:                                      │
│  - CI: Code linting, unit tests, schema validation               │
│  - CT: Data validation → training → evaluation → registry        │
│  - CD: Shadow → canary → production rollout                      │
│  - CM: Drift detection → alerting → retrain trigger              │
└─────────────────────────────────────────────────────────────────┘
```

### The Four Pipelines

| Pipeline | Trigger | Output | Owner |
|----------|---------|--------|-------|
| **CI** (Continuous Integration) | Every commit / PR | Validated code, passing tests | DevOps/Engineering |
| **CT** (Continuous Training) | Schedule, drift, data volume, KPI drop | New model version in registry | Data Science + ML Eng |
| **CD** (Continuous Delivery) | Registry promotion approval | Model deployed to production | DevOps/Platform |
| **CM** (Continuous Monitoring) | Always running | Alerts, drift reports, retrain triggers | SRE/ML Eng |

> [!IMPORTANT]
> Never conflate CI and CT. CI tests code. CT produces a new model artifact. They have different triggers, different outputs, and different failure modes.

***

## Core MLOps Components

### 1. Feature Store

A centralized system that stores, manages, and serves ML features. The core problem it solves is **training-serving skew** — ensuring that the exact same feature transformations used during training are applied during inference.

```
                    ┌─────────────────────────────────┐
                    │         FEATURE STORE            │
                    │                                 │
  Raw Data ──────── │  Feature Pipeline (shared code) │
                    │                                 │
                    ├──────────────┬──────────────────┤
                    │ Offline Store│  Online Store     │
                    │ (S3/BigQuery)│  (Redis/Cassandra)│
                    │ Historical   │  Low-latency      │
                    │ batch data   │  real-time lookup │
                    └──────┬───────┴────────┬──────────┘
                           │                │
                      Training Jobs    Inference Service
                      (same features)  (same features)
```

**Key insight:** A Feature Store's value is not storage — it is the **guarantee of feature parity** between training and serving.

**Tools:** Feast (OSS), Hopsworks, Tecton, Vertex AI Feature Store, SageMaker Feature Store

***

### 2. Model Registry

A versioned catalog of trained models with metadata (training metrics, dataset version, framework version, code commit). It serves as the promotion gate before models reach production.

**Staging Workflow:**

```
Training Run
     │
     ▼ (auto-register)
  None stage
     │
     ▼ (CI validation job passes)
  Staging stage
     │
     ▼ (shadow/canary testing passes)
  Production stage
     │
     ▼ (superseded by newer version)
  Archived stage
```

**Tools:** MLflow Model Registry, SageMaker Model Registry, Vertex AI Model Registry

***

### 3. Experiment Tracking

Records inputs (dataset version, hyperparameters, code commit) and outputs (metrics, artifacts) of every training run.

```python
import mlflow

mlflow.set_experiment("fraud_classifier_v3")

with mlflow.start_run(tags={"data_version": "2024-01-v3", "commit": "abc123"}):
    mlflow.log_params({"n_estimators": 200, "max_depth": 8})
    mlflow.log_metrics({"auc": 0.95, "f1": 0.89})
    mlflow.sklearn.log_model(model, "model")
```

**Tools:** MLflow Tracking, Weights & Biases, Neptune AI

***

### 4. Data Versioning (DVC)

DVC extends Git to version large binary files (datasets, model artifacts) by storing pointers in Git while data lives in remote storage.

```bash
# Track a dataset
dvc add data/training/
dvc remote add -d s3remote s3://my-bucket/dvc-cache
dvc push

# Commit the .dvc metadata file to git
git add data/training.dvc .gitignore
git commit -m "Add training dataset v3"

# Reproduce the full pipeline
dvc repro
```

***

### 5. Model Serving

Specialized inference servers optimized for ML workloads:

| Server | Best For | Key Features |
|--------|----------|--------------|
| **KServe** | Kubernetes-native serving | Autoscaling, canary, transformers |
| **NVIDIA Triton** | Multi-framework, multi-model | Dynamic batching, concurrent execution |
| **TorchServe** | PyTorch models | Custom handlers, multi-model |
| **TensorFlow Serving** | TensorFlow SavedModel | gRPC-first, model versioning |
| **vLLM** | LLM inference | PagedAttention, continuous batching |

***

## MLOps vs. DevOps Comparison

| Dimension | DevOps | MLOps |
|-----------|--------|-------|
| Primary artifact | Code binary | Code + Data + Model weights |
| Version control | Git (code) | Git + DVC (data) + Registry (model) |
| CI test | Unit test | Unit test + schema check + data validation |
| CD gate | Pass all tests | Pass tests + beat champion model metrics |
| Monitoring | CPU, memory, error rate | Drift, confidence distribution, business KPI |
| Rollback | Redeploy old container | Promote previous model version from registry |
| Unique risk | Logic bugs | Silent degradation with healthy infrastructure |

> [!TIP]
> In MLOps, a "successful" deployment (200 OK, low latency) is not enough. You must monitor for **Data Drift** — when the real-world data starts to look different from the training data, causing the model's performance to drop over time.

***

## Key MLOps Patterns

### Shadow Deployment

The new model receives 100% of live production traffic, but its predictions are **not** sent to the user. Instead, we compare its results against the existing model to see how it performs in the real world without any risk to the business.

**Use when:** First validation of a new model before any live traffic exposure.

### Canary Rollout

Route a small percentage (5-10%) of live traffic to the new model. Compare metrics (latency, error rate, business KPIs) against the champion. Gradually increase traffic if metrics are acceptable.

**Use when:** Model has passed shadow testing; validating at production scale.

### A/B Testing

Controlled split for statistical measurement of business metric impact. Requires significance testing before full rollout.

**Use when:** Measuring business KPI impact (CTR, conversion rate) with statistical confidence.

### Blue/Green Swap

Instant full swap from old to new model. Highest risk, fastest rollout.

**Use when:** Canary is not feasible due to infrastructure constraints.

***

## Continuous Training (CT) Pipeline Design

### CT Trigger Types

| Trigger | When to Use | Risk |
|---------|-------------|------|
| **Scheduled** (weekly, monthly) | Low-frequency data changes, stable domains | May retrain with insufficient new data |
| **Data volume** (N new rows) | High-velocity streams | May trigger too frequently on spiky data |
| **Drift threshold** | When input drift is detected | Delayed — drift must first accumulate |
| **Business KPI drop** | When business metric falls below threshold | Requires closed feedback loop with labels |
| **Explicit trigger** | Regulated environments, manual review required | Slowest, most controlled |

### The Delayed Label Problem

For many domains, ground truth labels arrive days to weeks after prediction:
- Fraud detection: 30 days
- Loan default: 90 days
- Churn: Variable

**You cannot retrain on accuracy in real time.** Use **proxy metrics** for real-time triggers:
- Data drift score (PSI, KS test)
- Confidence distribution shift
- Output entropy
- Business proxy metrics (chargeback rate, dispute rate)

Use accuracy-based triggers on a delayed schedule after labels arrive.

***

## CT Pipeline with Validation Gates

```
Raw Data
    │
    ▼
┌─────────────────────┐
│ Data Validation     │  ← Great Expectations / TFX
│ - Schema check      │    Fail: abort, alert, keep champion
│ - Volume check      │
│ - Distribution check│
└──────────┬──────────┘
           │ PASS
           ▼
┌─────────────────────┐
│ Feature Engineering │  ← Feature Store materialization
│ - Same transforms   │    as training baseline
│ - Validate feature  │
│   distributions     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Model Training      │  ← GPU cluster / SageMaker / Vertex AI
│ - Checkpoint to S3  │    (spot-safe)
│ - Log all params,   │
│   metrics, data     │
│   version to MLflow │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Model Evaluation    │  ← Validation gate
│ - Compare vs.       │    Fail: reject candidate, keep champion
│   champion metrics  │
│ - Latency SLA met?  │
│ - Fairness checks?  │
│ - Behavioral tests  │
└──────────┬──────────┘
           │ PASS
           ▼
┌─────────────────────┐
│ Registry Push       │  ← Stage: Staging (not Production yet)
│ - Tag: data version,│
│   code commit,      │
│   run ID            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Promotion Gate      │  ← Manual approval OR automated
│ - In regulated envs:│    mandatory human sign-off
│   mandatory sign-off│    + model card generation
└──────────┬──────────┘
           │ APPROVED
           ▼
     CD Pipeline
  (Shadow → Canary → Production)
```

***

## Troubleshooting Common ML Issues

### Scenario: Model returns 200 OK but predictions are wrong

1. **Check Input Schema:** Did the frontend change the JSON format? (e.g., sending strings instead of floats)
2. **Check Feature Parity:** Are serving transforms identical to training transforms? (This is why Feature Stores exist)
3. **Check Model Version:** Did CI/CD push a half-trained model? Check the Model Registry.

### Scenario: GPU Pod stuck in `Pending`

1. **Check Capacity:** `kubectl describe node` — are all GPU slots taken?
2. **Check Drivers:** Are NVIDIA drivers compatible with the CUDA version in the container?
3. **Check Quotas:** Is the namespace hitting a ResourceQuota limit for `requests.nvidia.com/gpu`?

### Scenario: Drift alerts fire, but labels won't arrive for days

1. Check whether the alert is data drift, concept drift, or upstream schema/freshness issue
2. Review proxy metrics: confidence shifts, output distribution, feature freshness, business KPI movement
3. Decide: hold rollout, retrain, or rollback to a safer champion model

### Scenario: Batch inference misses the business delivery window

1. Check queue time, dataset growth, retries, partition skew, storage throughput
2. Verify whether upstream data arrived late or cluster was starved by higher-priority workloads
3. Treat as an SLA issue, not merely a long-running job

***

## Production Best Practices

| Practice | Why It Matters |
|----------|----------------|
| **Model Checkpointing** | During long training runs, save checkpoints to S3. If a Spot Instance is reclaimed, resume from checkpoint instead of starting over. |
| **A/B Testing** | Never replace a model 100%. Use Istio/Service Mesh to split traffic and compare business KPIs. |
| **Reproducibility** | Every model must be traceable to the exact Git commit, DVC data version, and hyperparameters. |
| **Anti-Pattern: Hardcoded Weights** | Never bake model files (`.h5`, `.pt`) into Docker images. The image should be the "Server" and pull the "Model" from a URI at startup. |
| **Feature Freshness Monitoring** | Stale features in the online store cause training-serving skew even with a Feature Store. Monitor freshness as a first-class SLI. |
| **Prompt Versioning (LLMs)** | System prompt changes are deployments. Version prompts alongside model weights. |

***

## MLOps Cheat Sheet

| Term | SRE Definition |
|------|----------------|
| **MLflow** | The "Git" for ML models and experiments — tracks params, metrics, artifacts |
| **Triton** | NVIDIA's high-performance inference server for multi-framework serving |
| **CUDA** | NVIDIA's parallel computing platform for GPU-accelerated ML |
| **Cold Start** | The delay when a model is loaded into GPU memory for the first time |
| **Seldon Core** | Kubernetes operator for managing complex ML graphs and routing |
| **ONNX** | Universal format to move models between frameworks (PyTorch → TensorFlow) |
| **Feature Store** | Guarantees feature parity between training and serving |
| **Training-Serving Skew** | Divergence between feature transforms at train time vs. serve time |
| **Shadow Deployment** | New model sees live traffic but predictions are discarded — zero risk validation |
| **Continuous Training** | Automated pipeline from data validation to model promotion |

***

## Companion Files

This file is an overview. For deep dives, see:

| File | Topic |
|------|-------|
| [`notes.md`](notes.md) | Comprehensive MLOps theory — lifecycle, drift, GPU infrastructure, lineage |
| [`mlops-platforms-tools.md`](mlops-platforms-tools.md) | MLflow, Kubeflow, SageMaker, Vertex AI comparison and architecture |
| [`mlops-feature-stores-and-pipelines.md`](mlops-feature-stores-and-pipelines.md) | Feature Stores (Feast, Tecton), CT pipeline design, Kubeflow/Airflow |
| [`mlops-llmops-and-advanced-serving.md`](mlops-llmops-and-advanced-serving.md) | LLMOps, vLLM, RAG pipelines, GPU parallelism, cost control |
| [`mlops-monitoring-observability.md`](mlops-monitoring-observability.md) | Drift detection, Evidently AI, alerting strategies, runbooks |

***

## System Design Perspective

**Full ML Platform Stack (Production-Grade)**
- Data: Kafka → Spark Streaming → Delta Lake (versioned, time-travel) → Great Expectations validation.
- Features: Feast; offline BigQuery; online Redis; materialization scheduled every 15 minutes; freshness alert if lag > 30 minutes.
- Training: Kubeflow Pipelines orchestration; GPU node pool (A100 MIG for small models, full A100 for large); MLflow Tracking + Registry.
- Serving: KServe InferenceService for REST + gRPC; vLLM for LLMs; Triton for GPU batch inference; Istio for traffic management.
- Monitoring: Evidently AI for drift reports; Prometheus + DCGM Exporter for GPU metrics; Grafana dashboards per model endpoint.
- Governance: model card required in registry before production promotion; SHAP explainability report attached to each model version; fairness evaluation run as part of CT pipeline.

**Scaling Considerations**
- At 10K req/sec: single-region KServe with HPA on requests/second metric.
- At 100K req/sec: multi-region with regional model replicas, regional feature stores, global load balancing.
- At 1M req/sec: hierarchical caching (semantic cache → CDN-level cache for static responses), request batching, model quantization (INT8/INT4).
- Cost model: profile GPU utilization monthly; right-size instance types quarterly; evaluate quantization tradeoffs annually.
