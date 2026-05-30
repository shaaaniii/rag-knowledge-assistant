# backend/pipeline/embedder.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import OllamaEmbeddings


def get_embedding_model():
    """
    Returns the Ollama embedding model.
    Runs 100% locally on your laptop — no API key, no cost.

    nomic-embed-text is a high quality embedding model
    that works just as well as OpenAI's for our purposes.
    """

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
    )

    return embeddings