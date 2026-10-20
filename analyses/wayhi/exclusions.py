"""What the Book of Mormon side excludes, and what it misses.

Question: which Book of Mormon passages run parallel to the KJV, and at which
genre step does each leave the comparison? Does any stay in the narrative frame?

Why: the comparison counts the book's own narration. KJV text inside it
(Isaiah, Malachi, the Sermon on the Mount) would count the KJV's style as the
book's. The exclusion layers are data (`annotations/embedded.tsv`); this
analysis checks them against the texts instead of against memory.

Method: a Book of Mormon verse is a KJV parallel if it shares at least 2
distinct 8-word sequences with KJV verses (sequences found in more than 3 KJV
verses are stock phrases and don't count). Neighbouring parallel verses
(gap ≤ 2) with the same KJV book form one passage. A passage is reported if it
shares at least 6 sequences in all. Each verse is placed in its layer:
`quotation` (out from step 2, "without KJV quotations"), `speech` (out at step
4, "narrative frame"), or `frame` (stays in to the end).
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from bomstylo import corpus, spans
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="exclusions",
    family="wayhi",
    title="KJV parallels in the Book of Mormon, and the step at which each leaves the comparison",
    question="Which Book of Mormon passages run parallel to the KJV, and does any stay in the narrative frame?",
    why="Checks the exclusion annotation against the texts, so no KJV text is counted as the book's narration.",
    label="exploratory",
    corpora=["bom-current", "kjv"],
    annotations=["embedded.tsv"],
    params={"ngram": 8, "stock_phrase_verses": 3, "min_per_verse": 2, "gap": 2, "min_per_passage": 6},
)
STEP = {"quotation": "step 2 (without KJV quotations)", "speech": "step 4 (narrative frame)",
        "frame": "stays in the narrative frame"}


def _words(t: str) -> list[str]:
    return re.findall(r"[a-z]+", t.lower())


def run() -> dict:
    p = ANALYSIS.params
    n = p["ngram"]
    idx = defaultdict(set)
    for v in corpus.load("kjv_ot") + corpus.load("kjv_nt"):
        w = _words(v.text)
        for i in range(len(w) - n + 1):
            idx[" ".join(w[i:i + n])].add((v.book, v.chapter, v.verse))
    bom = corpus.load("bom")
    lay = spans.layers(bom)
    hits = []
    for i, v in enumerate(bom):
        if v.kind != "verse":
            continue
        w = _words(v.text)
        grams = {" ".join(w[j:j + n]) for j in range(len(w) - n + 1)}
        grams = {g for g in grams if g in idx and len(idx[g]) <= p["stock_phrase_verses"]}
        if len(grams) >= p["min_per_verse"]:
            src = Counter((b, c) for g in grams for b, c, _ in idx[g])
            layer = "quotation" if lay.quotation[i] else "speech" if lay.embedded[i] else "frame"
            hits.append({"i": i, "ref": v.ref, "n": len(grams), "kjv": src.most_common(1)[0][0], "layer": layer,
                         "words": corpus.words(v.text)})
    runs: list[list[dict]] = []
    for h in hits:
        if runs and h["i"] - runs[-1][-1]["i"] <= p["gap"] + 1 and h["kjv"][0] == runs[-1][-1]["kjv"][0]:
            runs[-1].append(h)
        else:
            runs.append([h])
    passages = []
    for r in runs:
        if sum(h["n"] for h in r) < p["min_per_passage"]:
            continue
        layers = Counter(h["layer"] for h in r)
        kjv = sorted({h["kjv"] for h in r}, key=lambda x: x[1])
        chs = sorted({c for _, c in kjv})
        passages.append({"bom": f"{r[0]['ref']}–{r[-1]['ref'].split(' ')[-1]}" if len(r) > 1 else r[0]["ref"],
                         "kjv": f"{kjv[0][0]} {chs[0]}" + (f"–{chs[-1]}" if len(chs) > 1 else ""),
                         "verses": len(r), "layers": dict(layers),
                         "leaves_at": STEP[layers.most_common(1)[0][0]],
                         "frame_verses": [h["ref"] for h in r if h["layer"] == "frame"],
                         "frame_words": sum(h["words"] for h in r if h["layer"] == "frame")})
    kinds = Counter(s.kind for s in lay.spans)
    return {"passages": passages, "span_kinds": dict(kinds), "n_spans": len(lay.spans),
            "quotation_spans": [f"{bom[s.start].ref}–{bom[s.end].ref}" for s in lay.spans if s.kind == "quotation"],
            "in_frame": [x for x in passages if x["frame_verses"]]}


def headline(d: dict) -> list[Headline]:
    fr = d["in_frame"]
    return [Headline("parallels_in_frame", len(fr),
                     text=f"{len(d['passages'])} KJV-parallel passages found; {len(fr)} keep verses in the narrative "
                          f"frame: " + "; ".join(f"{x['bom']} ({x['kjv']}, {len(x['frame_verses'])} verse{'s' if len(x['frame_verses']) > 1 else ''}, "
                                                 f"{x['frame_words']} words)" for x in fr) + ".")]
