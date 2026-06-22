# Customer Support AI Assistant (RAG + FastAPI)
---
title: Customer Support AI
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---
---

## Problem Statement

Users frequently ask repetitive support questions that can be answered using existing help-center documentation. Instead of routing every query to a human agent, this assistant:

- Accepts natural language support questions from users
- Retrieves the most relevant help-center documents using vector search
- Generates accurate, context-aware answers using a Large Language Model (RAG pipeline)

---

## Planned Features

- **Document Ingestion** — Load and parse support documents from local files or URLs
- **Embeddings + Vector Search** — Chunk documents, embed them, and store in a vector database (ChromaDB)
- **RAG-based Q&A** — Retrieve top-k relevant chunks and pass them to an LLM for answer generation
- **FastAPI Endpoint** — REST API to accept user queries and return AI-generated answers
- **Ticket Categorization** — Automatically classify incoming queries (e.g., billing, technical, shipping)
- **Entity Extraction** — Extract key info from queries (order IDs, email addresses, product names)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| API Framework | FastAPI |
| RAG Orchestration | LangChain |
| Vector Database | ChromaDB |
| Embeddings | OpenAI / HuggingFace (planned) |
| LLM | OpenAI GPT / Claude (planned) |
| Version Control | Git + GitHub |

---

## Project Structure

```
customer-support-ai-assistant/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration and environment variables
│   ├── rag/
│   │   ├── loader.py        # Document loading
│   │   ├── chunker.py       # Text chunking
│   │   ├── embedder.py      # Embedding generation
│   │   ├── retriever.py     # Vector search / retrieval
│   │   └── prompt_builder.py # Prompt construction for LLM
│   ├── api/
│   │   └── routes.py        # API route definitions
│   └── utils/
│       └── helpers.py       # Utility functions
├── data/
│   └── sample_support_docs/ # Sample knowledge base documents
├── notebooks/
│   └── rag_experiments.ipynb
├── requirements.txt
├── README.md
└── .gitignore
```

---

*Day 1 — Foundation. Structure first, logic next.*
