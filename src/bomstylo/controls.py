"""English comparison texts: pseudo-biblical pastiche written without the Book of Mormon.

- *The Late War* (Gilbert J. Hunt, 1816/1819), "in the ancient historical
  style". Only an uncorrected OCR scan exists, so it is cleaned here: page
  furniture, headings and OCR junk out; line-break hyphens rejoined; leading
  verse numbers stripped.
- Snowden, *American Revolution* (1793); *The First Book of Napoleon* (1809);
  *The Book of Nullification* (1830). Prepared from archive.org OCR into
  verse-like units (see `corpora/manifest.yaml`).
"""
from __future__ import annotations

import json
import re
import unicodedata

from . import paths

LATE_WAR_START = "it came to pass, in the one thousand eight"   # the scan drops the drop-cap N of "NOW"
PERIOD = {"Snowden, American Revolution (1793)": "snowden_1793.jsonl",
          "First Book of Napoleon (1809)": "napoleon_1809.jsonl",
          "Book of Nullification (1830)": "nullification_1830.jsonl"}

_HEADING = re.compile(r"^\s*(chapter|chap\.?|book|volume|vol\.|part|act|scene|contents|"
                      r"illustrations?|preface|introduction|appendix|index|footnote|transcriber)\b", re.I)
_BOILERPLATE = re.compile(r"(project gutenberg|digitized by|internet archive|google book|funding from|"
                          r"university of|all rights reserved|printed by|published by|copyright|etext|ebook)", re.I)
_NUMERAL_ONLY = re.compile(r"^\s*[\dIVXLCDMivxlcdm]+\s*[.\-]?\s*$")
_LEADING_VERSE_NO = re.compile(r"^\s*\d{1,3}\s*[.)]\s+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = (text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
            .replace("—", " -- ").replace("–", "-").replace("_", " "))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip()


def _junk(text: str, min_words=10, max_digit=0.05, min_alpha=0.72, max_upper=0.50) -> bool:
    """Thresholds loosened for 1819 letterpress OCR, which never reaches clean-text ratios."""
    if len(text.split()) < min_words or _HEADING.match(text) or _BOILERPLATE.search(text) \
            or _NUMERAL_ONLY.match(text):
        return True
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return True
    if sum(c.isdigit() for c in chars) / len(chars) > max_digit or sum(c.isalpha() for c in chars) / len(chars) < min_alpha:
        return True
    letters = [c for c in chars if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) / len(letters) > max_upper


def late_war() -> list[str]:
    """Cleaned paragraphs of The Late War."""
    text = paths.prepared("late_war.txt").read_text(encoding="utf-8", errors="replace").replace("\r", "")
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    norm = [normalize(p) for p in paras if len(p.split()) >= 5]
    key = normalize(LATE_WAR_START).lower()
    lo = next((i for i, t in enumerate(norm) if key in t.lower()), 0)
    out = []
    for t in norm[lo:]:
        t = _LEADING_VERSE_NO.sub("", re.sub(r"([a-z])-\s+([a-z])", r"\1\2", t))
        if not _junk(t):
            out.append(t)
    return out


def period(name: str) -> str:
    with paths.prepared("period", PERIOD[name]).open(encoding="utf-8") as fh:
        return " ".join(json.loads(l).get("text", "") for l in fh)
