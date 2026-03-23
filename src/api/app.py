"""
FastAPI app: POST /ask, GET /health. RAG_SYSTEM_DESIGN §7.
CORS: CORS_ORIGINS=... | Rate: API_RATE_LIMIT=30/minute (slowapi)
When RAG_API_KEY is set, rate limit is per key; otherwise per IP. Protects against abuse when using OpenAI.
"""
import logging
import os
from contextlib import asynccontextmanager

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.auth import require_rag_api_key_if_configured, _get_rag_key_from_request
from src.api.schemas import AskRequest, AskResponse
from src.api.service import ask
from src.config import FAISS_INDEX_PATH, METADATA_PATH

logger = logging.getLogger(__name__)

API_DESCRIPTION = """
## RAG document QA API

Retrieval-augmented question answering over a **fixed corpus** of chunked documents. Each question is
embedded with the same model used at index time, matched via **FAISS** (inner product on normalized vectors ≈ cosine similarity),
and passed to an **LLM** with **only** the retrieved passages as context. Responses include **source citations**
(document name, page, chunk id).

### Try it out (Swagger)

1. Open **POST /ask** → **Try it out**.
2. If your deployment sets **`RAG_API_KEY`**, click **Authorize** and enter the key (header `X-RAG-API-Key` or Bearer).
3. Send a JSON body `{"question": "…"}`. The response includes `answer`, `sources`, and `retrieved_chunks` (full rows + scores for inspection).

### Authentication (optional, server-dependent)

| When | What to send |
|------|----------------|
| Server has **`RAG_API_KEY` set** | Header **`X-RAG-API-Key: &lt;key&gt;`** or **`Authorization: Bearer &lt;key&gt;`** |
| Server has **no** `RAG_API_KEY` | No auth headers |

Invalid or missing key when required → **401**.

### Rate limits

Limits are enforced by **slowapi** from environment variables (defaults are portfolio-friendly):

- **`API_RATE_LIMIT`** — e.g. `30/minute` (use `off` / `none` / `0` to effectively disable per-minute cap).
- **`API_RATE_LIMIT_HOUR`** — e.g. `100/hour` (disable with `off` / `none` / `0`).

When `RAG_API_KEY` is set, limits apply **per key**; otherwise **per client IP**. Exceeded → **429**.

### Health vs readiness

**GET /health** always returns 200 if the process is up. Use the JSON field **`ready`**: `true` only when the FAISS index file, metadata CSV exist on disk, and the retrieval cache is loaded.

### Common errors (POST /ask)

| Status | Meaning |
|--------|---------|
| **400** | Empty `question` or bad request body. |
| **401** | `RAG_API_KEY` required but missing/invalid. |
| **429** | Rate limit exceeded. |
| **503** | LLM not configured (e.g. missing `OPENAI_API_KEY` when using OpenAI), or index/metadata not available. |

### Server configuration (reference)

Answers depend on **`OPENAI_API_KEY`** and **`OPENAI_MODEL`**, or **`OPENAI_API_BASE`** + model for OpenAI-compatible hosts (e.g. Ollama). Optional **`RETRIEVAL_MIN_SCORE`**: if the best retrieval score is below this threshold, the API returns a **fallback answer** without calling the LLM (chunks are still returned in `retrieved_chunks` for debugging).

See repository **`.env.example`** and **`docs/USAGE_GUIDE.md`** for full env list.
"""

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Liveness and retrieval readiness (index + metadata loaded).",
    },
    {
        "name": "qa",
        "description": "Ask a question; get a grounded answer, citations, and optional retrieved chunk payloads.",
    },
]

_cors = os.getenv("CORS_ORIGINS", "").strip()
_allow_origins = [o.strip() for o in _cors.split(",") if o.strip()] if _cors else ["*"]

_rl = (os.getenv("API_RATE_LIMIT") or "30/minute").strip().lower()
if _rl in ("", "off", "none", "0", "false"):
    _rl = "10000/minute"
# Hourly cap (default 100/hour for portfolio); applied in addition to per-minute. Set to off/none/0 to disable.
_rl_hour_raw = (os.getenv("API_RATE_LIMIT_HOUR") or "100/hour").strip().lower()
if _rl_hour_raw in ("", "off", "none", "0", "false"):
    _rl_hour = None
else:
    _rl_hour = _rl_hour_raw


