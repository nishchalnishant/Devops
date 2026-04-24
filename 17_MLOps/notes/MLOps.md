# 10. MLOps

### 10. MLOps

This section focuses on the tools and workflows needed to move machine learning from a data scientist's notebook into a scalable production environment.

## Companion Interview Resources

Use this file together with:

- `../07_Interview_Preparation/mlops-interview-playbook.md`
- `../07_Interview_Preparation/mlops-interview-questions-easy.md`
- `../07_Interview_Preparation/mlops-interview-questions-medium.md`
- `../07_Interview_Preparation/mlops-interview-questions-hard.md`
- `../07_Interview_Preparation/mlops-scenario-based-interview-drills.md`

## Practical Interview Focus

For scenario-heavy interview preparation, spend extra time on:

- wrong predictions with healthy endpoints
- training-serving skew
- data drift with delayed labels
- GPU scheduling and CUDA mismatch
- registry promotion mistakes
- feature-store degradation
- batch inference SLA misses
- cost spikes from uncontrolled training
- LLM retrieval quality regressions

#### The Intersection of Three Worlds

* Machine Learning: Designing the algorithms and training models.
* DevOps: Automating the deployment and maintaining infrastructure.
* Data Engineering: Managing the massive data pipelines that feed the models.

***

#### A. KubeFlow (The Kubernetes-Native Heavyweight)

KubeFlow is a comprehensive toolkit built specifically for running ML workloads on Kubernetes. It is designed for large-scale, enterprise-grade production environments.

* Kubeflow Pipelines: Used to build and deploy multi-step ML workflows as containerized units. It provides a visual dashboard to track every step from data cleaning to model training.
* Katib: An automated tool for Hyperparameter Tuning. It runs hundreds of experiments simultaneously to find the best settings for your model, saving weeks of manual work.
* KFServing / KServe: A specialized tool for "Serving" (deploying) your models so they can handle live traffic and auto-scale based on demand.
* Notebooks: Provides hosted Jupyter notebooks directly in the cluster, allowing data scientists to build models in the same environment where they will eventually be deployed.

***

#### B. MLFlow (The Agile Experiment Tracker)

While KubeFlow handles the infrastructure, MLFlow focuses on the Lifecycle. It is lightweight, framework-agnostic (works with any ML library), and can run anywhere—from your local laptop to the cloud.

* MLFlow Tracking: A centralized "Logbook." It records every experiment's parameters, code versions, and results (metrics like accuracy) so you can compare different model versions easily.
* MLFlow Projects: A standard format for packaging your ML code. It ensures that if a model runs on your machine, it will run exactly the same way on a production server.
* MLFlow Models: A way to package models for diverse deployment tools (e.g., deploying to AWS Sagemaker, Azure ML, or a simple Docker container).
* Model Registry: A centralized store to manage the full lifecycle of an ML model, including versioning, stage transitions (Staging to Production), and annotations.

***

#### Key Differences: DevOps vs. MLOps

| **Feature**     | **Traditional DevOps**       | **MLOps**                                     |
| --------------- | ---------------------------- | --------------------------------------------- |
| Main Artifact   | Code & Binaries              | Code + Data + Model                           |
| Version Control | Tracks code changes (Git)    | Tracks code, data versions, and model weights |
| CI/CD Goal      | Automated testing/deployment | Automated retraining and model validation     |
| Monitoring      | System health (CPU, RAM)     | Performance drift (Model accuracy decay)      |

> Pro Tip: In MLOps, a "successful" deployment isn't enough. You must monitor for Data Drift—when the real-world data starts to look different from the data the model was trained on, causing the model's performance to drop over time.

***

#### The MLOps Lifecycle

1. Design: Identifying the business problem and data availability.
2. Experimentation: Data scientists using MLFlow to track model training runs.
3. Operation: DevOps engineers using KubeFlow to automate the pipeline and deploy the model at scale.
4. Monitoring: Tracking the model's accuracy in production and triggering Automated Retraining if performance dips.



This is Section 10: MLOps (Machine Learning Operations). For a mid-to-senior SRE or DevOps Engineer, MLOps is the final frontier. It bridges the gap between traditional software engineering and the non-deterministic world of Machine Learning.

In a senior role, you aren't expected to build the models, but you are expected to build the high-performance, GPU-accelerated, scalable infrastructure that allows models to reach production safely and reliably.

***

#### 🔹 1. Improved Notes: DevOps for the Data Age

**The Core Difference: Code vs. Data**

* Traditional DevOps: Focuses on Code + Configuration. If code is the same, the output is (mostly) predictable.
* MLOps: Focuses on Code + Data + Model. Even if code is identical, changing the training data results in a completely different binary (the Model).
* Continuous Training (CT): This is unique to MLOps. It’s a pipeline that automatically triggers a model retraining when performance drops or new data arrives.

**The MLOps Components**

