"""The Greek New Testament: SBLGNT with MorphGNT parsing, and ἐγένετο.

Every aorist middle indicative 3sg of γίνομαι (201 in the NT), plus the one
present-tense formula (Mark 2:15, γίνεται), was read in context and labelled
by hand in `annotations/egeneto_labels.tsv`. Unlisted instances are `verb`:
ἐγένετο with its own subject or complement ("there was a calm"), excluded as
the Hebrew ordinary-verb wayhi is. Buckets match the Hebrew rule:

- setting: impersonal ἐγένετο, then a time phrase, ἐν τῷ + infinitive, a
  ὡς/ὅτε clause or a genitive absolute;
- event: impersonal ἐγένετο, then straight to what happened (accusative +
  infinitive: "ἐγένετο δὲ ἀποθανεῖν τὸν πτωχόν", "the beggar died");
- sub: impersonal ἐγένετο + infinitive inside a ὡς/ὅτε clause. Not a
  main-clause formula; reported, not compared.
"""
from __future__ import annotations

import csv
from functools import cache

from . import paths

BOOKS = {"Mt": "Matthew", "Mk": "Mark", "Lk": "Luke", "Jn": "John", "Ac": "Acts"}
FULL = {**BOOKS, "Ro": "Romans", "1Co": "1 Corinthians", "2Co": "2 Corinthians", "1Th": "1 Thessalonians",
        "2Ti": "2 Timothy", "Heb": "Hebrews", "Re": "Revelation"}
BUCKETS = ("setting", "event", "sub", "verb")
LABELS = paths.ANNOTATIONS / "egeneto_labels.tsv"
EXPECTED = 202


@cache
def gnt() -> dict[str, dict[tuple[int, int], list[tuple[str, str, str, str]]]]:
    """{book: {(ch, vs): [(pos, parse, text, lemma)]}} for the whole NT."""
    out = {}
    for f in sorted(paths.prepared("sblgnt").glob("*-morphgnt.txt")):
        d = out.setdefault(f.stem.split("-")[1], {})
        for line in f.open(encoding="utf-8"):
            bcv, pos, parse, text, word, norm, lemma = line.split()
            d.setdefault((int(bcv[2:4]), int(bcv[4:])), []).append((pos, parse, text, lemma))
    return out


def labels() -> dict[str, dict]:
    with LABELS.open(encoding="utf-8") as fh:
        return {r["ref"]: r for r in csv.DictReader(fh, delimiter="\t")}


def instances() -> list[dict]:
    lab = labels()
    present = {r for r, x in lab.items() if x["form"] == "present"}
    out = []
    for b, vv in gnt().items():
        for (ch, vs), ws in vv.items():
            for i, (pos, parse, text, lemma) in enumerate(ws):
                if lemma != "γίνομαι":
                    continue
                ref = f"{b} {ch}:{vs}"
                aorist = parse[:4] == "3AMI" and parse[5] == "S"
                if aorist or (parse[:4] == "3PMI" and ref in present):
                    out.append({"book": b, "ch": ch, "vs": vs, "pos": i, "n": len(ws), "ref": ref,
                                "bucket": lab[ref]["bucket"] if ref in lab else "verb"})
    found = {h["ref"] for h in out}
    if len(out) != EXPECTED or not set(lab) <= found:
        raise ValueError(f"expected {EXPECTED} instances covering every label; got {len(out)}, "
                         f"labels not found: {sorted(set(lab) - found)}")
    return out
