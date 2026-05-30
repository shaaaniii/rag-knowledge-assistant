# backend/routers/upload.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), "pipeline"))

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import aiofiles
import shutil

from pipeline.run_pipeline import process_document
from models.responses import UploadResponse
from database.db import get_db, log_document
from config import UPLOAD_DIR, VECTOR_STORE_PATH

router = APIRouter(prefix="/upload-doc", tags=["Documents"])

os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE_MB   = 50


@router.post("/", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Use PDF or TXT."
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Max is {MAX_FILE_SIZE_MB}MB"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    print(f"[Upload] Saved: {file_path}")

    def process_and_log():
        try:
            num_chunks = process_document(file_path)
            log_document(db, file.filename, num_chunks)
            print(f"[Upload] Done: {num_chunks} chunks created")
        except Exception as e:
            print(f"[Upload] Error: {e}")

    background_tasks.add_task(process_and_log)

    return UploadResponse(
        message="File received and processing in background",
        filename=file.filename,
        num_chunks=0,
        status="processing"
    )


@router.get("/list")
def list_documents(db: Session = Depends(get_db)):
    """Returns all uploaded documents."""
    from database.db import UploadedDocument
    docs = (
        db.query(UploadedDocument)
        .order_by(UploadedDocument.uploaded_at.desc())
        .all()
    )
    return {
        "documents": [
            {
                "filename":    d.filename,
                "num_chunks":  d.num_chunks,
                "uploaded_at": d.uploaded_at.isoformat(),
                "status":      d.status
            }
            for d in docs
        ]
    }


@router.delete("/{filename}")
def delete_document(filename: str, db: Session = Depends(get_db)):
    """
    Deletes a document completely:
    1. Removes the file from disk
    2. Removes from database
    3. Rebuilds the vector store without that document
    """
    from database.db import UploadedDocument
    import glob

    # ── DELETE FILE FROM DISK ──────────────────────────────────────
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"[Delete] Removed file: {file_path}")
    else:
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found"
        )

    # ── REMOVE FROM DATABASE ───────────────────────────────────────
    db.query(UploadedDocument).filter(
        UploadedDocument.filename == filename
    ).delete()
    db.commit()
    print(f"[Delete] Removed from database: {filename}")

    # ── REBUILD VECTOR STORE WITHOUT DELETED DOC ───────────────────
    # Delete old index
    if os.path.exists(VECTOR_STORE_PATH):
        shutil.rmtree(VECTOR_STORE_PATH)
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    # Get remaining files
    remaining = [
        f for f in os.listdir(UPLOAD_DIR)
        if f.endswith('.pdf') or f.endswith('.txt')
    ]

    if remaining:
        print(f"[Delete] Rebuilding vector store with {len(remaining)} files...")
        for fname in remaining:
            fpath = os.path.join(UPLOAD_DIR, fname)
            try:
                process_document(fpath)
                print(f"[Delete] Re-indexed: {fname}")
            except Exception as e:
                print(f"[Delete] Error re-indexing {fname}: {e}")
        print("[Delete] Vector store rebuilt successfully")
    else:
        print("[Delete] No remaining documents — vector store cleared")

    return {
        "message":  f"'{filename}' deleted successfully",
        "status":   "success",
        "remaining": len(remaining)
    }