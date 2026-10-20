"""The Egyptian side: old narrative particles, Demotic ḫpr, and the additive model.

Question: does Egyptian narrative use a "then / it came to pass" opening at a
rate and with a setting/event mix that would explain the Book of Mormon,
either alone or added to Hebrew *wayhi*?

Why: the book says it was written in "reformed Egyptian" (Mormon 9:32), so an
Egyptian contribution is the natural alternative to "Hebraism or English
imitation". Three measurements:
1. the old narrative particles (ꜥḥꜥ.n, wn.ꞽn) in named connected narratives
   (AED-TEI) and in the 25th–26th-dynasty royal inscriptions (the Saite check);
2. Demotic ḫpr "it came to pass" openings in TLA narrative sentences, and in
   pRylands 9 (c. 513 BC), each split into setting-first and straight-to-event;
3. the additive model: Hebrew setting-first *wayhi* plus each Egyptian rate,
   against the 1830 Book of Mormon frame.

Comparability (constitution II): a rate counts for or against the book only if
the text matches in genre (connected narrative) and date (composed about
600–500 BC or earlier). Each row carries `date_ok`, `genre_ok` and `matched`.
The Demotic sentences and pRylands 9 fail on genre (documents, later copies, a
petition), so their rows are reported but can't decide the question. The
matched narratives (Middle and Late Egyptian tales, Piye) use the old
particles, not ḫpr, and their rates are per *estimated* translation word.

Units: per 1,000 words is not a shared scale across languages (Demotic is
counted in German translation words; Egyptian tokens are scaled by a measured
expansion factor). per-verb re-measures the same comparison per 100 verbs.

Correction carried here: the first additive model (2026-10-13) added the
Hebrew ordinary-verb *wayhi* ("and there was light") as if it were the formula.
The Hebrew side is setting-first only; its straight-to-event bucket is empty.
"""
from __future__ import annotations

import re

from bomstylo import egyptian as E, results, stats
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="egyptian",
    family="wayhi",
    title="Egyptian narrative openings, and the Hebrew + Egyptian additive model",
    question="Do Egyptian narratives open clauses with 'then / it came to pass' at a rate and mix that, "
             "alone or added to Hebrew, matches the Book of Mormon?",
    why="Tests the 'reformed Egyptian' alternative on the texts that match in genre and date.",
    label="exploratory",
    corpora=["aed-tei", "tla"],
    depends=["genre-ladder"],
    params={"markers": E.MARKERS, "tla_date_cutoff": -200, "min_tokens": E.MIN_TOKENS,
            "expansion_hieroglyphic": E.EXPANSION_HIEROGLYPHIC, "date_limit_bc": 500},
)

_S = re.compile(r"<s\b[^>]*>(.*?)</s>", re.S)
_W = re.compile(r'<w [^>]*lemmaRef="tla:tla(\w+)"[^>]*>\s*<fs feats="([^"]*)"\s*/>(.*?)</w>', re.S)


def _flags(composed_bc: int | None, narrative: bool) -> dict:
    date_ok = composed_bc is not None and composed_bc >= ANALYSIS.params["date_limit_bc"]
    return {"date_ok": date_ok, "genre_ok": narrative, "matched": date_ok and narrative}


def _bc(s: str) -> int | None:
    m = re.search(r"(\d+) BC", s)
    return int(m.group(1)) if m else None


def hieroglyphic() -> dict:
    out = {}
    for tid, name in E.HIEROGLYPHIC.items():
        sents = [_W.findall(s) for s in _S.findall(E.aed(tid))]
        tok = sum(len(s) for s in sents)
        mk = sum(l in E.MARKERS for s in sents for l, _, _ in s)
        hp = sum(bool(s) and re.sub(r"<[^>]+>", "", s[0][2]).strip().startswith("ḫpr") for s in sents)
        out[name] = {"tokens": tok, "translated_word_equiv": round(tok * E.EXPANSION_HIEROGLYPHIC),
                     "old_particles": mk, "hpr_initial": hp,
                     "per_1k": round(1000 * (mk + hp) / (tok * E.EXPANSION_HIEROGLYPHIC), 2),
                     "below_floor": tok < E.MIN_TOKENS,
                     **_flags(_bc(name), True)}
    return out


def demotic() -> dict:
    out = {}
    for k, S in E.demotic_selections().items():
        tw = sum(len(r["translation"].split()) for r in S)
        hp = [r for r in S if E.HPR_INIT.match(r["transliteration"])]
        t = sum(bool(E.HPR_TIME_DE.search(r["translation"])) for r in hp)
        out[k] = {"sentences": len(S), "words": tw, "n": len(hp), "time": t, "event": len(hp) - t,
                  "formula_translated": sum(bool(E.HPR_FORMULA_DE.search(r["translation"])) for r in hp),
                  "all_per_1k": stats.rate_ci(len(hp), tw), "time_per_1k": stats.rate_ci(t, tw),
                  "event_per_1k": stats.rate_ci(len(hp) - t, tw), "event_share": stats.share_ci(len(hp) - t, len(hp)),
                  "date_ok": "700" in k, "genre_ok": False, "matched": False}
    return out


