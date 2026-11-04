"""Setup Guide step 03, 'Checking it works': one real call to each configured model.

Adapted from the guide's snippet for Groq (the guide allows OpenRouter or Groq).
The optional fallback provider is checked only if FALLBACK_API_KEY is set.
Run: python scripts/check_model.py
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

# (label, base URL, key, model). os.environ[...] fails loudly if a required value is absent.
CHECKS = [
    ("main", os.environ["LLM_BASE_URL"], os.environ["LLM_API_KEY"], os.environ["MODEL_NAME"]),
    ("backup", os.environ["LLM_BASE_URL"], os.environ["LLM_API_KEY"], os.environ["BACKUP_MODEL_NAME"]),
]
if os.getenv("FALLBACK_API_KEY"):
    CHECKS.append(("fallback", os.environ["FALLBACK_BASE_URL"],
                   os.environ["FALLBACK_API_KEY"], os.environ["FALLBACK_MODEL_NAME"]))

all_ok = True
for label, base_url, key, model in CHECKS:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with the word ready."}],
        "max_tokens": 200,
    }
    if "gpt-oss" in model:
        body["reasoning_effort"] = "low"  # otherwise gpt-oss can spend every token thinking
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
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

if not os.getenv("FALLBACK_API_KEY"):
    print("fallback: skipped (FALLBACK_API_KEY is empty, so failures escalate to a person)")

sys.exit(0 if all_ok else 1)