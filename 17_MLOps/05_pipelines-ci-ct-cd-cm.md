# 05 — Pipelines: CI, CT, CD, aur CM 🔁

Files 01–04 assume hain. Is file ka goal: tera existing CI/CD gyaan ML pipeline pe map karna, aur woh ek genuinely naya concept samajhna — **Continuous Training (CT)**.

## CI aur CD tujhe pata hai. Yahan kya badalta hai.

| Pipeline | Normal software mein | ML mein |
|---|---|---|
| **CI** (Continuous Integration) | Har commit pe lint, unit test, build | Code lint karo, feature transformation logic unit-test karo, har commit pe data schemas validate karo |
| **CT** (Continuous Training) | *Normal software mein exist hi nahi karta* | Trigger hone pe model automatically retrain karo (naya data, drift detect hua, schedule) |
| **CD** (Continuous Delivery/Deployment) | Built artifact deploy karo agar tests pass hue | Naya model version deploy karo agar evaluation gates pass hue |
| **CM** (Continuous Monitoring) | Uptime/latency/error-rate monitoring | Yeh sab, PLUS model-quality monitoring (drift, accuracy decay) — file 07 dekho |

CT hi woh ek truly naya concept hai. **First principle se socho:** code ek static artifact hai — jab tak koi usse change nahi karta, woh waisa hi rehta hai. Lekin model? Uski quality apne aap degrade ho sakti hai time ke saath, bina kisi ne code touch kiye — duniya badalti hai, data badalta hai, aur model ko pata hi nahi chalta jab tak tu retrain na kare. Traditional CI/CD mein kisi ne yeh socha hi nahi tha ki koi artifact khud-ba-khud stale ho jayega.

## CT run trigger kaun karta hai?

- **Schedule** — har raat / har hafte retrain, kuch bhi ho.
- **Data volume** — jab N naye labeled examples accumulate ho jayein, retrain karo.
- **Drift detected** — ek monitoring job (file 07) flag karti hai ki incoming data ab training data jaisa nahi laga raha.
- **Performance drop** — model se juda business KPI (conversion rate, fraud catch rate) threshold se neeche gir gaya.

## Pipeline ko orchestrate karna

File 02 ke steps (data validation → feature engineering → training → evaluation → registration → deployment) ko ek orchestrator chahiye jo unhe order mein chalaye, failures pe retry kare, aur steps ke beech artifacts pass kare. Options:

- **Kubeflow Pipelines** — Kubernetes-native, har step ek container hai.
- **SageMaker Pipelines** — AWS-managed equivalent.
- **Vertex AI Pipelines** — GCP-managed equivalent.
- **Airflow** — general-purpose DAG orchestrator, ML pipelines ke liye bhi commonly use hota hai, especially data-prep parts ke liye.

DevOps analogy: yeh bilkul Jenkins/GitHub Actions/GitLab CI pipeline jaisa hai, bas stages usually containerized steps ka DAG (directed acyclic graph) hote hain, linear shell-command sequence nahi — kyunki ML pipelines aksar branch aur merge karte hain (e.g., teen candidate model architectures parallel mein train karo, phir best wala pick karo).

```yaml
# conceptual pipeline definition (Kubeflow-style)
steps:
  - validate_data:      { runs: great_expectations_check.py }
  - build_features:      { runs: feature_pipeline.py, needs: [validate_data] }
  - train:                { runs: train.py, needs: [build_features] }
  - evaluate:             { runs: evaluate.py, needs: [train] }
  - register_if_better:  { runs: promote.py, needs: [evaluate] }
```

## Evaluation gates — ML pipeline ke "tests"

Naye trained model (**challenger**) ko promote hone se pehle evaluation gates pass karne padte hain — yeh CI test suite ka ML equivalent hai jo ek bekaar build ko merge hone se rokta hai.

```python
# evaluation_gate.py — training ke baad, registry promotion se pehle chalta hai

champion_metric = get_last_recorded_metric("churn-predictor", stage="Production")
challenger_metric = evaluate(new_model, validation_set)

# Gate conditions
if challenger_metric.accuracy < champion_metric.accuracy - 0.01:
    fail("challenger accuracy regressed more than 1% vs champion")

if challenger_metric.fairness_score < MIN_FAIRNESS_THRESHOLD:
    fail("challenger failed fairness check")

# Promote
register_model(new_model, stage="Staging")  # seedha Production nahi — file 06 dekho
```

Typical gates: accuracy/precision/recall champion ke against ek threshold se zyada regress nahi honi chahiye; fairness/bias checks; latency/model-size checks (bada model zyada accurate ho sakta hai par serve karne ke liye bahut slow); training set pe hi data quality checks (jahan null nahi hone chahiye wahan null nahi, schema expectations se match karta hai).

## Data validation — "linting" step

Training shuru hone se pehle hi, incoming data validate karo: correct schema, unexpected nulls nahi, values expected ranges ke andar, row count mein achanak change nahi. Tools: **Great Expectations**, **TensorFlow Data Validation (TFDV)**, **Pandera**.

DevOps analogy: yeh ek linter/static-analysis step hai, bas code ki jagah data check kar raha hai — "kya yeh data aisa lag raha hai jo ek sane model produce karega," na ki "yeh compile hota hai ya nahi."

## Sab jodke dekho

```
   trigger (schedule / drift / data volume)
             │
             ▼
   ┌───────────────────────────────────────────────┐
   │  CT PIPELINE (Kubeflow/Airflow se orchestrated) │
   │  1. Data validate karo                            │
   │  2. Features build karo                            │
   │  3. Train karo (challenger)                        │
   │  4. Champion ke against evaluate karo (gate)        │
   │  5. Register karo (Staging, agar gate pass hua)      │
   └───────────────────────────────────────────────┘
             │
             ▼
   CD: challenger ko Staging environment mein deploy karo (shadow/canary — file 06)
             │
             ▼
   CM: challenger ka real-world performance monitor karo (file 07)
             │
             ▼
   Production pe promote karo, ya rollback — insaan ya automated decision
```

## Quick self-check ✅

1. CT ka full form kya hai aur normal software pipeline ko yeh kyun nahi chahiye?
2. Teen cheezein bata jo CT run trigger kar sakti hain.
3. Evaluation gate kya hai, aur yeh normal CI test suite se kaise similar hai (aur kaise alag hai)?
4. Data validation training se pehle kyun hoti hai, baad mein kyun nahi?

**Next:** [`06_deployment-and-serving.md`](06_deployment-and-serving.md) — evaluation gate pass kar chuka model actually real users ke saamne safely kaise aata hai.
