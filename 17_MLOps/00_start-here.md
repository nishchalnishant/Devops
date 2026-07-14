# MLOps for DevOps Engineers — Start Here 🚀

Bhai, agar tu DevOps jaanta hai — CI/CD, Kubernetes, Terraform, monitoring, sab clear hai — lekin ML ka naam sunte hi thoda ghabra jaata hai, toh yeh folder tere liye hi bana hai. Zero ML background assume kiya gaya hai. Har naya ML concept ek DevOps concept se compare karke samjhaya jayega, kyunki tu already wo jaanta hai.

## Pehle principle se samjhte hai — yeh cheez hai kya, aur exist kyun karti hai

Sabse pehla sawaal jo poochna chahiye: **MLOps ek naya subject hai ya DevOps ka hi extension?**

Answer: extension hai. Tu already jaanta hai `code + config → running service`. Bas ML mein ek naya ingredient add ho jaata hai:

```
Normal app:   code + config                    → running service
ML app:       code + data + config → trained model → running service
```

Ek naya artifact aa gaya — **model**. Aur yeh model kisi engineer ne haath se nahi likha, yeh **data se "grow" hua hai** (training naam ke process se). Bas yehi ek fark hai, aur MLOps mein jitni bhi ajeeb-si cheezein lagti hain (feature store, drift monitoring, model registry...) — sab is ek fark ko handle karne ke liye exist karti hain. Agar tu yeh ek line yaad rakhega, poora MLOps "obvious" lagne lagega instead of "naya jargon."

**Toh sawaal yeh nahi hai "MLOps mein kya seekhna hai" — sawaal yeh hai "code ke saath ek aisa artifact aane se kya-kya naya problem aata hai, jo pehle exist hi nahi karta tha."** Har file isi lens se likhi gayi hai.

## Padhne ka order

Order mein hi padhna — har file pichli file ka gyaan assume karti hai, bilkul jaise ek dependency chain.

| # | File | Kya seekhega |
|---|------|--------------|
| 01 | [`01_ml-basics-for-devops.md`](01_ml-basics-for-devops.md) | Model asal mein hai kya, training vs inference, vocabulary (dataset, feature, label) — sab DevOps terms se map karke |
| 02 | [`02_ml-lifecycle-and-artifacts.md`](02_ml-lifecycle-and-artifacts.md) | Poora ML project lifecycle, teen artifacts (code/data/model), reproducibility, MLOps maturity levels |
| 03 | [`03_data-and-feature-management.md`](03_data-and-feature-management.md) | Data versioning, feature stores, training-serving skew, label leakage |
| 04 | [`04_experiment-tracking-and-registry.md`](04_experiment-tracking-and-registry.md) | Experiment tracking, hyperparameters, model registry, staging workflow |
| 05 | [`05_pipelines-ci-ct-cd-cm.md`](05_pipelines-ci-ct-cd-cm.md) | CI/CT/CD/CM pipelines — tere CI/CD ka ML version, plus Continuous Training |
| 06 | [`06_deployment-and-serving.md`](06_deployment-and-serving.md) | Models ko API ki tarah serve karna, batch vs online vs async, shadow/canary/A-B/blue-green |
| 07 | [`07_monitoring-and-drift.md`](07_monitoring-and-drift.md) | Model "up" hote hue bhi galat kaise ho sakta hai, data drift vs concept drift |
| 08 | [`08_platform-gpu-and-cost.md`](08_platform-gpu-and-cost.md) | Kubernetes pe ML chalana, GPU scheduling, distributed training, cost control |
| 09 | [`09_llmops-and-genai.md`](09_llmops-and-genai.md) | LLMOps: prompt versioning, RAG pipelines, vector databases, LLM serving |
| — | [`interview.md`](interview.md) | Upar ka sab kuch condensed — Easy / Medium / Hard interview Q&A |

## Ek line ka mental model — isse kabhi mat bhoolna

> **MLOps = DevOps + ab tujhe ek "config file" (model) ko version, test, deploy, aur monitor karna hai jise kisi ne haath se nahi likha — woh data se ugaya gaya hai, isliye woh chupke se stale ho sakta hai, bina code change kiye bhi.**

Yeh line har file ke peeche ka "why" hai. Jab bhi koi naya tool ya practice ajeeb lage, wapas isi line pe aa jaana — 90% chance hai answer yahin milega.

## Agar sirf interview prep chahiye

Seedha [`interview.md`](interview.md) pe jaa. Woh self-contained hai aur same material ko Q&A format mein cover karta hai — tension mat le.
