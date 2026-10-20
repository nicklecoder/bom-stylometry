"""The Hebrew side: wayhi and wehayah in the Westminster Leningrad Codex.

Source: OpenScriptures morphhb, which gives every word a Strong's lemma and a
morphology code. Lemma 1961 is hayah, "to be". Two macro-syntactic forms are
built on it:

  HC/Vqw3ms  wayhi    waw-consecutive imperfect, past narrative:
                      "and it came to pass" / "and it was"
  HC/Vqq3ms  wehayah  sequential perfect, future:
                      "and it shall come to pass" / "and it shall be"

The bucket rule (`classify`) looks at the words right after the form:

  time   a setting follows: a setting word (after, when, as, end, time, if,
         until, before), a time noun after a preposition or numeral, or a
         circumstantial clause (subject + participle, then a main verb later
         in the verse). The narrative-marker use.
  event  a finite verb follows directly. Doesn't occur with wayhi in practice;
         the bucket exists so that the absence is measured, not assumed.
  verb   anything else: wayhi is an ordinary verb with its own subject
         ("and there was light", "and the word of the LORD came"). Excluded
         from the comparison, because "it came to pass" doesn't render it.
"""
from __future__ import annotations

import re
from collections.abc import Iterator

from . import genre, paths

WAYHI, WEHAYAH = "HC/Vqw3ms", "HC/Vqq3ms"
TENSE = {WAYHI: "past", WEHAYAH: "future"}
HAYAH = "1961"

# Setting words: after, when/that (ki), as (asher), end, time, if (im), until, before.
SETTING_WORDS = {"310", "3588", "834", "7093", "6256", "518", "5704", "2962"}
# Time nouns: day, morning, evening, year, month, night, morrow; panah in
# "lifnot boqer" (at the turn of the morning); tequfah and teshuvah ([turn /
# return] of the year).
TIME_NOUNS = {"3117", "1242", "6153", "8141", "2320", "3915", "4283", "6437", "8622", "8666"}


def _num(lemma: str) -> set[str]:
    return set(re.findall(r"\d+", lemma))


# requiem: methods/wayhi/hebrew-rule
def classify(ws: list[tuple[str, str]], i: int) -> str:
    """Bucket for the wayhi / wehayah at ws[i]; ws is the verse as [(lemma, morph)]."""
    nl, nm = ws[i + 1] if i + 1 < len(ws) else ("", "")
    l2, m2 = ws[i + 2] if i + 2 < len(ws) else ("", "")
    if _num(nl) & SETTING_WORDS:
        return "time"
    # A time noun opens a setting after a preposition ("bayyom", "le'et"), or
    # bare only as "hayyom" ("and it fell on a day"). A bare "evening" or "the
    # days of" is a subject: "and there was evening", "the days of Jacob were".
    if _num(nl) & TIME_NOUNS and (nm.startswith("HR") or nl == "d/3117"):
        return "time"
    # l- or a numeral, then a time noun: "lishvat hayyamim", "litqufat hashanah".
    if (nm.startswith("HR") or "/Ac" in nm or nm.startswith("HAc")) and _num(l2) & TIME_NOUNS:
        return "time"
    # Circumstantial clause ("as they were emptying their sacks, behold..."):
    # subject, then a participle without the article (or "before"), then a main
    # verb later in the verse. Without the main verb it's periphrastic ("David
    # was executing justice"), which is the ordinary verb.
    if re.match(r"H(Td/)?(N|P)", nm) and ("2962" in _num(l2) or (
            re.search(r"V\w[rs]", m2) and (not l2.startswith("d/") or "3605" in _num(nl)) and any(
                re.match(r"H(C/)?V\w[pqwi]", m) and HAYAH not in _num(l) for l, m in ws[i + 3:]))):
        return "time"
    if nm.startswith("HR"):
        if re.fullmatch(r"HR/Sp\w+", nm):        # "bo", "lahem": preposition + pronoun only
            return "verb"
        return "verb" if nl.startswith("l") else "time"
    if re.match(r"H(C/)?V[a-zA-Z][pqwi]", nm):     # finite verb straight after
        return "event"
    return "verb"


# PREREG 2's Hebrew rule, kept verbatim for the registered re-run. It sends
# every l- preposition to "verb" before looking for a time word, misses bare
# time nouns, and has a shorter setting list; the revised rule above fixes
# these. Its bucket names are the registered ones.
_PREREG2_TIME = {"310", "3588", "834", "7093", "6256"}


def classify_prereg2(nl: str, nm: str) -> str:
    if nm.startswith("HR"):
        return "verb_use" if nl.startswith("l") else "time"
    if _num(nl) & _PREREG2_TIME:
        return "time"
    if re.match(r"H(C/)?V[a-zA-Z][pqwi]", nm):
        return "event"
    return "verb_use"


def _attr(a: str, n: str) -> str:
    m = re.search(n + r'="([^"]*)"', a)
    return m.group(1) if m else ""


_VERSE = re.compile(r'<verse osisID="[^.]+\.(\d+)\.(\d+)">(.*?)</verse>', re.S)


def verses() -> Iterator[tuple[str, int, int, list[tuple[str, str, str]]]]:
    """(book, chapter, verse, [(lemma, morph, surface)]) over the whole WLC."""
    word = re.compile(r"<w ([^>]*)>([^<]*)</w>")
    for osis, book in genre.OSIS_BOOKS.items():
        xml = paths.prepared("wlc", f"{osis}.xml").read_text(encoding="utf-8")
        for vm in _VERSE.finditer(xml):
            ws = [(_attr(a, "lemma"), _attr(a, "morph"), s) for a, s in word.findall(vm.group(3))]
            yield book, int(vm.group(1)), int(vm.group(2)), ws


def verse_tags(body: str) -> list[tuple[str, str]]:
    """[(lemma, morph)] for every <w> tag, including ones with nested markup."""
    return [(_attr(a, "lemma"), _attr(a, "morph")) for a in re.findall(r"<w ([^>]*)>", body)]


def tagged_verses() -> Iterator[tuple[str, int, int, list[tuple[str, str]]]]:
    """(book, chapter, verse, [(lemma, morph)]) counting every <w ...> tag."""
    for osis, book in genre.OSIS_BOOKS.items():
        xml = paths.prepared("wlc", f"{osis}.xml").read_text(encoding="utf-8")
        for vm in _VERSE.finditer(xml):
            yield book, int(vm.group(1)), int(vm.group(2)), verse_tags(vm.group(3))


def instances() -> list[dict]:
    """Every wayhi and wehayah, with its bucket and its position in the verse."""
    out = []
    for book, ch, vs, ws in tagged_verses():
        for i, (l, m) in enumerate(ws):
            if m not in TENSE or not re.search(r"(^|/)" + HAYAH, l):
                continue
            nl, nm = ws[i + 1] if i + 1 < len(ws) else ("", "")
            out.append({"book": book, "ch": ch, "vs": vs, "pos": i, "n": len(ws),
                        "tense": TENSE[m], "bucket": classify(ws, i),
                        "prereg2": classify_prereg2(nl, nm) if m == WAYHI else None})
    return out
