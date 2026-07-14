# routes.py
from datetime import datetime
from collections import defaultdict
import json
import os
import sys

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "../rag"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../auth"))

from retriever import retrieve
from prompt_builder import build_prompt
from support_extractor import extract_support_info
from helpers import log_query
from security import decode_access_token

load_dotenv()

router = APIRouter()

conversation_memory = defaultdict(list)
feedback_store = []

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.replace("Bearer ", "")
    username = decode_access_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username


class QueryRequest(BaseModel):
    question: str
    session_id: str = "default"


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


class FeedbackRequest(BaseModel):
    session_id: str
    question: str
    answer: str
    feedback: str


def prepare_request(question: str, session_id: str):
    extraction = extract_support_info(question)
    category = extraction.get("category", "general")
    priority = extraction.get("priority", "low")
    intent = extraction.get("user_intent", "general_inquiry")
    sentiment = extraction.get("sentiment", "neutral")
    entities = extraction.get("entities", {})

    chunks = retrieve(question, category=category)
    sources = list({c["filename"] for c in chunks})

    history = conversation_memory[session_id]
    history_text = ""
    for turn in history[-3:]:
        history_text += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    base_prompt = build_prompt(question, chunks)
    prompt = (
        f"Previous conversation:\n{history_text}\nCurrent question:\n{base_prompt}"
        if history_text else base_prompt
    )

    confidence = "high" if len(chunks) >= 2 else "medium"

    return {
        "category": category,
        "priority": priority,
        "intent": intent,
        "sentiment": sentiment,
        "entities": entities,
        "sources": sources,
        "prompt": prompt,
        "confidence": confidence,
    }


@router.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest, username: str = Depends(verify_token)):
    data = prepare_request(request.question, request.session_id)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": data["prompt"]}],
        max_tokens=512,
    )

    answer = response.choices[0].message.content

    conversation_memory[request.session_id].append(
        {"question": request.question, "answer": answer}
    )

    log_query(
        query=request.question,
        category=data["category"],
        priority=data["priority"],
        intent=data["intent"],
        sentiment=data["sentiment"],
        sources=data["sources"],
        answer=answer,
    )

    return QueryResponse(
        query=request.question,
        category=data["category"],
        priority=data["priority"],
        intent=data["intent"],
        sentiment=data["sentiment"],
        entities=data["entities"],
        retrieved_sources=data["sources"],
        answer=answer,
        confidence_note=data["confidence"],
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post("/ask/stream")
async def ask_stream(request: QueryRequest, username: str = Depends(verify_token)):
    data = prepare_request(request.question, request.session_id)

    def generate():
        yield f"data: {json.dumps({'type':'metadata','category':data['category'],'priority':data['priority'],'intent':data['intent'],'sentiment':data['sentiment'],'entities':data['entities'],'retrieved_sources':data['sources'],'confidence_note':data['confidence'],'timestamp':datetime.utcnow().isoformat()})}\n\n"

        full_answer = ""

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":data["prompt"]}],
            max_tokens=512,
            stream=True,
        )

        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                full_answer += token
                yield f"data: {json.dumps({'type':'token','content':token})}\n\n"

        conversation_memory[request.session_id].append(
            {"question": request.question, "answer": full_answer}
        )

        log_query(
            query=request.question,
            category=data["category"],
            priority=data["priority"],
            intent=data["intent"],
            sentiment=data["sentiment"],
            sources=data["sources"],
            answer=full_answer,
        )

        yield f"data: {json.dumps({'type':'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    feedback_store.append({
        "session_id": request.session_id,
        "question": request.question,
        "answer": request.answer,
        "feedback": request.feedback,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return {"status": "success", "message": "Feedback recorded"}


@router.get("/feedback/stats")
async def feedback_stats():
    total = len(feedback_store)
    up = sum(1 for f in feedback_store if f["feedback"] == "up")
    down = sum(1 for f in feedback_store if f["feedback"] == "down")
    return {"total": total, "up": up, "down": down}