1. Feature Store: A centralized repository (e.g., Feast, Hopsworks) that stores processed data "features" so they can be reused across different models, ensuring consistency between training and inference.
2. Model Registry: A version-control system for models (e.g., MLflow, WandB). It tracks who trained the model, with what data, and what the accuracy metrics were.
3. Inference Engines: Specialized servers like NVIDIA Triton, Seldon Core, or KServe that host models and handle high-concurrency requests.

***

#### 🔹 2. Interview View (Q\&A)

Q1: What is "Data Drift" and "Model Drift," and how do you monitor them?

* Answer: \* Data Drift: The input data in production has changed compared to the training data (e.g., a new user demographic).
  * Model Drift (Concept Drift): The relationship between input and output changes (e.g., consumer behavior changes after a global event).
* SRE Approach: We monitor this by comparing the statistical distribution of live inference data against the training baseline using tools like Evidently AI or Prometheus histograms.

Q2: How do you handle GPU resource management in a Kubernetes cluster?

* Answer: GPUs are expensive and cannot be easily "sliced" like CPUs (unless using NVIDIA MIG). We use NVIDIA Device Plugins for K8s to allow pods to request `nvidia.com/gpu`.
* Senior Twist: Mention Taints and Tolerations to ensure only ML workloads land on expensive GPU nodes, and Cluster Autoscaler to shut down those nodes when no training jobs are running.

Q3: Explain "Shadow Deployment" in the context of MLOps.

* Answer: In a Shadow Deployment, the new model receives 100% of the live production traffic, but its predictions are _not_ sent to the user. Instead, we compare its results against the existing model to see how it performs in the real world without any risk to the business.

***

#### 🔹 3. Architecture & Design: High-Performance Inference

Serving Architectures:

* Online Inference: Real-time (e.g., Credit Card Fraud detection). Requires <100ms latency. Usually deployed as a REST/gRPC service on Kubernetes.
* Batch Inference: Large scale (e.g., generating weekly recommendations). Usually run as Spark or Kubernetes Jobs overnight.

SRE Trade-off: Latency vs. Cost

* GPU Inference: Fastest, but extremely expensive.
* CPU Inference (with OpenVINO/ONNX): Slower, but significantly cheaper and easier to scale.
* Design Choice: Use GPUs for large LLMs or heavy Computer Vision; use optimized CPU inference for simpler tabular data models.

***

#### 🔹 4. Commands & Configs (The MLOps Stack)

**KServe InferenceService YAML (The Industry Standard)**

This YAML defines a model that can automatically scale to zero if not in use.

YAML

```
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "s3://my-model-bucket/iris-v2/"
      resources:
        limits:
          cpu: "1"
          memory: "2Gi"
          nvidia.com/gpu: "1" # Requesting GPU
```

**DVC (Data Version Control) CLI**

Because you can't push 10GB of data to Git, you use DVC to track the metadata in Git while the data lives in S3.

Bash

```
# Track a data folder
dvc add data/training_images/

# Push data to S3, but metadata to Git
dvc push
git add data/training_images.dvc .gitignore
git commit -m "Updated training dataset for v2 model"
```

***

#### 🔹 5. Troubleshooting & Debugging

Scenario: Model Inference is returning "200 OK" but the predictions are "wrong" or "garbage."

1. Check Input Schema: Did the frontend change the format of the JSON being sent? (e.g., sending strings instead of floats).
2. Check Feature Parity: Is the code that processes features in production identical to the code used during training? (This is why Feature Stores are vital).
3. Check Model Version: Did an automated CI/CD pipeline push a "half-trained" model? (Check the Model Registry).

Scenario: GPU Pod is stuck in `Pending`.

1. Check Capacity: Run `kubectl describe node`. Are all GPU slots taken?
2. Check Drivers: Are the NVIDIA drivers on the node compatible with the CUDA version in the container?
3. Check Quotas: Is the namespace hitting a ResourceQuota limit for `requests.nvidia.com/gpu`?

Scenario: Drift alerts fire, but labels will not arrive until days later.

1. Check whether the alert is data drift, concept drift, or just an upstream schema/freshness problem.
2. Review proxy metrics such as confidence shifts, output distribution, feature freshness, and business KPI movement.
3. Decide whether to hold rollout, retrain, or roll back to a safer champion model.

Scenario: Batch inference is healthy from an infrastructure perspective but repeatedly misses the business delivery window.

1. Check queue time, dataset growth, retries, partition skew, and storage throughput.
2. Verify whether upstream data arrived late or the cluster was starved by higher-priority workloads.
3. Treat it as an SLA issue, not merely a long-running job.

***

#### 🔹 6. Production Best Practices

* Model Checkpointing: During long training runs (which can take days), always save "checkpoints" to S3. If the Spot Instance is reclaimed, the job can resume from the last checkpoint rather than starting over.
* A/B Testing: Never replace a model 100%. Use an Ingress Controller or Service Mesh (Istio) to split traffic (90% old, 10% new) and compare business KPIs (e.g., Click-through rate).
* Reproducibility: Every model in production must be traceable back to the exact Git commit of the code and the exact DVC version of the data.
* Anti-Pattern: Hardcoding Model Weights. Never bake the model file (e.g., `.h5` or `.pt`) into the Docker image. The image should be the "Server," and it should pull the "Model" from a URI at startup.

