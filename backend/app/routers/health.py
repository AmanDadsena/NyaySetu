"""
Health-check router.

Reports whether the database is actually reachable, not just whether the
process is up. Those came apart in practice: after DATABASE_URL was pointed at
Postgres the service answered /api/health with 200 while every registration
returned 500, and with no access to the host's logs there was nothing to look
at. A liveness check that cannot distinguish "running" from "running and able
to store anything" is not much of a check.

Nothing here exposes the connection string. The host and database name are
shown because they are what you need to confirm you pointed at the right place;
everything before the @ is never read.
"""

from urllib.parse import urlsplit

from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import DATABASE_URL, IS_POSTGRES, engine

router = APIRouter(prefix="/api", tags=["health"])


def _safe_target() -> str:
    """Host and database only — never the user or the password."""
    try:
        parts = urlsplit(DATABASE_URL)
        if not parts.hostname:
            return parts.path.lstrip("/") or "local file"
        port = f":{parts.port}" if parts.port else ""
        return f"{parts.hostname}{port}{parts.path}"
    except ValueError:
        return "unparseable"


@router.get("/health")
async def health_check():
    """Service health, including whether the database answers."""
    database: dict[str, object] = {
        "backend": "postgres" if IS_POSTGRES else "sqlite",
        "target": _safe_target(),
        "persists_across_restart": IS_POSTGRES,
    }

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        database["reachable"] = True
    except Exception as exc:
        # The message can name a host or a role, never a password, and it is
        # the single most useful thing to see when a deploy half-works.
        database["reachable"] = False
        database["error"] = type(exc).__name__
        database["detail"] = str(exc)[:200]

    healthy = bool(database["reachable"])
    return {
        "status": "healthy" if healthy else "degraded",
        "service": "nyaysetu-api",
        "database": database,
    }
