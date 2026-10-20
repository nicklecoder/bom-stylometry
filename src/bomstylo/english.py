"""The English rule: find "it came / shall come to pass" and say what follows it.

Buckets (the same definitions as the Hebrew rule in `hebrew.py`):

  time   a setting comes first: a time phrase ("in the morning"), a temporal
         or conditional clause ("when my father had read", "if ye..."), or a
         relative condition ("whosoever doeth this shall..."). Corresponds to
         Hebrew wayhi / wehayah + setting.
  event  straight to what happened ("that the Jews did mock him"). Hebrew
         wayhi never does this.

Two versions are kept, and both are reported (constitution III):

  registered  PREREGISTRATION_2.md, unchanged. Looks only after the formula,
              at a short list of time words.
  revised     The registered list plus settings that the calibration against
              the Hebrew (and later against the Greek) showed it missing, a
              check for a setting placed just before the formula in the same
              clause, and relative-conditional openings.

History of the revised rule (each change was found by a calibration, and each
changed only the numbers noted):
  2026-10-18  first revision, from the Hebrew calibration (analysis kjv-rendering).
  2026-10-18  the registered pattern was being sliced one character short,
              dropping "the day"; fixed. Added "on a certain [day]", "on
              another [sabbath]", "on one of [those days]", "also on", from the
              Greek calibration (greek-egeneto). Only the KJV New Testament
              event share moved (20% -> 12%); the Book of Mormon never uses
              these phrases.
"""
from __future__ import annotations

import re
from collections import Counter

# requiem: methods/wayhi/english-rule-registered
EN_TIME = re.compile(r"(when|after|as|while|in the|on the|in that|in this|in those|"
                     r"at the|at that|about|before|until|on the morrow|the next|the day)\b")

# requiem: methods/wayhi/english-rule-revised
EN_TIME_REV = re.compile(
    EN_TIME.pattern[:-3] + r"|the same|the selfsame|the (?:first|second|third|fourth|fifth|"
    r"sixth|seventh|eighth|ninth|tenth|next|following)|at (?:midnight|noon|even|evening|night|"
    r"morning)|in process of time|upon a day|on a day|one day|afterwards?|a (?:long |little )?"
    r"(?:time|while|season)|within|in an?|in one|at what time|that night|that day|night|also in|"
    r"since|by the way|on a certain|a certain day|(?:also )?on (?:one|another)|also on)\b")

# Relative-conditional openings are conditions, i.e. settings, as Hebrew
# "wehayah kol motse'i..." ("every one that findeth me shall...") is.
EN_COND = re.compile(r"(whosoever|whoso|whatsoever|every (?:one|soul|man) (?:that|who|which)|"
                     r"all (?:those |they )?(?:that|who|which)|as many as|except|unless)\b")
# A setting placed before the formula in the same clause:
# "After this it came to pass, that David smote..."
EN_BEFORE = re.compile(r"\b(after|when|while|as soon as|in process of time|in the|on the|at the|"
                       r"the same|in those days|in that day|about)\b")

# Amendment 2 of PREREG 2: punctuation after the formula is skipped ("that, when ...").
PAST = re.compile(r"it came to pass[\s,;:]*(that\b)?[\s,;:]*(.{0,40})")
FUT = re.compile(r"it (?:shall|should|will) come to pass[\s,;:]*(that\b)?[\s,;:]*(.{0,40})")

RULES = ("revised", "registered")


def classify(after: str, future: bool = False, before: str = "", rule: str = "revised") -> str:
    """'time' or 'event' for the text after (and, revised only, before) the formula."""
    pat = EN_TIME if rule == "registered" else EN_TIME_REV
    if rule != "registered":
        after = re.sub(r"^saith the [a-z ]+?,\s*(that\b)?[\s,]*", "", after)   # quoting insert
        if EN_COND.match(after):
            return "time"
    if pat.match(after) or (future and re.match(r"if\b", after)):
        return "time"
    if rule != "registered" and EN_BEFORE.search(before):
        return "time"
    return "event"


def clause_before(text: str, start: int) -> str:
    """The clause leading up to position `start` (back to the last stop)."""
    seg = text[max(0, start - 120):start]
    return re.split(r"[.;:?!]", seg)[-1]


def counts(text: str, rule: str = "revised") -> Counter:
    """Counter over past_time, past_event, future_time, future_event."""
    c, t = Counter(), text.lower()
    for m in PAST.finditer(t):
        c["past_" + classify(m.group(2), False, clause_before(t, m.start()), rule)] += 1
    for m in FUT.finditer(t):
        c["future_" + classify(m.group(2), True, clause_before(t, m.start()), rule)] += 1
    return c


def registered_counts(text: str) -> dict[str, int]:
    """PREREG 2's own counter, kept verbatim: past formula only, after-text only."""
    c = Counter()
    for m in PAST.finditer(text.lower()):
        c["time" if EN_TIME.match(m.group(2)) else "event"] += 1
    return dict(c)
