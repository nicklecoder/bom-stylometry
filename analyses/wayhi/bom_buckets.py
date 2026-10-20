"""Book of Mormon "it came / shall come to pass", by bucket, at each genre step.

Question: how often does the Book of Mormon use the formula, split by what
follows it (a setting first, or straight to the event) and by tense, in the
whole text, without the KJV block quotations, in the narrative frame, and in
speech? The current text and the 1830 first edition are counted separately.

Why: the comparison with Hebrew (genre-ladder) needs the Book of Mormon side
cut the same way the Hebrew side is. The split by bucket is what locates any
difference. The 1830 text matters because later editions removed some uses of
the phrase.

Method:
- Every verse, title page and book superscription is counted (`corpus.load`).
- The genre masks come from `annotations/embedded.tsv` (`bomstylo.spans`).
- The bucket comes from the English rule (`bomstylo.english`), under both the
  revised and the registered versions.
- 1830: every removal found by the alignment (`bomstylo.edition1830`) is
  restored to the verse it was removed from, with its bucket, plus 4 words
  ("it came to pass") to the word count.
- Narrators come from `annotations/records.tsv`.
- Sensitivity: Zeniff's first-person record (Mosiah 9–10) is an embedded span
  of kind `narration`. By default it counts as speech, as in the published
  figures. Counting it as narrative frame instead is reported alongside.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from bomstylo import corpus, edition1830, english, spans, stats
from bomstylo.analysis import Analysis, Headline
from bomstylo.genre import BOM_LEVELS

ANALYSIS = Analysis(
    id="bom-buckets",
    family="wayhi",
    title="Book of Mormon uses by bucket and genre step, current and 1830 texts",
    question="How often does the Book of Mormon use the formula, setting-first vs straight to the "
             "event, at each genre step, in the current and 1830 texts?",
    why="The Book of Mormon side of every comparison, cut the same way as the Hebrew side.",
    label="exploratory",
    corpora=["bom-current", "bom-1830"],
    annotations=["embedded.tsv", "records.tsv"],
)


def levels(verses, lay, extra=None, rule="revised"):
    """Counts and words per genre level. `extra`: restored 1830 uses,
    [(verse index, {rule: bucket key}, added words)]."""
    lv = {k: {"words": 0, "counts": Counter()} for k in BOM_LEVELS}
    add = defaultdict(list)
    for vi, key, w in extra or []:
        add[vi].append((key, w))
    for i, v in enumerate(verses):
        w, c = corpus.words(v.text), english.counts(v.text, rule)
        for key, aw in add.get(i, []):
            c[key[rule]] += 1
            w += aw
        sel = ["whole text"]
        if not lay.quotation[i]:
            sel += ["without KJV quotations", "speech (not KJV)" if lay.embedded[i] else "narrative frame"]
        for s in sel:
            lv[s]["words"] += w
            lv[s]["counts"].update(c)
    return {k: {"words": d["words"], "counts": dict(d["counts"])} for k, d in lv.items()}


def event_share(c: dict, tense: str = "past") -> list:
    e, t = c.get(f"{tense}_event", 0), c.get(f"{tense}_time", 0)
    return [e, e + t, *stats.share_ci(e, e + t)]


def run() -> dict:
    verses = corpus.load("bom")
    lay = spans.layers(verses)
    e1830 = edition1830.align(verses)
    restored = [(r["vi"], r["key"], 4) for r in e1830["removed"]]
    out = {"e1830": e1830}
    for rule in english.RULES:
        out[f"current|{rule}"] = levels(verses, lay, rule=rule)
        out[f"1830|{rule}"] = levels(verses, lay, extra=restored, rule=rule)

    # Narrators, narrative frame, current text.
    att = spans.attribution(verses)
    by = defaultdict(lambda: {r: Counter() for r in english.RULES})
    for i, v in enumerate(verses):
        if lay.quotation[i] or lay.embedded[i]:
            continue
        rec = att.record_at(i) or "(none)"
        for r in english.RULES:
            by[rec][r].update(english.counts(v.text, r))
    out["narrators"] = {rec: {r: {"counts": dict(c), "event_share": event_share(c)} for r, c in d.items()}
                        for rec, d in by.items()}

    # Sensitivity: Zeniff's record as narrative frame.
    lay_z = spans.layers(verses, frame_kinds=("narration",))
    out["sensitivity_zeniff_as_frame"] = {
        "current": levels(verses, lay_z)["narrative frame"],
        "1830": levels(verses, lay_z, extra=restored)["narrative frame"]}

    fr = out["current|revised"]["narrative frame"]["counts"]
    out["event_share"] = {"current": event_share(fr),
                          "1830": event_share(out["1830|revised"]["narrative frame"]["counts"]),
                          "current, registered rule": event_share(
                              out["current|registered"]["narrative frame"]["counts"]),
                          "speech, future": event_share(
                              out["current|revised"]["speech (not KJV)"]["counts"], "future")}
    out["removed_by_bucket"] = dict(Counter(r["key"]["revised"] for r in e1830["removed"]))
    return out


def _rate(d, keys=("past_time", "past_event")):
    return stats.rate(sum(d["counts"].get(k, 0) for k in keys), d["words"])


def headline(d: dict) -> list[Headline]:
    cur, old = d["current|revised"]["narrative frame"], d["1830|revised"]["narrative frame"]
    es = d["event_share"]["current"]
    rem = d["removed_by_bucket"]
    return [
        Headline("frame_rate_current", _rate(cur),
                 text=f"Narrative frame, current text: {_rate(cur):.2f} past-tense uses per 1,000 words "
                      f"({cur['counts']['past_time']} setting-first, {cur['counts']['past_event']} "
                      f"straight to the event, {cur['words']:,} words)."),
        Headline("frame_rate_1830", _rate(old),
                 text=f"Narrative frame, 1830 text: {_rate(old):.2f} per 1,000 words."),
        Headline("frame_event_share", es[2], es[3], es[4],
                 text=f"Straight-to-the-event share, narrative frame, current text: {es[2]:.0%} "
                      f"({es[3]:.0%}–{es[4]:.0%}), {es[0]:,} of {es[1]:,}."),
        Headline("removed_after_1830", len(d["e1830"]["removed"]),
                 text=f"Uses removed after 1830: {len(d['e1830']['removed'])} "
                      f"({rem.get('past_time', 0)} past setting-first, {rem.get('past_event', 0)} past "
                      f"straight-to-event, {rem.get('future_time', 0) + rem.get('future_event', 0)} future); "
                      f"current-text uses not found in the 1830 OCR by the aligner: "
                      f"{d['e1830']['reverse'].get('absent from 1830', 0)} (an earlier hand check found these present "
                      f"but garbled or misaligned; its per-case labels weren't kept)."),
    ]
