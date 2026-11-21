"""Authentication routes: Google OAuth ID token login, local dev bypass, and current profile."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db.models import UserRecord
from app.db.repository import check_and_reset_daily_quota, upsert_user
from app.services.auth import create_access_token, get_current_user, verify_google_id_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class GoogleLoginRequest(BaseModel):
    id_token: str


class DevLoginRequest(BaseModel):
    email: str = "yogesh@vocl.local"
    name: str = "Yogesh Mali"


def _serialize_user(user: UserRecord, remaining_minutes: float) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "daily_minutes_used": round(user.daily_minutes_used, 2),
        "daily_quota_minutes": settings.DAILY_QUOTA_MINUTES,
        "remaining_minutes": remaining_minutes,
        "quota_reset_date": user.quota_reset_date.isoformat(),
    }


@router.post("/google")
async def login_with_google(body: GoogleLoginRequest) -> dict:
    info = verify_google_id_token(body.id_token)
    google_sub = str(info.get("sub") or "")
    email = str(info.get("email") or "")
    name = str(info.get("name") or email.split("@")[0] or "Vocl User")
    avatar_url = str(info.get("picture") or "")
    if not google_sub or not email:
        raise HTTPException(status_code=401, detail="Google token missing subject or email")

    user = await upsert_user(google_sub=google_sub, email=email, name=name, avatar_url=avatar_url)
    user, remaining = await check_and_reset_daily_quota(user.id)
    assert user is not None
    return {
        "access_token": create_access_token(user.id, user.email),
        "user": _serialize_user(user, remaining),
    }


@router.post("/dev-login")
async def login_dev(body: DevLoginRequest | None = None) -> dict:
    if not settings.DEV_AUTH_BYPASS:
        raise HTTPException(status_code=403, detail="Local dev login is disabled")
    req = body or DevLoginRequest()
    user = await upsert_user(
        google_sub=f"dev:{req.email.strip().lower()}",
        email=req.email.strip(),
        name=req.name.strip() or "Vocl Dev",
    )
    user, remaining = await check_and_reset_daily_quota(user.id)
    assert user is not None
    return {
        "access_token": create_access_token(user.id, user.email),
        "user": _serialize_user(user, remaining),
    }


@router.get("/me")
async def get_me(current_user: UserRecord = Depends(get_current_user)) -> dict:
    user, remaining = await check_and_reset_daily_quota(current_user.id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return _serialize_user(user, remaining)
