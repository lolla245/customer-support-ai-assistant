---
title: Customer Support AI
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# Customer Support AI Assistant (RAG + FastAPI)
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

# Day 2 Plan Notes — June 23, 2026

## Current Stack
- **Framework:** FastAPI + Uvicorn
- **Vector DB:** ChromaDB (persistent)
- **Embedding Model:** all-MiniLM-L6-v2 (local)
- **LLM:** Groq — llama-3.3-70b-versatile
- **Support Docs:** 5 .txt files (15 chunks)
- **UI:** Dark-themed chat (HTML/CSS/JS)
- **Deployment:** Hugging Face Spaces (Docker)

## Current Features
- Document loading + chunking (500 char chunks)
- Semantic search via ChromaDB
- RAG-based Q&A with Groq LLM
- Ticket classification (6 categories)
- Category shown in UI + API response
- Source docs shown in UI

## Current Limitations
- No metadata-aware retrieval
- No evaluation set
- README needs improvement
- Classification not influencing retrieval yet

## What to Build Today
1. ✅ Ticket classifier — DONE
2. Metadata-aware retrieval
3. Evaluation question set (15 questions)
4. README update
5. Aptitude + DSA
6. SQL/NLP revision notes
## 📊 Evaluation Results

| # | Question | Expected Category | Predicted Category | Retrieved Source | Answer Quality |
|---|---|---|---|---|---|
| 1 | How do I reset my password? | Login / Account | Login / Account | password_reset.txt | ✅ Good |
| 2 | What is your refund policy? | Refund / Cancellation | Refund / Cancellation | refund_policy.txt | ✅ Good |
| 3 | How do I track my order? | Order / Payment | Order / Payment | order_tracking_faq.txt | ✅ Good |
| 4 | How do I delete my account? | Login / Account | Login / Account | account_deletion_policy.txt | ✅ Good |
| 5 | I can't log in to my account | Login / Account | Login / Account | login_troubleshooting.txt | ✅ Good |
| 6 | How long does a refund take? | Refund / Cancellation | Refund / Cancellation | refund_policy.txt | ✅ Good |
| 7 | My order says delivered but I didn't receive it | Order / Payment | Order / Payment | order_tracking_faq.txt | ✅ Good |
| 8 | What are the password requirements? | Login / Account | Login / Account | password_reset.txt | 🟡 Okay |
| 9 | How to enable two factor authentication? | Technical Issue | Login / Account | login_troubleshooting.txt | 🟡 Okay |
| 10 | Can I change my delivery address? | Order / Payment | Order / Payment | order_tracking_faq.txt | ✅ Good |
| 11 | My payment failed but amount was
# Support Query Schema

## Structured Fields for Query Analysis

### 1. category
Classifies the type of support issue.
- `billing`
- `login`
- `technical`
- `refund`
- `order`
- `general`

### 2. priority
Urgency level of the query.
- `low` — general questions
- `medium` — account issues
- `high` — payment failures, urgent issues

### 3. user_intent
What the user wants to do.
- `reset_password`
- `ask_refund`
- `track_order`
- `cancel_subscription`
- `delete_account`
- `payment_failed`
- `bug_report`
- `general_inquiry`

### 4. product_area
Which part of the product is affected.
- `account`
- `payment`
- `subscription`
- `app`
- `delivery`

### 5. sentiment
User's emotional tone.
- `neutral`
- `frustrated`
- `urgent`
- `angry`

### 6. entities
Key info extracted from query.
- `order_id`
- `email`
- `date`
- `plan_name`
- `amount`