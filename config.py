import os

OPENAI_KEY = os.getenv("OPENAI_KEY", None)
if OPENAI_KEY is None:
    raise ValueError("OPENAI_KEY is not set")
GH_ACCESS_TOKEN = os.getenv("GH_ACCESS_TOKEN", None)
if GH_ACCESS_TOKEN is None:
    raise ValueError("GH_ACCESS_TOKEN is not set")
