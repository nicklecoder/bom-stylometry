"""The Egyptian side: narrative particles and Demotic ḫpr.

Two sources:
- AED-TEI (`simondschweitzer/aed-tei`): whole named texts, every word with a
  Thesaurus Linguae Aegyptiae lemma id.
- TLA open sentence subsets (Hugging Face): single sentences with
  transliteration, lemmas, UPOS tags, date range and a German translation.
  There are no text names, so narrative sentences are selected by rule.

Comparability (constitution II): an Egyptian rate counts for or against the
book only against a text matched in genre (connected narrative) and date
(about 600–500 BC or earlier; older is fine, since formal Egyptian kept the
older literary register and Saite scribes revived it). Each text below carries
its date, genre and register, and match flags.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from functools import cache

from . import paths

# --- the old narrative particles ---------------------------------------------------
# The two unambiguous clause-opening narrative particles: they mark the next
# event in a sequence ("then he did X"). Other candidates (khr, kheper, ist) are
# also common verbs or prepositions and can't be separated by lemma id alone.
# Counting these is a floor: a text that chains events another way reads as zero
# (Wenamun uses the Late Egyptian continuative iw=f hr sdm instead).
MARKERS = {"40111": "ꜥḥꜥ.n", "650007": "wn.ꞽn"}

TLA_SETS = {"Earlier Egyptian": "Earlier_Egyptian.jsonl", "Late Egyptian": "Late_Egyptian.jsonl",
            "Demotic": "Demotic.jsonl"}

# Named connected-narrative texts in AED-TEI.
# (id, title, period, kind, genre, approx. date of composition)
NAMED_TEXTS = [
    ("JIPPXMXOTNCQDIKJIQVYWMKOWU", "Sinuhe (pBerlin 3022, B)", "Middle Egyptian", "literary",
     "literary tale", "c. 1900 BC"),
    ("QUFWZTEPLRE4NHKCPAJXGSAOSQ", "Shipwrecked Sailor", "Middle Egyptian", "literary", "literary tale",
     "c. 1900 BC"),
    ("J4EXGHLCL5DR7JHSPDWTVEKMDY", "Tales of pWestcar", "Middle Egyptian", "literary", "literary tales",
     "c. 1600 BC"),
    ("PVLMEE7Y45FPXBSMF47T6PNPEE", "Eloquent Peasant (B1)", "Middle Egyptian", "literary",
     "literary tale with speeches", "c. 1850 BC"),
    ("QKN2PJK4CVGI7GXJSMMPTIZZYY", "Herdsman's Tale", "Middle Egyptian", "literary", "literary tale",
     "c. 1800 BC"),
    ("BMVO6CBMDNBQFMXW3DSIW66WSM", "Carnarvon Tablet I (Kamose)", "Middle Egyptian", "historical",
     "royal campaign narrative", "c. 1550 BC"),
    ("65XN4FHYGNH4FE6V6UEXOT6ZK4", "Kamose Stela I", "Middle Egyptian", "historical",
     "royal campaign narrative", "c. 1550 BC"),
    ("SXQSUAMQH5F2HORTAGXSEWEUGM", "Kamose Stela II", "Middle Egyptian", "historical",
     "royal campaign narrative", "c. 1550 BC"),
    ("C6HNRC4K7FAYBHNDS3LV24EANI", "Tale of Two Brothers", "Late Egyptian", "literary", "literary tale",
     "c. 1200 BC"),
    ("W25WDE27ZVAFXBDULVGJH7CHUQ", "Contendings of Horus and Seth", "Late Egyptian", "literary",
     "literary tale", "c. 1150 BC"),
    ("MTBRL3MIIJDKXAOF2336WRLMZA", "The Doomed Prince", "Late Egyptian", "literary", "literary tale",
     "c. 1300 BC"),
    ("SSS2W6HDXFA23OBG2ER6DYGGCY", "The Taking of Joppa", "Late Egyptian", "literary", "literary tale",
     "c. 1250 BC"),
    ("5UEPUHOXE5CCRF5VQGC4V7SQWQ", "Truth and Falsehood", "Late Egyptian", "literary", "literary tale",
     "c. 1250 BC"),
    ("IAE36426UNFSJHISJPKBZGSUSY", "Astarte and the Sea", "Late Egyptian", "literary", "literary tale",
     "c. 1400 BC"),
    ("HSPTIJABEREHFI6HCEUABYSFGE", "Report of Wenamun", "Late Egyptian", "historical",
     "first-person travel report", "c. 1050 BC"),
    ("4VLZLA44UVGJZN22WIWP774LOQ", "Bentresh Stela", "Late Egyptian", "historical",
     "temple legend in royal style", "c. 400 BC (set in Ramesside times)"),
    ("66ATQAWY55BNBFZYHSRGQK5RG4", "Piye Victory Stela", "Late Period", "historical",
     "royal campaign narrative", "c. 727 BC"),
]

# Hieroglyphic royal inscriptions of the 25th–26th dynasties (the Saite check).
# The large Saite narrative stelae (Nitocris, Psamtik II, Amasis) are not in
# the open data; only these are.
HIEROGLYPHIC = {
    "66ATQAWY55BNBFZYHSRGQK5RG4": "Piye Victory Stela (c. 727 BC)",
    "UZ5MMW4I2ZDQNEKTJK6TQFEQR4": "Taharqa flood stela, Cairo JE 48400 (c. 680 BC)",
    "WMNPTFRPMBBOXJVPXEQK5HGCZ4": "Taharqa stela Cairo JE 36861, lower text",
    "XSMWRMUR4NB6XEXIJVRVHJK2R4": "Banishment stela of Aspelta(?) (c. 600 BC)",
    "JM6ARFU6XZDABK7JONHLOCD5EQ": "Stela of Aryamani",
}
# Translation words per Egyptian token, Late Egyptian aggregate (measured in
# the TLA subset; used to put token counts on an approximate English scale).
EXPANSION_HIEROGLYPHIC = 1.47
MIN_TOKENS = 500   # below this a per-text rate is noise: reported, not pooled


def aed(tid: str) -> str:
    return paths.prepared("aed", f"{tid}.xml").read_text(encoding="utf-8")


@cache
def tla(name: str) -> list[dict]:
    with paths.prepared("tla", TLA_SETS[name]).open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh]


def subset_rates(before: int = -200) -> dict:
    """Marker rates in each TLA subset, sentences dated up to `before`.
    Gives each period's translation-words-per-token expansion."""
    out = {}
    for label in TLA_SETS:
        tokens = translated = sentences = 0
        hits = Counter()
        for row in tla(label):
            date = row.get("dateNotAfter") or row.get("dateNotBefore")
            try:
                date = int(date)
            except (TypeError, ValueError):
                continue
            if date > before:
                continue
            sentences += 1
            lemmas = (row.get("lemmatization") or "").split()
            tokens += len(lemmas)
            translated += len(re.findall(r"[A-Za-zÀ-ÿ]+", row.get("translation") or ""))
            for t in lemmas:
                lid = t.split("|", 1)[0]
                if lid in MARKERS:
                    hits[MARKERS[lid]] += 1
        total = sum(hits.values())
        out[label] = {"sentences": sentences, "lemma_tokens": tokens, "translated_words": translated,
                      "markers": dict(hits), "total": total,
                      "expansion": translated / tokens if tokens else 0.0,
                      "per1k_tokens": 1000 * total / tokens if tokens else 0.0,
                      "per1k_translated": 1000 * total / translated if translated else 0.0}
    return out


