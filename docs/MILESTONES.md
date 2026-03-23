# Phase 1 Milestones — RAG Document Intelligence

Implementation order. 7 milestones.

---

## Milestone 1 — Repo Skeleton + Document Processing

**Goal:** Documents can be read and text extracted.

**Done:**
- [x] Repo (rag-document-intelligence-qa-system)
- [x] Folder structure (data/raw_docs, processed, eval; src/ingestion, utils; artifacts/extraction; notebooks; tests)
- [x] 8–10 documents in data/raw_docs/
- [x] src/ingestion/load_documents.py, extract_text.py, run_extraction.py
- [x] src/utils/file_helpers.py (optional)
- [x] notebooks/01_document_exploration.ipynb, tests/test_extraction.py

**Output:** artifacts/extraction/extracted_documents.csv

---

## Milestone 2 — Chunking

**Goal:** Documents split into chunks with metadata.

**Done:** chunk_documents.py, run_chunking.py, notebooks/02, tests/test_chunking.py. Parameters: chunk_size=1200, chunk_overlap=200. **Output:** artifacts/chunks/chunked_documents.csv

---

## Milestone 3 — Embeddings + FAISS + Retrieval

**Goal:** Question → top-k chunks retrieved.

**Done:** embed_chunks.py, vector_store.py, retrieve.py, indexing_pipeline.py, retrieval_pipeline.py, notebooks/03, tests/test_retrieval.py. **Output:** chunk_embeddings.npy, chunk_metadata.csv, index.faiss

---

## Milestone 4 — QA Pipeline (Answer Generation)

**Goal:** Question → answer + sources. **Prerequisite:** .env + OPENAI_API_KEY.

**Done:** prompt_builder.py, answer_generator.py, qa_pipeline.py, fallback for insufficient context, notebooks/04, tests/test_generation.py. **Output:** End-to-end QA working.

---

## Milestone 5 — Evaluation

**Goal:** Retrieval and answer quality measured. **Done:** eval_questions.csv, evaluate_retrieval.py, evaluate_answers.py, notebooks/05, save results to CSV/JSON. **Output:** retrieval hit rates, answer eval table.

---

## Milestone 6 — API + Demo

**Goal:** FastAPI + Streamlit running. **Done:** schemas.py, service.py, app.py (POST /ask, GET /health), streamlit_app.py, error handling (empty question, missing index/key). **Output:** Working API, Streamlit demo.

---

## Milestone 7 — README / Case Study

**Goal:** Shareable portfolio project. **Done:** README (Overview, Architecture, Setup, Evaluation, Limitations); optional reports/figures. **Output:** Portfolio-ready repo.

---

## MVP vs Strong

| Component | MVP | Strong |
|-----------|-----|--------|
| Document count | 5–10 | 8–15 |
| Extraction / Chunking / Embeddings / FAISS / Retrieval | ✓ | ✓ |
| Answer + Sources / Fallback | ✓ | ✓ |
| Evaluation set | small | 20–30 questions |
| API / Streamlit / README | ✓ | ✓ |

---

## Completion criteria

- [x] All 7 milestones done
- [x] Indexing pipeline (extraction → chunking → embeddings → FAISS) runs
- [x] QA pipeline (question → retrieve → answer + sources) runs
- [x] API (POST /ask, GET /health) and Streamlit demo run
- [x] Recruiter Checklist (PROJECT_DECISION_RECORD §14) and README Checklist (IMPLEMENTATION_REFERENCE §13) met

---

*Use with RAG_SYSTEM_DESIGN.md and IMPLEMENTATION_REFERENCE.md.*
