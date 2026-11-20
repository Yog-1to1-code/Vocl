#!/usr/bin/env python3
"""
One-shot live smoke test for the Vocl interview pipeline.
Kept in scripts/ (outside tests/) to prevent accidental API quota burn.

Usage:
    cd /Users/yogesh/Desktop/Vocl
    .venv/bin/python scripts/test_live_smoke.py
"""

import asyncio, csv, json, os, struct, sys, time
from pathlib import Path

try:
    import websockets
except ImportError:
    sys.exit("websockets not installed – run: .venv/bin/pip install websockets")

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "palindrome_approach.pcm"
RESPONSE_WAV = ROOT / "tests" / "fixtures" / "last_ai_response.wav"
CSV_PATH = ROOT / "data" / "sessions.csv"
WS_URL = "ws://localhost:8080/ws/interview/longest-palindrome"

CHUNK_SIZE = 3200          # 100ms of 16kHz 16-bit mono
SILENCE_DURATION = 2.0     # seconds of trailing silence
CONNECT_TIMEOUT = 10
GREETING_TIMEOUT = 15
RESPONSE_TIMEOUT = 20


def write_wav(path: Path, pcm: bytes, sample_rate: int = 24000):
    """Write raw PCM bytes as a 16-bit mono WAV."""
    n = len(pcm)
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + n))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<I", n))
        f.write(pcm)


async def run():
    t0 = time.time()
    log = lambda msg: print(f"[{time.time()-t0:6.2f}s] {msg}")

    if not FIXTURE.exists():
        sys.exit(f"Missing fixture: {FIXTURE}\nRun: bash scripts/generate_test_audio.sh")

    pcm_data = FIXTURE.read_bytes()
    log(f"Loaded fixture: {len(pcm_data)} bytes ({len(pcm_data)/32000:.1f}s of 16kHz PCM)")

    # Count CSV rows before
    csv_rows_before = 0
    if CSV_PATH.exists():
        with open(CSV_PATH) as f:
            csv_rows_before = sum(1 for _ in csv.reader(f)) - 1  # minus header

    # Connect
    log(f"Connecting to {WS_URL}")
    ws = await asyncio.wait_for(websockets.connect(WS_URL), timeout=CONNECT_TIMEOUT)
    log("Connected")

    states_seen = []
    audio_chunks = []
    autopsy = None
    greeting_done = asyncio.Event()
    session_done = asyncio.Event()

    async def receiver():
        nonlocal autopsy
        try:
            async for msg in ws:
                if isinstance(msg, bytes):
                    audio_chunks.append(msg)
                    continue
                frame = json.loads(msg)
                ft = frame.get("type", "")
                if ft == "state":
                    status = frame.get("status", "")
                    states_seen.append(status)
                    log(f"State → {status}")
                    if status == "listening" and len(states_seen) > 1:
                        greeting_done.set()
                elif ft == "tool_result":
                    verdict = {k: v for k, v in frame.items() if k != "type"}
                    log(f"Tool result: {json.dumps(verdict, indent=2)[:240]}")
                elif ft == "autopsy":
                    autopsy = frame
                    log("Autopsy received")
                    session_done.set()
                elif ft == "error":
                    log(f"ERROR from server: {frame}")
                    session_done.set()
        except websockets.exceptions.ConnectionClosed:
            log("WebSocket closed by server")
            session_done.set()

    recv_task = asyncio.create_task(receiver())

    # Wait for greeting to finish
    log("Waiting for greeting to complete...")
    try:
        await asyncio.wait_for(greeting_done.wait(), timeout=GREETING_TIMEOUT)
    except asyncio.TimeoutError:
        log("⚠ Greeting timeout – proceeding anyway")

    # Stream PCM fixture in 100ms chunks
    log("Streaming user audio...")
    offset = 0
    while offset < len(pcm_data):
        chunk = pcm_data[offset:offset + CHUNK_SIZE]
        await ws.send(chunk)
        offset += CHUNK_SIZE
        await asyncio.sleep(0.1)
    log(f"Sent {offset} bytes of speech")

    # Send trailing silence
    log(f"Sending {SILENCE_DURATION}s silence...")
    silence_chunk = b"\x00" * CHUNK_SIZE
    for _ in range(int(SILENCE_DURATION / 0.1)):
        await ws.send(silence_chunk)
        await asyncio.sleep(0.1)
    log("Silence sent")

    # Wait for AI response cycle to complete
    log("Waiting for AI response...")
    try:
        await asyncio.wait_for(session_done.wait(), timeout=RESPONSE_TIMEOUT)
    except asyncio.TimeoutError:
        # Send end_session if not done yet
        pass

    # End session
    log("Sending end_session...")
    try:
        await ws.send(json.dumps({"type": "end_session"}))
        if not session_done.is_set():
            await asyncio.wait_for(session_done.wait(), timeout=10)
    except Exception as e:
        log(f"end_session send error (may be closed already): {e}")

    recv_task.cancel()
    try:
        await recv_task
    except asyncio.CancelledError:
        pass

    # ── Results ──────────────────────────────────────────────
    total_audio = sum(len(c) for c in audio_chunks)
    log(f"\n{'='*60}")
    log(f"States observed: {states_seen}")
    log(f"Audio chunks received: {len(audio_chunks)} ({total_audio} bytes)")

    # Assertions
    ok = True
    if "analyzing" in states_seen:
        log("✓ 'analyzing' state observed (tool call fired)")
    else:
        log("✗ 'analyzing' state NOT observed")
        ok = False

    if total_audio > 0:
        log(f"✓ Received {total_audio} bytes of 24kHz PCM audio ({total_audio/48000:.1f}s)")
    else:
        log("✗ No audio bytes received")
        ok = False

    if autopsy:
        log(f"✓ Autopsy JSON:\n{json.dumps(autopsy, indent=2)}")
    else:
        log("✗ No autopsy received")
        ok = False

    # Save AI response audio
    if total_audio > 0:
        all_audio = b"".join(audio_chunks)
        write_wav(RESPONSE_WAV, all_audio, sample_rate=24000)
        log(f"✓ Saved AI response → {RESPONSE_WAV}")

    # Check CSV
    csv_rows_after = 0
    if CSV_PATH.exists():
        with open(CSV_PATH) as f:
            csv_rows_after = sum(1 for _ in csv.reader(f)) - 1
    if csv_rows_after > csv_rows_before:
        log(f"✓ CSV row appended ({csv_rows_before} → {csv_rows_after})")
    else:
        log("✗ No new CSV row found")
        ok = False

    log(f"{'='*60}")
    log(f"{'✓ ALL CHECKS PASSED' if ok else '✗ SOME CHECKS FAILED'}")
    log(f"Total elapsed: {time.time()-t0:.1f}s")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(run())
