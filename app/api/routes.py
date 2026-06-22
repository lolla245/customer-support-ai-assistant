# routes.py
from fastapi import APIRouter
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../rag"))

from retriever import retrieve
from prompt_builder import build_prompt
from groq import Groq

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]

@router.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    # Step 1: Retrieve relevant chunks
    chunks = retrieve(request.question)

    # Step 2: Build prompt
    prompt = build_prompt(request.question, chunks)

    # Step 3: Call Groq LLM
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512
    )
    answer = response.choices[0].message.content

    # Step 4: Return response
    sources = list(set([chunk["filename"] for chunk in chunks]))
    return QueryResponse(
        question=request.question,
        answer=answer,
        sources=sources
    )