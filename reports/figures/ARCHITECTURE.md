# System architecture (RAG Document QA)

The diagram below can be viewed in GitHub / VS Code Mermaid preview.

```mermaid
flowchart TB
    subgraph ingest["1. Ingestion"]
        D[("PDF / TXT / MD")]
        E[pymupdf + plain text]
        C[Chunk 1200 / overlap 200]
        D --> E --> C
    end

    subgraph index["2. Indexing"]
        M[sentence-transformers\nall-MiniLM-L6-v2]
        F[(FAISS IndexFlatIP)]
        C --> M --> F
    end

    subgraph qa["3. Q&A"]
        Q([User question])
        R[Top-k retrieval]
        T{Score ≥\nRETRIEVAL_MIN_SCORE?}
        P[Prompt + context]
        L[OpenAI gpt-4o-mini]
        FB[Fallback answer]
        Q --> R --> T
        T -->|yes| P --> L
        T -->|no / disabled| FB
        R --> F
    end

    subgraph out["Output"]
        A[Answer + sources\ndocument, page, chunk_id]
    end
    L --> A
    FB --> A
```

## Retrieval → LLM flow (summary)

| Step | Component |
|------|-----------|
| Embed query | `embed_chunks.embed_texts` |
| Search | FAISS inner product (~cosine) |
| Threshold | `.env` → `RETRIEVAL_MIN_SCORE` (optional) |
| Generation | `prompt_builder` + `answer_generator` |
