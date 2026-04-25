# MLOps Tips & Tricks

Production-tested patterns, anti-patterns, and gotchas for ML systems in production.

***

## The #1 MLOps Mistake: Treating ML Like Software

```
Software: if tests pass and code is correct, the application works
ML:       if tests pass and code is correct, the MODEL might be wrong

What changes in ML that doesn't change in software:
  1. Data distribution (the world changes; your model doesn't)
  2. Upstream data schema (column renamed → silent null values)
  3. Feature engineering logic (library update changes behavior subtly)
  4. Ground truth labels (labeling team uses a different interpretation)
```

**Implication:** ML systems require a fundamentally different monitoring approach — you must monitor **data and model behavior**, not just infrastructure.

***

## Feature Engineering Pitfalls

### Training-serving skew — the silent killer
```
Training time:   average_session_length = sessions.groupby('user').mean()
                 → uses all historical sessions (including the current one!)

Serving time:    average_session_length = fetch_from_feature_store()
                 → feature store computes on sessions BEFORE the current request

The problem: the training feature includes data the model wouldn't have at serving time.
Result: model performs 15% better in training than in production — training-serving skew.

Prevention:
  1. Use a feature store with point-in-time correct queries
  2. Validate that training and serving pipelines use IDENTICAL feature computation code
  3. Log serving features and compare their distribution to training features
```

### Feature nulls / schema drift
```python
# BAD: silent null propagation
df['user_age_group'] = df['age'] // 10  # Returns NaN for missing age silently

# GOOD: explicit handling + alerting
if df['age'].isnull().sum() > 0.01 * len(df):
    raise DataQualityError("age null rate exceeds 1% — upstream schema may have changed")
df['age'] = df['age'].fillna(df['age'].median())
```

***

## Model Monitoring — What to Actually Monitor

### Three things to monitor (in priority order)

1. **Output distribution (most important, most ignored):**
   ```python
   # What the model is actually outputting
   # If the predicted churn score distribution shifts, something changed
   # (data, model, or both)
   
   # Alert: if mean prediction score shifts > 2 standard deviations from baseline
   current_mean = predictions.mean()
   if abs(current_mean - baseline_mean) > 2 * baseline_std:
       alert("Model output distribution shifted significantly")
   ```

2. **Feature distribution (data drift):**
   ```python
   # Use statistical tests to compare production feature distribution vs training
   from scipy.stats import ks_2samp
   
   statistic, p_value = ks_2samp(training_features['age'], serving_features['age'])
   if p_value < 0.05:
       alert(f"Data drift detected in 'age' feature (KS test p={p_value:.4f})")
   ```

3. **Ground truth / accuracy (slowest signal, but required):**
   ```
   # Hard: ground truth may arrive days or weeks later
   # Churn model: prediction made today, truth known in 30 days
   
   # Strategy: delayed evaluation pipeline
   # Day 0: log (user_id, predicted_churn_prob)
   # Day 30: join with actual_churn label
   # Day 30: compute precision, recall, AUC → alert if below threshold
   ```

***

## CI/CD for ML (CT — Continuous Training)

### The ML pipeline hierarchy
```
Level 0: Manual training — data scientists run notebooks manually
Level 1: ML pipeline automation — training runs on schedule or data trigger
Level 2: CT/CD — training is triggered by code change, data drift, or metric degradation;
          new models are auto-validated and promoted without human approval for regressions

# Most companies are at Level 0-1. Level 2 requires:
# - Reliable model validation pipeline
# - Automated A/B or shadow testing infrastructure
# - Strong data quality monitoring (garbage in → garbage model auto-promoted)
```

### Never retrain without validating on a held-out test set
```python
# Retrain pipeline validation gate
new_model_auc = evaluate(new_model, test_set)
prod_model_auc = evaluate(prod_model, test_set)

if new_model_auc < prod_model_auc - 0.005:  # 0.5% tolerance
    raise ModelRegressionError(
        f"New model AUC ({new_model_auc:.3f}) is worse than production "
        f"({prod_model_auc:.3f}). Blocking promotion."
    )
```

