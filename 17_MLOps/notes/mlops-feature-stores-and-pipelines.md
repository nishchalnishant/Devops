# MLOps Deep-Dive: Feature Stores & ML Pipeline Orchestration

> [!IMPORTANT]
> This is one of the highest-yield MLOps interview topics at the senior level. Feature Stores and CT Pipelines are where infrastructure engineering and ML diverge most sharply from standard DevOps. Master this file before any ML Platform or Senior MLOps interview.

**Companion files:**
- [MLOps Interview Playbook](mlops-interview-playbook.md)
- [MLOps Hard Questions](mlops-interview-questions-hard.md)
- [MLOps Scenario Drills](mlops-scenario-based-interview-drills.md)

***

## Part 1: Feature Stores

### The Problem Feature Stores Solve

In a standard ML workflow without a Feature Store, this is what happens:

```
Data Scientist (Training):
  raw_data → custom_transform_v1.py → feature_matrix → train model

Data Engineer (Serving):
  raw_data → custom_transform_v2.py → feature_vector → serve model
```

The transforms drift. The model was trained on one version of a feature and served with another. The model gives wrong predictions despite "healthy" infrastructure. This is **training-serving skew** — the most common silent killer in production ML.

A Feature Store solves this by being the **single source of truth** for feature definitions and their computed values.

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

> [!TIP]
> The **click moment** for interviewers: A Feature Store's value is not storage. It is **guarantee of feature parity** between training and serving. If you explain it as "a database for features" you will be downgraded. Explain it as "the system that makes training-serving skew architecturally impossible."

***

### Feature Store Architecture: Offline vs. Online

#### Offline Store
- **Purpose:** Historical feature values for model training and batch inference
- **Storage:** Data warehouse or object storage (BigQuery, S3 + Parquet, Delta Lake)
- **Access pattern:** Large batch reads keyed by entity + timestamp
- **Point-in-time correctness:** Critical. Must retrieve the feature value as it existed at a past timestamp, not today's value. Prevents label leakage.

#### Online Store
- **Purpose:** Low-latency feature retrieval during real-time inference
- **Storage:** Key-value store (Redis, DynamoDB, Cassandra, Bigtable)
- **Access pattern:** Single-entity lookup in <10ms
- **Freshness:** Features must be materialized from offline store on a schedule or via streaming

#### The Materialization Pipeline

```
Offline Store (cold, historical) ──► Materialization Job ──► Online Store (hot, fresh)
                                           │
                                    Runs on schedule
                                    (e.g., every 15 min)
                                    or triggered by upstream
                                    data pipeline completion
```

> [!CAUTION]
> The materialization lag is a production risk. If your online store is 2 hours stale and your model was trained on fresh data, you have implicit training-serving skew even though you're using a Feature Store. Always monitor feature freshness as a first-class SLI.

***

### Feature Store Tools: Comparison

| Tool | Managed | Online Store | Offline Store | Streaming | Best For |
|---|---|---|---|---|---|
| **Feast** | Self-hosted (or managed via Tecton) | Redis, DynamoDB, BigTable | S3, GCS, BigQuery | Kafka (limited) | Teams wanting OSS control |
| **Hopsworks** | Self-hosted or cloud | RonDB (MySQL NDB) | Hudi/Delta | Kafka native | Enterprises needing SQL + streaming |
| **Tecton** | Fully managed SaaS | DynamoDB, Redis | S3, Snowflake | Spark Streaming, Flink | Teams wanting zero ops overhead |
| **Vertex AI Feature Store** | GCP managed | Bigtable | BigQuery | Dataflow | GCP-native stacks |
| **SageMaker Feature Store** | AWS managed | DynamoDB | S3 | Kinesis | AWS-native stacks |
| **Azure ML Feature Store** | Azure managed | CosmosDB | ADLS Gen2 | EventHub | Azure-native stacks |

***

### Feast: Architecture Deep-Dive

Feast is the most common OSS Feature Store in interviews. Know its components.

