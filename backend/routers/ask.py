# backend/routers/ask.py

import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "pipeline"))

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from pipeline.rag_chain import run_rag
from models.requests import AskRequest
from models.responses import AskResponse, SourceInfo
from database.db import get_db, save_message

router = APIRouter(prefix="/ask", tags=["Chat"])


@router.post("/", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    start = time.time()

    try:
        result = run_rag(
            query=request.query,
            role=request.role,
            session_id=request.session_id,
            k=request.k,
            active_document=request.active_document,
            selected_documents=request.selected_documents
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="No documents found. Please upload documents first."
        )
    except Exception as e:
        print(f"[Ask] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

    save_message(db, request.session_id, "user",      request.query)
    save_message(db, request.session_id, "assistant", result["answer"])

    elapsed = round(time.time() - start, 2)
    print(f"[Ask] Done in {elapsed}s | Confidence: {result['confidence']}")

    sources = [
        SourceInfo(source=s["source"], page=s["page"])
        for s in result["sources"]
    ]

    return AskResponse(
        answer=result["answer"],
        sources=sources,
        confidence=result["confidence"],
        num_chunks_used=result["num_chunks_used"],
        session_id=request.session_id
    )