# loader.py
# Loads all .txt support documents from the data/sample_support_docs/ folder

import os

def load_documents(docs_path: str) -> list[dict]:
    """
    Reads all .txt files from the given folder.
    Returns a list of dicts with 'filename' and 'content'.
    """
    documents = []

    for filename in os.listdir(docs_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append({
                "filename": filename,
                "content": content
            })
            print(f" Loaded: {filename}")

    return documents


# Quick test — run this file directly to verify
if __name__ == "__main__":
    docs_path = os.path.join(os.path.dirname(__file__), "../../data/sample_support_docs")
    docs = load_documents(docs_path)
    print(f"\n Total docs loaded: {len(docs)}")
    print(f"First doc preview:\n{docs[0]['content'][:200]}")