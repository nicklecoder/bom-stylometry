"""The 1830 first edition, aligned to the current text.

Source: the archive.org OCR of a University of Pittsburgh copy
(`bookofmormonacco1830smit`). Every "came / come to pass" in the 1830 text
is located in the current text by matching the words that follow it. The
question asked of each is: does the current text still have the phrase there?
The reverse pass asks the same of every current-text instance, to find any the
1830 text lacks.

Hand-checked: one false hit (Mosiah 6:2), where a later wording change in
Mosiah 5:10 moves the anchor and makes the phrase look removed when it isn't.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from . import english, paths
from .corpus import Verse

# OCR-tolerant matchers for "came / come", "to", "pass".
COME = re.compile(r"^c\w{1,2}me$")
TO = re.compile(r"^t\w$")
PASS = re.compile(r"^p\w{1,2}s$")
K = 6           # anchor length, in words
TRIES = 6       # anchors tried, sliding forward over the following words
WINDOW = 0.04   # positional prior: a match must lie within 4% of the expected place
# requiem: methods/wayhi/1830-false-removals
FALSE_REMOVALS = {"Mosiah 6:2"}


def toks(text: str) -> list[str]:
    text = re.sub(r"-\s*\n\s*", "", text)
    return re.findall(r"[a-z]+", text.lower())


def _is_phrase(w, i):
    return i + 2 < len(w) and COME.match(w[i]) and TO.match(w[i + 1]) and PASS.match(w[i + 2])


def _grams(seq):
    g = defaultdict(list)
    for j in range(len(seq) - K):
        g[tuple(seq[j:j + K])].append(j)
    return g


def _align(src, dst, gdst, i, exp):
    after = src[i + 3:i + 3 + K + TRIES + 1]
    if after[:1] == ["that"]:
        after = after[1:]
    hit = None
    for s in range(TRIES):
        for j in gdst.get(tuple(after[s:s + K]), []):
            if abs(j - exp) <= WINDOW * len(dst) and (hit is None or abs(j - exp) < abs(hit[0] - exp)):
                hit = (j, s)
        if hit:
            break
    return None if hit is None else hit[0] - hit[1]


def align(verses: list[Verse]) -> dict:
    """Removals (in 1830, gone now) and additions (now, absent in 1830)."""
    old = toks(paths.prepared("bom1830.txt").read_text(encoding="utf-8", errors="replace"))
    new, vidx = [], []
    for v in verses:
        for t in toks(v.text):
            new.append(t)
            vidx.append(v.index)
    gnew, gold = _grams(new), _grams(old)
    new_set = {j for j in range(len(new)) if _is_phrase(new, j)}
    old_set = {i for i in range(len(old)) if _is_phrase(old, i)}
    scale = len(new) / len(old)

    removed, status, last = [], Counter(), None
    for i in sorted(old_set):
        exp = (last[1] + (i - last[0]) * scale) if last else i * scale
        j = _align(old, new, gnew, i, exp)
        if j is None:
            status["unmatched (OCR)"] += 1
            continue
        last = (i, j)
        if any(k in new_set for k in range(j - 12, j)):
            status["present"] += 1
            continue
        v = verses[vidx[min(j, len(vidx) - 1)]]
        if f"{v.book} {v.chapter}:{v.verse}" in FALSE_REMOVALS:
            status["present"] += 1
            continue
        status["removed"] += 1
        tense = "future" if old[i][1] == "o" or re.match(r"(shall|should|will)", old[i - 1]) else "past"
        follow = re.sub(r"^that\s+", "", " ".join(old[i + 3:i + 13]))
        before = " ".join(old[i - 7:i - 1])
        key = {r: f"{tense}_{english.classify(follow, tense == 'future', before, r)}" for r in english.RULES}
        removed.append({"vi": v.index, "ref": f"{v.book} {v.chapter}:{v.verse}", "key": key,
                        "old": " ".join(old[i - 2:i + 12]), "new": " ".join(new[max(0, j - 10):j + 6])})

    added, rstatus, last = [], Counter(), None
    for j in sorted(new_set):
        exp = (last[1] + (j - last[0]) / scale) if last else j / scale
        i = _align(new, old, gold, j, exp)
        if i is None:
            rstatus["unmatched"] += 1
            continue
        last = (j, i)
        if any(k in old_set for k in range(i - 14, i)):
            rstatus["present in 1830"] += 1
        else:
            rstatus["absent from 1830"] += 1
            v = verses[vidx[j]]
            added.append({"ref": f"{v.book} {v.chapter}:{v.verse}",
                          "new": " ".join(new[j - 3:j + 10]), "old": " ".join(old[max(0, i - 12):i + 4])})
    return {"old_total": len(old_set), "new_total": len(new_set), "status": dict(status),
            "removed": removed, "reverse": dict(rstatus), "added": added}
