"""The decision log: writes and reads storage/decisions.db (FR-10).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.

Every decision is checked against a fixed schema (Pydantic, Module 7) before it is
written; a record that fails the check raises, and the caller escalates the ticket
instead (FR-10). The table is the Setup Guide's (step 05) with the marked additions
in scripts/setup_decision_log.py. No customer name or ticket text is ever stored:
the input summary holds only channel, plan, region, fluency and length.
"""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
PREFIX = "sqlite:///"


def db_path(url=None) -> Path:
    url = url or os.getenv("DATABASE_URL", "sqlite:///./storage/decisions.db")
    if not url.startswith(PREFIX):
        raise ValueError(f"DATABASE_URL must start with {PREFIX}")
    p = Path(url[len(PREFIX):])
    return p if p.is_absolute() else (ROOT / p).resolve()


class DecisionRecord(BaseModel):
    run_id: str = Field(min_length=1)
    ticket_id: str = Field(min_length=1)               # the trace ID: one ticket, one trace
    stage: Literal["classification", "routing", "generation", "validation"]
    input_summary: str = Field(min_length=1)
    prediction: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    alternatives: List[dict] = []
    threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    action_taken: Literal["classified", "auto_respond", "escalate", "block"]
    label: str = ""
    reason: str = Field(min_length=10)                 # a sentence a support manager can read
    sources_used: List[dict] = []
    guardrails: dict = {}
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[int] = Field(default=None, ge=0)
    prompt_version: Optional[str] = None
    requirement_ids: List[str] = []

    @field_validator("label")
    @classmethod
    def label_is_known(cls, v):
        if v not in ("", "Draft ready: check and send", "Needs a specialist"):
            raise ValueError(f"unknown label {v!r}")
        return v


def connect(url=None) -> sqlite3.Connection:
    path = db_path(url)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: run python scripts/setup_decision_log.py")
    return sqlite3.connect(path)


def write(record: DecisionRecord, connection: sqlite3.Connection) -> str:
    record = DecisionRecord.model_validate(record.model_dump())     # re-check before writing
    decision_id = str(uuid.uuid4())
    row = record.model_dump()
    for k in ("alternatives", "sources_used", "guardrails", "requirement_ids"):
        row[k] = json.dumps(row[k])
    row.update(decision_id=decision_id, created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    cols = ", ".join(row)
    connection.execute(f"INSERT INTO decisions ({cols}) VALUES ({', '.join('?' * len(row))})", list(row.values()))
    connection.commit()
    return decision_id


def read(connection, run_id, stage=None) -> list:
    q, args = "SELECT * FROM decisions WHERE run_id = ?", [run_id]
    if stage:
        q, args = q + " AND stage = ?", args + [stage]
    cur = connection.execute(q + " ORDER BY created_at, rowid", args)
    names = [c[0] for c in cur.description]
    return [dict(zip(names, r)) for r in cur.fetchall()]
