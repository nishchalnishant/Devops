# MLOps — Interview Prep 🎯

ML mein naya hai? Pehle [`00_start-here.md`](00_start-here.md) se [`09_llmops-and-genai.md`](09_llmops-and-genai.md) tak padh — yeh har concept ko scratch se build karte hain, sirf DevOps knowledge assume karke. Yeh file uska condensed Q&A companion hai.

```
MLOps — Topic Map (gradual order)
├── 01 ML Basics             — model, training vs inference, features/labels
├── 02 Lifecycle & Artifacts — code+data+model, reproducibility, maturity levels
├── 03 Data & Features        — DVC, feature stores, training-serving skew, leakage
├── 04 Tracking & Registry    — experiment tracking, hyperparameters, model registry
├── 05 Pipelines              — CI/CT/CD/CM, orchestration, evaluation gates
├── 06 Deployment & Serving   — batch/online/async, shadow/canary/A-B/blue-green
├── 07 Monitoring & Drift     — data drift vs concept drift, detection, alerting
├── 08 Platform/GPU/Cost      — k8s GPU scheduling, Spot training, distributed training
└── 09 LLMOps & GenAI         — prompts, RAG, vector DBs, vLLM, cost per token
```

### First Principles

- ML systems mein teen artifacts hote hain (code, data, model) software ke ek (code) ke against — teeno version hone chahiye, warna system reproducible hi nahi hai.
- Ek model `200 OK` return kar sakta hai 20ms mein aur phir bhi galat ho sakta hai — infra health aur model quality do alag monitoring problems hain.
- Models apne aap degrade hote hain, bina kisi code change ke, kyunki duniya jisse data represent karta hai woh khud badalti rehti hai (drift) — isi wajah se Continuous Training exist karta hai.
- Feature stores, evaluation gates, aur staged rollouts — yeh sab ek hi root problem solve karte hain: "model ne kya seekha" aur "production mein woh kya dekh raha hai" ke beech ka gap chupke se badhne se roko.
- LLMOps, MLOps hi hai ek aise system pe applied jahan tu usually training khud nahi karta — operational focus training pipelines se hatke prompts, retrieval, aur cost-per-token pe shift ho jaata hai.

## Easy

**1. MLOps kya hai?**

MLOps DevOps principles — automation, versioning, testing, monitoring — ko machine learning systems pe apply karta hai. Yeh poora lifecycle cover karta hai: data preparation, training, evaluation, deployment, aur monitoring. Goal hai reliable, reproducible, continuously deliverable ML — na ki one-off notebooks.

**2. Plain terms mein, model kya hai?**

Ek file jisme parameters (numbers) hote hain jo historical data pe ek algorithm chalake seekhe gaye hain, kisi developer ne haath se nahi likhe. Yeh ek build artifact hai, jaise ek compiled binary — bas iska "source" data hai, code nahi. Dekh [`01`](01_ml-basics-for-devops.md).

**3. Training aur inference mein kya farak hai?**

Training model banati hai: ek slow, batch, usually GPU-heavy process jo historical data se parameters seekhta hai (`docker build` jaisa). Inference trained model use karke naye data pe predict karta hai: fast, constant, latency-sensitive (built container chalake request handle karne jaisa).

**4. Feature kya hai, aur label kya hai?**

Feature ek input column hai jo prediction banane ke liye use hota hai (e.g., `customer_age`). Label ek past example ka sahi jawaab hai, training ke dauraan use hota hai (e.g., `churned: yes/no`) — inference time pe tere paas label kabhi nahi hota; wahi toh tu predict karne ki koshish kar raha hai.

**5. ML systems ko ek ki jagah teen versioned artifacts kyun chahiye?**

Code, data, aur model — teeno outcome affect karte hain. Same Git commit checkout karna normal software mein behavior reproduce kar deta hai; ML mein tujhe exact same training data aur hyperparameters bhi chahiye same model wapas paane ke liye — warna tu na ek bekaar model debug kar sakta hai na ek prediction audit kar sakta hai.

**6. DVC kya hai aur yeh kaunsi problem solve karta hai?**

Data Version Control, Git-style versioning ko bade datasets tak extend karta hai. Ek chhota pointer file Git mein store hoti hai jabki actual data S3/GCS/Azure Blob mein rehta hai — `git checkout` + `dvc pull` exact wahi dataset reproduce kar deta hai jo ek diye gaye commit ke liye use hua tha, same pattern jo bade binaries ke liye ek artifact repository mein use hota hai.

