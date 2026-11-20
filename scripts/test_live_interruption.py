#!/usr/bin/env python3
"""
Synchronized two-way live interruption test for Vocl.
Streams a rambling approach without stopping, records exact timestamps for System 1/2
events, and mixes a 24kHz stereo WAV (Left = Candidate, Right = Vocl AI).

Usage:
    cd /Users/yogesh/Desktop/Vocl
    .venv/bin/python scripts/test_live_interruption.py
"""
from __future__ import annotations

import asyncio
import audioop
import json
import struct
import sys
import time
from array import array
from pathlib import Path

try:
    import websockets
except ImportError:
    sys.exit("websockets not installed — run: .venv/bin/pip install websockets")

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "palindrome_ramble.pcm"
MIX_WAV_PATH = ROOT / "tests" / "fixtures" / "live_interruption_mix.wav"
WS_URL = "ws://localhost:8080/ws/interview/longest-palindrome"

USER_SAMPLE_RATE = 16000
MIX_SAMPLE_RATE = 24000
CHUNK_BYTES = 3200         # 100ms of 16kHz 16-bit mono PCM
CHUNK_INTERVAL_SEC = 0.1
TRAILING_SILENCE_SEC = 3.0
GREETING_TIMEOUT_SEC = 20.0
POST_SPEECH_TIMEOUT_SEC = 20.0


def _resample_16k_to_24k(pcm_16k: bytes, state: tuple | None) -> tuple[bytes, tuple]:
    return audioop.ratecv(pcm_16k, 2, 1, USER_SAMPLE_RATE, MIX_SAMPLE_RATE, state)


def _place_channel_chunks(chunks: list[tuple[float, bytes]]) -> array:
    """Place timestamped 24kHz mono PCM chunks onto a timeline without overlapping bursts."""
    if not chunks:
        return array("h")

    placements: list[tuple[int, array]] = []
    cursor = 0
    for elapsed_sec, pcm in chunks:
        samples = array("h")
        samples.frombytes(pcm)
        if sys.byteorder == "big":
            samples.byteswap()
        target = int(elapsed_sec * MIX_SAMPLE_RATE)
        # Advance to wall-clock offset after gaps while keeping burst chunks contiguous
        start = max(cursor, target)
        placements.append((start, samples))
        cursor = start + len(samples)

    timeline = array("h", [0]) * cursor
    for start, samples in placements:
        timeline[start : start + len(samples)] = samples
    return timeline


def write_stereo_mix_wav(
    path: Path,
    user_chunks_16k: list[tuple[float, bytes]],
    ai_chunks_24k: list[tuple[float, bytes]],
) -> float:
    """Mix Left (user, resampled to 24kHz) and Right (AI, 24kHz) into a stereo WAV."""
    rate_state = None
    user_chunks_24k: list[tuple[float, bytes]] = []
    for ts, pcm_16k in user_chunks_16k:
        pcm_24k, rate_state = _resample_16k_to_24k(pcm_16k, rate_state)
        user_chunks_24k.append((ts, pcm_24k))

    left = _place_channel_chunks(user_chunks_24k)
    right = _place_channel_chunks(ai_chunks_24k)
    total_frames = max(len(left), len(right))
    if len(left) < total_frames:
        left.extend([0] * (total_frames - len(left)))
    if len(right) < total_frames:
        right.extend([0] * (total_frames - len(right)))

    interleaved = array("h", [0]) * (total_frames * 2)
    interleaved[0::2] = left
    interleaved[1::2] = right
    if sys.byteorder == "big":
        interleaved.byteswap()

    pcm_bytes = interleaved.tobytes()
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + len(pcm_bytes)))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 2, MIX_SAMPLE_RATE, MIX_SAMPLE_RATE * 4, 4, 16))
        f.write(b"data")
        f.write(struct.pack("<I", len(pcm_bytes)))
        f.write(pcm_bytes)

    return total_frames / MIX_SAMPLE_RATE


