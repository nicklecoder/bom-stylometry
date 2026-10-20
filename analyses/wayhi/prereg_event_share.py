"""PREREGISTRATION_2: does the narrative particle lead into an event or a time?

Registered test, run exactly as written (with its Amendments 1–2). Nothing here
may change to move the result; a change is an amendment in the
pre-registration file, which is fingerprinted with this analysis.

E = Egyptian pooled event share (old particles ꜥḥꜥ.n, wn.ꞽn in the 17 named
texts, those of at least 500 tokens); H = Hebrew *wayhi* (17 units); B = the
Book of Mormon narrative frame. Decision rule:
- R0: the feature separates Hebrew from Egyptian only if |E − H| ≥ 0.30;
- R1: E ≥ 0.50;
- R2, match: |B − E| ≤ 0.15, otherwise a miss;
- R3, discrimination: the KJV Old Testament and The Late War must each be more
  than 0.15 from B (n ≥ 30).

The registered English rule is `english.registered_counts` (text after the
formula only). Later exploratory re-measurements under the revised rule are in
event-shares and bom-buckets; they don't change this verdict.

Frame: as registered, Zeniff's record (embedded kind "narration") counts as
narrative frame here, as in bom-buckets.
"""
from __future__ import annotations

import re
from collections import Counter

from bomstylo import controls, corpus, egyptian as E, english, genre, hebrew, spans
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="prereg-event-share",
    family="wayhi",
    title="Pre-registered: what the narrative particle introduces (PREREG 2)",
    question="Does the Book of Mormon's event/time split of 'it came to pass' match the Egyptian "
             "narrative particles (within 0.15), and do English controls fail to?",
    why="The registered test of the 'Egyptian particle' reading of the event-first share.",
    label="registered",
    preregistration="PREREGISTRATION_2.md",
    corpora=["aed-tei", "wlc", "bom-current", "kjv", "late-war"],
    annotations=["embedded.tsv", "records.tsv"],
    params={"min_tokens": E.MIN_TOKENS},
)

# Egyptian rule (PREREG 2, Amendment 1): what follows the marker in its <s>.
TEMPORAL_PREPS = {"65300", "851455", "851453", "116761"}
SIMPLE_PREPS = {"64360", "107520", "91900", "78870"}
TIME_NOUNS = {"99060", "94920", "850581", "93", "178000", "167920", "172700",
              "96390", "5", "80840", "40480", "854543"}
_S = re.compile(r"<s\b[^>]*>(.*?)</s>", re.S)
_EW = re.compile(r'<w [^>]*lemmaRef="tla:tla(\w+)"[^>]*>\s*<fs feats="([^"]*)"', re.S)


def egyptian_classify(nxt: list[tuple[str, str]]) -> str:
    if not nxt:
        return "other"
    for i, (lid, _) in enumerate(nxt[:2]):
        if lid in TEMPORAL_PREPS:
            return "time"
        if lid in SIMPLE_PREPS and i + 1 < len(nxt) and nxt[i + 1][0] in TIME_NOUNS:
            return "time"
    head = nxt[0][1].split()[0] if nxt[0][1] else ""
    return "event" if head in ("verb", "substantive", "pronoun", "particle") else "other"


def egyptian() -> dict:
    out = {}
    for tid, title, period, *_ in E.NAMED_TEXTS:
        c, n = Counter(), 0
        for s in _S.findall(E.aed(tid)):
            toks = _EW.findall(s)
            n += len(toks)
            for i, (lid, _) in enumerate(toks):
                if lid in E.MARKERS:
                    c[egyptian_classify(toks[i + 1:])] += 1
        out[title] = {"period": period, "tokens": n, **c}
    return out


def share(c: dict) -> float | None:
    e, t = c.get("event", 0), c.get("time", 0)
    return e / (e + t) if e + t else None


def run() -> dict:
    eg = egyptian()
    pooled = Counter()
    for r in eg.values():
        if r["tokens"] >= E.MIN_TOKENS:
            pooled.update({k: r.get(k, 0) for k in ("event", "time", "other")})
    Es = share(pooled)

    unit_of = genre.unit_of_chapter()
    whole, named = Counter(), Counter()
    for h in hebrew.instances():
        if h["prereg2"] is None:
            continue
        whole[h["prereg2"]] += 1
        if (h["book"], h["ch"]) in unit_of:
            named[h["prereg2"]] += 1
    hb = {"whole Hebrew Bible": dict(whole), "17 narrative units": dict(named)}
    H = share(hb["17 narrative units"])

    bom = corpus.load("bom")
    att = spans.attribution(bom)
    frame = [v for v in bom if v.kind == "verse" and att.kind_at(v.index) in (None, "narration")]
    Bc = english.registered_counts(" ".join(v.text for v in frame))
    B = share(Bc)
    by_narrator = {rec: english.registered_counts(" ".join(v.text for v in frame if att.record_at(v.index) == rec))
                   for rec in ("Nephi1", "Mormon", "Moroni")}
    ctrl = {"KJV Old Testament": english.registered_counts(" ".join(v.text for v in corpus.load("kjv_ot"))),
            "KJV New Testament": english.registered_counts(" ".join(v.text for v in corpus.load("kjv_nt"))),
            "The Late War (1819)": english.registered_counts(" ".join(controls.late_war()))}

    verdict = {"R0 boundary |E-H| >= 0.30": abs(Es - H) >= 0.30, "R1 E >= 0.50": Es >= 0.50,
               "R2 |B-E| <= 0.15": abs(B - Es) <= 0.15}
    r3 = {}
    for k in ("KJV Old Testament", "The Late War (1819)"):
        if sum(ctrl[k].values()) < 30:
            r3[k] = "underpowered"
        else:
            r3[k] = "separate" if abs(share(ctrl[k]) - B) > 0.15 else "within 0.15 of B"
    verdict["R3 controls"] = r3
    if not verdict["R0 boundary |E-H| >= 0.30"]:
        overall = "NO INFORMATION: feature does not separate Hebrew from Egyptian"
    elif not verdict["R1 E >= 0.50"]:
        overall = "FAIL: Egyptian particles do not mainly lead into events"
    elif not verdict["R2 |B-E| <= 0.15"]:
        overall = "MISS: the book does not match the Egyptian proportion"
    elif any(v == "within 0.15 of B" for v in r3.values()):
        overall = "MATCH, BUT NOT DISCRIMINATING: an English control does the same"
    elif any(v == "underpowered" for v in r3.values()):
        overall = "MATCH; discrimination untested (underpowered control)"
    else:
        overall = "PASS on all four rules"
    return {"egyptian": eg, "egyptian_pooled": dict(pooled), "E": Es, "hebrew": hb, "H": H,
            "bom_frame": Bc, "B": B, "bom_by_narrator": by_narrator, "controls": ctrl,
            "verdict": {**verdict, "overall": overall}}


def headline(d: dict) -> list[Headline]:
    gap = abs(d["B"] - d["E"])
    return [Headline("gap", gap,
                     text=f"PREREG 2 (registered): Egyptian particles {d['E']:.2f} event-first, Book of Mormon frame "
                          f"{d['B']:.2f}; gap {gap:.2f} > 0.15. Verdict: {d['verdict']['overall']}")]
