# 09 — LLMOps aur GenAI 🤖

Files 01–08 assume hain — un sab mein jo likha hai woh abhi bhi apply hota hai. Yeh file cover karti hai *extra* kya sach hai jab model ek Large Language Model (LLM) ho, jaise GPT-4, Claude, ya Llama.

## LLMs mein operationally actually alag kya hai

Traditional ML model (file 01 ka churn example): chhota model, chhota input, chhota output, cheap aur fast inference, tu khud training pipeline own karta hai. Ek LLM: huge model (billions of parameters), tu usually khud train *nahi* karta (ya toh API call karta hai ya ek open-weight model self-host karta hai), input/output variable-length text hai, aur inference comparatively mehenga aur slow hai. Isse operational focus "apna model train karo" se shift hokar "model ko calls orchestrate karo, use kya feed karta hai manage karo, aur cost control karo" ban jaata hai.

## Prompt versioning

Kyunki tu usually model train nahi kar raha, tera primary "code" ban jaata hai **prompt** — woh instructions aur context jo tu LLM ko bhejta hai. First principle se socho: **agar prompt hi tera "logic" hai, toh usko wahi discipline nahi chahiye jo kisi bhi production code ko milti hai?** Bilkul chahiye:

- Version-controlled (Git, ya ek dedicated prompt registry).
- Changes ship hone se pehle test hone chahiye (naya prompt known inputs/outputs ke ek benchmark set pe regress toh nahi karta?).
- Gradually rollout hona chahiye (naye prompt version ko waise hi canary karo jaise naye model ko karega — file 06 ki strategies abhi bhi apply hoti hain).

DevOps analogy: prompt LLMOps mein "source code" ke sabse kareeb ki cheez hai, aur prompt registry model registry (file 04) ke sabse kareeb — same lifecycle stages (draft → staging → production), same change review ki zaroorat.

## RAG (Retrieval-Augmented Generation)

**Problem:** ek LLM sirf wahi jaanta hai jo uske training data mein tha (jiski ek cutoff date hai) aur tere private/internal data ke baare mein sawaal answer nahi kar sakta. **RAG** yeh solve karta hai — request time pe relevant documents retrieve karke unhe prompt mein context ki tarah stuff karke.

```
  user ka sawaal
       │
       ▼
  1. sawaal ko embed karo (text ko vector mein badlo)
       │
       ▼
  2. vector DB similarity search (ANN — approximate nearest neighbor)
       │     tere documents ke sabse relevant chunks dhoondta hai
       ▼
  3. rerank (optional) — ek chhota, zyada precise model top
       candidates ko relevance ke hisaab se re-order karta hai
       │
       ▼
  4. prompt assemble karo = sawaal + retrieved chunks
       │
       ▼
  5. LLM ko bhejo  ──▶  jawaab, TERE data mein grounded
```

Pipeline stages, seedhe shabdon mein:

1. **Ingestion & chunking** — documents ko chhote pieces (chunks) mein todo, kyunki poora document ek prompt mein fit nahi hota.
2. **Embedding** — har chunk ko (aur baad mein, user ke sawaal ko) ek vector mein convert karo (numbers ki list jo meaning represent karti hai) ek embedding model use karke.
3. **Vector database** — un vectors ko store karta hai aur fast similarity search support karta hai. Tools: **Pinecone**, **Weaviate**, **Qdrant**, **pgvector** (Postgres extension).
4. **Retrieval** — sawaal ke vector ko dekhke, sabse similar document chunks dhoondo.
5. **Reranking** (optional par common) — ek zyada precise (aur slower) model top N retrieved chunks ko re-score karta hai, kyunki fast vector search step speed ke liye thodi accuracy trade karta hai.
6. **Generation** — LLM retrieved chunks ko context ki tarah use karke jawaab deta hai.

DevOps analogy: vector DB ko ek specialized search index samajh (jaise Elasticsearch), aur RAG ko cache-aside pattern ka ML equivalent — poora knowledge model mein bake karne ke bajaye (mehenga, stale, retraining chahiye), tu request time pe usko lookup karta hai aur fresh model ko de deta hai.