```
┌─────────────────────────────────────────────────────────────┐
│                      FEAST ARCHITECTURE                     │
│                                                             │
│  Feature Repo (Git)                                         │
│  ├── feature_store.yaml    (registry + store config)        │
│  ├── driver_features.py    (FeatureView definitions)        │
│  └── entities.py           (entity definitions)             │
│                      │                                      │
│                 feast apply                                  │
│                      │                                      │
│            ┌─────────▼─────────┐                           │
│            │   Registry (DB)   │  ← source of truth for    │
│            │ SQLite/Postgres/   │    feature definitions    │
│            │ GCS/S3            │                            │
│            └─────────┬─────────┘                           │
│                      │                                      │
│         feast materialize-incremental                        │
│                      │                                      │
│     ┌────────────────┼────────────────┐                     │
│     ▼                                 ▼                     │
│ Offline Store                    Online Store               │
│ (S3 + Parquet)                   (Redis)                    │
│                                                             │
│  Training:                    Serving:                      │
│  store.get_historical_features store.get_online_features    │
└─────────────────────────────────────────────────────────────┘
```

**Key Feast CLI commands:**

```bash
# Register feature definitions from the repo
feast apply

# Materialize features up to now (full)
feast materialize <start_date> <end_date>

# Materialize only new data since last run (incremental)
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")

# Serve the online feature server (REST API)
feast serve

# Validate that online and offline stores are in sync
feast feature-views list
```

**Python SDK — Training:**

```python
from feast import FeatureStore
from datetime import datetime
import pandas as pd

store = FeatureStore(repo_path=".")

# Entity DataFrame: the entities and timestamps you want historical features for
entity_df = pd.DataFrame({
    "driver_id": [1001, 1002, 1003],
    "event_timestamp": [datetime(2024, 1, 1)] * 3,
})

# Point-in-time correct retrieval — features as they existed at each timestamp
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
).to_df()
```

**Python SDK — Inference:**

```python
# Online retrieval — latest feature values for real-time serving
feature_vector = store.get_online_features(
    features=["driver_hourly_stats:conv_rate", "driver_hourly_stats:acc_rate"],
    entity_rows=[{"driver_id": 1001}],
).to_dict()
```

> [!TIP]
> The critical difference: `get_historical_features` is **point-in-time correct** — it retrieves the value of a feature as it existed at a past timestamp. This is what prevents label leakage in training. `get_online_features` always returns the latest value.

***

## Part 2: ML Pipeline Orchestration

### The Four Pipelines of MLOps

Do not conflate these. Interviewers at the senior level will test whether you know the difference.

```
┌────────────────────────────────────────────────────────────────┐
│               THE FOUR MLOPS PIPELINES                         │
├─────────────────┬──────────────────────────────────────────────┤
│ CI Pipeline     │ Code linting, unit tests, schema validation   │
│                 │ Triggers on: every PR / commit                │
├─────────────────┼──────────────────────────────────────────────┤
│ CT Pipeline     │ Data validation → training → evaluation →     │
│ (Continuous     │ registry → promotion decision                 │
│  Training)      │ Triggers on: schedule, data volume,           │
│                 │ drift alert, or explicit trigger              │
├─────────────────┼──────────────────────────────────────────────┤
│ CD Pipeline     │ Promote model from registry → staging →       │
│ (Continuous     │ shadow → canary → production                  │
│  Delivery)      │ Triggers on: registry promotion approval      │
├─────────────────┼──────────────────────────────────────────────┤
│ CM Pipeline     │ Drift detection → alerting → retrain trigger  │
│ (Continuous     │ Triggers on: scheduled metric evaluation       │
│  Monitoring)    │ (always running)                              │
└─────────────────┴──────────────────────────────────────────────┘
```

***

### Continuous Training (CT) Pipeline Design

#### CT Trigger Types

| Trigger | When to Use | Risk |
|---|---|---|
| **Scheduled** (e.g., weekly) | Low-frequency data changes, stable domains | May retrain with insufficient new data |
| **Data volume** (e.g., 10k new rows) | High-velocity data, stream environments | May trigger too frequently on spiky data |
| **Drift threshold** | When model degradation is detected | Delayed — drift must first be detected |
| **Business KPI drop** | When business metric falls below threshold | Requires a closed feedback loop with labels |
| **Explicit trigger** | Regulated environments, manual review required | Slowest, most controlled |

