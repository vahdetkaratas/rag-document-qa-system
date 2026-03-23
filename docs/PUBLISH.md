# GitHub and Deployment

## What to add to the repo

| Location | Note |
|----------|------|
| `src/`, `tests/`, `notebooks/` | Code and notebooks |
| `data/raw_docs/`, `data/eval/` | Sample docs and eval CSV |
| `requirements.txt`, `.env.example`, `.gitignore` | |
| `docs/` | Design, usage (this file included) |
| `reports/figures/` | Architecture (Mermaid) |

**Do not commit:** `.env`, `.venv/`, large `artifacts/embeddings/*.npy` and `artifacts/faiss_index/*.faiss` (optional `.gitignore`; regenerate with pipeline after clone).

---

## Deploying the API (summary)

Per PDR: not full-stack on Vercel; use **Render / Railway / Fly.io / HF Spaces** or **local demo + video**.

1. **LLM (choose one):**
   - **OpenAI (paid):** Set `OPENAI_API_KEY` in the deploy environment.
   - **Free / no key:** Use **Ollama** on the same machine or a separate LLM server. Set `OPENAI_API_BASE=http://localhost:11434/v1` (or your Ollama server URL) and `OPENAI_MODEL=llama3.2`. No API key needed; see `.env.example`.
2. **Abuse protection (recommended when using OpenAI):** Set `RAG_API_KEY` so only your clients can call `/ask`; set `API_RATE_LIMIT` (e.g. `30/minute`) to cap requests per IP or per key. Optionally set `RETRIEVAL_MIN_SCORE` so weak retrieval does not trigger an LLM call. See `.env.example`. **Where to enter the key:** **Server** — in `.env` or the host’s environment (e.g. `RAG_API_KEY=your-secret`). **Client** — send it in each request: header `X-RAG-API-Key: your-secret` or `Authorization: Bearer your-secret`.
3. Optionally set `CORS_ORIGINS` as needed.
4. **Start:** `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`  
   **Docker:** `docker build -t rag-qa .` (after indexing locally so `artifacts/` exists), then `docker run -p 8000:8000 --env-file .env rag-qa`. See **README.md** (VPS deployment notes).
5. **Add indexing to build** (if no persistent disk):  
   `python -m src.ingestion.run_extraction && python -m src.ingestion.run_chunking && python -c "from src.pipeline.indexing_pipeline import run_indexing_pipeline; run_indexing_pipeline()"`  
   (First build may be slow due to model download.)

Streamlit as a separate service or Streamlit Cloud; local + screen recording is enough for a demo.

**Cost summary (LLM):** Either you **pay for the OpenAI API** (usage-based), or you **run Ollama**. Ollama is free on your own machine (local demo); if you want the app and Ollama online 24/7, you pay for a server (Render, Railway, VPS) to host both the RAG backend and Ollama. So: **pay for API (OpenAI) or pay for a host (Ollama 24/7)**—unless you run everything locally, in which case Ollama is free.

**Which is cheaper?** For **low or medium traffic** (e.g. demo, portfolio, a few hundred to a few thousand queries per month), **OpenAI (gpt-4o-mini)** is usually cheaper: a few dollars or even under $1/month. A 24/7 server for Ollama typically costs about **$5–7/month** (Render, Railway, small VPS) regardless of usage. So **Ollama on a server becomes cheaper only at high volume** (tens of thousands of queries per month). Summary: **low usage → OpenAI; high usage or need to avoid API → Ollama on a server; zero cost → Ollama locally.**

**If we need a server anyway, why pay for OpenAI?** You don’t have to. **Running Ollama on the same server** (backend + Ollama on Render/Railway/VPS) means **no extra LLM cost** beyond the server you already pay for. So: **server + Ollama = one bill, no API usage.** The **advantages of OpenAI** in that case are: (1) **Easier setup** — no Ollama install, no model pull, no RAM/CPU sizing for the model. (2) **Often better answer quality** — gpt-4o-mini is very consistent; small local models can be less fluent. (3) **Smaller/cheaper server** — with OpenAI the server only runs FastAPI + FAISS; with Ollama you may need a larger instance (e.g. 4 GB+ RAM) to run the model. (4) **No maintenance** — model updates and scaling are on OpenAI. So: **same server + Ollama = save money, more ops; same server + OpenAI key = pay per use, less ops, often better quality.** For a portfolio demo, **Ollama on the same host** is a valid and often cheaper choice.

