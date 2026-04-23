# MLOps Interview Questions (Hard)

These questions are aimed at senior MLOps, ML platform, and ML infrastructure roles where architecture, reliability, cost, and governance matter as much as tooling.

## Architecture And Scaling

**1. How would you design a multi-region online inference platform for a business-critical model?**

I would separate control plane, artifact storage, feature access, model registry, and serving endpoints by failure domain. The design should include regional failover, model version pinning, data locality, observability, and a clear rollback path.

**2. A model is too large for a single GPU. What are your options?**

Options include model parallelism, tensor parallelism, pipeline parallelism, quantization, distillation, or serving a smaller model tier for latency-critical traffic. The right choice depends on latency targets, throughput, and acceptable quality loss.

**3. How do you monitor model quality in real time when true labels are delayed or unavailable?**

I would use proxy metrics such as confidence shifts, drift signals, output distribution changes, feature freshness, and business KPI proxies. Once labels arrive, I would reconcile those proxies against actual performance.

**4. How do you design an MLOps platform for multiple teams without turning it into a one-off collection of notebooks?**

I would create reusable patterns for data validation, training, registry promotion, deployment, and monitoring. The goal is a paved road with flexibility at the edges, not a bespoke pipeline per model.

**5. What is the hardest part of building a shared feature platform?**

Consistency and ownership. You must keep offline and online definitions aligned, manage schema evolution safely, and make sure feature ownership is clear when upstream data changes.

## Delivery, Rollout, And Governance

**6. Compare shadow deployment, canary deployment, and A/B testing for models.**

Shadow is safest for observing live behavior without user impact. Canary exposes a small amount of real traffic and is useful for rollout safety. A/B testing is best when the goal is optimizing business outcomes across user groups.

**7. How would you prevent a half-trained or invalid model from reaching production?**

I would require registry gates, validation thresholds, lineage completeness, signed promotion steps, and deployment policies that reject unapproved model versions.

**8. How do you handle rollback if the new model is technically healthy but business KPIs are worse?**

That is still a rollback condition. The serving system must support fast reversal to the previous champion, and the release process should include KPI guardrails, not only infrastructure health checks.

**9. How do you govern model promotion in a regulated environment?**

Use approval workflows, model cards, dataset lineage, audit logs, reproducible runs, and clearly separated access between training, review, and production deployment.

**10. How do you avoid "configuration drift" in model-serving systems?**

Treat serving configs, feature configs, and promotion states as versioned artifacts. If model infra is changed manually, the same drift problems appear as in ordinary infrastructure.

## Platform Operations

**11. How would you optimize a Kubernetes cluster for mixed CPU and GPU ML workloads?**

I would isolate GPU pools, use taints and tolerations, size node pools intentionally, and tune autoscaling to avoid constant expensive spin-up or idle waste. Bin packing and workload separation matter more than in generic app clusters.

**12. Training cost has doubled in the last month. How would you investigate it?**

I would look at data growth, experiment explosion, job retries, checkpoint usage, idle GPU time, storage locality, and whether expensive models are being retrained more often than justified.

**13. What is the trade-off between a centralized model-serving platform and service-owned model deployments?**

A centralized platform improves standardization, observability, and governance. Service-owned deployments can move faster for special cases, but usually create inconsistent rollout, monitoring, and security practices.

**14. How do you handle disaster recovery for an MLOps platform?**

You need backups and replication for metadata stores, artifact storage, registry state, and possibly feature stores. Recovery plans must also define how to restore the serving fleet and which model version becomes the initial champion.

## Data, Drift, And Feedback Loops

**15. How do you design retraining triggers without causing unstable model churn?**

I use a combination of schedule, drift thresholds, business KPI thresholds, and minimum data volume. Retraining should be deliberate, because overreacting to noise can be as harmful as not retraining.

**16. How do you decide whether a detected drift event should trigger rollback, retraining, or no action?**

It depends on severity, label availability, KPI impact, and whether the issue is input quality or actual concept change. Drift is a signal for investigation, not an automatic conclusion.

**17. How do you handle feature freshness problems in real-time inference?**

I would define freshness SLOs, monitor lag, add fallback logic where safe, and make the failure mode explicit. In some systems, stale features should block prediction rather than silently return misleading outputs.

**18. What is the most dangerous type of MLOps issue that looks like an infrastructure problem but is actually a data problem?**

