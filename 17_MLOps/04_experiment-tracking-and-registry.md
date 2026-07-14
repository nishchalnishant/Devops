# 04 — Experiment Tracking aur Model Registry 🧪

Files 01–03 assume hain. Is file ka goal: samajhna training runs kaise record aur compare hote hain, aur ek trained model "approved, deployable artifact" kaise banta hai.

## Bas `train.py` chalake result eyeball kyun nahi kar sakta?

First principles se socho: ek data scientist model ek baar train nahi karta — dozens ya hundreds baar karta hai, har baar hyperparameters (settings jaise learning rate, training passes ki count, model architecture) tweak karke dekhta hai kya best result deta hai. **Ab yeh sawaal poochh:** agar 40 attempts kiye aur kahin record nahi kiya, tu kaise batayega kaunsa best tha, ya production mein abhi kaunsa model hai aur woh kis hyperparameters se bana? Bina system ke, yeh sawaal answerable hi nahi hai.

DevOps analogy: yeh CI system ke build history aur artifact provenance ka ML version hai — bas ek commit pe ek build nahi, ek commit pe dozens "builds" (training runs) ho sakte hain, har ek alag tuning knobs ke saath, aur tujhe unki *quality* compare karni hai, sirf "compile hua ya nahi" nahi.

## Experiment tracking

Ek **experiment tracker** har training run ke liye yeh log karta hai:

- **Inputs**: hyperparameters use hue, dataset version, code commit hash, random seed.
- **Outputs**: metrics (accuracy, precision, recall, loss curves), aur resulting model artifact.

```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("num_epochs", 20)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("f1_score", 0.91)
    mlflow.sklearn.log_model(model, "my_model")
```

Har run ek UI mein dikhta hai jahan runs ko side-by-side sort/filter/compare kar sakta hai — e.g., "mujhe har wo run dikha jispe `learning_rate < 0.05` hai, `accuracy` descending sort ke saath." Popular tools: **MLflow Tracking**, **Weights & Biases (W&B)**, **Neptune**.

Yeh system na ho toh teams "graduate student descent" karte hain — haath se values tweak karte hain aur results spreadsheet mein (ya kahin bhi nahi) yaad rakhte hain. Company scale pe yeh tikta nahi.

## Hyperparameters vs. parameters — interview mein confuse mat karna

First principle se yaad rakh: **kaun set karta hai, aur kab?**

- **Parameters** (weights) — training *ke dauraan* automatically seekhe jaate hain. Tu inhe kabhi haath se set nahi karta. Yeh "model" hai.
- **Hyperparameters** — insaan (ya automated search) training *shuru hone se pehle* set karta hai. Yeh control karte hain *training kaise hoti hai*: learning rate, batch size, layers ki count, epochs ki count.

DevOps analogy: hyperparameters build flags jaise hain (`-O2`, `--target=prod`) — yeh build process ko configure karte hain. Parameters compiled output khud hain.

## Model registry hai kya, aur exist kyun karta hai?

Ek training run tujhe achha model de deta hai. Ab first principles se socho: **"ek run jo experiment tracker mein hai" aur "production mein deploy karne layak, approved model" — yeh ek hi cheez hai kya?** Nahi. Experiment tracker sabkuch log karta hai — including bekaar runs. Tujhe ek alag, zyada permanent aur structured jagah chahiye jahan sirf woh models hon jo actually promote hone ke liye consider ho rahe hain. Yehi **model registry** hai: trained models ka ek versioned catalog, har ek metadata ke saath (konsa run, konsi metrics, konsi dataset version) aur ek **lifecycle stage**.

Standard staging workflow:

```
None ──▶ Staging ──▶ Production ──▶ Archived
```

- **None**: abhi-abhi register hua, promotion ke liye evaluate nahi hua.
- **Staging**: candidate jo evaluate ho raha hai (e.g., shadow-tested — file 06 mein dekho).
- **Production**: live traffic actively serve kar raha hai.
- **Archived**: retire ho chuka, audit/rollback ke liye rakha hua.

DevOps analogy: yeh bilkul container image registry jaisa hai environment promotion ke saath (`dev` tag → `staging` tag → `prod` tag) — bas yahan "image" ek model file hai, aur "promotion" ke liye integration tests nahi, accuracy/fairness checks pass karne padte hain.

```python
# MLflow Model Registry example
mlflow.register_model("runs:/<run_id>/my_model", "churn-predictor")

# ek version ko Production pe promote karo
client.transition_model_version_stage(
    name="churn-predictor", version=3, stage="Production"
)
```

Popular tools: **MLflow Model Registry**, **W&B Model Registry**, **SageMaker Model Registry**, **Vertex AI Model Registry**.

## Model cards

Ek **model card** documentation hai jo registered model ke saath ship hoti hai: yeh kya karta hai, kis data pe train hua, known limitations, intended use cases, aur fairness/bias evaluation results. Isse model artifact ka README samajh — kisi bhi company mein zaroori hai jahan model governance ya compliance requirements hon (finance, healthcare, hiring).

## Quick self-check ✅

1. Parameter aur hyperparameter mein kya farak hai?
2. Experiment tracker kya log karta hai jo model registry nahi karta (aur vice versa)?
3. Standard model registry staging workflow describe kar.
4. Model registry ko container registry with environment promotion jaisa kyun bola jaata hai?

**Next:** [`05_pipelines-ci-ct-cd-cm.md`](05_pipelines-ci-ct-cd-cm.md) — training, evaluation, aur registration ko automated pipelines mein wire karna, aur "Continuous Training" CI/CD ke upar kya add karta hai.
