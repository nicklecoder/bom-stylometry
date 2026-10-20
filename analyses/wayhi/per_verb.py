"""The comparisons again, per verb and per source word instead of per English word.

Question: do the Hebrew / Book of Mormon ratio and the additive model hold up
when the unit is not English words?

Why: every "per 1,000 words" elsewhere counts the KJV's English words for
Hebrew, the book's own words for the Book of Mormon, and German translation
words for Demotic. Word counts don't carry between languages: Hebrew writes
"and-he-said" as one word, English as three.

Method (see `bomstylo.verbs`):
1. per 100 verbs, each language counted in its own text;
2. as a check that verbs survive translation, the KJV English of the same 17
   Hebrew units is counted the same way (KJV verbs per Hebrew verb should be
   near 1, while KJV words per Hebrew word is not);
3. per 1,000 source words (Hebrew words; transliterated Demotic words), with
   the Book of Mormon in English, since it has no source text.

Hebrew: the 17 narrative units, narrative frame (outside WEB quotation marks),
setting-first *wayhi* only. 1830 verbs are scaled from the current text by
word count.
"""
from __future__ import annotations

from collections import Counter

from bomstylo import corpus, egyptian as E, english, genre, hebrew, results, spans, stats, verbs, web
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="per-verb",
    family="wayhi",
    title="'It came to pass' per verb and per source word",
    question="Do the Hebrew ratio and the additive model survive when the unit is verbs or source words "
             "rather than English words?",
    why="English word counts don't translate between languages; verbs roughly do.",
    label="exploratory",
    corpora=["wlc", "web", "kjv", "bom-current", "tla"],
    annotations=["embedded.tsv"],
    depends=["bom-buckets", "egyptian"],
    needs_verbs=True,
)


def per(k, n, scale=100):
    return stats.rate_ci(k, n, scale)


def hebrew_side() -> dict:
    unit_of = genre.unit_of_chapter()
    heb_words = heb_verbs = 0
    for book, ch, vs, ws in hebrew.tagged_verses():
        if (book, ch) not in unit_of:
            continue
        for i, (_, m) in enumerate(ws):
            if web.in_speech(book, ch, vs, i, len(ws)):
                continue
            heb_words += 1
            heb_verbs += verbs.hebrew(m)
    c = Counter(h["bucket"] for h in hebrew.instances()
                if (h["book"], h["ch"]) in unit_of and h["tense"] == "past"
                and not web.in_speech(h["book"], h["ch"], h["vs"], h["pos"], h["n"]))
    kv = [v for v in corpus.load("kjv_ot") if (v.book, v.chapter) in unit_of]
    fr = [web.frame_share(v.book, v.chapter, v.verse) for v in kv]
    nv = verbs.english([v.text for v in kv])
    return {"hebrew_words": heb_words, "hebrew_verbs": heb_verbs,
            "kjv_words": sum(corpus.words(v.text) * f for v, f in zip(kv, fr)),
            "kjv_verbs": sum(n * f for n, f in zip(nv, fr)),
            "setting": c["time"], "verb_use": c["verb"], "event": c["event"]}


def bom_side() -> dict:
    verses = corpus.load("bom")
    lay = spans.layers(verses)
    fr = [v.text for i, v in enumerate(verses) if not lay.quotation[i] and not lay.embedded[i]]
    c = Counter()
    for t in fr:
        c.update(english.counts(t))
    d = results.data("bom-buckets")["1830|revised"]["narrative frame"]
    return {"words": sum(corpus.words(t) for t in fr), "verbs": sum(verbs.english(fr)),
            "setting": c["past_time"], "event": c["past_event"],
            "setting_1830": d["counts"]["past_time"], "event_1830": d["counts"]["past_event"],
            "words_1830": d["words"]}


def demotic_side() -> dict:
    eg = results.data("egyptian")
    out = {}
    for k, S in E.demotic_selections().items():
        m = eg["demotic"][k]
        out[k] = {"sentences": len(S), "german_words": sum(len(r["translation"].split()) for r in S),
                  "demotic_words": sum(len(r["transliteration"].split()) for r in S),
                  "verbs": sum(verbs.demotic(r) for r in S), "setting": m["time"], "event": m["event"]}
    ryl = [r for r in E.rylands() if not E.QUOTE.search(r["translation"])]
    p = eg["rylands"]["unquoted (narrative frame)"]
    out["pRylands 9"] = {"sentences": len(ryl), "german_words": sum(len(r["translation"].split()) for r in ryl),
                         "demotic_words": sum(len(r["transliteration"].split()) for r in ryl),
                         "verbs": sum(verbs.demotic(r) for r in ryl),
                         "setting": p["time_first"], "event": p["event_first"]}
    return out