**Abuse protection when using OpenAI:** To protect against bad actors and control cost, use: (1) **RAG_API_KEY** — only requests with a valid key (header `X-RAG-API-Key` or `Authorization: Bearer`) can call `/ask`. You can give the same key to your frontend or to multiple users; only callers that send this key can use the API. (2) **API_RATE_LIMIT** — e.g. `30/minute`. When `RAG_API_KEY` is set, the limit is **per key**: if everyone uses the same key (e.g. one key in your deployed app), that key gets 30 requests per minute in total (all users share this cap). For per-user caps, use multiple keys (`RAG_API_KEY=key1,key2,...`) and give each user or client a different key. (3) **API_RATE_LIMIT_HOUR** — defaults to `100/hour` (portfolio-friendly); adds an hourly cap in addition to the per-minute limit. Set to `off` or `none` to disable. (4) **RETRIEVAL_MIN_SCORE** (optional) — if the best retrieval score is below this, the LLM is not called and a fallback answer is returned, reducing unnecessary API usage.

**How the request limit works:** The app uses **slowapi** and applies the limit to `POST /ask` only. The limit is counted **per key** when `RAG_API_KEY` is set (each key has its own bucket), or **per IP** when no key is required. Exceeding the limit returns **429 Too Many Requests**. By default the app applies **30/minute** and **100/hour** per key (or per IP). So burst is capped at 30/min and sustained use at 100/hour, which is suitable for a portfolio demo while limiting abuse. Together with **OpenAI billing limit**, this is usually enough for a deployed demo.

