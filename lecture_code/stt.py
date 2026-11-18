"""Speech to text (slide 12): send a recording, get the words back.

    python stt.py          the sentence as a laptop records it (16 kHz)
    python stt.py phone    the same sentence cut to 8 kHz, like a phone call (slides 29 and 30)

Costs a fraction of a cent per run.
"""
import sys
import time

import requests

from _env import CLIPS, HEADERS

clip = CLIPS / ("sentence_8k.wav" if "phone" in sys.argv else "sentence_16k.wav")
audio = clip.read_bytes()

start = time.perf_counter()
reply = requests.post(
    "https://api.smallest.ai/waves/v1/stt/",
    params={"model": "pulse", "language": "en", "word_timestamps": "true"},
    headers={**HEADERS, "Content-Type": "application/octet-stream"},
    data=audio,
    timeout=60,
)
reply.raise_for_status()
took = (time.perf_counter() - start) * 1000
result = reply.json()

print(f"Clip: {clip.name}")
print(f"Heard: {result['transcription']}   ({took:.0f} ms)")
for word in result.get("words", []):
    print(f"  {word['start']:5.2f}s  {word['word']:<12} sure: {word['confidence']:.0%}")