> [!IMPORTANT]
> The most common interview mistake: saying "we retrain when accuracy drops." Accuracy requires labels. Labels are delayed. You cannot retrain on accuracy in real time. Use **proxy metrics** (drift, confidence distribution, output entropy) for real-time triggers. Use accuracy-based triggers on a delayed schedule after labels arrive.

#### CT Pipeline Stages with Validation Gates

```
Raw Data
    │
    ▼
┌─────────────────┐
│ Data Validation │  ← Great Expectations / TFX ExampleValidator
│                 │    - Schema check: correct columns and types?
│                 │    - Stats check: distribution vs. training baseline?
│                 │    - Volume check: enough new data to train?
└────────┬────────┘
         │ PASS (FAIL → abort, alert)
         ▼
┌─────────────────┐
│ Feature Eng.    │  ← Feature Store materialization
│                 │    - Run same transforms as training baseline
│                 │    - Validate feature distributions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Training  │  ← GPU cluster / Spark / Ray
│                 │    - Checkpoint frequently (spot-safe)
│                 │    - Log all params, metrics, data version to MLflow
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Evaluation│  ← Validation gate: compare vs. current champion
│                 │    - Accuracy ≥ champion − threshold?
│                 │    - Latency SLA met?
│                 │    - Fairness/bias checks?
│                 │    - Behavioral tests (known-good inputs)?
└────────┬────────┘
         │ PASS (FAIL → reject, keep champion)
         ▼
┌─────────────────┐
│ Registry Push   │  ← Push to MLflow / SageMaker Model Registry
│                 │    - Tag: data version, code commit, run ID
│                 │    - Stage: Staging (not Production yet)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Promotion Gate  │  ← Manual approval OR automated if confidence high
│                 │    - In regulated environments: mandatory human sign-off
│                 │    - Model card generation
└────────┬────────┘
         │ APPROVED
         ▼
     CD Pipeline
   (Shadow → Canary → Production)
```

***

### Kubeflow Pipelines: Architecture & Code

Kubeflow Pipelines is the industry standard for K8s-native ML pipeline orchestration.

```
┌─────────────────────────────────────────────────────────┐
│              KUBEFLOW PIPELINES ARCHITECTURE            │
│                                                         │
│  Pipeline SDK (Python) ──► Compile ──► pipeline.yaml   │
│                                              │          │
│                                    KFP Server (K8s)     │
│                                              │          │
│              ┌───────────────────────────────┤          │
│              │  Pipeline Run                 │          │
│              │                               │          │
│              │  [Step 1: Data Validation]    │          │
│              │         │                     │          │
│              │  [Step 2: Feature Eng.]       │          │
│              │         │                     │          │
│              │  [Step 3: Training Pod]  ──── │─► GPU    │
│              │         │               (requests        │
│              │  [Step 4: Evaluate]      nvidia.com/gpu) │
│              │         │                     │          │
│              │  [Step 5: Push Registry]      │          │
│              └───────────────────────────────┘          │
│                                                         │
│  Metadata Store (MLMD) tracks all artifact lineage      │
└─────────────────────────────────────────────────────────┘
```

**Kubeflow Pipeline definition (Python SDK v2):**

```python
from kfp import dsl
from kfp.dsl import component, pipeline, Dataset, Model, Input, Output

@component(base_image="python:3.11", packages_to_install=["pandas", "scikit-learn"])
def validate_data(
    input_dataset: Input[Dataset],
    validation_report: Output[Dataset],
) -> bool:
    import pandas as pd
    df = pd.read_parquet(input_dataset.path)
    # Schema and distribution checks
    assert df.shape[0] > 1000, "Insufficient training samples"
    assert df.isnull().sum().sum() == 0, "Null values detected"
    return True


@component(base_image="python:3.11", packages_to_install=["scikit-learn", "mlflow"])
def train_model(
    input_dataset: Input[Dataset],
    model_artifact: Output[Model],
    mlflow_tracking_uri: str,
    n_estimators: int = 100,
):
    import mlflow
    import pickle
    import pandas as pd
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


@pipeline(name="ct-pipeline", description="Continuous Training Pipeline")
def ct_pipeline(
    dataset_uri: str,
    mlflow_tracking_uri: str,
    n_estimators: int = 100,
):
    validate_task = validate_data(input_dataset=dataset_uri)

    # Conditional: only train if validation passes
    with dsl.Condition(validate_task.output == "True", name="validation-passed"):
        train_task = train_model(
            input_dataset=validate_task.outputs["validation_report"],
            mlflow_tracking_uri=mlflow_tracking_uri,
            n_estimators=n_estimators,
        )
        # GPU resource request
        train_task.set_accelerator_type("NVIDIA_TESLA_T4").set_accelerator_limit(1)
        train_task.set_memory_limit("16G")
```

