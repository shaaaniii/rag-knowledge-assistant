# backend/test_rag.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))
sys.path.insert(0, os.path.dirname(__file__))

from pipeline.rag_chain import run_rag

print("\n" + "="*50)
print("TEST 1 — Valid question")
print("="*50)
result = run_rag(
    query="How many annual leave days do employees get?",
    role="employee",
    session_id="test1"
)
print(f"Answer:     {result['answer']}")
print(f"Sources:    {result['sources']}")
print(f"Confidence: {result['confidence']}")

print("\n" + "="*50)
print("TEST 2 — Question NOT in the document")
print("="*50)
result = run_rag(
    query="What is the recipe for chocolate cake?",
    role="employee",
    session_id="test2"
)
print(f"Answer: {result['answer']}")

print("\n" + "="*50)
print("TEST 3 — Follow up question (memory test)")
print("="*50)
result = run_rag(
    query="What about part time employees, do they get less?",
    role="employee",
    session_id="test1"   # same session as TEST 1
)
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")