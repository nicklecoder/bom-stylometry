"""Hebrew *wayhi* against the Book of Mormon, one genre control at a time.

Question: how much more often does the Book of Mormon use "it came to pass"
than Hebrew narrative uses the construction behind it, once both sides are cut
to the same kind of text? And which use of the formula makes up the
difference?

Why: the often-quoted ratio compares the Book of Mormon's English with the
KJV's English across the whole Old Testament. That mixes two problems. The KJV
doesn't render every *wayhi* as "it came to pass" (see kjv-rendering), and the
Old Testament is largely poetry, law and prophecy, where the construction
barely occurs. This analysis counts the Hebrew directly and changes one genre
control at a time, on both sides (see `bomstylo.genre`).

Method:
- Hebrew side: every *wayhi* and *wehayah*, bucketed by the Hebrew rule
  (`bomstylo.hebrew`). Each is placed in or out of speech by the World English
  Bible's quotation marks (`bomstylo.web`).
- Rates are per 1,000 KJV words of the same passages. Narrative-frame word
  counts take each verse's WEB share of words outside quotes. per-verb checks
  this choice of unit.
- Only setting-first *wayhi* (the `time` bucket) is compared with the Book of
  Mormon's past formula. The ordinary-verb use ("and there was light") has no
  "it came to pass" counterpart.
- Book of Mormon side: from bom-buckets.
- Intervals are exact: conditional binomial for rate ratios, Poisson for rates.
"""
from __future__ import annotations

from collections import Counter

from bomstylo import corpus, english, genre, hebrew, results, stats, web
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="genre-ladder",
    family="wayhi",
    title="Genre ladder: Hebrew setting-first wayhi vs the Book of Mormon",
    question="How does the Book of Mormon's rate compare with Hebrew wayhi at each matched genre "
             "step, and which use of the formula carries the difference?",
    why="Replaces the whole-Bible English-to-English ratio with a like-for-like comparison, showing "
        "the effect of each control.",
    label="exploratory",
    corpora=["wlc", "web", "kjv"],
    depends=["bom-buckets"],
)


def hebrew_levels():
    heb = hebrew.instances()
    kjv = {(v.book, v.chapter, v.verse): v.text for v in corpus.load("kjv_ot")}
    narr, story = list(genre.NARRATIVE_BOOKS), genre.STORY_BOOKS
    with_web = set(narr) | {"Jonah"}
    unit_of = genre.unit_of_chapter()

    kjv_words, frame_words, speech_words, unit_frame = Counter(), Counter(), Counter(), Counter()
    for (b, ch, vs), t in kjv.items():
        kjv_words[b] += corpus.words(t)
    for (b, ch, vs), t in kjv.items():
        if b not in with_web:
            continue
        w, fr = corpus.words(t), web.frame_share(b, ch, vs)
        if b in narr:
            frame_words[b] += w * fr
            speech_words[b] += w * (1 - fr)
        if (b, ch) in unit_of:
            unit_frame[unit_of[(b, ch)]] += w * fr
    for h in heb:
        if h["book"] in with_web:
            s = web.in_speech(h["book"], h["ch"], h["vs"], h["pos"], h["n"])
            h["speech"] = bool(s) if s is not None else False
            h["unaligned"] = s is None
        h["unit"] = unit_of.get((h["book"], h["ch"]))

    def hcount(sel):
        return dict(Counter(f"{h['tense']}_{h['bucket']}" for h in heb if sel(h)))

    def kjv_phrase(books, where="all"):
        """KJV 'it came to pass' in these books, placed in frame or speech like the Hebrew."""
        n = 0
        for (b, ch, vs), t in kjv.items():
            if b not in books or (where == "units" and (b, ch) not in unit_of):
                continue
            for m in english.PAST.finditer(t.lower()):
                if where == "all":
                    n += 1
                    continue
                s = web.in_speech(b, ch, vs, max(m.start(), 1), len(t))
                n += (where == "speech") == bool(s)
        return n

    kjv_total_past = sum(english.counts(t)["past_time"] + english.counts(t)["past_event"]
                         for t in kjv.values())
    lv = {
        "whole OT": (hcount(lambda h: True), sum(kjv_words.values()), kjv_total_past),
        "17 narrative books": (hcount(lambda h: h["book"] in narr),
                               sum(kjv_words[b] for b in narr), kjv_phrase(narr)),
        "story books (no Lev/Num/Deut)": (hcount(lambda h: h["book"] in story),
                                          sum(kjv_words[b] for b in story), kjv_phrase(story)),
        "story books, narrative frame": (hcount(lambda h: h["book"] in story and not h.get("speech")),
                                         sum(frame_words[b] for b in story), kjv_phrase(story, "frame")),
        "17 narrative units, narrative frame": (hcount(lambda h: h["unit"] and not h.get("speech")),
                                                sum(unit_frame.values()),
                                                kjv_phrase({u[1] for u in genre.HEBREW_UNITS}, "units")),
        "story books, speech only": (hcount(lambda h: h["book"] in story and h.get("speech")),
                                     sum(speech_words[b] for b in story), kjv_phrase(story, "speech")),
    }
    units = {lab: {"frame_words": unit_frame[lab],
                   "counts": hcount(lambda h, l=lab: h["unit"] == l and not h.get("speech"))}
             for lab in unit_frame}
    return ({k: {"counts": c, "words": w, "kjv_past_phrase": kp} for k, (c, w, kp) in lv.items()},
            units, sum(1 for h in heb if h.get("unaligned")))


def _past(c):
    return c.get("past_time", 0) + c.get("past_event", 0)


