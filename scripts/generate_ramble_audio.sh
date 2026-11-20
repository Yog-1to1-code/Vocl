#!/bin/bash
# Generates a ~25s rambling 16kHz PCM fixture to test mid-speech interruption.
set -euo pipefail

SCRIPT="For the longest palindromic substring problem, my approach is to use two nested loops to generate every possible substring, and a third inner loop to check if each substring is a palindrome from both ends. I'll just write a helper function called isPalindrome that takes left and right pointers, increments left, decrements right, and returns true if they match. Then in my main function, I'll initialize maxLength to zero, bestStart to zero, and every time isPalindrome returns true and the length is greater than maxLength, I'll update maxLength and bestStart, and finally slice the string at the end."

mkdir -p tests/fixtures

say -o /tmp/palindrome_ramble.aiff "$SCRIPT"
afconvert /tmp/palindrome_ramble.aiff \
  -o tests/fixtures/palindrome_ramble.wav \
  -d LEI16@16000 -f WAVE -c 1

python3 -c "
import wave
with wave.open('tests/fixtures/palindrome_ramble.wav', 'rb') as w:
    raw = w.readframes(w.getnframes())
with open('tests/fixtures/palindrome_ramble.pcm', 'wb') as f:
    f.write(raw)
print(f'Generated {len(raw)} bytes of 16kHz PCM ({len(raw)/32000:.1f}s)')
"

ls -lh tests/fixtures/palindrome_ramble.*
