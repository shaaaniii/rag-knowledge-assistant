# backend/models/requests.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List





class AskRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    session_id: str = Field(default="default", min_length=1, max_length=100)
    role: str = Field(default="employee")
    k: int = Field(default=5, ge=1, le=20)

    # Single doc filter (old)
    active_document: Optional[str] = Field(default=None)

    # Multi doc filter (new) — list of filenames to search
    selected_documents: Optional[List[str]] = Field(default=None)

    @field_validator("role")
    @classmethod
    def role_must_be_valid(cls, v):
        allowed = ["employee", "hr", "admin"]
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v):
        if v.strip() == "":
            raise ValueError("Query cannot be blank")
        return v.strip()


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=100)
    message_index: int = Field(..., ge=0)
    rating: str = Field(...)
    comment: Optional[str] = Field(default=None, max_length=500)

    @field_validator("rating")
    @classmethod
    def rating_must_be_valid(cls, v):
        if v not in ["helpful", "not_helpful"]:
            raise ValueError("Rating must be helpful or not_helpful")
        return v