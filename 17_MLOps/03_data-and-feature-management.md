# 03 — Data aur Feature Management 📦

Files 01–02 assume hain. Is file ka goal: data versioning, feature stores, aur woh do bugs samajhna jo sabse zyada silent ML production failures cause karte hain — training-serving skew aur label leakage.

## DVC se data versioning

**Problem pehle samjho:** Git chhoti text files ke liye bana hai. Training dataset gigabytes ya terabytes ka ho sakta hai. Woh Git mein commit nahi kar sakta.

**Solution: DVC (Data Version Control).** Yeh Git jaisa kaam karta hai, bas data ke liye:

```bash
dvc add data/training_set.csv     # ek chhoti .dvc pointer file banata hai (symlink jaisi)
git add data/training_set.csv.dvc  # tu POINTER commit karta hai Git mein, data nahi
dvc push                           # actual data S3/GCS/Azure Blob pe upload hota hai
```

Baad mein, koi bhi kar sakta hai:

```bash
git checkout <commit>   # us commit ka code AUR pointer file milta hai
dvc pull                 # jo data woh pointer refer karta hai, wo download hota hai
```

DevOps analogy: yeh bilkul waisa hai jaise bade binaries ko artifact repository (Artifactory, S3) mein rakhna aur sirf manifest/checksum Git mein commit karna — same pattern jo tu bade Docker layers ya build caches ke liye use karta hai, bas ab datasets ke liye.

Bade scale pe DVC ka alternative: **Delta Lake** ya **Apache Iceberg** — S3/GCS ke upar table formats jo *time travel* support karte hain (table ko query karo jaise woh kisi specific past timestamp pe dikhti thi). Isse separate pointer-file system ke bina hi dataset versioning mil jaati hai.

## Feature store hai kya, aur exist kyun karta hai?

File 01 se yaad karo: **feature** ek input column hai jo model use karta hai (e.g., `num_support_tickets`). Ab first principles se socho: **agar 5 alag teams ko ek hi feature chahiye ("last 30 days ka average order value"), aur har team apna khud ka code likh le, toh kya hoga?** Do problems: duplicate compute waste hoga, aur zyada bura — **dono implementations ke values thode alag-alag aa sakte hain** subtle bugs ki wajah se.

Ek **feature store** ek centralized system hai jo feature ko ek baar compute karta hai aur har model ko serve karta hai jise woh chahiye. Iske do halves hain:

- **Offline store** — bada, sasta, slow-to-query storage (S3, BigQuery, Parquet files) jisme poora historical feature data hota hai. **Training** ke time use hota hai, jahan lakhon rows ek saath chahiye aur millisecond latency ki fikar nahi.
- **Online store** — chhota, fast, low-latency key-value storage (Redis, DynamoDB) jisme sirf *current* feature value hota hai har entity ke liye (e.g., har customer). **Inference** ke time use hota hai, jahan ek customer ka feature <10ms mein chahiye.

```
                     ┌─────────────────────┐
   raw data  ──────▶ │  feature pipeline    │  (feature ko EK BAAR compute karta hai)
                     └──────────┬──────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                     ▼
     OFFLINE STORE (S3/BigQuery)           ONLINE STORE (Redis/DynamoDB)
     use karta hai: TRAINING                use karta hai: INFERENCE (real-time)
     lakhon rows, batch reads               ek entity, <10ms reads
```

Popular tools: **Feast** (open source), **Tecton** (managed).

DevOps analogy: feature store bilkul caching layer (DB ke aage Redis) plus shared library jaisa hai — exist isliye karta hai taaki har consumer *same, correct* value padhe, na ki paanch teams same computation ko subtle bugs ke saath reimplement karein.

## Training-serving skew (ML ka #1 silent bug)

**Training-serving skew** tab hota hai jab training time pe compute hua feature value, inference time pe compute hue feature value se match nahi karta — jabki dono "same feature" maane jaate hain. Model ek distribution pe train hua tha, ab use dusra distribution feed ho raha hai — woh bina kisi error, crash, ya alert ke bas galat predictions dega. Yehi sabse dangerous hai — **kuch bhi crash nahi hota, sab kuch "healthy" dikhta hai.**

Common causes:

- Do alag code paths same feature compute karte hain — ek Python training script mein, ek Java serving service mein — aur time ke saath drift ho jaate hain.
- Feature ek aggregate use karta hai (e.g., "last 30 days ka average") jo batch job mein easy hai lekin real-time mein correctly compute karna mushkil — toh online version ek rough approximation ban jaata hai.
- Online store mein stale data hai kyunki use refresh karne wala pipeline (materialization) delayed ya broken hai.

**Fix:** har feature ko ek hi feature store code path se compute karo, jo training aur serving dono use karein. Yehi poora reason hai feature stores exist karne ka — "central storage" ke liye nahi, is bug class ko root se khatam karne ke liye.

DevOps analogy: yeh "works on my machine" ka ML version hai, jo dev aur prod ke alag config ki wajah se hota hai — bas yahan silent hai, kyunki koi error nahi aata, sirf gradually predictions kharab hoti jaati hain.

## Point-in-time joins

Training dataset banate waqt, sirf woh feature values use karni chahiye **jo historical prediction ke moment pe exist karti thi**, feature ki current value nahi. Warna future ka information training mein leak ho jaata hai (label leakage, neeche dekho).

Example: tu 6 mahine purane transactions pe fraud model train kar raha hai. Agar tu customer ka *current* "total lifetime fraud flags" count join karta hai (jisme us transaction ke *baad* discover hua fraud bhi included hai), model cheat kar raha hai — woh answer dekh raha hai. Point-in-time join yeh ensure karta hai ki feature value *us historical timestamp* pe jaisi thi waisi join ho, aaj wali nahi. Feast jaise feature stores yeh automatically handle karte hain — haath se karna bahut easy hai galat karna.

## Label leakage

**Label leakage** tab hoti hai jab koi feature accidentally aisi information contain kare jo label se derive hui ho (ya highly correlated ho) — information jo real world mein prediction time pe actually available hi nahi hoti.

Example: insurance claim approve hoga ya nahi predict kar rahe ho, aur ek feature `claim_approval_timestamp` hai (sirf tab populate hota hai jab claim *approve* ho chuka ho). Model ek "perfect" shortcut seekh leta hai jo real world mein exist hi nahi karta, validation mein zabardast accuracy deta hai, phir production mein completely fail ho jaata hai kyunki naye, unapproved claims ke liye woh field empty hai.

**Prevention:** strict temporal ordering enforce karo — feature sirf us data se banna chahiye jo genuinely prediction se *pehle* exist karta tha. Yeh bilkul waisi discipline hai jaise unit test mein aisa data assert nahi karte jo tere code ko abhi mila hi nahi.

## Quick self-check ✅

1. DVC konsa problem solve karta hai jo sirf Git nahi kar sakta?
2. Feature store ke offline store aur online store mein kya farak hai, aur kaunsa training serve karta hai aur kaunsa inference?
3. Training-serving skew apne shabdon mein define karo aur ek example do.
4. Point-in-time join kya hai, aur usko skip karne se label leakage kaise hoti hai?

**Next:** [`04_experiment-tracking-and-registry.md`](04_experiment-tracking-and-registry.md) — training runs kaise track hote hain, aur trained models "abhi-abhi trained" se "production ke liye approved" tak kaise pahunchte hain.
