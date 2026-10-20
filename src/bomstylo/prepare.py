"""Preparation steps: raw download → what analyses read in corpora/prepared/.

Each source in the manifest names one step here (`prepare:`). A step reads
`corpora/raw/<id>/` and writes the source's prepared paths. Steps are
deterministic, so `bomstylo verify` can check the output against the pinned
checksums. Each step's docstring is the human description of the
transformation; the report quotes it.
"""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

from . import corpus, genre, paths


def raw(source_id: str, *parts: str) -> Path:
    return paths.RAW.joinpath(source_id, *parts)


def copy_files(src: dict) -> None:
    """None: the files are used exactly as downloaded."""
    for r in src["raw"]:
        if "files" in r:
            sub = r.get("dest", src["prepared"]["paths"][0])
            for name in r["files"]:
                dest = paths.PREPARED / sub / Path(name).name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(raw(src["id"], Path(name).name), dest)
        else:
            dest = paths.PREPARED / r["save_as"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(raw(src["id"], r["save_as"]), dest)


def bom_current(src: dict) -> None:
    """CRLF to LF; keep from the first line "THE BOOK OF MORMON" after the
    Project Gutenberg small print; drop the "TRANSLATED BY JOSEPH SMITH, JUN."
    block through the witness statements (up to the first "1 Nephi" line);
    split into verses, keeping the title page and book superscriptions."""
    lines = raw(src["id"], "mormon13.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("*END*THE SMALL PRINT!"))
    start = next(i for i in range(start, len(lines)) if lines[i].strip() == "THE BOOK OF MORMON")
    lines = lines[start:]
    a = next(i for i, l in enumerate(lines) if l.strip() == "TRANSLATED BY JOSEPH SMITH, JUN.")
    b = next(i for i in range(a, len(lines)) if lines[i].strip() == "1 Nephi")
    tmp = raw(src["id"], "bom_full.txt")
    tmp.write_text("\n".join(lines[:a] + lines[b:]), encoding="utf-8")
    corpus.save(corpus.parse_bom(tmp), paths.PREPARED / "bom.jsonl")


def kjv(src: dict) -> None:
    """Strip the Project Gutenberg header and licence; split into Old and New
    Testament verses, using the edition's own table of contents for book titles."""
    ot, nt = corpus.parse_kjv(raw(src["id"], "pg10.txt"))
    corpus.save(ot, paths.PREPARED / "kjv_ot.jsonl")
    corpus.save(nt, paths.PREPARED / "kjv_nt.jsonl")


def web_codes() -> set[str]:
    return set(genre.NARRATIVE_BOOKS.values()) | set(genre.WEB_CODE_EXTRA.values())


def web(src: dict) -> None:
    """Extract the read-aloud chapter files of the books used (Genesis–Esther,
    Jonah, the Gospels, Acts). The live zip revises the text from time to time;
    `patch` in the manifest restores the pinned wording, line by line."""
    out = paths.PREPARED / "web"
    out.mkdir(parents=True, exist_ok=True)
    codes = web_codes()
    with zipfile.ZipFile(raw(src["id"], "eng-web_readaloud.zip")) as z:
        for name in z.namelist():
            base = Path(name).name
            m = re.match(r"eng-web_\d+_([0-9A-Z]{3})_\d+_read\.txt$", base)
            if m and m.group(1) in codes:
                (out / base).write_bytes(z.read(name))
    for p in src.get("patch", []):
        f = out / p["file"]
        lines = f.read_bytes().split(b"\n")
        old, new = p["live"].encode(), p["pinned"].encode()
        if old not in lines[p["line"] - 1]:
            if new in lines[p["line"] - 1]:
                continue            # the zip already has the pinned wording
            raise ValueError(f"web patch: {p['file']} line {p['line']} has neither wording")
        lines[p["line"] - 1] = lines[p["line"] - 1].replace(old, new)
        f.write_bytes(b"\n".join(lines))


def tla(src: dict) -> None:
    """None: each Hugging Face `train.jsonl` is saved as `<subset>.jsonl`."""
    copy_files(src)


# --- 19th-century pastiches ---------------------------------------------------------
# (archive.org id, label, start line regex, search from line, end regex)
PERIOD_SPECS = {
    "snowden_1793": ("americanrevoluti00snow", "Snowden, American Revolution (1793; 1802 printing)",
                     r"C\s*H\s*A\s*P\.\s*[IL1]\.?\s*$", 380, r"COLUMBIAD|AMERICAN\s+WAR"),
    "napoleon_1809": ("firstbooknapole00gruagoog", "The First Book of Napoleon (1809)",
                      r"^\s*BOOK I\.", 530, r"END OF BOOK I"),
    "nullification_1830": ("bookofnullificat00char", "The Book of Nullification (1830)",
                           r"CHAPTER\s+I\.", 0, None),
}
_HEAD = re.compile(r"^\s*(CHAP|CHAPTER|LECTURE|BOOK|PART|SECTION)\b.*$|^\W*\d*\W*$|"
                   r"^\s*[ivxlcdm\d]+\s+[A-Z][A-Z .,’']+\.?\s*\d*\s*$|^\s*[A-Z][A-Z .,’']{3,}\s*\d*\s*$")
_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")


def _vocab(lexicon: Path) -> set[str]:
    v = {l.split("\t")[0].lower() for l in lexicon.open(encoding="utf-8")}
    for work in ("kjv_ot", "kjv_nt"):
        for x in corpus.load(work):
            v |= set(re.findall(r"[a-z]+", x.text.lower()))
    for x in corpus.load("bom"):
        if x.kind == "verse":
            v |= set(re.findall(r"[a-z]+", x.text.lower()))
    return v


def _long_s(text: str, V: set[str]) -> str:
    """Repair OCR of the long s ('fhall' → 'shall') when the repaired form is a
    word and the original isn't."""
    text = text.replace("ſ", "s")

    def fix(m):
        w = m.group(0)
        lw = w.lower()
        if lw in V or "f" not in lw:
            return w
        idx = [i for i, ch in enumerate(lw) if ch == "f"][:4]
        for mask in range(1, 1 << len(idx)):
            c = list(w)
            for b, i in enumerate(idx):
                if mask >> b & 1:
                    c[i] = "s" if c[i] == "f" else "S"
            if "".join(c).lower() in V:
                return "".join(c)
        return w
    return re.sub(r"[A-Za-z]+", fix, text)


def _kjv_grams() -> set[str]:
    g = set()
    for work in ("kjv_ot", "kjv_nt"):
        for x in corpus.load(work):
            w = re.findall(r"[a-z]+", x.text.lower())
            g |= {" ".join(w[i:i + 6]) for i in range(len(w) - 5)}
    return g


def _period_clean(lines: list[str]) -> str:
    t = "\n".join(l for l in lines if not _HEAD.match(l))
    t = re.sub(r"(\w)[-¬]\s*\n\s*(\w)", r"\1\2", t)          # de-hyphenate across lines
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"(?<![\w,])\d{1,3}\s*\.\s+", " ", t)           # verse numbers "12. "
    t = re.sub(r"\[[^\]]{0,80}\]|\*", " ", t)
    t = re.sub(r"[^\w\s.,;:!?'’\"“”()\-—]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def period(src: dict) -> None:
    """Cut each OCR text to its body (start and end lines in PERIOD_SPECS);
    drop headings and verse numbers, rejoin hyphens; repair the long s in
    Snowden against a vocabulary (Brysbaert concreteness lemmas + KJV + Book of
    Mormon words); split into sentences; drop sentences that are verbatim KJV
    (half or more of their 6-word sequences in the KJV). Needs kjv and
    bom-current prepared first."""
    out = paths.PREPARED / "period"
    out.mkdir(parents=True, exist_ok=True)
    V, G = _vocab(raw(src["id"], "brysbaert_concreteness.txt")), _kjv_grams()
    for key, (ia, label, start, after, end) in PERIOD_SPECS.items():
        lines = raw(src["id"], f"{ia}_djvu.txt").read_text(encoding="utf-8", errors="replace").splitlines()
        s = next(i for i in range(after, len(lines)) if re.search(start, lines[i]))
        e = next((i for i in range(s + 1, len(lines)) if re.search(end, lines[i])), len(lines)) if end else len(lines)
        t = _period_clean(lines[s:e])
        if key == "snowden_1793":
            t = _long_s(t, V)
        units, wc, blk, n = [], 0, 1, 0
        for sent in (x.strip() for x in _SENT.split(t) if len(x.split()) >= 3):
            w = re.findall(r"[a-z]+", sent.lower())
            gr = [" ".join(w[i:i + 6]) for i in range(len(w) - 5)]
            if gr and sum(x in G for x in gr) / len(gr) >= 0.5:
                continue
            n += 1
            units.append({"ref": f"{label.split(',')[0].split(' (')[0]} {blk}:{n}", "text": sent})
            wc += len(sent.split())
            if wc >= 2000:
                blk, wc, n = blk + 1, 0, 0
        with (out / f"{key}.jsonl").open("w", encoding="utf-8") as f:
            for u in units:
                f.write(json.dumps(u, ensure_ascii=False) + "\n")


STEPS = {"bom_current": bom_current, "kjv": kjv, "web": web, "tla": tla, "period": period,
         "copy": copy_files}