**7. Feature store kya hai?**

Ek centralized system jo ek feature ko ek baar compute karta hai aur har us model ko serve karta hai jisko uski zaroorat hai, do parts mein split: **offline store** (S3/BigQuery, training ke liye — high volume, latency matter nahi karti) aur **online store** (Redis/DynamoDB, inference ke liye — ek entity, sub-10ms). Yeh exist karta hai duplicated, inconsistent feature computation ko teams ke across rokne ke liye.

**8. Training-serving skew kya hai?**

Jab training time pe ek feature ki value inference time ki value se alag hoti hai — e.g., do alag code paths "same" feature ko thoda differently compute karte hain. Yeh silently bekaar predictions cause karta hai, koi error ya alert nahi aata. Fix: training aur serving dono ko ek hi feature store code path se route karo.

**9. Model registry kya hai?**

Trained models ka ek versioned catalog, metadata (metrics, dataset version, code commit) ke saath, aur ek staging workflow: `None → Staging → Production → Archived`. Ek container image registry jaisa environment-promotion tags ke saath, bas promotion ke liye sirf integration tests nahi, accuracy/fairness checks pass karna padta hai.

**10. Experiment tracking kya hai, aur yeh kyun matter karta hai?**

Yeh har training run ke inputs (hyperparameters, dataset version, code commit, seed) aur outputs (metrics, artifacts) log karta hai, taaki tu runs compare kar sake, best wala reproduce kar sake, aur audit kar sake ki kya try kiya gaya tha. Iske bina, tuning untracked trial-and-error ban jaati hai jo team scale pe nahi tikti. Tools: MLflow, Weights & Biases.

**11. Parameter aur hyperparameter mein kya farak hai?**

Parameters (weights) training ke dauraan automatically seekhe jaate hain — tu inhe kabhi haath se set nahi karta; yehi "model" hai. Hyperparameters (learning rate, batch size, epochs) training shuru hone se pehle ek insaan set karta hai aur control karte hain ki training *kaise* hoti hai — build flags jaisa jo ek build process ko configure karte hain.

**12. MLOps mein CI, CT, aur CD mein kya farak hai?**

CI code test karta hai, pipelines lint karta hai, har commit pe data schemas validate karta hai. CT (Continuous Training — normal software ke against naya) drift, schedule, ya naye data volume se trigger hokar model ko automatically retrain karta hai. CD naya model version deploy karta hai agar woh evaluation gates pass kare.

**13. Batch, online, aur async inference mein kya farak hai?**

Batch: ek bade dataset ko schedule pe score karo, throughput matter karta hai, latency nahi (nightly churn scoring). Online: synchronous HTTP/gRPC API, latency-critical, usually <100ms (checkout pe fraud check). Async: client ek job submit karta hai, poll karta hai ya baad mein callback milta hai, use hota hai jab inference synchronous response ke liye bahut slow ho (video analysis, bade LLM generations).

**14. Ek ML model ke liye shadow deployment kya hai?**

Challenger model champion ke saath parallel mein wahi live requests score karta hai, lekin uske predictions log hote hain, users ko kabhi nahi dikhaye jaate. Yeh real-world behavior aur latency validate karta hai zero user-facing risk ke saath, isse pehle ki koi actual traffic usko route ho.

**15. Data drift kya hai?**

Input features ki distribution training aur serving time ke beech badal jaati hai, jabki input-output relationship khud same rehta hai — e.g., inflation ke baad income distributions shift hote hain, lekin "higher income → lower default risk" abhi bhi hold karta hai. Feature distributions compare karke detect hota hai (PSI, KS test) ek reference window aur current traffic ke beech.

## Medium

**16. Concept drift kya hai, aur yeh data drift se kaise alag hai?**

Data drift = inputs badal gaye (sawaal badal gaye). Concept drift = inputs aur outputs ke beech ka relationship badal gaya (jawaab badal gaye) — e.g., ek fraud pattern jiska matlab pehle "safe" tha ab "fraud" hai kyunki tactics evolve hue. Concept drift ko zyada same-kism ke data se fix nahi kiya ja sakta; ground-truth mapping khud ab alag hai.

**17. Point-in-time join kya hai, aur ise skip karne se kya problem hoti hai?**

