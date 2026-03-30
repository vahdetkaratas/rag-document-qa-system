# RAG Document Intelligence QA System — Usage Guide

This document describes the project purpose, setup, run steps, expected outputs, and API usage.

---

## 1. Project Purpose

**RAG Document Intelligence QA System** provides **question–answering** over a document collection. The user asks a question; the system finds relevant chunks, passes them as context to an LLM, and returns an answer **with source citations**.

### Business problem

- Company knowledge is scattered across PDFs, handbooks, and policy docs.
- Keyword search is insufficient.
- Users want to ask questions and get answers **with sources**.

### What the system provides

- **Document processing:** PDF/TXT/MD text extraction and chunking.
- **Semantic search:** Embedding + FAISS to retrieve chunks closest to the question.
- **Grounded answer:** LLM answer based only on retrieved context; “not enough evidence” fallback when context is weak.
- **Source citation:** document, page, chunk_id per source.
- **API and demo:** FastAPI `POST /ask`, Streamlit UI.

### Technical scope

- **Pipeline:** Extraction → Chunking (1200/200) → Embeddings (sentence-transformers/all-MiniLM-L6-v2) → FAISS → Question → Top-k retrieval → Prompt → OpenAI → Answer + sources.
- **Evaluation:** Eval set for retrieval (hit@1/3/5) and answer quality.

---

## 2. Prerequisites

