# Scenario-Based MLOps Interview Drills

Use these drills for MLOps, ML platform, model-serving, inference, training-platform, and LLMOps interviews.

## How To Answer MLOps Scenarios

For each scenario:

1. Separate platform health from model correctness.
2. Identify the active artifact versions: code, data, features, model, config, and serving runtime.
3. Check rollout history and recent data, schema, or feature changes.
4. Use metrics for both service health and model-quality signals.
5. Mitigate safely before optimizing.
6. Close with reproducibility, rollback, and prevention.

## First 5 Minutes Checklist

When the interviewer gives you an MLOps production incident, a strong opening sounds like this:

1. I would confirm whether the problem is availability, latency, cost, or prediction quality.
2. I would identify which model version and feature pipeline version are serving traffic.
3. I would check whether a recent release, retraining job, or upstream data change happened.
4. I would decide whether the safest action is rollback, traffic reduction, degraded mode, or closer observation.

## What To Look At In Almost Every MLOps Scenario

### Model-Specific Signals

- model version and registry stage
- experiment run ID
- training dataset version
- feature view version
- offline evaluation metrics

### Serving Signals

- p50, p95, and p99 latency
- throughput
- error rate
- autoscaling state
- model load time and cold starts

### Data And Feature Signals

- schema validation failures
- feature freshness lag
- null rate changes
- cardinality changes
- drift metrics

### Business And Outcome Signals

- KPI movement such as CTR, approval rate, fraud catch rate, or conversion
- confidence score changes
- output distribution shifts
- delayed-label trends when ground truth is not immediate

## Scenario 1: `200 OK` But Predictions Are Wrong

### Prompt

The inference endpoint is healthy and returning `200 OK`, but downstream teams report obviously wrong predictions after a new model release.

### What A Strong Answer Should Cover

- This is likely a correctness problem, not an infrastructure outage.
- Validate payload schema, feature order, transformation parity, model version, and registry lineage.
- Check whether the wrong model or wrong feature view was promoted.

### First Things To Inspect

- registry stage and current serving model URI
- sample request and response against known-good payloads
- online feature values versus training-time expectations
- recent schema or feature-pipeline changes

### Commands And Checks You Can Name

- `curl` a known-good payload to the inference endpoint
- inspect model version in MLflow or registry metadata
- compare online features to offline feature snapshots
- review recent deployment or pipeline history

### Likely Root Causes

- feature skew
- input schema mismatch
- wrong registry version or bad promotion
- stale or missing online features
- incorrect preprocessing in the serving container

### Strong Mitigation Ideas

- roll back to the previous model
- pin the serving endpoint to the last known-good registry version
- switch to cached or champion features if the online feature path is broken
- block additional traffic to the bad release

### Long-Term Prevention

- schema contracts at the serving boundary
- feature validation before rollout
- registry promotion gates that include sample payload tests
- automated comparison between offline and online transformations

### Follow-Up Questions Interviewers Often Ask

- How would you prove whether the bug is in features versus the model itself?
- What would you log without leaking PII?
- How would you design a smoke test for model correctness?

## Scenario 2: GPU Inference Pods Are Stuck In `Pending`

### Prompt

New inference pods cannot start during traffic growth because the GPU-backed pods remain in `Pending`.

### What A Strong Answer Should Cover

- Distinguish scheduler constraints from GPU runtime issues.
- Check capacity, node isolation rules, quotas, and device plugin health.
- Mention that GPU scarcity is both a reliability and cost issue.

### First Things To Inspect

- `describe` output for the pending pod
- node pool capacity and allocatable GPU count
- device plugin DaemonSet health
- taints, tolerations, and namespace quotas

### Commands And Checks You Can Name

- `kubectl describe pod <name>`
- `kubectl describe node <name>`
- `kubectl get events --sort-by=.lastTimestamp`
- `kubectl get ds -A`
- `nvidia-smi`

### Likely Root Causes

- no free GPU capacity
- missing or unhealthy device plugin
- taints and tolerations mismatch
- driver or CUDA incompatibility
- quota limits

### Strong Mitigation Ideas

- scale the GPU node group if capacity is the problem
- shift non-critical traffic off the expensive model tier
- fix plugin health or scheduling rules
- temporarily use a CPU fallback model if business impact is severe

