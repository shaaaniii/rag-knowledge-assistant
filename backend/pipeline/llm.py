# backend/pipeline/llm.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_ollama import ChatOllama


def get_llm(temperature: float = 0.0):
    """
    Returns Llama 3.2 via Ollama.

    num_predict = max tokens in response (800 = detailed but not rambling)
    repeat_penalty = stops the model repeating itself
    """
    llm = ChatOllama(
        model="llama3.2:1b",
        temperature=temperature,
        num_predict=800,
        repeat_penalty=1.1,
    )
    return llm