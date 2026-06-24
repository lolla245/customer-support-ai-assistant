# retriever.py
import chromadb

CATEGORY_MAP = {
   "Billing": ["refund_policy.txt"],
    "billing": ["refund_policy.txt"],  # lowercase కూడా add చేయి
    "Refund / Cancellation": ["refund_policy.txt", "order_tracking_faq.txt"],
    "refund": ["refund_policy.txt"],
    "Order / Payment": ["order_tracking_faq.txt"],
    "order": ["order_tracking_faq.txt"],
    "Login / Account": ["password_reset.txt", "login_troubleshooting.txt", "account_deletion_policy.txt"],
    "login": ["password_reset.txt", "login_troubleshooting.txt"],
    "Technical Issue": ["login_troubleshooting.txt"],
    "technical": ["login_troubleshooting.txt"],
    "General Support": [],
    "general": []
}

def get_collection(collection_name: str = "support_docs", db_path: str = "./chroma_db"):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(collection_name)
    return collection

def retrieve(query: str, top_k: int = 3, category: str = None) -> list[dict]:
    collection = get_collection()

    # Build where filter if category provided
    where = None
    if category and category in CATEGORY_MAP and CATEGORY_MAP[category]:
        preferred_files = CATEGORY_MAP[category]
        if len(preferred_files) == 1:
            where = {"filename": {"$eq": preferred_files[0]}}
        else:
            where = {"filename": {"$in": preferred_files}}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )
    except Exception:
        # Fallback — no filter
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "content": results["documents"][0][i],
            "filename": results["metadatas"][0][i]["filename"],
            "category": results["metadatas"][0][i].get("category", ""),
            "distance": results["distances"][0][i]
        })

    return chunks


if __name__ == "__main__":
    print("🔍 Without category filter:")
    results = retrieve("I want a refund", top_k=2)
    for r in results:
        print(f"  → {r['filename']} | {r['category']} | {r['distance']:.3f}")

    print("\n🔍 With category filter (Refund / Cancellation):")
    results = retrieve("I want a refund", top_k=2, category="Refund / Cancellation")
    for r in results:
        print(f"  → {r['filename']} | {r['category']} | {r['distance']:.3f}")