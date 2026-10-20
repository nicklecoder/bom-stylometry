"""The Pearl of Great Price (bcbooks/scriptures-json): Moses and Abraham by chapter."""
from __future__ import annotations

import json
from functools import cache

from . import paths


@cache
def _books() -> dict:
    d = json.loads(paths.prepared("pgp.json").read_text(encoding="utf-8"))
    return {b["book"]: {c["chapter"]: [v["text"] for v in c["verses"]] for c in b["chapters"]} for b in d["books"]}


def text(book: str, chapters: list[int] | None = None) -> str:
    chs = _books()[book]
    return " ".join(t for c in (chapters or sorted(chs)) for t in chs[c])
