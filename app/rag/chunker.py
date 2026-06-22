# chunker.py
# Splits loaded documents into smaller overlapping chunks

def chunk_documents(documents: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Takes a list of docs and splits each into chunks.
    Returns a list of dicts with 'chunk_id', 'filename', 'content'.
    """
    chunks = []
    chunk_id = 0

    for doc in documents:
        content = doc["content"]
        filename = doc["filename"]
        start = 0

        while start < len(content):
            end = start + chunk_size
            chunk_text = content[start:end]

            chunks.append({
                "chunk_id": f"{filename}_chunk_{chunk_id}",
                "filename": filename,
                "content": chunk_text
            })

            chunk_id += 1
            start += chunk_size - overlap  # overlap for context continuity

    print(f"Total chunks created: {len(chunks)}")
    return chunks


# Quick test
if __name__ == "__main__":
    import os
    from loader import load_documents

    docs_path = os.path.join(os.path.dirname(__file__), "../../data/sample_support_docs")
    docs = load_documents(docs_path)
    chunks = chunk_documents(docs)

    print(f"\nSample chunk:")
    print(f"ID: {chunks[0]['chunk_id']}")
    print(f"Content:\n{chunks[0]['content']}")