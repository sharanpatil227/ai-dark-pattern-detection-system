"""
FastAPI application entry point.
Configures CORS, lifespan events, and registers API routers.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import connect_to_mongodb, close_mongodb_connection
from app.routes import scan, reports, dashboard, health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("darkguard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager handling startup and shutdown."""
    logger.info("Starting Dark Pattern Detection API on %s:%d", settings.HOST, settings.PORT)
    await connect_to_mongodb()
    yield
    logger.info("Shutting down Dark Pattern Detection API...")
    await close_mongodb_connection()


app = FastAPI(
    title="AI-Powered Dark Pattern Detection API",
    description="Backend detection engine, NLP classification, and reporting API.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for Vite dashboard and Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*",  # Extension and local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router)
app.include_router(scan.router)
app.include_router(reports.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    return {
        "name": "AI-Powered Dark Pattern Detection System API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/api/health",
    }

