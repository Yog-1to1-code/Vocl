"""Backwards-compatible re-export of SessionAudioRecorder."""
from app.services.audio_recorder import DEFAULT_RECORDINGS_DIR as _RECORDINGS_DIR, SessionAudioRecorder

__all__ = ["SessionAudioRecorder", "_RECORDINGS_DIR"]
