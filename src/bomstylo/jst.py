"""The Joseph Smith Translation (1867 Inspired Version, archive.org OCR) against the KJV.

Fixed by PREREGISTRATION_30.md (and its Amendment 1): segment the OCR by book,
clean it, align it with the KJV word by word, and mark each JST "it came to
pass" as retained (a KJV formula within 10 aligned tokens) or added.

The segmentation uses line numbers in the OCR file (GENESIS_START, NT_FROM),
so the file is pinned by sha256 in the manifest: a re-OCR breaks it.
"""
from __future__ import annotations

import difflib
import re
from collections import Counter

from . import corpus, english, paths

BOOKS = [
    ("Genesis", r"GENESIS"), ("Exodus", r"EXODUS"), ("Leviticus", r"LEVITICUS"),
    ("Numbers", r"NUMBERS"), ("Deuteronomy", r"DEUTERONOMY"), ("Joshua", r"JOSHUA"),
    ("Judges", r"JUDGES"), ("Ruth", r"RUTH"),
    ("1 Samuel", r"(THE\s+FIRST\s+BOOK\s+OF\s+SAMUEL|I\.\s+SAMUEL)"),
    ("2 Samuel", r"(THE\s+SECOND\s+BOOK\s+OF\s+SAMUEL|(II|11|IL|TI)\.\s+SAMUEL)"),
    ("1 Kings", r"(THE\s+FIRST\s+BOOK\s+OF\s+THE\s+KINGS|I\.\s+KINGS)"),
    ("2 Kings", r"(THE\s+SECOND\s+BOOK\s+OF\s+THE\s+KINGS|(II|11)\.\s+KINGS)"),
    ("1 Chronicles", r"(THE\s+FIRST\s+BOOK\s+OF\s+THE\s+CHRONICLES|I\.\s+CHRONICLES)"),
    ("2 Chronicles", r"(THE\s+SECOND\s+BOOK\s+OF\s+THE\s+CHRONICLES|(II|11)\.\s+CHRONICLES)"),
    ("Ezra", r"EZRA"), ("Nehemiah", r"NEHEMIAH"), ("Esther", r"ESTHER"), ("Job", r"JOB"),
    ("Matthew", r"THE\s+TESTIMONY\s+OF\s+ST\.\s+MATTHEW"), ("Mark", r"ST\.\s+MARK"),
    ("Luke", r"ST\.\s+LUKE"), ("John", r"ST\.\s+JOHN"), ("Acts", r"THE\s+ACTS"),
    ("Romans", r"ROMANS"),
]
PRIMARY = ["Genesis", "Exodus", "Numbers", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
           "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther"]
SECONDARY = ["Matthew", "Mark", "Luke", "John", "Acts"]
GENESIS_START = 298        # Moses 1, printed as the preface to JST Genesis
NT_FROM = 141400           # the NT headers before this line are the contents table
HEADNOTE_LINES = 4         # Amendment 1
TOK = re.compile(r"[a-z']+")
HEADER = re.compile(r"^\s*([A-Z0-9!.'^\\]+\s*){1,8}[.,]?\s*$")     # running heads, page numbers


def segment(lines: list[str]) -> dict[str, tuple[int, int]]:
    starts, pos = {}, 0
    for name, rx in BOOKS:
        if name == "Genesis":
            starts[name] = pos = GENESIS_START
            continue
        if name == "Matthew":
            pos = max(pos, NT_FROM)
        pat = re.compile(r"^\s*" + rx + r"[\s.,]*$")
        for i in range(pos + 1, len(lines)):
            if pat.match(lines[i]):
                starts[name] = pos = i
                break
    order = [b for b, _ in BOOKS if b in starts]
    return {b: (starts[b], starts[order[k + 1]] if k + 1 < len(order) else len(lines))
            for k, b in enumerate(order)}


def clean(block: list[str], headnote_lines: int = HEADNOTE_LINES) -> str:
    """Drop running heads, CHAPTER lines and their italic headnotes; join hyphens.
    Amendment 1: a headnote is at most 4 lines and ends at the first line ending
    in a full stop; verse 1 (opening word in capitals) also ends it."""
    out, in_headnote, hn = [], False, 0
    for ln in block:
        s = ln.strip()
        if not s:
            continue
        if re.match(r"^[CV]?HAPTER\b|^CHAPTER\b", s):
            in_headnote, hn = True, 0
            continue
        if in_headnote:
            if re.match(r"^[A-Z]{2,}\b", s) or hn >= headnote_lines:
                in_headnote = False
            else:
                hn += 1
                if s.endswith("."):
                    in_headnote = False
                continue
        if HEADER.match(s) and not re.search(r"[a-z]", s):
            continue
        out.append(s)
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", "\n".join(out))
    return re.sub(r"\s+", " ", re.sub(r"\b\d+\b", " ", text))


