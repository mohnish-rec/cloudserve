"""First tests (Setup Guide step 07).

They need no API key and no model download, so they behave the same on
this laptop and in GitHub Actions.
"""
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    with open(ROOT / "data" / name, encoding="utf-8") as f:
        return json.load(f)


def test_all_four_datasets_load():
    for name in ["development_tickets.json", "validation_tickets.json",
                 "ground_truth_responses.json", "documentation.json"]:
        assert load(name), f"{name} is empty"


def test_every_document_has_the_fields_the_vector_store_reads():
    docs = load("documentation.json")
    assert len(docs) == 29
    for doc in docs:
        assert doc["doc_id"] and doc["title"] and doc["content"] and doc["category"]


def test_env_example_lists_every_setting_and_holds_no_real_key():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "gsk_" not in text and "sk-or-" not in text  # Groq and OpenRouter key prefixes
    for name in ["LLM_BASE_URL", "LLM_API_KEY", "MODEL_NAME", "BACKUP_MODEL_NAME",
                 "EMBEDDING_MODEL", "CHROMA_PATH", "DATABASE_URL"]:
        assert f"{name}=" in text, f"{name} missing from .env.example"


def test_decision_log_setup_creates_the_table_and_is_repeatable(tmp_path):
    db = tmp_path / "decisions.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db.as_posix()}"}
    for _ in range(2):  # running twice must also succeed
        result = subprocess.run([sys.executable, "scripts/setup_decision_log.py"],
                                cwd=ROOT, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    connection = sqlite3.connect(db)
    columns = [row[1] for row in connection.execute("PRAGMA table_info(decisions)")]
    connection.close()
    assert len(columns) == 18
    assert {"decision_id", "run_id", "ticket_id", "action_taken", "reason", "provider"} <= set(columns)


def test_metrics_module_defines_the_guide_metrics():
    from src import metrics
    for name in ["TICKETS", "LATENCY", "GUARDRAIL", "CONFIDENCE"]:
        assert hasattr(metrics, name)