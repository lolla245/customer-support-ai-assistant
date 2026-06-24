# helpers.py
import json
import os
from datetime import datetime

LOG_FILE = "logs/query_logs.jsonl"

def log_query(query: str, category: str, priority: str, 
              intent: str, sentiment: str, sources: list, answer: str):
    os.makedirs("logs", exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "category": category,
        "priority": priority,
        "intent": intent,
        "sentiment": sentiment,
        "retrieved_sources": sources,
        "answer_length": len(answer),
        "quality_note": "good" if len(answer) > 100 else "short"
    }
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f" Logged: {category} | {priority} | {intent}")