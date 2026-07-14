FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "from app.rag.loader import load_documents; \
    from app.rag.chunker import chunk_documents; \
    from app.rag.embedder import embed_and_store; \
    import os; \
    docs = load_documents('data/sample_support_docs'); \
    chunks = chunk_documents(docs); \
    embed_and_store(chunks)"

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]