### Long-Term Prevention

- dedicated GPU node pools
- quotas per team or namespace
- autoscaling with warm capacity for latency-sensitive models
- admission controls that prevent non-ML workloads from using GPU nodes

### Follow-Up Questions Interviewers Often Ask

- How do you keep GPU nodes from sitting idle?
- When would you choose warm standby capacity?
- How would you isolate training and inference on the same cluster?

## Scenario 3: Latency Spikes After Deploying A New Model

### Prompt

The new model is more accurate offline, but p99 latency in production doubled after deployment.

### What A Strong Answer Should Cover

- Compare model size, runtime, hardware assumptions, batching, and cold starts.
- Check whether the new model changed preprocessing, sequence length, or memory profile.
- Explain how you would decide between rollback and optimization.

### First Things To Inspect

- canary versus champion latency
- model load time
- batching configuration
- concurrency and autoscaling state
- CPU versus GPU utilization

### Metrics To Mention

- p95 and p99 latency
- queue time
- model initialization time
- request concurrency
- GPU memory utilization
- tokens per second or batch throughput for LLM workloads

### Likely Root Causes

- larger model weights
- ineffective batching
- cold starts
- CPU deployment of a model that needs GPU
- upstream feature lookup latency

### Strong Mitigation Ideas

- hold or roll back the canary
- reduce traffic to the new model
- move to better hardware placement
- optimize with quantization, batching, or compiled runtime formats such as ONNX or TensorRT

### Long-Term Prevention

- pre-release load test on production-like hardware
- rollout guardrails based on latency SLO
- regression benchmarks baked into the model promotion workflow

### Follow-Up Questions Interviewers Often Ask

- How would you decide between quantization and horizontal scaling?
- What trade-offs come with aggressive batching?
- What is your rollback trigger if accuracy is better but latency is worse?

## Scenario 4: Data Drift Alert Fires But Labels Arrive Days Later

### Prompt

A drift detector shows that production input distributions have changed, but you do not yet have enough labels to know whether the model is truly underperforming.

### What A Strong Answer Should Cover

- Drift is a warning signal, not automatic proof of failure.
- Use proxy metrics and business signals while waiting for labels.
- Decide whether the risk justifies rollback, closer observation, or retraining.

### First Things To Inspect

- affected features and severity of shift
- recent upstream data changes
- confidence score changes
- output distribution changes
- business KPI movement

### Metrics To Mention

- PSI or similar drift score
- feature null rate
- feature cardinality changes
- output distribution shift
- business KPI proxies

### Strong Mitigation Ideas

- tighten monitoring and halt further promotion
- trigger controlled retraining if thresholds justify it
- revert to a safer champion if business impact is already visible
- isolate whether the issue is drift, freshness, or schema breakage

### Long-Term Prevention

- explicit retraining and rollback thresholds
- drift monitors on high-value features
- richer offline eval datasets that reflect recent production changes

### Follow-Up Questions Interviewers Often Ask

- What is the difference between drift and bad data ingestion?
- How do you avoid retraining on bad or corrupted data?
- What proxy signals do you trust most when labels are delayed?

## Scenario 5: Training Cost Explodes Overnight

### Prompt

Your monthly training cost suddenly rises far above forecast after a new team starts using the platform.

### What A Strong Answer Should Cover

- Investigate usage patterns, retries, idle GPU time, experiment explosion, and dataset growth.
- Treat this as a platform governance issue, not just a billing issue.

### First Things To Inspect

- job count by team
- average job duration
- retry rate
- checkpoint usage
- GPU utilization

### Metrics To Mention

- cost by namespace, project, or team
- GPU utilization
- job success rate
- average training runtime
- spot versus on-demand usage mix
- data transfer and storage costs

### Likely Root Causes

- duplicated experiments
- low-utilization GPU jobs
- repeated failed runs
- missing checkpointing
- too many full retrains instead of incremental workflows

### Strong Mitigation Ideas

- enforce quotas and concurrency limits
- move eligible jobs to spot or preemptible capacity
- require checkpointing for long jobs
- build cost dashboards and ownership by team

### Long-Term Prevention

- budget alerts
- platform-level cost guardrails
- template pipelines with sane defaults
- regular training-cost reviews by team

