# ticket_classifier.py
# Classifies user support queries into categories using Groq LLM

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

CATEGORIES = [
    "Billing",
    "Login / Account",
    "Technical Issue",
    "Order / Payment",
    "Refund / Cancellation",
    "General Support"
]

def classify_ticket(query: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a customer support ticket classifier.
Classify the following user query into exactly one of these categories:
{', '.join(CATEGORIES)}

Rules:
- Reply with ONLY the category name, nothing else.
- Choose the most relevant category.

User query: "{query}"

Category:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )

    category = response.choices[0].message.content.strip()

    # Validate category
    for cat in CATEGORIES:
        if cat.lower() in category.lower():
            return {"category": cat, "confidence": "high"}

    return {"category": "General Support", "confidence": "low"}


# Quick test
if __name__ == "__main__":
    test_queries = [
        "How do I reset my password?",
        "I want a refund for my order",
        "My payment failed but amount was deducted",
        "App crashes after login",
        "How do I track my order?"
    ]

    for q in test_queries:
        result = classify_ticket(q)
        print(f"Q: {q}")
        print(f"   → {result['category']} ({result['confidence']})")
        print()