async def run_interruption_test() -> None:
    if not FIXTURE_PATH.exists():
        sys.exit(f"Missing fixture: {FIXTURE_PATH}\nRun: bash scripts/generate_ramble_audio.sh")

    pcm_data = FIXTURE_PATH.read_bytes()
    t0 = time.monotonic()
    elapsed = lambda: time.monotonic() - t0
    log = lambda msg: print(f"[+{elapsed():6.2f}s] {msg}")

    user_chunks: list[tuple[float, bytes]] = []
    ai_chunks: list[tuple[float, bytes]] = []
    timeline: dict[str, float | None] = {
        "greeting_start": None,
        "greeting_end": None,
        "user_speech_start": None,
        "user_speech_end": None,
        "analyzing": None,
        "tool_result": None,
        "ai_interrupt_start": None,
        "ai_interrupt_end": None,
        "counter_start": None,
        "counter_end": None,
    }
    tool_verdict: dict | None = None
    autopsy: dict | None = None

    greeting_done = asyncio.Event()
    post_interrupt_done = asyncio.Event()
    autopsy_received = asyncio.Event()

    log(f"Loaded fixture: {len(pcm_data)} bytes ({len(pcm_data) / (USER_SAMPLE_RATE * 2):.1f}s)")
    log(f"Connecting to {WS_URL}")
    ws = await asyncio.wait_for(websockets.connect(WS_URL), timeout=10.0)
    log("Connected")

    async def receive_loop() -> None:
        nonlocal tool_verdict, autopsy
        try:
            async for msg in ws:
                now = elapsed()
                if isinstance(msg, bytes):
                    ai_chunks.append((now, msg))
                    if not greeting_done.is_set():
                        if timeline["greeting_start"] is None:
                            timeline["greeting_start"] = now
                    elif timeline["user_speech_start"] is not None:
                        if timeline["ai_interrupt_start"] is None:
                            timeline["ai_interrupt_start"] = now
                            log("AI interruption audio STARTED")
                        timeline["ai_interrupt_end"] = now
                        # Counter-question = first AI audio after System 2 verdict
                        if timeline["tool_result"] is not None and not post_interrupt_done.is_set():
                            if timeline["counter_start"] is None:
                                timeline["counter_start"] = now
                                log("Counter-question audio STARTED")
                            timeline["counter_end"] = now
                    continue

                frame = json.loads(msg)
                frame_type = frame.get("type", "")
                if frame_type == "state":
                    status = frame.get("status", "")
                    log(f"State -> {status}")
                    if status == "speaking" and not greeting_done.is_set() and timeline["greeting_start"] is None:
                        timeline["greeting_start"] = now
                    elif status == "listening":
                        if not greeting_done.is_set() and timeline["greeting_start"] is not None:
                            timeline["greeting_end"] = now
                            greeting_done.set()
                        elif timeline["counter_start"] is not None:
                            timeline["counter_end"] = now
                            post_interrupt_done.set()
                    elif status == "analyzing" and timeline["analyzing"] is None:
                        timeline["analyzing"] = now
                elif frame_type == "tool_result":
                    timeline["tool_result"] = now
                    tool_verdict = {k: v for k, v in frame.items() if k != "type"}
                    log(f"Tool result: complexity={tool_verdict.get('time_complexity')} optimal={tool_verdict.get('is_optimal')}")
                elif frame_type == "autopsy":
                    autopsy = frame
                    log("Autopsy received")
                    autopsy_received.set()
                elif frame_type == "error":
                    log(f"Server ERROR: {frame}")
                    autopsy_received.set()
        except websockets.exceptions.ConnectionClosed:
            log("WebSocket closed by server")
            autopsy_received.set()

    recv_task = asyncio.create_task(receive_loop())

    log("Waiting for opening greeting to finish...")
    try:
        await asyncio.wait_for(greeting_done.wait(), timeout=GREETING_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        log("Greeting timeout — starting user audio stream")
        greeting_done.set()

    # Stream full ramble clip continuously without stopping on analyzing/speaking
    timeline["user_speech_start"] = elapsed()
    log("Streaming full rambling user speech (no stop on interrupt)...")
    offset = 0
    while offset < len(pcm_data):
        chunk = pcm_data[offset : offset + CHUNK_BYTES]
        user_chunks.append((elapsed(), chunk))
        await ws.send(chunk)
        offset += CHUNK_BYTES
        await asyncio.sleep(CHUNK_INTERVAL_SEC)
    timeline["user_speech_end"] = elapsed()
    log(f"User speech ended ({offset} bytes streamed)")

    # Stream trailing silence so Gemini finishes any pending turn
    silence = b"\x00" * CHUNK_BYTES
    log(f"Streaming {TRAILING_SILENCE_SEC:.0f}s trailing silence...")
    for _ in range(int(TRAILING_SILENCE_SEC / CHUNK_INTERVAL_SEC)):
        user_chunks.append((elapsed(), silence))
        await ws.send(silence)
        await asyncio.sleep(CHUNK_INTERVAL_SEC)

    if not post_interrupt_done.is_set():
        log(f"Waiting up to {POST_SPEECH_TIMEOUT_SEC:.0f}s for AI post-interruption speech to finish...")
        try:
            await asyncio.wait_for(post_interrupt_done.wait(), timeout=POST_SPEECH_TIMEOUT_SEC)
        except asyncio.TimeoutError:
            log("Post-interruption speech wait timed out")

    log("Sending end_session...")
    try:
        await ws.send(json.dumps({"type": "end_session"}))
        if not autopsy_received.is_set():
            await asyncio.wait_for(autopsy_received.wait(), timeout=10.0)
    except Exception as exc:
        log(f"end_session error: {exc}")

    recv_task.cancel()
    try:
        await recv_task
    except asyncio.CancelledError:
        pass
    await ws.close()

    duration_sec = write_stereo_mix_wav(MIX_WAV_PATH, user_chunks, ai_chunks)

    # ── Synchronized Timeline Summary ─────────────────────────────────────────
    user_end_ts = timeline["user_speech_end"]
    fmt = lambda v: f"+{v:05.2f}s" if v is not None else "   N/A "
    print("\n" + "=" * 68)
    print("SYNCHRONIZED TWO-WAY INTERRUPTION TIMELINE")
    print("=" * 68)
    print(f"  Opening greeting start   : {fmt(timeline['greeting_start'])}")
    print(f"  Opening greeting end     : {fmt(timeline['greeting_end'])}")
    print(f"  User speech start        : {fmt(timeline['user_speech_start'])}")
    print(f"  State -> analyzing       : {fmt(timeline['analyzing'])}")
    print(f"  System 2 tool_result     : {fmt(timeline['tool_result'])}")
    print(f"  AI interruption start    : {fmt(timeline['ai_interrupt_start'])}")
    print(f"  User speech end          : {fmt(timeline['user_speech_end'])}")
    print(f"  AI interruption end      : {fmt(timeline['ai_interrupt_end'])}")
    print(f"  Counter-question start   : {fmt(timeline['counter_start'])}")
    print(f"  Counter-question end     : {fmt(timeline['counter_end'])}")
    if timeline["analyzing"] is not None and timeline["tool_result"] is not None:
        print(f"  System 2 latency         : {timeline['tool_result'] - timeline['analyzing']:.2f}s")
    if timeline["counter_start"] is not None and user_end_ts is not None:
        print(f"  Gap (user end -> counter): {timeline['counter_start'] - user_end_ts:+.2f}s")
    print("-" * 68)

    ai_start = timeline["ai_interrupt_start"]
    user_end = timeline["user_speech_end"]
    if ai_start is not None and user_end is not None:
        delta = user_end - ai_start
        if delta > 0:
            print(f"  OVERLAP RESULT: MID-SPEECH INTERRUPT ({delta:.2f}s BEFORE user finished speaking)")
        else:
            print(f"  OVERLAP RESULT: Post-speech reply ({abs(delta):.2f}s AFTER user finished speaking)")
    else:
        print("  OVERLAP RESULT: No post-user AI audio observed")

    if tool_verdict:
        print(f"  System 2 verdict: {tool_verdict.get('time_complexity')} / {tool_verdict.get('space_complexity')} | optimal={tool_verdict.get('is_optimal')} | score={tool_verdict.get('score_delta')}")
    if autopsy:
        print(f"  Autopsy JSON:\n{json.dumps(autopsy, indent=2)}")
    print(f"  Stereo mix saved: {MIX_WAV_PATH} ({duration_sec:.1f}s, L=User, R=Vocl AI)")
    print("=" * 68)


if __name__ == "__main__":
    asyncio.run(run_interruption_test())