***

### Airflow for ML Pipelines: When to Use vs. Kubeflow

| Dimension | Kubeflow Pipelines | Apache Airflow |
|---|---|---|
| **Native environment** | Kubernetes | General (can run on K8s via KubernetesOperator) |
| **Artifact lineage** | First-class (MLMD) | Requires custom plugins |
| **GPU scheduling** | Native (K8s resource requests) | Via KubernetesPodOperator |
| **ML-specific UI** | Yes (compare runs, metrics) | No (generic DAG UI) |
| **Trigger complexity** | Simple | Complex event-driven triggers, sensors |
| **Best for** | Pure ML training pipelines | Complex multi-system data workflows |
| **When to use both** | Use Airflow to orchestrate data pipelines that feed Kubeflow training pipelines |

***

## Part 3: Data Drift & Data Lineage

### Drift Types (Precise Definitions)

| Type | Definition | Detection Method |
|---|---|---|
| **Data Drift** (Covariate Shift) | Distribution of input features P(X) changes | PSI, KS test, Jensen-Shannon divergence on feature histograms |
| **Concept Drift** | Relationship between X and Y changes: P(Y\|X) changes | Requires labels; compare model accuracy over time windows |
| **Label Drift** | Distribution of output labels P(Y) changes | Monitor output distribution of model predictions |
| **Feature Drift** | Individual feature statistics change (mean, variance, null rate) | Per-feature monitoring in Evidently AI |
| **Schema Drift** | Upstream data schema changes (new column, type change) | Great Expectations schema validation |

> [!IMPORTANT]
> **The delayed-label problem:** You can detect data drift immediately. You cannot detect concept drift without labels, and labels arrive days to weeks later (e.g., a credit card fraud label may take 30 days to confirm). This is the core tension in ML monitoring. The answer is **proxy metrics** — monitor data drift and output distribution as leading indicators while you wait for true labels.

### Evidently AI: Monitoring Pipeline

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import ColumnDriftMetric

# Reference = training data distribution
reference_data = pd.read_parquet("s3://data/training/baseline.parquet")
# Current = recent production inference inputs
current_data = pd.read_parquet("s3://data/production/last_7_days.parquet")

report = Report(metrics=[
    DataDriftPreset(),          # Checks all features for drift
    DataQualityPreset(),        # Null rates, type violations, range violations
    ColumnDriftMetric(column_name="user_age"),  # Per-feature drift score
])

report.run(reference_data=reference_data, current_data=current_data)

# Save as HTML dashboard
report.save_html("drift_report.html")

# Extract drift score programmatically (for alerting)
result = report.as_dict()
drift_share = result["metrics"][0]["result"]["share_of_drifted_columns"]
if drift_share > 0.3:
    # More than 30% of features have drifted — trigger retrain pipeline
    trigger_retraining_pipeline()
```

### Data Lineage: What It Is and Why Interviewers Test It

**Data lineage** answers: "Where did this model's training data come from, and what transformations were applied?"

In a regulated environment (finance, healthcare), you must be able to answer:
- Which version of which dataset trained the model in production?
- What preprocessing was applied?
- Were any records excluded? Why?
- Can I reproduce this model's training data from scratch?

**Tools:**

| Tool | Scope | Integration |
|---|---|---|
| **Apache Atlas** | Data catalog, lineage graph, governance | Hadoop ecosystem, Spark |
| **OpenLineage** | Open standard for lineage events | Airflow, Spark, dbt, Flink |
| **Marquez** | OpenLineage server — stores and visualizes lineage | Any OpenLineage-compliant producer |
| **MLflow** | Model lineage (run → dataset version → model) | Native MLflow ecosystem |
| **DVC** | Code + data + model lineage via Git | Any Python ML project |

**OpenLineage event example (Airflow → Marquez):**

```python
# Airflow task with OpenLineage integration
from openlineage.airflow.dag import DAG
from openlineage.airflow.operators.python import PythonOperator

