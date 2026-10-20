"""Every "and + *hayah*" form in the Hebrew Bible, counted separately.

Question: how many *wayhi* are there, how many of the look-alike forms, and how
many of each kind of *wayhi* by bucket?

Why: "*wayhi*" is usually spoken of as one word, but several forms of *hayah*
carry the conjunction, and they are easy to pool by accident:
- spelling and accent variants of *wayhi* itself (one morphology tag);
- its plural and feminine (*wayyihyu* "and they were", *wattehi*);
- *wehayah*, the future "and it shall come to pass";
- *wihi*, "and let it be", spelled exactly like *wayhi* without vowel points
  (ויהי);
- plain "and" + perfect, spelled exactly like *wehayah* (והיה).

A concordance search on unpointed consonants catches the look-alikes too. This
analysis counts each form by morphology and by consonants, so the published
figures (published-claims) can be traced to a counting rule.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from bomstylo import hebrew
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="hebrew-forms",
    family="wayhi",
    title="Forms of 'and + hayah' in the Hebrew Bible, and wayhi by bucket",
    question="How many wayhi, wehayah and look-alike forms are there, and how do wayhi and wehayah "
             "split into setting-first, straight-to-event and ordinary-verb uses?",
    why="Separates forms that are easy to pool by accident, which is where published counts diverge.",
    label="exploratory",
    corpora=["wlc"],
)

FORM_NAMES = {
    "HC/Vqw3ms": "wayhi (and it was / and it came to pass)",
    "HC/Vqw3mp": "wayyihyu (and they were)",
    "HC/Vqw3fs": "wattehi (and she/it [fem.] was)",
    "HC/Vqw2ms": "wattehi (and you were)",
    "HC/Vqw1cs": "wa'ehi (and I was)",
    "HC/Vqw3fp": "wattihyenah (and they [fem.] were)",
    "HC/Vqw1cp": "wanniheyeh (and we were)",
    "HC/Vqq3ms": "wehayah (and it shall be / shall come to pass)",
    "HC/Vqq3cp": "wehayu (and they shall be)",
    "HC/Vqq3fs": "wehayetah (and she/it shall be)",
    "HC/Vqj3ms": "wihi (and let it be; jussive)",
    "HC/Vqi3ms": "weyihyeh (and it will be; plain imperfect)",
}
_POINTS = re.compile(r"[֑-ׇ/]")


def run() -> dict:
    toks = []
    for book, ch, vs, ws in hebrew.verses():
        for pos, (lemma, morph, surface) in enumerate(ws):
            if not lemma or not morph:
                continue
            parts = [p.strip().split()[0] for p in lemma.split("/") if p.strip()]
            if hebrew.HAYAH in parts and "c" in parts:
                toks.append((morph, _POINTS.sub("", surface)))
    by_morph = Counter(m for m, _ in toks)
    cons = defaultdict(Counter)
    for m, c in toks:
        cons[c][m] += 1
    vyhy, vhyh = sum(cons["ויהי"].values()), sum(cons["והיה"].values())
    wayhi, wehayah = by_morph[hebrew.WAYHI], by_morph[hebrew.WEHAYAH]
    inst = hebrew.instances()
    buckets = {t: dict(Counter(h["bucket"] for h in inst if h["tense"] == t)) for t in ("past", "future")}
    return {
        "by_morph": dict(by_morph.most_common()), "form_names": FORM_NAMES,
        "by_consonants": {k: dict(v) for k, v in sorted(cons.items(), key=lambda kv: -sum(kv[1].values()))[:8]},
        "counting_rules": {
            "wayhi only (morphology)": wayhi,
            "wayhi + wihi (unpointed ויהי)": vyhy,
            "wayhi + wehayah (morphology)": wayhi + wehayah,
            "unpointed ויהי + unpointed והיה": vyhy + vhyh,
            "all 3rd-person wayyiqtol (wayhi, wayyihyu, wattehi)":
                wayhi + by_morph["HC/Vqw3mp"] + by_morph["HC/Vqw3fs"],
            "every hayah form with 'and'": len(toks)},
        "buckets": buckets,
        "bucket_rule_instances": {"wayhi": len([h for h in inst if h["tense"] == "past"]),
                                  "wehayah": len([h for h in inst if h["tense"] == "future"])},
    }


def headline(d: dict) -> list[Headline]:
    r = d["counting_rules"]
    b = d["buckets"]["past"]
    return [
        Headline("wayhi", r["wayhi only (morphology)"],
                 text=f"Hebrew Bible: {r['wayhi only (morphology)']} wayhi by morphology "
                      f"({b.get('time', 0)} setting-first, {b.get('event', 0)} straight to the event, "
                      f"{b.get('verb', 0)} ordinary verb); {d['by_morph']['HC/Vqq3ms']} wehayah."),
        Headline("unpointed_pooled", r["unpointed ויהי + unpointed והיה"],
                 text=f"Unpointed ויהי + והיה = {r['unpointed ויהי + unpointed והיה']:,}, the only counting rule "
                      f"near 1,204; it pools past wayhi with future wehayah and their look-alikes."),
    ]