def _rate_limit_key(request: Request) -> str:
    """Rate limit by API key when RAG_API_KEY is set, else by IP. Limits abuse per client."""
    key = _get_rag_key_from_request(request)
    if key:
        return f"key:{key}"
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key, default_limits=[])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RAG API process starting")
    try:
        from src.retrieval import retrieve as retrieve_mod

        retrieve_mod.preload_retrieval()
        logger.info("Retrieval preload completed at startup")
    except FileNotFoundError as e:
        logger.warning("Retrieval preload skipped (artifacts not on disk): %s", e)
    except Exception:
        logger.exception("Retrieval preload failed")
    yield
    logger.info("RAG API process shutting down")


app = FastAPI(
    title="RAG Document QA API",
    version="0.1.0",
    description=API_DESCRIPTION,
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    },
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=_allow_origins, allow_methods=["*"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version="3.1.0",
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
    )
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {}).update(
        {
            "RAGApiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "X-RAG-API-Key",
                "description": (
                    "Required when the server sets environment variable **RAG_API_KEY**. "
                    "Use the same value the operator configured. Leave empty in Authorize if the server does not use API keys."
                ),
            },
            "RAGBearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "token",
                "description": (
                    "Alternative to **X-RAG-API-Key**: send `Authorization: Bearer <your RAG_API_KEY value>`."
                ),
            },
        }
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get(
    "/health",
    tags=["health"],
    summary="Liveness and readiness",
    response_description="Status flags for process, files on disk, and in-memory retrieval cache.",
)
def health():
    """
    **Always returns HTTP 200** if this handler runs (process is up).

    For load balancers and operators, use the JSON field **`ready`**:

    - `true` only when the FAISS index file exists, chunk metadata CSV exists, and retrieval has been loaded into memory.
    - Also returns `index_file`, `metadata_file`, and `retrieval_loaded` for granular checks.
    """
    from src.retrieval import retrieve as retrieve_mod

    index_ok = FAISS_INDEX_PATH.exists()
    meta_ok = METADATA_PATH.exists()
    loaded = retrieve_mod.is_retrieval_loaded()
    ready = bool(index_ok and meta_ok and loaded)
    return {
        "status": "ok",
        "ready": ready,
        "index_file": index_ok,
        "metadata_file": meta_ok,
        "retrieval_loaded": loaded,
    }


def _ask_limits():
    if _rl_hour:
        return f"{_rl};{_rl_hour}"
    return _rl


@app.post(
    "/ask",
    response_model=AskResponse,
    tags=["qa"],
    summary="Ask a question (RAG)",
    response_description="Answer text, source citations, and optional full retrieved chunks + scores.",
    responses={
        400: {"description": "Whitespace-only `question` after strip (rare if body already validated)."},
        422: {"description": "Validation error: missing `question`, empty string, or invalid JSON shape."},
        401: {
            "description": "Server requires `RAG_API_KEY`; request had no valid `X-RAG-API-Key` or Bearer token."
        },
        429: {"description": "Rate limit exceeded (`API_RATE_LIMIT` / `API_RATE_LIMIT_HOUR`)."},
        503: {
            "description": "LLM not configured (e.g. missing OpenAI credentials) or retrieval index/metadata unavailable."
        },
    },
)
@limiter.limit(_ask_limits())
def post_ask(request: Request, req: AskRequest):
    """
    Run the full RAG pipeline for one question.

    1. **Retrieve** top-k chunks from FAISS using the question embedding.
    2. Optionally apply **`RETRIEVAL_MIN_SCORE`**: if the best score is below the threshold, return a short fallback answer **without** calling the LLM (chunks still included in `retrieved_chunks`).
    3. Otherwise **build a prompt** from retrieved text and call the configured **chat model**.
    4. Return **`answer`**, **`sources`** (citations), and **`retrieved_chunks`** (diagnostic rows including `text` and `score`).

    Use **Authorize** in Swagger when your deployment uses **`RAG_API_KEY`**.
    """
    require_rag_api_key_if_configured(request)
    question = (req.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    try:
        result = ask(question, include_retrieved_chunks=True)
        return AskResponse(**result)
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            raise HTTPException(status_code=503, detail="API key not configured")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.warning("Ask failed: retrieval artifacts missing: %s", e)
        raise HTTPException(status_code=503, detail=f"Index not ready: {e}")
