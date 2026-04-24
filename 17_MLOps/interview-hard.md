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

---

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