Training dataset banate waqt, feature values ko unke *historical prediction ke exact moment* ki value ke hisaab se join karna zaroori hai, unki current value ke hisaab se nahi — warna tu future ki information training mein leak kar deta hai. Example: customer ka current total fraud-flag count join karna (jisme woh fraud bhi shamil hai jo transaction ke baad discover hua) model ko ek shortcut sikha deta hai jo real world mein exist hi nahi karta.

**18. Label leakage kya hai? Ek example de.**

Ek feature accidentally aisi information contain karta hai jo label se derived ya correlated hai, jo prediction time pe genuinely available nahi hoti. Example: insurance claim approval predict karna `claim_approval_timestamp` use karke, jo sirf approve hone ke baad populate hota hai — model validation mein zabardast dikhta hai, phir production mein completely fail hota hai jahan naye claims ke liye woh field empty hoti hai.

**19. Ek typical CT (Continuous Training) pipeline walk through kar.**

Trigger (schedule, drift detected, data volume, KPI drop) → incoming data validate karo (schema, nulls, ranges — Great Expectations/TFDV) → features build karo → challenger train karo → champion ke recorded metrics ke against evaluate karo (gate: accuracy regression threshold, fairness checks, latency/size checks) → agar pass ho jaaye, `Staging` mein register karo, seedha `Production` mein nahi. Kubeflow Pipelines, SageMaker Pipelines, ya Airflow se ek containerized steps ke DAG ki tarah orchestrate hota hai.

**20. Evaluation gate kya hai aur typically promotion kya block karta hai?**

Ek test suite ka ML equivalent jo ek bekaar build ko merge hone se rokta hai. Typical gates: accuracy/precision/recall current production ("champion") model ke against ek threshold se zyada regress nahi honi chahiye; fairness/bias checks; latency ya model-size checks (ek zyada accurate lekin bahut slow model fail hota hai); training set pe hi data quality checks.

**21. Naye model ke liye shadow → canary → A/B → blue/green rollout sequence explain kar.**

Shadow (0% user-visible, kya yeh sahi se chalta hai aur expected latency match karta hai) → canary (~5% live traffic, kya yeh real traffic survive karta hai) → A/B test (50/50 split, statistically significant business-metric comparison — kya yeh *provably* behtar hai) → blue/green swap se full rollout, instant rollback ready ke saath. Har stage zyada user exposure cost karta hai lekin zyada confidence bhi prove karta hai; stages skip karna hi "wrong predictions with 200 OK" incidents ki wajah banta hai.

**22. Zyadatar production models ke liye tu model accuracy ko directly near-real-time mein monitor kyun nahi kar sakta?**

Ground truth labels aksar delayed hote hain — tujhe shayad ek saal tak pata na chale ki loan actually default hua ya nahi. Teams proxy signals pe rely karti hain: confidence/probability distribution shifts, output entropy jumps, input drift (ek leading indicator), aur proxy business metrics (e.g., CTR, turant available, chahe "true satisfaction" na pata ho).

**23. PSI (Population Stability Index) kis liye use hota hai, aur ise kaise padhte hain?**

Ek single number jo summarize karta hai ki ek feature ki distribution ek reference window aur current window ke beech kitni shift hui. Rough thresholds: `<0.1` koi significant shift nahi, `0.1–0.25` moderate (watch karo), `>0.25` significant (investigate/retrain). KS tests (continuous features) aur chi-squared tests (categorical features) ke saath use hota hai.

**24. Kubernetes mein GPU scheduling ke liye taints aur tolerations kaise use hote hain, aur kyun?**

GPU nodes taint kiye jaate hain (e.g., `nvidia.com/gpu=true:NoSchedule`) taaki sirf woh pods jo explicitly taint ko tolerate karte hain aur `nvidia.com/gpu` resource request karte hain wahan land karein — isse regular CPU workloads accidentally expensive, scarce GPU nodes consume nahi kar paate. NVIDIA device plugin hi hai jo `nvidia.com/gpu` ko ek schedulable resource banata hai.

**25. Spot/preemptible instances training ke liye commonly use hote hain lekin serving ke liye nahi, kyun?**

Training jobs fault-tolerant hote hain agar checkpointed ho — model state ko S3 mein har N steps pe save karo, aur ek interrupted job bas last checkpoint se resume ho jaata hai, isse 60-90% Spot discount basically free savings ban jaata hai. Serving, iske ulta, stable capacity maangta hai kyunki ek interrupted inference pod ka matlab hai dropped user-facing requests — same risk calculus jo kisi bhi latency-sensitive production service ke liye ek interruptible batch job ke against hota hai.

**26. RAG pipeline kya hai? Uske stages order mein bata.**

