# 02 — ML Lifecycle aur Teen Artifacts 🔄

Assume karta hoon tune [`01_ml-basics-for-devops.md`](01_ml-basics-for-devops.md) padh liya hai. Is file ka goal: poora project lifecycle samajhna, aur yeh samajhna ki "reproducibility" ML mein itna bada deal kyun hai normal software ke comparison mein.

## Software ka ek artifact hota hai. ML ke teen.

Chalo first principles se sochte hain: **agar kal tera model production mein galat prediction de raha hai, tujhe kya-kya cheezein pata honi chahiye taaki tu wapas trace kar sake ki kya hua?** Sirf code kaafi nahi hoga — tujhe pata hona chahiye kis *data* pe train hua tha, aur konsa *model* actually deployed hai. Yehi teen cheezein ban jaati hain teen artifacts.

| | Normal software | ML system |
|---|---|---|
| Artifact 1 | **Code** | **Code** (training script, feature logic, serving code) |
| Artifact 2 | — | **Data** (jis dataset pe train hua) |
| Artifact 3 | — | **Model** (trained weights + preprocessing steps + metadata) |

Normal web app mein, same Git commit checkout karne se same behavior milta hai. ML system mein, same commit checkout karna kaafi nahi — tujhe *same data* bhi chahiye, aur ideally same random seed, taaki wapas wahi model mile. Interview mein "ML ko special tooling kyun chahiye" wale sawaal ka yehi sabse bada reason hai.

**First principle:** agar tu model reproduce nahi kar sakta, tu use debug nahi kar sakta, audit nahi kar sakta, aur safely improve bhi nahi kar sakta. Is file ki har cheez isi ek problem ko solve karne ke liye hai — reproduction possible banane ke liye.

## End-to-end lifecycle

```
1. Data collection & validation
        │
        ▼
2. Feature engineering  ──────────────┐
        │                             │ (yeh logic training time aur serving
        ▼                             │  time pe IDENTICAL hona chahiye —
3. Training                           │  dekho 03_data-and-feature-management.md)
        │                             │
        ▼                             │
4. Evaluation  (current production    │
   model se compare — "champion")     │
        │                             │
        ▼                             │
5. Registration (model registry)      │
        │                             │
        ▼                             │
6. Deployment (serving layer)  ◀──────┘
        │
        ▼
7. Monitoring (drift, latency, business KPIs)
        │
        └──▶ wapas step 1 pe trigger karta hai (retrain) — yeh loop hi "Continuous Training" hai
```

Isse normal CI/CD pipeline se compare karo: steps 1–5 "build and test" ki jagah lete hain, step 6 "deploy" hai, aur step 7 "observability" hai — bas farak yeh hai ki step 7 khud step 1 ko trigger kar sakta hai automatically. Yeh feedback loop (monitoring → retraining) normal software mein barely exist karta hai, lekin ML systems mein central hai.

## Teeno artifacts ko version karna

Code version karna tujhe pata hai (Git). ML do aur cheezein add karta hai jo version karni padti hain — aur dono ka reason wahi ek line hai: **agar version nahi kiya, reproduce nahi kar sakta.**

- **Data versioning** — tools jaise **DVC** (Data Version Control) bade datasets ko Git-jaisa version karne dete hain, bina Git repo ko bloat kiye. DVC ek chhota pointer file Git mein rakhta hai; actual data S3/GCS/Azure Blob mein hota hai. `git checkout <commit>` + `dvc pull` = wahi exact dataset jo us commit ke time use hua tha. Detail mein [`03_data-and-feature-management.md`](03_data-and-feature-management.md) mein.
- **Model versioning** — ek **model registry** (e.g., MLflow Model Registry) har trained model ko metadata ke saath store karta hai: konsa code commit, konsi dataset version, konse hyperparameters, aur kya metrics mile. Detail mein [`04_experiment-tracking-and-registry.md`](04_experiment-tracking-and-registry.md) mein.

Reproducibility checklist (yeh interview mein baar-baar aata hai):

1. Library versions pin karo (`requirements.txt`, conda lockfile, ya container image) — bilkul waisa jaise kisi bhi software build mein dependencies pin karte ho.
2. Training data version karo (DVC, Delta Lake / Iceberg table snapshot).
3. Har hyperparameter aur use hua random seed log karo.
4. Training run ke exact Git commit hash ko record karo.
5. Yeh sab model artifact ke saath registry mein store karo.

Agar yeh paanch cheezein hain, tu hamesha jawab de sakta hai "yeh model aisa behave kyun kar raha hai" — bilkul wahi reason jispe tu container image ke liye build provenance rakhta hai.

## MLOps maturity levels

Yeh ek bahut common interview framing hai (Google ke MLOps whitepaper se). In teen levels ko cold yaad rakh — first principles se socho: **automation kitna hai, aur retrain kaun trigger karta hai — insaan ya system?**

- **Level 0 — Manual.** Ek data scientist apne laptop pe model train karta hai, file ko engineer ko email karta hai, jo manually deploy karta hai. Koi automation nahi, koi pipeline nahi, koi monitoring nahi. Fragile hai, ek-do models se zyada scale nahi karta.
- **Level 1 — Pipeline automation, but no Continuous Training.** Data prep → training → evaluation ek automated pipeline mein wired hai (e.g., Kubeflow Pipelines, SageMaker Pipelines), lekin ek insaan abhi bhi decide karta hai *kab* retrain trigger karna hai aur *kya* result deploy karna hai.
- **Level 2 — Full CI/CD/CT.** System khud detect karta hai ki model ko retraining chahiye (drift, schedule, naya data volume), khud retrain karta hai, gates ke against evaluate karta hai, aur pass hone pe khud promote kar deta hai — ek fully automated CI/CD pipeline ka ML version, bas beech mein ek training step hai.

Zyadatar real companies apne zyada models ke liye Level 1 pe operate karti hain, aur Level 2 sirf un chuninda, high-value, high-change-rate models ke liye reserve karti hain (e.g., fraud detection, ad ranking) jahan manual retraining drift ke saath keep up nahi kar sakti.

## "Champion vs. challenger" — yeh term baar-baar sunega

- **Champion**: woh model jo abhi production mein live hai.
- **Challenger**: naya trained candidate model jo evaluate ho raha hai ki champion ko replace kar sake ya nahi.

Har evaluation step (upar step 4) asal mein yeh poochh raha hai: *kya challenger champion ko un metrics pe beat karta hai jo matter karte hain, bina un metrics ko regress kiye jo nahi karte?* Yeh conceptually bilkul waisa hai jaise ek canary deployment naye software version ko currently-running version se compare karta hai — bas comparison metric error-rate/latency ki jagah model accuracy/precision/recall hai. Deployment strategies [`06_deployment-and-serving.md`](06_deployment-and-serving.md) mein hain.

## Quick self-check ✅

1. Teen artifacts naam bata jo ML system ke paas hote hain jo normal app ke paas nahi (well, do extra — code toh common hai).
2. "Same Git commit checkout karna" kyun kaafi nahi hai ML result reproduce karne ke liye?
3. MLOps maturity Level 1 aur Level 2 mein kya farak hai?
4. "Champion" model kya hota hai?

**Next:** [`03_data-and-feature-management.md`](03_data-and-feature-management.md) — data aur features kaise store, version, aur training/serving ke beech consistent rakhe jaate hain.
