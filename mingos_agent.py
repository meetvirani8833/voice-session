"""Moved: the agent's settings now live in lecture_code/agent.py. This runs that file."""
import os
import runpy
import sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lecture_code")
sys.path.insert(0, HERE)
runpy.run_path(os.path.join(HERE, "agent.py"), run_name="__main__")
