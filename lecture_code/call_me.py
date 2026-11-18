"""The phone call (slide 31): how Mingos rang my phone for the recording.

The voice platform is also our telephony provider: it owns a phone number and the link
to the phone operators, so one request is enough to make it dial. It calls the number
saved as MY_PHONE in .env.

Costs real money: about eleven and a half rupees a minute (slide 36). Calls stop after five minutes.
"""
import requests

from _env import HEADERS, MY_PHONE

AGENT_ID = "6af94772057531c582e7374b"
API = "https://api.smallest.ai/atoms/v1"

branches = requests.get(f"{API}/agent/{AGENT_ID}/branches", headers=HEADERS, timeout=60).json()
branch = next(b["branch"]["_id"] for b in branches["data"]["branches"] if b["branch"].get("isDefault"))

reply = requests.post(
    f"{API}/agent/{AGENT_ID}/branches/{branch}/test-call",
    headers=HEADERS,
    json={"mode": "telephony", "toPhone": MY_PHONE, "includeDraft": False},
    timeout=60,
)
print("Ringing your phone now." if reply.ok else f"Didn't call: {reply.status_code}")