Training-serving skew is a strong example. The service can be healthy, scaled, and fast while producing systematically wrong outputs due to mismatched transformations or stale features.

## LLMOps And Advanced Serving

**19. How would you evaluate and release a new LLM-based workflow safely?**

I would version prompts, retrieval logic, model configuration, and evaluation datasets. Then I would use offline evals, shadow traffic, safety checks, fallback behavior, and business KPI monitoring before broader rollout.

**20. How do you reason about throughput versus cost in large-model inference?**

I look at model size, token throughput, batching, cache hit rate, latency SLOs, concurrency, and fallback tiers. For large models, cost control is part of platform design, not an afterthought.

**21. When is quantization a good idea, and what do you trade away?**

Quantization reduces memory and can improve serving efficiency, but it may reduce accuracy or change model behavior. It is useful when hardware limits or inference cost are the main bottlenecks.

**22. How would you standardize evaluation across multiple ML teams?**

I would define shared metrics, baseline datasets, evaluation templates, registry metadata requirements, and promotion criteria. Teams can still add domain-specific checks, but the platform should enforce a common minimum bar.

***

## Multi-GPU Training & Distributed Systems (HARD - Extended)

**23. Compare tensor parallelism, pipeline parallelism, and data parallelism for training a 70B parameter model.**

For a 70B model that does not fit in a single GPU:
- **Data parallelism (DP):** Each GPU holds the full model and processes different mini-batches. AllReduce synchronizes gradients. Only works if the model fits in one GPU — not viable for 70B on a single A100 (80GB).
- **Tensor parallelism (TP):** Each linear layer is split column-wise/row-wise across N GPUs. A single matrix multiply is computed in parallel across GPUs with AllReduce communications per layer. High communication overhead — requires NVLink bandwidth. Typical: TP degree 4-8 within a node.
- **Pipeline parallelism (PP):** The model's layers are staged across GPUs. GPU 0 runs layers 1-10, GPU 1 runs layers 11-20, etc. Micro-batching fills the pipeline to reduce bubble fraction. PP allows spanning nodes connected by Ethernet (lower bandwidth acceptable) but introduces pipeline bubble overhead.
- **3D parallelism (Megatron-DeepSpeed):** Combines all three: DP across node groups, TP within nodes (NVLink), PP across nodes. For 70B, a typical configuration: TP=8 (within node), PP=4 (across 4 nodes), DP=2 (two data parallel replicas). ZeRO optimizer shards optimizer states and gradients across DP replicas to reduce memory per GPU.

**24. How does ZeRO (Zero Redundancy Optimizer) work and what are the three stages?**

ZeRO reduces memory redundancy in data parallel training where each GPU redundantly stores the full optimizer state, gradients, and parameters:
- **ZeRO Stage 1:** Shard optimizer state across DP ranks. Each GPU only stores `1/N` of optimizer states (Adam moments). Reduces optimizer state memory by N×.
- **ZeRO Stage 2:** Stage 1 + shard gradients across DP ranks. Gradients are accumulated locally and then reduced to the owning rank. Reduces gradient memory by N×.
- **ZeRO Stage 3:** Stage 2 + shard model parameters across DP ranks. Parameters are gathered (AllGather) before use in forward/backward pass. Most memory-efficient but highest communication overhead. A 70B model with ZeRO Stage 3 across 64 GPUs reduces per-GPU parameter memory from 140GB to ~2.2GB.
- **ZeRO-Infinity:** Offloads parameters and optimizer state to CPU RAM or NVMe storage, enabling training models too large for all GPU memory combined.

**25. How do you design a fault-tolerant distributed training job on Kubernetes?**

Failure modes and mitigations:
- **Node failure mid-training:** Use PyTorch Elastic Training (`torchrun` with `--rdzv_backend etcd`) which allows dynamic membership changes — surviving nodes resume training without full restart. Requires checkpointing at regular intervals.
- **Checkpointing strategy:** Save model state, optimizer state, and RNG state every N steps to S3/GCS. On pod restart, resume from the latest checkpoint. Use `torch.distributed.checkpoint` for distributed checkpoints that each rank saves its own shard.
- **Kubernetes job management:** Use the Kubeflow Training Operator's `PyTorchJob` CRD with `restartPolicy: OnFailure`. The operator handles pod re-scheduling on node failure.
- **Spot instance preemption:** For cost-efficient training on preemptible nodes, use `spot-sigterm-handler` sidecars that catch SIGTERM and trigger an immediate checkpoint before pod termination.
- **Health monitoring:** Leader election among workers to detect hung nodes (no heartbeat within 60s = stale worker). Reinitialize distributed group excluding the failed node if Elastic Training is enabled.

