"""Greek New Testament ἐγένετο, the New Testament counterpart of *wayhi*.

Question: how do the Gospels and Acts use ἐγένετο ("and it came to pass"),
by bucket, and how does the Book of Mormon compare with them?

Why: Luke and Acts imitate Septuagint style, so they are the obvious
non-Hebrew model for a heavy "it came to pass" style that the Book of
Mormon's author would have known from the KJV New Testament. The hand labels
also test the English rule on a second language whose true bucket is known.
(That test found a bug in the revised rule: see the corrections in the
report.)

Method: hand labels in `annotations/egeneto_labels.tsv` (see
`bomstylo.greek`). As for Hebrew: KJV rendering by bucket, the English rule
against the Greek, and rates in the narrative books with speech removed per
instance by WEB quotation marks. Rates per 1,000 KJV words and per 100 Greek
verbs (MorphGNT V tags).
"""
from __future__ import annotations

from collections import Counter

from bomstylo import corpus, english, greek, results, stats, verbs, web
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="greek-egeneto",
    family="wayhi",
    title="Greek New Testament ἐγένετο by bucket",
    question="How often do the Gospels and Acts use the formula, by bucket, against the Book of Mormon?",
    why="Luke-Acts is the nearest non-Hebrew model of a heavy 'it came to pass' style, and the hand "
        "labels test the English rule on a second language.",
    label="exploratory",
    corpora=["sblgnt", "kjv", "web"],
    annotations=["egeneto_labels.tsv"],
    depends=["per-verb"],
    needs_verbs=True,
)
S, E = "setting", "event"
LEVELS = (("Gospels + Acts", list(greek.BOOKS)), ("Luke + Acts", ["Lk", "Ac"]),
          ("Matthew + Mark + John", ["Mt", "Mk", "Jn"]))


def past(t: str) -> int:
    c = english.counts(t)
    return c["past_time"] + c["past_event"]


def run() -> dict:
    G, inst = greek.gnt(), greek.instances()
    tot = Counter(h["bucket"] for h in inst)
    by_book = {b: dict(Counter(h["bucket"] for h in inst if h["book"] == b)) for b in G}
    kjv = {(v.book, v.chapter, v.verse): v.text for v in corpus.load("kjv_nt")}
    per_v = Counter(h["ref"] for h in inst)
    cal = {k: Counter() for k in greek.BUCKETS}
    for h in inst:
        t = kjv.get((greek.FULL[h["book"]], h["ch"], h["vs"]))
        if t is None or per_v[h["ref"]] != 1:
            continue
        c = english.counts(t)
        n = c["past_time"] + c["past_event"]
        cal[h["bucket"]]["verses"] += 1
        cal[h["bucket"]]["rendered"] += n > 0
        if n == 1 and h["bucket"] in (S, E):
            cal[h["bucket"]]["rule_agrees"] += c["past_time"] if h["bucket"] == S else c["past_event"]
    has = {(greek.FULL[h["book"]], h["ch"], h["vs"]) for h in inst if h["bucket"] in (S, E, "sub")}
    kjv_all, orph = 0, []
    for key, t in kjv.items():
        n = past(t)
        kjv_all += n
        if n and key not in has:
            orph.append(f"{key[0]} {key[1]}:{key[2]}")

    lv = {}
    for lab, books in LEVELS:
        kw = kf = gv = gvf = 0.0
        texts, fr = [], []
        for b in books:
            name = greek.BOOKS[b]
            for (ch, vs), ws in G[b].items():
                t = kjv.get((name, ch, vs), "")
                f = web.frame_share(name, ch, vs)
                kw += corpus.words(t)
                kf += corpus.words(t) * f
                texts.append(t)
                fr.append(f)
                for i, (pos, _, _, _) in enumerate(ws):
                    if pos.startswith("V"):
                        gv += 1
                        gvf += not web.in_speech(name, ch, vs, i, len(ws))
        ev = verbs.english(texts)
        sel = [h for h in inst if h["book"] in books]
        lv[lab] = {"kjv_words": kw, "kjv_words_frame": kf, "greek_verbs": gv, "greek_verbs_frame": gvf,
                   "kjv_verbs": sum(ev), "kjv_verbs_frame": sum(n * f for n, f in zip(ev, fr)),
                   "counts": dict(Counter(h["bucket"] for h in sel)),
                   "counts_frame": dict(Counter(h["bucket"] for h in sel if not web.in_speech(
                       greek.BOOKS[h["book"]], h["ch"], h["vs"], h["pos"], h["n"]))),
                   "kjv_phrase_all": sum(past(t) for t in texts)}

    B = results.data("per-verb")["bom"]
    bw, bv = B["words_1830"], B["verbs"] * B["words_1830"] / B["words"]
    bs, be = B["setting_1830"], B["event_1830"]
    rows = {}
    for lab, x in lv.items():
        s, e = x["counts_frame"].get(S, 0), x["counts_frame"].get(E, 0)
        k, v = x["kjv_words_frame"], x["greek_verbs_frame"]
        rows[lab] = {"setting": s, "event": e, "per_1k": [1000 * s / k, 1000 * e / k, 1000 * (s + e) / k],
                     "per_100_verbs": 100 * (s + e) / v, "event_share": e / (s + e) if s + e else None,
                     "event_share_ci": stats.share_ci(e, s + e),
                     "bom_ratio": (bs + be) / bw * k / (s + e),
                     "bom_ratio_1k": stats.ratio_ci(bs + be, bw, s + e, k),
                     "bom_ratio_per_verb": (bs + be) / bv * v / (s + e),
                     "bom_ratio_verbs": stats.ratio_ci(bs + be, bv, s + e, v),
                     "kjv_verbs_per_greek_verb": x["kjv_verbs"] / x["greek_verbs"]}
    lab = greek.labels()
    return {"instances": inst, "totals": dict(tot), "by_book": by_book,
            "calibration": {k: dict(v) for k, v in cal.items()},
            "kjv_nt_phrase": kjv_all, "kjv_orphans": orph, "levels": lv, "rows": rows,
            "bom_1830": {"per_1k": 1000 * (bs + be) / bw, "per_100_verbs": 100 * (bs + be) / bv,
                         "event_share": be / (bs + be)},
            "borderline": sorted(r for r, x in lab.items() if x["note"].startswith("borderline")),
            "subject_after_time": sorted(r for r, x in lab.items() if x["bucket"] == "verb")}


def headline(d: dict) -> list[Headline]:
    r = d["rows"]["Luke + Acts"]
    lo, hi = r["bom_ratio_1k"]
    c = d["calibration"]
    return [
        Headline("luke_acts_ratio", r["bom_ratio"], lo, hi,
                 text=f"Luke + Acts narrative frame: {r['per_1k'][2]:.2f} per 1,000 KJV words, "
                      f"{r['event_share']:.0%} straight to the event; the 1830 Book of Mormon is "
                      f"{r['bom_ratio']:.1f}× ({lo:.1f}–{hi:.1f}) that rate."),
        Headline("greek_totals", d["totals"].get(S, 0),
                 text=f"Greek NT ἐγένετο: {d['totals'].get(S, 0)} setting-first, {d['totals'].get(E, 0)} straight to "
                      f"the event, {d['totals'].get('sub', 0)} subordinate, {d['totals'].get('verb', 0)} ordinary verb; "
                      f"English rule agrees on {c[S].get('rule_agrees', 0)}/{c[S].get('rendered', 0)} rendered settings."),
    ]
