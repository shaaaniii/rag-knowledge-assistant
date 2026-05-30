# backend/models/responses.py

from pydantic import BaseModel
from typing import Optional, Union


class SourceInfo(BaseModel):
    source: str
    page: Union[int, str]


class AskResponse(BaseModel):
    """
    What POST /ask returns.

    Example:
    {
        "answer": "Employees get 20 days...",
        "sources": [{"source": "hr_policy.pdf", "page": 1}],
        "confidence": "high",
        "num_chunks_used": 5,
        "session_id": "user_123"
    }
    """
    answer: str
    sources: list[SourceInfo]
    confidence: str
    num_chunks_used: int
    session_id: str


class UploadResponse(BaseModel):
    """What POST /upload-doc returns."""
    message: str
    filename: str
    num_chunks: int
    status: str


class HistoryMessage(BaseModel):
    role: str
    content: str


class HistoryResponse(BaseModel):
    """What GET /history returns."""
    session_id: str
    messages: list[HistoryMessage]
    total_messages: int


class FeedbackResponse(BaseModel):
    """What POST /feedback returns."""
    message: str
    status: str