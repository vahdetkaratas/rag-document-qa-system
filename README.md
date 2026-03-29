# RAG Document Intelligence QA System

Question–answering over policy/handbook-style documents using **semantic retrieval + LLM**. Answers are grounded in retrieved chunks and return **sources (document, page, chunk_id)**.

**Doc index:** [docs/README.md](docs/README.md) · **Issues / plan:** [docs/ISSUES_AND_REMEDIATION_PLAN.md](docs/ISSUES_AND_REMEDIATION_PLAN.md) · **Publishing:** [docs/PUBLISH.md](docs/PUBLISH.md)

---

## Features

- PDF / TXT / MD → chunking → `sentence-transformers` → **FAISS** top-k  
- LLM for answers: **OpenAI** (paid) or **Ollama** (free, local) via `OPENAI_API_BASE` + `OPENAI_MODEL`  
- FastAPI: `POST /ask`, `GET /health` · Streamlit demo  
- Eval: Hit@k; optional `RAG_API_KEY`, rate limit, retrieval score threshold  

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Paths are rooted at project root via `src/config.py`.

`.env` — see `.env.example`. For answers: `OPENAI_API_KEY` (OpenAI) or `OPENAI_API_BASE` + `OPENAI_MODEL` (e.g. Ollama, no key). Optional: `CORS_ORIGINS`, `RETRIEVAL_MIN_SCORE`, `API_RATE_LIMIT`, `RAG_API_KEY`.

---

## Pipeline (once)

```bash
python -m src.ingestion.run_extraction
python -m src.ingestion.run_chunking
python -c "from src.pipeline.indexing_pipeline import run_indexing_pipeline; run_indexing_pipeline()"
```

---

## Run

```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
streamlit run src/demo/streamlit_app.py
```

`POST /ask`: `{"question": "..."}`

---

## Test

```bash
pytest tests -q
pytest tests -q -m "not slow"
```

---

## VPS deployment notes (Docker)

- **Image:** `Dockerfile` copies the **full project root** into `/app`. **Artifacts must be built before `docker build`:** run extraction → chunking → indexing locally (or in CI), so `artifacts/embeddings/chunk_metadata.csv` and `artifacts/faiss_index/index.faiss` exist in the build context. The container **does not** rebuild the index on startup.
- **Run:** listens on **`0.0.0.0:8000`** (internal port **8000**). Example: `docker build -t rag-qa .` then `docker run -p 8000:8000 --env-file .env rag-qa`.
- **Env vars:** Same as local — at minimum **`OPENAI_API_KEY`** (or **`OPENAI_API_BASE` + `OPENAI_MODEL`** for Ollama). Optional: **`RAG_API_KEY`**, **`CORS_ORIGINS`**, **`RAG_PROJECT_ROOT`** (usually `/app` in Docker if `WORKDIR` is `/app`), rate limits, **`RETRIEVAL_MIN_SCORE`**. See **`.env.example`**. If the browser UI is on a **subdomain** (e.g. `https://rag.vahdetkaratas.com` vs apex site), include that origin explicitly in **`CORS_ORIGINS`**.
- **Reverse proxy:** Put **Caddy** or **Nginx** in front; terminate TLS there and **`proxy_pass`** to `http://127.0.0.1:8000` (or the container’s published port).
- **Health:** `GET /health` returns **`ready`** (true only if index + metadata files exist and are loaded in memory), plus `index_file`, `metadata_file`, `retrieval_loaded`. HTTP stays **200** while the process is alive; use **`ready`** for load-balancer / script checks.

---

## Architecture

- Diagram: [reports/figures/ARCHITECTURE.md](reports/figures/ARCHITECTURE.md)  
- Design: [docs/RAG_SYSTEM_DESIGN.md](docs/RAG_SYSTEM_DESIGN.md)
