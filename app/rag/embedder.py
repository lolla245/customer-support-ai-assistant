# embedder.py
# Converts text chunks into vectors and stores them in ChromaDB

import chromadb
import os

def get_chroma_client(db_path: str = "./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)
    return client

def embed_and_store(chunks: list[dict], collection_name: str = "support_docs"):
    """
    Takes chunks, embeds them using ChromaDB's default embedding,
    and stores in a persistent ChromaDB collection.
    """
    client = get_chroma_client()

    # Delete existing collection if it exists (fresh start)
    existing = [c.name for c in client.list_collections()]
    if collection_name in existing:
        client.delete_collection(collection_name)
        print(f" Deleted existing collection: {collection_name}")

    collection = client.create_collection(collection_name)

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [{"filename": chunk["filename"]} for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Embedded and stored {len(chunks)} chunks in ChromaDB")
    return collection


# Quick test
if __name__ == "__main__":
    import os, sys
    sys.path.append(os.path.dirname(__file__))
    from loader import load_documents
    from chunker import chunk_documents

    docs_path = os.path.join(os.path.dirname(__file__), "../../data/sample_support_docs")
    docs = load_documents(docs_path)
    chunks = chunk_documents(docs)
    collection = embed_and_store(chunks)

    print(f"\n Collection count: {collection.count()}")