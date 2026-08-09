"""
Shared runtime configuration.

Exists mainly so the JWT signing key is resolved in exactly one place. It was
previously read separately in `auth.py` and `middleware.py`, each with the same
hardcoded development fallback — a value that lives in a public repository and
would let anyone mint a valid token for any user id.
"""

from __future__ import annotations

import os
import secrets

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development").lower()
IS_PRODUCTION = APP_ENV in {"production", "prod"}

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", str(60 * 24)))


def _resolve_jwt_secret() -> str:
    configured = os.getenv("JWT_SECRET_KEY", "").strip()

    if configured and configured not in {"change_me", "nyaysetu_secret_key_dev_only"}:
        return configured

    if IS_PRODUCTION:
        raise RuntimeError(
            "JWT_SECRET_KEY must be set to a real secret when APP_ENV=production. "
            "Generate one with: python -c \"import secrets; "
            "print(secrets.token_urlsafe(48))\""
        )

    # Development: mint a random key per process rather than using a shared
    # literal. Tokens stop working across restarts, which is a mild annoyance
    # locally and vastly better than shipping a known signing key.
    print(
        "[config] JWT_SECRET_KEY not set — using a random per-process key. "
        "Sessions will not survive a restart. Set it in .env to keep them."
    )
    return secrets.token_urlsafe(48)


JWT_SECRET_KEY = _resolve_jwt_secret()
