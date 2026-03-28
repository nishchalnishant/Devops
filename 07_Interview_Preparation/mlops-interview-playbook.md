# MLOps Interview Playbook

Use this file for MLOps, ML platform, ML infrastructure, inference platform, and model-serving interviews.

## What Interviewers Are Really Testing

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

## A Strong MLOps Answer Framework

For most interview questions, use this structure:

1. Identify whether the problem is in data, training, model, serving, or platform.
2. Clarify the artifact versions involved: code, data, features, model, config.
3. Explain how you would validate correctness before optimizing performance.
4. Talk about safe rollout, rollback, and observability.
5. Close with reproducibility and prevention controls.

Example:

> I would first separate platform health from model correctness. If the endpoint is healthy but predictions are wrong, I would validate input schema, feature transformation parity, model version, and registry lineage before changing infrastructure.

## What You Should Know By Topic

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

## Must-Know Commands And Checks

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

## High-Value Scenarios To Practice

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

## Strong Signals In Senior MLOps Answers

- You distinguish platform health from model quality.
- You talk about lineage and reproducibility without being prompted.
- You mention rollout safety and rollback for models, not just services.
- You connect data quality and feature quality to production risk.
- You think about cost, GPU utilization, and throughput, not just model accuracy.

## Common Weak Signals

- Treating MLOps as ordinary CI/CD with a notebook attached
- Ignoring data versioning
- Saying the model is fine because the endpoint returned `200`
- Recommending retraining without defining a trigger or validation gate
- Ignoring feature skew and delayed labels

## Final Revision Checklist

- I can explain the difference between DevOps and MLOps.
- I can explain reproducibility across code, data, features, and model versions.
- I can explain model registry, feature store, experiment tracking, and drift.
- I can discuss batch, online, and async inference trade-offs.
- I can explain safe rollout patterns for new models.
- I can troubleshoot wrong predictions even when infrastructure is healthy.
- I can discuss GPU scheduling, latency, and cost trade-offs at a senior level.