- **Python:** 3.10 or higher.
- **LLM for answers (choose one):**
  - **OpenAI (paid):** Set `OPENAI_API_KEY=sk-...` in `.env`.
  - **Ollama (free, local):** Install [Ollama](https://ollama.com), run `ollama pull llama3.2`, then in `.env` set `OPENAI_API_BASE=http://localhost:11434/v1` and `OPENAI_MODEL=llama3.2`. No API key needed.
- **Documents:** PDF, TXT, or MD in `data/raw_docs/` (8 sample .txt files are included).

All commands should be run from the **project root**.

---

## 3. Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

**LLM (for answer generation):**

- Create a `.env` file at project root.
- **OpenAI:** Add `OPENAI_API_KEY=sk-...` (see [platform.openai.com](https://platform.openai.com/api-keys)).
- **Ollama (free):** Add `OPENAI_API_BASE=http://localhost:11434/v1` and `OPENAI_MODEL=llama3.2` (install Ollama, then `ollama pull llama3.2`). No key required.
- See `.env.example`. Do not commit `.env`.

---

## 4. Running the Project

### 4.1 Pipeline (in order)

Run once (or when documents change).

**1. Text extraction**

```bash
python -m src.ingestion.run_extraction
```

- **Input:** .pdf, .txt, .md in `data/raw_docs/`.
- **Output:** `artifacts/extraction/extracted_documents.csv`.

**2. Chunking**

```bash
python -m src.ingestion.run_chunking
```

- **Input:** `artifacts/extraction/extracted_documents.csv`.
- **Output:** `artifacts/chunks/chunked_documents.csv`. Parameters: chunk_size=1200, chunk_overlap=200.

**3. Embedding + FAISS index**

```bash
python -c "from src.pipeline.indexing_pipeline import run_indexing_pipeline; run_indexing_pipeline()"
```

- **Input:** `artifacts/chunks/chunked_documents.csv`.
- **Output:** `artifacts/embeddings/`, `artifacts/faiss_index/index.faiss`. First run downloads the embedding model.

---

### 4.2 API (FastAPI)

With index built and `OPENAI_API_KEY` in `.env`:

```bash
uvicorn src.api.app:app --reload
```

- **Root:** http://127.0.0.1:8000  
- **Interactive docs:** http://127.0.0.1:8000/docs  

| Endpoint    | Description                    |
|------------|---------------------------------|
| `GET /health` | Health check             |
| `POST /ask`   | Send question → answer + sources |

**Example request (POST /ask):** `{ "question": "What is the cancellation policy?" }`

---

### 4.3 Streamlit demo

```bash
streamlit run src/demo/streamlit_app.py
```

- Question box in browser; “Ask” returns answer and source list. Without `OPENAI_API_KEY`, no answer is generated.

---

### 4.4 Evaluation

**Retrieval (Hit@1, Hit@3, Hit@5):**

```python
from src.evaluation.evaluate_retrieval import evaluate_retrieval
r = evaluate_retrieval()
print(r["hit_rates"])
```

Eval set: `data/eval/eval_questions.csv`. Index and chunk metadata must exist.

**Answer evaluation (batch):**

```python
from src.evaluation.evaluate_answers import evaluate_answers_batch
evaluate_answers_batch(use_llm=True)  # requires OPENAI_API_KEY
# Output: artifacts/eval_results/answer_eval.csv
```

---

### 4.5 Tests

```bash
python -m pytest tests/ -v
pytest tests -q -m "not slow"   # skip slow embedding tests
```

- Extraction, chunking, generation (prompt), API tests run without API key. Retrieval tests require pipeline to be run first.

---

## 5. Expected Outputs

| Location | Description |
|----------|-------------|
| `artifacts/extraction/extracted_documents.csv` | Raw text per page/doc |
| `artifacts/chunks/chunked_documents.csv` | Chunked text + metadata |
| `artifacts/embeddings/chunk_embeddings.npy` | Chunk embeddings |
| `artifacts/embeddings/chunk_metadata.csv` | Chunk id, document, page, text |
| `artifacts/faiss_index/index.faiss` | FAISS index |
| `artifacts/eval_results/answer_eval.csv` | Answer eval batch output |

---

## 6. Configuration

- **Embedding model:** `src/embeddings/embed_chunks.py` — `EMBEDDING_MODEL`, `NORMALIZE`.
- **Chunking:** `src/ingestion/chunk_documents.py` — `CHUNK_SIZE`, `CHUNK_OVERLAP`.
- **LLM:** `src/generation/answer_generator.py` — `DEFAULT_MODEL`. API key via `.env`.

---

## 7. Common Issues

- **OPENAI_API_KEY error:** Use either (1) OpenAI: create `.env` with `OPENAI_API_KEY=sk-...`, or (2) Ollama: set `OPENAI_API_BASE=http://localhost:11434/v1` and `OPENAI_MODEL=llama3.2` (no key). See `.env.example`.
- **FAISS index not found:** Run `run_extraction` → `run_chunking` → indexing pipeline in order.
- **No documents found:** Add at least one .pdf, .txt, or .md in `data/raw_docs/`.
- **sentence_transformers / faiss import error:** Run `pip install -r requirements.txt`.

---

## 8. Command Summary

| Purpose | Command |
|---------|---------|
| Install deps | `pip install -r requirements.txt` |
| Extraction | `python -m src.ingestion.run_extraction` |
| Chunking | `python -m src.ingestion.run_chunking` |
| Indexing | `python -c "from src.pipeline.indexing_pipeline import run_indexing_pipeline; run_indexing_pipeline()"` |
| Start API | `uvicorn src.api.app:app --reload` |
| Streamlit | `streamlit run src/demo/streamlit_app.py` |
| Tests | `python -m pytest tests/ -v` |

---

## 9. API Access Notes

**Where to enter the API key:** (1) **Server:** Put your secret in the **environment** where the API runs: project root `.env` (e.g. `RAG_API_KEY=your-secret-key`) or your host’s env vars (Render, Railway, etc.). Do not commit `.env`. (2) **Client (frontend / Postman / curl):** Send the **same value** in every request to `POST /ask` using one of these headers: **`X-RAG-API-Key: your-secret-key`** or **`Authorization: Bearer your-secret-key`**. If the key is missing or wrong, the API returns 401.

---

## 10. Related Docs

| File | Description |
|------|-------------|
| **README.md** | Overview, setup, limitations |
| **docs/RAG_SYSTEM_DESIGN.md** | Pipeline, retrieval, API design |
