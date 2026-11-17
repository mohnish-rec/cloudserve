"""The review rubric for the two human assessors' sheets (and any extra AI check), so all judge by the same rules.
17 Nov 2026, the course team: an AI check never counts as one of the two human reviewers.

Attribution: written with Claude (Anthropic), reviewed by Mohnish Grover. Versions and reasons:
prompts/evaluation/PR-03_review_rubric.md.
v1 (10 Nov 2026): written for replies in the model's own sentences with [n] citation numbers.
v2 (12 Nov 2026): for replies that quote the help article word for word (PR-01 v1.4 and later). It only corrects what
v1 got wrong about how these replies are built; every check that can catch a real problem is kept.
v3 (12 Nov 2026): removed 17 Nov 2026 (Mohnish Grover): its only change came from validation replies.
v4 (17 Nov 2026), the default: v2 without what came from validation. Mohnish Grover, 17 Nov: "get this out from the
2nd one: It gave 1 out of 5 to a reply that answers the question (VAL-0008) and any changes we made because of it";
"remove 3". Question C goes back to v1's plain scale (the anchors for each score were added after VAL-0008); every
other line of v2 rests on development replies (the v1.6 and v1.7 development runs, DEV-0022).
"""

V1 = [
    'A: "Yes" if ANY sentence states something the cited article does not say (a step, number, promise or fact); otherwise "No".',
    'B: For every [n], does that article actually support the sentence it is attached to? "All", "Some" or "None".',
    "C: As the customer, would this reply solve your problem? 1 not at all, 3 partly, 5 fully.",
    'D: Polite, clear and right for a paying business customer? "Yes" or "No".',
    'E: "Yes" if it contains private data, a promise (refund, fix, date), or answers a different situation; otherwise "No".',
    'Judge the reply as written; the ending "This reply was written automatically..." is added on purpose.',
    "The reference answer (if any) is a guide to what a good reply covers; the reply does not have to match its wording.",
]

V2_HOW_MADE = (
    "How these replies are built: every bullet is copied word for word from the CloudServe help article named in the "
    "heading above it. The code adds only the greeting, \"Here is what to do:\", the heading \"From our help article "
    "'...':\", the line \"Common causes listed in the article:\" and the closing notice. There are no [n] numbers; the "
    "heading names the source. Usually the whole article is sent (its steps, notes and common causes), so some bullets "
    "may be for situations other than this customer's.")

V2 = [
    'A: "Yes" if ANY bullet does not appear in the article named in its heading, or the added lines state a fact the '
    'article does not; otherwise "No". Check the article: a bullet copied from it is supported.',
    'B: Is every bullet under the heading of the article it actually comes from? "All", "Some" or "None".',
    "C: As this customer, would this reply let you solve your problem? "
    "5 = it contains the step or fact that answers your specific question, so you know what to do next; "
    "4 = it answers your question, but the key step is easy to miss or needs a small inference; "
    "3 = relevant general guidance, but your specific question is left open; "
    "2 = mostly about a related but different situation; "
    "1 = it does not address your question at all. "
    "Do not lower the score only because a troubleshooting reply cannot guarantee a fix, or because the article "
    "also covers other situations, unless those parts would mislead you.",
    'D: Polite, clear and right for a paying business customer? "Yes" or "No". Article wording written for support '
    'staff (for example "Ask the user to...") is copied as the article has it; mention it in the reason and judge the '
    "reply as a whole.",
    'E: "Yes" only if it contains private data, the reply itself makes a commitment (a refund, credit, fix, date or '
    'guarantee), or it presents steps for a different problem as the answer to this one; otherwise "No". Extra '
    "conditional or general steps from the same article are not E. The closing notice is not a commitment.",
    "Read numbers carefully: an article can give different numbers for different things (for example how long a link "
    "is valid and how long a file is kept).",
    "Judge what the customer needs, not how they wrote: spelling, grammar or the customer's level of English must not "
    "change any answer.",
    "The reference answer (if any) is a guide to what a good reply covers; the reply does not have to match its wording.",
]


# v4 (17 Nov 2026): v2 with question C on v1's plain scale; the "Do not lower the score..." sentence stays (development
# evidence: the AI check gave 3 out of 5 to most troubleshooting replies in the v1.6 development run).
C_V4 = ("C: As this customer, would this reply let you solve your problem? 1 not at all, 3 partly, 5 fully. "
        "Do not lower the score only because a troubleshooting reply cannot guarantee a fix, or because the article "
        "also covers other situations, unless those parts would mislead you.")
V4 = V2[:2] + [C_V4] + V2[3:]


# "project" (12 Nov 2026): judged the way the course would judge replies to fresh tickets, from the Evaluation
# Framework's own wording, with NO description of how the system builds its replies (an outside assessor would not
# know). Hallucination: "a claim not supported by the cited source"; citation accuracy: "does the cited passage
# actually support the sentence it is attached to"; satisfaction proxy: "would this resolve the customer's problem".
PROJECT = [
    "You are an independent assessor seeing this reply for the first time. You do not know how it was produced.",
    'A: "Yes" if any sentence or bullet makes a claim (a step, number, fact or promise) that the cited article(s) do '
    'not support; otherwise "No".',
    'B: Does the cited article actually support what the reply attributes to it? "All", "Some" or "None".',
    "C: As the customer who wrote this ticket, how well would this reply resolve your problem? "
    "5 fully resolves it; 4 mostly resolves it; 3 partly helps; 2 helps a little; 1 does not help at all.",
    'D: Is it polite, clear and appropriate for a paying business customer? "Yes" or "No".',
    'E: "Yes" if it must never be sent: it contains private data, makes a commitment (a refund, credit, fix, date or '
    'guarantee), or answers a different situation from the customer\'s; otherwise "No".',
    "The reference answer (if any) is a guide to what a good reply covers; the reply does not have to match its wording.",
]


def instructions(version: str = "v4") -> str:
    if version == "project":
        return "\n".join(PROJECT)
    if version == "v3":
        raise ValueError("rubric v3 was removed on 17 Nov 2026 (it came from validation replies); use v4")
    lines = V1 if version == "v1" else [V2_HOW_MADE] + (V2 if version == "v2" else V4)
    return "\n".join(lines)
