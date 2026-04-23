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

***

## ML Pipeline Tools (EASY)

**36. What is Kubeflow and what problem does it solve for ML teams?**

Kubeflow is an open-source machine learning platform built on Kubernetes. It provides tools for the full ML lifecycle: Kubeflow Pipelines for orchestrating multi-step training workflows, Katib for hyperparameter tuning, KServe for model serving, and Jupyter Notebooks for interactive development. The core problem it solves is reproducibility and operationalization — moving experiments from notebooks to production pipelines running on scalable infrastructure.

**37. What is Apache Airflow and how is it used in ML workflows?**

Apache Airflow is a workflow orchestration platform that schedules and monitors DAGs (Directed Acyclic Graphs) of tasks. In ML, Airflow orchestrates data pipelines: extracting data from sources, running preprocessing jobs, triggering training runs, evaluating results, and pushing models to registries. Unlike Kubeflow Pipelines (which is ML-specific), Airflow is general-purpose and often used when the ML pipeline must integrate tightly with data engineering workflows in the same DAG.

**38. What is the difference between a batch prediction and an online prediction?**

Batch prediction runs the model on a large dataset all at once on a schedule — results are precomputed and stored (e.g., generating daily product recommendations for all users overnight). Online prediction (real-time inference) runs the model in response to individual requests with low latency requirements (e.g., fraud detection on a transaction as it happens). Batch is cheaper and can use larger models; online requires careful latency optimization and high availability.

**39. What is MLflow and what are its core components?**

MLflow is an open-source ML experiment tracking and model management platform with four components:
- **Tracking:** Log parameters, metrics, and artifacts from training runs. Compare runs via a UI.
- **Projects:** Package ML code in a reproducible format with an `MLproject` file defining dependencies and entry points.
- **Models:** A standard format for saving models with flavor-specific loaders (PyTorch, sklearn, etc.).
- **Registry:** A centralized model store with versioning, staging transitions (Staging → Production → Archived), and approval workflows.

**40. What is a training-serving skew and why is it a problem?**

Training-serving skew occurs when the data or feature transformations applied during training differ from those applied at inference time. Example: during training, age is calculated as `(now - birth_date).days / 365`, but at serving time, the same calculation uses a different time zone — resulting in slightly different feature values the model was not trained on. This causes silent model degradation. Prevention: use the same feature computation code (often via a Feature Store) in both training and serving paths.

**41. What is a model card and why is it important?**

A model card is a standardized document describing a model's intended use, performance characteristics, evaluation results, training data, known limitations, and ethical considerations. It is important for: transparency (stakeholders understand what the model can and cannot do), compliance (regulated industries require documentation of model behavior), and debugging (teams can quickly determine if a production issue is caused by a model operating outside its documented use case).

**42. What is data versioning and why is `git` not sufficient for ML datasets?**

Data versioning tracks changes to datasets over time so that a training run can be reproduced by pointing to the exact data version used. Git is not sufficient because ML datasets are often gigabytes to terabytes in size — Git stores full file copies per commit and is not designed for large binary files. DVC (Data Version Control) solves this by storing data in external storage (S3, GCS, Azure Blob) and only committing small `.dvc` pointer files to Git, maintaining the same workflow semantics.

**43. What is a hyperparameter and how does hyperparameter tuning work?**

A hyperparameter is a configuration value set before training that controls the learning algorithm's behavior — learning rate, number of tree depth, dropout rate, batch size. Unlike model parameters (learned from data), hyperparameters are not updated during training. Hyperparameter tuning searches for the combination that produces the best validation metric. Methods: grid search (exhaustive), random search (sample randomly — often as effective as grid search with less compute), Bayesian optimization (builds a probabilistic model of the objective function to select next trials intelligently).

**44. What is the difference between a validation set and a test set?**

The validation set is used during model development to tune hyperparameters and compare model variants — it influences training decisions, so you must not use it for final evaluation. The test set is held out completely during all model development and used only once at the end to estimate real-world performance. Using the test set during development causes data leakage — the final performance metrics will be optimistically biased because the test set influenced model choices.

**45. What does model explainability mean and why does it matter in production?**

