# 06 — Deployment aur Serving 🚦

Files 01–05 assume hain. Is file ka goal: samajhna trained model ek usable service ki tarah kaise expose hota hai, aur naye model versions deploy karne ke safe-rollout patterns kya hain.

## Predictions serve karne ke teen tareeke

Model serve kaise karna hai — yeh koi chhota technical detail nahi, yeh fundamentally ek latency-vs-throughput tradeoff hai, bilkul waisa jaisa normal software mein synchronous API call vs background job queue choose karne ka hota hai.

- **Batch inference** — model ko ek bade dataset pe schedule pe chalao (e.g., raat ko), results ek table mein likh do. High throughput, latency irrelevant hai. Example: har customer ka churn risk raat mein ek baar score karna.
- **Online (real-time) inference** — model ek HTTP/gRPC API ke peeche deploy hota hai. Request aati hai, prediction jaati hai, synchronously, usually 100ms se kam mein. Example: checkout ke dauraan fraud check.
- **Async inference** — client request submit karta hai, ek job ID wapas milta hai, baad mein result poll karta hai (ya webhook milta hai). Tab use hota hai jab inference synchronously karne ke liye bahut slow ho. Example: video content moderation, bade LLM generations.

DevOps analogy: batch = cron job / ETL job. Online = tight SLA wala normal REST API. Async = message-queue-backed worker (SQS + Lambda, ya Celery), jahan client result ka wait karke block nahi hota.

## Serving frameworks

Ek trained model file akele ek service nahi hai — tujhe ek serving layer chahiye jo model load kare, API expose kare, batching/concurrency handle kare, aur scale kare.

- **KServe** — Kubernetes-native model serving, kai frameworks support karta hai (scikit-learn, TensorFlow, PyTorch, XGBoost) ek standard inference API ke saath, autoscaling (scale-to-zero included).
- **TensorFlow Serving** — high-performance serving specifically TensorFlow models ke liye.
- **Triton Inference Server** (NVIDIA) — GPU-optimized, multiple frameworks aur multiple models per server support karta hai, high-throughput batch/GPU workloads ke liye achha.
- **vLLM** — LLMs efficiently serve karne ke liye specialized (file 09 dekho).

DevOps analogy: yeh application server ka ML equivalent hain (jaise Gunicorn ya Envoy) — yeh tere "code" (model) ko woh plumbing pehna dete hain jo HTTP/gRPC traffic ko scale pe reliably serve karne ke liye chahiye, taaki tu production mein `model.predict()` ke around khud Flask app hand-roll na kare.

```yaml
# conceptual KServe InferenceService — model ko k8s-native API ki tarah deploy karna
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: churn-predictor
spec:
  predictor:
    sklearn:
      storageUri: "s3://models/churn-predictor/v3"
    minReplicas: 2
    maxReplicas: 10
```

## Safe rollout strategies — jo tujhe already pata hai, usi pe mapped

Blue/green, canary, aur A/B testing tujhe regular deployments se pata hai. ML mein yeh same reason se use hote hain (naye version ka risk kam karna), lekin jo cheez tu compare kar raha hai woh sirf "crash toh nahi ho raha" nahi hai — woh hai "kya is model ki *prediction quality* actually behtar hai."

| Strategy | Normal software | ML models |
|---|---|---|
| **Shadow** | Naye service ko duplicate traffic milta hai, response discard hota hai, sirf log hota hai | Challenger model wahi live requests score karta hai jo champion karta hai, lekin uske predictions users ko kabhi nahi dikhaye jaate — sirf offline accuracy/latency compare karne ke liye use hota hai |
| **Canary** | Traffic ka chhota % naye version ko route hota hai | Live traffic ka chhota % challenger model ko route hota hai; uske predictions users ko DIKHAYE jaate hain, lekin blast radius chhota rehta hai |
| **A/B testing** | Do versions ke beech conversion compare karo | Users ko bucket A (champion) / bucket B (challenger) mein daalo; business metric (CTR, conversion) ko statistical significance testing ke saath measure karo, phir winner decide karo |
| **Blue/Green** | Poora traffic swap, instant rollback | Same — poora traffic naye model version pe swap karo, purana warm rakho instant rollback ke liye |

Genuinely naye model ke liye typical order: **Shadow → Canary → A/B test → full rollout (Blue/Green swap)**. Har stage zyada cost karta hai (user exposure ke terms mein) lekin zyada prove bhi karta hai (confidence ke terms mein).

```
  Shadow            Canary              A/B Test              Full rollout
  (0% user-visible) (~5% user-visible)  (50/50 statistical)   (100%, instant rollback ready)
  ────────────────▶ ─────────────────▶ ─────────────────────▶ ─────────────────────
  "yeh sahi se        "kya yeh real       "kya yeh ACTUALLY      "ship kar do"
   chal bhi raha hai?"  traffic survive     behtar hai,
                        karta hai?"          provably?"
```

Normal software ke comparison mein yeh extra step kyun? Kyunki ek model infra point-of-view se perfectly "healthy" ho sakta hai (koi error nahi, normal latency, har request pe HTTP 200) jabki chupke se *worse predictions* de raha ho. Traditional health checks yeh catch nahi kar sakte — prediction quality compare karne ke liye real traffic chahiye, aur aksar statistical testing bhi. Yehi wajah hai ki "wrong predictions with 200 OK" sabse common ML incident types mein se ek hai (file 07 aur `interview.md` dekho).

## Models ke liye rollback

Kyunki models registry mein versioned artifacts hain (file 04), rollback usually sirf serving layer ko previous model version pe wapas point karna hai — conceptually bilkul waisa jaisa ek container deployment ko previous image tag pe rollback karna.

```bash
# rollback = serving config ko revert karo, purani registry version pe point karo
kubectl apply -f inference-service-v2.yaml   # storageUri: s3://models/churn-predictor/v2
```

Agar serving config Git mein hai (GitOps-style), rollback literally serving manifest pe `git revert` hai — bilkul kisi bhi aur GitOps rollback jaisa.

## Quick self-check ✅

1. Batch inference kab choose karega online inference ke bajaye?
2. Ek model ke liye shadow deployment aur canary deployment mein kya farak hai?
3. Ek model deployment infra dashboards pe "healthy" kaise dikh sakta hai jabki woh actually ek bekaar rollout ho?
4. Naye model version ke rollout stages ka typical order kya hai, aur order kyun matter karta hai?

**Next:** [`07_monitoring-and-drift.md`](07_monitoring-and-drift.md) — model live hone ke baad kya monitor karna hai, aur is file ka "chupke se galat" failure mode kaise detect karte hain.
