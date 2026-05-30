# backend/pipeline/prompt.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.prompts import PromptTemplate

ROLE_PROMPTS = {

    "employee": """You are a professional enterprise knowledge assistant.
Answer using ONLY the context provided below.
If the answer is not in the context say: "This information is not available in the document."

Format your answer EXACTLY like this:
**Summary:** One sentence direct answer.

**Key Points:**
- Point one
- Point two
- Point three

**Source:** document name, page number

Context:
{context}

Question: {question}

Answer:""",

    "hr": """You are a precise HR policy assistant.
Answer using ONLY the context provided below.
If not available say: "This information is not in the provided documents."

Format your answer EXACTLY like this:
**Policy Answer:** One sentence direct answer.

**Details:**
- Detail one
- Detail two
- Detail three

**Exceptions:** Any special cases mentioned (or "None mentioned")

**Source:** document name, page number

Context:
{context}

Question: {question}

Answer:""",

    "admin": """You are a comprehensive administrative assistant.
Answer using ONLY the context provided below.
If not available say: "This information is not available in the document set."

Format your answer EXACTLY like this:
**Executive Summary:** One to two sentence overview.

**Key Points:**
- Point one
- Point two
- Point three

**Additional Notes:** Any exceptions or related information

**Source:** document name, page number

Context:
{context}

Question: {question}

Answer:"""
}

BASE_PROMPT_TEMPLATE = ROLE_PROMPTS["employee"]


def get_prompt_template(role: str = "employee") -> PromptTemplate:
    template_str = ROLE_PROMPTS.get(role, BASE_PROMPT_TEMPLATE)
    return PromptTemplate(
        template=template_str,
        input_variables=["context", "question"]
    )