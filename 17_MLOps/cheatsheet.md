# MLOps Cheatsheet

## Core Vocabulary Map

| Term | One-Line Definition |
|------|-------------------|
| Feature store | Centralized system for computing, storing, and serving ML features (offline + online) |
| Training-serving skew | Features at inference differ from features seen during training |
| Data drift | Input distribution P(X) changes between training and serving |
| Concept drift | Relationship P(Y\|X) changes — the world changes, not just the data |
| Model registry | Versioned catalog of trained models with staging workflow |
| Experiment tracker | Records params, metrics, artifacts for every training run |
| CT pipeline | Continuous Training — automated retrain → evaluate → promote |
| Shadow deployment | Challenger runs in parallel; predictions logged, not returned to users |
| Canary deployment | Small % of live traffic to challenger; metrics validate before full rollout |
| Label leakage | Training feature derived from or correlated with the target variable |
| Point-in-time join | Feature lookup uses only values available at the prediction timestamp |
| PSI | Population Stability Index — measures feature distribution shift |
| KV cache | Key-Value attention cache; critical memory resource in LLM serving |
| PagedAttention | Non-contiguous KV cache blocks for memory-efficient LLM inference (vLLM) |
| ZeRO | Zero Redundancy Optimizer — shards optimizer state / gradients / params across GPUs |
| RAGAS | Retrieval Augmented Generation Assessment — evaluates RAG pipeline quality |
| MIG | Multi-Instance GPU — partition A100/H100 into isolated GPU slices |
| KEDA | Kubernetes Event-Driven Autoscaler — scale pods on external metrics (queue depth, Prometheus) |

## The Four MLOps Pipelines

```
CI  ──── every commit ────────► lint, unit tests, schema validation
CT  ──── data/schedule/drift ──► validate → train → evaluate → register
CD  ──── registry promotion ──► shadow → canary → production
CM  ──── always running ───────► drift detection → alerting → trigger CT
```

## MLflow Commands

```bash
# Start tracking server
mlflow server --backend-store-uri sqlite:///mlflow.db \
              --default-artifact-root s3://my-bucket/mlflow

# Log a run programmatically
mlflow.set_experiment("fraud-detection-v2")
with mlflow.start_run():
    mlflow.log_params({"lr": 0.001, "epochs": 50})
    mlflow.log_metric("auc", 0.94)
    mlflow.sklearn.log_model(model, "model")

# Serve a registered model
mlflow models serve -m "models:/fraud-detector/Production" -p 5001

# Transition model stage (CLI)
mlflow models transition-stage \
  --name fraud-detector \
  --version 12 \
  --stage Production

# Compare runs
mlflow runs list --experiment-id 1 --order-by "metrics.auc DESC"
```

## DVC Commands

```bash
dvc init                                   # initialize in git repo
dvc add data/train.csv                     # track file (creates .dvc pointer)
dvc push                                   # push data to remote (S3, GCS)
dvc pull                                   # download tracked data
dvc repro                                  # reproduce pipeline (dvc.yaml)
dvc status                                 # show what changed
dvc diff HEAD~1                            # compare with last commit
dvc run -n train -d data/ -o model.pkl \
  python train.py                          # define pipeline stage

# Remote setup
dvc remote add -d myremote s3://my-bucket/dvc
dvc remote modify myremote region us-east-1
```

## Kubeflow Pipelines (KFP)

```python
from kfp import dsl, compiler

@dsl.component(base_image="python:3.11")
def validate_data(data_path: str) -> bool:
    import great_expectations as ge
    context = ge.get_context()
    results = context.run_checkpoint(checkpoint_name="schema_check")
    return results.success

@dsl.component(packages_to_install=["scikit-learn"])
def train_model(data_path: str, model_path: dsl.Output[dsl.Model]):
    from sklearn.ensemble import GradientBoostingClassifier
    # ... train and save to model_path.path

@dsl.pipeline(name="fraud-pipeline")
def fraud_pipeline(data_path: str = "gs://bucket/data"):
    validate_task = validate_data(data_path=data_path)
    train_task = train_model(data_path=data_path)
    train_task.after(validate_task)

compiler.Compiler().compile(fraud_pipeline, "pipeline.yaml")
```

## Feast Feature Store

```python
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo/")

# Training: historical features with point-in-time joins
training_df = store.get_historical_features(
    entity_df=entity_df,  # columns: entity_id, event_timestamp
    features=["user_features:age", "user_features:transaction_count_7d"]
).to_df()

# Inference: online features (< 10ms)
features = store.get_online_features(
    features=["user_features:age", "user_features:transaction_count_7d"],
    entity_rows=[{"user_id": "u123"}]
).to_dict()

# Materialize offline → online
store.materialize_incremental(end_date=datetime.now())
```

