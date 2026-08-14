import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()

RAW_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nyaysetu.db")


def _normalise(url: str) -> str:
    """
    Coerce a hosted Postgres URL into the async driver form SQLAlchemy needs.

    Neon, Supabase, Render and Railway all hand out `postgres://` or
    `postgresql://` URLs. SQLAlchemy's async engine needs an explicit async
    driver, and pasting the URL as given produces a driver error that reads
    like a config problem. Rewrite it instead of making that someone's
    deployment-day surprise.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # asyncpg configures TLS itself and rejects libpq's `sslmode` query
    # parameter, which most providers append to the URL they show you.
    if "+asyncpg" in url and "sslmode=" in url:
        from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

        parts = urlsplit(url)
        kept = [(k, v) for k, v in parse_qsl(parts.query) if k != "sslmode"]
        url = urlunsplit(parts._replace(query=urlencode(kept)))

    return url


DATABASE_URL = _normalise(RAW_DATABASE_URL)
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# Serverless Postgres (Neon, Supabase) puts a connection pooler in front and
# charges for idle connections, so keeping a local pool of long-lived sockets
# is counterproductive. NullPool opens per request and closes after; the
# provider's pooler does the real pooling. SQLite gets the default pool.
_engine_kwargs: dict = {"echo": False}
if IS_POSTGRES:
    _engine_kwargs.update(
        poolclass=NullPool,
        # Statement caching breaks through a transaction-mode pooler such as
        # PgBouncer or Supabase's port 6543, which is the default many people
        # paste in. Disabling it costs a little speed and avoids a class of
        # "prepared statement already exists" errors that are painful to debug.
        connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
    )

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