## RAG quality evaluate karna: RAGAS metrics

Traditional accuracy metrics directly apply nahi hote "kya LLM ne achha jawaab diya" pe. RAGAS ek common framework hai in metrics ke saath:

- **Faithfulness** — kya jawaab sirf woh facts use karta hai jo retrieved context mein actually present hain (matlab, hallucinate to *nahi* kar raha)?
- **Answer relevancy** — kya jawaab actually pooche gaye sawaal ko address karta hai?
- **Context precision** — jitne chunks retrieve hue, unme se kitne actually relevant/useful the?
- **Context recall** — kya retrieval ne *sab* relevant chunks fetch kiye, ya important wale miss ho gaye?

Yeh tere evaluation gates (file 05 ka concept) ban jaate hain RAG pipeline ke liye — tu ek prompt ya retrieval-pipeline change ko ship hone se rokega agar woh faithfulness regress kare, bilkul waise jaise tu ek code change ko rokega jo test coverage regress kare.

## LLMs ko efficiently serve karna: vLLM aur PagedAttention

Ek LLM ko naively serve karna (model load karo, ek time pe ek request chalao) bahut zyada GPU memory aur throughput waste karta hai. **vLLM** ek serving engine hai jo specifically isko fix karne ke liye bana hai:

- **KV cache**: generation ke dauraan, ek LLM intermediate computations ("KV cache") ko per-request cache karta hai taaki har naye token ke liye kaam dobara na kare. Yeh cache bada hota hai aur uska size per-request vary karta hai (depend karta hai conversation kitni lambi hai).
- **PagedAttention**: us KV cache ko chhote, non-contiguous memory "pages" mein manage karta hai (wahi idea jo OS virtual memory paging ka hai), har request ke liye ek bada contiguous memory block ki zaroorat ke bajaye. Isse memory fragmentation khatam hoti hai aur ek hi GPU pe kahin zyada concurrent requests fit ho paate hain.
- **Continuous batching**: requests ka poora batch aane ka wait karne ke bajaye (static batching), naye requests running batch mein turant add ho jaate hain jaise hi ek GPU "slot" free hota hai — variable/bursty traffic ke under GPU utilization dramatically improve hoti hai.

DevOps analogy: PagedAttention literally OS-level paged virtual memory ka idea borrow karke GPU memory fragmentation problem solve karta hai. Continuous batching ML-serving ka equivalent hai ek fixed-batch-window queue consumer se ek streaming, hamesha-draining consumer pe move karne ka.

## Model routing aur semantic caching (cost control)

LLM inference per-token billed hota hai aur ek GenAI system mein dominant cost driver hai — cost optimization yahan file 08 ke GPU-utilization framing se alag dikhta hai, kyunki tu aksar hourly instance price ke bajaye ek per-token API price pay kar raha hota hai.

- **Model routing**: incoming queries ko complexity se classify karo; simple queries ko chhote/sasta model pe bhejo, complex queries ko bade/mehenge model pe. Same idea jo traffic ko load ke hisaab se alag instance sizes pe route karne ki hai, bas yahan "instance size" model size hai.
- **Semantic caching**: LLM responses ko *meaning* se key karke cache karo, exact text match se nahi — agar naya query pehle answer hue kisi query se semantically similar hai (embedding similarity se), cached response serve karo LLM ko dobara call karne ke bajaye. Yeh ek HTTP response cache ka advanced version hai, jahan "same URL" ki jagah "similar meaning" hai.

## Quick self-check ✅

1. Prompt registry file 04 ke model registry jaisa role kyun play karta hai?
2. RAG pipeline ke 5 stages order mein walk through kar.
3. RAGAS mein "faithfulness" kya measure karta hai, aur normal accuracy metrics isko kyun capture nahi kar sakte?
4. Plain English mein, PagedAttention kaunsi problem solve karta hai, aur woh kaunse OS concept se borrow karta hai?
5. Cost-control techniques ki tarah model routing aur semantic caching mein kya farak hai?

**Next:** [`interview.md`](interview.md) — sabhi nau topics condensed, Easy / Medium / Hard interview questions aur answers mein.