def run() -> dict:
    H, units, unaligned = hebrew_levels()
    bb = results.data("bom-buckets")
    B, O = bb["current|revised"], bb["1830|revised"]

    ladder = []
    for h, b in genre.LADDER:
        hw = H[h]["words"]
        hs_k = H[h]["counts"].get("past_time", 0)
        ladder.append({
            "hebrew_level": h, "bom_level": b,
            "kjv": stats.rate(H[h]["kjv_past_phrase"], hw), "hebrew_setting": stats.rate(hs_k, hw),
            "bom": stats.rate(_past(B[b]["counts"]), B[b]["words"]),
            "bom_1830": stats.rate(_past(O[b]["counts"]), O[b]["words"]),
            "bom_setting": stats.rate(B[b]["counts"].get("past_time", 0), B[b]["words"]),
            "bom_event": stats.rate(B[b]["counts"].get("past_event", 0), B[b]["words"]),
        })
        r = ladder[-1]
        r.update(ratio_kjv=r["bom"] / r["kjv"], ratio_hebrew=r["bom"] / r["hebrew_setting"],
                 ratio_hebrew_1830=r["bom_1830"] / r["hebrew_setting"],
                 ratio_hebrew_ci=stats.ratio_ci(_past(B[b]["counts"]), B[b]["words"], hs_k, hw),
                 ratio_hebrew_1830_ci=stats.ratio_ci(_past(O[b]["counts"]), O[b]["words"], hs_k, hw))

    hu, hsp = H["17 narrative units, narrative frame"], H[genre.SPEECH_PAIR[0]]
    bf, of_, bs, os_ = B["narrative frame"], O["narrative frame"], B["speech (not KJV)"], O["speech (not KJV)"]
    buckets = {}
    for key, hh, b_, o_ in (("past_time", hu, bf, of_), ("past_event", hu, bf, of_), ("past_verb", hu, bf, of_),
                            ("future_time", hsp, bs, os_), ("future_event", hsp, bs, os_),
                            ("future_verb", hsp, bs, os_)):
        hk, bk, ok = hh["counts"].get(key, 0), b_["counts"].get(key, 0), o_["counts"].get(key, 0)
        hr = stats.rate_ci(hk, hh["words"])
        buckets[key] = {"hebrew": [hk, *hr], "bom": [bk, stats.rate(bk, b_["words"])],
                        "bom_1830": [ok, stats.rate(ok, o_["words"])],
                        "ratio_ci": stats.ratio_ci(bk, b_["words"], hk, hh["words"]) if hk else None,
                        "ratio_1830_ci": stats.ratio_ci(ok, o_["words"], hk, hh["words"]) if hk else None}
    unit_rows = {lab: {**u, "setting_per1k": stats.rate(u["counts"].get("past_time", 0), u["frame_words"]),
                       "all_wayhi_per1k": stats.rate(sum(v for k, v in u["counts"].items()
                                                         if k.startswith("past")), u["frame_words"])}
                 for lab, u in units.items()}
    kjv_ot = Counter()
    for v in corpus.load("kjv_ot"):
        kjv_ot.update(english.counts(v.text))
    return {"hebrew_levels": H, "hebrew_unaligned": unaligned, "units": unit_rows, "ladder": ladder,
            "buckets": buckets,
            "kjv_ot_event_share": [kjv_ot["past_event"], kjv_ot["past_event"] + kjv_ot["past_time"],
                                   *stats.share_ci(kjv_ot["past_event"],
                                                   kjv_ot["past_event"] + kjv_ot["past_time"])]}


def headline(d: dict) -> list[Headline]:
    first, last = d["ladder"][0], d["ladder"][-1]
    lo, hi = last["ratio_hebrew_ci"]
    lo8, hi8 = last["ratio_hebrew_1830_ci"]
    s = d["buckets"]["past_time"]
    slo, shi = s["ratio_ci"]
    dens = max(d["units"].items(), key=lambda kv: kv[1]["setting_per1k"])
    return [
        Headline("ratio_whole", first["ratio_hebrew"],
                 text=f"Whole Old Testament vs whole Book of Mormon: {first['ratio_hebrew']:.1f}x the Hebrew "
                      f"setting-first wayhi rate ({first['ratio_kjv']:.1f}x the KJV's English)."),
        Headline("ratio_matched", last["ratio_hebrew"], lo, hi,
                 text=f"17 Hebrew narrative units vs Book of Mormon narrative frame: {last['ratio_hebrew']:.1f}x "
                      f"({lo:.1f}-{hi:.1f}) current text, {last['ratio_hebrew_1830']:.1f}x ({lo8:.1f}-{hi8:.1f}) "
                      f"1830 text, per 1,000 KJV-scale words."),
        Headline("setting_ratio", s["bom"][1] / s["hebrew"][1], slo, shi,
                 text=f"Setting-first uses alone: Book of Mormon {s['bom'][1]:.2f} vs Hebrew {s['hebrew'][1]:.2f} "
                      f"per 1,000 = {s['bom'][1] / s['hebrew'][1]:.2f}x ({slo:.2f}-{shi:.2f}). Hebrew has "
                      f"{d['buckets']['past_event']['hebrew'][0]} straight-to-the-event wayhi; the Book of Mormon "
                      f"{d['buckets']['past_event']['bom'][0]}."),
        Headline("densest_unit", dens[1]["setting_per1k"],
                 text=f"Densest Hebrew unit (setting-first): {dens[0]} at {dens[1]['setting_per1k']:.2f} per "
                      f"1,000, against the Book of Mormon frame's {last['bom']:.2f}."),
    ]
