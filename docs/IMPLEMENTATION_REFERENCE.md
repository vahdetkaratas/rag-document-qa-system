# Implementation Reference — RAG Project

Specific values needed during implementation.

---

## 1. Repo structure (final)

```
rag-document-intelligence-qa-system/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw_docs/
│   ├── processed/
│   └── eval/
│       └── eval_questions.csv
│
├── notebooks/
│   ├── 01_document_exploration.ipynb
│   ├── 02_chunking_experiments.ipynb
│   ├── 03_retrieval_tests.ipynb
│   ├── 04_answer_generation_tests.ipynb
│   └── 05_evaluation_analysis.ipynb
│
├── src/
│   ├── ingestion/
│   │   ├── load_documents.py
│   │   ├── extract_text.py
│   │   ├── chunk_documents.py
│   │   └── run_extraction.py, run_chunking.py
│   ├── embeddings/
│   │   ├── embed_chunks.py
│   │   └── vector_store.py
│   ├── retrieval/
│   │   └── retrieve.py
│   ├── generation/
│   │   ├── prompt_builder.py
│   │   └── answer_generator.py
│   ├── pipeline/
│   │   ├── indexing_pipeline.py
│   │   ├── retrieval_pipeline.py
│   │   └── qa_pipeline.py
│   ├── evaluation/
│   │   ├── evaluate_retrieval.py
│   │   └── evaluate_answers.py
│   ├── api/
│   │   ├── app.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── demo/
│   │   └── streamlit_app.py
│   └── utils/
│       └── file_helpers.py
│
├── artifacts/
│   ├── extraction/
│   ├── chunks/
│   ├── embeddings/
│   ├── faiss_index/
│   ├── eval_results/
│   └── answers/
│
├── reports/
│   └── figures/
│
└── tests/
    ├── test_extraction.py
    ├── test_chunking.py
    ├── test_retrieval.py
    ├── test_generation.py
    └── test_api.py
```

---

## 2. requirements.txt

**Milestone 1:** pymupdf, pandas, pytest, jupyter

**Milestone 3 ek:** sentence-transformers, faiss-cpu, numpy

**Milestone 4 ek:** openai, python-dotenv

**Full:**
```
pymupdf
pandas
pytest
jupyter
sentence-transformers
faiss-cpu
numpy
openai
python-dotenv
fastapi
uvicorn
streamlit
```

---

## 2b. API Key Setup (LLM — before Milestone 4)

**Prerequisite:** OpenAI API key (or OpenRouter etc.) required.

1. Create `.env` at project root:
```
OPENAI_API_KEY=sk-...
```

2. `.env.example` (commit to repo; do not commit .env):
```
OPENAI_API_KEY=your_key_here
```

3. Add to `.gitignore`: `.env`

4. In code: load with `python-dotenv`, use `os.getenv("OPENAI_API_KEY")`. Meaningful error if key missing.

**In README:** "Setup: create .env and add OPENAI_API_KEY"

---

## 3. Chunking Parametreleri

| Parameter | Value |
|-----------|-------|
| chunk_size | 1200 (characters) |
| chunk_overlap | 200 (characters) |

---

## 4. Embedding

| Property | Value |
|----------|-------|
| Model | sentence-transformers/all-MiniLM-L6-v2 |
| normalize_embeddings | True |

---

## 5. FAISS

| Property | Value |
|----------|-------|
| Index type | IndexFlatIP (inner product) |
| Embeddings | float32 |

---

## 6. Retrieval

| Parameter | Value |
|-----------|-------|
| top_k | 3 or 5 |

---

## 7. Paths

All paths in `src/config.py` are relative to `PROJECT_ROOT`; CWD-independent.

```python
# src/config.py — summary (full list in file)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DOCS_DIR = PROJECT_ROOT / "data" / "raw_docs"
EXTRACTION_OUTPUT = PROJECT_ROOT / "artifacts" / "extraction" / "extracted_documents.csv"
CHUNK_OUTPUT = PROJECT_ROOT / "artifacts" / "chunks" / "chunked_documents.csv"
# ... EMBEDDINGS_PATH, METADATA_PATH, FAISS_INDEX_PATH, EVAL_QUESTIONS_PATH
```

---

## 8. API Schemas

### POST /ask Request

```json
{ "question": "What is the cancellation policy?" }
```

### Response

```json
{
  "answer": "...",
  "sources": [
    {
      "document": "refund_and_cancellation_policy.pdf",
      "page": 3,
      "chunk_id": "refund_policy_p3_c2"
    }
  ],
  "retrieved_chunks": [...]
}
```

---

## 9. Eval Questions CSV

| Column | Description |
|--------|-------------|
| question | Question text |
| expected_document | Expected source document |
| expected_answer_summary | Expected answer summary |
| difficulty | easy/medium/hard (optional) |
| notes | Optional |

**How to create eval questions:** After reading documents, write 2–4 questions per doc. Target 20–30 questions. Prepare before M5.

---

## 9b. Document Source (Data)

Where to get 8–15 documents: (A) Create your own — fictional handbook, policy, FAQ. (B) Public samples — privacy policy, ToS, handbook excerpts. (C) Hybrid. Fill data/raw_docs/ in M1.

---

## 10. Example Document Names

- customer_onboarding_policy.pdf
- refund_and_cancellation_policy.pdf
- incident_response_manual.pdf
- technical_support_workflow.pdf
- pricing_rules_guide.pdf
- account_management_procedures.pdf
- service_level_policy.pdf
- internal_faq.pdf
- escalation_matrix.pdf
- billing_policy.pdf

---

## 11. SUPPORTED_EXTENSIONS

```python
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}
```

---

## 12. Chunk Metadata Columns

chunk_id, document_name, page_number, chunk_index_within_page, text, char_count, start_char, end_char

---

## 13. README & Presentation Checklist

- [x] **Repo name:** rag-document-intelligence-qa-system
- [x] **Description:** "Retrieval-augmented QA system that answers questions over document collections using embeddings and vector search"
- [x] **README:** Architecture diagram, document ingestion → chunking → embeddings → FAISS → answer + sources
- [x] **Setup:** Create .env, add OPENAI_API_KEY; .env.example; mention API key in How to run
- [x] **Tech stack:** Python, FAISS, embedding models, LLM APIs, Streamlit
- [ ] **Demo screenshot:** Question → Answer + Sources example (optional)
- [x] **Evaluation section:** Retrieval hit rates, answer quality

---

*Root README and doc index: docs/README.md.*
