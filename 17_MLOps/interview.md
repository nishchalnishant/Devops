# MLOps — Interview Questions

All difficulty levels combined.

---

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

---

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
