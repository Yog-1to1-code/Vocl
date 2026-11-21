"""Supabase JWKS, Google ID token, and local HS256 JWT verification for REST and WebSocket."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException, WebSocket
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.config import settings
from app.db.models import UserRecord
from app.db.repository import get_user_by_id, upsert_user

_jwks_client: jwt.PyJWKClient | None = None
_jwks_url: str = ""


def _get_supabase_jwks_client() -> jwt.PyJWKClient | None:
    global _jwks_client, _jwks_url
    if not settings.SUPABASE_URL:
        return None
    target = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    if _jwks_client is None or _jwks_url != target:
        _jwks_client = jwt.PyJWKClient(target)
        _jwks_url = target
    return _jwks_client


def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.JWT_EXPIRE_HOURS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_local_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def verify_supabase_jwt(token: str) -> dict | None:
    """Verify an asymmetric ES256/RS256 Supabase Auth JWT via JWKS."""
    client = _get_supabase_jwks_client()
    if client is None:
        return None
    try:
        signing_key = client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
        )
    except Exception:
        return None


def verify_google_id_token(raw_token: str) -> dict:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured on this server")
    try:
        return google_id_token.verify_oauth2_token(
            raw_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid Google ID token") from exc


def extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.strip().split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip():
        return parts[1].strip()
    return None


async def resolve_user_from_token(token: str) -> UserRecord | None:
    """Resolve an authenticated UserRecord from either a local HS256 JWT or a Supabase JWKS JWT."""
    local_claims = decode_local_jwt(token)
    if local_claims and local_claims.get("sub"):
        return await get_user_by_id(str(local_claims["sub"]))

    sb_claims = verify_supabase_jwt(token)
    if sb_claims and sb_claims.get("sub"):
        sub = str(sb_claims["sub"])
        email = str(sb_claims.get("email") or f"{sub[:8]}@supabase.user")
        display_name = email.split("@")[0] or "Vocl User"
        return await upsert_user(google_sub=f"supabase:{sub}", email=email, name=display_name)

    return None


async def get_current_user(authorization: str | None = Header(default=None)) -> UserRecord:
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    user = await resolve_user_from_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


async def authenticate_websocket_user(websocket: WebSocket) -> UserRecord | None:
    """Authenticate a WebSocket client via Authorization header or ?token=<jwt> query param."""
    token = extract_bearer_token(websocket.headers.get("authorization")) or websocket.query_params.get("token")
    if not token:
        return None
    return await resolve_user_from_token(token)
