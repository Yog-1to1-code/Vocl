"""Google ID token verification, JWT issuance, and FastAPI/WebSocket auth dependencies."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException, WebSocket
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.config import settings
from app.db.models import UserRecord
from app.db.repository import get_user_by_id


def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.JWT_EXPIRE_HOURS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


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


async def get_current_user(authorization: str | None = Header(default=None)) -> UserRecord:
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    claims = decode_access_token(token)
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = await get_user_by_id(str(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def authenticate_websocket_user(websocket: WebSocket) -> UserRecord | None:
    """Authenticate a WebSocket client via Authorization header or ?token=<jwt> query param."""
    token = extract_bearer_token(websocket.headers.get("authorization")) or websocket.query_params.get("token")
    if not token:
        return None
    try:
        claims = decode_access_token(token)
        user_id = claims.get("sub")
        if not user_id:
            return None
        return await get_user_by_id(str(user_id))
    except HTTPException:
        return None
