"""Reads the API key (and your phone number) from the .env file one folder up.

Never print these, and never put them in a slide.
"""
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

env = {}
for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        name, value = line.split("=", 1)
        env[name.strip()] = value.strip().strip('"')

KEY = env["SMALLEST_API_KEY"]
MY_PHONE = env.get("MY_PHONE", "")
HEADERS = {"Authorization": f"Bearer {KEY}"}
CLIPS = Path(__file__).resolve().parent.parent / "clips"
