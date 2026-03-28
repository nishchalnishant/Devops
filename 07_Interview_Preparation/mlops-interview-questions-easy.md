# MLOps Interview Questions (Easy)

These questions cover the fundamentals that usually appear in junior-to-mid MLOps, ML platform, or ML infrastructure interviews.

## Foundations

**1. What is MLOps?**

MLOps is the discipline of building, deploying, monitoring, and governing machine learning systems in production. It extends DevOps by treating data, features, and models as first-class artifacts.

**2. How is MLOps different from traditional DevOps?**

Traditional DevOps mainly manages code and infrastructure. MLOps must also manage training data, model artifacts, experiment metadata, and model quality after deployment.

**3. What is the difference between training and inference?**

Training is the process of fitting a model on historical data. Inference is the process of using the trained model to generate predictions on new data.

**4. What is model serving?**

Model serving is the process of exposing a trained model so applications can call it for predictions, usually through an API, batch job, or stream consumer.

**5. What is a model artifact?**

A model artifact is the saved output of training, such as a serialized model file, along with metadata needed to load and run it.

**6. Why is reproducibility important in MLOps?**

Because you must be able to trace a production model back to the exact code, data, parameters, and environment that created it. Without that, debugging and compliance become difficult.

**7. What is experiment tracking?**

Experiment tracking records parameters, metrics, code version, and artifacts for each training run so teams can compare results and reproduce the best model.

**8. What is a model registry?**

A model registry stores versioned models and their metadata, and often supports lifecycle stages such as staging, approved, and production.

## Data And Features

**9. Why is data versioning needed in MLOps?**

Because changing the dataset can change the model even when the code stays the same. Versioning helps reproduce training runs and compare models fairly.

**10. Why not store large datasets directly in Git?**

Git is not designed for large binary data and becomes slow and bloated. Tools like DVC store metadata in Git and the actual data in object storage.

**11. What is DVC?**

DVC, or Data Version Control, is a tool that tracks datasets and ML artifacts while integrating with Git for metadata and remote object storage for data.

**12. What is a feature in machine learning?**

A feature is an input variable used by a model to make a prediction, such as age, transaction amount, or device type.

**13. What is a feature store?**

A feature store is a system that manages reusable features for both training and inference, helping keep transformations consistent across environments.

**14. What is training-serving skew?**

Training-serving skew happens when the feature processing used in production differs from what was used during training, causing incorrect or degraded predictions.

**15. What is label leakage?**

Label leakage happens when information that would not truly be available at prediction time leaks into training data, making offline evaluation look better than real production behavior.

## Deployment And Delivery

**16. What is CI, CT, and CD in MLOps?**

CI validates code and tests. CT, or continuous training, retrains models when needed. CD deploys model-serving changes safely into production.

**17. What is batch inference?**

Batch inference runs predictions over large datasets in bulk, often on a schedule. It is common for reporting, recommendations, or nightly scoring jobs.

**18. What is online inference?**

Online inference returns predictions in real time for a live request, usually with strict latency requirements.

**19. What is async inference?**

Async inference accepts requests quickly and processes them later, which is useful when predictions take too long for a synchronous API response.

**20. What is shadow deployment?**

Shadow deployment sends production traffic to a new model without returning its predictions to users. It lets you compare behavior safely before exposure.

**21. What is canary deployment for models?**

Canary deployment sends a small percentage of production traffic to a new model and increases traffic gradually if metrics remain healthy.

**22. What is A/B testing in MLOps?**

A/B testing exposes different user groups to different models so you can compare business outcomes such as conversion rate or click-through rate.

**23. What is champion-challenger?**

It is a setup where the current production model is the champion and a candidate model is the challenger. The challenger is evaluated before full promotion.

## Monitoring And Quality

**24. What is data drift?**

Data drift means the input data distribution in production is changing compared with the training baseline.

**25. What is concept drift or model drift?**

Concept drift means the relationship between inputs and outputs changes over time, so a model that used to be accurate becomes less useful.

**26. Why is monitoring model accuracy harder than monitoring uptime?**

Because labels often arrive late or not at all, so you may not know true accuracy in real time. You often need proxy metrics and delayed evaluation.

**27. What kinds of metrics do you monitor for a model-serving system?**

Latency, throughput, error rate, resource usage, feature null rates, confidence distribution, drift signals, and business KPI impact.

**28. Why can a model endpoint be healthy but still be wrong?**

Because the infrastructure may be serving requests correctly while the model, features, or input schema are incorrect.

## Infrastructure

**29. Why are GPUs used in MLOps?**

GPUs accelerate parallel numerical operations and are often needed for deep learning training and high-performance inference.

**30. Why are GPUs handled differently from CPUs in Kubernetes?**

They are limited, expensive, and often require device plugins, node isolation, and special scheduling controls such as taints and tolerations.

**31. What is cold start in model serving?**

Cold start is the latency hit when a model or runtime is loaded for the first time, especially when large model weights must be loaded into memory or GPU.

## Governance

**32. Why is lineage important in MLOps?**

Lineage tells you which code, data, features, and model version produced a given prediction service. It is essential for debugging, audits, and rollback.

**33. Why does MLOps care about PII and compliance?**

Because models may be trained on sensitive data, and the platform must enforce access control, auditability, and safe handling of regulated information.

**34. What is rollback in MLOps?**

Rollback means restoring a previous trusted model, feature pipeline, or serving configuration when the new model degrades production behavior.

**35. What is LLMOps?**

LLMOps is a specialization of MLOps focused on large language models, prompt versioning, evaluation, retrieval pipelines, inference cost, and safety controls.
