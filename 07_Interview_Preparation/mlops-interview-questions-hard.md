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
