"""Text to speech (slide 14), and why streaming wins (slide 24).

Makes the same reply twice in Mingos's voice:
  1. all at once: nothing can play until the whole reply is made
  2. streamed: audio arrives in pieces, so playback starts on the first one

Saves the first one as reply.wav next to this file. Costs a fraction of a cent per run.
"""
import time
from pathlib import Path

import requests

from _env import HEADERS

REPLY = "So that's two cold coffees to Central Block for one hundred and eighty rupees. Confirm that?"
VOICE = {"voice_id": "meher", "model": "lightning_v3.1_pro", "language": "en", "sample_rate": 24000}
TTS = "https://api.smallest.ai/waves/v1/tts"


def ms_since(start):
    return (time.perf_counter() - start) * 1000


# 1. All at once
start = time.perf_counter()
whole = requests.post(TTS, headers={**HEADERS, "Accept": "audio/wav"},
                      json={"text": REPLY, **VOICE, "output_format": "wav"}, timeout=60)
whole.raise_for_status()
out = Path(__file__).resolve().parent / "reply.wav"
out.write_bytes(whole.content)
print(f"All at once: first sound after {ms_since(start):.0f} ms  (saved {out.name})")

# 2. Streamed
start = time.perf_counter()
with requests.post(TTS + "/live", headers=HEADERS, json={"text": REPLY, **VOICE},
                   stream=True, timeout=60) as live:
    live.raise_for_status()
    for line in live.iter_lines():
        if line.startswith(b"data:") and b'"audio"' in line:
            print(f"Streamed:    first sound after {ms_since(start):.0f} ms")
            break