### Follow-Up Questions Interviewers Often Ask

- How would you balance cost controls against experimentation speed?
- When would you deny a team's training job?
- How do you allocate shared cluster costs fairly?

## Scenario 6: Real-Time Feature Store Is Degraded

### Prompt

The model-serving layer is healthy, but the online feature store is slow or timing out, and inference latency is now breaching SLO.

### What A Strong Answer Should Cover

- Explain that model quality and latency can both degrade if feature delivery is bad.
- Check whether the service has fallback features, cache paths, or a safe degraded mode.
- Mention that not every model should keep serving if feature freshness is broken.

### First Things To Inspect

- feature-store latency
- timeout rates
- cache hit ratio
- freshness lag
- fallback path behavior

### Metrics To Mention

- feature lookup latency
- timeout count
- feature freshness lag
- cache hit ratio
- inference p99 latency
- downstream dependency saturation

### Strong Mitigation Ideas

- fail over to cached or default-safe features where appropriate
- degrade gracefully for non-critical recommendations
- shed traffic or reduce concurrency while the dependency recovers
- route traffic to the last known-safe model if feature freshness is mandatory

### Long-Term Prevention

- explicit freshness SLOs
- cache and fallback design
- dependency isolation tests
- circuit breakers between serving and feature store

### Follow-Up Questions Interviewers Often Ask

- When should the model refuse to serve instead of using fallback features?
- How do you test freshness failure modes before production?

## Scenario 7: A New Model Improves Offline Metrics But Hurts Business KPI

### Prompt

Offline evaluation improved, but after rollout the business KPI drops even though the model service is healthy.

### What A Strong Answer Should Cover

- Offline metrics are necessary but not sufficient.
- Validate whether the evaluation set represented production reality.
- Review rollout cohort, KPI definition, label delay, and data drift.

### First Things To Inspect

- rollout cohort and traffic split
- KPI measurement window
- evaluation dataset representativeness
- feature distribution differences between offline and production

### Strong Mitigation Ideas

- stop rollout or roll back to the champion
- re-evaluate the test set and promotion criteria
- add business KPI gates to future promotion workflows

### Long-Term Prevention

- online evaluation before full promotion
- champion-challenger workflow tied to business metrics
- production-like validation datasets

### Follow-Up Questions Interviewers Often Ask

- How long would you wait before deciding a KPI regression is real?
- What if offline metrics improved because of leakage or biased data?

## Scenario 8: Training Pipeline Fails After A Schema Change

### Prompt

A daily retraining pipeline has started failing after an upstream team added and renamed columns in the raw dataset.

### What A Strong Answer Should Cover

- Treat this as a data contract problem, not only a pipeline problem.
- Mention schema validation, backward compatibility, and ownership boundaries.
- Explain how you would protect the last good model from accidental promotion gaps.

### First Things To Inspect

- pipeline failure stage
- schema validation logs
- upstream release notes or changes
- feature transformation code

### Checks You Can Name

- data validation report comparison
- schema registry or contract diff
- training job logs
- last successful run metadata

### Likely Root Causes

- column rename or type change
- missing field
- changed nullability
- incompatible default values

### Strong Mitigation Ideas

- stop automatic promotion
- patch the transformation layer or add a compatibility adapter
- coordinate with the upstream owner on a stable schema contract
- keep the champion model serving until retraining is healthy again

### Long-Term Prevention

- schema contracts and contract tests
- compatibility window for upstream changes
- alerting on validation failure before the training phase starts

## Scenario 9: Online And Offline Features Do Not Match

### Prompt

Your offline evaluation looks strong, but live production predictions degrade. Investigation suggests the online feature path is not producing the same values used during training.

### What A Strong Answer Should Cover

- This is classic training-serving skew.
- Explain how shared feature definitions or a feature store reduce this risk.
- Separate model quality from feature pipeline quality.

### First Things To Inspect

- example entities with both offline and online features
- transformation code ownership
- feature timestamps and freshness
- serialization and type conversions

### Strong Mitigation Ideas

- revert to the previous feature view or previous model
- disable the broken online feature path
- add parity tests between offline and online feature computations

### Long-Term Prevention

- single source of truth for feature definitions
- parity tests on sampled entities
- stronger lineage between feature view and model version

