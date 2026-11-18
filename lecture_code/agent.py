"""The agent (Parts 2 and 3): every setting from the talk, in one place.

Running this publishes a new version of the live Mingos agent with these settings.
It's free and takes about half a minute. Only run it when you change something.
"""
import time

import requests

from _env import HEADERS
from prompt import FIRST_MESSAGE, PROMPT

AGENT_ID = "6af94772057531c582e7374b"
API = "https://api.smallest.ai/atoms/v1"

END_CALL = {"name": "end_call", "type": "end_call", "enabled": True,
            "description": "Terminate the call when conversation is complete."}

settings = {
    # Decide the reply (slide 13): the prompt, plus one tool the model may use: hanging up
    "singlePromptConfig": {"prompt": PROMPT, "tools": [END_CALL]},
    "globalPrompt": "",
    "firstMessage": FIRST_MESSAGE,

    # Hear the caller (slides 10 and 11)
    "voiceDetectionConfig": {
        "confidence": 0.7,          # VAD: how sure it must be that this is speech
        "minVolume": 0.6,           # VAD: ignore quiet background noise
        "triggerTimeInSecs": 0.2,   # VAD: 200 ms of speech before it counts as talking
        "releaseTimeInSecs": 0.8,   # endpointing: 800 ms of silence means "they've finished"
    },                              #   (that's the 800 ms bar on slides 23 and 24)
    "allowInterruptions": True,     # barge-in: stop talking when the caller starts (slide 10)

    # Text to speech (slide 14): Mingos's voice
    "synthesizer": {
        "voiceConfig": {"model": "waves_lightning_v3_1_pro", "voiceId": "meher", "gender": "female"},
        "speed": 1,
        "sampleRate": 24000,
        "numberPronunciationLanguage": "auto",
    },

    # Every call ends after five minutes, whatever happens
    "sessionTimeoutConfig": {"timeoutTimeInSecs": 300},
    "timezone": {"label": "(GMT+0:00) UTC", "offset": 0},

    # The "Talk to Mingos" button on the web page (not part of the talk)
    "widgetConfig": {
        "mode": "voice", "theme": "light", "size": "full", "position": "bottom-right",
        "widgetName": "Mingos", "title": "Mingos", "ctaName": "Talk to Mingos",
        "startButtonText": "Start call", "endButtonText": "End call", "voiceShowTranscript": True,
        "accentColor": "#E0662A", "textOnAccentColor": "#FFFFFF", "baseColor": "#FBFCFE",
        "primaryTextColor": "#14243D", "secondaryTextColor": "#50607A", "agentBubbleColor": "#F3F6FA",
    },
}


def api(method, path, body=None):
    reply = requests.request(method, API + path, headers=HEADERS, json=body, timeout=60)
    reply.raise_for_status()
    return reply.json()["data"]


if __name__ == "__main__":
    branches = api("GET", f"/agent/{AGENT_ID}/branches")["branches"]
    branch = next(b["branch"]["_id"] for b in branches if b["branch"].get("isDefault"))

    latest = api("GET", f"/agent/{AGENT_ID}/branches/{branch}/revisions?limit=1")["revisions"][0]["revisionNumber"]
    api("PUT", f"/agent/{AGENT_ID}/branches/{branch}/draft", settings)
    api("POST", f"/agent/{AGENT_ID}/branches/{branch}/draft/publish", {"label": "Mingos settings"})
    print("Publishing...")

    for _ in range(30):
        time.sleep(4)
        revision = api("GET", f"/agent/{AGENT_ID}/branches/{branch}/revisions?limit=1")["revisions"][0]
        if revision["revisionNumber"] > latest and revision.get("status") == "published":
            print(f"Live: version {revision['revisionNumber']}")
            break
    else:
        print("Still publishing. Check the dashboard in a minute.")
