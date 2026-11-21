"""Background Google Drive uploader for analytics-only session audio archives."""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from uuid import uuid4

import httpx
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials

from app.config import settings
from app.db.repository import update_session_audio_path

logger = logging.getLogger(__name__)

_DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
_TOKEN_URI = "https://oauth2.googleapis.com/token"
_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"


def _effective_client_id() -> str:
    return settings.GDRIVE_CLIENT_ID or settings.GOOGLE_CLIENT_ID


def is_gdrive_configured() -> bool:
    return bool(
        _effective_client_id()
        and settings.GDRIVE_CLIENT_SECRET
        and settings.GDRIVE_REFRESH_TOKEN
        and settings.GDRIVE_FOLDER_ID
    )


def _refresh_access_token() -> str:
    creds = Credentials(
        token=None,
        refresh_token=settings.GDRIVE_REFRESH_TOKEN,
        token_uri=_TOKEN_URI,
        client_id=_effective_client_id(),
        client_secret=settings.GDRIVE_CLIENT_SECRET,
        scopes=[_DRIVE_SCOPE],
    )
    creds.refresh(GoogleAuthRequest())
    if not creds.token:
        raise RuntimeError("Google OAuth refresh returned an empty access token")
    return creds.token


def _build_multipart_body(metadata: dict, audio_bytes: bytes, content_type: str, boundary: str) -> bytes:
    meta_bytes = json.dumps(metadata).encode("utf-8")
    parts = [
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode("utf-8"),
        meta_bytes,
        f"\r\n--{boundary}\r\nContent-Type: {content_type}\r\n\r\n".encode("utf-8"),
        audio_bytes,
        f"\r\n--{boundary}--\r\n".encode("utf-8"),
    ]
    return b"".join(parts)


async def upload_session_audio(file_path: Path, session_id: str, problem_id: str) -> str | None:
    """Upload compressed session audio to Google Drive and return 'gdrive:<file_id>'."""
    if not is_gdrive_configured():
        logger.info("Google Drive upload skipped (GDRIVE_* env vars not configured)")
        return None
    if not file_path.is_file():
        logger.warning("Google Drive upload skipped; file missing: %s", file_path)
        return None

    access_token = await asyncio.to_thread(_refresh_access_token)
    ext = file_path.suffix.lower() or ".ogg"
    content_type = "audio/ogg" if ext == ".ogg" else "audio/wav"
    metadata = {
        "name": f"{session_id}_{problem_id}{ext}",
        "parents": [settings.GDRIVE_FOLDER_ID],
    }
    boundary = f"vocl-{uuid4().hex}"
    body = _build_multipart_body(metadata, file_path.read_bytes(), content_type, boundary)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            _DRIVE_UPLOAD_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": f"multipart/related; boundary={boundary}",
            },
            content=body,
        )
        resp.raise_for_status()
        file_id = str(resp.json().get("id") or "")
        if not file_id:
            raise RuntimeError("Google Drive upload response missing file id")
        return f"gdrive:{file_id}"


async def upload_and_cleanup_session_audio(session_id: str, problem_id: str, local_path: Path) -> str | None:
    """Upload audio to Google Drive, update sessions.audio_path, and remove local file."""
    try:
        remote_ref = await upload_session_audio(local_path, session_id, problem_id)
        if not remote_ref:
            return None
        await update_session_audio_path(session_id, remote_ref)
        local_path.unlink(missing_ok=True)
        logger.info("Archived session %s audio to %s and removed local file", session_id, remote_ref)
        return remote_ref
    except Exception:
        logger.exception("Background Google Drive upload failed for session %s", session_id)
        return None
