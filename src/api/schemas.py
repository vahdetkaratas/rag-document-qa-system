"""API request/response schemas. RAG_SYSTEM_DESIGN §7, IMPLEMENTATION_REFERENCE §8."""
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class SourceCitation(BaseModel):
    document: str
    page: int
    chunk_id: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
    retrieved_chunks: list[dict] | None = None
