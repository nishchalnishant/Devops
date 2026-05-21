# MLOps (Machine Learning Operations)

```
MLOps (Machine Learning Operations)
├── Core Concept: Three Artifacts
│   ├── Code: training scripts, feature engineering, model architecture
│   ├── Data: training datasets, feature values, labels
│   └── Model: trained weights + preprocessing transforms + metadata
├── MLOps Maturity Levels
│   ├── L0 (Manual): laptop → email model to engineer → deploy manually
│   ├── L1 (Pipeline Automation): Kubeflow/SageMaker pipeline; no CT
│   └── L2 (CI/CD/CT): automated retrain on drift/schedule + auto-promotion
├── Core Components
│   ├── Feature Store: offline (S3/BigQuery) + online (Redis/DynamoDB)
│   ├── Model Registry: versioned catalog (MLflow); None→Staging→Production→Archived
│   ├── Experiment Tracker: logs params, metrics, artifacts per run (MLflow, W&B)
│   └── Serving Layer: KServe, Triton, TF Serving, vLLM (LLMs)
├── Four Pipelines
│   ├── CI: test code, validate features, lint pipelines
│   ├── CT (Continuous Training): trigger → train → evaluate → register
│   ├── CD: deploy new model version to serving infra
│   └── CM (Continuous Monitoring): drift detection, label monitoring, alerts
├── Data Drift & Model Degradation
│   ├── Data drift (covariate shift): P(X) changes
│   ├── Concept drift: P(Y|X) changes — world changes, model doesn't
│   ├── Detection: PSI, KS test, Jensen-Shannon, Chi-squared
│   └── CT trigger: drift threshold, schedule, data volume, business KPI drop
├── Deployment Strategies
│   ├── Shadow: challenger runs in parallel; predictions not returned to users
│   ├── Canary: small % of live traffic to challenger
│   ├── A/B testing: statistical significance gate before full rollout
│   └── Blue/Green: full traffic swap with instant rollback capability
└── LLMOps Extensions
    ├── Prompt versioning and registry
    ├── RAG pipeline: chunk → embed → vector DB → retrieve → rerank → LLM
    ├── RAGAS metrics: faithfulness, answer_relevancy, context_precision
    ├── vLLM: PagedAttention + continuous batching for high-throughput serving
    └── Cost per token as primary LLM serving metric
```

## First Principles

- ML models are code + data + config — all three must be versioned and reproducible, or you cannot debug degraded models.
- Models degrade silently over time (data drift, concept drift) — monitoring model behavior is as critical as monitoring infrastructure.
- Feature computation is expensive — cache computed features in a feature store to avoid duplication between training and serving, and to prevent training-serving skew.
- Serving needs latency SLOs: batch vs real-time is not a technical choice, it is a latency trade-off — real-time serving requires online feature stores and fast model runtimes.
- Continuous Training is not Continuous Deployment: retraining a model requires data validation, performance evaluation, and promotion gates — not just CI passing.
- LLMOps adds unique challenges: prompt versioning, KV cache management, cost per token, and RAG pipeline quality — none of which exist in standard MLOps.

MLOps is the application of DevOps principles to Machine Learning. It bridge the gap between Data Science (building models) and Engineering (running models in production), focusing on automation, scalability, and reliability of ML systems.

#### 1. The ML Lifecycle vs. Software Lifecycle
*   **Standard DevOps:** Code + Data = Software.
*   **MLOps:** Code + Data + **Model** = Software.
*   **The Challenge:** In standard software, the code is static. In ML, the data changes over time ("Data Drift"), which causes the model's accuracy to decay.

#### 2. The Three Levels of MLOps
1.  **Level 0 (Manual):** Data Scientists build models on their laptops and send them to Engineers to deploy. No automation.
2.  **Level 1 (Pipeline Automation):** The entire process from data cleaning to model training is automated in a pipeline (e.g., Kubeflow, SageMaker).
3.  **Level 2 (CI/CD/CT):** Continuous Training. The system automatically detects when a model is failing and triggers a new training run with fresh data.

#### 3. Core Components
*   **Feature Store:** A central repository for pre-calculated "features" (data inputs) so they can be reused across different models. (e.g., Feast).
*   **Model Registry:** A version-controlled "store" for trained models. (e.g., MLflow).
*   **Serving Layer:** The infrastructure that hosts the model as an API (e.g., Seldon Core, TF Serving).

#### 4. Data Drift & Model Monitoring
Unlike a web server that either "works" or "is down," an ML model can be "up" but giving "wrong" answers.
*   **Concept Drift:** The relationship between input and output changes (e.g., customer behavior changes during a pandemic).
*   **Data Drift:** The distribution of input data changes (e.g., a new sensor starts giving slightly different readings).