def rylands() -> dict:
    out = {}
    for label, sel in (("all sentences", lambda r: True),
                       ("unquoted (narrative frame)", lambda r: not E.QUOTE.search(r["translation"]))):
        X = [r for r in E.rylands() if sel(r)]
        w = sum(len(r["translation"].split()) for r in X)
        hits = [r for r in X if E.RYLANDS_OPEN.match(r["transliteration"])]
        t = [r for r in hits if E.rylands_time_first(r)]
        out[label] = {"sentences": len(X), "words": w, "openings": len(hits),
                      "per_1k": stats.rate_ci(len(hits), w), "time_first": len(t), "event_first": len(hits) - len(t),
                      "event_share": stats.share_ci(len(hits) - len(t), len(hits)),
                      "examples": [(r["transliteration"][:50], r["translation"][:100]) for r in hits],
                      "date_ok": True, "genre_ok": False, "matched": False}
    return out


def run() -> dict:
    subsets = E.subset_rates(ANALYSIS.params["tla_date_cutoff"])
    expansion = {"Middle Egyptian": subsets["Earlier Egyptian"]["expansion"],
                 "Late Egyptian": subsets["Late Egyptian"]["expansion"],
                 "Late Period": subsets["Late Egyptian"]["expansion"]}
    named = E.named_rates(expansion)
    for t in named["texts"].values():
        t.update(_flags(_bc(t["composed"]), True))
    hiero, dem, ryl = hieroglyphic(), demotic(), rylands()

    gl = results.data("genre-ladder")["buckets"]
    ht, ht_lo, ht_hi = gl["past_time"]["hebrew"][1:]
    bt, be = gl["past_time"]["bom_1830"][1], gl["past_event"]["bom_1830"][1]
    model = {}
    for k, v in dem.items():
        model[f"Hebrew + {k}"] = {"time": [ht + x for x in v["time_per_1k"]], "event": v["event_per_1k"],
                                  "total": [ht + x for x in v["all_per_1k"]], "matched": False}
    p = ryl["unquoted (narrative frame)"]
    pw = p["words"]
    model["Hebrew + pRylands 9"] = {"time": [ht + x for x in stats.rate_ci(p["time_first"], pw)],
                                    "event": stats.rate_ci(p["event_first"], pw),
                                    "total": [ht + x for x in stats.rate_ci(p["openings"], pw)], "matched": False}
    piye = named["texts"]["Piye Victory Stela"]
    model["Hebrew + Piye (old particles, all straight-to-event)"] = {
        "time": [ht, ht_lo, ht_hi], "event": [piye["per1k_translated"]] * 3,
        "total": [ht + piye["per1k_translated"]] * 3, "matched": True,
        "note": "Piye rate is per estimated translation word; no interval is given for the scale factor"}
    matched_rates = [t["per1k_translated"] for t in named["texts"].values() if t["matched"] and not t["below_floor"]]
    return {"subsets": subsets, "expansion": expansion, "named": named, "hieroglyphic": hiero,
            "demotic": dem, "rylands": ryl,
            "additive_model": {"hebrew_setting": [ht, ht_lo, ht_hi], "rows": model,
                               "bom_1830": {"time": bt, "event": be, "total": bt + be,
                                            "event_share": be / (bt + be)}},
            "matched_range": [min(matched_rates), max(matched_rates)] if matched_rates else None}


def headline(d: dict) -> list[Headline]:
    lo, hi = d["matched_range"]
    piye = d["named"]["texts"]["Piye Victory Stela"]["per1k_translated"]
    m = d["additive_model"]
    dem = [r["total"] for k, r in m["rows"].items() if k.startswith("Hebrew + demotic")]
    p = d["rylands"]["unquoted (narrative frame)"]
    return [
        Headline("matched_range_high", hi,
                 text=f"Egyptian connected narratives matched in genre and date run {lo:.0f}–{hi:.0f} old-particle "
                      f"openings per 1,000 estimated translation words by text (Piye c. 727 BC: {piye:.2f}); they "
                      f"bracket the Book of Mormon's {m['bom_1830']['total']:.2f} (1830 frame), so the rate test is "
                      f"inconclusive, not negative."),
        Headline("additive_demotic_max", max(r[0] for r in dem),
                 text=f"Hebrew settings + Demotic ḫpr: {min(r[0] for r in dem):.1f}–{max(r[0] for r in dem):.1f} per "
                      f"1,000 against the 1830 frame's {m['bom_1830']['total']:.2f}; the Demotic texts fail on genre, "
                      f"so this does not decide the question."),
        Headline("rylands_openings", p["openings"],
                 text=f"pRylands 9 narration (c. 513 BC): {p['openings']} 'it came to pass' openings in {p['words']:,} "
                      f"German words ({p['per_1k'][0]:.2f}), {p['time_first']} setting-first, "
                      f"{p['event_first']} straight to the event."),
    ]