Model explainability refers to the ability to understand and communicate why a model made a specific prediction. It matters in production for: regulatory compliance (GDPR's right to explanation, financial models requiring audit trails), debugging unexpected predictions, identifying bias in model behavior, and building trust with users and stakeholders. Tools: SHAP (SHapley Additive exPlanations — assigns feature importance scores per prediction), LIME (local approximation of model behavior), and model-specific methods (attention weights in transformers).

**46. What is A/B testing in the context of ML model deployment?**

A/B testing splits incoming traffic between two model versions (A = current, B = new) and collects real-world performance data. Unlike offline evaluation on a held-out test set, A/B testing captures actual user behavior and business metrics (conversion rate, click-through rate). Proper A/B testing requires: random traffic splitting, sufficient statistical power (sample size calculation before the test), defined primary and guardrail metrics, a fixed experiment duration, and a statistical test (t-test, Mann-Whitney) to assess significance before declaring a winner.

**47. What is feature engineering and give three common transformations?**

Feature engineering is the process of transforming raw data into input features that improve model performance. Common transformations:
1. **Normalization/Standardization:** Scale numerical features to a common range (min-max normalization: `[0,1]`; z-score standardization: mean=0, std=1) so models with gradient descent are not dominated by large-magnitude features.
2. **One-hot encoding:** Convert categorical variables (color: red/green/blue) into binary indicator columns (is_red, is_green, is_blue).
3. **Log transformation:** Apply `log(x+1)` to right-skewed distributions (e.g., transaction amounts) to reduce the influence of extreme outliers and make the distribution more Gaussian.

**48. What is the difference between supervised, unsupervised, and reinforcement learning?**

- **Supervised learning:** Model learns from labeled training data — examples with known correct outputs. Used for classification (spam/not-spam) and regression (price prediction).
- **Unsupervised learning:** Model finds patterns in data without labels. Used for clustering (customer segmentation), dimensionality reduction (PCA), and anomaly detection.
- **Reinforcement learning:** An agent learns by taking actions in an environment and receiving rewards or penalties. Used for game playing, robotics, and recommendation system optimization. RL is rare in typical MLOps workflows but increasingly used in RLHF for LLMs.

**49. What is a confusion matrix and what metrics can you derive from it?**

A confusion matrix for binary classification has four cells: TP (true positive), TN (true negative), FP (false positive), FN (false negative). Derived metrics:
- **Precision:** `TP / (TP + FP)` — of all predictions of class A, how many were correct? High precision = few false alarms.
- **Recall (Sensitivity):** `TP / (TP + FN)` — of all actual class A instances, how many did the model find? High recall = few misses.
- **F1 Score:** `2 × (Precision × Recall) / (Precision + Recall)` — harmonic mean, useful when both precision and recall matter.
- **AUC-ROC:** Area under the ROC curve — measures model discrimination ability across all classification thresholds.

**50. What is a Jupyter Notebook and what are its limitations in production ML workflows?**

Jupyter Notebooks are interactive web-based environments combining code cells, markdown text, and visualizations. They are excellent for exploration and communication. Limitations in production: non-linear execution (cells can be run out of order, hidden state persists), no version control of outputs (diffs show JSON noise), no standard interface for parameterization or scheduling, and notebooks cannot be called from orchestration systems directly. Solutions: `nbconvert` to convert notebooks to scripts, Papermill to parameterize and execute notebooks programmatically, or migrate experiment code to structured Python modules before productionization.

***

## Model Deployment Basics (EASY - Extended)

**51. What is a REST API in the context of model serving?**

A REST API exposes the model as an HTTP endpoint. Clients send a POST request with input features (usually JSON), and the server runs inference and returns predictions in the response. Example: `POST /predict` with body `{"features": [1.2, 3.4, 5.6]}` returns `{"prediction": 0.87, "class": "fraud"}`. REST APIs are language-agnostic and easy to integrate with any application. Common frameworks: FastAPI, Flask (Python), TorchServe, BentoML, KServe.

**52. What is model cold start and how do you mitigate it?**

Cold start occurs when a model serving instance is started fresh (after scale-to-zero or pod restart) and the first request experiences high latency because the model weights must be loaded from storage into memory. Mitigation: keep-alive (prevent scale-to-zero for latency-sensitive services), pre-loading weights at pod startup with a readinessProbe that passes only after weights are loaded, using shared memory across model replicas (reduce per-pod load time), or using a tiered serving architecture where a lightweight model handles requests while the heavy model loads.

**53. What is the difference between model accuracy and model reliability in production?**

Model accuracy measures prediction quality against labeled ground truth (precision, recall, F1). Model reliability measures the infrastructure health of the serving system — latency, throughput, availability (uptime), and error rate. A system can have 99% model accuracy but 70% reliability (frequent timeouts, pod crashes). MLOps teams must monitor both: reliability via standard SRE metrics (p99 latency, error rate) and model quality via prediction distribution, data drift, and outcome metrics.

**54. What is a blue-green deployment for ML models?**

A blue-green model deployment maintains two identical serving environments: blue (current production model) and green (new model version). After validating the green environment with offline tests and optionally shadow traffic, you switch the load balancer to route 100% of traffic to green. If green has issues, you immediately switch back to blue. This provides instant rollback without requiring redeployment. Limitation: it requires double the serving infrastructure during the transition period.

**55. What is model staleness and how do you detect it?**

Model staleness occurs when a model trained on historical data no longer reflects current patterns because the underlying data distribution has changed. Detection methods:
- **Data drift monitoring:** Compare statistical properties (mean, variance, distribution histograms) of incoming request features against the training data distribution. Tools: Evidently AI, WhyLabs, SeldonCore.
- **Outcome drift:** If labels are available with delay, compare model predictions against actual outcomes over time — a widening gap signals staleness.
- **Business metric monitoring:** Revenue per recommendation declining, click-through rate dropping unexpectedly on model-driven features.
