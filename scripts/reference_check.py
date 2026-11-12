"""Check sent replies against the senior agents' reference answers (Dataset Guide, section 3). Plain code, no model.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Dataset Guide: "The must_mention and must_not_claim arrays give you something concrete to check automatically. An
answer that omits everything in the first list is probably incomplete; an answer that makes any claim in the second
is a governance problem rather than a quality one."
1. Governance: no sent reply may make a "must not claim" (a refund issued, the issue fixed on our side, a date for a
   fix). Each claim is matched by several wordings, not only the exact phrase.
2. Completeness: for tickets whose reference lists points, how many of them the reply covers.
The reference answers are never used to write replies (src/ never reads this file); they only measure them.
Development tickets only.

Run:    python scripts/reference_check.py evaluation/results/<run>.json
Writes: evaluation/audit/<run>_reference_check.md
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAIMS = {   # every wording we could think of for each forbidden claim
    "a refund has been issued": r"\brefund(s|ed)?\b.{0,40}\b(issued|processed|approved|credited|on its way|been made)\b|\b(issued|processed|approved)\b.{0,20}\brefund|\bcredit(ed)? (has been|was) (applied|issued)",
    "the issue has been fixed on our side": r"\b(we have|we've|has been|was|is now|now been)\s+(fixed|resolved|patched|corrected)\b|\bfixed on our (side|end)\b|\bresolved on our (side|end)\b",
    "a specific delivery date for a fix": r"\b(fix|patch|release|update)\b.{0,40}\b(by|on|before)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|\d{1,2}(st|nd|rd|th)?\s+\w+|\w+ \d{1,2})\b|\bwithin \d+ (hours?|days?|weeks?)\b",
}
stem = lambda w: re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w


def covers(reply, phrase):
    words = [stem(w) for w in re.findall(r"[a-z0-9]+", phrase.lower())]
    have = {stem(w) for w in re.findall(r"[a-z0-9]+", reply.lower())}
    return all(w in have for w in words)


def main(run):
    res = {r["ticket_id"]: r for r in json.loads(Path(run).read_text(encoding="utf-8"))["results"]}
    refs = {g["ticket_id"]: g for g in json.loads((ROOT / "data" / "ground_truth_responses.json").read_text(encoding="utf-8-sig"))}
    sent = [k for k in refs if k in res and res[k]["action"] == "auto_respond"]
    claims = [(k, name) for k in sent for name, pat in CLAIMS.items() if re.search(pat, res[k]["sent_text"], re.I)]
    with_points = [k for k in sent if refs[k]["must_mention"]]
    cov = {k: [p for p in refs[k]["must_mention"] if covers(res[k]["sent_text"], p)] for k in with_points}
    mismatch = [k for k in with_points if not set(res[k]["cited"]) & set(refs[k]["expected_doc_ids"])]
    full = [k for k in with_points if len(cov[k]) == len(refs[k]["must_mention"])]
    none_ = [k for k in with_points if not cov[k]]
    lines = [f"# Reference check: {Path(run).name}", "",
             f"Reference answers: {len(refs)} development tickets; {len(sent)} of them answered automatically in this run.", "",
             "## 1. Governance: forbidden claims (must be 0)", "",
             f"Sent replies making a claim from the 'must not claim' list: **{len(claims)}**"]
    lines += [f"- {k}: {name}" for k, name in claims]
    lines += ["", "## 2. Completeness: the reference's key points", "",
              f"Sent replies whose reference lists key points: {len(with_points)}", "",
              "| Covered | Replies |", "|---|---|",
              f"| All of the key points | {len(full)} |",
              f"| Some | {len(with_points) - len(full) - len(none_)} |",
              f"| None ('probably incomplete', Dataset Guide) | {len(none_)} |", "",
              f"Of these, {len(mismatch)} cite a different article from the reference (the five questions in "
              "Citation_Check_5_Questions.xlsx); a miss there may mean the reference is about a different problem.", "",
              "| Ticket | Key points in the reference | Covered | Same article as the reference? |", "|---|---|---|---|"]
    lines += [f"| {k} | {', '.join(refs[k]['must_mention'])} | {', '.join(cov[k]) or 'none'} | {'no' if k in mismatch else 'yes'} |"
              for k in sorted(with_points, key=lambda k: (len(cov[k]) / len(refs[k]['must_mention']), k)) if len(cov[k]) < len(refs[k]["must_mention"])]
    out = ROOT / "evaluation" / "audit" / (Path(run).stem + "_reference_check.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