Retrieval-Augmented Generation ek LLM ke jawaab ko tere apne data mein request time pe ground karta hai, sirf training-time knowledge pe rely karne ke bajaye. Stages: ingestion & chunking (documents ko pieces mein todo) → embedding (chunks aur query ko vectors mein convert karo) → vector DB similarity search (sabse relevant chunks retrieve karo) → reranking (optional, top candidates ka zyada precise re-scoring) → prompt assembly (sawaal + retrieved context) → generation (LLM grounded jawaab produce karta hai).

**27. RAGAS metrics kya hain, aur inki zaroorat normal accuracy ke bajaye kyun hai?**

Traditional accuracy "kya yeh ek achha LLM answer tha" pe apply nahi hoti. RAGAS metrics mein shamil hain faithfulness (kya jawaab sirf retrieved context mein present facts use karta hai — matlab, no hallucination), answer relevancy (kya yeh sawaal ko address karta hai), context precision (kya retrieved chunks actually relevant the), aur context recall (kya retrieval ne important chunks miss kiye). Yeh ek RAG pipeline ke evaluation gates ki tarah serve karte hain, wahi role jo file 05 ke gates normal model ke liye play karte hain.

## Hard

**28. Ek mid-size organization ke liye ek ML platform architecture design kar. Har layer walk through kar.**

- **Data layer:** Delta Lake ya Iceberg S3/GCS pe versioned training data ke liye; ingestion pe validation ke liye Great Expectations.
- **Feature layer:** Feast ya Tecton; offline store S3/BigQuery pe, online store Redis/DynamoDB pe; ek scheduled materialization job online store ko fresh rakhta hai.
- **Training layer:** orchestration ke liye Kubeflow Pipelines ya SageMaker Pipelines; experiment tracking aur model registry ke liye MLflow; ek GPU node pool (Karpenter-managed) jo idle hone pe zero tak scale ho.
- **Serving layer:** standard models ke liye KServe; LLMs ke liye vLLM; GPU-accelerated batch inference ke liye Triton.
- **Monitoring layer:** drift detection ke liye Evidently AI; latency/throughput ke liye Prometheus; model-quality metrics ke custom dashboards jo CT triggers mein feed back hote hain.

**29. Ek model ki accuracy raatों-raat 10% gir gayi, bina kisi code deploy ke. Apni diagnosis walk through kar.**

Pehle infra ko model quality se separate kar: latency/error-rate dashboards check kar — agar woh clean hain, toh yeh infra incident nahi hai. Current input feature distributions ko training reference window ke against compare kar (PSI/KS test) data drift check karne ke liye — e.g., ek feature jo pehle 0-1 range mein tha ab 0.5 pe cluster ho raha hai, ya ek categorical feature mein ek naya unseen value aa gaya hai. Agar input distributions stable lagte hain, toh concept drift ya ek upstream data pipeline bug suspect kar (ek source table ka schema badal gaya, ek join silently rows drop karne laga). Yeh bhi check kar ki kya kisi recent, unrelated deploy ne *serving* code path (model nahi) mein training-serving skew introduce kiya hai jisne feature compute hone ka tareeka badal diya.

**30. GPU pods `Pending` mein stuck hain. Tu kya check karega, aur kis order mein?**

1. `kubectl describe pod` — pehle scheduling failure reason check kar.
2. Node capacity: kya `nvidia.com/gpu` resource wala koi available node free hai, aur kya pod isko correctly request/limit kar raha hai?
3. Taints/tolerations: kya pod GPU node ke taint ko tolerate karta hai?
4. Cluster autoscaler/Karpenter: kya yeh naye GPU nodes provision karne ke liye configured hai, aur kya yeh cloud provider quota limit hit kar raha hai (GPU quotas commonly actual blocker hote hain)?
5. NVIDIA device plugin: kya yeh GPU nodes pe running aur healthy hai — iske bina, `nvidia.com/gpu` ek schedulable resource hi nahi hai, chahe physical GPU present ho.

**31. Ek fraud-detection model, jo automatically retrain hota hai (Level 2 / full CT), uske liye ek safe rollout process kaise design karega?**

