# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()

# No API key needed for Ollama — runs locally
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "data/faiss_index")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))