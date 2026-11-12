"""After a run: re-check every problem found in earlier runs, and compare with an earlier run. Plain code, no model.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Problems checked (each found on the 500 development tickets, 10-11 Nov 2026):
  1. Replies too short: how many Resolution steps of each cited article reached the customer.
  2. Rollback replies leaving out "If the release included a database migration..." (14 in the v1.4 run).
  3. Word for word: every bullet must be an exact copy of a span of its article (a closing full stop aside).
  4. Replies blocked for length (the 230-word rule), and blocks and handovers overall.
  5. Wording written for a support agent copied into a customer reply ("Ask the user ...").
  6. DEV-0209 (restore, Asia-Pacific): blocked in v1.4 because connection-pool steps were mixed in.
  7. Zero tolerance: tickets the labels say must not be answered automatically that were, and private data checks.
Run:    python scripts/check_run.py evaluation/results/<new>.json [evaluation/results/<earlier>.json] [--tickets validation_tickets.json]
Writes: evaluation/results/<new>_check.md
"""
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# 11 Nov: --tickets <file> for another ticket file (e.g. validation_tickets.json); default development
_TF = sys.argv[sys.argv.index("--tickets") + 1] if "--tickets" in sys.argv else "development_tickets.json"
T = {t["ticket_id"]: t for t in json.loads((ROOT / "data" / _TF).read_text(encoding="utf-8-sig"))}
DOCS = {d["doc_id"]: d for d in json.loads((ROOT / "data/documentation.json").read_text(encoding="utf-8-sig"))}
flat = lambda s: " ".join(s.split())
MIGRATION = "If the release included a database migration"


def steps(doc_id):
    m = re.search(r"## Resolution\n(.*?)(\n## |\Z)", DOCS[doc_id]["content"], re.S)
    return [flat(s) for s in re.findall(r"^\s*\d+\.\s+(.*)$", m.group(1) if m else "", re.M)]


def bullets(text):
    return [flat(l[2:].split(" (also in:")[0]) for l in (text or "").splitlines() if l.startswith("- ")]


def summary(path):
    R = json.loads(Path(path).read_text(encoding="utf-8"))["results"]
    sent = [r for r in R if r["action"] == "auto_respond"]
    out = {"n": len(R), "sent": len(sent), "actions": Counter(r["action"] for r in R)}
    cover, one_step, mig_missing, mig_total, not_exact, agent = [], [], [], 0, [], []
    for r in sent:
        text = flat(r["sent_text"] or "")
        for d in r["cited"] or []:
            st = steps(d)
            got = sum(s in text for s in st)
            cover.append(got / len(st) if st else 1)
            if d == "DOC-DEPLOY-002":
                mig_total += 1
                if MIGRATION not in text:
                    mig_missing.append(r["ticket_id"])
        b = bullets(r["sent_text"])
        if len(b) <= 1:
            one_step.append(r["ticket_id"])
        arts = " ".join(flat(DOCS[d]["content"]) for d in (r["cited"] or []) if d in DOCS)
        # Common causes are list items without a full stop in the article; the reply ends them with one. Words unchanged.
        if any(x.rstrip(".") not in arts for x in b):
            not_exact.append(r["ticket_id"])
        if re.search(r"\b(ask the (user|customer)|the customer should|tell the customer)\b", text, re.I):
            agent.append(r["ticket_id"])
    words = [len(" ".join(bullets(r["sent_text"])).split()) for r in sent]
    long_blocks = [r["ticket_id"] for r in R if "too long" in json.dumps(r.get("guardrails", {}))]
    refund_blocks = [r["ticket_id"] for r in R if "refund or credit" in json.dumps(r.get("guardrails", {}))]
    must_not = [r["ticket_id"] for r in sent if T[r["ticket_id"]]["labels"].get("must_not_auto_respond")]
    priv = [r["ticket_id"] for r in R if str(r.get("guardrails", {}).get("private_data", "pass")).startswith("block")]
    out.update(cover=sum(cover) / len(cover) if cover else 0, full=sum(c == 1 for c in cover), cited=len(cover),
               one_step=one_step, mig_missing=mig_missing, mig_total=mig_total, not_exact=not_exact, agent=agent,
               words=(min(words), sum(words) / len(words), max(words)) if words else (0, 0, 0),
               long_blocks=long_blocks, refund_blocks=refund_blocks, must_not=must_not, priv=priv,
               dev0209=next((r["action"] for r in R if r["ticket_id"] == "DEV-0209"), "not in run"))
    return out


def main(new, old=None):
    a = summary(new)
    b = summary(old) if old else None
    col = lambda f: (f(a), f(b) if b else "")
    rows = [
        ("Automatic replies (FCR proxy)", lambda s: f"{s['sent']}/{s['n']} = {100*s['sent']/s['n']:.1f}%"),
        ("Decisions", lambda s: ", ".join(f"{k} {v}" for k, v in sorted(s["actions"].items()))),
        ("1. Share of each cited article's Resolution steps sent", lambda s: f"{100*s['cover']:.1f}%"),
        ("1. Cited articles with ALL their steps sent", lambda s: f"{s['full']}/{s['cited']}"),
        ("1. Replies with only one step", lambda s: str(len(s["one_step"]))),
        ("1. Words in the steps (fewest / average / most)", lambda s: "%d / %.0f / %d" % s["words"]),
        ("2. Rollback replies missing the migration step", lambda s: f"{len(s['mig_missing'])} of {s['mig_total']}"),
        ("3. Replies with a bullet not copied exactly from its article", lambda s: str(len(s["not_exact"]))),
        ("4. Replies blocked for length", lambda s: str(len(s["long_blocks"]))),
        ("4. Replies blocked for refund wording (e.g. Ines's proration article)", lambda s: str(len(s["refund_blocks"]))),
        ("5. Replies with wording meant for a support agent", lambda s: str(len(s["agent"]))),
        ("6. DEV-0209 (restore, Asia-Pacific)", lambda s: s["dev0209"]),
        ("7. Must-not tickets answered automatically", lambda s: str(len(s["must_not"]))),
        ("7. Replies blocked by the private-data check", lambda s: str(len(s["priv"]))),
    ]
    L = [f"# Run check: {Path(new).name}" + (f" vs {Path(old).name}" if old else ""), "",
         "| Check | This run |" + (" Earlier run |" if old else ""), "|---|---|" + ("---|" if old else "")]
    for name, f in rows:
        x, y = col(f)
        L.append(f"| {name} | {x} |" + (f" {y} |" if old else ""))
    L += ["", "## Tickets to look at (this run)", "",
          f"- Rollback replies missing the migration step: {', '.join(a['mig_missing']) or 'none'}",
          f"- Bullets not copied exactly: {', '.join(a['not_exact']) or 'none'}",
          f"- Blocked for length: {', '.join(a['long_blocks']) or 'none'}",
          f"- Blocked for refund wording: {', '.join(a['refund_blocks']) or 'none'}",
          f"- Wording meant for a support agent: {', '.join(a['agent']) or 'none'}",
          f"- Only one step: {', '.join(a['one_step'][:40]) or 'none'}" + (" ..." if len(a['one_step']) > 40 else ""),
          f"- Must-not answered automatically: {', '.join(a['must_not']) or 'none'}"]
    out = Path(new).with_name(Path(new).stem + "_check.md")
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main(*[a for a in sys.argv[1:] if a != "--tickets" and a != _TF][:2])
