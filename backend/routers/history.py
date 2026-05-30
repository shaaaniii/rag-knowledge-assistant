# backend/routers/history.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.db import get_db, get_messages
from models.responses import HistoryResponse, HistoryMessage

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/", response_model=HistoryResponse)
def get_chat_history(
    session_id: str = Query(..., min_length=1, max_length=100),
    db: Session = Depends(get_db)
):
    """Returns full conversation history for a session."""
    db_messages = get_messages(db, session_id)

    messages = [
        HistoryMessage(role=msg.role, content=msg.content)
        for msg in db_messages
    ]

    return HistoryResponse(
        session_id=session_id,
        messages=messages,
        total_messages=len(messages)
    )


@router.delete("/")
def clear_chat_history(
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Clears all messages for a session. Called on New Chat."""
    from database.db import ChatMessage
    from pipeline.memory import clear_history

    deleted = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .delete()
    )
    db.commit()
    clear_history(session_id)

    return {
        "message": f"Cleared {deleted} messages for session {session_id}",
        "status": "success"
    }