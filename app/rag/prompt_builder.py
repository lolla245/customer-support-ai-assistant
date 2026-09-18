# prompt_builder.py
# Builds the final prompt to send to the LLM


def build_prompt(query: str, retrieved_chunks: list[dict]) -> str:
    """
    Combines user query + retrieved chunks into a structured prompt.
    """
    context = ""

    for i, chunk in enumerate(retrieved_chunks):
        context += f"\n--- Document {i+1} ({chunk['filename']}) ---\n"
        context += chunk["content"]
        context += "\n"

    prompt = f"""You are a helpful customer support assistant for an e-commerce platform.

If the user's message is a greeting or small talk (e.g. "hi", "hello", "how are you"), respond warmly and briefly introduce what you can help with — password resets, refunds, order tracking, account issues, and general support questions. Do NOT use the context below for greetings.

For actual support questions, use ONLY the context below to answer. If the answer is not in the context, say "I don't have information about that."

Context:
{context}

User Question: {query}

Answer:"""

    return prompt


# Quick test
if __name__ == "__main__":
    import os
    import sys

    sys.path.append(os.path.dirname(__file__))
    from retriever import retrieve

    query = "How do I reset my password?"
    chunks = retrieve(query)
    prompt = build_prompt(query, chunks)

    print("Built Prompt:\n")
    print(prompt)