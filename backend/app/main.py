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
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env into os.environ

from app.routers import analyze, health, auth, lawyers, cases, chat, bot, tools, deadlines
from app.db.database import IS_POSTGRES, engine, Base


async def _widen_timestamps(conn) -> None:
    """
    Convert any naive timestamp column to `timestamptz`.

    `create_all` creates missing tables and never alters existing ones, so a
    database first created against the earlier models keeps
    TIMESTAMP WITHOUT TIME ZONE columns. asyncpg refuses to write a
    timezone-aware datetime into one, which is every write this app makes: the
    service answers health checks perfectly and returns 500 on registration.

    There is no migration tool here, and adding one to fix a single column type
    would be heavier than the problem. This asks the catalogue which columns are
    still naive and alters only those, so it is idempotent and does nothing on a
    database that was created correctly.
    """
    from sqlalchemy import text

    naive = await conn.execute(
        text(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND data_type = 'timestamp without time zone'"
        )
    )
    columns = naive.fetchall()
    for table, column in columns:
        await conn.execute(
            text(
                f'ALTER TABLE "{table}" ALTER COLUMN "{column}" '
                f'TYPE timestamptz USING "{column}" AT TIME ZONE \'UTC\''
            )
        )
    if columns:
        print(f"Migrated {len(columns)} timestamp columns to timestamptz.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create any missing tables on boot, and bring existing ones up to date.

    This deliberately does NOT drop existing tables. It used to, which meant
    every restart — including every idle-wake on a hosted platform — silently
    deleted all registered users, cases and messages. Set RESET_DB=1 to opt in
    to the destructive behaviour locally when the schema changes.
    """
    async with engine.begin() as conn:
        if os.environ.get("RESET_DB") == "1":
            print("RESET_DB=1 — dropping all tables before recreating them.")
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        if IS_POSTGRES:
            await _widen_timestamps(conn)
        print("Database schema ready.")
    yield

app = FastAPI(
    title="Nyaysetu API",
    version="0.1.0",
    description="Backend API for the Nyaysetu platform",
    lifespan=lifespan
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js dev server (port 3000) and production origins
#
# Note: browsers reject `Access-Control-Allow-Origin: *` together with
# `allow_credentials=True`, so a wildcard list silently breaks any credentialed
# request. Vercel also generates a fresh preview subdomain per deployment, so
# production origins are matched by regex rather than enumerated by hand.
# ---------------------------------------------------------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add custom origins from environment if provided
custom_origins = os.environ.get("CORS_ORIGINS", "")
if custom_origins:
    origins.extend([origin.strip() for origin in custom_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
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
app.include_router(tools.router)
app.include_router(deadlines.router)


@app.get("/")
async def root():
    """Root redirect / welcome message."""
    return {
        "message": "Welcome to the Nyaysetu API",
        "docs": "/docs",
        "health": "/api/health",
    }
