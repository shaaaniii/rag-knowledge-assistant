# backend/pipeline/rag_chain.py

import os
import sys
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_store import search_multi_document
from llm import get_llm
from prompt import get_prompt_template
from memory import add_to_history, format_history_for_prompt


def format_context(chunks_with_scores: list) -> str:
    parts = []
    for doc, score in chunks_with_scores:
        source = doc.metadata.get("source", "Unknown")
        page   = doc.metadata.get("page", "?")
        part   = f"From {source} (page {page}):\n{doc.page_content}"
        parts.append(part)
    return "\n\n---\n\n".join(parts)


def extract_sources(chunks_with_scores: list) -> list:
    seen    = set()
    sources = []
    for doc, score in chunks_with_scores:
        source = doc.metadata.get("source", "Unknown")
        page   = doc.metadata.get("page", "?")
        key    = (source, page)
        if key not in seen:
            seen.add(key)
            sources.append({"source": source, "page": page})
    return sources


def calculate_confidence(chunks_with_scores: list) -> str:
    if not chunks_with_scores:
        return "none"
    best_score = min(score for _, score in chunks_with_scores)
    print(f"[RAG] Best score: {best_score:.3f}")
    if best_score < 0.8:
        return "high"
    elif best_score < 1.2:
        return "medium"
    else:
        return "low"


def clean_answer(text: str) -> str:
    phrases = [
        "I don't have that information. Please check with HR.",
        "I don't have that information. Please check with your HR department.",
        "PROFESSIONAL ANSWER:", "PROFESSIONAL HR ANSWER:",
        "COMPREHENSIVE ANSWER:", "STRICT RULES:",
        "Use ONLY the context.", "Answer:", "Direct Answer:",
    ]
    for phrase in phrases:
        text = text.replace(phrase, "")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def run_rag(
    query: str,
    role: str = "employee",
    session_id: str = "default",
    k: int = 5,
    active_document: str = None,
    selected_documents: list = None
) -> dict:
    """
    Main RAG function.

    selected_documents = ["hr.pdf", "report.pdf"] → search those only
    active_document    = "hr.pdf"                 → search one doc
    both None                                     → search everything
    """

    # ── DETERMINE WHICH DOCS TO SEARCH ────────────────────────────
    # selected_documents takes priority (multi-select)
    # active_document is fallback (single select)
    # None = search all
    if selected_documents and len(selected_documents) > 0:
        docs_to_search = selected_documents
    elif active_document:
        docs_to_search = [active_document]
    else:
        docs_to_search = None

    # ── HISTORY ───────────────────────────────────────────────────
    history_str    = format_history_for_prompt(session_id)
    enriched_query = (
        f"{history_str}\nCurrent question: {query}"
        if history_str else query
    )

    # ── SEARCH ────────────────────────────────────────────────────
    print(f"\n[RAG] Query: '{query}'")
    print(f"[RAG] Searching: {docs_to_search or 'ALL'}")

    try:
        chunks_with_scores = search_multi_document(
            enriched_query,
            selected_docs=docs_to_search,
            k=k
        )
    except FileNotFoundError:
        raise FileNotFoundError("No documents found. Please upload first.")

    print(f"[RAG] Found {len(chunks_with_scores)} chunks:")
    for doc, score in chunks_with_scores:
        print(f"  {score:.3f} | {doc.metadata.get('source')} "
              f"p.{doc.metadata.get('page')}")

    # ── NO RESULTS ────────────────────────────────────────────────
    if not chunks_with_scores:
        msg = "The available documents do not contain information on this topic."
        add_to_history(session_id, "user", query)
        add_to_history(session_id, "assistant", msg)
        return {
            "answer": msg, "sources": [],
            "confidence": "none", "num_chunks_used": 0
        }

    # ── BUILD + SEND PROMPT ───────────────────────────────────────
    context         = format_context(chunks_with_scores)
    prompt_template = get_prompt_template(role)
    full_question   = (
        f"{history_str}\n\nCurrent question: {query}"
        if history_str else query
    )
    filled_prompt = prompt_template.format(
        context=context, question=full_question
    )

    print(f"[RAG] Sending to LLM...")
    llm      = get_llm(temperature=0.0)
    response = llm.invoke(filled_prompt)
    answer   = clean_answer(response.content)
    print(f"[RAG] Done!")

    add_to_history(session_id, "user",      query)
    add_to_history(session_id, "assistant", answer)

    return {
        "answer":          answer,
        "sources":         extract_sources(chunks_with_scores),
        "confidence":      calculate_confidence(chunks_with_scores),
        "num_chunks_used": len(chunks_with_scores)
    }