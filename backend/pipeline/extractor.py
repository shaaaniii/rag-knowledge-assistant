# backend/pipeline/extractor.py

import os
import sys
import fitz  # PyMuPDF

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Opens a PDF file and pulls out all the text, page by page.

    INPUT:  file_path → full path to the PDF
    OUTPUT: list of dicts, one per page
            [{"page": 1, "text": "...", "source": "hr_policy.pdf"}, ...]
    """

    filename = os.path.basename(file_path)
    doc = fitz.open(file_path)
    pages = []

    for page_index, page in enumerate(doc):
        text = page.get_text()

        # skip blank or image-only pages
        if len(text.strip()) < 30:
            continue

        pages.append({
            "page": page_index + 1,
            "text": text.strip(),
            "source": filename
        })

    doc.close()
    return pages


def extract_text_from_txt(file_path: str) -> list[dict]:
    """
    Reads a plain .txt file.
    Treats the whole file as one page.
    """
    filename = os.path.basename(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if len(text.strip()) < 30:
        return []

    return [{
        "page": 1,
        "text": text.strip(),
        "source": filename
    }]


def extract_text(file_path: str) -> list[dict]:
    """
    Master function — picks the right extractor based on file type.
    Supports: .pdf and .txt
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .pdf or .txt")