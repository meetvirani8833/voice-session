# Mingos: the code behind the demo

Short files to show at the end of the talk, if there's time. Each one is a piece of the
call the class heard, in the order the talk covers them. The key and your phone number
come from `../.env` and are never printed.

| Show | File | What it shows | Slides |
| --- | --- | --- | --- |
| 1 | `prompt.py` | The instructions the model reads before every reply | 13, 25 |
| 2 | `agent.py` | Every setting in one place: VAD, the 800 ms endpointing wait, barge-in, the voice, the five-minute cap | 10, 11, 14, 23 |
| 3 | `stt.py` | Speech to text on the sentence, with the time of each word | 12, 29, 30 |
| 4 | `tts.py` | The reply in Mingos's voice, made all at once and then streamed | 14, 24 |
| 5 | `call_me.py` | How the platform rang my phone: one request | 31 |
| 6 | `bridge.py` | Sketch: what a telephony provider streams to your own server | 29, 31 |

## Running them live

From this folder, with the voice-session virtual environment active:

```
python prompt.py         free: prints the prompt and how many words it is
python stt.py            a fraction of a cent
python stt.py phone      the same, on the 8 kHz copy
python tts.py            a fraction of a cent; saves reply.wav
python agent.py          free: publishes the settings to the live agent
python call_me.py        rings MY_PHONE: about ₹11.5 a minute
```

`bridge.py` is never run in class. It needs `pip install websockets` and a real
provider pointing at it.

Run `stt.py` once before class: the first request of the day took about 4 seconds,
and the next one well under 1.

Good moments to run live: `stt.py` then `stt.py phone` (does the 8 kHz copy still
hear "Central Block"?), and `tts.py` (all at once against streamed, the same gap as
slides 23 and 24).