CT trigger (drift threshold ya schedule) aur pipeline ko evaluation gates tak automate kar, lekin ek high-stakes model class ke liye final promotion step pe human-in-the-loop (ya ek stricter automated gate) rakh — full auto-promotion fraud ke liye zyada risky hai, kisi recommendation model ke against, kyunki false negatives ka direct financial cost hota hai. Concretely: CT pipeline challenger train karta hai → evaluation gate champion ke against precision/recall compare karta hai ek tight regression threshold ke saath, plus ek fairness check → sirf `Staging` tak auto-promote → live traffic ke against mandatory shadow period → chhote percentage pe canary, automated rollback ke saath agar fraud-catch-rate ya false-positive-rate threshold se zyada regress kare → tabhi full promotion ke eligible. Model registry pichle "champion" ko poore time instant-rollback target ki tarah retain karta hai.

**32. PagedAttention aur continuous batching explain kar, aur yeh LLM serving cost ke liye kyun matter karte hain.**

Ek LLM generation ke dauraan per-token intermediate computation (KV cache) cache karta hai taaki har naye token ke liye kaam dobara na kare; is cache ka size per-request vary karta hai aur conversation badhne ke saath grow karta hai. Naive serving har request ke liye is cache ke liye ek bada contiguous memory block allocate karta hai, jo GPU memory ko fragment karta hai aur capacity waste karta hai. PagedAttention KV cache ko chhote, non-contiguous pages mein manage karta hai — OS virtual-memory paging ka idea borrow karke — fragmentation khatam karta hai aur ek hi GPU pe kahin zyada concurrent requests fit karne deta hai. Continuous batching naye requests ko running batch mein turant add kar deta hai jaise hi ek GPU slot free hota hai, ek fixed batch window ka wait karne ke bajaye, bursty traffic ke under GPU utilization high rakhta hai. Dono milke wahi main wajah hain ki vLLM naive serving setup se dramatically zyada throughput per GPU achieve karta hai — directly cost-per-token kam karta hai.

**33. LLM cost control karne ke liye model routing kab use karega vs semantic caching, aur kya dono use kar sakta hai?**

Model routing per-request cost address karta hai — query complexity ko model size se match karke — ek classifier simple queries ko chhote/sasta model pe bhejta hai aur complex queries ko sirf bade/mehenge model pe route karta hai, average cost per request kam karta hai. Semantic caching *redundant* requests address karta hai — agar ek naya query embedding-similar hai kisi pehle answer hue query se, cached response serve karo kisi bhi LLM ko call kiye bina, us request ke liye cost completely eliminate ho jaata hai. Yeh dono achhe se compose hote hain: pehle semantic cache check karo (sabse sasta path), aur model routing ko sirf cache misses ke liye invoke karo.

**34. Tera RAG system confidently galat jawaab de raha hai (hallucinating) jabki retrieval sahi lag raha hai. Failure ko kaise isolate karega?**

Pipeline ko stages mein todo aur har ek ko independently evaluate karo RAGAS-style metrics use karke, final answers ko eyeball karne ke bajaye. Pehle context precision/recall check kar — agar retrieval irrelevant ya incomplete chunks fetch kar raha hai, toh yeh ek retrieval-tuning problem hai (embedding model quality, chunk size, reranker), generation problem nahi. Agar retrieved context verified achha hai (high precision/recall) lekin faithfulness abhi bhi low hai, toh issue generation mein hai — LLM provided context ko ignore ya contradict kar raha hai, jo usually ek prompt-engineering fix maangta hai (context sirf use karne ki zyada explicit instruction, kam temperature), retrieval fix nahi. Ise ek opaque "RAG system bekaar hai" problem ki tarah treat karna, retrieval vs generation isolate karne ke bajaye, sabse common mistake hai yahan.

**35. Ek naye LLM prompt version ko production mein promote karne ke liye evaluation gate design kar. Kya promotion ko block karega?**

Representative queries ka ek benchmark set maintain kar, known-good expected answers ya graded rubrics ke saath. Har prompt change pe, benchmark ke against RAGAS metrics (faithfulness, answer relevancy, context precision/recall) chalao aur current production prompt ke baseline scores se compare karo — kisi bhi regression pe promotion block karo jo ek chhoti tolerance se zyada ho, wahi regression-threshold pattern jo traditional model accuracy gates ke liye use hota hai. Cost aur latency pe bhi gate laga (ek prompt change jo bahut saare extra context tokens add karta hai woh cost-per-token aur response time regress kar sakta hai chahe quality improve ho), aur safety/policy checks pe bhi agar applicable ho. Ise ek model change ki tarah shadow → canary → A/B sequence se rollout kar, kyunki prompt behavior real traffic pe aise degrade ho sakta hai jo ek static benchmark catch nahi karega.
