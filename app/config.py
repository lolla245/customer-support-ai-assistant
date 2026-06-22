# config.py
# Centralized configuration — API keys, model names, paths
# TODO: Load from .env using python-dotenv

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
DOCS_PATH = os.getenv("DOCS_PATH", "./data/sample_support_docs")
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-3.5-turbo"
