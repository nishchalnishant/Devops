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

***

