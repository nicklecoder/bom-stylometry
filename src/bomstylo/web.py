"""Speech on the Bible side, from the World English Bible's quotation marks.

The KJV marks no speech. The World English Bible (public domain, ebible.org
read-aloud edition, one file per chapter) does, with curly double quotes. Each
Hebrew or Greek instance is placed inside or outside speech by its relative
position in the matching WEB verse, and narrative-frame word counts take each
verse's share of words outside quotes and apply it to the KJV's words.
"""
from __future__ import annotations

import re
from functools import cache

from . import genre, paths

_WORD = re.compile(r"[A-Za-z’']+")


@cache
def verses(book: str) -> dict[tuple[int, int], tuple[str, list[tuple[int, int]], int, int]]:
    """{(ch, vs): (text, [(start, end) speech spans], words outside, words total)}."""
    code = genre.web_code(book)
    out = {}
    for f in sorted(paths.prepared("web").glob(f"eng-web_*_{code}_*_read.txt")):
        ch = int(f.stem.split("_")[-2])
        lines = f.read_text(encoding="utf-8-sig").split("\n")
        start = next(k for k, l in enumerate(lines) if re.match(r"^Chapter \d", l.strip())) + 1
        lines = [l for l in lines[start:] if l.strip()]
        inside = False   # WEB double quotes don't nest; a re-opened paragraph stays inside
        for vs, line in enumerate(lines, 1):
            spans, s0 = [], (0 if inside else None)
            for k, c in enumerate(line):
                if c == "“" and not inside:
                    inside, s0 = True, k
                elif c == "”" and inside:
                    inside = False
                    spans.append((s0, k))
            if inside:
                spans.append((s0, len(line)))
            tot = len(_WORD.findall(line))
            q = sum(len(_WORD.findall(line[a:b])) for a, b in spans)
            out[(ch, vs)] = (line, spans, tot - q, tot)
    return out


def in_speech(book: str, ch: int, vs: int, pos: int, n: int) -> bool | None:
    """Is word `pos` of `n` in a source verse inside quotation marks in the WEB?
    None if the WEB has no such verse (versification differences)."""
    v = verses(book).get((ch, vs))
    if v is None:
        return None
    line, spans = v[0], v[1]
    k = int(len(line) * pos / max(n, 1))      # same relative place in the English verse
    return any(a <= k <= b for a, b in spans) if pos else any(a == 0 for a, _ in spans)


def frame_share(book: str, ch: int, vs: int) -> float:
    """Share of the verse's words outside quotation marks (1.0 if unaligned)."""
    v = verses(book).get((ch, vs))
    return (v[2] / v[3]) if v and v[3] else 1.0


def narration_share(book: str, first: int | None = None, last: int | None = None) -> float | None:
    """Share of words outside quotation marks over whole chapters (the older,
    per-chapter method used by `published-claims`; quotes may nest here)."""
    code = genre.web_code(book)
    if code is None:
        return None
    files = sorted(paths.prepared("web").glob(f"eng-web_*_{code}_*_read.txt"))
    if first is not None:
        wanted = {f"{c:02d}" for c in range(first, last + 1)}
        files = [f for f in files if f.stem.split("_")[-2] in wanted]
    if not files:
        return None
    inside = outside = 0
    for f in files:
        text = f.read_text(encoding="utf-8-sig")
        text = "\n".join(l for l in text.split("\n") if not re.match(r"^(Chapter \d|The .*Book)", l.strip()))
        depth, buf, quoted, plain = 0, [], [], []
        for ch in text:
            if ch == "“":
                (quoted if depth else plain).append("".join(buf))
                buf, depth = [], depth + 1
            elif ch == "”":
                quoted.append("".join(buf))
                buf, depth = [], max(0, depth - 1)
            else:
                buf.append(ch)
        (quoted if depth else plain).append("".join(buf))
        inside += sum(len(_WORD.findall(s)) for s in quoted)
        outside += sum(len(_WORD.findall(s)) for s in plain)
    return outside / (inside + outside) if inside + outside else None