# The OpenLineage plugin automatically emits START/COMPLETE/FAIL
# events for each task, recording input and output datasets
with DAG("training_pipeline", ...) as dag:
    preprocess = PythonOperator(
        task_id="preprocess_data",
        python_callable=preprocess_fn,
        # Lineage metadata: this task reads from raw, writes to processed
        inlets=[Dataset(namespace="s3://raw-data", name="user_events")],
        outlets=[Dataset(namespace="s3://processed", name="user_features")],
    )
```

***

## Interview Q&A Bank

### Easy — Foundational

**Q1: What is a Feature Store and what problem does it solve?**

A Feature Store is a centralized system that stores, manages, and serves ML features. The core problem it solves is **training-serving skew** — ensuring that the exact same feature transformations used during training are applied during inference. Without it, teams typically have duplicate transformation logic in training code and serving code that drifts over time, causing model degradation without any infrastructure failure.

**Q2: What is the difference between an offline store and an online store in a Feature Store?**

The offline store holds historical feature values optimized for large batch reads — used for training and batch inference. It typically lives in a data warehouse or object storage like S3 with Parquet files. The online store holds only the latest feature values optimized for low-latency point-in-time reads during real-time inference — typically a key-value store like Redis or DynamoDB. The materialization pipeline keeps them in sync.

**Q3: What is point-in-time correctness in the context of Feature Stores?**

When retrieving historical features for training, you must retrieve the value of a feature **as it existed at the training example's timestamp**, not today's value. If you use today's feature values to train on yesterday's labels, you introduce label leakage — the model learns from information it would not have had at prediction time, producing artificially high training accuracy and poor production performance.

***

### Medium — Production Depth

**Q4: A model's accuracy was 92% in validation but drops to 74% two weeks after deployment. The inference endpoint is healthy. Walk through your diagnosis.**

Start by separating platform health from model quality — the endpoint returning `200 OK` tells you nothing about prediction correctness.

Step 1: Check for **schema drift** — has the upstream data schema changed? New or renamed columns?

Step 2: Check for **data drift** — run an Evidently or whylogs report comparing recent inference inputs against the training baseline. Has feature distribution shifted?

Step 3: Check for **training-serving skew** — are the feature transformations in the serving path identical to those used during training? Is the Feature Store being used consistently?

Step 4: Check the **model registry** — was there an inadvertent model promotion? Is the right model version serving production traffic?

Step 5: If labels are available for recent predictions, compute accuracy directly and compare to the known degradation timeline. Correlate with any upstream data pipeline changes.

Step 6: Check for **concept drift** — if the business domain changed (e.g., consumer behavior post-event), the model's learned relationships may no longer hold.

**Q5: Your Feature Store's online store is populated via a batch materialization job that runs every hour. What are the risks and how do you mitigate them?**

The primary risk is **feature staleness**. If a feature captures recent user behavior (e.g., "purchases in the last 10 minutes"), a 1-hour old materialized value can severely degrade model quality for time-sensitive predictions.

Mitigations:
1. **Streaming materialization** — replace or supplement batch with a Kafka → Flink/Spark Streaming pipeline that writes to the online store in near real-time.
2. **Freshness SLIs** — instrument each feature with a `last_materialized_at` timestamp and alert when freshness exceeds the threshold.
3. **Feature-tier differentiation** — classify features by required freshness. Slow-changing features (demographics) use batch. Fast-changing features (session behavior) use streaming.
4. **On-demand features** — compute certain features at inference time from raw data, bypassing the materialization lag entirely. Accept the higher inference latency as a trade-off.

***

### Hard — Architecture & Trade-offs

**Q6: Design the CT pipeline trigger strategy for a fraud detection model where labels arrive 30 days after the transaction.**

This is the delayed-label problem in its most extreme form.

**Immediate monitoring (no labels):**
- Monitor input feature drift (transaction patterns, device fingerprints, geolocation distribution) with PSI or KS tests
- Monitor output distribution (the model's predicted fraud probability histogram)
- Monitor proxy business metrics: dispute rate, chargeback rate (available in 1-7 days, not 30)

**Retraining trigger:**
- Primary: Data drift threshold exceeded on a key feature cluster (input-side signal)
- Secondary: Chargeback rate increases beyond a rolling 7-day average by more than 15%
- Tertiary: Scheduled monthly retrain to incorporate 30-day delayed labels from the previous period

**Pipeline gate after labels arrive:**
- Run retroactive accuracy evaluation on the held-out validation set
- Compare the retrained model's performance on the labeled historical period
- Only promote if the candidate model outperforms the champion on the labeled evaluation set

**Q7: Compare Kubeflow Pipelines, Airflow, and Prefect for ML orchestration. When would you use each?**

Use **Kubeflow Pipelines** when: your ML workloads run on Kubernetes, you need first-class artifact tracking and ML metadata (MLMD), you want native GPU scheduling, and your team's primary concern is the training pipeline lifecycle. The trade-off is higher operational complexity and tight K8s coupling.

Use **Apache Airflow** when: you have complex multi-system orchestration (ML is one piece of a larger data ecosystem including DBT, Spark, external APIs), you need sophisticated scheduling (sensors, event-driven triggers), and you want a large plugin ecosystem. The trade-off is that ML-specific features require custom implementation.

Use **Prefect** when: you want a modern Python-native orchestration layer with lower operational overhead than Airflow, built-in observability, and flexible deployment (cloud or self-hosted). Good for teams transitioning from Airflow or starting fresh. The trade-off is a smaller ecosystem than Airflow.

Use **all three together**: Airflow orchestrates upstream data pipelines (ingestion, transformation). Kubeflow runs the training pipeline when Airflow signals new data is ready. Prefect may handle lightweight operational workflows (alerting, cleanup, reporting).

**Q8: A Feature Store deployment is degrading prediction quality without any visible error. Walk through a full incident response.**

Start with the principle: **Feature Store failures are silent** — they degrade model quality without infrastructure errors.

**Triage Phase:**
```bash
# Check if the online store data is fresh
redis-cli TTL driver:1001:conv_rate  # Check TTL / expiry
redis-cli HGET driver:1001 last_updated  # Check materialization timestamp