**Total spending cap (OpenAI):** To set a **hard money limit** (e.g. $10 or $50 per month), use **OpenAI’s billing limits**, not this app. In the [OpenAI platform](https://platform.openai.com): go to **Settings → Billing → Limits** (or **Usage limits**), enable **Budget limit** and enter a monthly amount. Once the limit is reached, OpenAI will block API calls until the next billing cycle. Our app’s rate limit (requests per minute) caps usage indirectly; for a strict cost cap, set the budget in the OpenAI dashboard.

---

## Deployment in detail

### Where to run the RAG backend

This project has **heavy runtime requirements**:

- **Python** with FastAPI, sentence-transformers, FAISS, numpy, pandas.
- **Persistent or rebuilt state:** FAISS index and embedding metadata (or rebuild on each deploy).
- **Optional LLM:** OpenAI (API call) or **Ollama** (a long-running server process).

That determines which platforms are suitable.

| Platform | RAG backend (FastAPI + FAISS + embeddings) | Ollama | Notes |
|----------|--------------------------------------------|--------|--------|
| **Render, Railway, Fly.io** | ✅ Yes (Web Service / background) | ✅ Yes, on same or separate service | Recommended. |
| **Hugging Face Spaces** | ✅ Possible (Docker or Python) | ❌ No (use HF Inference or external API) | Good for demos. |
| **Vercel (Pro)** | ⚠️ Not recommended (see below) | ❌ No | Use only for frontend in a hybrid setup. |
| **Local / VPS** | ✅ Yes | ✅ Yes (e.g. `ollama serve`) | Full control, free. |

---

### Why the full RAG stack does not fit Vercel (OpenAI or Ollama)

**Same constraints with OpenAI:** The reasons below apply **whether you use OpenAI or Ollama**. The problematic part on Vercel is the **RAG backend** (FastAPI + sentence-transformers + FAISS), not which LLM you call. With OpenAI you only add an API key; you do not host any LLM. So: **Render/Railway/Fly.io for the backend, optional Vercel for frontend**—that recommendation is the same for both.

**1. If you use Ollama: it cannot run on Vercel**

- Ollama is a **long-running server process** (daemon) that serves models over HTTP.
- Vercel runs **serverless functions**: short-lived, stateless, no persistent processes.
- You cannot install or run Ollama on Vercel. So “Ollama solution” must run **elsewhere** (your machine, VPS, or another cloud service).

**2. RAG backend is a poor fit for Vercel serverless (any LLM)**

- **Dependencies:** sentence-transformers, faiss-cpu, torch/numpy are large. Even with a 500 MB limit (Python on Vercel), the bundle is tight and cold starts are slow.
- **No persistent disk:** The FAISS index and metadata would need to be re-loaded (or rebuilt) on every cold start, which can take tens of seconds and hit timeouts.
- **Execution time:** Loading models and index can exceed typical function duration limits; first request would often fail or be very slow.

So: **full RAG backend on Vercel is not a viable option** with either OpenAI or Ollama. The project’s decision (PDR) to avoid Vercel for this app is correct. With OpenAI you still deploy the backend on Render/Railway/etc. and set `OPENAI_API_KEY`; with Ollama you run Ollama on that same host (or another) and set `OPENAI_API_BASE` + `OPENAI_MODEL`.

---

### Using Vercel in a hybrid setup (frontend only)

You can still use **Vercel Pro** for part of the system:

- **On Vercel:** Only the **frontend** (e.g. Next.js/React) or a thin proxy that calls your RAG API. No FAISS, no embedding model, no Ollama.
- **Elsewhere:** The **RAG backend** (FastAPI + indexing + retrieval) and **Ollama** run on Render, Railway, Fly.io, or a VPS.

Flow:

1. User opens the app hosted on Vercel.
2. Frontend calls your backend API (e.g. `https://your-rag-api.onrender.com/ask`).
3. Backend runs retrieval (FAISS) and calls Ollama (or OpenAI) for the answer.
4. Response is shown in the Vercel-hosted UI.

So: **“Deploy with Ollama”** means: deploy **backend + Ollama** on a suitable host; you can optionally put the **UI on Vercel**. With **OpenAI**, the same hybrid applies: backend on Render/Railway/etc. with `OPENAI_API_KEY`; no Ollama to host. The platform choice (Vercel only for frontend) is the same for both LLM options.

---

### Recommended: single-host deployment with Ollama (free)

For a **free or low-cost demo** including Ollama:

1. **Host:** Render (Web Service), Railway, or Fly.io. Or your own VPS.
2. **Backend:** Deploy this repo’s FastAPI app; run extraction, chunking, and indexing in the build/start phase (or once manually if you have persistent disk).
3. **Ollama:**  
   - **Same machine:** Install Ollama on the host and run it (e.g. `ollama serve`); in `.env` set `OPENAI_API_BASE=http://localhost:11434/v1` and `OPENAI_MODEL=llama3.2`.  
   - **Different machine:** Run Ollama on another server and set `OPENAI_API_BASE=http://that-server:11434/v1`.
4. **Start command:** `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`.

No OpenAI API key is required when using Ollama. Retrieval quality (embedding + FAISS) is unchanged; only the answer text comes from the local model.

---

### LLM choice: Ollama vs OpenAI (quality)

- **Retrieval and sources:** Identical. Embeddings and FAISS are local; chunk selection does not depend on whether you use Ollama or OpenAI.
- **Answer text:** Depends on the model. OpenAI’s gpt-4o-mini is strong and consistent. Ollama models (e.g. llama3.2, mistral) can be close for RAG if the prompt is clear; smaller models may be less fluent or slightly more prone to ignoring context. For a portfolio or internal demo, Ollama is usually sufficient; for production you may compare both and choose.

Using Ollama does **not** lower the technical quality of the project (architecture, eval, API design); it only changes the LLM that generates the final answer text.

---

### Current pricing and best option for portfolio (updated)

Rough **2024–2025** figures. Always check each provider’s pricing page before committing.

| Option | Host | LLM | Approx. monthly cost | Notes |
|--------|------|-----|----------------------|--------|
| **Render Free** | Free (750 h/mo) | OpenAI (usage) | $0 + OpenAI (~$0–2) | Spins down after 15 min; 512 MB can be tight for FAISS + embedding; ephemeral disk. |
| **Render Starter** | $7/mo | OpenAI | ~$7 + usage (~$0–2) | 512 MB, 0.5 CPU; may need Standard ($25) for Ollama. |
| **Railway Hobby** | $5/mo (includes $5 usage) | OpenAI or Ollama | ~$5–7 | Easiest managed deploy; enough for backend; add RAM if running Ollama. |
| **Fly.io** | ~$0–5 (free allowance) | OpenAI | ~$0–5 + usage | Small free allowance; need ≥1 GB RAM for our stack. |
| **Hetzner VPS (e.g. CX23)** | ~€3.5/mo (~\$4) | Ollama on same server | ~\$4 | 4 GB RAM, 2 vCPU; run backend + Ollama; no OpenAI bill; you manage OS. |
| **Hetzner + OpenAI** | ~€3.5/mo | OpenAI | ~\$4 + usage (~$0–2) | Same server, smaller RAM need; pay only for API. |

**OpenAI (gpt-4o-mini):** about **$0.15 / 1M input** and **$0.60 / 1M output** tokens. A typical RAG request is ~1.5k input + ~0.2k output → **~\$0.00035 per request**; 1,000 requests ≈ **\$0.35**, 3,000 ≈ **\$1**.

**Recommendation for portfolio:**

- **En düşük maliyet, biraz sunucu yönetimi:** **Hetzner CX23** (~€3.5/mo) + **Ollama** aynı sunucuda. Tek fatura, LLM için ekstra ödeme yok; backend + Ollama kurulumu sizin.
- **En az iş, yönetilen platform:** **Railway Hobby** ($5/mo) + **OpenAI** (kullanım ~$0–2). Deploy kolay; OpenAI’da aylık bütçe limiti koy.
- **Ücretsiz denemek:** **Render Free** + **OpenAI**; servis 15 dk hareketsizlikten sonra uyur, ilk istekte uyanır (gecikme olur).
