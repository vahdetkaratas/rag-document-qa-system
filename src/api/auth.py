"""
Optional API key: RAG_API_KEY or comma-separated RAG_API_KEY=a,b,c
Header: X-RAG-API-Key or Authorization: Bearer <key>
If empty, no validation (local demo).
"""
import os

from fastapi import HTTPException, Request


def _get_rag_key_from_request(request: Request) -> str:
    """Extract RAG API key from request headers. Returns "" if not sent. Used for rate-limit key when RAG_API_KEY is set."""
    key = (request.headers.get("X-RAG-API-Key") or "").strip()
    if not key:
        auth = (request.headers.get("Authorization") or "").strip()
        if auth.lower().startswith("bearer "):
            key = auth[7:].strip()
    return key


def require_rag_api_key_if_configured(request: Request) -> None:
    raw = (os.getenv("RAG_API_KEY") or "").strip()
    if not raw:
        return
    allowed = {x.strip() for x in raw.split(",") if x.strip()}
    key = _get_rag_key_from_request(request)
    if key not in allowed:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid API key (use X-RAG-API-Key or Authorization: Bearer)",
        )
