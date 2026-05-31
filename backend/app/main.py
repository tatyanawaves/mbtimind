"""MBTI Platform - FastAPI Application Entry Point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import test_sessions, questions, results

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="B2B/B2G MBTI psychometric testing platform for HR, universities, and schools",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Debugging: Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(test_sessions.router, prefix="/api/v1/sessions", tags=["Test Sessions"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["Questions"])
app.include_router(results.router, prefix="/api/v1/results", tags=["Results"])


@app.on_event("startup")
async def on_startup():
    """Initialize database tables and seed questions on startup."""
    from app.core.init_db import init_db
    try:
        await init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
