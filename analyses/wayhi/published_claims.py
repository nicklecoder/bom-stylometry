"""The published figures, checked against the texts.

Question: do the counts most often cited for "and it came to pass" reproduce
from the texts? And how often does the phrase occur in the passages the same
literature names?

The figures are those of Donald W. Parry, "I Have a Question", *Ensign* 22/12
(December 1992), 28–30, repeated in ch. 21 of Parry, *Preserved in
Translation* (BYU Religious Studies Center / Deseret Book, 2020):
- *wayhi* about 1,204 times in the Hebrew Bible;
- "came to pass" 727 times in the KJV Old Testament;
- 1,404 times in the Book of Mormon;
- 1,494 in the original text (credited to Royal Skousen).

Neither publication names the forms counted or the concordance used, so each
figure is set beside the measured count. hebrew-forms gives the counting rules
that could produce 1,204.

Why: later analyses replace these numbers, so the report has to show where
they come from and how far they are off, and with what counting rule they would
reproduce.
"""
from __future__ import annotations

import re

from bomstylo import corpus, results
from bomstylo.analysis import Analysis, Headline

ANALYSIS = Analysis(
    id="published-claims",
    family="wayhi",
    title="Published figures vs measured counts",
    question="Do the published counts (Parry 1992/2020) reproduce from the texts?",
    why="Shows where the familiar numbers come from before the comparison replaces them.",
    label="exploratory",
    corpora=["kjv", "bom-current"],
    depends=["hebrew-forms"],
    params={"parry": {"wayhi_in_hebrew_bible": 1204, "came_to_pass_in_kjv_ot": 727,
                      "book_of_mormon": 1404, "original_text": 1494}},
)

# Passages the same literature names as places the phrase is scarce if its
# distribution follows the narrative, tested on its own examples.
NAMED_PASSAGES = {
    "Psalm of Nephi (2 Ne 4:16-35)": ("2 Nephi", 4, 4, 16, 35),
    "King Benjamin (Mosiah 2-5)": ("Mosiah", 2, 5, None, None),
    "Abinadi (Mosiah 12-16)": ("Mosiah", 12, 16, None, None),
    "Alma 5": ("Alma", 5, 5, None, None),
    "Alma 32-34": ("Alma", 32, 34, None, None),
    "Jesus (3 Nephi 11-18)": ("3 Nephi", 11, 18, None, None),
    "Moroni 7-10": ("Moroni", 7, 10, None, None),
    "Alma war chapters (43-62)": ("Alma", 43, 62, None, None),
    "1 Nephi (whole book)": ("1 Nephi", None, None, None, None),
    "Ether (whole book)": ("Ether", None, None, None, None),
}


def run() -> dict:
    bom, ot, nt = corpus.load("bom"), corpus.load("kjv_ot"), corpus.load("kjv_nt")
    ott = " ".join(v.text for v in ot).lower()
    ntt = " ".join(v.text for v in nt).lower()
    bt = " ".join(v.text for v in bom).lower()
    measured = {
        "kjv_ot_came_to_pass": len(re.findall(r"came to pass", ott)),
        "kjv_ot_it_came_to_pass": len(re.findall(r"it came to pass", ott)),
        "kjv_ot_come_to_pass_any": len(re.findall(r"\b(?:came|come|cometh) to pass", ott)),
        "kjv_nt_came_to_pass": len(re.findall(r"came to pass", ntt)),
        "kjv_whole_come_to_pass_any": len(re.findall(r"\b(?:came|come|cometh) to pass", ott + " " + ntt)),
        "bom_it_came_to_pass": len(re.findall(r"it came to pass", bt)),
        "bom_it_shall_come_to_pass": len(re.findall(r"it shall come to pass", bt)),
    }
    hf = results.data("hebrew-forms")["counting_rules"]
    p = ANALYSIS.params["parry"]
    checks = [
        {"claim": "wayhi in the Hebrew Bible", "published": p["wayhi_in_hebrew_bible"],
         "measured": hf["wayhi only (morphology)"],
         "note": f"unpointed ויהי + והיה = {hf['unpointed ויהי + unpointed והיה']:,}"},
        {"claim": "'came to pass' in the KJV Old Testament", "published": p["came_to_pass_in_kjv_ot"],
         "measured": measured["kjv_ot_came_to_pass"],
         "note": f"{measured['kjv_ot_come_to_pass_any']} with 'come to pass'; "
                 f"{measured['kjv_whole_come_to_pass_any']} in the whole KJV, any tense"},
        {"claim": "'it came to pass' in the Book of Mormon", "published": p["book_of_mormon"],
         "measured": measured["bom_it_came_to_pass"], "note": "current text"},
        {"claim": "in the original text", "published": p["original_text"], "measured": None,
         "note": "manuscript-level count; outside this check (see bom-buckets for the 1830 edition)"},
    ]
    named = {}
    for label, (book, c1, c2, v1, v2) in NAMED_PASSAGES.items():
        sel = [v for v in bom if v.book == book and (c1 is None or c1 <= v.chapter <= c2)
               and (v1 is None or v1 <= v.verse <= v2)]
        w = sum(corpus.words(v.text) for v in sel)
        n = sum(len(re.findall(r"it came to pass", v.text.lower())) for v in sel)
        named[label] = {"words": w, "phrase": n, "per1k": 1000 * n / w if w else 0.0}
    return {"measured": measured, "checks": checks, "named_passages": named}


def headline(d: dict) -> list[Headline]:
    wayhi, kjv, bom = (x["measured"] for x in d["checks"][:3])
    return [Headline("parry_check", wayhi,
                     text=f"Published vs measured: wayhi 1,204 vs {wayhi:,}; KJV Old Testament 'came to pass' "
                          f"727 vs {kjv:,}; Book of Mormon 1,404 vs {bom:,}.")]
