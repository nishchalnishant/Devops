# 08 — Platform, GPU Scheduling, aur Cost 💰

Files 01–07 assume hain. Is file mein tera existing Kubernetes/Terraform/cost-optimization expertise almost directly transfer hota hai — main naya variable bas GPU hai.

## GPUs kyun, aur yeh ek scheduling problem kyun hai

Training (aur large models serve karna) mein massive matrix multiplication hota hai, jo GPUs CPUs se kahin zyada fast karte hain. GPUs per-hour CPU instances se 10-50x zyada mehenge bhi hote hain, aksar scarce hote hain (cloud quota limits), aur idle GPU time pure waste hai. Isi wajah se "GPU scheduling" platform engineering ke andar apni khud ki specialty ban jaati hai.

## Kubernetes pe GPU workloads chalana

Taints, tolerations, aur node affinity tujhe already pata hai — ML mein exactly yahin use hote hain:

```yaml
# GPU node pool: tainted hai taaki sirf GPU-requesting pods yahan land karein
apiVersion: v1
kind: Node
metadata:
  labels:
    accelerator: nvidia-a100
spec:
  taints:
    - key: "nvidia.com/gpu"
      value: "true"
      effect: "NoSchedule"
---
# Training job: taint ko tolerate karta hai, GPU resource request karta hai
apiVersion: batch/v1
kind: Job
metadata:
  name: train-churn-model
spec:
  template:
    spec:
      tolerations:
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"
      containers:
        - name: trainer
          image: my-training-image:v3
          resources:
            limits:
              nvidia.com/gpu: 1
```

**NVIDIA device plugin** Kubernetes ke liye hi `nvidia.com/gpu` ko ek schedulable resource banata hai — iske bina, Kubernetes ko GPUs ka concept hi nahi hota, bilkul waisa jaise bina CSI driver ke usse disk ka concept nahi hota.

## GPU nodes autoscale karna

**Karpenter** (ya cluster autoscaler) GPU nodes on-demand provision karta hai jab koi training job ek maangta hai, aur idle hone pe unhe wapas zero tak scale kar deta hai — critical hai kyunki GPU nodes unused chalate rehna bahut mehenga hai. Yeh wahi "idle hone pe zero tak scale karo" pattern hai jo tu kisi bhi expensive, bursty workload pe apply karega, bas galat hone ka cost-per-hour yahan bahut zyada hai.

## Training ke liye Spot instances

Training jobs usually fault-tolerant hote hain ek aise tareeke se jo normal production services nahi hote — agar training job beech mein kill ho jaaye, tu bas resume kar sakta hai, agar checkpoint kar rakha ho.

- **Checkpointing**: har N training steps pe model state S3/GCS mein save karo. Agar job (ya jis Spot instance pe woh chal rahi thi) kill ho jaaye, agla run scratch se shuru hone ke bajaye last checkpoint se resume hota hai.
- Isi se **Spot/Preemptible instances** training ke liye perfect fit ban jaate hain (on-demand se 60-90% sasta) — wahi risk-tolerance calculus jo tu kisi bhi interruptible batch workload ke liye use karega, bas ab GPUs pe apply ho raha hai jahan savings absolute dollars mein bade hote hain.

```python
# conceptual checkpointing ek training loop mein
for step, batch in enumerate(training_data):
    train_step(model, batch)
    if step % 500 == 0:
        save_checkpoint(model, f"s3://checkpoints/run-42/step-{step}")
```

Inference/serving, iske ulta, usually stable (non-Spot) capacity pe rehna chahiye, kyunki ek interrupted serving pod ka matlab hai dropped user-facing requests — bilkul wahi logic jo kisi bhi latency-sensitive production service ke liye hota hai.

## Distributed training (vocabulary jaan, internals nahi)

Jo models ek GPU pe fit nahi hote, unki training multiple GPUs/machines mein split hoti hai:

- **Data parallelism**: har GPU model ki poori copy rakhta hai, data ka alag slice process karta hai, gradients GPUs ke across sync/average hote hain.
- **Model/tensor parallelism**: model khud itna bada hai ki ek GPU pe fit nahi hota, toh alag *layers ya tensor shards* alag GPUs pe rehte hain.
- **PyTorch FSDP** / **DeepSpeed ZeRO**: frameworks jo model parameters, gradients, aur optimizer state ko GPUs ke across shard karte hain taaki bahut bade models bina ek giant GPU ke trainable ho sakein.
- **InfiniBand networking**: high-bandwidth, low-latency networking GPUs ke beech, zaroori hai kyunki distributed training constantly bahut saara data machines ke beech sync karti hai — normal Ethernet scale pe bottleneck ban jaata hai.

Inhe implement karna zaroori nahi — bas naam pehchaan, aur *kyun* exist karte hain woh jaan: ek GPU ki memory limited hoti hai (e.g., 80GB), aur bade models (ya bade batch sizes) simply fit nahi hote, isliye kaam split karna padta hai.

## Cost optimization — zyadatar familiar levers, bas GPUs pe applied

| Lever | Normal DevOps context | ML/GPU context |
|---|---|---|
| Right-sizing | CPU/memory over-provision mat kar | Chhote model ke liye A100 mat maang jab T4 kaafi ho |
| Spot/preemptible | Batch jobs, CI runners | Training jobs (checkpointing ke saath) |
| Autoscaling to zero | Idle dev environments | Idle GPU node pools |
| Off-peak pe batch work schedule karna | Nightly batch ETL | Bade training runs off-peak cloud pricing windows ke liye scheduled |
| Multi-tenancy | Nodes pe pods ko bin-pack karna | Ek GPU ko multiple chhote inference workloads mein share karna (e.g., NVIDIA MIG — Multi-Instance GPU, ek physical GPU ko isolated slices mein split karta hai) |
| Model-level cost control | N/A | "Simple" queries ko chhote/sasta models pe route karo, bada mehenga model tabhi use karo jab zaroorat ho (file 09 dekho) |

## Quick self-check ✅

1. GPU node pools usually sirf labels ke bajaye taints aur tolerations kyun use karte hain?
2. Spot instances training ke liye usually theek kyun hain lekin serving ke liye risky?
3. Checkpointing konsi problem solve karta hai, aur yeh Spot instances ko training ke liye use karne layak kaise banata hai?
4. GPU cost kam karne ka ek lever bata jiska direct DevOps-world equivalent hai, aur ek jo ML-specific hai.

**Next:** [`09_llmops-and-genai.md`](09_llmops-and-genai.md) — upar ka sab kuch abhi bhi apply hota hai, plus large language models operate karne mein kya unique hai.
