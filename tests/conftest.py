"""Shared fixtures. Tests that need prepared corpora skip when they are absent,
so the fast tests run on a fresh clone before `bomstylo fetch`."""
from __future__ import annotations

import json

import pytest

from bomstylo import paths


def result(aid: str) -> dict:
    p = paths.RESULTS / "wayhi" / f"{aid}.json"
    if not p.exists():
        pytest.skip(f"no result for {aid}")
    return json.loads(p.read_text(encoding="utf-8"))["data"]


needs_corpora = pytest.mark.skipif(not (paths.PREPARED / "bom.jsonl").exists(),
                                   reason="prepared corpora not fetched")
