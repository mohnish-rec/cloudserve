"""Setup Guide step 05: create the decision log database.

The guide's table with five added columns (marked), so a run can be
reconciled and every decision traced to the model that made it.
Run: python scripts/setup_decision_log.py
"""
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
url = os.environ["DATABASE_URL"]  # sqlite:///./storage/decisions.db
prefix = "sqlite:///"
if not url.startswith(prefix):
    raise SystemExit(f"DATABASE_URL must start with {prefix} (got {url!r})")
DB_PATH = (ROOT / url[len(prefix):]).resolve()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # guide's code fails if storage/ does not exist yet

connection = sqlite3.connect(DB_PATH)
connection.execute("""
CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,            -- added: which run made this decision (A8, A9)
    created_at TEXT NOT NULL,
    ticket_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    prediction TEXT,
    confidence REAL,
    alternatives TEXT,               -- added: runner-up predictions and their confidence
    threshold REAL,
    action_taken TEXT NOT NULL,
    reason TEXT NOT NULL,
    sources_used TEXT,
    guardrails TEXT,
    provider TEXT,                   -- added: which provider answered, or none (A11)
    model TEXT,                      -- added: which model answered
    latency_ms INTEGER,              -- added: time taken, for the 95th percentile target
    prompt_version TEXT,
    requirement_ids TEXT
)
""")
connection.commit()

columns = [row[1] for row in connection.execute("PRAGMA table_info(decisions)")]
rows = connection.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
connection.close()
shown = DB_PATH.relative_to(ROOT) if DB_PATH.is_relative_to(ROOT) else DB_PATH
print(f"decision log ready: {shown} ({len(columns)} columns, {rows} rows)")