# backend/pipeline/run_pipeline.py

import os
import sys

# This tells Python exactly where to find our other files
# It adds the pipeline folder to Python's search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Also add backend folder so config.py can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor import extract_text
from chunker import chunk_pages
from vector_store import add_to_vector_store


def process_document(file_path: str) -> int:
    """
    Master function that runs the complete pipeline for one file.

    FULL FLOW:
    PDF file
      → extract_text()        → list of pages
      → chunk_pages()         → list of smaller chunks
      → add_to_vector_store() → saved to FAISS on disk

    Returns number of chunks created.
    """

    print(f"\n{'='*50}")
    print(f"Processing: {os.path.basename(file_path)}")

    # STEP 1 — Extract text
    print("Step 1: Extracting text...")
    pages = extract_text(file_path)

    if not pages:
        raise ValueError(f"No readable text found in {file_path}")

    print(f"  → Found {len(pages)} pages with text")

    # STEP 2 — Split into chunks
    print("Step 2: Splitting into chunks...")
    chunks = chunk_pages(pages)
    print(f"  → Created {len(chunks)} chunks")

    # STEP 3 — Embed and store
    print("Step 3: Embedding and storing in vector database...")
    add_to_vector_store(chunks)

    print(f"\nDone! {os.path.basename(file_path)} is now searchable.")
    print(f"{'='*50}\n")

    return len(chunks)


# ── MANUAL TEST ────────────────────────────────────────────────────
if __name__ == "__main__":

    test_file = "data/uploads/hr_policy.pdf"

    if not os.path.exists(test_file):
        print(f"File not found: {test_file}")
        print("Make sure hr_policy.pdf is in backend/data/uploads/")
        sys.exit(1)

    num_chunks = process_document(test_file)

    print("Testing search...")
    from vector_store import search_similar_chunks

    test_queries = [
        "How many leave days do employees get?",
        "Can I work from home?",
        "When is salary paid?",
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = search_similar_chunks(query, k=2)
        for i, doc in enumerate(results):
            print(f"  Result {i+1} "
                  f"[{doc.metadata['source']} | "
                  f"page {doc.metadata['page']}]:")
            print(f"  {doc.page_content[:150]}...")