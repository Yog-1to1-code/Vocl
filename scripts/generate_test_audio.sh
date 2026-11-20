#!/bin/bash
# Generates a spoken 16kHz PCM fixture for the live smoke test.
set -euo pipefail

SCRIPT="For the longest palindromic substring problem, my approach is to use two nested loops to generate every possible substring, and then a third inner loop to check if each substring is a palindrome by comparing characters from both ends. I'll track the longest valid one and return it. That gives me a simple solution using constant extra space."

mkdir -p tests/fixtures

echo "→ Synthesizing speech via macOS 'say'..."
say -o /tmp/palindrome_approach.aiff "$SCRIPT"

echo "→ Converting to 16kHz 16-bit mono WAV..."
afconvert /tmp/palindrome_approach.aiff \
  -o tests/fixtures/palindrome_approach.wav \
  -d LEI16@16000 -f WAVE -c 1

echo "→ Extracting raw PCM from WAV..."
python3 -c "
import wave
with wave.open('tests/fixtures/palindrome_approach.wav', 'rb') as w:
    raw = w.readframes(w.getnframes())
with open('tests/fixtures/palindrome_approach.pcm', 'wb') as f:
    f.write(raw)
print(f'Generated {len(raw)} bytes of raw 16kHz 16-bit mono PCM ({len(raw)/32000:.1f}s)')
"

echo "✓ Fixtures ready:"
ls -lh tests/fixtures/palindrome_approach.*
