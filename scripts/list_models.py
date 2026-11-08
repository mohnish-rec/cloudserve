"""List the models the provider offers right now, so model names are checked, not remembered.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Found on 8 Nov 2026: llama-3.1-8b-instant returned HTTP 404 (no longer offered).
Prints model names only, never the key.
Run: python scripts/list_models.py
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()
r = requests.get(f"{os.environ['LLM_BASE_URL']}/models",
                 headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}"}, timeout=30)
print("HTTP", r.status_code)
if r.status_code == 200:
    for m in sorted(r.json().get("data", []), key=lambda m: m["id"]):
        print(f"  {m['id']:<50} owned by {m.get('owned_by', '?')}")
else:
    print(r.text[:300])
