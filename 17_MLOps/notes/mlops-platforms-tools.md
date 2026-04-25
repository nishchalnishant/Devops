# MLOps Platforms & Tools — Deep Dive

## Table of Contents

1. [MLflow — Experiment & Model Lifecycle](#1-mlflow--experiment--model-lifecycle)
2. [Kubeflow — Kubernetes-Native MLOps](#2-kubeflow--kubernetes-native-mlops)
3. [AWS SageMaker](#3-aws-sagemaker)
4. [Google Vertex AI](#4-google-vertex-ai)
5. [Azure Machine Learning](#5-azure-machine-learning)
6. [Weights & Biases](#6-weights--biases)
7. [Neptune AI](#7-neptune-ai)
8. [Platform Comparison Matrix](#8-platform-comparison-matrix)
9. [Selection Framework](#9-selection-framework)

***

## 1. MLflow — Experiment & Model Lifecycle

MLflow is the most widely adopted open-source MLOps platform. It is framework-agnostic (works with PyTorch, TensorFlow, scikit-learn, XGBoost, etc.) and can run anywhere from a laptop to a multi-cloud enterprise deployment.

### Four Core Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **MLflow Tracking** | Log experiments (params, metrics, artifacts) | Auto-log, runs comparison, search API |
| **MLflow Projects** | Reproducible code packaging | Conda/Docker environments, entry points |
| **MLflow Models** | Standard model packaging format | Python Function, ONNX, TorchScript, TF SavedModel |
| **MLflow Model Registry** | Versioned model catalog with staging workflow | Aliases, transitions, annotations |

### MLflow Tracking Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  MLFLOW TRACKING SERVER                     │
│                                                             │
│  Clients (Python SDK, REST API, CLI)                        │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────┐           │
│  │  Backend Store (Metadata)                   │           │
│  │  - SQLite (local)                           │           │
│  │  - PostgreSQL (production)                  │           │
│  │  - MySQL                                    │           │
│  └─────────────────────────────────────────────┘           │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────┐           │
│  │  Artifact Store (Model weights, datasets)   │           │
│  │  - Local filesystem (dev)                   │           │
│  │  - S3, GCS, Azure Blob (production)         │           │
│  │  - HDFS (on-prem)                           │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Experiment Tracking — Basic Usage

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score

# Set experiment (creates if doesn't exist)
mlflow.set_experiment("fraud_classifier_v3")

# Start a run
with mlflow.start_run(tags={"data_version": "2024-01-v3", "commit": "abc123"}):
    # Enable autologging (captures params, metrics, model automatically)
    mlflow.sklearn.autolog()
    
    model = RandomForestClassifier(n_estimators=200, max_depth=8)
    model.fit(X_train, y_train)
    
    # Custom metrics beyond autolog
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    mlflow.log_metrics({
        "auc": roc_auc_score(y_test, y_pred_proba),
        "f1": f1_score(y_test, model.predict(X_test)),
    })
    
    # Log the model artifact explicitly
    mlflow.sklearn.log_model(model, "model")
    
    # Run ID is available for registration
    run_id = mlflow.active_run().info.run_id
```

### MLflow 2.x Model Aliases (vs. Stages)

MLflow 2.x introduced **aliases** as a more flexible alternative to hard-coded stages (`None`, `Staging`, `Production`, `Archived`).

```python
import mlflow

client = mlflow.tracking.MlflowClient()

# Register a new model version
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

# Load by alias in serving code
model = mlflow.pyfunc.load_model("models:/fraud_classifier@champion")

# Transition: promote challenger to champion
client.set_registered_model_alias(
    name="fraud_classifier",
    alias="champion",
    version=new_version.version,
)
# Old champion is now just a version without the alias
```

**Why aliases are better than stages:**
- Multiple aliases per model (e.g., `@champion`, `@challenger`, `@staging`, `@canary`)
- No enforced workflow — you define your own promotion semantics
- Aliases can point to any version, not just the latest
- Easier to implement A/B testing (load both `@champion` and `@challenger`)

### Model Registry Stages Workflow

```
Training Run Complete
        │
        ▼ (auto-register)
    Version N — Stage: None
        │
        ▼ (CI validation passes)
    Version N — Stage: Staging
        │
        ▼ (Shadow deployment healthy)
    Version N — Stage: Production (Stage: Production is set)
        │
        ▼ (Version N+1 promoted)
    Version N — Stage: Archived
```

### MLflow Projects — Reproducible Packaging

```python
# MLproject file (YAML format)
name: fraud_detection
conda_env: environment.yml

entry_points:
  train:
    parameters:
      data_path: {type: str, default: "s3://data/fraud/train.parquet"}
      n_estimators: {type: int, default: 100}
      max_depth: {type: int, default: 10}
    command: "python src/train.py --data-path {data_path} --n-estimators {n_estimators} --max-depth {max_depth}"
  
  evaluate:
    parameters:
      model_uri: str
      test_data_path: str
    command: "python src/evaluate.py --model-uri {model_uri} --test-data {test_data_path}"
```

```bash
# Run a project locally
mlflow run . --entry-point train -P n_estimators=200

# Run a project on Databricks
mlflow run . --entry-point train -P n_estimators=200 \
  --backend databricks --backend-config cluster.json

# Run from Git
mlflow run https://github.com/your-org/fraud-detection.git \
  --entry-point train -P n_estimators=200
```

### MLflow Model Flavors

MLflow Models support **flavors** — different serialization formats for different deployment targets.

```python
# Log model with multiple flavors
mlflow.sklearn.log_model(model, "model")
# Creates:
# - Python Function flavor (universal)
# - Scikit-learn flavor (native format)

# Log PyTorch model
mlflow.pytorch.log_model(model, "model")
# Creates:
# - Python Function flavor
# - PyTorch flavor (state_dict)

# Log TensorFlow model
mlflow.tensorflow.log_model(model, "model")
# Creates:
# - Python Function flavor
# - TensorFlow flavor (SavedModel)
```

**Deployment targets per flavor:**
| Flavor | Deployment Targets |
|--------|-------------------|
| Python Function | Docker, Kubernetes, Azure ML, SageMaker, Databricks |
| Scikit-learn | Same as above + native pickle loading |
| PyTorch | TorchServe, Docker, Kubernetes |
| TensorFlow | TensorFlow Serving, Docker, Kubernetes |
| ONNX | Triton Inference Server, ONNX Runtime |

***

## 2. Kubeflow — Kubernetes-Native MLOps

Kubeflow is the most comprehensive open-source MLOps platform, built specifically for Kubernetes. It is the default choice for teams already invested in K8s who want full control over their ML infrastructure.

### Kubeflow Components

| Component | Purpose | Best For |
|-----------|---------|----------|
| **Kubeflow Pipelines (KFP)** | Orchestrate ML workflows as containerized DAGs | Multi-step CT pipelines with GPU |
| **KServe** | Model serving with autoscaling, canary, transformers | Production inference at scale |
| **Katib** | Hyperparameter tuning (Grid, Random, Bayesian, PBT) | Automated HPO at scale |
| **Training Operator** | Distributed training (PyTorchJob, TFJob, MXNetJob) | Large model training on K8s |
| **Notebooks** | Managed JupyterLab in the cluster | Data scientist development environment |
| **Model Registry** | Model versioning and staging | Basic registry needs |

### Kubeflow Pipelines Architecture

```
┌─────────────────────────────────────────────────────────┐
│              KUBEFLOW PIPELINES ARCHITECTURE            │
│                                                         │
│  Pipeline SDK (Python) ──► Compile ──► pipeline.yaml   │
│                                              │          │
│                                    KFP Server (K8s)     │
│                                    - API Server         │
│                                    - Scheduler          │
│                                    - Persistence Agent  │
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
│  Artifact Store (MinIO/S3) stores outputs               │
└─────────────────────────────────────────────────────────┘
```

### Kubeflow Pipeline Definition (SDK v2)

```python
from kfp import dsl
from kfp.dsl import component, pipeline, Dataset, Model, Input, Output

@component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas", "scikit-learn", "mlflow"]
)
def validate_data(
    input_dataset: Input[Dataset],
    validation_report: Output[Dataset],
) -> bool:
    """Validate input data schema and distribution."""
    import pandas as pd
    import json
    
    df = pd.read_parquet(input_dataset.path)
    
    # Schema checks
    required_columns = ["user_id", "transaction_amount", "merchant_category", "label"]
    assert all(col in df.columns for col in required_columns), "Missing required columns"
    
    # Volume check
    assert len(df) > 1000, "Insufficient training samples"
    
    # Null check
    assert df.isnull().sum().sum() == 0, "Null values detected"
    
    # Write validation report
    report = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "null_count": df.isnull().sum().sum(),
        "passed": True,
    }
    
    with open(validation_report.path, "w") as f:
        json.dump(report, f)
    
    return True


@component(
    base_image="python:3.11-slim",
    packages_to_install=["scikit-learn", "mlflow", "pandas"]
)
def train_model(
    input_dataset: Input[Dataset],
    model_artifact: Output[Model],
    mlflow_tracking_uri: str,
    n_estimators: int = 100,
    max_depth: int = 10,
):
    """Train a Random Forest model and log to MLflow."""
    import mlflow
    import pickle
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    df = pd.read_parquet(input_dataset.path)
    X, y = df.drop("label", axis=1), df["label"]
    
    with mlflow.start_run():
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
        )
        model.fit(X, y)
        
        mlflow.log_params({
            "n_estimators": n_estimators,
            "max_depth": max_depth,
        })
        mlflow.log_metrics({
            "train_accuracy": model.score(X, y),
        })
        mlflow.sklearn.log_model(model, "model")
    
    with open(model_artifact.path, "wb") as f:
        pickle.dump(model, f)


@component(
    base_image="python:3.11-slim",
    packages_to_install=["scikit-learn", "mlflow"]
)
def evaluate_model(
    model: Input[Model],
    test_dataset: Input[Dataset],
    mlflow_tracking_uri: str,
    champion_auc: float,
) -> dict:
    """Evaluate model against test set and champion baseline."""
    import mlflow
    import pickle
    import pandas as pd
    from sklearn.metrics import roc_auc_score
    
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    with open(model.path, "rb") as f:
        model = pickle.load(f)
    
    df = pd.read_parquet(test_dataset.path)
    X_test, y_test = df.drop("label", axis=1), df["label"]
    
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    
    # Compare against champion
    result = {
        "auc": auc,
        "champion_auc": champion_auc,
        "beat_champion": auc >= champion_auc,
    }
    
    return result


@pipeline(
    name="fraud-detection-ct",
    description="Continuous Training Pipeline for Fraud Detection"
)
def fraud_ct_pipeline(
    dataset_uri: str,
    test_dataset_uri: str,
    mlflow_tracking_uri: str,
    champion_auc: float = 0.92,
    n_estimators: int = 100,
    max_depth: int = 10,
):
    # Step 1: Validate data
    validate_task = validate_data(input_dataset=dataset_uri)
    
    # Step 2: Train model (only if validation passes)
    with dsl.Condition(validate_task.output == "True", name="validation-passed"):
        train_task = train_model(
            input_dataset=validate_task.outputs["validation_report"],
            mlflow_tracking_uri=mlflow_tracking_uri,
            n_estimators=n_estimators,
            max_depth=max_depth,
        )
        # Request GPU for training
        train_task.set_accelerator_type("nvidia.com/gpu")
        train_task.set_accelerator_limit(1)
        train_task.set_memory_limit("16Gi")
        
        # Step 3: Evaluate model
        evaluate_task = evaluate_model(
            model=train_task.outputs["model_artifact"],
            test_dataset=test_dataset_uri,
            mlflow_tracking_uri=mlflow_tracking_uri,
            champion_auc=champion_auc,
        )
        
        # Step 4: Register if beats champion
        with dsl.Condition(evaluate_task.output["beat_champion"] == True):
            # Add registry push component here
            pass
```

### KServe — Production Model Serving

KServe (formerly KFServing) is the Kubernetes-native model serving framework built on Knative.

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "fraud-detector"
  namespace: "inference"
  annotations:
    # Autoscaling configuration
    autoscaling.knative.dev/minScale: "2"
    autoscaling.knative.dev/maxScale: "10"
    autoscaling.knative.dev/target: "10"  # requests per pod
spec:
  predictor:
    # Canary rollout — 10% traffic to this version
    canaryTrafficPercent: 10
    model:
      modelFormat:
        name: sklearn
      storageUri: "s3://models/fraud-detector/v3/"
      resources:
        limits:
          cpu: "2"
          memory: "4Gi"
          nvidia.com/gpu: "1"
        requests:
          cpu: "1"
          memory: "2Gi"
          nvidia.com/gpu: "1"
    # Transformer for pre/post-processing
    transformer:
      containers:
        - image: "my-registry/fraud-transformer:v3"
          name: transformer
          resources:
            limits:
              cpu: "1"
              memory: "1Gi"
```

### Katib — Hyperparameter Tuning

```yaml
apiVersion: "kubeflow.org/v1beta1"
kind: "Experiment"
metadata:
  name: "hpo-fraud-detector"
  namespace: "training"
spec:
  # Objective: maximize AUC
  objective:
    type: maximize
    goal: 0.95
    objectiveMetricName: auc
  
  # Algorithm: Bayesian Optimization
  algorithm:
    algorithmName: bayesianoptimization
  
  # Search space
  parameters:
    - name: n_estimators
      parameterType: int
      feasibleSpace:
        min: "50"
        max: "500"
    - name: max_depth
      parameterType: int
      feasibleSpace:
        min: "3"
        max: "20"
    - name: learning_rate
      parameterType: double
      feasibleSpace:
        min: "0.01"
        max: "0.3"
  
  # Parallelism
  parallelTrialCount: 5
  maxTrialCount: 30
  maxFailedTrialCount: 5
  
  # Trial template
  trialTemplate:
    trialParameters:
      - name: n_estimators
        description: "Number of trees"
      - name: max_depth
        description: "Max tree depth"
      - name: learning_rate
        description: "Learning rate"
    trialSpec:
      apiVersion: batch/v1
      kind: Job
      spec:
        template:
          spec:
            containers:
              - name: training
                image: "my-registry/fraud-trainer:v1"
                command:
                  - "python"
                  - "train.py"
                  - "--n_estimators=${n_estimators}"
                  - "--max_depth=${max_depth}"
                  - "--learning_rate=${learning_rate}"
```

***

## 3. AWS SageMaker

SageMaker is AWS's fully managed MLOps platform. It abstracts away infrastructure management while providing deep AWS integration.

### Core SageMaker Components

| Component | Purpose | AWS Integration |
|-----------|---------|-----------------|
| **SageMaker Studio** | Web-based IDE for ML development | IAM, S3, EFS |
| **SageMaker Pipelines** | ML workflow orchestration | EventBridge, Lambda |
| **SageMaker Feature Store** | Online + Offline feature storage | DynamoDB, S3, Kinesis |
| **SageMaker Experiments** | Experiment tracking | S3 artifact storage |
| **SageMaker Model Registry** | Model versioning and approval | IAM policies |
| **SageMaker Endpoints** | Managed inference | CloudWatch, ALB |
| **SageMaker Clarify** | Bias detection and explainability | Comprehend integration |
| **SageMaker Model Monitor** | Production drift detection | CloudWatch alarms |

### SageMaker Pipeline Definition

```python
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.parameters import ParameterInteger, ParameterString
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn

# Define pipeline parameters
processing_instance_count = ParameterInteger(name="ProcessingInstanceCount", default_value=1)
training_instance_type = ParameterString(name="TrainingInstanceType", default_value="ml.m5.xlarge")
model_approval_status = ParameterString(name="ModelApprovalStatus", default_value="Pending")

# Create pipeline session
pipeline_session = PipelineSession()

# Processing step
sklearn_processor = SKLearnProcessor(
    framework_version="1.0-1",
    instance_type="ml.m5.xlarge",
    instance_count=processing_instance_count,
    base_job_name="fraud-preprocessing",
    role=role,
)

processing_step = ProcessingStep(
    name="Preprocessing",
    processor=sklearn_processor,
    inputs=[ProcessingInput(source=train_data_uri, destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(output_name="train", destination="/opt/ml/processing/output/train")],
    code="preprocess.py",
)

# Training step
estimator = SKLearn(
    entry_point="train.py",
    role=role,
    instance_type=training_instance_type,
    framework_version="1.0-1",
    base_job_name="fraud-training",
    sagemaker_session=pipeline_session,
)

training_step = TrainingStep(
    name="Training",
    estimator=estimator,
    inputs={"train": ProcessingInput(input_name="train", source=processing_step.outputs[0].destination)},
)

# Register model step
from sagemaker.workflow.model_step import ModelStep
from sagemaker.model import Model

model = Model(
    image_uri=training_step.properties.EstimatedModelArn,
    role=role,
)

model_step = ModelStep(
    name="RegisterModel",
    step_args=model.register(
        content_types=["text/csv"],
        response_types=["text/csv"],
        inference_instances=["ml.t2.medium", "ml.m5.large"],
        transform_instances=["ml.m5.large"],
        model_package_group_name="FraudDetectorPackage",
        approval_status=model_approval_status,
    ),
)

# Build and create pipeline
from sagemaker.workflow.pipeline import Pipeline

pipeline = Pipeline(
    name="FraudDetectionPipeline",
    parameters=[processing_instance_count, training_instance_type, model_approval_status],
    steps=[processing_step, training_step, model_step],
    sagemaker_session=pipeline_session,
)

pipeline.create(role=role)
pipeline.start()
```

### SageMaker Feature Store

```python
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.session import Session

# Create feature group
feature_group = FeatureGroup(name="fraud-features", sagemaker_session=Session())

# Define feature schema
feature_definitions = [
    FeatureDefinition(feature_name="user_id", feature_type=FeatureType.STRING),
    FeatureDefinition(feature_name="transaction_amount", feature_type=FeatureType.FRACTIONAL),
    FeatureDefinition(feature_name="merchant_category", feature_type=FeatureType.STRING),
    FeatureDefinition(feature_name="label", feature_type=FeatureType.STRING),
]

feature_group.create(
    feature_definitions=feature_definitions,
    record_identifier_name="user_id",
    event_time_feature_name="event_timestamp",
    role_arn=role,
    online_store_config=OnlineStoreConfig(
        security_config={
            "KmsKeyId": kms_key_id,
        }
    ),
    offline_store_config=OfflineStoreConfig(
        s3_storage_config={
            "S3Uri": f"s3://{bucket}/offline-store/",
        },
        table_format="GLUE",
    ),
)

# Ingest data
feature_group.ingest(dataframe=df)

# Retrieve features for training (point-in-time correct)
from datetime import datetime

training_data = feature_group.batch_get_record(
    record_identifiers=[
        {"user_id": "1001", "event_time": datetime(2024, 1, 1)},
        {"user_id": "1002", "event_time": datetime(2024, 1, 15)},
    ],
)

# Retrieve online features for inference
response = feature_group.get_record(RecordIdentifierValueAsString="1001")
```

***

## 4. Google Vertex AI

Vertex AI is Google Cloud's unified MLOps platform, combining AutoML and custom training with deep BigQuery integration.

### Vertex AI Components

| Component | Purpose | GCP Integration |
|-----------|---------|-----------------|
| **Vertex AI Workbench** | Managed JupyterLab | Cloud Storage, BigQuery |
| **Vertex AI Pipelines** | Kubeflow or TFX orchestration | Cloud Build, Artifact Registry |
| **Vertex AI Feature Store** | Online (Bigtable) + Offline (BigQuery) | BigQuery, Dataflow |
| **Vertex AI Experiments** | Experiment tracking | Cloud Storage |
| **Vertex AI Model Registry** | Model catalog with evaluation | Cloud Monitoring |
| **Vertex AI Endpoints** | Managed inference | Cloud Load Balancing |
| **Vertex AI Model Monitoring** | Drift detection, explanation | Cloud Logging, Alerting |

### Vertex AI Pipeline (KFP backend)

```python
from google.cloud import aiplatform
from kfp import dsl
from kfp.dsl import component, pipeline, Dataset, Model, Input, Output

@component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas", "scikit-learn", "google-cloud-aiplatform"]
)
def preprocess_data(
    input_data: Input[Dataset],
    output_data: Output[Dataset],
) -> str:
    """Preprocess raw data for training."""
    import pandas as pd
    
    df = pd.read_parquet(input_data.path)
    
    # Preprocessing logic
    df = df.dropna()
    df = df.drop_duplicates()
    
    df.to_parquet(output_data.path, index=False)
    
    return f"Processed {len(df)} rows"


@component(
    base_image="python:3.11-slim",
    packages_to_install=["scikit-learn", "mlflow"]
)
def train_model(
    dataset: Input[Dataset],
    model: Output[Model],
    n_estimators: int = 100,
) -> float:
    """Train model and return accuracy."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    
    df = pd.read_parquet(dataset.path)
    X, y = df.drop("label", axis=1), df["label"]
    
    model_rf = RandomForestClassifier(n_estimators=n_estimators)
    model.fit(X, y)
    
    accuracy = accuracy_score(y, model.predict(X))
    
    import pickle
    with open(model.path, "wb") as f:
        pickle.dump(model_rf, f)
    
    return accuracy


@pipeline(name="vertex-fraud-pipeline")
def fraud_pipeline(
    project: str,
    bucket: str,
    n_estimators: int = 100,
):
    preprocess_task = preprocess_data(
        input_data=f"gs://{bucket}/data/raw/train.parquet"
    )
    
    train_task = train_model(
        dataset=preprocess_task.outputs["output_data"],
        n_estimators=n_estimators,
    )
```

### Vertex AI Model Monitoring

```python
from google.cloud import aiplatform

# Create model deployment monitoring job
monitoring_job = aiplatform.ModelDeploymentMonitoringJob.create(
    display_name="fraud-detector-monitoring",
    project=project,
    location="us-central1",
    endpoint_name=endpoint.resource_name,
    analysis_instance_count=1,
    logging_sampling_strategy={
        "random_sample_config": {"sample_rate": 0.1},
    },
    objective_configs=[
        aiplatform.ModelMonitoringObjectiveConfig(
            prediction_drift=aiplatform.ModelMonitoringObjectiveConfig.PredictionDrift(
                drift_thresholds={
                    "transaction_amount": aiplatform.ModelMonitoringObjectiveConfig.ThresholdConfig(
                        value=0.05,
                    ),
                }
            ),
        ),
        aiplatform.ModelMonitoringObjectiveConfig(
            training_model_drift=aiplatform.ModelMonitoringObjectiveConfig.TrainingModelDrift(
                drift_thresholds={
                    "transaction_amount": aiplatform.ModelMonitoringObjectiveConfig.ThresholdConfig(
                        value=0.1,
                    ),
                }
            ),
        ),
    ],
    schedule_interval="1 0 * * *",  # Daily at midnight
)
```

***

## 5. Azure Machine Learning

Azure ML is Microsoft's cloud-native MLOps platform with strong integration into the Microsoft ecosystem.

### Azure ML Components

| Component | Purpose | Azure Integration |
|-----------|---------|-------------------|
| **Azure ML Studio** | Web-based ML development portal | Azure AD, RBAC |
| **Azure ML Pipelines** | ML workflow orchestration | Data Factory, Event Grid |
| **Azure ML Feature Store** | Online (Cosmos DB) + Offline (ADLS) | Event Hubs, Stream Analytics |
| **Azure ML Experiments** | Experiment tracking | Log Analytics |
| **Azure ML Model Registry** | Model versioning and staging | Azure Policy |
| **Azure ML Endpoints** | Managed inference (real-time + batch) | Application Gateway |
| **Azure ML Responsible AI** | Fairness, explainability, error analysis | Azure Policy |

### Azure ML Pipeline Definition

```python
from azure.ai.ml import MLClient, command, Input, Output
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential

# Connect to workspace
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id,
    resource_group,
    workspace_name,
)

# Define pipeline component
@component(
    code="./src",
    environment="azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
)
def train_component(
    training_data: Input(type=AssetTypes.URI_PARQUET),
    model_output: Output(type=AssetTypes.URI_FOLDER),
    n_estimators: int = 100,
) -> None:
    """Train a Random Forest model."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import pickle
    
    df = pd.read_parquet(training_data.path)
    X, y = df.drop("label", axis=1), df["label"]
    
    model = RandomForestClassifier(n_estimators=n_estimators)
    model.fit(X, y)
    
    with open(model_output.path, "wb") as f:
        pickle.dump(model, f)


# Build pipeline
from azure.ai.ml import dsl

@dsl.pipeline(
    name="fraud-detection-pipeline",
    description="CT pipeline for fraud detection",
)
def fraud_pipeline(
    training_data_uri: str,
    n_estimators: int = 100,
):
    training_data = Input(type=AssetTypes.URI_PARQUET, path=training_data_uri)
    
    train_step = train_component(
        training_data=training_data,
        model_output=Output(type=AssetTypes.URI_FOLDER),
        n_estimators=n_estimators,
    )
    
    return {"model": train_step.outputs.model_output}


# Submit pipeline
pipeline_job = fraud_pipeline(
    training_data_uri="azureml:fraud-data-asset:1",
    n_estimators=200,
)

pipeline_job = ml_client.jobs.create_or_update(
    pipeline_job,
    experiment_name="fraud-detection",
)

ml_client.jobs.stream(pipeline_job.name)
```

***

## 6. Weights & Biases

Weights & Biases (W&B) is a cloud-first experiment tracking and model management platform focused on deep learning workflows.

### W&B Key Features

| Feature | Description |
|---------|-------------|
| **Experiment Tracking** | Log params, metrics, artifacts with rich visualization |
| **Artifact Versioning** | DVC-like data/model versioning with lineage |
| **Model Registry** | Model catalog with aliases and stages |
| **Reports** | Collaborative notebooks with live metrics |
| **Sweeps** | Hyperparameter tuning (Grid, Random, Bayesian) |
| **Tables** | Interactive data exploration and labeling |

### W&B Basic Usage

```python
import wandb

# Initialize run
wandb.init(
    project="fraud-detection",
    config={
        "model": "random_forest",
        "n_estimators": 200,
        "max_depth": 10,
        "learning_rate": 0.01,
    },
    tags=["fraud", "v3"],
)

config = wandb.config

# Training loop
for epoch in range(epochs):
    train_loss = train_one_epoch(model, train_loader)
    val_auc = evaluate(model, val_loader)
    
    # Log metrics
    wandb.log({
        "train_loss": train_loss,
        "val_auc": val_auc,
        "epoch": epoch,
    })

# Log model as artifact
artifact = wandb.Artifact("fraud-model", type="model")
artifact.add_file("model.pkl")
wandb.log_artifact(artifact)

wandb.finish()
```

### W&B Sweeps (Hyperparameter Tuning)

```yaml
# sweep.yaml
program: train.py
method: bayes
metric:
  name: val_auc
  goal: maximize
parameters:
  n_estimators:
    min: 50
    max: 500
  max_depth:
    min: 3
    max: 20
  min_samples_split:
    values: [2, 5, 10]
early_terminate:
  type: hyperband
  min_iter: 5
```

```bash
# Create sweep
wandb sweep sweep.yaml

# Run sweep agents (parallel)
wandb agent <sweep_id>
wandb agent <sweep_id>  # Multiple agents run in parallel
```

***

## 7. Neptune AI

Neptune is an experiment tracker focused on enterprise ML teams with strong metadata management and collaboration features.

### Neptune Key Features

| Feature | Description |
|---------|-------------|
| **Experiment Tracking** | Log anything: params, metrics, images, videos |
| **Model Registry** | Version models with stage transitions |
| **Feature Tables** | Track feature definitions and lineage |
| **Dashboards** | Custom views across experiments |
| **Integrations** | 15+ ML frameworks + custom logging |

### Neptune Basic Usage

```python
import neptune.new as neptune

# Initialize run
run = neptune.init_run(
    project="my-org/fraud-detection",
    api_token="YOUR_API_TOKEN",
)

# Log parameters
run["parameters"] = {
    "n_estimators": 200,
    "max_depth": 10,
    "learning_rate": 0.01,
}

# Log metrics
run["train/auc"] = 0.95
run["train/f1"] = 0.89

# Log series metrics (per epoch)
for epoch in range(epochs):
    run["train/loss"].append(train_loss)
    run["val/auc"].append(val_auc)

# Upload model artifact
run["models/model"].upload("model.pkl")

# Stop run
run.stop()
```

***

## 8. Platform Comparison Matrix

| Platform | Deployment | Cost Model | Best For | Limitations |
|----------|------------|------------|----------|-------------|
| **MLflow** | Self-hosted or Databricks | Free (OSS) + Databricks managed | Teams wanting flexibility, multi-cloud | No built-in orchestration, need KFP/Airflow |
| **Kubeflow** | Kubernetes (self-managed) | Infrastructure cost only | K8s-native teams, full control | High operational complexity |
| **SageMaker** | AWS managed | Pay-per-use + instance hours | AWS-native teams, minimal ops | Vendor lock-in, can get expensive |
| **Vertex AI** | GCP managed | Pay-per-use + instance hours | GCP-native teams, BigQuery integration | GCP lock-in |
| **Azure ML** | Azure managed | Pay-per-use + instance hours | Microsoft ecosystem teams | Azure lock-in |
| **W&B** | Cloud SaaS | Per-seat + storage | Deep learning research teams | Cloud-only, cost at scale |
| **Neptune** | Cloud SaaS | Per-seat + storage | Enterprise ML teams | Cloud-only |

***

## 9. Selection Framework

### Decision Tree

```
Start: What is your primary constraint?
│
├── "We need full control and run on-premises"
│   └── Kubeflow + MLflow (self-hosted)
│
├── "We want minimal infrastructure management"
│   │
│   ├── On AWS → SageMaker
│   ├── On GCP → Vertex AI
│   └── On Azure → Azure ML
│
├── "We need best-in-class experiment tracking for DL research"
│   └── Weights & Biases
│
├── "We need enterprise collaboration and audit trails"
│   └── Neptune AI or MLflow + custom RBAC
│
└── "We need open-source with no vendor lock-in"
    └── MLflow (experiments) + Kubeflow (pipelines) + KServe (serving)
```

### Evaluation Criteria

| Criterion | Questions to Ask |
|-----------|------------------|
| **Integration** | Does it integrate with our existing cloud, data warehouse, and CI/CD? |
| **Operational overhead** | Do we have K8s expertise to run Kubeflow, or do we need managed? |
| **Cost at scale** | What is the TCO for 1000+ training runs/month, 100+ models in production? |
| **Vendor lock-in** | Can we export models and metadata if we switch clouds? |
| **Team skills** | Does our team know Python + K8s, or do we need low-code tools? |
| **Compliance** | Does it support audit trails, RBAC, and data residency requirements? |

***

## Key Gotchas

| Gotcha | Detail |
|--------|--------|
| MLflow tracking server bottleneck | SQLite backend does not scale — use PostgreSQL for production |
| Kubeflow operational complexity | KFP requires K8s expertise — factor in 2-3 FTE for maintenance |
| SageMaker cost surprises | Training is cheap; endpoints and data transfer add up quickly |
| W&B offline mode limitations | W&B requires internet for sync — air-gapped environments need workarounds |
| Feature Store staleness | Online store lag causes training-serving skew even with Feature Store |
| Model registry without governance | Registry is useless without enforced promotion workflows |
| KServe cold starts | Knative scale-to-zero causes cold starts — set minScale > 0 for latency-sensitive models |
