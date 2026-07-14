# 07 — Monitoring aur Drift 📉

Files 01–06 assume hain. Is file ka goal: samajhna "service up hai" ML ke liye kaafi kyun nahi hai, aur drift detection ki vocabulary seekhna.

## Core idea: ek model "up" ho sakta hai aur phir bhi galat

Ek web server ya toh sahi respond karta hai ya nahi karta — tu uptime, latency, error rate monitor karta hai, aur basically covered hai. ML model alag hai: woh har single baar HTTP 200 de sakta hai, 20ms mein, jabki **systematically galat predictions** de raha ho. Sirf infra monitoring yeh dekh hi nahi sakti. Tujhe apni normal infra monitoring ke upar ek second, ML-specific monitoring layer chahiye.

```
   INFRA MONITORING (yeh tujhe pata hai)          MODEL MONITORING (naya)
   ────────────────────────────────────────     ─────────────────────
   Kya service up hai?                            Kya predictions abhi bhi achhe hain?
   Latency, error rate, CPU/memory                Drift, confidence distribution,
   Prometheus, Grafana, PagerDuty                 delayed accuracy, business KPIs
```

Dono zaroori hain. Koi bhi dusre ki jagah nahi le sakta.

## Models time ke saath degrade kyun hote hain?

Kyunki model ne "duniya" ko waisa seekha jaisi woh training data mein dikhti thi. Agar duniya badal jaaye aur model retrain na ho, uski assumptions stale ho jaati hain. Yeh do alag tareekon se hota hai — yeh distinction sabse commonly tested MLOps interview concepts mein se ek hai:

### Data drift (a.k.a. covariate shift)

**Input features ki distribution** badal jaati hai, jabki inputs aur outputs ke beech ka underlying relationship nahi badla. Example: 2023 income data pe trained ek credit scoring model 2024 mein systematically alag income distributions dekhna shuru karta hai inflation ki wajah se. Relationship "higher income → lower default risk" abhi bhi sach hai — lekin model ab aise input values dekh raha hai jinpe woh train nahi hua tha, toh uski calibration kharab ho jaati hai.

### Concept drift

**Inputs aur outputs ke beech ka relationship khud** badal jaata hai — duniya ke rules change hue, sirf inputs nahi. Example: ek fraud model jo naye fraud technique aane se pehle train hua tha; wahi input pattern jo pehle "safe" matlab rakhta tha ab "fraud" matlab rakhta hai, kyunki fraudsters ne tactics badal diye. "Aur zyada wahi data" is problem ko fix nahi karta — ground truth mapping ab genuinely alag hai.

Yaad rakhne ka simple tareeka: **data drift = sawaal badal gaye. Concept drift = jawaab badal gaye.**

## Drift detect kaise karte hain?

Ek reference window ki distribution (e.g., training data, ya pichle mahine ka traffic) ko current window ki distribution (is hafte ka live traffic) se compare karo, per feature.

Common statistical tests:

- **PSI (Population Stability Index)** — ek single number jo batata hai feature ki distribution kitni shift hui; common thresholds: `<0.1` = koi significant shift nahi, `0.1–0.25` = moderate, `>0.25` = significant shift, investigate karo.
- **KS test (Kolmogorov–Smirnov)** — test karta hai ki do samples same distribution se aaye hain ya nahi, continuous numeric features ke liye achha kaam karta hai.
- **Chi-squared test** — categorical features ke liye.
- **Jensen-Shannon divergence** — ek aur distribution-comparison metric, symmetric aur bounded, drift-monitoring tools mein popular.

Tools jo yeh tere liye karte hain: **Evidently AI**, **WhyLabs**, **Arize**, **Fiddler** — tu inhe apna reference aur current data windows point kar deta hai aur yeh metrics compute karke thresholds pe alert karte hain.

```python
# conceptual drift check
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=training_set, current_data=last_7_days_of_traffic)
# report flag karti hai kaunse features threshold se zyada drift hue
```

## Delayed-label problem

Bahut se models ke liye, tujhe *actual* sahi jawab (ground truth label) days ya weeks baad hi pata chalta hai. Example: loan actually default hua ya nahi? Shayad ek saal tak pata na chale. Iska matlab hai tu aksar "accuracy" ko near-real-time mein directly monitor nahi kar sakta — tujhe proxy signals chahiye:

- **Confidence/probability distribution** — agar model ke predicted probabilities achanak 0.5 (uncertain) ke bahut kareeb cluster hone lagein jitna pehle nahi hote the, kuch off hai, ground truth aane se pehle hi.
- **Output entropy** — prediction uncertainty mein overall jump.
- **Input drift** (upar wala) — ek strong leading indicator ki output quality kharab hone wali hai, labels aane se pehle hi.
- **Proxy business metrics** — e.g., ek recommendation model ke liye, click-through rate turant available hai, chahe "kya unhone actually product enjoy kiya" na pata ho.

## Retrain kya trigger karta hai (file 05 ke CT se wapas jodo)

- Drift metric (PSI, KS test) threshold cross kar jaaye.
- Scheduled retrain (e.g., weekly, drift ho ya na ho).
- Ek proxy business KPI threshold se neeche gir jaaye.
- Itna naya labeled data accumulate ho jaaye ki retrain worth ho.

## Ek monitoring stack, end to end

```
   Serving layer  ──▶  har (input, prediction, confidence) log karo
                              │
                              ▼
                    ┌───────────────────┐
                    │  Drift monitoring   │  (Evidently / WhyLabs, scheduled job)
                    │  live vs             │
                    │  training distribution compare karta hai│
                    └─────────┬──────────┘
                              │ threshold breach hua
                              ▼
                    alert (PagerDuty/Slack)  ──▶  CT pipeline trigger karta hai (file 05)
                              │
                              ▼
                    jab ground truth aa jaaye:
                    REAL accuracy compute karo, loop close karo
```

## Quick self-check ✅

1. Uptime/latency monitoring ek ML system ke liye kaafi kyun nahi hai?
2. Ek-ek sentence mein, data drift ko concept drift se distinguish kar.
3. Drift detect karne ke liye use hone wale do statistical tests bata aur kaunsa kis type ke feature ke liye best suited hai.
4. Teams accuracy directly dekhne ke bajaye confidence distribution jaise proxy signals pe kyun rely karti hain?

**Next:** [`08_platform-gpu-and-cost.md`](08_platform-gpu-and-cost.md) — yeh sab infrastructure Kubernetes pe chalana, GPU scheduling, aur cost control.
