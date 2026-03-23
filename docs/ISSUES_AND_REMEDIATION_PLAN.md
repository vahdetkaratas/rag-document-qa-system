# Issues and Remediation Plan — RAG Document Intelligence QA

Gaps, risks, and **how to fix them** (step-by-step) identified from code analysis.

**Priority:** P0 = critical, P1 = short-term, P2 = improvement.

### Completed (tracking)

| Item | Status |
|------|--------|
| P0-1 Hit@k + `_doc_in_results` + `tests/test_evaluation.py` | Done |
| P0-2 `qa_pipeline` error leakage (generic fallback except API key) | Done |
| P1-4 Eval CSV ~22 questions | Done |
| P1-5 `reports/figures/` (`.gitkeep`) | Done |
| P1-3 RAG README → root README.md | Done |
| P2-8 Project root paths (`src/config.py`, all artifact/data paths) | Done |
| P2-9 CORS → `CORS_ORIGINS` (.env) | Done |
| P2-11 Retrieval score threshold → `RETRIEVAL_MIN_SCORE` | Done |
| Root README → RAG links | Done |
| P2-10 Rate limit (`slowapi`, `API_RATE_LIMIT`) | Done |
| P2-12 requirements version ranges + lock note | Done |
| M7 Architecture diagram | Done `reports/figures/ARCHITECTURE.md` (Mermaid) |
| Optional `RAG_API_KEY` (REST) | Done `src/api/auth.py` |
| CI (GitHub Actions) | Done `.github/workflows/ci.yml` |
| `pytest -m slow` / `not slow` | Done `pytest.ini`, `test_retrieval` |
| `requirements-lock.txt` generation note | Done (file header) |

---

## P0 — Critical (correctness / security)

### 1. Retrieval Hit@k metric wrong (`evaluate_retrieval.py`) — Fixed

**Issue:** `break` on first successful k per question. If the correct doc is at rank 2, Hit@3 increments but Hit@5 is not counted; **Hit@5 was underreported**.

**Remediation:** Remove `break`; count each k independently; optional `_doc_matches()` for partial doc name match; test with mocked `retrieve_top_k`.

---

### 2. LLM / server error leakage (`qa_pipeline.py`) — Fixed

**Issue:** When `generate_answer` fails, response included `"(Error: …)"`; API details could leak.

**Remediation:** Re-raise for `OPENAI_API_KEY` (ValueError); use fixed `FALLBACK_ANSWER` for other exceptions; (optional) log server-side.

---

## P1 — Portfolio and documentation

### 3. Root README not RAG-focused — Partially done

**Status:** Root `README.md` simplified for RAG. Details: `docs/README.md`, `docs/USAGE_GUIDE.md`.

---

### 4. Eval set 10 questions (target 20–30) — Done ~22

**Remaining:** Optionally expand to 30; re-run retrieval metrics.

---

### 5. `reports/figures/` empty — Folder done, images pending

**Remaining:** Add PNG diagrams (architecture, eval summary). Link from README.

---

## P1 — Test and CI

### 6. Retrieval integration test skipped when no index

**Issue:** `test_retrieve_top_k` skips if index is not built in CI.

**Remediation:** CI job builds mini pipeline (Option A) or test creates temp index (Option B); use `pytest -m "not slow"` for fast/slow split.

---

### 7. Generation / API tests shallow

**Issue:** No LLM mock; `/ask` only validation tests.

**Remediation:** Mock `generate_answer` for end-to-end; assert 200 + `answer` + `sources` shape.

---

## P2 — Production and robustness

### 8. Working directory — relative paths — Done

**Status:** `src/config.py` with `PROJECT_ROOT`; all paths derived from it.

---

### 9. CORS `allow_origins=["*"]` — Done

**Status:** `.env` → `CORS_ORIGINS`. Use explicit origins in production.

---

### 10. Rate limit / auth — Partially done

**Status:** `slowapi` for `POST /ask`; `API_RATE_LIMIT`; optional `RAG_API_KEY` header.

---

### 11. Fallback only at prompt level — Done

**Status:** `RETRIEVAL_MIN_SCORE`; if best score below threshold, return `FALLBACK_ANSWER` without calling LLM.

---

### 12. `requirements.txt` versions — Partially done

**Status:** Version ranges for main packages; generate `requirements-lock.txt` in production.

---

### 13. Windows / Hugging Face symlink warning

**Remediation:** `HF_HUB_DISABLE_SYMLINKS_WARNING=1` in README or `.env.example`; optional Windows Developer Mode.

---

### 14. Root README vs folder structure (monorepo)

**Remediation:** If repo is RAG-only, keep README focused; if monorepo, portfolio README at parent level.

---

## Suggested order

| # | Item | Note |
|---|------|------|
| 1 | P0-1 Hit@k fix + test | Metric reliability |
| 2 | P0-2 Error leakage | API security |
| 3 | P1-4 Eval CSV expansion | Quick win |
| 4 | P1-5 reports/figures | Structure ready |
| 5 | P1-3 README | Sharing |
| 6 | P1-6/7 Test depth | CI |
| 7 | P2 items | As needed |

---

*Last update: code analysis and plan approval.*
