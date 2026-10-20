"""The hand-made layers that say who is speaking where in the Book of Mormon.

`annotations/embedded.tsv` marks embedded material: sermons, epistles,
prophecies, embedded records, and verbatim KJV block quotations (kind
`quotation`). `annotations/records.tsv` marks whose record each stretch
belongs to (Nephi, Jacob, Mormon, Moroni, ...). These layers record what the
book says about itself. They are inputs to the genre controls, not evidence
about authorship.

Every genre step on the Book of Mormon side is defined here, so no analysis
carries its own exclusion list.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from . import paths
from .corpus import Verse

EMBEDDED = paths.ANNOTATIONS / "embedded.tsv"
RECORDS = paths.ANNOTATIONS / "records.tsv"
CONFIDENCE = ("explicit", "inferred", "uncertain")


@dataclass
class Span:
    start_ref: str
    end_ref: str
    layer: str        # "record" (whose book) or "embedded" (quoted material)
    speaker: str
    kind: str         # narration | discourse | epistle | prophecy | allegory | liturgy | quotation
    confidence: str
    note: str = ""
    start: int = -1   # resolved verse indices, inclusive
    end: int = -1

    def contains(self, i: int) -> bool:
        return self.start <= i <= self.end

    @property
    def n_verses(self) -> int:
        return self.end - self.start + 1


class RefIndex:
    """Resolve 'Alma 32:21' (or a chapter, 'Jacob 7') to a verse index."""

    def __init__(self, verses: list[Verse]):
        self._exact: dict[str, int] = {}
        self._first: dict[tuple[str, int], int] = {}
        self._last: dict[tuple[str, int], int] = {}
        for v in verses:
            if v.kind != "verse":
                continue
            self._exact[v.ref] = v.index
            self._first.setdefault((v.book, v.chapter), v.index)
            self._last[(v.book, v.chapter)] = v.index

    def resolve(self, ref: str, end: bool = False) -> int:
        ref = ref.strip()
        if ref in self._exact:
            return self._exact[ref]
        book, _, tail = ref.rpartition(" ")
        if ":" in tail:
            raise KeyError(f"unknown reference: {ref!r}")
        table = self._last if end else self._first
        key = (book, int(tail))
        if key not in table:
            raise KeyError(f"unknown chapter: {ref!r}")
        return table[key]


def load_spans(verses: list[Verse], *files: Path) -> list[Span]:
    idx = RefIndex(verses)
    spans: list[Span] = []
    for p in files:
        with Path(p).open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                if not row.get("start_ref") or row["start_ref"].startswith("#"):
                    continue
                if row["confidence"] not in CONFIDENCE:
                    raise ValueError(f"{p.name}: bad confidence {row['confidence']!r} for {row['start_ref']}")
                s = Span(row["start_ref"], row["end_ref"], row["layer"], row["speaker"],
                         row["kind"], row["confidence"], row.get("note", ""))
                s.start, s.end = idx.resolve(s.start_ref), idx.resolve(s.end_ref, end=True)
                if s.end < s.start:
                    raise ValueError(f"{p.name}: reversed span {s.start_ref}-{s.end_ref}")
                spans.append(s)
    return spans


class Attribution:
    """Which spans cover a verse."""

    def __init__(self, verses: list[Verse], spans: list[Span]):
        self.verses, self.spans = verses, spans
        self.records = [s for s in spans if s.layer == "record"]

    def at(self, i: int) -> list[Span]:
        """All spans covering verse i, outermost first."""
        return sorted((s for s in self.spans if s.contains(i)), key=lambda s: (-s.n_verses, s.start))

    def kind_at(self, i: int) -> str | None:
        """Kind of the innermost span covering verse i."""
        hits = self.at(i)
        return hits[-1].kind if hits else None

    def record_at(self, i: int) -> str | None:
        for s in self.records:
            if s.contains(i):
                return s.speaker
        return None


def attribution(verses: list[Verse]) -> Attribution:
    """Both layers: records and embedded material."""
    return Attribution(verses, load_spans(verses, EMBEDDED, RECORDS))


@dataclass
class Layers:
    """Per-verse genre masks for the Book of Mormon.

    embedded:  inside any embedded span (speech, epistle, prophecy, embedded
               record, quotation). Removed at the narrative-frame step.
    quotation: inside a KJV block quotation (Isaiah, Malachi). Removed from
               the "without KJV quotations" step on.
    """
    embedded: list[bool]
    quotation: list[bool]
    spans: list[Span]


def layers(verses: list[Verse], frame_kinds: tuple[str, ...] = ()) -> Layers:
    """Genre masks. `frame_kinds` lists embedded kinds to count as frame
    instead (the sensitivity check passes ("narration",) for Zeniff's record)."""
    spans = load_spans(verses, EMBEDDED)
    emb, quo = [False] * len(verses), [False] * len(verses)
    for s in spans:
        for i in range(s.start, s.end + 1):
            if 0 <= i < len(verses):
                if s.kind not in frame_kinds:
                    emb[i] = True
                if s.kind == "quotation":
                    quo[i] = True
    return Layers(emb, quo, spans)