***

#### 🔹 Cheat Sheet / Quick Revision

| **Term**    | **SRE Definition**                                                                  |
| ----------- | ----------------------------------------------------------------------------------- |
| MLflow      | The "Git" for ML models and experiments.                                            |
| Triton      | A high-performance inference server from NVIDIA.                                    |
| CUDA        | The platform that allows software to use GPU power.                                 |
| Cold Start  | The delay when a model is loaded into GPU memory for the first time.                |
| Seldon Core | A K8s operator for managing complex ML graphs.                                      |
| ONNX        | A universal format to move models between frameworks (e.g., PyTorch to TensorFlow). |

***

This is Section 10: MLOps. While traditional DevOps handles the lifecycle of code, MLOps handles the lifecycle of Code + Data + Models. For an SRE/DevOps professional, this section is about building the infrastructure that makes AI scalable, reproducible, and observable.

***

#### 🟢 Easy: MLOps Foundations

_Focus: Understanding the "What" and the fundamental differences from DevOps._

1. What is the core difference between a DevOps pipeline and an MLOps pipeline?
   * _Context:_ Focus on the fact that MLOps must manage Data and Models as first-class citizens alongside code.
2. What is "Model Serving" or "Inference"?
   * _Context:_ Define the process of taking a trained model and deploying it as an API (REST/gRPC) to provide predictions.
3. What is a Model Registry (e.g., MLflow, SageMaker Model Registry)?
   * _Context:_ It is the "GitHub for Models," where you store model versions, their accuracy scores, and who trained them.
4. Why do we need GPUs for Machine Learning instead of just using high-end CPUs?
   * _Context:_ Explain parallel processing—CPUs are good for sequential logic, but GPUs are designed for the massive matrix multiplications required in ML.

***

#### 🟡 Medium: Data Management & Serving

_Focus: Ensuring consistency and scaling the model in production._

1. Explain the difference between Data Drift and Concept Drift.
   * _Context:_ Data Drift is when the _input_ data changes (e.g., users are now using mobile instead of desktop). Concept Drift is when the _relationship_ between input and output changes (e.g., buying patterns change after a pandemic).
2. What is a Feature Store (e.g., Feast), and what problem does it solve?
   * _Context:_ It ensures that the exact same data transformations used during Training are also used during Inference, preventing "Training-Serving Skew."
3. Explain "Shadow Deployment" in MLOps. Why is it safer than A/B testing for a new model?
   * _Context:_ Shadowing sends real traffic to the new model but doesn't show the user the result; it just logs it for comparison. This has zero risk to the user experience.
4. What is DVC (Data Version Control)? Why can't we just store our 10GB datasets in Git?
   * _Context:_ Git is not designed for large binary files. DVC stores the _metadata_ in Git and the actual _data_ in S3/GCS.

***

#### 🔴 Hard: Senior Infrastructure & Resource Optimization

_Focus: Performance, cost, and high-level architectural trade-offs._

1. Scenario: You have an LLM (Large Language Model) that is too large for a single GPU. How do you deploy it?
   * _Context:_ The interviewer is looking for Model Parallelism (splitting the model layers across GPUs) or Quantization (reducing the precision of the model weights to save memory).
2. How do you monitor the "Accuracy" of a model in real-time when you don't yet have the "Ground Truth" (labels) for the new data?
   * _Context:_ Discuss using Proxy Metrics like confidence scores, output distribution shifts, or latency instead of direct accuracy.
3. Explain "Continuous Training" (CT). What triggers a CT pipeline to start?
   * _Context:_ Triggers include: A scheduled timer, a performance drop below a threshold, or the arrival of a specific amount of new data.
4. How do you optimize K8s resource management for ML? Specifically, discuss Taints, Tolerations, and Bin Packing for GPU nodes.
   * _Context:_ How do you ensure your expensive $30,000 GPUs aren't running cheap web-server pods?
5. Calculate the throughput of an inference service if the p99 latency is 100ms and you have 4 replicas with a concurrency of 1 per replica.
   *   Context: Basic math for capacity planning:

       \$$\text{Throughput} = \frac{1}{\text{latency\}} \times \text{concurrency} \times \text{replicas}\$$\$$\text{Throughput} = \frac{1}{0.1\text{s\}} \times 1 \times 4 = 40 \text{ requests per second}\$$

***

#### 💡 Pro-Tip for your Interview

When talking about MLOps, always mention "Reproducibility."

* The SRE Answer: "In MLOps, my goal is absolute reproducibility. If a model behaves strangely in production, I must be able to trace it back to the exact Git commit of the code, the exact DVC version of the dataset, and the exact Hyperparameters used during the training run in the Model Registry."
