# admin_routes.py
import os
import sys
from fastapi import APIRouter, UploadFile, File, Header, HTTPException

sys.path.append(os.path.join(os.path.dirname(__file__), "../rag"))
from loader import load_documents
from chunker import chunk_documents
from embedder import embed_and_store

admin_router = APIRouter(prefix="/admin")

DOCS_PATH = os.path.join(os.path.dirname(__file__), "../../Data/sample_support_docs")
ADMIN_KEY = os.getenv("ADMIN_KEY", "changeme")


def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")


def rebuild_index():
    """Re-run the ingest pipeline so ChromaDB reflects the current files on disk."""
    docs = load_documents(DOCS_PATH)
    chunks = chunk_documents(docs)
    collection = embed_and_store(chunks)
    return collection.count()


@admin_router.get("/documents")
async def list_documents(x_admin_key: str = Header(...)):
    verify_admin(x_admin_key)
    files = [f for f in os.listdir(DOCS_PATH) if f.endswith(".txt")]
    return {"documents": files, "count": len(files)}


@admin_router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    x_admin_key: str = Header(...)
):
    verify_admin(x_admin_key)

    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    dest_path = os.path.join(DOCS_PATH, file.filename)
    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    chunk_count = rebuild_index()
    return {
        "status": "success",
        "message": f"Uploaded {file.filename} and rebuilt index",
        "total_chunks": chunk_count
    }


@admin_router.delete("/documents/{filename}")
async def delete_document(filename: str, x_admin_key: str = Header(...)):
    verify_admin(x_admin_key)

    file_path = os.path.join(DOCS_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)
    chunk_count = rebuild_index()
    return {
        "status": "success",
        "message": f"Deleted {filename} and rebuilt index",
        "total_chunks": chunk_count
    }