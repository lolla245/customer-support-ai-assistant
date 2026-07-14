---
title: Customer Support AI
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# Customer Support AI Assistant (RAG + FastAPI + Groq)

A production-style, full-stack Retrieval-Augmented Generation (RAG) customer support assistant. Users ask natural-language support questions; the system retrieves the most relevant help-center documents via vector search and generates accurate, context-aware answers using an LLM — complete with authentication, streaming responses, an admin panel for managing the knowledge base, and operational safeguards like rate limiting and structured logging.

**GitHub:** https://github.com/lolla245/customer-support-ai-assistant
**Live Demo:** https://lolla245-customer-support-ai.hf.space

---

## Problem Statement

Users frequently ask repetitive support questions that can be answered using existing help-center documentation. Instead of routing every query to a human agent, this assistant:

- Accepts natural language support questions from users
- Retrieves the most relevant help-center documents using vector search
- Generates accurate, context-aware answers using a Large Language Model (RAG pipeline)
- Remembers conversation context across turns
- Streams answers back in real time
- Lets an admin manage the underlying knowledge base without touching code

---

## Features

### Core RAG Pipeline
- Document ingestion from `.txt` support files
- Chunking (500-char chunks) and embedding into **ChromaDB** (persistent vector store)
- Category-aware semantic retrieval
- Prompt construction from retrieved chunks + conversation history

### NLP / Query Understanding
- **Ticket classification** across 6 categories (Billing, Login/Account, Technical, Order/Payment, Refund/Cancellation, General)
- **Structured extraction** per query: category, priority, user intent, sentiment, and named entities (order ID, email, date, amount, plan name)
- Confidence scoring based on retrieval strength

### Conversational Experience
- **Conversation memory** — session-based, last 3 turns injected into the prompt so follow-up questions ("how long is that valid?") resolve correctly
- **Streaming responses** — token-by-token via Server-Sent Events (SSE), rendered live in the UI
- **Feedback system** — 👍 / 👎 on every answer, recorded server-side with stats endpoint
- **Conversation export** — download as TXT or print to PDF
- **Sidebar chat history** — past conversations saved, reloadable, and deletable, with New Chat / Home navigation and a collapsible sidebar

### Auth & Admin
- **JWT authentication** — signup/login endpoints, bcrypt password hashing, bearer-token-protected chat endpoints
- **Admin panel** (key-protected) — list, upload, and delete knowledge-base documents; deleting/uploading automatically rebuilds the vector index

### Production Hardening
- **Rate limiting** — sliding-window limiter (10 requests / 60s per IP) on chat endpoints, returns clean 429s
- **Structured logging** — every request logged with method, path, status, and latency to both console and `logs/app.log`
- **Global exception handling** — unhandled errors return a clean JSON error instead of a raw traceback

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| API Framework | FastAPI + Uvicorn |
| Vector Database | ChromaDB (persistent) |
| Embeddings | all-MiniLM-L6-v2 (local) |
| LLM | Groq — `llama-3.3-70b-versatile` |
| Auth | PyJWT + Passlib (bcrypt) |
| Frontend | HTML / CSS / vanilla JS (dark-themed, streaming chat UI, sidebar) |
| Deployment | Docker → Hugging Face Spaces |
| Version Control | Git + GitHub |

---

## Project Structure

```
customer-support-ai-assistant/
├── app/
│   ├── main.py                 # FastAPI app entry point, middleware, logging, rate limiting
│   ├── config.py                # Configuration and environment variables
│   ├── auth/
│   │   ├── security.py          # Password hashing, JWT create/verify, user store
│   │   └── auth_routes.py       # /auth/signup, /auth/login, /auth/me
│   ├── rag/
│   │   ├── loader.py            # Document loading
│   │   ├── chunker.py           # Text chunking
│   │   ├── embedder.py          # Embedding generation + ChromaDB ingest
│   │   ├── retriever.py         # Category-aware vector search
│   │   ├── prompt_builder.py    # Prompt construction for LLM
│   │   ├── ticket_classifier.py # 6-category classification
│   │   └── support_extractor.py # Structured metadata extraction (priority, intent, sentiment, entities)
│   ├── api/
│   │   ├── routes.py            # /ask, /ask/stream, /feedback, /feedback/stats
│   │   └── admin_routes.py      # /admin/documents (list/upload/delete)
│   ├── static/
│   │   ├── index.html           # Main chat UI (sidebar, streaming, export)
│   │   ├── login.html           # Login / signup page
│   │   └── admin.html           # Knowledge-base admin panel
│   └── utils/
│       └── helpers.py           # Query logging (JSONL)
├── Data/
│   └── sample_support_docs/     # Knowledge base (.txt files)
├── chroma_db/                   # Persistent vector store (generated)
├── logs/                        # app.log + query_logs.jsonl
├── Notebooks/
│   └── rag_experiments.ipynb    # Chunking + retrieval quality experiments
├── requirements.txt
├── Dockerfile
├── README.md
└── .gitignore
```