def run() -> dict:
    H, B, D = hebrew_side(), bom_side(), demotic_side()
    rows = {}
    hs = per(H["setting"], H["hebrew_verbs"])
    rows["Hebrew"] = {"setting": hs, "event": [0.0, 0.0, per(0, H["hebrew_verbs"])[2]], "total": hs}
    for lab, s, e, n in (("Book of Mormon (current)", B["setting"], B["event"], B["verbs"]),
                         ("Book of Mormon (1830)", B["setting_1830"], B["event_1830"],
                          B["verbs"] * B["words_1830"] / B["words"])):
        rows[lab] = {"setting": per(s, n), "event": per(e, n), "total": per(s + e, n)}
    for k, v in D.items():
        ds, de = per(v["setting"], v["verbs"]), per(v["event"], v["verbs"])
        rows[k] = {"setting": ds, "event": de, "total": per(v["setting"] + v["event"], v["verbs"])}
        rows["Hebrew + " + k] = {"setting": [hs[0] + x for x in ds], "event": de,
                                 "total": [hs[0] + x for x in per(v["setting"] + v["event"], v["verbs"])]}
    src = {"Hebrew per 1,000 Hebrew words": 1000 * H["setting"] / H["hebrew_words"],
           "Hebrew per 1,000 KJV words": 1000 * H["setting"] / H["kjv_words"],
           "BoM 1830 per 1,000 words": 1000 * (B["setting_1830"] + B["event_1830"]) / B["words_1830"]}
    for k, v in D.items():
        src[f"{k} per 1,000 Demotic words"] = 1000 * (v["setting"] + v["event"]) / v["demotic_words"]
        src[f"{k} per 1,000 German words"] = 1000 * (v["setting"] + v["event"]) / v["german_words"]
    validation = {"kjv_verbs_per_hebrew_verb": H["kjv_verbs"] / H["hebrew_verbs"],
                  "kjv_words_per_hebrew_word": H["kjv_words"] / H["hebrew_words"],
                  "words_per_verb": {"KJV (17 units)": H["kjv_words"] / H["kjv_verbs"],
                                     "Book of Mormon": B["words"] / B["verbs"],
                                     **{f"German, {k}": v["german_words"] / v["verbs"] for k, v in D.items()}}}
    ratio = {"current": rows["Book of Mormon (current)"]["total"][0] / hs[0],
             "1830": rows["Book of Mormon (1830)"]["total"][0] / hs[0],
             "current_ci": stats.ratio_ci(B["setting"] + B["event"], B["verbs"], H["setting"], H["hebrew_verbs"]),
             "1830_ci": stats.ratio_ci(B["setting_1830"] + B["event_1830"], B["verbs"] * B["words_1830"] / B["words"],
                                       H["setting"], H["hebrew_verbs"])}
    return {"hebrew": H, "bom": B, "demotic": D, "per_100_verbs": rows, "per_1k": src,
            "validation": validation, "ratio": ratio}


def headline(d: dict) -> list[Headline]:
    r, v = d["ratio"], d["validation"]
    rows = d["per_100_verbs"]
    model = [x["total"][0] for k, x in rows.items() if k.startswith("Hebrew + ")]
    return [
        Headline("ratio_per_verb", r["current"], r["current_ci"][0], r["current_ci"][1],
                 text=f"Per 100 verbs, Book of Mormon ÷ Hebrew = {r['current']:.2f}× ({r['current_ci'][0]:.1f}–"
                      f"{r['current_ci'][1]:.1f}) current, {r['1830']:.2f}× 1830 (2.7× per KJV word)."),
        Headline("verbs_survive", v["kjv_verbs_per_hebrew_verb"],
                 text=f"Validation: KJV has {v['kjv_verbs_per_hebrew_verb']:.3f} verbs per Hebrew verb in the same "
                      f"passages, but {v['kjv_words_per_hebrew_word']:.2f} words per Hebrew word."),
        Headline("additive_per_verb_max", max(model),
                 text=f"Additive model per 100 verbs: {min(model):.2f}–{max(model):.2f} against the 1830 book's "
                      f"{rows['Book of Mormon (1830)']['total'][0]:.2f}."),
    ]
