"""Verse-level texts: the Book of Mormon and the KJV.

Every verse-structured text is reduced to a flat list of `Verse` records, kept
in `corpora/prepared/<name>.jsonl`. The parsers that build those files from the
raw downloads are here too, and `bomstylo fetch` calls them.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from . import paths


@dataclass
class Verse:
    work: str            # "bom", "kjv_ot", "kjv_nt"
    book: str            # "1 Nephi", "Genesis", ...
    chapter: int
    verse: int
    text: str
    index: int = -1      # position within the work
    kind: str = "verse"  # "verse" | "title_page" | "book_heading"

    @property
    def ref(self) -> str:
        if self.kind != "verse":
            return f"{self.book} [{self.kind}]"
        return f"{self.book} {self.chapter}:{self.verse}"


WORD = re.compile(r"[A-Za-z']+")


def words(text: str) -> int:
    """English word count used for every per-1,000-words rate."""
    return len(WORD.findall(text))


def load(name: str) -> list[Verse]:
    """A prepared verse file: "bom", "kjv_ot" or "kjv_nt"."""
    with paths.prepared(f"{name}.jsonl").open(encoding="utf-8") as fh:
        return [Verse(**json.loads(line)) for line in fh]


def save(verses: list[Verse], dest: Path) -> None:
    with dest.open("w", encoding="utf-8") as fh:
        for v in verses:
            fh.write(json.dumps(asdict(v)) + "\n")


def _finalize(verses: list[Verse]) -> list[Verse]:
    for i, v in enumerate(verses):
        v.index = i
    return verses


# --- Book of Mormon (Project Gutenberg plain text) ------------------------------

# Verse header lines look like "1 Nephi 3:7" on a line of their own. The body
# follows, repeating its verse number, and runs to the next structural marker:
# blank lines can't end a verse, because some verses contain a paragraph break.
_BOM_HEADER = re.compile(r"^([A-Za-z0-9][A-Za-z0-9 ]*?) (\d+):(\d+)$")


def parse_bom(path: Path) -> list[Verse]:
    """Verses plus the title page and the book superscriptions.

    The superscriptions ("An account of Lehi and his wife Sariah...") are part
    of the printed text, not study aids, so they are kept as records with
    `kind` set. The `Book N` / `Chapter N` navigation lines are dropped."""
    lines = [l.strip() for l in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    books = {m.group(1) for l in lines if (m := _BOM_HEADER.match(l))}
    chapter_mark = re.compile(
        rf"^({'|'.join(re.escape(b) for b in books)})\s+\d+$|^(Chapter)\s+\d+$", re.I)

    def classify(line: str):
        if not line:
            return "blank", None
        if m := _BOM_HEADER.match(line):
            return "verse", m
        if m := chapter_mark.match(line):
            return "chapter", m
        if line in books:
            return "book", None
        return "text", None

    verses: list[Verse] = []
    mode: str | None = "heading"
    meta: tuple = ("Title Page", "title_page")
    body: list[str] = []

    def flush():
        if not body or mode is None:
            return
        text = re.sub(r"\s+", " ", " ".join(body)).strip()
        if not text:
            return
        if mode == "verse":
            book, chap, vs = meta
            text = re.sub(rf"^{vs}\s+", "", text)
            verses.append(Verse("bom", book, chap, vs, text))
        else:
            book, kind = meta
            verses.append(Verse("bom", book, 0, 0, text, kind=kind))

    for line in lines:
        what, m = classify(line)
        if what == "blank":
            continue
        if what == "text":
            body.append(line)
            continue
        flush()
        body = []
        if what == "verse":
            mode, meta = "verse", (m.group(1), int(m.group(2)), int(m.group(3)))
        elif what == "book":
            mode, meta = "heading", (line, "book_heading")
        elif m.group(1):
            # "Enos 1": single-chapter books have no bare book line, so their
            # superscription follows the chapter marker instead.
            mode, meta = "heading", (m.group(1), "book_heading")
        else:
            mode, meta = None, ()
    flush()
    return _finalize(verses)


# --- King James Version (Project Gutenberg ebook #10) ---------------------------

GUT_START = "*** START OF THE PROJECT GUTENBERG EBOOK"
GUT_END = "*** END OF THE PROJECT GUTENBERG EBOOK"
_OT_HEADING = "The Old Testament of the King James Version of the Bible"
_NT_HEADING = "The New Testament of the King James Bible"

_KJV_RENAME = {
    "The First Book of Moses: Called Genesis": "Genesis",
    "The Second Book of Moses: Called Exodus": "Exodus",
    "The Third Book of Moses: Called Leviticus": "Leviticus",
    "The Fourth Book of Moses: Called Numbers": "Numbers",
    "The Fifth Book of Moses: Called Deuteronomy": "Deuteronomy",
    "The Book of Joshua": "Joshua",
    "The Book of Judges": "Judges",
    "The Book of Ruth": "Ruth",
    "The First Book of Samuel": "1 Samuel",
    "The Second Book of Samuel": "2 Samuel",
    "The First Book of the Kings": "1 Kings",
    "The Second Book of the Kings": "2 Kings",
    "The First Book of the Chronicles": "1 Chronicles",
    "The Second Book of the Chronicles": "2 Chronicles",
    "The Book of Nehemiah": "Nehemiah",
    "The Book of Esther": "Esther",
    "The Book of Job": "Job",
    "The Book of Psalms": "Psalms",
    "The Proverbs": "Proverbs",
    "The Song of Solomon": "Song of Solomon",
    "The Book of the Prophet Isaiah": "Isaiah",
    "The Book of the Prophet Jeremiah": "Jeremiah",
    "The Lamentations of Jeremiah": "Lamentations",
    "The Book of the Prophet Ezekiel": "Ezekiel",
    "The Book of Daniel": "Daniel",
    "The Gospel According to Saint Matthew": "Matthew",
    "The Gospel According to Saint Mark": "Mark",
    "The Gospel According to Saint Luke": "Luke",
    "The Gospel According to Saint John": "John",
    "The Acts of the Apostles": "Acts",
    "The Epistle of Paul the Apostle to the Romans": "Romans",
    "The First Epistle of Paul the Apostle to the Corinthians": "1 Corinthians",
    "The Second Epistle of Paul the Apostle to the Corinthians": "2 Corinthians",
    "The Epistle of Paul the Apostle to the Galatians": "Galatians",
    "The Epistle of Paul the Apostle to the Ephesians": "Ephesians",
    "The Epistle of Paul the Apostle to the Philippians": "Philippians",
    "The Epistle of Paul the Apostle to the Colossians": "Colossians",
    "The First Epistle of Paul the Apostle to the Thessalonians": "1 Thessalonians",
    "The Second Epistle of Paul the Apostle to the Thessalonians": "2 Thessalonians",
    "The First Epistle of Paul the Apostle to Timothy": "1 Timothy",
    "The Second Epistle of Paul the Apostle to Timothy": "2 Timothy",
    "The Epistle of Paul the Apostle to Titus": "Titus",
    "The Epistle of Paul the Apostle to Philemon": "Philemon",
    "The Epistle of Paul the Apostle to the Hebrews": "Hebrews",
    "The General Epistle of James": "James",
    "The First Epistle General of Peter": "1 Peter",
    "The Second General Epistle of Peter": "2 Peter",
    "The First Epistle General of John": "1 John",
    "The Second Epistle General of John": "2 John",
    "The Third Epistle General of John": "3 John",
    "The General Epistle of Jude": "Jude",
    "The Revelation of Saint John the Divine": "Revelation",
}

_VERSE_MARK = re.compile(r"(?:(?<=\s)|(?<=^))(\d+):(\d+)\s")


def _kjv_split_book(book: str, raw: str, work: str) -> list[Verse]:
    out: list[Verse] = []
    marks = list(_VERSE_MARK.finditer(raw))
    for j, m in enumerate(marks):
        end = marks[j + 1].start() if j + 1 < len(marks) else len(raw)
        text = re.sub(r"\s+", " ", raw[m.end():end]).strip()
        if text:
            out.append(Verse(work, book, int(m.group(1)), int(m.group(2)), text))
    return out


def _kjv_testament(raw: str, work: str, titles: set[str]) -> list[Verse]:
    out: list[Verse] = []
    current: str | None = None
    buf: list[str] = []

    def flush():
        if current and buf:
            out.extend(_kjv_split_book(current, " ".join(buf), work))

    # Samuel and Kings carry an "Otherwise Called:" alternate title that is
    # another book's real title; skip the one title line after that marker.
    skip_next_title = False
    for line in raw.split("\n"):
        s = line.strip()
        if s == "Otherwise Called:":
            skip_next_title = True
        elif s in titles:
            if skip_next_title:
                skip_next_title = False
                continue
            flush()
            current, buf = _KJV_RENAME.get(s, s), []
        elif current and s:
            buf.append(s)
    flush()
    return out


def parse_kjv(path: Path) -> tuple[list[Verse], list[Verse]]:
    """(Old Testament, New Testament) verses from the Gutenberg file."""
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r", "")
    text = text.split(GUT_START, 1)[1].split(GUT_END, 1)[0]
    # The OT heading opens both the table of contents and the text. The table of
    # contents is the authoritative list of book titles for this edition.
    parts = text.split(_OT_HEADING)
    if len(parts) < 3:
        raise ValueError("unexpected KJV layout: could not locate body")
    ot_toc, nt_toc = parts[1].split(_NT_HEADING)
    ot_titles = {l.strip() for l in ot_toc.split("\n") if l.strip()}
    nt_titles = {l.strip() for l in nt_toc.split("\n") if l.strip()}
    if len(ot_titles) != 39 or len(nt_titles) != 27:
        raise ValueError(f"expected 39+27 books, got {len(ot_titles)}+{len(nt_titles)}")
    ot_raw, nt_raw = parts[2].split(_NT_HEADING)
    return (_finalize(_kjv_testament(ot_raw, "kjv_ot", ot_titles)),
            _finalize(_kjv_testament(nt_raw, "kjv_nt", nt_titles)))
