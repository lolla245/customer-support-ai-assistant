# embedder.py
import chromadb
import os

CATEGORY_MAP = {
    "password_reset.txt": "Login / Account",
    "login_troubleshooting.txt": "Login / Account",
    "refund_policy.txt": "Refund / Cancellation",
    "order_tracking_faq.txt": "Order / Payment",
    "account_deletion_policy.txt": "Login / Account"
}

def get_chroma_client(db_path: str = "./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)
    return client

def embed_and_store(chunks: list[dict], collection_name: str = "support_docs"):
    client = get_chroma_client()

    existing = [c.name for c in client.list_collections()]
    if collection_name in existing:
        client.delete_collection(collection_name)
        print(f"🗑️ Deleted existing collection: {collection_name}")

    collection = client.create_collection(collection_name)

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "filename": chunk["filename"],
            "category": CATEGORY_MAP.get(chunk["filename"], "General Support"),
            "doc_type": chunk["filename"].replace(".txt", "")
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Embedded and stored {len(chunks)} chunks with metadata")
    return collection


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(__file__))
    from loader import load_documents
    from chunker import chunk_documents

    docs_path = os.path.join(os.path.dirname(__file__), "../../data/sample_support_docs")
    docs = load_documents(docs_path)
    chunks = chunk_documents(docs)
    collection = embed_and_store(chunks)
    print(f"Collection count: {collection.count()}")