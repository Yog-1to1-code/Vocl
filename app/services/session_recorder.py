"""Optional stereo WAV recorder for live interview sessions (Left = User, Right = Vocl AI)."""
from __future__ import annotations

import audioop
import logging
import shutil
import struct
import sys
import time
from array import array
from pathlib import Path

from app.config import DOWNSTREAM_SAMPLE_RATE, UPSTREAM_SAMPLE_RATE

logger = logging.getLogger(__name__)

_RECORDINGS_DIR = Path("data/recordings")


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
    """Captures timestamped 16kHz upstream + 24kHz downstream PCM and writes a 24kHz stereo WAV."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
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
        _RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = _RECORDINGS_DIR / f"session_{self.session_id}.wav"

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

        latest_path = _RECORDINGS_DIR / "latest_session_mix.wav"
        shutil.copyfile(out_path, latest_path)
        logger.info("Saved stereo session mix: %s (%.1fs)", out_path, total / DOWNSTREAM_SAMPLE_RATE)
        return out_path
