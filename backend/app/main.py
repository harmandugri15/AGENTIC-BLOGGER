import sys
import os
from pathlib import Path

# Ensure workspace root and backend root are always on sys.path
_current_dir = Path(__file__).resolve().parent
_backend_root = _current_dir.parent
_workspace_root = _backend_root.parent
for _p in [str(_workspace_root), str(_backend_root)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from contextlib import asynccontextmanager

try:
    from backend.app.config import settings
    from backend.app.models.base import engine, Base
    from backend.app.api.v1.campaigns import router as campaigns_router
    from backend.app.core.logger import get_logger, setup_global_logging
except ModuleNotFoundError:
    from app.config import settings
    from app.models.base import engine, Base
    from app.api.v1.campaigns import router as campaigns_router
    from app.core.logger import get_logger, setup_global_logging

setup_global_logging()
logger = get_logger("Main")
http_logger = get_logger("HTTP")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Multi-agent AI content generation platform for CitiusTech.com with real RAG, search gap analysis, and human-style quality gates.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    # Avoid spamming terminal with polling GET requests every 1.5s
    is_polling = method == "GET" and "/campaigns/" in path
    
    if not is_polling:
        http_logger.info(f"--> {method} {path}")
        
    response = await call_next(request)
    duration = time.time() - start_time
    
    if not is_polling or response.status_code >= 400:
        http_logger.info(f"<-- {method} {path} - {response.status_code} ({duration:.2f}s)")
        
    return response

app.include_router(campaigns_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "llm_provider": settings.LLM_PROVIDER
    }

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "health_url": "/health"
    }
