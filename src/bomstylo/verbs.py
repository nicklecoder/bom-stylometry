"""Verb counts, the language-neutral denominator.

A verb is roughly one clause in any language, so "uses per 100 verbs" compares
Hebrew, English and Demotic without converting word counts between them.

- Hebrew: a word whose morphology tag has a V segment (prefixes included).
- Demotic: TLA's UPOS tag VERB.
- English: spaCy `en_core_web_lg` (optional extra `verbs`). A VERB or AUX that
  heads a predicate counts; auxiliaries attached to another verb don't, and
  the "pass" of "came to pass" doesn't (the formula is one verb, like wayhi).

TLA's VERB tag and the Hebrew V tag aren't validated against each other (no
parallel text); infinitives and participles count as verbs on every side.
"""
from __future__ import annotations

import re
from functools import cache

FORMULA = re.compile(r"\b(?:came|come) to pass\b", re.I)


@cache
def _nlp():
    import spacy
    return spacy.load("en_core_web_lg", disable=["ner", "lemmatizer"])


def english(texts: list[str]) -> list[int]:
    """Predicate-heading verbs per text."""
    out = []
    for t, doc in zip(texts, _nlp().pipe(texts, batch_size=256)):
        n = sum(1 for tok in doc if tok.pos_ in ("VERB", "AUX") and tok.dep_ not in ("aux", "auxpass"))
        out.append(n - len(FORMULA.findall(t)))
    return out


def hebrew(morph: str) -> bool:
    return any(s.startswith("V") for s in morph[1:].split("/"))


def demotic(row: dict) -> int:
    return row["UPOS"].split().count("VERB")
