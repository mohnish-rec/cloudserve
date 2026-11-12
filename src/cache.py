"""Reply cache (D-025): the same prompt to the same model is answered once, then reused.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Build Specification: "Free tiers throttle. Handling that with backoff, queuing and caching is part of
the engineering." The tickets repeat: 343 different texts among the 500 development tickets.

The key is a hash of everything the model receives (the prompt version's text, the ticket, the
articles) and the model list, so a changed prompt, ticket, article or model never reuses an old answer.
Only answers that were read successfully are stored. Replies hold no personal details (guardrail 1
blocks any that do), and the cache lives in storage/, which Git ignores.
Turned off with REPLY_CACHE=off. Only the real model call uses it; tests with fake models never do.
The harness (src/run_evaluation.py) turns it OFF for every run unless --use-cache is given, and that
flag is only for development runs: validation, hidden-set and final runs neither read nor write it,
so they stay a fresh, independent test, as the assessors' run will be (9 Nov, Mohnish's point).
"""
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def enabled() -> bool:
    return os.getenv("REPLY_CACHE", "on").strip().lower() not in {"off", "0", "false", "no"}


def path() -> Path:
    p = Path(os.getenv("CACHE_PATH", "storage/cache.db"))
    return p if p.is_absolute() else ROOT / p


def key(messages, models) -> str:
    return hashlib.sha256(json.dumps([list(models), messages], sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def _connect():
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, model TEXT, raw TEXT, created_at TEXT)")
    return con


def get(k):
    """(raw text, model) or None. Never raises: a broken cache just means a fresh call."""
    try:
        con = _connect()
        row = con.execute("SELECT raw, model FROM cache WHERE key = ?", (k,)).fetchone()
        con.close()
        return row
    except Exception:  # noqa: BLE001
        return None


def put(k, raw, model):
    try:
        con = _connect()
        con.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?)",
                    (k, model, str(raw), datetime.now(timezone.utc).isoformat(timespec="seconds")))
        con.commit()
        con.close()
    except Exception:  # noqa: BLE001
        pass
