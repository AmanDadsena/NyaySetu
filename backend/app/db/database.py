import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()

RAW_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nyaysetu.db")


#: libpq sslmode values that mean "the connection must be encrypted".
_SSL_REQUIRED = {"require", "verify-ca", "verify-full"}


def _normalise(url: str) -> tuple[str, bool]:
    """
    Coerce a hosted Postgres URL into the async driver form SQLAlchemy needs.

    Returns the rewritten URL and whether TLS was asked for.

    Neon, Supabase, Render and Railway all hand out `postgres://` or
    `postgresql://` URLs. SQLAlchemy's async engine needs an explicit async
    driver, and pasting the URL as given produces a driver error that reads
    like a config problem. Rewrite it instead of making that someone's
    deployment-day surprise.

    The TLS half of this is easy to get half-right, and being half-right is
    worse than doing nothing. asyncpg rejects libpq's `sslmode` query parameter,
    so it has to come out of the URL — but simply dropping it leaves the
    connection unencrypted, and Neon closes those with "connection is insecure
    (try using `sslmode=require`)", which reads like the parameter was missing
    rather than removed. So the intent is captured here and handed to asyncpg
    through connect_args instead.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    wants_tls = False
    if "+asyncpg" in url and "sslmode=" in url:
        from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

        parts = urlsplit(url)
        kept = []
        for key, value in parse_qsl(parts.query):
            if key == "sslmode":
                wants_tls = value.lower() in _SSL_REQUIRED
            elif key == "channel_binding":
                # Neon appends this; asyncpg does not accept it either and
                # negotiates channel binding itself where the server offers it.
                continue
            else:
                kept.append((key, value))
        url = urlunsplit(parts._replace(query=urlencode(kept)))

    return url, wants_tls


DATABASE_URL, _WANTS_TLS = _normalise(RAW_DATABASE_URL)
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

# Serverless Postgres (Neon, Supabase) puts a connection pooler in front and
# charges for idle connections, so keeping a local pool of long-lived sockets
# is counterproductive. NullPool opens per request and closes after; the
# provider's pooler does the real pooling. SQLite gets the default pool.
_engine_kwargs: dict = {"echo": False}
if IS_POSTGRES:
    _connect_args: dict = {
        # Statement caching breaks through a transaction-mode pooler such as
        # PgBouncer or Supabase's port 6543, which is the default many people
        # paste in. Disabling it costs a little speed and avoids a class of
        # "prepared statement already exists" errors that are painful to debug.
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    }
    if _WANTS_TLS:
        # Carries over the sslmode the URL asked for, which had to be stripped
        # above. Every managed Postgres worth using requires this.
        _connect_args["ssl"] = True
    _engine_kwargs.update(poolclass=NullPool, connect_args=_connect_args)

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