**26. What is gradient checkpointing and when do you use it?**

Gradient checkpointing (also called activation checkpointing) trades compute for memory during backpropagation. Normally, all intermediate activations from the forward pass are retained in memory for computing gradients during backward. With gradient checkpointing, only a subset of activations is stored; the rest are recomputed on-the-fly during the backward pass from the nearest checkpoint. Cost: 30-40% more compute per step. Benefit: memory usage drops from O(n_layers) to O(√n_layers). Use it when: training large models where activation memory is the memory bottleneck (common for long-sequence transformers), combined with mixed precision to further reduce memory. In PyTorch: `torch.utils.checkpoint.checkpoint(layer, input)`.

**27. How do you profile and optimize a training loop that is GPU-bound vs. CPU-bound?**

Diagnosis: Use PyTorch Profiler or NVIDIA Nsight Systems.
- **GPU-bound:** GPU utilization near 100% (`nvidia-smi`), CPU idle. Optimizations: increase batch size (better GPU utilization), use AMP (mixed precision) to reduce memory and enable Tensor Core usage, use `torch.compile()` or TorchScript to reduce Python overhead, use CUDA Graph to reduce kernel launch overhead.
- **CPU-bound (data loading bottleneck):** GPU utilization fluctuates (GPU idle waiting for data). `DataLoader` profiling shows long `collate_fn` or disk read times. Optimizations: increase `num_workers` (multi-process data loading), use `pin_memory=True` for faster H2D transfers, pre-process and cache datasets, use WebDataset for streaming large datasets from object storage.
- **Communication-bound (distributed training):** AllReduce operations dominate the profile. Use gradient compression (PowerSGD), increase gradient accumulation steps (fewer AllReduce calls), use FSDP with communication-computation overlap.

***

## LLMOps & Advanced Serving (HARD - Extended)

**28. How does vLLM's PagedAttention work and why does it dramatically improve LLM serving throughput?**

In standard LLM serving, the KV cache (key-value pairs from the attention mechanism) is pre-allocated per request based on the maximum possible sequence length — even if most requests are short. This wastes GPU memory and limits concurrent requests. PagedAttention (from vLLM) applies virtual memory concepts to KV cache management:
- **Logical KV blocks** are allocated per request in variable sizes matching actual sequence growth.
- **Physical memory pages** (fixed-size blocks, e.g., 16 tokens per block) are allocated from a pool only as needed.
- A **block table** maps logical blocks to physical pages, enabling non-contiguous physical allocation.
- When a request finishes, its physical pages are returned to the pool immediately (no fragmentation).
- **Copy-on-write** enables prefix sharing: multiple requests sharing the same system prompt share the same physical KV pages until they diverge.
Result: near-zero KV cache memory waste, 2-4× more concurrent requests per GPU, and significantly higher throughput (tokens/second) compared to naive pre-allocation.

**29. How do you design a Triton Inference Server deployment for multi-model serving with dynamic batching?**

Triton architecture for production:
1. **Model repository:** Mount models (ONNX, TensorRT, PyTorch) in a structured directory. Each model has a `config.pbtxt` defining backend, input/output shapes, and batching config:
```
dynamic_batching {
  preferred_batch_size: [8, 16]
  max_queue_delay_microseconds: 5000
}
max_batch_size: 32
```
2. **Dynamic batching:** Triton accumulates requests into batches up to `max_queue_delay_microseconds` before dispatching to the model. This amortizes fixed inference overhead across multiple requests.
3. **Model instances:** Configure `instance_group: { kind: KIND_GPU, count: 2 }` to run two model instances per GPU (for CPU-bound preprocessing + GPU inference overlap).
4. **Ensemble pipeline:** Chain preprocessing → model → postprocessing as a Triton ensemble — single client request triggers the full pipeline internally.
5. **Multi-model GPU sharing:** Triton manages GPU memory across all loaded models. Models with `priority: HIGH` preempt lower-priority models during memory pressure.
6. **Load balancing:** Deploy multiple Triton pods behind a Kubernetes Service. Use least-connection load balancing (not round-robin) to handle request-duration variability.

