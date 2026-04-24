# MLOps — Deep Theory Notes

## Table of Contents

1. [MLOps Lifecycle](#1-mlops-lifecycle)
2. [Feature Stores](#2-feature-stores)
3. [Continuous Training Pipelines](#3-continuous-training-pipelines)
4. [ML Platforms](#4-ml-platforms)
5. [Model Serving](#5-model-serving)
6. [Model Registry](#6-model-registry)
7. [Experiment Tracking](#7-experiment-tracking)
8. [Data Versioning with DVC](#8-data-versioning-with-dvc)
9. [Model Drift and Monitoring](#9-model-drift-and-monitoring)
10. [A/B Testing for Models](#10-ab-testing-for-models)
11. [LLMOps](#11-llmops)
12. [Responsible AI and Bias Detection](#12-responsible-ai-and-bias-detection)
13. [GPU Infrastructure](#13-gpu-infrastructure)
14. [ML Metadata Lineage (MLMD)](#14-ml-metadata-lineage-mlmd)

***

## 1. MLOps Lifecycle

MLOps applies DevOps principles to the full machine learning lifecycle. The core difference from DevOps: code alone is not the artifact. Code, data, and model weights are all first-class versioned artifacts, and each combination of the three produces a different production system.

### The Four Pipelines

| Pipeline | Trigger | Scope |
|---|---|---|
| **CI** | Every commit / PR | Lint, unit test, schema validate |
| **CT** (Continuous Training) | Schedule, drift, data volume, KPI drop | Data validation → training → evaluation → registry |
| **CD** (Continuous Delivery) | Registry promotion approval | Shadow → canary → production |
| **CM** (Continuous Monitoring) | Always running | Drift detection → alerting → retrain trigger |

> [!IMPORTANT]
> Never conflate CI and CT. CI tests code. CT produces a new model artifact. They have different triggers, different outputs, and different failure modes.

### Lifecycle Stages

```
Data Collection
      │
      ▼
Data Validation ──► Fail fast (schema, volume, distribution checks)
      │
      ▼
Feature Engineering ──► Feature Store (offline + online)
      │
      ▼
Model Training ──► Experiment Tracker (params, metrics, artifacts)
      │
      ▼
Model Evaluation ──► Compare vs. champion; fairness/bias checks
      │
      ▼
Model Registry ──► Staging stage; model card generation
      │
      ▼
Model Serving ──► Shadow → Canary → Production
      │
      ▼
Monitoring ──► Drift detection → retrain trigger → back to CT
```

### MLOps vs. DevOps Comparison

| Dimension | DevOps | MLOps |
|---|---|---|
| Primary artifact | Code binary | Code + Data + Model weights |
| Version control | Git (code) | Git + DVC (data) + Registry (model) |
| CI test | Unit test | Unit test + schema check + data validation |
| CD gate | Pass all tests | Pass tests + beat champion model metrics |
| Monitoring | CPU, memory, error rate | Drift, confidence distribution, business KPI |
| Rollback | Redeploy old container | Promote previous model version from registry |
| Unique risk | Logic bugs | Silent degradation with healthy infrastructure |

***

## 2. Feature Stores

### The Problem Feature Stores Solve

Without a Feature Store, training and serving code diverge. This causes **training-serving skew** — the most common silent failure in production ML.

```
WITHOUT a Feature Store:
  Training:  raw → custom_transform_v1.py → feature_matrix → model
  Serving:   raw → custom_transform_v2.py → feature_vector → model
  Result: model returns wrong predictions despite 200 OK

WITH a Feature Store:
  Training:  store.get_historical_features() → feature_matrix → model
  Serving:   store.get_online_features()     → feature_vector → model
  Result: guaranteed transformation parity
```

> [!TIP]
> The click moment for interviewers: a Feature Store's value is not storage — it is the architectural guarantee of feature parity between training and serving.

### Offline vs. Online Store

| Dimension | Offline Store | Online Store |
|---|---|---|
| Purpose | Historical features for training and batch inference | Low-latency feature retrieval for real-time inference |
| Storage | S3 + Parquet, BigQuery, Delta Lake | Redis, DynamoDB, Cassandra, Bigtable |
| Access pattern | Large batch reads (entity + timestamp range) | Single-entity lookup in < 10 ms |
| Latency | Minutes to hours | < 10 ms p99 |
| Point-in-time correctness | Required — retrieves values as they existed at a past timestamp | N/A — always returns latest value |
| Freshness | Updated by materialization job | Materialized from offline store on schedule or via streaming |

### Point-in-Time Correctness

When generating training datasets, each training example must only use feature values available at prediction time — not future values. Without point-in-time joins, you introduce **label leakage**: the model trains on information it would not have had in production, producing inflated training metrics and poor production performance.

```python
# Feast point-in-time correct training data retrieval
from feast import FeatureStore
import pandas as pd
from datetime import datetime

store = FeatureStore(repo_path=".")

entity_df = pd.DataFrame({
    "driver_id": [1001, 1002, 1003],
    "event_timestamp": [
        datetime(2024, 1, 1),
        datetime(2024, 1, 15),
        datetime(2024, 2, 1),
    ],
})

# For each entity+timestamp, retrieves the feature values
# as they existed at that timestamp — not today's values
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
).to_df()
```

### Materialization Pipeline

```
Offline Store ──► Materialization Job ──► Online Store
(cold, historical)   (scheduled or         (hot, fresh)
                      streaming)
```

> [!CAUTION]
> Materialization lag is a production risk. A 2-hour stale online store combined with a model trained on fresh data is implicit training-serving skew — even while using a Feature Store. Always monitor feature freshness as a first-class SLI and alert when lag exceeds the threshold.

### Feature Store Comparison

| Tool | Managed | Online Store | Streaming | Best For |
|---|---|---|---|---|
| **Feast** | Self-hosted | Redis, DynamoDB, Bigtable | Kafka (limited) | OSS control |
| **Hopsworks** | Self-hosted or cloud | RonDB | Kafka native | SQL + streaming enterprise |
| **Tecton** | Fully managed SaaS | DynamoDB, Redis | Spark Streaming, Flink | Zero-ops overhead |
| **Vertex AI FS** | GCP managed | Bigtable | Dataflow | GCP-native stacks |
| **SageMaker FS** | AWS managed | DynamoDB | Kinesis | AWS-native stacks |

### Feature Tiers by Freshness Requirement

| Feature Type | Examples | Required Freshness | Recommended Path |
|---|---|---|---|
| Static / slow-changing | Demographics, credit score band | Hours to days | Batch materialization |
| Session-level | Last 10 purchases, recent clicks | Minutes | Streaming materialization (Kafka → Flink) |
| Real-time | Current cart value, live transaction | Seconds | On-demand computation at inference time |

***

## 3. Continuous Training Pipelines

### CT Trigger Types

| Trigger | When to Use | Risk |
|---|---|---|
| **Scheduled** (weekly, monthly) | Low-frequency data changes, stable domains | May retrain with insufficient new data |
| **Data volume** (N new rows) | High-velocity streams | May trigger too frequently on spiky data |
| **Drift threshold** | When input drift is detected | Delayed — drift must first accumulate |
| **Business KPI drop** | When business metric falls below threshold | Requires closed feedback loop with labels |
| **Explicit trigger** | Regulated environments, manual review required | Slowest, most controlled |

> [!IMPORTANT]
> Never say "we retrain when accuracy drops" in an interview. Accuracy requires labels. Labels are delayed by days to weeks. Use proxy metrics — drift score, confidence distribution, output entropy — for real-time triggers. Use accuracy-based triggers on a delayed schedule after labels arrive.

### CT Pipeline with Validation Gates

```
Raw Data
    │
    ▼
┌─────────────────────┐
│ Data Validation     │  ← Great Expectations / TFX ExampleValidator
│ - Schema check      │    Fail: abort, alert, keep champion serving
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

### Delayed Label Problem

For many domains, ground truth labels arrive days to weeks after prediction (fraud: 30 days, loan default: 90 days, churn: variable). Strategies:

1. **Proxy metrics**: Monitor output distribution shifts as leading indicators even before labels arrive.
2. **Early feedback sampling**: Randomly sample predictions, expedite human labeling.
3. **Delayed evaluation pipeline**: Join predictions with labels as they arrive; continuously update AUC/precision-recall.
4. **Cohort tracking**: Track performance by prediction cohort date. Compare day-30 metrics across cohorts to spot degradation trends.

***

## 4. ML Platforms

### Kubeflow

Kubeflow is the Kubernetes-native MLOps platform. Components:

| Component | Purpose |
|---|---|
| **KFP (Kubeflow Pipelines)** | Orchestrate ML workflows as containerized DAGs; artifact lineage via MLMD |
| **KServe** | Model serving with autoscaling, canary rollout, transformer hooks |
| **Katib** | Hyperparameter tuning: Grid, Random, Bayesian, PBT |
| **Training Operator** | Manages PyTorchJob, TFJob, MXNetJob — fault-tolerant distributed training |
| **Notebooks** | Managed JupyterLab in the cluster, same environment as production |

```python
# Kubeflow Pipelines SDK v2 example
from kfp import dsl
from kfp.dsl import component, pipeline, Dataset, Model, Input, Output

@component(base_image="python:3.11", packages_to_install=["scikit-learn", "mlflow"])
def train_model(
    input_dataset: Input[Dataset],
    model_artifact: Output[Model],
    mlflow_tracking_uri: str,
    n_estimators: int = 100,
):
    import mlflow, pickle, pandas as pd
    from sklearn.ensemble import RandomForestClassifier

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    df = pd.read_parquet(input_dataset.path)
    X, y = df.drop("label", axis=1), df["label"]

    with mlflow.start_run():
        model = RandomForestClassifier(n_estimators=n_estimators)
        model.fit(X, y)
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_metric("train_accuracy", model.score(X, y))
        mlflow.sklearn.log_model(model, "model")

    with open(model_artifact.path, "wb") as f:
        pickle.dump(model, f)


@pipeline(name="ct-pipeline")
def ct_pipeline(dataset_uri: str, mlflow_uri: str):
    train_task = train_model(
        input_dataset=dataset_uri,
        mlflow_tracking_uri=mlflow_uri,
    )
    # Request GPU
    train_task.set_accelerator_type("NVIDIA_TESLA_T4").set_accelerator_limit(1)
    train_task.set_memory_limit("16G")
```

### MLflow

MLflow is the framework-agnostic experiment and model lifecycle tool.

| Component | Purpose |
|---|---|
| **MLflow Tracking** | Log params, metrics, artifacts per run; compare runs |
| **MLflow Projects** | Reproducible code packages (conda env + entry point) |
| **MLflow Models** | Standard model packaging (Python function, ONNX, TF, PyTorch) |
| **MLflow Model Registry** | Versioned catalog with staging workflow, aliases, annotations |

Key MLflow 2.x concept: **model aliases** (`@champion`, `@challenger`) replace hard stages (`Staging`, `Production`) for more flexible workflows. The serving layer reads the `@champion` alias and hot-reloads when the alias is updated.

### SageMaker

AWS-managed MLOps platform. Key concepts:

- **SageMaker Pipelines**: Step-based ML workflow with native AWS integration
- **SageMaker Feature Store**: Online (DynamoDB) + Offline (S3) with Kinesis streaming
- **SageMaker Model Registry**: Groups of model versions with approval workflow
- **SageMaker Endpoints**: Managed inference with multi-model, canary, and shadow variants
- **SageMaker Clarify**: Bias detection and explainability

### Vertex AI

Google Cloud MLOps platform.

- **Vertex AI Pipelines**: Kubeflow Pipelines or TFX as orchestration backends
- **Vertex AI Feature Store**: Bigtable (online) + BigQuery (offline)
- **Vertex AI Experiments**: Experiment tracking with lineage to runs
- **Vertex AI Model Registry**: Centralized model catalog with evaluation framework
- **Vertex AI Model Monitoring**: Drift detection with configurable thresholds

### Airflow vs. Kubeflow Pipelines

| Dimension | Kubeflow Pipelines | Apache Airflow |
|---|---|---|
| Native environment | Kubernetes | General; runs on K8s via KubernetesOperator |
| Artifact lineage | First-class (MLMD) | Requires custom plugins |
| GPU scheduling | Native (K8s resource requests) | Via KubernetesPodOperator |
| ML-specific UI | Yes (compare runs, metrics) | No (generic DAG UI) |
| Complex triggers | Simple | Sophisticated sensors, event-driven |
| Best for | Pure ML training pipelines | Complex multi-system data workflows |
| Recommended pattern | Use Airflow for upstream data pipelines; trigger KFP training pipeline when data is ready |

***

## 5. Model Serving

### Inference Patterns

| Pattern | Latency | Throughput | Use Case |
|---|---|---|---|
| **Online (real-time)** | < 100 ms p99 | Moderate | Fraud detection, recommendations, search |
| **Async** | Seconds to minutes | High | LLM generation, video analysis, batch scoring with SLA |
| **Batch** | Hours | Very high | Weekly scoring jobs, offline recommendations |
| **Streaming** | Sub-second | High | Clickstream scoring, IoT sensor prediction |

### REST vs. gRPC

| Dimension | REST (HTTP/JSON) | gRPC (HTTP/2 + Protobuf) |
|---|---|---|
| Latency | Higher (JSON serialization overhead) | Lower (binary Protobuf) |
| Throughput | Lower | Higher |
| Streaming | SSE or chunked | Native bidirectional streaming |
| Client compatibility | Universal | Requires gRPC client |
| Best for | Public APIs, simple payloads | Internal high-performance services, LLM streaming |

### Model Serving Engines

#### TorchServe

PyTorch-native model server. Supports custom handlers, dynamic batching, and multi-model serving. Best for PyTorch models without multi-framework requirements.

#### TensorFlow Serving

TF-native serving for SavedModel format. gRPC-first, highly optimized for TensorFlow graphs. Batching, model versioning, and A/B routing built-in.

#### Triton Inference Server (NVIDIA)

Multi-framework, multi-model server supporting TensorRT, ONNX, PyTorch, TF, and custom backends. Dynamic batching, concurrent model execution, and Prometheus metrics built-in.

```protobuf
# Triton model config with dynamic batching
name: "bert_classifier"
backend: "onnxruntime"
max_batch_size: 32

input [{ name: "input_ids" data_type: TYPE_INT64 dims: [-1, 128] }]
output [{ name: "logits" data_type: TYPE_FP32 dims: [-1, 2] }]

dynamic_batching {
  preferred_batch_size: [8, 16, 32]
  max_queue_delay_microseconds: 5000
}

instance_group [{ count: 2 kind: KIND_GPU }]
```

### Canary Model Rollout

```
Production Traffic
        │
        ▼
   ┌──────────┐
   │  Istio   │ ← VirtualService weighted routing
   │ Gateway  │
   └────┬─────┘
        │
   ┌────┴────────────────┐
   │                     │
   ▼ (95%)               ▼ (5%)
Champion Model       Challenger Model
(stable)             (new candidate)
        │                 │
        ▼                 ▼
   Prometheus metrics compared
   - accuracy (if labels available)
   - latency p50/p95/p99
   - error rate
   - prediction distribution
        │
        ▼
   Promote challenger to 100%
   OR roll back to 0% (keep champion)
```

### Shadow Deployment

1. Deploy challenger as a separate Kubernetes Deployment.
2. Configure traffic mirroring in Istio/Envoy — all production requests are duplicated to the challenger. The challenger's response is discarded.
3. Log challenger predictions, latency, and errors to a separate metrics namespace.
4. After 24-48 hours, compare metrics against production.
5. If metrics are acceptable, route 5% live traffic (canary), then graduate to full production.

### KServe InferenceService

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: sklearn-model
  namespace: inference
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "s3://models/sklearn-v3/"
      resources:
        limits:
          cpu: "2"
          memory: "4Gi"
          nvidia.com/gpu: "1"
  # Canary config
  canaryTrafficPercent: 10
```

***

## 6. Model Registry

A model registry is a versioned catalog of trained models with metadata (training metrics, dataset version, framework version, code commit). It serves as the promotion gate before models reach production.

### Staging Workflow

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

### MLflow 2.x Aliases

```python
import mlflow

client = mlflow.tracking.MlflowClient()

# Register a new version
model_version = mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name="fraud_classifier"
)

# Set alias — serving layer reads @champion, not a hard stage
client.set_registered_model_alias(
    name="fraud_classifier",
    alias="champion",
    version=model_version.version,
)

# Load by alias in serving
model = mlflow.pyfunc.load_model("models:/fraud_classifier@champion")
```

### Model Card

A model card is structured documentation attached to a model version:
- Intended use cases and out-of-scope uses
- Performance metrics across demographic groups (bias audit)
- Training and evaluation dataset descriptions
- Known limitations and failure modes
- Ethical considerations and risk tier

Required for regulatory compliance (SR 11-7 in financial services, EU AI Act, FDA for medical AI).

***

## 7. Experiment Tracking

Experiment tracking records inputs (dataset version, hyperparameters, code commit) and outputs (metrics, artifacts) of every training run.

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

mlflow.set_experiment("fraud_classifier_v3")

with mlflow.start_run(tags={"data_version": "2024-01-v3", "commit": "abc123"}):
    model = RandomForestClassifier(n_estimators=200, max_depth=8)
    model.fit(X_train, y_train)

    # Log hyperparameters
    mlflow.log_params({"n_estimators": 200, "max_depth": 8})

    # Log metrics
    mlflow.log_metrics({
        "auc": roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]),
        "f1": f1_score(y_test, model.predict(X_test)),
    })

    # Log the model artifact
    mlflow.sklearn.log_model(model, "model")

    # Autolog captures framework-specific metrics automatically
    # mlflow.sklearn.autolog()
```

### MLflow Autolog

```python
mlflow.sklearn.autolog()   # Captures n_estimators, max_depth, OOB score, etc.
mlflow.pytorch.autolog()   # Captures per-epoch loss/accuracy, gradient norms
mlflow.xgboost.autolog()   # Captures eval metrics, best iteration
```

***

## 8. Data Versioning with DVC

DVC extends Git to version large binary files (datasets, model artifacts) by storing pointers in Git while data lives in remote storage.

```bash
# Initialize DVC in a git repo
dvc init

# Track a dataset
dvc add data/training/

# Push data to remote (S3, GCS, Azure Blob, SSH)
dvc remote add -d s3remote s3://my-bucket/dvc-cache
dvc push

# Commit the .dvc metadata file to git
git add data/training.dvc .gitignore
git commit -m "Add training dataset v3"

# Reproduce the full pipeline (uses caching — skips unchanged stages)
dvc repro

# Pull data for a specific git commit
git checkout v2.1.0
dvc pull

# Check pipeline status (shows which stages are stale)
dvc status

# Run a specific stage
dvc run -n train \
  -d data/training/ -d src/train.py \
  -o models/model.pkl \
  python src/train.py
```

### DVC Pipelines (dvc.yaml)

```yaml
stages:
  prepare:
    cmd: python src/prepare.py
    deps:
      - src/prepare.py
      - data/raw/
    outs:
      - data/prepared/

  train:
    cmd: python src/train.py --n-estimators 200
    deps:
      - src/train.py
      - data/prepared/
    params:
      - params.yaml:
          - train.n_estimators
          - train.max_depth
    outs:
      - models/model.pkl
    metrics:
      - metrics/train.json
```

***

## 9. Model Drift and Monitoring

### Drift Taxonomy

| Type | Definition | Detection Method | Label Required |
|---|---|---|---|
| **Data Drift** (Covariate Shift) | P(X) changes — input feature distributions shift | PSI, KS test, Jensen-Shannon divergence | No |
| **Concept Drift** | P(Y\|X) changes — relationship between inputs and target changes | Compare accuracy over time windows | Yes (delayed) |
| **Label Drift** | P(Y) changes — output label distribution shifts | Monitor model output distribution | No (proxy) |
| **Feature Drift** | Individual feature statistics change (mean, variance, null rate) | Per-feature monitoring | No |
| **Schema Drift** | Upstream data schema changes (new column, type change) | Great Expectations schema validation | No |

### PSI (Population Stability Index)

```
PSI = Σ (Actual% - Expected%) × ln(Actual% / Expected%)
```

Thresholds: PSI < 0.1 (negligible), 0.1–0.2 (investigate), > 0.2 (significant — consider retraining).

### Monitoring with Evidently AI

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import ColumnDriftMetric

reference_data = pd.read_parquet("s3://data/training/baseline.parquet")
current_data = pd.read_parquet("s3://data/production/last_7_days.parquet")

report = Report(metrics=[
    DataDriftPreset(),
    DataQualityPreset(),
    ColumnDriftMetric(column_name="user_age"),
])

report.run(reference_data=reference_data, current_data=current_data)
report.save_html("drift_report.html")

# Programmatic threshold check for alerting
result = report.as_dict()
drift_share = result["metrics"][0]["result"]["share_of_drifted_columns"]
if drift_share > 0.3:
    trigger_retraining_pipeline()
```

### Monitoring Strategy

```
Immediate (minutes):
  - Request latency, error rate, throughput
  - Feature null rates
  - Feature freshness lag

Short-term (hours):
  - Data drift per feature (PSI, KS test)
  - Model output distribution shift
  - Confidence score distribution

Medium-term (days):
  - Business KPI movement (CTR, conversion, fraud catch rate)
  - Proxy label metrics (dispute rate, chargeback rate)

Long-term (weeks):
  - Ground truth accuracy (when labels arrive)
  - Concept drift detection
  - Cohort comparison across prediction dates
```

***

## 10. A/B Testing for Models

A/B testing routes a percentage of live traffic to the challenger model. Statistical significance tests determine if the challenger's business metrics are meaningfully different before full rollout.

### Implementation Pattern

```python
# Traffic splitting via Istio VirtualService
# 90% champion, 10% challenger
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: model-routing
spec:
  http:
  - route:
    - destination:
        host: champion-model-svc
        port:
          number: 80
      weight: 90
    - destination:
        host: challenger-model-svc
        port:
          number: 80
      weight: 10
```

### Statistical Significance

```python
from scipy import stats
import numpy as np

# Business metric (e.g., conversion rate) for each cohort
champion_conversions = np.array([...])   # shape: (n_users,)
challenger_conversions = np.array([...])

# Two-sample z-test for proportions
champion_rate = champion_conversions.mean()
challenger_rate = challenger_conversions.mean()

z_stat, p_value = stats.proportions_ztest(
    [challenger_conversions.sum(), champion_conversions.sum()],
    [len(challenger_conversions), len(champion_conversions)],
)

# Promote if statistically significant improvement
if p_value < 0.05 and challenger_rate > champion_rate:
    promote_challenger_to_production()
```

### A/B vs. Shadow vs. Canary

| Pattern | User Impact | Risk | Use When |
|---|---|---|---|
| **Shadow** | None — challenger response discarded | Zero | First validation of new model |
| **Canary** | Small % of users see new model | Low | Model has passed shadow; validating at scale |
| **A/B test** | Controlled split for business metric measurement | Controlled | Measuring business KPI impact statistically |
| **Blue/Green** | Instant full swap | High | When canary is not feasible |

***

## 11. LLMOps

### Why LLMOps Differs from Standard MLOps

| Dimension | Standard MLOps | LLMOps |
|---|---|---|
| Model size | MB to low GB | 7B–700B+ params, 14GB–400GB+ |
| Hardware | CPU or single GPU | Multi-GPU or multi-node |
| Latency unit | ms per prediction | TTFT, TPOT, Tokens Per Second |
| Evaluation | Accuracy, F1, AUC | BLEU, ROUGE, LLM-as-judge, human eval |
| Versioning | Model weights | Weights + system prompt + retrieval context |
| Drift detection | Feature distribution | Output quality, groundedness, hallucination rate |
| Cost unit | Inference per second | Tokens per dollar, cost per conversation |
| Primary failure mode | Wrong number | Hallucination, prompt injection, guardrail breach |

### LLM Serving Metrics

| Metric | Definition | Target |
|---|---|---|
| **TTFT** (Time to First Token) | Time from request to first token | < 500 ms interactive, < 2 s batch |
| **TPOT** (Time Per Output Token) | Latency between successive tokens | < 30 ms/token for chat |
| **TPS** (Tokens Per Second) | Total tokens generated per second (throughput) | Maximize for cost efficiency |
| **KV cache hit rate** | % of requests reusing cached KV blocks | Higher = faster, cheaper |
| **Request concurrency** | Simultaneous in-flight requests | Drives batching strategy |

### vLLM and PagedAttention

Traditional LLM inference pre-allocates a contiguous KV cache buffer per sequence based on maximum sequence length, causing:
- Internal fragmentation (most sequences shorter than max length)
- Inability to share prefix blocks across requests with the same system prompt

PagedAttention manages KV cache in fixed-size non-contiguous blocks, inspired by OS virtual memory:
- Blocks are allocated dynamically as tokens generate — near-zero fragmentation
- Multiple requests sharing the same system prompt share physical blocks for that prefix
- Enables continuous batching: new requests join mid-flight as pages free up
- Result: 2-24x throughput improvement over naive serving

```bash
# vLLM serve command
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --tensor-parallel-size 2 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --enable-prefix-caching \
  --served-model-name llama3-8b \
  --port 8000
```

### RAG Pipeline Architecture

```
INDEXING (offline):
Documents → Chunker → Embedder → Vector DB
             (512 tok,  (OpenAI,   (Pinecone,
              50 overlap) E5, BGE)   Weaviate,
                                     pgvector)

RETRIEVAL + GENERATION (per query):
User Query
    → Embedder → Query Vector
    → Vector DB ANN search (top-k=5)
    → Reranker (Cohere, cross-encoder)
    → Prompt Assembly (context + query)
    → LLM → Grounded Response
```

### RAG Failure Modes

| Failure Mode | Symptom | Mitigation |
|---|---|---|
| Retrieval miss | LLM says "I don't know" when answer exists | Hybrid search (BM25 + dense), better chunking |
| Context dilution | Vague unfocused answer | Reduce k, add reranker, use MMR |
| Hallucination with retrieval | LLM adds fabricated details beyond context | Citation enforcement, faithfulness eval, lower temperature |
| Stale index | Outdated answer despite correct documents | Incremental re-indexing, TTL-based refresh |
| Chunk boundary problem | Answer spans chunk boundary | Semantic chunking, sliding window with overlap |

### RAG Evaluation with RAGAS

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

result = evaluate(
    dataset,  # questions, answers, contexts, ground_truths
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
)
# Alert if faithfulness < 0.85
```

### Prompt Versioning

Prompt changes are deployments. A system prompt change can cause as much behavioral change as a weight update. Treat prompts as first-class versioned artifacts:

```python
class PromptRegistry:
    def register(self, name: str, template: str, metadata: dict) -> str:
        prompt_hash = hashlib.sha256(template.encode()).hexdigest()[:8]
        version = f"{name}:{datetime.utcnow().strftime('%Y%m%d')}:{prompt_hash}"
        self.store.put(version, {"template": template, "metadata": metadata})
        return version
```

### Fine-tuning Pipeline

When RAG and prompt engineering cannot solve the problem (domain-specific style, private knowledge too large for context, format enforcement), fine-tuning is appropriate:

1. **Data preparation**: Curate instruction-following pairs (prompt → ideal response). Use RLHF or DPO for preference alignment.
2. **PEFT (Parameter-Efficient Fine-Tuning)**: LoRA or QLoRA adds trainable rank-decomposition matrices — fine-tunes 0.1-1% of parameters with near full-model quality. Avoids catastrophic forgetting.
3. **Experiment tracking**: Log base model version, LoRA rank/alpha, learning rate, dataset version.
4. **Evaluation**: Benchmark on held-out eval set (MMLU, domain-specific tasks). Compare to base model.
5. **Serving**: Merge LoRA adapters into base model weights for serving, or serve adapters separately with a multi-LoRA serving framework.

### LLM Cost Control

| Strategy | Mechanism | Savings Potential |
|---|---|---|
| Prompt compression | LLMLingua, selective context truncation | 30-60% input tokens |
| Semantic caching | Cache by query embedding similarity, not exact string | 40-70% for repetitive queries |
| Model routing | Route simple queries to smaller model (8B), complex to large (70B) | 50-80% cost reduction |
| Quantization | AWQ INT4 or GPTQ INT8 | 4x memory reduction, 2x throughput |
| Batch API | Group async requests; providers offer 50% batch discount | 50% off |

***

## 12. Responsible AI and Bias Detection

### Fairness Metrics

| Metric | Definition | Formula |
|---|---|---|
| **Demographic Parity** | P(Y=1 \| Group A) = P(Y=1 \| Group B) | Equal positive rate across groups |
| **Equalized Odds** | Equal TPR and FPR across groups | Same error rates for both positive and negative cases |
| **Equal Opportunity** | Equal TPR across groups | Same recall for the positive class |
| **Disparate Impact** | Ratio of positive rate between groups | < 0.8 is considered disparate impact under 80% rule |

### Detecting Bias

```python
from fairlearn.metrics import MetricFrame, demographic_parity_difference
from sklearn.metrics import accuracy_score, precision_score

mf = MetricFrame(
    metrics={"accuracy": accuracy_score, "precision": precision_score},
    y_true=y_test,
    y_pred=y_pred,
    sensitive_features=df_test["race"],
)

print(mf.by_group)
print("Demographic parity difference:", demographic_parity_difference(y_test, y_pred, sensitive_features=df_test["race"]))
```

### SHAP Explainability

```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Per-prediction explanation
shap.force_plot(explainer.expected_value[1], shap_values[1][0], X_test.iloc[0])

# Global feature importance
shap.summary_plot(shap_values[1], X_test)
```

### Mitigation Strategies

| Phase | Strategy | Mechanism |
|---|---|---|
| Pre-processing | Resampling | Oversample underrepresented groups |
| Pre-processing | Reweighting | Assign sample weights to balance group influence |
| In-processing | Constrained optimization | Add fairness constraints to training objective |
| Post-processing | Threshold adjustment | Set different decision thresholds per group to equalize error rates |

> [!CAUTION]
> Fairness constraints typically trade off accuracy. Document the trade-off explicitly in the model card and get stakeholder sign-off before deployment.

***

## 13. GPU Infrastructure

### GPU Hierarchy (NVIDIA Data Center)

| GPU | Memory | Bandwidth | NVLink | Primary Use |
|---|---|---|---|---|
| T4 | 16GB GDDR6 | 320 GB/s | No | Inference, CPU-comparable workloads |
| A10G | 24GB GDDR6 | 600 GB/s | No | Inference, medium fine-tuning |
| A100 40GB | 40GB HBM2 | 1.6 TB/s | 600 GB/s | Training, large inference |
| A100 80GB | 80GB HBM2e | 2 TB/s | 600 GB/s | Large model training |
| H100 | 80GB HBM3 | 3.35 TB/s | 900 GB/s | Frontier model training |

### CUDA Memory Model

```
GPU Memory Hierarchy:
  Global Memory (DRAM / HBM) ← 16-80GB, ~TB/s bandwidth
      ├── L2 Cache             ← 40-80MB
      │     └── L1 Cache / Shared Memory ← 192KB per SM
      │           └── Registers          ← per thread
      └── Texture/Constant Cache

Key insight: bandwidth matters more than FLOPS for many DL operations.
Arithmetic intensity = FLOPS / bytes — compute-bound vs. memory-bound.
```

### Multi-GPU Distributed Training

**Data Parallelism**: Each GPU holds the full model; data is split. Gradients synchronized via all-reduce (NCCL ring all-reduce). Simple, scales well when model fits on one GPU.

**Tensor Parallelism**: A single layer's weight matrix is split across GPUs (each computes part of the matrix multiply). Requires NVLink for low-latency all-reduce. Best on same-node GPUs.

**Pipeline Parallelism**: Different model layers run on different GPUs. GPU 0 handles layers 1-12, GPU 1 handles layers 13-24. Micro-batching reduces pipeline bubble time. Works across nodes over InfiniBand.

**3D Parallelism**: Combines all three. Standard for frontier model training (GPT-4, LLaMA 3 70B+).

### ZeRO Optimizer Stages (DeepSpeed / PyTorch FSDP)

| Stage | What Gets Partitioned | Memory Reduction | Use When |
|---|---|---|---|
| ZeRO-1 | Optimizer state | ~4x (Adam) | Easy win; negligible overhead |
| ZeRO-2 | Optimizer state + gradients | ~8x | Medium models |
| ZeRO-3 | Parameters + gradients + optimizer state | Linear with N GPUs | Models > 10B params |
| ZeRO-3 + Offload | Above + CPU RAM offload | Extreme | Limited GPU memory, accept slower training |

### NVIDIA MIG (Multi-Instance GPU)

MIG partitions an A100 or H100 into up to 7 isolated, fixed-size GPU slices with dedicated compute, memory, and cache.

```bash
# Enable MIG on node
nvidia-smi -mig 1

# Create 7x 1g.10gb instances from A100 80GB
nvidia-smi mig -cgi 1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb,1g.10gb
nvidia-smi mig -cci

# Kubernetes: request a MIG slice
# resources:
#   limits:
#     nvidia.com/mig-1g.10gb: "1"
```

**Use MIG when**: running multiple small inference workloads on a single GPU with isolation requirements; multi-tenant inference platforms.

### Gradient Checkpointing

Normally, the forward pass stores all intermediate activations for backpropagation — consuming more memory than the parameters themselves for large models.

Gradient checkpointing trades compute for memory: only a subset of activations are stored during the forward pass. Non-stored activations are recomputed from the nearest checkpoint during backpropagation. Memory: O(√n_layers) instead of O(n_layers), at the cost of ~30% increased training time.

```python
# PyTorch
import torch.utils.checkpoint as checkpoint
output = checkpoint.checkpoint(layer, input)

# HuggingFace Transformers
model.gradient_checkpointing_enable()
```

### InfiniBand vs. Ethernet for Distributed Training

| Dimension | InfiniBand (HDR/NDR) | Ethernet (100GbE/400GbE) |
|---|---|---|
| Bandwidth | 200-400 Gb/s | 100-400 Gb/s |
| Latency | ~1 µs | 5-30 µs |
| RDMA | Native (RDMA over IB) | RDMA over Converged Ethernet (RoCE) |
| Cost | High (HCA + switch) | Lower |
| Use for | Multi-node large model training | Inference clusters, smaller training |

***

## 14. ML Metadata Lineage (MLMD)

ML Metadata (MLMD) tracks the full provenance of ML artifacts: datasets, models, evaluations, and the executions that produced them.

### MLMD Concepts

| Concept | Definition |
|---|---|
| **Artifact** | A named, typed, versioned entity (dataset, model, metrics) |
| **Execution** | A step that consumed and produced artifacts (training run, evaluation) |
| **Context** | A grouping of related artifacts and executions (an experiment, a pipeline run) |
| **Event** | The relationship between an Execution and an Artifact (INPUT / OUTPUT) |

### MLMD in Kubeflow Pipelines

KFP automatically records lineage to MLMD for every component. You can query it:

```python
import ml_metadata as mlmd
from ml_metadata.proto import metadata_store_pb2

connection_config = metadata_store_pb2.ConnectionConfig()
connection_config.sqlite.filename_uri = '/tmp/mlmd.db'
store = mlmd.MetadataStore(connection_config)

# Get all model artifacts
model_type = store.get_artifact_type("Model")
models = store.get_artifacts_by_type("Model")

# Trace: which dataset trained a given model
events = store.get_events_by_artifact_ids([model.id for model in models])
```

### OpenLineage (Cross-Tool Lineage Standard)

OpenLineage is an open standard for lineage events across Airflow, Spark, dbt, Flink, and Kubeflow. Events flow to Marquez (lineage server) for visualization.

```python
# Airflow task with OpenLineage integration
from openlineage.airflow.dag import DAG
from openlineage.airflow.operators.python import PythonOperator

with DAG("training_pipeline", ...) as dag:
    preprocess = PythonOperator(
        task_id="preprocess_data",
        python_callable=preprocess_fn,
        inlets=[Dataset(namespace="s3://raw-data", name="user_events")],
        outlets=[Dataset(namespace="s3://processed", name="user_features")],
    )
```

### Lineage Tools Comparison

| Tool | Scope | Integration |
|---|---|---|
| **MLMD** | ML artifacts within KFP/TFX | Kubeflow Pipelines, TFX |
| **MLflow** | Experiment run → dataset version → model | Native MLflow |
| **DVC** | Code + data + model via Git | Any Python ML project |
| **OpenLineage / Marquez** | Cross-tool data lineage standard | Airflow, Spark, dbt, Flink |
| **Apache Atlas** | Data catalog + lineage graph | Hadoop ecosystem, Spark |