# Check if materialization jobs are running successfully
kubectl get pods -n feast-system
kubectl logs feast-materialization-<pod> --tail=100

# Check online vs. offline parity for a sample entity
python -c "
from feast import FeatureStore
store = FeatureStore('.')
online = store.get_online_features(['driver_stats:conv_rate'], [{'driver_id': 1001}]).to_dict()
print('Online value:', online)
# Compare to expected value from offline store
"
```

**Root cause categories:**
1. **Materialization job failure** — online store not updated, serving stale features
2. **Schema mismatch** — upstream data source changed column names or types, materialization silently skips affected features
3. **Registry desync** — Feature Store registry out of sync with deployed serving code, serving different feature versions
4. **Online store eviction** — Redis memory pressure causing key eviction, features returning `None` silently defaulted to 0

**Resolution and prevention:**
- Add feature null rate monitoring to production dashboards
- Alert on materialization job failures with < 5 minute lag
- Implement a canary check: before serving real traffic, sample 10 requests against expected feature distributions

***

## Key Terms Cheat Sheet

| Term | One-Line Definition |
|---|---|
| Feature Store | Centralized system guaranteeing feature parity between training and serving |
| Offline Store | Historical feature values for training; batch access; e.g., S3 + Parquet |
| Online Store | Latest feature values for real-time inference; low-latency; e.g., Redis |
| Materialization | Job that copies features from offline to online store on a schedule |
| Point-in-time Correctness | Retrieving feature values as they existed at a past timestamp, preventing leakage |
| Training-Serving Skew | Divergence between feature transforms at train time vs. serve time |
| CT Pipeline | Continuous Training — automated pipeline from data validation to model promotion |
| Data Drift | Input feature distribution P(X) changes from training baseline |
| Concept Drift | Relationship P(Y\|X) changes — requires labels to detect directly |
| Label Leakage | Using future information to train a model, causing inflated evaluation metrics |
| OpenLineage | Open standard for emitting data lineage events across tools |
| Feast | Most common OSS Feature Store; Redis online, S3/BigQuery offline |