### Model versioning — what to version together
```
✓ Model weights/artifacts
✓ Feature engineering code (exact commit SHA)
✓ Training data version (date range or dataset hash)
✓ Hyperparameters
✓ Evaluation metrics on validation set
✓ Environment (requirements.txt, Python version, CUDA version)

# If any of these change between training runs, it's a different model
# MLflow, W&B, and Neptune all handle this — pick one and use it consistently
```

***

## Model Serving Performance

### GPU utilization is the key cost metric
```bash
# Check GPU utilization on inference server
nvidia-smi dmon -s u   # Streaming GPU memory and compute utilization

# Target: > 70% GPU compute utilization for production inference
# If < 30%: you're paying for idle GPU — use request batching

# Triton batching config:
# dynamic_batching {
#   preferred_batch_size: [8, 16]
#   max_queue_delay_microseconds: 5000   # Wait up to 5ms to fill a batch
# }
```

### The cold start problem in serverless inference
```
Problem: Kubernetes scales to zero at night; first morning request takes 30-60s
         (container startup + model loading + GPU warm-up)

Solutions (in order of cost):
  1. KEDA with min replicas = 1 (always warm, small cost)
  2. Scheduled scale-up: cron to pre-warm before business hours
  3. Model caching in persistent volume (faster load from PV than S3)
  4. Quantized models load 4x faster (INT8 vs FP32)
  5. Triton model warm-up: --model-ready-timeout=0 delays serving until model is warm
```

### vLLM for LLM serving — key settings
```python
# PagedAttention + continuous batching = handle variable-length requests efficiently
from vllm import LLM

llm = LLM(
    model="mistralai/Mistral-7B-v0.1",
    tensor_parallel_size=2,       # Spread across 2 GPUs
    gpu_memory_utilization=0.85,  # Leave 15% for overhead
    max_num_batched_tokens=4096,  # Max tokens in a single batch
    enable_prefix_caching=True,   # Cache common prompt prefixes (RAG patterns)
)

# Key metric to monitor: Token generation throughput (tokens/second)
# Target: > 50 tokens/second per GPU for 7B models
```

***

## Experiment Management

### The experiment tracking minimum viable setup
```python
import mlflow

# Every training run should log:
with mlflow.start_run():
    mlflow.log_params({
        "model_type": "XGBoost",
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
    })
    # ... training ...
    mlflow.log_metrics({
        "train_auc": train_auc,
        "val_auc": val_auc,
        "val_precision": val_precision,
    })
    mlflow.log_artifact("feature_importance.png")
    mlflow.sklearn.log_model(model, "model")
    
    # Critical: log data lineage
    mlflow.set_tag("training_data_version", "2024-01-01_to_2024-06-30")
    mlflow.set_tag("git_commit", subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip())
```

### Reproducibility checklist
```
□ Seed set for all random operations: numpy, torch, sklearn, Python random
□ Training data version logged
□ All hyperparameters logged (not just the ones you tuned)
□ Python + library versions pinned in requirements.txt or conda env
□ Data preprocessing code at exact Git SHA logged with the model
□ Deterministic data loader (shuffle=False in validation, fixed seed in training)
```

***

## Common Production Anti-Patterns

| Anti-Pattern | Problem | Fix |
|:---|:---|:---|
| Pickle for model serialization | Version-dependent, security risk (arbitrary code execution on load) | Use ONNX, SavedModel, or framework-native formats |
| Training on production database directly | Lock contention, GDPR risk | Always train on a read replica or exported snapshot |
| One giant notebook for training | Not reproducible, not testable, not deployable | Split into modular scripts with unit tests |
| Skipping validation for "quick" retrains | A bad retrain can be silent and degrade for weeks | Always gate on held-out evaluation |
| Same feature store for training and serving without TTL | Stale features in serving or data leakage in training | Enforce point-in-time queries in training |
| No rollback plan for model updates | Can't quickly recover from a bad promotion | Keep previous model artifact registered; one-line rollback in serving config |
| Logging features as floats only | Loses interpretability | Log raw string values + numerical encoded values together |
