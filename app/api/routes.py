# routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))

from retriever import retrieve
from prompt_builder import build_prompt
from support_extractor import extract_support_info
from helpers import log_query
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    query: str
    category: str
    priority: str
    intent: str
    sentiment: str
    entities: dict
    retrieved_sources: list[str]
    answer: str
    confidence_note: str
    timestamp: str

@router.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    # Step 1: Extract structured info
    extraction = extract_support_info(request.question)
    category = extraction.get("category", "general")
    priority = extraction.get("priority", "low")
    intent = extraction.get("user_intent", "general_inquiry")
    sentiment = extraction.get("sentiment", "neutral")
    entities = extraction.get("entities", {})

    # Step 2: Retrieve
    chunks = retrieve(request.question, category=category)
    sources = list(set([chunk["filename"] for chunk in chunks]))

    # Step 3: Build prompt + LLM
    prompt = build_prompt(request.question, chunks)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512
    )
    answer = response.choices[0].message.content

    # Step 4: Confidence note
    confidence_note = "high" if len(chunks) >= 2 else "medium"

    # Step 5: Log
    log_query(
        query=request.question,
        category=category,
        priority=priority,
        intent=intent,
        sentiment=sentiment,
        sources=sources,
        answer=answer
    )

    return QueryResponse(
        query=request.question,
        category=category,
        priority=priority,
        intent=intent,
        sentiment=sentiment,
        entities=entities,
        retrieved_sources=sources,
        answer=answer,
        confidence_note=confidence_note,
        timestamp=datetime.utcnow().isoformat()
    )