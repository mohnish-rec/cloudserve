"""Setup Guide step 03, 'Checking it works': one real call to each model.

Adapted from the guide's snippet for Groq (the guide allows OpenRouter or Groq).
Run: python scripts/check_model.py
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ["LLM_BASE_URL"]
API_KEY = os.environ["LLM_API_KEY"]  # fails loudly if absent, which is what you want
MODELS = {"main": os.environ["MODEL_NAME"], "backup": os.environ["BACKUP_MODEL_NAME"]}

all_ok = True
for label, model in MODELS.items():
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with the word ready."}],
        "max_tokens": 200,
    }
    if "gpt-oss" in model:
        body["reasoning_effort"] = "low"  # otherwise gpt-oss can spend every token thinking
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=body,
        timeout=30,
    )
    print(f"{label}: {model} {response.status_code}")
    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"] or ""
        print("  reply:", reply.strip())
    else:
        all_ok = False
        print("  error:", response.text[:300])

sys.exit(0 if all_ok else 1)