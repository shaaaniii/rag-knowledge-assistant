# backend/pipeline/chunker.py

import os
import sys

# Add pipeline folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add backend folder to path so config.py can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_pages(pages: list) -> list:
    """
    Takes the list of pages from extractor.py and cuts each page's
    text into smaller overlapping pieces called chunks.

    WHY CHUNK?
    GPT-4o can only read a limited amount of text at once.
    A 100 page PDF is too big. We cut it into small pieces
    and only send the RELEVANT pieces to the AI.

    WHY OVERLAP?
    If a sentence falls right at a chunk boundary we would lose it.
    Overlap means each chunk shares some text with the previous one
    so nothing important gets cut off.

    INPUT:  pages → list of dicts from extractor.py
    OUTPUT: list of LangChain Document objects
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,        # 500 characters per chunk
        chunk_overlap=CHUNK_OVERLAP,  # 50 characters shared with next chunk
        length_function=len,
    )

    all_chunks = []

    for page in pages:
        # Split the page text into smaller strings
        text_chunks = splitter.split_text(page["text"])

        # Wrap each string in a LangChain Document object
        # Document has two parts:
        #   page_content → the actual text
        #   metadata     → where it came from
        for i, chunk_text in enumerate(text_chunks):
            doc = Document(
                page_content=chunk_text,
                metadata={
                    "source": page["source"],
                    "page":   page["page"],
                    "chunk":  i + 1
                }
            )
            all_chunks.append(doc)

    return all_chunks