# routes.py
from fastapi import APIRouter
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../rag"))

from retriever import retrieve
from prompt_builder import build_prompt
from ticket_classifier import classify_ticket
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    category: str
    answer: str
    sources: list[str]

@router.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    # Step 1: Classify ticket
    classification = classify_ticket(request.question)
    category = classification["category"]

    # Step 2: Retrieve relevant chunks
    chunks = retrieve(request.question, category=category)

    # Step 3: Build prompt
    prompt = build_prompt(request.question, chunks)

    # Step 4: Call Groq LLM
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512
    )
    answer = response.choices[0].message.content

    # Step 5: Return response
    sources = list(set([chunk["filename"] for chunk in chunks]))
    return QueryResponse(
        question=request.question,
        category=category,
        answer=answer,
        sources=sources
    )