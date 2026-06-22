# retriever.py
# Searches ChromaDB for the most relevant chunks to a user query

import chromadb

def get_collection(collection_name: str = "support_docs", db_path: str = "./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(collection_name)
    return collection

def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """
    Takes a user query, searches ChromaDB,
    returns top_k most relevant chunks.
    """
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "content": results["documents"][0][i],
            "filename": results["metadatas"][0][i]["filename"],
            "distance": results["distances"][0][i]
        })

    return chunks


# Quick test
if __name__ == "__main__":
    query = "How do I reset my password?"
    print(f" Query: {query}\n")

    results = retrieve(query)
    for i, chunk in enumerate(results):
        print(f"--- Result {i+1} ---")
        print(f"File: {chunk['filename']}")
        print(f"Distance: {chunk['distance']:.4f}")
        print(f"Content:\n{chunk['content'][:300]}")
        print()