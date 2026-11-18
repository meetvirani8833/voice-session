"""SKETCH, not used by Mingos: what a telephony provider sends your server (slides 29 and 31).

Mingos doesn't need this file, because the voice platform runs this part for us.
If you ran your own agent server instead, the provider would open a WebSocket to it
(server to server, slide 22) and stream the call like this:

  {"event": "start"}                               the call is connected
  {"event": "media", "media": {"payload": "..."}}  20 ms of the caller's voice, every 20 ms
  {"event": "stop"}                                the caller hung up

The audio is 8,000 samples a second (slide 29), squeezed into one byte per sample
by G.711 mu-law, the phone network's old codec (slide 9). Message names differ a
little between providers; the idea is the same everywhere.

    pip install websockets
    python bridge.py
"""
import asyncio
import base64
import json

import websockets


def mulaw_to_pcm(byte):
    """Undo G.711 mu-law: one byte back into one 16-bit sample."""
    byte = ~byte & 0xFF
    sign, exponent, mantissa = byte & 0x80, (byte >> 4) & 0x07, byte & 0x0F
    sample = (((mantissa << 3) + 0x84) << exponent) - 0x84
    return -sample if sign else sample


async def handle_call(ws):
    async for message in ws:
        event = json.loads(message)

        if event["event"] == "start":
            print("Call connected")

        elif event["event"] == "media":
            chunk = base64.b64decode(event["media"]["payload"])   # 160 bytes = 20 ms at 8 kHz
            samples = [mulaw_to_pcm(b) for b in chunk]
            # Next, the six steps from Part 2:
            # VAD -> endpointing -> speech to text -> model -> text to speech,
            # then send the reply's audio back the same way:
            # await ws.send(json.dumps({"event": "media", "media": {"payload": reply_audio_base64}}))

        elif event["event"] == "stop":
            print("Caller hung up")


async def main():
    async with websockets.serve(handle_call, "0.0.0.0", 8080):
        print("Waiting for the provider to connect on port 8080...")
        await asyncio.Future()   # run until stopped


if __name__ == "__main__":
    asyncio.run(main())
