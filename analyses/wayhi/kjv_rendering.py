"""How the KJV rendered each kind of *wayhi*, and whether the English rule agrees.

Question: when the Hebrew has a setting-first *wayhi*, an ordinary-verb
*wayhi*, or the future *wehayah*, how often does the KJV say "it came / shall
come to pass"? How often does the KJV say it with no such form in the verse?
And when the English rule sorts a KJV verse into setting-first or
straight-to-the-event, does it agree with the Hebrew?

Why: two things depend on this. First, the claim that the KJV translators
varied the phrase freely: if they did, counting the KJV's English would
undercount the construction, which is why the Hebrew is counted instead.
Second, the Book of Mormon side can only be bucketed by an English rule. Its
error rate has to be measured on text whose true bucket is known.

Method: verses with exactly one *wayhi* or *wehayah* (so the English phrase
can only render that form). The KJV verse is classified with both English
rules. Verse numbers are matched directly, and Hebrew/English versification
differences show up as unmatched.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from bomstylo import corpus, english, hebrew
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="kjv-rendering",
    family="wayhi",
    title="KJV rendering of each Hebrew bucket, and calibration of the English rule",
    question="How consistently did the KJV render each kind of wayhi/wehayah as 'came to pass', and "
             "how often does the English rule recover the Hebrew bucket?",
    why="Tests the 'translators varied it' premise, and measures the English rule's error rate on "
        "text whose bucket is known.",
    label="exploratory",
    corpora=["wlc", "kjv"],
)


def run() -> dict:
    heb = hebrew.instances()
    kjv = {(v.book, v.chapter, v.verse): v.text for v in corpus.load("kjv_ot")}
    per_v = Counter((h["book"], h["ch"], h["vs"]) for h in heb)
    cal = {r: defaultdict(Counter) for r in english.RULES}
    unmatched = 0
    for h in heb:
        key = (h["book"], h["ch"], h["vs"])
        if per_v[key] != 1:
            continue
        if key not in kjv:
            unmatched += 1
            continue
        for r in cal:
            c = english.counts(kjv[key], r)
            p = [k for k in c if k.startswith(h["tense"])]
            if not p:
                cal[r][(h["tense"], h["bucket"])]["not rendered"] += 1
            for k in p:
                cal[r][(h["tense"], h["bucket"])]["English says " + k.split("_")[1]] += c[k]
    has = defaultdict(set)
    for h in heb:
        has[(h["book"], h["ch"], h["vs"])].add(h["tense"])
    orphan, total = Counter(), Counter()
    orphan_refs = defaultdict(list)
    for key, t in kjv.items():
        c = english.counts(t)
        for tense in ("past", "future"):
            n = c[f"{tense}_time"] + c[f"{tense}_event"]
            total[tense] += n
            if n and tense not in has[key]:
                orphan[tense] += n
                orphan_refs[tense].append(f"{key[0]} {key[1]}:{key[2]}")
    table = {}
    for (tense, bucket), c in cal["revised"].items():
        n = sum(v for k, v in c.items() if k != "not rendered") + c["not rendered"]
        verses = sum(1 for h in heb if (h["tense"], h["bucket"]) == (tense, bucket)
                     and per_v[(h["book"], h["ch"], h["vs"])] == 1 and (h["book"], h["ch"], h["vs"]) in kjv)
        rendered = verses - c["not rendered"]
        table[f"{tense}|{bucket}"] = {"verses": verses, "rendered": rendered,
                                      "share": rendered / verses if verses else None}
    # Agreement on Hebrew settings that the KJV rendered with the phrase.
    agree = {r: {t: [cal[r][(t, "time")]["English says time"],
                     sum(cal[r][(t, "time")][f"English says {x}"] for x in ("time", "event"))]
                 for t in ("past", "future")} for r in english.RULES}
    return {"calibration": {r: {f"{a}|{b}": dict(c) for (a, b), c in cc.items()} for r, cc in cal.items()},
            "rendering": table, "rule_agreement_on_settings": agree, "unmatched_verses": unmatched,
            "kjv_orphans": dict(orphan), "kjv_orphan_refs": dict(orphan_refs), "kjv_totals": dict(total)}


def headline(d: dict) -> list[Headline]:
    t = d["rendering"]
    ok, n = d["rule_agreement_on_settings"]["revised"]["past"]
    rok, rn = d["rule_agreement_on_settings"]["registered"]["past"]
    fok, fn = d["rule_agreement_on_settings"]["revised"]["future"]
    o, tot = d["kjv_orphans"].get("past", 0), d["kjv_totals"]["past"]
    return [
        Headline("rendered_setting", t["past|time"]["share"],
                 text=f"The KJV renders {t['past|time']['share']:.0%} of setting-first wayhi as 'came to pass' "
                      f"({t['past|time']['rendered']} of {t['past|time']['verses']} single-form verses); "
                      f"ordinary-verb wayhi {t['past|verb']['share']:.1%}; future setting-first wehayah "
                      f"{t['future|time']['share']:.0%}."),
        Headline("kjv_additions", o,
                 text=f"KJV past 'it came to pass' with no wayhi in the verse: {o} of {tot} ({o / tot:.0%})."),
        Headline("rule_agreement", ok / n,
                 text=f"English rule (revised) agrees with the Hebrew on {ok} of {n} rendered past settings "
                      f"(registered rule {rok} of {rn}); future settings {fok} of {fn}."),
    ]
