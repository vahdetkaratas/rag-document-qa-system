# Project Decision Record — RAG-based Document Intelligence QA System

Project decisions and scope. RAG-based document QA project for portfolio.

---

## 1. Selected Project

**RAG-based Document Intelligence QA System**

A QA system over a multi-document collection: chunking, semantic retrieval, grounded answers with source citations.

**Portfolio role:** Project 1 (Churn) shows classic tabular ML; this project shows modern LLM/retrieval application.

---

## 2. Why This Project Was Chosen

- **Applied ML Engineer roles** now expect embeddings, retrieval, LLM use, not only classic ML
- **Single project** demonstrates embeddings, vector search, retrieval pipeline, answer generation, grounding/citation
- **Document-based**, retrieval-focused, measurable system rather than "I built a chatbot"
- **Product-oriented** — user asks; system returns answer + sources

---

## 3. Rejected / Alternative Ideas

| Category | Rejected |
|----------|----------|
| Project type | Chatbot only, LLM call only |
| Data | Novels, heavy academic papers, random blogs |
| Framework | Putting everything in LangChain |
| Presentation | Hiding retrieval, not showing sources |
| Evaluation | No evaluation |

---

## 4. Target Users

- **Primary:** Recruiters (Applied ML Engineer role)
- **Secondary:** Small team, analyst, support — users searching documents for information

---

## 5. Problem Statement

Company knowledge is scattered across PDFs, handbooks, policy docs. Keyword search is weak. Users want to ask questions and get answers with sources.

**Core question:** Unstructured documents → searchable, grounded knowledge system

---

## 6. Core Value Proposition

- **Technical:** Document ingestion → chunking → embeddings → FAISS retrieval → grounded answer + sources
- **Business:** Search within documents, semantic search, source citation
- **Portfolio:** Modern ML application, retrieval pipeline, evaluation

---

## 7. Proposed Phase 1 Scope (MVP)

### Minimum Version

- 5–10 documents
- PDF/text extraction
- Chunking
- Embeddings (sentence-transformers)
- FAISS retrieval
- LLM answer
- Source citations
- Simple API
- README

### Strong Version

- Evaluation set (20–30 questions)
- Retrieval comparison
- Chunking comparison
- Streamlit demo
- Answer quality analysis
- Fallback logic ("not enough evidence")

---

## 8. Out of Scope / Non-Goals

- Hybrid search, reranker (first version)
- Multi-hop reasoning
- Auth, user management
- Conversation memory
- Agentic workflows
- Production database
- Vercel deployment (heavier than Churn; use Render, Railway, HF Spaces, or local demo + video)

---

## 9. Technical Direction

| Component | Choice |
|-----------|--------|
| Document processing | pymupdf |
| Chunking | Custom (1200 char, 200 overlap) |
| Embeddings | sentence-transformers, all-MiniLM-L6-v2 |
| Vector store | FAISS (faiss-cpu) |
| Generation | OpenAI API (or abstract interface) |
| API | FastAPI |
| Demo | Streamlit |

---

## 10. Business / Portfolio Intent

- **Target:** Applied ML Engineer
- **Signal:** "Not only sklearn; also modern ML application stack"
- **Portfolio trio:** Churn (tabular) + RAG (retrieval/LLM) + Monitoring (next project)

---

## 11. Open Questions

- Deployment: Local demo + video vs Render/Railway/HF Spaces?
- LLM provider: OpenAI, OpenRouter, or local model? (API-based recommended at start)

---

## 12. Risks / Weaknesses

- Bad chunking weakens retrieval
- LLM hallucination — grounding and fallback matter
- Deployment heavier than Churn (FAISS, documents, LLM calls)

---

## 13. Assumptions

- Can start with 8–15 documents
- Controlled document set (fictional company handbook, policy docs) usable
- 20–30 question eval set sufficient
- OpenAI API or equivalent accessible

---

## 14. Recruiter Checklist

What makes this more than "chat with PDF" — **Potential flagship project:**

- [x] **Document ingestion** — How documents are loaded (load_documents, extract_text, run_extraction)
- [x] **Chunking** — Strategy (1200 char, 200 overlap, chunk_documents)
- [x] **Embeddings** — Model and usage (sentence-transformers/all-MiniLM-L6-v2, normalize)
- [x] **FAISS** (or equivalent) — Vector retrieval (IndexFlatIP)
- [x] **Source citation** — Answer with sources (document, page, chunk_id)
- [x] **Evaluation** — Retrieval + answer metrics (eval_questions.csv, evaluate_retrieval, evaluate_answers)
- [x] **Demo** — Streamlit interface (streamlit_app.py)

*These should be visible. Avoid "wrapper around API" perception.*