## KServe / InferenceService

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: fraud-detector
  namespace: ml-serving
spec:
  predictor:
    sklearn:
      storageUri: "s3://models/fraud-detector/v12"
      resources:
        requests:
          cpu: "2"
          memory: 4Gi
        limits:
          nvidia.com/gpu: "1"
  canaryTrafficPercent: 10    # 10% to canary
  canary:
    predictor:
      sklearn:
        storageUri: "s3://models/fraud-detector/v13"
```

```bash
kubectl apply -f inference-service.yaml
kubectl get inferenceservice fraud-detector
kubectl get isvc fraud-detector -o jsonpath='{.status.url}'
```

## Triton Inference Server

```
# model_config.pbtxt
name: "bert_classifier"
platform: "onnxruntime_onnx"
max_batch_size: 32

input [{
  name: "input_ids"
  data_type: TYPE_INT64
  dims: [-1, 128]
}]
output [{
  name: "logits"
  data_type: TYPE_FP32
  dims: [-1, 2]
}]

dynamic_batching {
  preferred_batch_size: [8, 16, 32]
  max_queue_delay_microseconds: 5000
}

instance_group [{ count: 2 kind: KIND_GPU }]
```

```bash
# Start Triton
docker run --gpus all -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -v $(pwd)/models:/models \
  nvcr.io/nvidia/tritonserver:24.01-py3 \
  tritonserver --model-repository=/models

# Health check
curl localhost:8000/v2/health/ready

# Model stats
curl localhost:8000/v2/models/bert_classifier/stats
```

## vLLM

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3-8b-instruct", quantization="awq")

outputs = llm.generate(
    ["Explain transformer attention in one paragraph"],
    SamplingParams(temperature=0.7, max_tokens=512)
)

# Serve as OpenAI-compatible API
# python -m vllm.entrypoints.openai.api_server \
#   --model meta-llama/Llama-3-8b-instruct \
#   --quantization awq \
#   --gpu-memory-utilization 0.90 \
#   --max-model-len 8192
```

## Evidently AI Drift Detection

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.metrics import ColumnDriftMetric

report = Report(metrics=[
    DataDriftPreset(),
    DataQualityPreset(),
    ColumnDriftMetric(column_name="income"),
])

report.run(reference_data=train_df, current_data=prod_df)
report.save_html("drift_report.html")

# Extract metrics for Grafana
result = report.as_dict()
dataset_drift = result["metrics"][0]["result"]["dataset_drift"]
drift_share = result["metrics"][0]["result"]["share_of_drifted_columns"]
```

## KEDA for Inference Autoscaling

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: inference-scaler
spec:
  scaleTargetRef:
    name: fraud-detector-deployment
  minReplicaCount: 1
  maxReplicaCount: 20
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus.monitoring:9090
      metricName: nv_inference_queue_duration_ms
      threshold: "100"
      query: avg(nv_inference_queue_duration_ms{model="fraud-detector"})
  - type: cron
    metadata:
      timezone: "America/New_York"
      start: "0 8 * * 1-5"    # scale up at 8am weekdays
      end: "0 20 * * 1-5"     # scale down at 8pm weekdays
      desiredReplicas: "5"
```

## GPU Kubernetes Setup

```yaml
# Request GPU in pod spec
resources:
  requests:
    nvidia.com/gpu: "1"
  limits:
    nvidia.com/gpu: "1"

# MIG slice
resources:
  limits:
    nvidia.com/mig-1g.10gb: "1"

# Toleration for GPU node taint
tolerations:
- key: "nvidia.com/gpu"
  operator: "Exists"
  effect: "NoSchedule"
```

```bash
# Install NVIDIA device plugin
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.5/nvidia-device-plugin.yml

# Check GPU availability
kubectl describe nodes | grep -A5 "nvidia.com/gpu"

# Check GPU utilization in pod
kubectl exec -it <pod> -- nvidia-smi
```

## PyTorch Distributed Training

```python
# Single-node multi-GPU with DDP
torchrun --nproc_per_node=4 train.py

# Multi-node (4 nodes, 8 GPUs each = 32 GPUs total)
torchrun --nnodes=4 --nproc_per_node=8 \
         --node_rank=0 --master_addr="10.0.0.1" --master_port=12355 \
         train.py

# DeepSpeed ZeRO-3
deepspeed --num_gpus=8 train.py --deepspeed ds_zero3_config.json
```

```json
// ds_zero3_config.json
{
  "zero_optimization": {
    "stage": 3,
    "offload_optimizer": {"device": "cpu"},
    "offload_param": {"device": "cpu"}
  },
  "bf16": {"enabled": true},
  "train_micro_batch_size_per_gpu": 4
}
```

