"""The genre steps, defined once for both sides.

Each step narrows the comparison the same way on both sides. The ladder is
reported step by step so the effect of each control is visible (constitution
II).

  step  Old Testament side                        Book of Mormon side
  1     whole OT                                  whole text
  2     17 narrative books                        minus KJV block quotations
  3     story books (no Leviticus, Numbers,       minus KJV block quotations
        Deuteronomy)
  4     story books, speech removed               narrative frame
  5     17 named narrative units, speech removed  narrative frame

Speech on the OT side is removed per instance, using the quotation marks of
the World English Bible verse the instance stands in (the KJV marks no speech).
On the Book of Mormon side it is removed by the hand-made span layer
(`spans.py`).
"""
from __future__ import annotations

# OSIS file names of the Westminster Leningrad Codex books, in canonical order.
OSIS_BOOKS = {
    "Gen": "Genesis", "Exod": "Exodus", "Lev": "Leviticus", "Num": "Numbers",
    "Deut": "Deuteronomy", "Josh": "Joshua", "Judg": "Judges", "Ruth": "Ruth",
    "1Sam": "1 Samuel", "2Sam": "2 Samuel", "1Kgs": "1 Kings", "2Kgs": "2 Kings",
    "1Chr": "1 Chronicles", "2Chr": "2 Chronicles", "Ezra": "Ezra",
    "Neh": "Nehemiah", "Esth": "Esther", "Job": "Job", "Ps": "Psalms",
    "Prov": "Proverbs", "Eccl": "Ecclesiastes", "Song": "Song of Solomon",
    "Isa": "Isaiah", "Jer": "Jeremiah", "Lam": "Lamentations", "Ezek": "Ezekiel",
    "Dan": "Daniel", "Hos": "Hosea", "Joel": "Joel", "Amos": "Amos",
    "Obad": "Obadiah", "Jonah": "Jonah", "Mic": "Micah", "Nah": "Nahum",
    "Hab": "Habakkuk", "Zeph": "Zephaniah", "Hag": "Haggai", "Zech": "Zechariah",
    "Mal": "Malachi",
}

# Step 2: the books that carry the OT narrative, with their World English Bible
# file codes.
NARRATIVE_BOOKS = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM",
    "Deuteronomy": "DEU", "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT",
    "1 Samuel": "1SA", "2 Samuel": "2SA", "1 Kings": "1KI", "2 Kings": "2KI",
    "1 Chronicles": "1CH", "2 Chronicles": "2CH", "Ezra": "EZR",
    "Nehemiah": "NEH", "Esther": "EST",
}
# WEB codes needed only for the named units (Jonah) and the Greek analysis.
WEB_CODE_EXTRA = {"Jonah": "JON", "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK",
                  "John": "JHN", "Acts": "ACT"}


def web_code(book: str) -> str | None:
    return NARRATIVE_BOOKS.get(book) or WEB_CODE_EXTRA.get(book)


# Step 3: Leviticus, Numbers and Deuteronomy are mostly law and address inside a
# narrative frame. Including them adds words without adding narrative.
LAW_BOOKS = {"Leviticus", "Deuteronomy", "Numbers"}
STORY_BOOKS = [b for b in NARRATIVE_BOOKS if b not in LAW_BOOKS]

# Step 5: connected narrative blocks as standardly delimited, so the Hebrew side
# is measured on the same kind of material as a narrative history. Whole books
# are too coarse: Genesis has genealogies, Exodus turns into law at chapter 20,
# and Kings is padded with regnal formulae.
#
# Boundaries are chapter-aligned. Some conventional divisions fall mid-chapter
# (the Jacob cycle properly opens at Gen 25:19); chapter alignment lets the
# per-chapter World English Bible files serve for speech removal.
#
# Daniel is left out on purpose. Its court tales are close analogues to Book of
# Mormon narrative, but Daniel 2–7 is Aramaic, where the verb is hwh and no
# wayhi occurs: it would read as a false zero.
HEBREW_UNITS = [
    # (label, book, first chapter, last chapter)
    ("Abraham cycle", "Genesis", 12, 25),
    ("Jacob cycle", "Genesis", 26, 36),
    ("Joseph novella", "Genesis", 37, 50),
    ("Exodus narrative", "Exodus", 1, 19),
    ("Conquest", "Joshua", 1, 12),
    ("Judges tales", "Judges", 3, 16),
    ("Ruth", "Ruth", 1, 4),
    ("Samuel and Saul", "1 Samuel", 1, 15),
    ("Rise of David", "1 Samuel", 16, 31),
    ("Court narrative", "2 Samuel", 9, 20),
    ("Solomon", "1 Kings", 1, 11),
    ("Elijah cycle", "1 Kings", 17, 22),
    ("Elisha cycle", "2 Kings", 2, 13),
    ("Hezekiah narrative", "2 Kings", 18, 20),
    ("Esther", "Esther", 1, 10),
    ("Nehemiah memoir", "Nehemiah", 1, 7),
    ("Jonah", "Jonah", 1, 4),
]


def unit_of_chapter() -> dict[tuple[str, int], str]:
    return {(b, c): lab for lab, b, a, z in HEBREW_UNITS for c in range(a, z + 1)}


# Hebrew-side level names and the Book of Mormon level each is paired with.
BOM_LEVELS = ("whole text", "without KJV quotations", "narrative frame", "speech (not KJV)")
LADDER = [
    ("whole OT", "whole text"),
    ("17 narrative books", "without KJV quotations"),
    ("story books (no Lev/Num/Deut)", "without KJV quotations"),
    ("story books, narrative frame", "narrative frame"),
    ("17 narrative units, narrative frame", "narrative frame"),
]
# The future tense lives in speech on both sides, so it is compared speech to speech.
SPEECH_PAIR = ("story books, speech only", "speech (not KJV)")
