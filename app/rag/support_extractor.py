# support_extractor.py
# Extracts structured metadata from user support queries using Groq LLM

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def extract_support_info(query: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are a support issue extraction engine.
Extract structured information from the user query below.

Return ONLY valid JSON with these exact fields:
{{
  "category": "billing|login|technical|refund|order|general",
  "priority": "low|medium|high",
  "user_intent": "reset_password|ask_refund|track_order|cancel_subscription|delete_account|payment_failed|bug_report|general_inquiry",
  "product_area": "account|payment|subscription|app|delivery",
  "sentiment": "neutral|frustrated|urgent|angry",
  "entities": {{
    "order_id": null,
    "email": null,
    "date": null,
    "amount": null,
    "plan_name": null
  }}
}}

Rules:
- Return ONLY JSON, no explanation
- Choose the most relevant value for each field
- For entities, extract actual values if mentioned, else null

User query: "{query}"

JSON:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    raw = response.choices[0].message.content.strip()

    # Clean and parse JSON
    try:
        # Remove markdown backticks if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {
            "category": "general",
            "priority": "low",
            "user_intent": "general_inquiry",
            "product_area": "account",
            "sentiment": "neutral",
            "entities": {}
        }


# Test with 10 queries
if __name__ == "__main__":
    test_queries = [
        "My payment failed yesterday and amount got deducted. I want a refund.",
        "How do I reset my password?",
        "I can't log in to my account since 2 days!",
        "Where is my order? It's been 10 days.",
        "App keeps crashing after the latest update.",
        "I want to cancel my premium subscription.",
        "Can I get a refund for order #12345?",
        "How do I delete my account permanently?",
        "My refund of $50 hasn't been processed yet.",
        "I'm very frustrated, nothing is working!"
    ]

    for q in test_queries:
        print(f"\nQ: {q}")
        result = extract_support_info(q)
        print(json.dumps(result, indent=2))
        print("-" * 50)