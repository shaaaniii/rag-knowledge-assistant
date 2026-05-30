import os
import sys
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _load_config():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.py"
    )
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

config = _load_config()
VECTOR_STORE_PATH = config.VECTOR_STORE_PATH

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from embedder import get_embedding_model


def build_vector_store(chunks: list[Document]):
    embeddings = get_embedding_model()
    print(f"  Embedding {len(chunks)} chunks... (this may take a minute)")
    vector_store = FAISS.from_documents(chunks, embeddings)
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"  Vector store saved to: {VECTOR_STORE_PATH}")
    return vector_store


def add_to_vector_store(chunks: list[Document]):
    embeddings = get_embedding_model()
    index_path = os.path.join(VECTOR_STORE_PATH, "index.faiss")

    if os.path.exists(index_path):
        existing = FAISS.load_local(
            VECTOR_STORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        existing.add_documents(chunks)
        existing.save_local(VECTOR_STORE_PATH)
        print(f"  Added {len(chunks)} chunks to existing vector store")
    else:
        build_vector_store(chunks)


def load_vector_store():
    index_path = os.path.join(VECTOR_STORE_PATH, "index.faiss")

    if not os.path.exists(index_path):
        raise FileNotFoundError(
            "No vector store found. Please upload a document first."
        )

    embeddings = get_embedding_model()
    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def search_similar_chunks(query: str, k: int = 5) -> list[Document]:
    vector_store = load_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results
def search_with_scores(query: str, k: int = 5) -> list:
    """
    Same as search_similar_chunks but also returns
    the similarity score for each chunk.

    Score is a distance — LOWER means MORE similar:
    0.0  = perfect match
    0.5  = decent match  
    1.0+ = probably not relevant

    Returns list of (Document, score) tuples.
    """
    vector_store = load_vector_store()
    results = vector_store.similarity_search_with_score(query, k=k)
    return results

def search_with_scores_filtered(query: str, 
                                 source_filter: str = None,
                                 k: int = 5) -> list:
    """
    Search vector store but only return chunks from
    a specific document if source_filter is provided.

    source_filter = "hr_policy.pdf"
    → only returns chunks where metadata source == hr_policy.pdf

    source_filter = None
    → searches all documents (old behavior)
    """
    vector_store = load_vector_store()

    if source_filter:
        # LangChain FAISS filter by metadata
        results = vector_store.similarity_search_with_score(
            query,
            k=k,
            filter={"source": source_filter}
        )
    else:
        results = vector_store.similarity_search_with_score(query, k=k)

    return results

def search_multi_document(query: str,
                          selected_docs: list = None,
                          k: int = 5) -> list:
    """
    Search across multiple selected documents.

    selected_docs = ["hr_policy.pdf", "report.pdf"]
    → searches ONLY those documents

    selected_docs = None or []
    → searches ALL documents
    """
    vector_store = load_vector_store()

    if selected_docs and len(selected_docs) > 0:
        # Search each document separately then combine results
        all_results = []
        k_per_doc = max(2, k // len(selected_docs))

        for doc_name in selected_docs:
            try:
                results = vector_store.similarity_search_with_score(
                    query,
                    k=k_per_doc,
                    filter={"source": doc_name}
                )
                all_results.extend(results)
            except Exception as e:
                print(f"[Search] Error searching {doc_name}: {e}")

        # Sort all results by score (lowest = most relevant)
        all_results.sort(key=lambda x: x[1])

        # Return top k
        return all_results[:k]
    else:
        return vector_store.similarity_search_with_score(query, k=k)