def named_rates(expansion: dict[str, float]) -> dict:
    """Old-particle rates per named text, per 1,000 estimated translation words."""
    word_re = re.compile(r'<w [^>]*lemmaRef="tla:tla(\d+)"')
    date_re = re.compile(r'not(Before|After)="(-?\d+)"')
    texts = {}
    for tid, title, period, kind, genre, date in NAMED_TEXTS:
        head, _, body = aed(tid).partition("<body>")
        tokens, hits = 0, Counter()
        for m in word_re.finditer(body):
            tokens += 1
            if m.group(1) in MARKERS:
                hits[MARKERS[m.group(1)]] += 1
        dates = [int(v) for _, v in date_re.findall(head)]
        total = sum(hits.values())
        factor = expansion.get(period) or expansion.get("Late Egyptian") or 1.5
        texts[title] = {"id": tid, "period": period, "kind": kind, "genre": genre, "composed": date,
                        "tokens": tokens, "markers": dict(hits), "total": total,
                        "manuscript_date_earliest": min(dates) if dates else None,
                        "manuscript_date_latest": max(dates) if dates else None,
                        "per1k_tokens": 1000 * total / tokens if tokens else 0.0,
                        "per1k_translated": 1000 * total / (tokens * factor) if tokens else 0.0,
                        "expansion_used": factor, "below_floor": tokens < MIN_TOKENS}
    groups = {}
    for label, sel in (("Middle Egyptian narrative", "Middle Egyptian"), ("Late Egyptian narrative", "Late Egyptian"),
                       ("Late Period narrative", "Late Period"), ("all named narrative texts", None)):
        rows = [t for t in texts.values() if (sel is None or t["period"] == sel) and not t["below_floor"]]
        if rows:
            tok, tot = sum(r["tokens"] for r in rows), sum(r["total"] for r in rows)
            trans = sum(r["tokens"] * r["expansion_used"] for r in rows)
            groups[label] = {"n_texts": len(rows), "tokens": tok, "total": tot,
                             "per1k_tokens": 1000 * tot / tok, "per1k_translated": 1000 * tot / trans}
    return {"texts": texts, "groups": groups, "min_tokens": MIN_TOKENS}