## Scenario 10: Batch Inference Is Missing SLA Windows

### Prompt

A nightly batch scoring job used by a downstream business team is missing its delivery window and the reports are now late every morning.

### What A Strong Answer Should Cover

- Treat batch inference like a production SLA-backed workflow.
- Investigate data arrival, queue depth, cluster capacity, job parallelism, and retry behavior.

### First Things To Inspect

- upstream data arrival time
- job start delay
- executor or worker capacity
- failed partitions
- storage throughput

### Metrics To Mention

- pipeline duration
- queue time before start
- task retry rate
- failed partition count
- data volume growth

### Strong Mitigation Ideas

- scale batch workers or parallelism carefully
- separate batch and online resource pools
- optimize data locality and partitioning
- communicate downstream ETA while stabilizing

### Long-Term Prevention

- explicit batch SLOs
- capacity planning based on dataset growth
- dedicated windows or pools for critical batch jobs

## Scenario 11: Model Registry Promotion Went Wrong

### Prompt

A model version was marked as production in the registry, but the serving layer still appears to be using an older artifact in one region and a newer artifact in another.

### What A Strong Answer Should Cover

- Distinguish registry state from deployment state.
- Explain why promotion and rollout need explicit synchronization and auditability.
- Mention digest pinning or immutable artifact references.

### First Things To Inspect

- registry stage
- deployment config in each region
- artifact URI or digest
- rollout history and automation logs

### Strong Mitigation Ideas

- freeze further promotions
- align all regions to the last known-good immutable version
- fix the promotion-to-deployment handoff

### Long-Term Prevention

- immutable artifact references
- deployment confirmation back into the registry
- regional rollout status checks

## Scenario 12: LLM Retrieval Pipeline Starts Hallucinating More Often

### Prompt

A retrieval-augmented generation workflow suddenly starts giving lower-quality answers even though the base model and endpoint health look normal.

### What A Strong Answer Should Cover

- Separate base-model health from retrieval quality.
- Check embedding version, chunking logic, index freshness, ranking changes, and prompt template changes.
- Mention that LLMOps failures often happen in the retrieval pipeline, not the model host.

### First Things To Inspect

- retrieval hit rate
- index freshness
- prompt template version
- embedding model version
- response quality or evaluation score

### Strong Mitigation Ideas

- roll back the embedding or retrieval change
- fall back to a previous prompt or index
- restrict risky traffic while evaluation stabilizes

### Long-Term Prevention

- retrieval evaluation sets
- versioning for prompts and embeddings
- index freshness monitoring
- business-safe fallback flows

## Practical Mini-Frameworks You Can Use In Answers

### If The Endpoint Is Healthy But The Answers Are Wrong

Say:

> I would treat this as a correctness incident. I would validate schema, feature parity, model lineage, and recent data or feature changes before touching infrastructure.

### If The Platform Is Slow Or Unstable

Say:

> I would confirm whether latency is from model execution, feature retrieval, model loading, or hardware saturation, then decide whether rollback, scaling, batching, or degraded mode is the safest mitigation.

### If Costs Blow Up

Say:

> I would investigate experiment explosion, low GPU utilization, retries, checkpointing, and ownership by team before recommending cost controls.

## What Makes A Candidate Sound Senior

- You treat model correctness and platform health as separate but connected layers.
- You mention reproducibility and lineage naturally.
- You discuss rollout safety, rollback, and governance for models.
- You think about latency, accuracy, and cost together.
- You describe both the immediate mitigation and the prevention plan.

***

## Scenario 1: Model Training Data Drift
**Symptom:** The model's accuracy in production has dropped by 10% compared to validation.
**Diagnosis:** The real-world data distribution has changed compared to the training set.
**Fix:** Implement **Monitoring for Data Drift** (e.g., using EvidentlyAI). Retrain the model on the latest data.

## Scenario 2: GPU Resource Starvation
**Symptom:** ML training jobs are stuck in `Pending` for hours.
**Diagnosis:** The Kubernetes cluster has run out of GPU-enabled nodes.
**Fix:** Use the **Cluster Autoscaler** with GPU node groups. Implement "Multi-Instance GPU" (MIG) on A100s to slice one physical GPU for multiple small jobs.