## Inference Optimization Techniques

| Technique | Memory | Throughput | Quality Loss | When to Use |
|-----------|--------|-----------|--------------|-------------|
| FP16 / BF16 | 2x | 1.5-2x | Minimal | Default for serving |
| INT8 quantization | 4x | 2x | Small | CPU or GPU inference |
| INT4 / AWQ | 8x | 3-4x | Moderate | Edge, cost-sensitive |
| TensorRT | Same | 2-5x | None | NVIDIA GPU serving |
| ONNX Runtime | Same | 1.5-3x | None | CPU or cross-platform |
| Dynamic batching | — | 2-8x | None | High-concurrency APIs |
| Gradient checkpointing | 4-8x less | -30% | None | Training memory savings |
| KV cache tuning | — | 2x | None | LLM serving |

## Drift Detection Metrics Reference

| Metric | Type | Threshold | Notes |
|--------|------|-----------|-------|
| PSI | Numeric/categorical | < 0.1 OK, > 0.2 retrain | Financial services standard |
| KS test (p-value) | Numeric | p < 0.05 = drift | Kolmogorov-Smirnov |
| KL Divergence | Any | > 0.1 investigate | Not symmetric — use carefully |
| Chi-squared | Categorical | p < 0.05 = drift | Per-category distribution |
| Jensen-Shannon | Any | > 0.1 investigate | Symmetric, bounded [0,1] |
| Wasserstein | Numeric | Domain-specific | Earth Mover's Distance |

## Rollout Pattern Decision Tree

```
New model candidate ready
         │
         ▼
    Shadow deploy (100% traffic mirrored, responses discarded)
    Monitor for 24h: latency, error rate, prediction distribution
         │
    ┌────┴────┐
  PASS      FAIL
    │          │
    ▼          └──► Debug / retrain
  Canary (5%)
  Monitor for 24-48h: business KPIs, latency SLO
         │
    ┌────┴────┐
  PASS      FAIL
    │          │
    ▼          └──► Roll back to champion
  Promote to 100%
  Archive old champion
```

## Common PSI Calculation

```python
import numpy as np

def psi(expected, actual, buckets=10):
    """PSI between reference (expected) and current (actual) distributions."""
    breakpoints = np.linspace(0, 100, buckets + 1)
    expected_pct = np.histogram(expected, np.percentile(expected, breakpoints))[0] / len(expected)
    actual_pct = np.histogram(actual, np.percentile(expected, breakpoints))[0] / len(actual)

    # Avoid division by zero
    expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
    actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)

    return np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
```

## Key Tooling Matrix

| Category | OSS Tool | Managed Alternative |
|----------|----------|-------------------|
| Experiment tracking | MLflow | W&B, Neptune, Comet |
| Data versioning | DVC | Pachyderm, LakeFS |
| Feature store | Feast | Tecton, Vertex AI FS, SageMaker FS |
| Pipeline orchestration | Kubeflow Pipelines, Airflow | Vertex AI Pipelines, SageMaker Pipelines |
| Model registry | MLflow Model Registry | W&B, Databricks Unity Catalog |
| Model serving | KServe, Triton | SageMaker Endpoints, Vertex AI Endpoints |
| LLM serving | vLLM, TGI | Bedrock, Vertex AI, Azure OpenAI |
| Drift monitoring | Evidently, Whylogs | Arize, Fiddler, SageMaker Clarify |
| Hyperparameter tuning | Optuna, Ray Tune | Katib, Vertex AI Vizier |
| Distributed training | DeepSpeed, FSDP | SageMaker Distributed, Vertex AI Training |

## Gotchas

| Gotcha | Detail |
|--------|--------|
| `sensitive = true` doesn't protect state | Only redacts terminal output — value still in MLflow/registry in plaintext |
| Offline metrics don't guarantee online performance | Evaluation set may not match production distribution |
| `for_each` key order matters | Removing a feature from the middle of a list causes reindex |
| DVC doesn't version the data inside git | It stores a pointer; the actual file is in remote storage |
| Feature TTL in online store | Stale features if materialization job falls behind — monitor freshness lag |
| PSI only detects numeric/categorical shift | Doesn't detect temporal ordering violations (label leakage) |
| OIDC token expires during long training | Re-authenticate before artifact push at end of job |
| Shadow mode doubles serving costs | Budget for the duplicate traffic before enabling |
| Gradient checkpointing adds ~30% compute | Don't enable it unless memory is actually constrained |
| KV cache growth with long sequences | Pre-allocate based on max_model_len or OOM mid-request |
