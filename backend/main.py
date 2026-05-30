# backend/main.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pipeline"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from routers.upload   import router as upload_router
from routers.ask      import router as ask_router
from routers.history  import router as history_router
from routers.feedback import router as feedback_router
from middleware.logging import log_requests
from database.db import create_tables

app = FastAPI(
    title="Enterprise AI Knowledge Assistant",
    description="RAG-based chatbot for internal documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — allows the React frontend to call this API
# CORS — allows the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins in development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],

)

# Log every request automatically
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)


@app.on_event("startup")
async def startup():
    """Runs once when server starts."""
    create_tables()
    print("Database ready")
    print("Server running at http://localhost:8000")
    print("API docs at      http://localhost:8000/docs")


# Register all routers
app.include_router(upload_router)
app.include_router(ask_router)
app.include_router(history_router)
app.include_router(feedback_router)


@app.get("/")
def root():
    return {
        "status":  "running",
        "message": "Enterprise AI Knowledge Assistant API",
        "docs":    "http://localhost:8000/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}