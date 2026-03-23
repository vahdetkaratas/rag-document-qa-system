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
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.auth import require_rag_api_key_if_configured, _get_rag_key_from_request
from src.api.schemas import AskRequest, AskResponse
from src.api.service import ask
from src.config import FAISS_INDEX_PATH, METADATA_PATH

logger = logging.getLogger(__name__)

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


app = FastAPI(title="RAG Document QA API", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=_allow_origins, allow_methods=["*"])


@app.get("/health")
def health():
    """
    Process is up (always 200 if this handler runs).
    Use `ready` for routing: true only when artifact files exist and retrieval cache is loaded in memory.
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


@app.post("/ask", response_model=AskResponse)
@limiter.limit(_ask_limits())
def post_ask(request: Request, req: AskRequest):
    """Answer a question using retrieved context and LLM."""
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