---

## API Overview

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/` | GET | — | Serves the chat UI |
| `/auth/signup` | POST | — | Create a user, returns JWT |
| `/auth/login` | POST | — | Authenticate, returns JWT |
| `/auth/me` | GET | Bearer token | Returns current username |
| `/ask` | POST | Bearer token | Full (non-streamed) RAG answer |
| `/ask/stream` | POST | Bearer token | SSE-streamed RAG answer |
| `/feedback` | POST | — | Record 👍/👎 on an answer |
| `/feedback/stats` | GET | — | Aggregate feedback counts |
| `/admin/documents` | GET | Admin key | List knowledge-base files |
| `/admin/documents/upload` | POST | Admin key | Upload a `.txt` file, rebuilds index |
| `/admin/documents/{filename}` | DELETE | Admin key | Delete a file, rebuilds index |

### Sample `/ask` Response
```json
{
  "query": "My payment failed, I want a refund",
  "category": "billing",
  "priority": "high",
  "intent": "ask_refund",
  "sentiment": "frustrated",
  "entities": {"date": "yesterday", "amount": null},
  "retrieved_sources": ["refund_policy.txt"],
  "answer": "...",
  "confidence_note": "high",
  "timestamp": "2026-06-24T10:57:48"
}
```

---

## Setup Instructions

### 1. Python Version
Use **Python 3.10** (newer versions like 3.14 lack pre-built wheels for several dependencies and will force slow/broken source builds).

```bash
py -3.10 -m venv venv
venv\Scripts\Activate.ps1      # Windows
# source venv/bin/activate     # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key
JWT_SECRET=your_random_secret
ADMIN_KEY=your_admin_password
```
Get a free Groq API key at https://console.groq.com/keys

### 4. Build the Vector Index
```bash
python app/rag/embedder.py
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000 — you'll be redirected to log in / sign up before accessing the chat.

Admin panel: http://127.0.0.1:8000/static/admin.html

---

## Evaluation Results

- 15 test queries evaluated across all 6 categories
- 13/15 rated "Good", 2/15 "Okay", 0 "Bad"
- **Overall retrieval/answer accuracy: 87%**

---

## Resume Bullets

**Bullet 1:** Built an end-to-end RAG-based customer support AI system using FastAPI, ChromaDB vector database, and Groq LLM (Llama 3.3 70B); ingests support documents, generates embeddings with all-MiniLM-L6-v2, and retrieves semantically relevant chunks for context-aware, multi-turn Q&A with session-based conversation memory.

**Bullet 2:** Designed a multi-stage NLP pipeline that extracts structured metadata from user queries — category, priority, intent, sentiment, and named entities (order IDs, amounts, dates) — via LLM-based extraction, combined with 6-category ticket classification and category-aware retrieval.

**Bullet 3:** Implemented production-grade API features: JWT authentication with bcrypt password hashing, sliding-window rate limiting, structured request logging, and global exception handling with clean error responses.

**Bullet 4:** Built a real-time streaming chat interface (Server-Sent Events) with a sidebar for chat history management, conversation export (TXT/PDF), and a 👍/👎 feedback loop persisted server-side.

**Bullet 5:** Built an admin panel for non-technical knowledge-base management — upload/delete support documents through a UI, automatically triggering vector index rebuilds — and deployed the full stack on Hugging Face Spaces via Docker.

---

## Roadmap / Not Yet Implemented

- LangChain-based refactor (PromptTemplate, Chains, RetrievalQA, LCEL) — currently a custom-built RAG pipeline
- AI agent / tool-calling, query rewriting, hybrid search (BM25 + vector), reranking
- Persistent database for users/conversations (currently JSON file + in-memory + browser localStorage)
- Analytics dashboard (query volume, category breakdown, latency, retrieval accuracy over time)
- Expanded evaluation set (15 → 50 queries)
- Architecture/sequence diagrams, demo video

---

*Built as part of a 22-day AI Engineer preparation sprint.*
