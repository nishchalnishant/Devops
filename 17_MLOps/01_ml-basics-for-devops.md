# 01 — ML Basics for DevOps Engineers 🧠

Is file ka goal: end tak tu *model*, *training*, *inference*, *dataset*, *feature*, aur *label* define kar payega bina kahin dekhe — sirf DevOps se comparisons use karke, jo tu already jaanta hai.

## "Model" hai kya cheez, first principles se?

AI ka hype ek side rakh de do second ke liye. Ek sawaal se shuru karte hain: **agar main tujhe koi bhi normal software artifact ka example du (jar, binary, container image), unme common kya hai?** Sabme ek cheez common hai — woh kisi *process* se generate hue hain, kisi *source* se.

Ab **model** bhi wahi hai — bas uska "source" alag hai. Model ek file hai jisme ek mathematical function ke parameters (numbers) hote hain, jo **historical data pe algorithm chalake produce hue hain** — na ki kisi developer ne line-by-line likhe hain.

| DevOps | ML | Why same shape hai |
|---|---|---|
| Tu haath se likhta hai `if income > 50000: approve()` | Algorithm ko 100,000 purane loan decisions dikhaye jaate hain, woh khud rule *derive* karta hai (numbers ki form mein, code nahi) | Dono cases mein goal same hai: input se output tak ek reliable rule chahiye |
| Output: source code se bana binary/JAR/container image | Output: training data se bana model file (weights) | Dono "compiled" outputs hain — insaan seedha nahi padh sakta, par machine use kar sakti hai |
| Build step: `docker build` | Training step: `python train.py` | Dono ek slow, occasional process hain jo ek reusable artifact banate hain |
| Same source se binary deterministic hota hai | Same data + code + random seed se model (mostly) deterministic hota hai | Reproducibility dono jagah important hai — warna debug kaise karega? |

**Toh model bas ek aur build artifact hai** — jaise `.jar` ya Docker image — bas uska "source code" data tha, hand-written logic nahi. Yeh ek line agar samajh gaya, MLOps ka aadha dar khatam.

## Training vs. Inference — yeh do terms sabse zaroori hain

Interview mein sabse zyada is pair pe confusion hoti hai. Isliye pehle first principles se socho: **koi bhi system jo "seekhta" hai, usme do alag phases honge — seekhne ka phase, aur seekhe hue ko use karne ka phase.** ML mein bhi bas yehi do phases hain, bas naam alag hain.

- **Training** = model *banane* ka process. Algorithm ko bahut saara purana data dikhaya jaata hai; woh apne internal numbers (parameters) tab tak adjust karta hai jab tak already-dekhe examples pe sahi answer na de. Yeh ek batch job hai — minutes, hours, ya weeks bhi lag sakte hain. Usually GPU chahiye hota hai.
- **Inference** = pehle se trained model ko *use* karke naye, kabhi na dekhe data pe prediction nikaalna. Yehi hai jo "production mein chal raha model" karta hai — fast (milliseconds), aur chhote models ke liye GPU bhi zaroori nahi.

DevOps comparison: training = `docker build` (slow, kabhi-kabhi hota hai, ek artifact banata hai). Inference = built container ko chalake request handle karna (fast, hamesha ho raha hai, artifact ko use karta hai).

```
   TRAINING (batch, slow, occasional)         INFERENCE (real-time, fast, constant)
   ─────────────────────────────────          ──────────────────────────────────
   historical data  ──▶  [algorithm]           new input  ──▶  [trained model]  ──▶  prediction
                            │                                        ▲
                            ▼                                        │
                      model file (artifact)  ───────────────────────┘
                      (build output jaisa)
```

## Vocabulary — cheezon ko naam do jo tu already jaanta hai

| ML term | Seedha matlab | DevOps analogy | Yeh naam kyun zaroori hai |
|---|---|---|---|
| **Dataset** | Purane examples ka bada table | Log file / DB table jise tu analytics ke liye query karta hai | Bina naam ke "training data" har jagah alag word se refer hota, confusion badhta |
| **Feature** | Ek input column jo prediction banane mein use hota hai (e.g., "customer age") | Config file ka field, ya function ka input parameter | "Feature" ek short, precise word hai instead of "input variable" baar baar bolne ke |
| **Label** | Purane example ka sahi jawab, training ke liye (e.g., "customer churn hua: yes/no") | Unit test ke assertion ka expected output | Bina label ke training hi nahi ho sakti — algorithm ko pata hi nahi chalega "sahi" kya tha |
| **Model parameters / weights** | Training se seekhe hue numbers | Compiled bytecode — insaan nahi padh sakta, par functional hai | Yeh differentiate karta hai "settings tu deta hai" vs "numbers model khud seekhta hai" |
| **Hyperparameters** | Settings jo *tu* training se pehle choose karta hai (e.g., kitni training passes karni hain) | Build flags / env variables jo build process control karte hain, code nahi | Confusion yahi hoti hai ki "parameter" aur "hyperparameter" alag cheez hain — table isliye separate rakha |
| **Prediction / inference output** | Naye input ke liye model ka output | Function call ka return value | — |
| **Ground truth** | Real, actual outcome (baad mein pata chalta hai, e.g., customer sach mein churn hua ya nahi) | Real production incident jo tere alert se match karta hai ya nahi | Yeh word baad ke files mein "monitoring" samjhne ke liye critical hai |

