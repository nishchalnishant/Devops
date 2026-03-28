# MLOps Interview Questions (Medium)

These questions focus on practical MLOps design, delivery, observability, and platform operations.

## Pipelines And Reproducibility

**1. How would you design a basic MLOps pipeline from data to deployment?**

I would separate the flow into data validation, feature preparation, training, evaluation, model registration, approval, deployment, and monitoring. I would also capture lineage across code, data version, model artifact, and environment.

**2. How do you make a training run reproducible?**

Version the code, training data, feature definitions, hyperparameters, environment, and final model artifact. Without all of those, you can reproduce only part of the run.

**3. How do you decide when a model is ready for promotion from staging to production?**

I would require offline evaluation thresholds, validation checks, lineage completeness, and a deployment strategy such as shadow or canary. The decision should include both technical and business metrics.

**4. What is the role of CI in MLOps if the model is trained later?**

CI still validates the code, tests feature transformations, checks schemas, runs quality gates, and ensures pipeline definitions are valid. It reduces the chance of broken training or serving logic before retraining happens.

**5. What triggers a continuous training pipeline?**

Typical triggers include a schedule, new data arrival, detected drift, business KPI degradation, or a manual approval from a model owner.

## Data And Features

**6. How do you prevent training-serving skew?**

Use shared feature definitions, a feature store, or a common transformation library for both training and inference. I also validate example payloads and compare offline and online feature distributions.

**7. When is a feature store worth introducing?**

A feature store is useful when multiple models share features, online and offline consistency matters, or teams are repeatedly rebuilding the same feature logic.

**8. How do you handle schema changes in upstream data sources?**

I add schema validation, contract checks, and backward-compatible evolution rules. Breaking changes should fail fast before they poison training or live inference.

**9. How do you validate data quality before training?**

I would check schema, null rates, range violations, cardinality changes, duplicates, freshness, and label availability. Data validation should be a gated pipeline step, not a manual afterthought.

**10. How do you deal with stale features in an online prediction system?**

I would monitor feature freshness, timestamp lag, cache behavior, and fallback logic. Some systems should fail closed, while others may need a degraded-mode prediction path.

## Serving And Release Safety

**11. When would you choose batch inference instead of online inference?**

Use batch inference when latency is not user-facing and throughput or cost efficiency matters more than real-time response, such as nightly scoring or scheduled recommendations.

**12. When is async inference the right design?**

Async inference is useful when the request takes too long for a synchronous API but still needs a request-response workflow through queues, callbacks, or status polling.

**13. How do you deploy a new model safely?**

I prefer a rollout path such as shadow, canary, or champion-challenger. The model should promote only after both serving health and prediction-quality signals look acceptable.

**14. How do you choose between KServe, Triton, and a custom API container?**

I choose based on model framework support, scaling needs, batching needs, GPU use, routing complexity, and the team's operational maturity. The best tool depends on whether the main problem is standardized serving, high-performance inference, or custom business logic.

**15. Why might a custom serving container still be necessary even with a model-serving framework?**

Some use cases need custom preprocessing, postprocessing, feature lookups, or business-specific routing that off-the-shelf serving frameworks do not handle cleanly.

## Observability And Monitoring

**16. How do you monitor drift when labels arrive hours or days later?**

I use proxy metrics such as confidence shifts, output distribution changes, feature distribution drift, and business KPI proxies until labeled feedback becomes available.

**17. What metrics would you put on a dashboard for a production inference service?**

Latency, throughput, error rate, autoscaling state, model version, feature freshness, confidence distribution, drift metrics, and a business KPI such as conversion or fraud catch rate.

**18. How do you know whether a bad result comes from the model or the platform?**

I first separate serving health from prediction correctness. If the endpoint is healthy, I validate payload schema, feature generation, model version, and drift before blaming compute or networking.

**19. Why are business metrics important in MLOps monitoring?**

Because a model can be technically available and still damage outcomes such as revenue, fraud detection, approval quality, or user engagement.

**20. How do you reduce alert fatigue in MLOps systems?**

I avoid paging on every metric anomaly. I separate infrastructure alerts from model-quality alerts, route them to the right owners, and page only on user-impacting or policy-impacting conditions.

## Platform And Infrastructure

**21. How do you manage GPU workloads in Kubernetes efficiently?**

Use node pools dedicated to GPU workloads, device plugins, taints and tolerations, proper resource requests, and autoscaling policies that respect cost and startup time.

**22. Why is checkpointing important for long-running training jobs?**

Because training jobs may be interrupted by failures or spot instance eviction. Checkpoints allow resuming progress instead of restarting from zero.

**23. How do you decide between CPU and GPU inference?**

I compare latency targets, model size, throughput needs, and cost. Some lighter models run cheaply and well on CPU, while larger deep-learning models need GPU for acceptable latency.

**24. What does model batching trade off in inference?**

Batching can improve throughput and GPU efficiency, but it may increase individual request latency if not tuned carefully.

**25. How do you prevent expensive GPU nodes from running ordinary workloads?**

Use taints, tolerations, node selectors, quotas, and admission rules so only approved ML workloads can consume GPU capacity.

## Security, Governance, And Delivery

**26. How do you secure model and dataset access in an MLOps platform?**

Use role-based access, short-lived credentials, audit trails, and separate permissions for data access, model promotion, and production deployment.

**27. What should be reviewed before approving a model for production in a regulated environment?**

Lineage, evaluation results, data source approval, explainability needs, monitoring plan, rollback path, and who approved the release.

**28. How do you handle secrets in training and inference pipelines?**

Never hardcode them in notebooks or pipeline code. Use a secret manager or platform-native secret store with role-based access and auditability.

**29. Why does MLOps need stronger lineage than many traditional applications?**

Because model behavior depends on data and experiments, not just code. When something goes wrong, you need to trace the exact training inputs and promotion path.

**30. How would you integrate Terraform into an MLOps platform?**

I would use Terraform to provision the infrastructure layer such as networks, clusters, storage, IAM, and registries, while model-specific delivery happens through pipelines and serving frameworks.
