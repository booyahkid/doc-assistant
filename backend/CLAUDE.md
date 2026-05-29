# Project: AI Document Assistant — Backend

## Stack
- Python 3.11, FastAPI, LangChain v0.3
- ChromaDB for vector storage
- PyMuPDF + python-docx for file parsing
- sentence-transformers for embeddings

## Structure
- backend/main.py       → FastAPI app entry point
- backend/parser.py     → File parsing logic
- backend/rag.py        → RAG pipeline (chunking, embedding, retrieval)
- backend/chat.py       → LLM call + citation logic

## Rules
- Always use async endpoints
- API keys go in .env, never hardcoded
- Every function needs a docstring
- Run: uvicorn main:app --reload