def formulas(text: str, rule: str = "registered") -> list[tuple[int, str]]:
    """(char offset, 'event'|'time') per past 'it came to pass'. "registered" is
    PREREG 2's rule exactly (text after the formula only)."""
    t = text.lower()
    if rule == "registered":
        return [(m.start(), "time" if english.EN_TIME.match(m.group(2)) else "event") for m in english.PAST.finditer(t)]
    return [(m.start(), english.classify(m.group(2), False, english.clause_before(t, m.start()), rule))
            for m in english.PAST.finditer(t)]


def _tokens(text: str) -> list[tuple[str, int]]:
    return [(m.group(), m.start()) for m in TOK.finditer(text.lower())]


def analyse(jst_raw: str, kjv_raw: str, rule: str = "registered") -> dict:
    jt, kt = _tokens(jst_raw), _tokens(kjv_raw)
    jw, kw = [t for t, _ in jt], [t for t, _ in kt]
    ops = difflib.SequenceMatcher(None, jw, kw, autojunk=False).get_opcodes()
    jmap, newcomp = [0] * len(jw), [False] * len(jw)
    for tag, i1, i2, j1, j2 in ops:
        for i in range(i1, i2):
            jmap[i] = j1 + (i - i1) if tag == "equal" else j1
            # "no KJV counterpart": a pure insert, or a replace whose KJV side is
            # under a fifth of the JST side (OCR noise makes pure inserts rare)
            if (i2 - i1) >= 50 and (tag == "insert" or (tag == "replace" and (j2 - j1) * 5 < (i2 - i1))):
                newcomp[i] = True
    kjv_ctp = {i for i in range(len(kw) - 2) if kw[i:i + 3] == ["came", "to", "pass"]}
    off2tok = {off: k for k, (_, off) in enumerate(jt)}
    rows = []
    for off, kind in formulas(jst_raw, rule):
        ti = off2tok.get(off)
        if ti is None:
            continue
        kp = jmap[ti]
        rows.append({"kind": kind, "status": "retained" if any(p in kjv_ctp for p in range(kp - 10, kp + 11)) else "added",
                     "context": "new composition" if newcomp[ti] else "revision", "text": jst_raw[off:off + 90]})
    kmap = [0] * len(kw)
    for tag, i1, i2, j1, j2 in ops:
        for j in range(j1, j2):
            kmap[j] = i1 + (j - j1) if tag == "equal" else i1
    jst_ctp = {i for i in range(len(jw) - 2) if jw[i:i + 3] == ["came", "to", "pass"]}
    removed = sum(1 for j in kjv_ctp
                  if kw[j - 1:j] == ["it"] and not any(p in jst_ctp for p in range(kmap[j] - 10, kmap[j] + 11)))
    return {"jst_words": len(jw), "kjv_words": len(kw), "kjv_formulas": sum(1 for j in kjv_ctp if kw[j - 1:j] == ["it"]),
            "removed": removed, "formulas": rows,
            "match_ratio": sum(i2 - i1 for t, i1, i2, _, _ in ops if t == "equal") / max(1, len(kw))}


def run(rule: str = "registered", headnote_lines: int = HEADNOTE_LINES) -> dict[str, dict]:
    """Per-book alignment for the primary and secondary panels."""
    lines = paths.prepared("jst1867.txt").read_text(encoding="utf-8", errors="replace").splitlines()
    seg = segment(lines)
    kjv = {}
    for work in ("kjv_ot", "kjv_nt"):
        for v in corpus.load(work):
            kjv.setdefault(v.book, []).append(v.text)
    res = {}
    for b in PRIMARY + SECONDARY:
        if b in seg:
            a, z = seg[b]
            res[b] = analyse(clean(lines[a:z], headnote_lines), " ".join(kjv[b]), rule)
            res[b]["lines"] = [a, z]
    return res


def tally(books, res, status=None, context=None) -> Counter:
    c = Counter()
    for b in books:
        for f in res[b]["formulas"]:
            if (status is None or f["status"] == status) and (context is None or f["context"] == context):
                c[f["kind"]] += 1
    return c
