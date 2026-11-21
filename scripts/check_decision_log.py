"""Count what one run wrote to the decision log, to check it against that run's metrics report (README step 10).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
By default it checks the most recent run; give a run id (from the top of a metrics report) to check another.
Run: python scripts/check_decision_log.py            (the most recent run)
     python scripts/check_decision_log.py <run id>   (a particular run)
"""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "storage" / "decisions.db"
OUTCOME = {"auto_respond": "answered automatically", "escalate": "sent to a person", "block": "blocked by a guardrail"}


def main() -> int:
    if not DB.exists():
        print("No decision log yet: run step 6, then process some tickets (step 8 or 9).")
        return 1
    c = sqlite3.connect(DB)
    if len(sys.argv) > 1:
        run = sys.argv[1]
    else:
        row = c.execute("SELECT run_id FROM decisions ORDER BY created_at DESC LIMIT 1").fetchone()
        if not row:
            print("The decision log is empty: process some tickets first (step 8 or 9).")
            return 1
        run = row[0]
    rows = c.execute("SELECT COUNT(*) FROM decisions WHERE run_id = ?", (run,)).fetchone()[0]
    if not rows:
        print(f"No decisions found for run {run}.")
        return 1
    tickets = c.execute("SELECT COUNT(DISTINCT ticket_id) FROM decisions WHERE run_id = ?", (run,)).fetchone()[0]
    outcomes = c.execute("SELECT COUNT(*) FROM decisions WHERE run_id = ? AND stage = 'outcome'", (run,)).fetchone()[0]
    once = c.execute("SELECT COUNT(*) FROM (SELECT ticket_id FROM decisions WHERE run_id = ? AND stage = 'outcome' "
                     "GROUP BY ticket_id HAVING COUNT(*) = 1)", (run,)).fetchone()[0]
    print(f"Run: {run}")
    print(f"Rows written to the decision log: {rows}")
    print("By step:")
    for stage, n in c.execute("SELECT stage, COUNT(*) FROM decisions WHERE run_id = ? GROUP BY stage ORDER BY stage",
                              (run,)):
        print(f"  {stage:<15} {n}")
    print("Final outcomes:")
    for action, n in c.execute("SELECT action_taken, COUNT(*) FROM decisions WHERE run_id = ? AND stage = 'outcome' "
                               "GROUP BY action_taken ORDER BY action_taken", (run,)):
        print(f"  {OUTCOME.get(action, action):<25} {n}")
    ok = tickets == outcomes == once
    print(f"Tickets: {tickets}; final outcomes: {outcomes}; tickets with exactly one final outcome: {once}")
    print("Result: RECONCILES (every ticket has exactly one final outcome)" if ok else "Result: DOES NOT RECONCILE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
