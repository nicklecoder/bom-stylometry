"""Straight-to-the-event share of "it came to pass" in the English comparison texts.

Question: how often do English texts in biblical style, written without (or
before) the Book of Mormon, put the event straight after the formula? And
Joseph Smith's own later scripture?

Why: the Book of Mormon's event-first share (70%) is the feature an Egyptian
source was proposed to explain (PREREG 2). Before that explanation is needed,
English has to be shown not to produce it. Texts:
- the KJV Old and New Testaments (the model every pastiche imitated);
- four pastiches: Snowden (1793), The First Book of Napoleon (1809),
  The Late War (1819), The Book of Nullification (1830);
- the JST under the revised rule (the registered run is prereg-jst-then);
- Moses and Abraham (Pearl of Great Price), as Smith dictated them. Abraham
  claims an Egyptian source; Moses doesn't. Descriptive only.

Each text is counted under both English rules; whole texts, speech included.
Rates per 1,000 words are given for scale.
"""
from __future__ import annotations

from scipy.stats import fisher_exact

from bomstylo import controls, corpus, english, jst, pgp, stats
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="event-shares",
    family="wayhi",
    title="Event-first share in English comparison texts, the JST, Moses and Abraham",
    question="Do English texts in biblical style reach the Book of Mormon's event-first share and rate?",
    why="An Egyptian explanation of the event-first share is needed only if English doesn't produce it.",
    label="exploratory",
    corpora=["kjv", "late-war", "period-pastiches", "jst-1867", "moses-abraham"],
)
PGP = {"Moses 1": ("Moses", [1]), "Moses 2–4": ("Moses", [2, 3, 4]), "Moses 5–8": ("Moses", [5, 6, 7, 8]),
       "Moses (all)": ("Moses", None), "Abraham": ("Abraham", None)}


def texts() -> dict[str, str]:
    t = {"KJV Old Testament": " ".join(v.text for v in corpus.load("kjv_ot")),
         "KJV New Testament": " ".join(v.text for v in corpus.load("kjv_nt")),
         "The Late War (1819)": " ".join(controls.late_war())}
    for name in controls.PERIOD:
        t[name] = controls.period(name)
    for name, (book, chs) in PGP.items():
        t[name] = pgp.text(book, chs)
    return t


def run() -> dict:
    out = {}
    for k, t in texts().items():
        w = corpus.words(t)
        for r in english.RULES:
            c = english.counts(t, r)
            e, tm = c["past_event"], c["past_time"]
            out[f"{k} | {r}"] = {"event": e, "time": tm, "share": stats.share_ci(e, e + tm),
                                 "words": w, "per_1k": stats.rate(e + tm, w)}
    m, a = out["Moses (all) | revised"], out["Abraham | revised"]
    p = fisher_exact([[a["event"], a["time"]], [m["event"], m["time"]]])[1]
    res = jst.run("revised")
    from analyses.wayhi.prereg_jst_then import BOUNDARY_SPILL, panels
    return {"texts": out, "abraham_vs_moses_fisher_p": p,
            "jst_revised": {"panels": panels(res), "boundary_corrected": panels(res, BOUNDARY_SPILL)}}


def headline(d: dict) -> list[Headline]:
    t = d["texts"]
    past = ["Snowden, American Revolution (1793)", "First Book of Napoleon (1809)", "The Late War (1819)",
            "Book of Nullification (1830)"]
    rows = ", ".join(f"{k.split(',')[0].split(' (')[0]} {t[k + ' | revised']['share'][0]:.0%} of "
                     f"{t[k + ' | revised']['event'] + t[k + ' | revised']['time']}" for k in past)
    rates = [t[k + " | revised"]["per_1k"] for k in past]
    J = d["jst_revised"]["boundary_corrected"]["primary (OT narrative)"]
    a, m = t["Abraham | revised"], t["Moses (all) | revised"]
    return [
        Headline("pastiche_max_share", max(t[k + " | revised"]["share"][0] for k in past),
                 text=f"Pastiche event-first shares (revised rule): {rows}; rates {min(rates):.2f}–{max(rates):.2f} "
                      f"per 1,000 words, at most a third of the Book of Mormon's."),
        Headline("kjv_ot_share", t["KJV Old Testament | revised"]["share"][0],
                 text=f"KJV Old Testament: {t['KJV Old Testament | revised']['share'][0]:.0%} event-first "
                      f"({t['KJV Old Testament | revised']['event']}/{t['KJV Old Testament | revised']['event'] + t['KJV Old Testament | revised']['time']}); "
                      f"New Testament {t['KJV New Testament | revised']['share'][0]:.0%}."),
        Headline("jst_added_share", J["added"]["share"][0], J["added"]["share"][1], J["added"]["share"][2],
                 text=f"JST additions, revised rule, boundary-corrected: {J['added']['event']}/{J['added']['n']} "
                      f"event-first ({J['added']['share'][0]:.0%}); formulas kept from the KJV "
                      f"{J['retained']['share'][0]:.0%}."),
        Headline("abraham_vs_moses_p", d["abraham_vs_moses_fisher_p"],
                 text=f"Abraham (claims an Egyptian source) {a['event']}/{a['event'] + a['time']} event-first at "
                      f"{a['per_1k']:.2f} per 1,000; Moses {m['event']}/{m['event'] + m['time']} at {m['per_1k']:.2f}. "
                      f"Fisher p = {d['abraham_vs_moses_fisher_p']:.2f}: no difference."),
    ]
