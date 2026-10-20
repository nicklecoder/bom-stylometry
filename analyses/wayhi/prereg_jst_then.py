"""PREREGISTRATION_30: is "it came to pass that" Joseph Smith's all-purpose "then"?

Registered test, run as written with Amendment 1 (the headnote fix). The JST
is aligned with the KJV book by book (`bomstylo.jst`); every JST formula is
retained or added, and event-first or time-first by PREREG 2's English rule.

Decision rule on the primary panel (OT narrative), S = event share of added
formulas: fewer than 30 added → R0 underpowered; S ≥ 0.56 → R1 the habit
transfers; S ≤ 0.35 → R2 it doesn't; otherwise R3 undecided.

Also computed, as the pre-registration's own post-run checks record them
(neither changes the verdict):
- Amendment 2.1: five "added" formulas are KJV formulas from the start of the
  next book that spill over before its first running head; S without them.
- The robustness note: S under other headnote limits.

Reading (Amendment 3): R1 shows Smith had the event-first idiom by 1830, in
new narrative with no source behind it. Every Smith narrative postdates the
Book of Mormon dictation, so carryover from it can't be ruled out.
"""
from __future__ import annotations

from bomstylo import jst, stats
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="prereg-jst-then",
    family="wayhi",
    title="Pre-registered: is 'it came to pass' Smith's all-purpose 'then'? (PREREG 30, JST)",
    question="When Joseph Smith added 'it came to pass' to the KJV in the JST, was it event-first at the "
             "Book of Mormon's share?",
    why="Tests the main competitor to a non-English source: Smith's own English, in his later scripture.",
    label="registered",
    preregistration="PREREGISTRATION_30.md",
    corpora=["jst-1867", "kjv"],
    params={"B": 0.71, "thresholds": [0.35, 0.56], "min_added": 30, "headnote_lines": jst.HEADNOTE_LINES,
            "robustness_headnote_lines": [2, 3, 6, 8]},
)

# Amendment 2.1: KJV formulas of the next book's opening, counted as "added" to
# the book before. (book they fall in, start of the formula text)
BOUNDARY_SPILL = [
    ("Genesis", "it came to pass, because the midwives feared God"),        # Exodus 1:21
    ("Judges", "it came to pass in the days when the judges ruled"),         # Ruth 1:1
    ("Judges", "it came to pass, when they were come to Beth-lehem"),        # Ruth 1:19
    ("Nehemiah", "it came to pass in the days of Ahasuerus"),                # Esther 1:1
    ("Nehemiah", "it came to pass, when the king's commandment"),            # Esther 9:1
]


def panels(res: dict, exclude=()) -> dict:
    out = {}
    for label, books in (("primary (OT narrative)", jst.PRIMARY), ("secondary (NT narrative)", jst.SECONDARY)):
        books = [b for b in books if b in res]
        words = sum(res[b]["jst_words"] for b in books)
        blk = {}
        for name, kw in (("added", dict(status="added")), ("retained", dict(status="retained")),
                         ("added, new composition", dict(status="added", context="new composition")),
                         ("added, revision", dict(status="added", context="revision"))):
            c = jst.tally(books, res, **kw)
            for b, prefix in exclude:
                if b in books:
                    for f in res[b]["formulas"]:
                        if f["text"].startswith(prefix) and all(f[k] == v for k, v in kw.items()):
                            c[f["kind"]] -= 1
            n = c["event"] + c["time"]
            s = stats.share_ci(c["event"], n)
            blk[name] = {"event": c["event"], "time": c["time"], "n": n, "share": s}
        blk["added_per_1k_jst_words"] = 1000 * blk["added"]["n"] / words
        blk["jst_words"] = words
        out[label] = blk
    return out


def decide(P: dict) -> tuple[str, bool]:
    S, lo, hi = P["share"]
    lo_t, hi_t = ANALYSIS.params["thresholds"]
    if P["n"] < ANALYSIS.params["min_added"]:
        v = "R0 UNDERPOWERED: fewer than 30 added formulas; no verdict from S"
    elif S >= hi_t:
        v = "R1 HABIT TRANSFERS: H_then is a sufficient explanation of the event-first share"
    elif S <= lo_t:
        v = "R2 HABIT DOES NOT TRANSFER: H_then, as Smith's general narrative habit, not supported"
    else:
        v = "R3 UNDECIDED"
    straddle = S is not None and P["n"] >= 30 and any(lo < t < hi for t in (lo_t, hi_t))
    return v, straddle


def run() -> dict:
    res = jst.run("registered")
    out = panels(res)
    verdict, straddle = decide(out["primary (OT narrative)"]["added"])
    found = [(b, p) for b, p in BOUNDARY_SPILL
             if any(f["status"] == "added" and f["text"].startswith(p) for f in res[b]["formulas"])]
    if len(found) != len(BOUNDARY_SPILL):
        raise ValueError(f"boundary spill-over formulas not all found: {sorted(set(BOUNDARY_SPILL) - set(found))}")
    corrected = panels(res, BOUNDARY_SPILL)
    robust = {}
    for k in ANALYSIS.params["robustness_headnote_lines"]:
        P = panels(jst.run("registered", headnote_lines=k))["primary (OT narrative)"]["added"]
        robust[str(k)] = {"added": P["n"], "S": P["share"][0], "verdict": decide(P)[0][:2]}
    return {"books": {b: {k: v for k, v in r.items() if k != "formulas"} for b, r in res.items()},
            "panels": out, "verdict": verdict, "interval_straddles": straddle,
            "amendment2_boundary_corrected": corrected,
            "amendment2_verdict": decide(corrected["primary (OT narrative)"]["added"])[0],
            "robustness_headnote_lines": robust,
            "added_examples": {b: [f for f in res[b]["formulas"] if f["status"] == "added"][:15] for b in res},
            "all_formulas": {b: r["formulas"] for b, r in res.items()}}


def headline(d: dict) -> list[Headline]:
    P = d["panels"]["primary (OT narrative)"]["added"]
    C = d["amendment2_boundary_corrected"]["primary (OT narrative)"]["added"]
    return [
        Headline("S_registered", P["share"][0], P["share"][1], P["share"][2],
                 text=f"PREREG 30 (registered): {P['n']} added formulas in JST OT narrative, {P['event']} event-first, "
                      f"S = {P['share'][0]:.2f} ({P['share'][1]:.2f}–{P['share'][2]:.2f}). Verdict: {d['verdict'][:2]}, "
                      f"the habit transfers."),
        Headline("S_boundary_corrected", C["share"][0], C["share"][1], C["share"][2],
                 text=f"Without the five boundary spill-overs (Amendment 2): {C['n']} added, {C['event']} event-first, "
                      f"S = {C['share'][0]:.2f} ({C['share'][1]:.2f}–{C['share'][2]:.2f}); verdict unchanged. "
                      f"Shows the idiom was Smith's by 1830; whether he had it before the Book of Mormon is untested."),
    ]