**30. How do you build a production RAG (Retrieval-Augmented Generation) pipeline and what are the failure modes?**

RAG architecture components:
1. **Ingestion pipeline:** Documents → chunking (fixed-size, semantic, or recursive) → embedding model → vector database (Pinecone, Weaviate, pgvector). Chunking strategy significantly impacts recall — too small loses context, too large reduces relevance precision.
2. **Retrieval:** Query → embedding → ANN search in vector DB → top-K chunks retrieved. Hybrid retrieval: combine dense (embedding) and sparse (BM25 keyword) search with RRF (Reciprocal Rank Fusion) for better coverage.
3. **Generation:** Retrieved chunks + query → LLM → response.

Failure modes by stage:
- **Embedding drift:** If the embedding model is updated, old document vectors become incompatible with new query vectors. Mitigation: version the embedding model, re-embed corpus on model update.
- **Retrieval hallucination:** Retrieved chunks are irrelevant; LLM hallucinates a response using its parametric knowledge instead. Mitigation: add retrieval confidence thresholds, include a "cannot answer from provided context" fallback.
- **Context window overflow:** Retrieved chunks exceed LLM context window. Mitigation: implement re-ranking (cross-encoder) to select the most relevant K chunks before truncation.
- **Staleness:** Vector DB contains outdated document versions. Mitigation: trigger incremental re-ingestion when source documents are updated (document update webhooks → re-chunk and upsert changed document chunks with deletion of old chunks).
- **Latency:** Embedding + ANN search + LLM = stacked latency. Mitigation: cache frequent query embeddings, use approximate (not exact) ANN, use smaller embedding model for retrieval, async streaming of LLM response.

**31. How do you evaluate a RAG system quantitatively using RAGAS?**

RAGAS (Retrieval-Augmented Generation Assessment) provides four key metrics:
- **Faithfulness:** Is the answer grounded in the retrieved context? (Score: 0-1, measures hallucination). Computed by LLM-based decomposition of answer into claims, then verifying each claim against retrieved chunks.
- **Answer Relevance:** Is the answer relevant to the question, independent of correctness? Low score = answer is factual but off-topic.
- **Context Precision:** Of the retrieved chunks, what fraction are actually relevant to the question? Measures retrieval over-retrieval.
- **Context Recall:** Of all ground-truth relevant information, what fraction was retrieved? Measures retrieval under-retrieval.

Integration into CI: run RAGAS evaluation as a pipeline step using a golden dataset (question/answer/ground-truth pairs curated by domain experts). Gate promotion on: Faithfulness > 0.85, Context Recall > 0.80. Regression in these scores on a new embedding model or chunking strategy blocks deployment.

**32. What is prompt engineering at the platform level and how do you version and test prompts?**

Platform-level prompt engineering goes beyond crafting prompts manually:
- **Prompt versioning:** Store prompts in a registry (LangSmith, PromptLayer, custom Git-backed registry) with semantic versioning. Each prompt version has: template text, model target, temperature/sampling config, and evaluation results.
- **Prompt testing:** A/B test prompt variants on shadow traffic before promoting. Automated evaluation using RAGAS, G-Eval, or reference-based metrics on golden datasets. Regression tests: ensure prompt changes don't degrade performance on a held-out benchmark.
- **Prompt injection defense:** For user-facing prompts, implement input validation (detect jailbreak patterns), system prompt isolation (separate system prompt namespace from user input), and output filtering (detect policy violations before returning responses).
- **Cost tracking:** Different prompts result in different token counts. Track average input/output tokens per prompt version and alert when a prompt change significantly increases average token cost.

**33. How do you design an ML governance framework for a regulated financial services company?**

