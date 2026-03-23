# RAG System Design

Technical design for the RAG-based Document Intelligence QA System.

---

## 1. End-to-End Pipeline Overview

```
Documents (PDF/TXT/MD)
        │
        ▼
┌───────────────────┐
│ Text Extraction   │  (pymupdf, page-based)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Chunking          │  (1200 char, 200 overlap, metadata)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Embeddings        │  (sentence-transformers, all-MiniLM-L6-v2)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ FAISS Index       │  (IndexFlatIP, normalized)
└─────────┬─────────┘
          │
          ▼
User Question
        │
        ▼
┌───────────────────┐
│ Query Embedding   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Top-k Retrieval   │  (k=3 or 5)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Prompt Construction│  (retrieved context + question)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ LLM Answer        │  (grounded, fallback if insufficient)
└─────────┬─────────┘
          │
          ▼
Answer + Sources
```

---

## 2. Document Set

| Property | Value |
|----------|-------|
| **Type** | Technical / procedural docs (policy, manual, workflow) |
| **Count** | 8–15 documents |
| **Format** | Mostly PDF, some TXT/MD |
| **Length** | ~2–10 pages |

**Example file names:** customer_onboarding_policy.pdf, refund_and_cancellation_policy.pdf, incident_response_manual.pdf, technical_support_workflow.pdf, pricing_rules_guide.pdf, account_management_procedures.pdf, service_level_policy.pdf, internal_faq.pdf

---

## 3. Ingestion (Layer 1)

### Text Extraction

- **PDF:** pymupdf (fitz), page-by-page `page.get_text("text")`
- **TXT/MD:** Plain file read
- **Output:** document_name, page_number, text, char_count
- **Artifact:** artifacts/extraction/extracted_documents.csv

### Chunking

| Parameter | Value |
|-----------|-------|
| chunk_size | 1200 characters |
| chunk_overlap | 200 characters |
| Level | Page-based (extraction is page-level) |

### Chunk Metadata

- chunk_id (e.g. doc_p3_c2)
- document_name
- page_number
- chunk_index_within_page
- text
- char_count
- start_char, end_char (optional)

---

## 4. Retrieval (Layer 2)

### Embeddings

- **Model:** sentence-transformers/all-MiniLM-L6-v2
- **normalize_embeddings:** True (for cosine-like similarity)
- **Artifact:** chunk_embeddings.npy, chunk_metadata.csv

### Vector Store

- **FAISS:** IndexFlatIP (inner product, cosine-like when normalized)
- **Artifact:** artifacts/faiss_index/index.faiss

### Retrieval

- **top_k:** 3 or 5
- **Output:** Retrieved chunks + score

---

## 5. Answer Generation (Layer 3)

### Prompt

- Retrieved context is put into the prompt
- Rely only on given context
- If insufficient: "I could not find enough supporting evidence" fallback
- Consider sources; do not invent

### Source Citation

- Sources are returned **separately** from retrieval (even when LLM produces answer)
- Format: document, page, chunk_id

### Output Format

```json
{
  "question": "What is the cancellation policy?",
  "answer": "Cancellation requires written notice at least 14 days before renewal.",
  "sources": [
    {
      "document": "refund_and_cancellation_policy.pdf",
      "page": 3,
      "chunk_id": "refund_policy_p3_c2"
    }
  ]
}
```

---

## 6. Evaluation

### Eval Set

- **File:** data/eval/eval_questions.csv
- **Columns:** question, expected_document, expected_answer_summary, difficulty
- **Count:** 20–30 questions

### Retrieval Metrics

- Top-1 hit rate
- Top-3 hit rate
- Top-5 hit rate

### Answer Metrics (semi-manual)

- Correctness (0/1)
- Groundedness (0/1)
- Completeness (0/1)
- Hallucination check

---

## 7. API Design

| Endpoint | Description |
|----------|-------------|
| POST /ask | Main endpoint — question → answer + sources |
| GET /health | Health check |
| POST /index | Optional — index documents (not required in first version) |

### /ask Request

```json
{ "question": "What is the cancellation policy?" }
```

### /ask Response

```json
{
  "answer": "...",
  "sources": [...],
  "retrieved_chunks": [...]  // optional
}
```

---

## 8. Demo

- **Streamlit** recommended
- Question input → answer + source list
- Minimal UI

---

## 9. Potential Technical Risks

| Risk | Mitigation |
|------|------------|
| Bad chunking | Parameter tuning, notebook quality check |
| Hallucination | Grounded prompt, fallback, show sources separately |
| Wrong retrieval | Evaluation set, top-k comparison |
| FAISS index size | Start with small document set |

---

