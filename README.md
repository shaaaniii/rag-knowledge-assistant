# 🧠 Enterprise AI Knowledge Assistant

A production-style **RAG (Retrieval-Augmented Generation)** chatbot
that answers questions from your uploaded documents using local LLMs.
Built as a full-stack AI application with FastAPI backend and React frontend.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![React](https://img.shields.io/badge/React-18-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2-orange)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-red)

---

## 🎯 What It Does

Upload any PDF or TXT document and ask questions about it in
natural language. The assistant finds the most relevant sections
and generates professional structured answers — citing sources.

**Use cases:**
- HR policy documents
- Project reports
- Meeting minutes
- Legal contracts
- Research papers
- Financial reports

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Document Upload | Upload PDF and TXT files |
| 🗑️ Document Delete | Remove documents from knowledge base |
| ☑️ Multi-Document Select | Search one or multiple documents |
| 💬 RAG Pipeline | Semantic search + LLM answer generation |
| 🧠 Conversation Memory | Follow-up questions work naturally |
| 📎 Source Citations | Every answer cites document and page |
| 👍 Feedback System | Rate answers helpful or not helpful |
| 👤 Role-Based Prompts | Employee, HR, Admin personas |
| ⚡ Local LLM | Runs 100% free with Ollama — no API costs |

---

🏗️ Architecture
User Question
↓
FastAPI Backend (/ask)
↓
FAISS Vector Store (semantic search)
↓
Top-K relevant chunks retrieved
↓
Prompt built with context + question
↓
Llama 3 via Ollama (local LLM)
↓
Structured answer + sources returned
↓
React Frontend displays response


---

## 🛠️ Tech Stack

**Backend**
- Python 3.11
- FastAPI — REST API
- LangChain — RAG orchestration
- FAISS — Vector database
- Ollama — Local LLM runner
- Llama 3.2 — Language model
- nomic-embed-text — Embedding model
- SQLite — Chat history and feedback
- PyMuPDF — PDF text extraction

**Frontend**
- React 18
- Vite
- Axios

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com/download) installed

### 1. Clone the repository
```bash
git clone https://github.com/shaaaniii/rag-knowledge-assistant.git
cd rag-knowledge-assistant
```

### 2. Install Ollama models
```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

### 3. Backend setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Start the backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

### 6. Open the app
http://localhost:5173/

---

## 📁 Project Structure
rag-assistant/
├── backend/
│ ├── pipeline/
│ │ ├── extractor.py
│ │ ├── chunker.py
│ │ ├── embedder.py
│ │ ├── vector_store.py
│ │ ├── rag_chain.py
│ │ ├── llm.py
│ │ ├── prompt.py
│ │ └── memory.py
│ ├── routers/
│ │ ├── upload.py
│ │ ├── ask.py
│ │ ├── history.py
│ │ └── feedback.py
│ ├── models/
│ ├── database/
│ └── main.py
├── frontend/
│ └── src/
│ ├── App.jsx
│ └── App.css
└── requirements.txt

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /upload-doc/ | Upload a document |
| GET | /upload-doc/list | List all documents |
| DELETE | /upload-doc/{filename} | Delete a document |
| POST | /ask/ | Ask a question |
| GET | /history/ | Get chat history |
| DELETE | /history/ | Clear chat history |
| POST | /feedback/ | Submit feedback |
| GET | /feedback/stats | View feedback stats |

---

## 💡 How RAG Works

1. **Upload** — PDF is parsed, text extracted page by page
2. **Chunk** — Text split into 500-character overlapping segments
3. **Embed** — Each chunk converted to a vector using nomic-embed-text
4. **Store** — Vectors saved in FAISS vector database
5. **Query** — User question embedded and compared to all chunks
6. **Retrieve** — Top 5 most similar chunks returned
7. **Generate** — LLM reads chunks + question, writes structured answer
8. **Cite** — Answer includes source document and page number

---

## 🎓 Built For

This project was built as part of an AI/ML internship portfolio
demonstrating skills in:
- Generative AI and LLMs
- RAG architecture
- Vector databases
- REST API development
- Full-stack development
- Local AI deployment