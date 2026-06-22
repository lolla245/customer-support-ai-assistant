# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from app.api.routes import router

app = FastAPI(title="Customer Support AI Assistant")

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routes
app.include_router(router)

@app.get("/")
def root():
    return FileResponse("app/static/index.html")