Governance pillars:
1. **Model inventory:** Every model in production is registered in a model catalog with: owner, use case, business impact rating (high/medium/low), data inputs, performance thresholds, monitoring plan, and last review date.
2. **Pre-deployment approval:** High-impact models require: independent model validation (separate team reviews methodology, data, and results), bias assessment (Fairlearn), explainability report (SHAP), and sign-off from Risk and Compliance.
3. **Continuous monitoring obligations:** High-impact models: daily monitoring reports, monthly performance reviews, quarterly bias re-evaluation, annual full model revalidation.
4. **Change management:** Any change to a production model (retrain, feature change, threshold adjustment) triggers a new review proportional to the change's risk level. Emergency changes (hotfixes) have a 24-hour expedited review with post-hoc full review.
5. **Audit trail:** Immutable logs of all model transitions, dataset accesses, evaluation results, and approval decisions stored for 7 years (financial regulatory requirement). OpenLineage + Marquez for data lineage; MLflow Model Registry for model lifecycle events.
6. **Model retirement:** Documented process for decommissioning models — including impact assessment, handoff plan, data retention decision, and stakeholder notification.

**34. How do you handle multi-region model serving with data residency requirements?**

Architecture for GDPR-compliant multi-region serving:
- **Regional model deployments:** Deploy separate serving infrastructure in each required data sovereignty region (EU, US, APAC). EU user requests are routed exclusively to EU serving infrastructure — traffic never crosses regional boundaries.
- **Model artifact distribution:** Use a regional artifact registry per region. CI/CD copies model artifacts to all required regional registries. Each region's serving deployment pulls from its local registry.
- **Feature Store per region:** Regional Feature Store deployments (Feast with regional Redis + regional offline store). EU user features never stored outside EU.
- **Data plane isolation:** Verify isolation at the network level: VNet/VPC per region with no cross-region peering for data paths. Only control plane communications (metrics, model registry sync) are allowed cross-region and carry no personal data.
- **Consistency challenge:** Models may diverge across regions if training data differs by region. Mitigate by: training on anonymized global datasets with regional fine-tuning only, or accepting regional model variants with separate evaluation and monitoring per region.

**35. How do you implement online learning for a model that must adapt to streaming data?**

Online learning systems update model weights continuously from new data without retraining from scratch:
- **Approaches:** (1) Full model retraining triggered frequently (hourly/daily) on recent data windows — simple but expensive. (2) Warm-start incremental training: initialize from the current production model and fine-tune on the new data batch. (3) True online learning: update weights after each example using SGD or river (Python ML library for streaming). (4) Contextual bandit: model adapts by exploring action space and updating from reward signals in real time.
- **Infrastructure:** Stream processing (Kafka → Flink) to compute real-time features; model update service consuming processed feature batches; shadow deployment of updated model for validation before replacing production.
- **Stability controls:** Apply learning rate decay, clip gradient norms, maintain a frozen baseline model for comparison. If updated model's validation metrics degrade >5% from baseline, halt updates and page on-call. Use exponential moving average of weights to smooth rapid updates.
- **Concept drift handling:** Monitor both input distribution and output distribution. When drift is detected, increase learning rate temporarily to accelerate adaptation, then decay back to the stable rate once the distribution stabilizes.

**36. How would you design a cost-optimization strategy for LLM inference at scale (10M requests/day)?**

Multi-layer cost optimization:
1. **Request routing by complexity:** Implement a classifier that routes simple requests (short queries, factual lookups) to a smaller, cheaper model (e.g., GPT-3.5-class or a fine-tuned 7B model) and routes complex requests to the large model. Classify using embedding similarity against a complexity-scored golden set. Target: route 60-70% of traffic to the small model.
2. **Semantic caching:** Cache LLM responses by embedding similarity of the query. Incoming queries are embedded and compared against a Redis vector cache. If cosine similarity > 0.95, return the cached response without calling the LLM. Effective for FAQ-like patterns. Tools: GPTCache, semantic-cache.
3. **KV cache sharing (prefix caching):** For requests sharing a common system prompt (common in enterprise deployments), use vLLM's prefix caching to share KV cache pages, eliminating redundant prefill computation.
4. **Quantization and hardware:** Serve quantized models (INT4/INT8) on fewer GPUs. For 10M requests/day at 1000 tokens average: benchmark throughput per GPU across quantization levels and pick the highest tokens/dollar on spot instances.
5. **Batching + async queuing:** Use SQS → Lambda → Triton/vLLM batch endpoint. Accumulate requests in queue, batch dispatch for maximum GPU utilization.
6. **Cost observability:** Track cost per request per model tier with Prometheus metrics. Alert when cost/request exceeds budget threshold ($0.002/request at scale). Monthly Kubecost report by model tier and requesting team for chargeback.
