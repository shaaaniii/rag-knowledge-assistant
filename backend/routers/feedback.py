# backend/routers/feedback.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db, save_feedback, Feedback
from models.requests import FeedbackRequest
from models.responses import FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Stores user feedback on an answer."""
    save_feedback(
        db=db,
        session_id=request.session_id,
        message_index=request.message_index,
        rating=request.rating,
        comment=request.comment
    )
    print(f"[Feedback] {request.rating} from session {request.session_id}")

    return FeedbackResponse(message="Feedback received!", status="success")


@router.get("/stats")
def get_feedback_stats(db: Session = Depends(get_db)):
    """Returns feedback statistics for the admin dashboard."""
    all_feedback = db.query(Feedback).all()
    total        = len(all_feedback)

    if total == 0:
        return {"total": 0, "helpful": 0, "not_helpful": 0, "helpful_pct": 0}

    helpful     = sum(1 for f in all_feedback if f.rating == "helpful")
    not_helpful = total - helpful

    return {
        "total":       total,
        "helpful":     helpful,
        "not_helpful": not_helpful,
        "helpful_pct": round((helpful / total) * 100, 1)
    }