# --- Demotic ḫpr ("it came to pass that...") --------------------------------------------
# TLA Demotic sentences carry no text names, so narrative sentences are chosen
# from the German translation: a 3rd-person preterite storytelling verb and no
# quotation marks. "strict" also drops sentences with 1st/2nd-person pronouns.
HPR_INIT = re.compile(r"^(ḫpr\b|ḫpr=|ḫpr =)")
HPR_FORMULA_DE = re.compile(r"[Ee]s geschah|ereignete sich|begab sich|geschah es|[Ee]ines Tages")
PRETERITE_DE = re.compile(
    r"\b(sprach|sprachen|kam|kamen|ging|gingen|sagte|sagten|fand|fanden|sah|sahen|nahm|nahmen|tat|taten|"
    r"war|waren|rief|riefen|gab|gaben|stand|standen|brachte|brachten|machte|machten|ließ|ließen|hörte|"
    r"hörten|fuhr|fuhren|kehrte|kehrten|antwortete|antworteten|schickte|schickten|setzte|setzten|wurde|"
    r"wurden|lief|liefen|trat|traten|zog|zogen|legte|legten|blieb|blieben|erreichte|fragte|fragten|tötete|"
    r"starb|weinte|öffnete|fiel|fielen)\b")
FIRST_SECOND_DE = re.compile(r"\b(ich|wir|du|ihr|mich|mir|uns|dich|dir|euch|Ich|Wir|Du|Ihr)\b")
# Setting-first vs straight to the event, read from the German translation.
HPR_TIME_DE = re.compile(r"Eines Tages|\b[Aa]ls\b|[Nn]achher|[Dd]anach|Morgen|Zeit|Tag\b|[Ee]inmal")


def demotic_narrative(r: dict, strict: bool) -> bool:
    t = r["translation"]
    if any(q in t for q in '"„“'):
        return False
    if not PRETERITE_DE.search(HPR_FORMULA_DE.sub("", t)):   # the formula itself never qualifies a sentence
        return False
    return not (strict and FIRST_SECOND_DE.search(t))


def demotic_year(r: dict) -> int | None:
    v = r["dateNotBefore"]
    return int(v) if v.lstrip("-").isdigit() else None


def demotic_selections() -> dict[str, list[dict]]:
    """The four narrative selections: loose/strict x all dates / 700–300 BC."""
    rows = tla("Demotic")
    out = {}
    for strict in (False, True):
        for dn, ds in (("all dates", lambda r: True),
                       ("700–300 BC", lambda r: demotic_year(r) is not None and -700 <= demotic_year(r) < -300)):
            out[f"demotic {'strict' if strict else 'loose'}, {dn}"] = [
                r for r in rows if demotic_narrative(r, strict) and ds(r)]
    return out


# pRylands 9 (Petition of Peteese; G. Vittmann, Der demotische Papyrus Rylands 9,
# 1998): written c. 513 BC, narrating events from Psamtik I on. Selected as the
# TLA Demotic sentences dated 525–501 BC. Both "it came to pass" openings are
# counted: bare ḫpr and ꞽ.ꞽr=s-ḫpr (the ancestor of Coptic ⲁⲥϣⲱⲡⲉ).
RYLANDS_DATES = ("-525", "-501")
RYLANDS_OPEN = re.compile(r"^(?:ḫpr\b|ḫpr=|ḫpr =|ꞽ\.ꞽr\s*=\s*s\s*-?\s*ḫpr)")
QUOTE = re.compile(r'["„“”]')
RYLANDS_TIME_DE = re.compile(r"Eines Tages|\b[Aa]ls\b|[Nn]achher|[Dd]anach|Morgen|Abend\b|Zeit|Tag\b|[Ee]inmal|"
                             r"[Nn]achdem|Jahr")


def rylands() -> list[dict]:
    return [r for r in tla("Demotic") if (r["dateNotBefore"], r["dateNotAfter"]) == RYLANDS_DATES]


def rylands_time_first(r: dict) -> bool:
    return bool(RYLANDS_TIME_DE.match(r["translation"]) or re.match(r"Am |Da kam|Als", r["translation"]))