***

#### 🔹 1. Improved Notes: Advanced MLOps
*   **GPU Orchestration:** Managing expensive GPU resources in Kubernetes. Using "Taints" and "Affinity" to ensure ML workloads only run on machines with the right hardware.
*   **Inference Strategies:**
    *   **Real-time:** Model is an API (Low latency).
    *   **Batch:** Model runs on a massive dataset once a day (High throughput).
    *   **Streaming:** Model processes data in real-time as it flows through Kafka.

#### 🔹 2. Interview View (Q&A)
*   **Q:** What is a "Feature Store"?
*   **A:** It's a central database for data scientists to share and discover features. It ensures that the data used during **Training** is exactly the same as the data used during **Inference** (preventing "Training-Serving Skew").
*   **Q:** Explain "Canary Deployment" for ML.
*   **A:** You deploy the new model to 5% of users. You compare its predictions to the old model. If the accuracy and business metrics look good, you roll it out to 100%.

***

#### 🔹 3. Architecture & Design: The MLOps Pipeline
1.  **Data Ingestion:** Pulling data from Data Warehouses (Snowflake, BigQuery).
2.  **Validation:** Checking data for missing values or outliers.
3.  **Training:** Running the ML algorithm on a cluster.
4.  **Evaluation:** Comparing the new model's accuracy to the "Champion" model.
5.  **Deployment:** Packaging the model as a Docker container.

***

#### 🔹 4. Commands & Configs (MLflow Example)
```python
# Log a model with MLflow
import mlflow

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.sklearn.log_model(model, "my_model")
```

***

#### 🔹 5. Troubleshooting & Debugging
*   **Scenario:** A model's accuracy dropped by 10% overnight.
*   **Fix:** Check for **Data Drift**. Compare the distribution of the "live" data to the "training" data. If a feature that was usually `0` or `1` is now `0.5`, the model will be confused.

***

#### 🔹 6. Production Best Practices
*   **Versioning Everything:** Version the code (Git), Version the Data (DVC), and Version the Model (MLflow).
*   **Reproducibility:** If a model gives a weird prediction in Prod, you must be able to recreate the exact environment and data used to train it to figure out why.
*   **Testing:** Unit tests for code, and **Statistical Tests** for data quality.

***

#### 🔹 Cheat Sheet / Quick Revision
| **Concept** | **Purpose** | **DevOps Context** |
| :--- | :--- | :--- |
| `DVC` | Data Version Control | Managing large datasets without bloating Git. |
| `Inference` | Running the model | Making a prediction on a new piece of data. |
| `Hyperparameter` | Model configuration | Tuning the "knobs" of an algorithm. |
| `A/B Testing` | Comparing models | Showing Model A to 50% and Model B to 50% of users. |

***

This is Section 17: MLOps. For a senior role, you should focus on **LLMOps (Generative AI operations)**, **Multi-model serving**, and **GPU cost optimization**.

***

## System Design Perspective

**ML Platform Architecture (Mid-Size Organization)**
- Data layer: Delta Lake or Iceberg on S3/GCS for versioned training data; Great Expectations for data validation at ingestion.
- Feature layer: Feast or Tecton for feature store; offline store backed by S3/BigQuery; online store backed by Redis or DynamoDB; materialization job runs on a schedule.
- Training layer: Kubeflow Pipelines or SageMaker Pipelines for orchestration; MLflow for experiment tracking and model registry; GPU node pool (Karpenter) for training jobs.
- Serving layer: KServe for standard models; vLLM for LLMs; Triton for GPU-accelerated batch inference.
- Monitoring layer: Evidently AI for drift detection; Prometheus for serving latency and throughput; custom dashboards for model quality metrics.

**LLM Serving at Scale**
- vLLM with PagedAttention: non-contiguous KV cache blocks enable high GPU utilization and concurrent request handling.
- Model routing: small models for simple queries (cost optimization), large models for complex queries — route based on query complexity classifier.
- RAG pipeline: document ingestion → chunking → embedding → vector DB (Pinecone, Weaviate, Qdrant) → ANN retrieval → cross-encoder reranking → LLM prompt assembly.
- Semantic caching: cache LLM responses for semantically similar queries to reduce cost and latency.

**Distributed Training Architecture**
- For models > single GPU: PyTorch FSDP or DeepSpeed ZeRO Stage 3 for parameter sharding across GPUs.
- Checkpointing to S3 every N steps — enables resumption on Spot instance preemption.
- InfiniBand networking for GPU-to-GPU communication in large clusters (essential for Tensor Parallelism).