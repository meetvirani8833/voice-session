"""Kept so the older scripts still run. The prompt itself now lives in lecture_code/prompt.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lecture_code"))
from prompt import FIRST_MESSAGE as FIRST, PROMPT  # noqa: E402,F401
