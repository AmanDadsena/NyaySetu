"""
Nyaysetu — FastAPI Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~
Entry point for the API server. Configures CORS middleware for the
Next.js frontend and exposes a health-check endpoint plus a sample
API router.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv() # Load variables from .env into os.environ

from app.routers import analyze, health, auth, lawyers, cases, chat, bot
from app.db.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables (Drop and recreate for schema changes)
    async with engine.begin() as conn:
        print("Recreating database tables for new schema...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Database schema updated successfully.")
    yield

app = FastAPI(
    title="Nyaysetu API",
    version="0.1.0",
    description="Backend API for the Nyaysetu platform",
    lifespan=lifespan
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js dev server (port 3000) and production origin
# ---------------------------------------------------------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(auth.router)
app.include_router(lawyers.router)
app.include_router(cases.router)
app.include_router(chat.router)
app.include_router(bot.router)


@app.get("/")
async def root():
    """Root redirect / welcome message."""
    return {
        "message": "Welcome to the Nyaysetu API",
        "docs": "/docs",
        "health": "/api/health",
    }