### Worked example: customer subscription cancel karega ya nahi, predict karna

- **Dataset**: pichhle 2 saal ke customer records.
- **Features** (inputs, columns): `days_since_signup`, `num_support_tickets`, `monthly_spend`, `logged_in_last_7_days`.
- **Label** (jawab, sirf purane customers ke liye pata hai): `churned` = `yes` ya `no`.
- **Training**: algorithm ko hazaron `(features, label)` pairs dikhaye jaate hain. Woh seekhta hai kaunse feature combinations `churned=yes` ke saath jaate hain.
- **Model**: result file jo roughly kehti hai, "agar `num_support_tickets` high hai aur `logged_in_last_7_days` false hai, toh `churned=yes` predict karo 82% confidence ke saath."
- **Inference**: ek naya customer signup karta hai. Tujhe abhi nahi pata woh churn karega ya nahi (koi label nahi hai — future hua hi nahi abhi). Uske current feature values model mein daalta hai aur prediction milta hai: `churn_probability = 0.82`.

Yehi pattern hai almost har ML use case ke peeche: fraud detection, recommendation engines, spam filters, churn prediction, image classification — sabka shape same hai, bas data alag hai.

## Toh seedha `if` statements kyun nahi likh sakte?

Kabhi-kabhi likh sakte ho, aur likhna bhi chahiye — ML hamesha sahi tool nahi hota. First-principles test yeh hai: **kya main is rule ko explicitly, cleanly likh sakta hoon?** Agar haan, toh ML mat use karo — woh cheaper hai build, debug, aur operate karna. ML tab use karo jab:

1. Rule itna complex ya subtle hai ki insaan haath se likh hi nahi sakta (e.g., "pixels mein face kaisa dikhta hai").
2. Rule *time ke saath badalta hai* aur tu chahta hai woh naye data se khud adapt ho.
3. Bahut saare historical examples hain lekin koi clean, explicit rule nahi jo inputs ko outputs se jodta ho.

Agar clean `if/else` rule likh sakta hai, wahi likh — interview mein "ML kab NOT use karna hai" pata hona ek strong signal hai.

## ML ke types jo MLOps job mein milenge (bas pehchanne layak)

Yeh banane nahi hain — pehchaanne hain ki tu kis type ka system operate kar raha hai.

- **Classification**: category predict karta hai (`spam` / `not spam`). Output ek label ya per-category probability hai.
- **Regression**: number predict karta hai (delivery time in minutes, house price).
- **Ranking / recommendation**: *order* predict karta hai (50 products ko is user ke liye rank karo).
- **Generative / LLMs**: text (ya image) andar, naya text (ya image) bahar. Covered in [`09_llmops-and-genai.md`](09_llmops-and-genai.md).

Infrastructure ke point of view se, pehli teen similar behave karti hain (chhota input → chhota output, fast inference, chhota model file). LLMs itne alag hain (bada model, mehenga inference, alag serving tools) ki unko apni file mil gayi.

## Quick self-check ✅

Agle file pe jaane se pehle, khud se poochh:

1. Training aur inference mein kya fark hai, aur kaunsa `docker build` jaisa hai?
2. "Feature" kya hai aur "label" kya hai, aur inme kya fark hai (hint: inference time pe label pata hota hai kya)?
3. Trained model ko build *artifact* kyun mana jaata hai?

Agar koi bhi shaky lage, "worked example" section wapas padh — wahi internalize karna hai.

**Next:** [`02_ml-lifecycle-and-artifacts.md`](02_ml-lifecycle-and-artifacts.md) — yeh pieces poore project lifecycle mein kaise fit hote hain, aur "reproducibility" ka matlab kya hota hai jab data bhi (sirf code nahi) involve ho.
