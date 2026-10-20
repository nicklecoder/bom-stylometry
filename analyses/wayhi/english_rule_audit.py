"""The English rule against a hand reading of 120 Book of Mormon cases.

Question: on the Book of Mormon itself, how often does the English rule's
setting-first / straight-to-the-event call agree with a careful human reading?

Why: kjv-rendering checks the rule on KJV English, whose true bucket is known
from the Hebrew. But the Book of Mormon's sentences are its own. A rule tuned
on the KJV could misread them, for example its long run-on settings, or
settings placed before the formula.

Method: 120 narrative-frame instances drawn at random (seed 20261018) from the
current text were read in context and labelled by hand. The labels are in
`annotations/wayhi_audit_bom.tsv`, column `hand`. The rule is re-applied to
the stored context (the clause before the formula and the 40 characters after
it) under both rule versions, and compared with the hand label.
"""
from __future__ import annotations

import csv
from collections import Counter

from bomstylo import english, paths, stats
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="english-rule-audit",
    family="wayhi",
    title="English rule vs hand labels, 120 Book of Mormon cases",
    question="How often does the English rule agree with a hand reading of Book of Mormon instances?",
    why="Measures the rule's error on the text it is used to classify, not only on the KJV.",
    label="exploratory",
    annotations=["wayhi_audit_bom.tsv"],
    params={"sample_seed": 20261018, "sample_size": 120},
)


def run() -> dict:
    with (paths.ANNOTATIONS / "wayhi_audit_bom.tsv").open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh, delimiter="\t") if r["hand"] in ("time", "event")]
    out = {"n": len(rows), "hand": dict(Counter(r["hand"] for r in rows))}
    for rule in english.RULES:
        c = Counter((english.classify(r["follows"], False, r["before"], rule), r["hand"]) for r in rows)
        agree = c[("time", "time")] + c[("event", "event")]
        out[rule] = {"confusion": {f"rule {a} | hand {b}": n for (a, b), n in sorted(c.items())},
                     "agree": agree, "share": stats.share_ci(agree, len(rows)),
                     "disagreements": [r["ref"] for r in rows
                                       if english.classify(r["follows"], False, r["before"], rule) != r["hand"]]}
    return out


def headline(d: dict) -> list[Headline]:
    r, g = d["revised"], d["registered"]
    return [Headline("agreement_revised", r["share"][0], r["share"][1], r["share"][2],
                     text=f"English rule vs hand labels on {d['n']} Book of Mormon cases: revised rule agrees on "
                          f"{r['agree']} ({r['share'][1]:.0%}-{r['share'][2]:.0%}), registered rule on {g['agree']}. "
                          f"Disagreements (revised): {', '.join(r['disagreements']) or 'none'}.")]
