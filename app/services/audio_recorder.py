"""Per-session stereo audio recorder with Opus (.ogg) compression and WAV fallback."""
from __future__ import annotations

import asyncio
import audioop
import logging
import math
import shutil
import struct
import sys
import time
from array import array
from pathlib import Path

from app.config import DOWNSTREAM_SAMPLE_RATE, UPSTREAM_SAMPLE_RATE

logger = logging.getLogger(__name__)

DEFAULT_RECORDINGS_DIR = Path("data/recordings")
_ACTIVE_SAMPLE_THRESHOLD = 120
_FALLBACK_TARGET_RMS = 3500.0
_MAX_USER_GAIN = 6.0


def _active_rms(samples: array) -> float:
    sq_sum = 0.0
    count = 0
    for s in samples:
        if abs(s) > _ACTIVE_SAMPLE_THRESHOLD:
            sq_sum += float(s) * float(s)
            count += 1
    return math.sqrt(sq_sum / count) if count > 0 else 0.0


def _normalize_user_channel(left: array, right: array) -> array:
    """Match user mic loudness to the AI channel with soft-clipping to prevent distortion."""
    user_rms = _active_rms(left)
    if user_rms <= 0.0:
        return left
    ai_rms = _active_rms(right)
    target_rms = ai_rms if ai_rms > 500.0 else _FALLBACK_TARGET_RMS
    gain = min(_MAX_USER_GAIN, max(1.5, target_rms / user_rms))
    return array("h", (int(round(32767.0 * math.tanh((s * gain) / 32767.0))) for s in left))


def _place_chunks(chunks: list[tuple[float, bytes]]) -> array:
    if not chunks:
        return array("h")
    placements: list[tuple[int, array]] = []
    cursor = 0
    for elapsed_sec, pcm in chunks:
        samples = array("h")
        samples.frombytes(pcm[: len(pcm) - (len(pcm) % 2)])
        if sys.byteorder == "big":
            samples.byteswap()
        start = max(cursor, int(elapsed_sec * DOWNSTREAM_SAMPLE_RATE))
        placements.append((start, samples))
        cursor = start + len(samples)

    timeline = array("h", [0]) * cursor
    for start, samples in placements:
        timeline[start : start + len(samples)] = samples
    return timeline


class SessionAudioRecorder:
    """Captures timestamped 16kHz user + 24kHz AI PCM and saves compact Opus (.ogg) or WAV."""

    def __init__(self, session_id: str, recordings_dir: Path | None = None) -> None:
        self.session_id = session_id
        self._recordings_dir = recordings_dir or DEFAULT_RECORDINGS_DIR
        self._t0 = time.monotonic()
        self._user_chunks: list[tuple[float, bytes]] = []
        self._ai_chunks: list[tuple[float, bytes]] = []

    def record_user_pcm(self, pcm_16k: bytes) -> None:
        self._user_chunks.append((time.monotonic() - self._t0, pcm_16k))

    def record_ai_pcm(self, pcm_24k: bytes) -> None:
        self._ai_chunks.append((time.monotonic() - self._t0, pcm_24k))

    def save_stereo_wav(self) -> Path | None:
        if not self._user_chunks and not self._ai_chunks:
            return None
        self._recordings_dir.mkdir(parents=True, exist_ok=True)
        out_path = self._recordings_dir / f"{self.session_id}.wav"

        rate_state = None
        user_24k: list[tuple[float, bytes]] = []
        for ts, pcm_16k in self._user_chunks:
            even = pcm_16k[: len(pcm_16k) - (len(pcm_16k) % 2)]
            if not even:
                continue
            resampled, rate_state = audioop.ratecv(even, 2, 1, UPSTREAM_SAMPLE_RATE, DOWNSTREAM_SAMPLE_RATE, rate_state)
            user_24k.append((ts, resampled))

        left = _place_chunks(user_24k)
        right = _place_chunks(self._ai_chunks)
        left = _normalize_user_channel(left, right)
        total = max(len(left), len(right))
        if len(left) < total:
            left.extend([0] * (total - len(left)))
        if len(right) < total:
            right.extend([0] * (total - len(right)))

        interleaved = array("h", [0]) * (total * 2)
        interleaved[0::2] = left
        interleaved[1::2] = right
        if sys.byteorder == "big":
            interleaved.byteswap()

        pcm_bytes = interleaved.tobytes()
        with open(out_path, "wb") as f:
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + len(pcm_bytes)))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write(struct.pack("<IHHIIHH", 16, 1, 2, DOWNSTREAM_SAMPLE_RATE, DOWNSTREAM_SAMPLE_RATE * 4, 4, 16))
            f.write(b"data")
            f.write(struct.pack("<I", len(pcm_bytes)))
            f.write(pcm_bytes)

        logger.info("Saved stereo WAV mix: %s (%.1fs)", out_path, total / DOWNSTREAM_SAMPLE_RATE)
        return out_path

    async def save_recording(self) -> Path | None:
        """Write Opus .ogg (24 kbps) via ffmpeg when available, falling back to .wav."""
        wav_path = self.save_stereo_wav()
        if wav_path is None:
            return None

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            logger.info("ffmpeg not found on PATH; keeping WAV recording %s", wav_path)
            return wav_path

        ogg_path = self._recordings_dir / f"{self.session_id}.ogg"
        try:
            proc = await asyncio.create_subprocess_exec(
                ffmpeg_bin,
                "-y",
                "-i",
                str(wav_path),
                "-c:a",
                "libopus",
                "-b:a",
                "24k",
                "-vbr",
                "on",
                str(ogg_path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            if proc.returncode == 0 and ogg_path.exists() and ogg_path.stat().st_size > 0:
                wav_path.unlink(missing_ok=True)
                logger.info("Compressed recording to Opus: %s (%d bytes)", ogg_path, ogg_path.stat().st_size)
                return ogg_path
            logger.warning("ffmpeg exited %s; keeping WAV fallback: %s", proc.returncode, stderr.decode(errors="ignore")[:200])
        except Exception:
            logger.warning("ffmpeg Opus compression failed; keeping WAV fallback", exc_info=True)
            ogg_path.unlink(missing_ok=True)
        return wav_path
