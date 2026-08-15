"""
Prove a DATABASE_URL works before trusting it with real accounts.

Pasting a connection string into a hosting dashboard and hoping is how the
original data-loss bug survived as long as it did: the app fell back to SQLite
on an ephemeral disk, started cleanly, served traffic, and quietly lost every
account on each restart. Nothing looked wrong until someone tried to log in the
next day.

This connects, creates the schema, writes a row, reads it back and deletes it,
so a green result means the thing that actually matters — persistence — has been
observed rather than assumed.

    # PowerShell
    $env:DATABASE_URL = "postgresql://...";  python -m scripts.check_database
    # bash
    DATABASE_URL="postgresql://..." python -m scripts.check_database

The credential is never printed. Host and database name are shown so you can
confirm you pointed at the right place; everything before the @ is masked.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _safe_target(url: str) -> str:
    """Host and database only. Never the user or the password."""
    try:
        parts = urlsplit(url)
        host = parts.hostname or "?"
        port = f":{parts.port}" if parts.port else ""
        return f"{host}{port}{parts.path}"
    except ValueError:
        return "(unparseable URL)"


async def main() -> int:
    raw = os.environ.get("DATABASE_URL", "").strip()
    if not raw:
        print("DATABASE_URL is not set.\n")
        print("Without it the app uses SQLite on local disk. That is fine for")
        print("development and silently loses every account on a hosted restart.")
        return 1

    # Imported here rather than at module scope because importing the database
    # module builds the engine, which imports the driver. A missing driver then
    # raises before any of this file's error handling exists, and the user gets
    # a SQLAlchemy traceback instead of the one sentence that would help.
    try:
        from sqlalchemy import delete, select

        from app.db.database import DATABASE_URL, IS_POSTGRES, Base, engine
        from app.db.models import User
    except ModuleNotFoundError as exc:
        if exc.name == "asyncpg":
            print("  The Postgres driver is not installed in this environment.\n")
            print("    pip install asyncpg\n")
            print("  It is already in requirements.txt, so a deployed host has it;")
            print("  only a local venv that predates it needs this.")
            return 1
        raise

    print(f"  target   {_safe_target(raw)}")
    print(f"  driver   {DATABASE_URL.split('://', 1)[0]}")

    if not IS_POSTGRES:
        print("\n  This is not a Postgres URL, so it will not survive a restart")
        print("  on Hugging Face Spaces, Render or any other ephemeral host.")
        return 1

    probe = "__persistence_probe__@example.invalid"

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("  schema   created or already present")

        async with engine.begin() as conn:
            # Clean up after an interrupted earlier run before inserting.
            await conn.execute(delete(User).where(User.email == probe))
            await conn.execute(
                User.__table__.insert().values(
                    name="persistence probe",
                    email=probe,
                    hashed_password="not-a-real-hash",
                    role="client",
                )
            )

        async with engine.connect() as conn:
            found = (
                await conn.execute(select(User).where(User.email == probe))
            ).first()

        async with engine.begin() as conn:
            await conn.execute(delete(User).where(User.email == probe))

        if not found:
            print("\n  Wrote a row and could not read it back. Do not use this URL.")
            return 1

        print("  write    ok")
        print("  read     ok")
        print("  cleanup  ok")
        print("\n  This database persists. Set it as DATABASE_URL on your host.")
        return 0

    except Exception as exc:
        message = str(exc)
        print(f"\n  Connection failed: {type(exc).__name__}")
        print(f"  {message[:300]}")
        print("\n  Common causes:")
        if "password authentication" in message.lower():
            print("   - Wrong password. Copy the string again from the dashboard;")
            print("     Neon shows it once and regenerating is easier than guessing.")
        elif "does not exist" in message.lower():
            print("   - Database name in the URL does not match one that exists.")
        elif "timeout" in message.lower() or "unreachable" in message.lower():
            print("   - Host unreachable. Check the hostname, and that any IP")
            print("     allow-list on the provider includes where this is running.")
        else:
            print("   - Copy the URL again, whole, including the ?sslmode= part.")
            print("     sslmode is stripped automatically; asyncpg rejects it.")
        return 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
