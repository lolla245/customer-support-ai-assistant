from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from collections import defaultdict
from app.auth.auth_routes import auth_router
import os
import time
import logging
import traceback

load_dotenv()
from app.api.routes import router
from app.api.admin_routes import admin_router

# ---- Logging setup ----
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("support-assistant")

app = FastAPI(title="Customer Support AI Assistant")

# ---- Rate limiting setup ----
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 10
request_log = defaultdict(list)  # ip -> list of timestamps

# ---- Request logging middleware ----
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        duration = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{request.method} {request.url.path} FAILED after {duration}ms | {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": "Something went wrong. Please try again."}
        )
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} {response.status_code} | {duration}ms")
    return response

# ---- Rate limiting middleware ----
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/ask", "/ask/stream"]:
        client_ip = request.client.host
        now = time.time()

        request_log[client_ip] = [t for t in request_log[client_ip] if now - t < RATE_LIMIT_WINDOW]

        if len(request_log[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests", "detail": "Please wait a moment before sending more messages."}
            )

        request_log[client_ip].append(now)

    return await call_next(request)

# ---- Global exception handler (catches unhandled exceptions cleanly) ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Something went wrong. Please try again."}
    )

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)
app.include_router(admin_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return FileResponse("app/static/index.html")