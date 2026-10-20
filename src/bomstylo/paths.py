"""Where things live. Every other module takes its paths from here."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("BOMSTYLO_ROOT", Path(__file__).resolve().parents[2]))

CORPORA = ROOT / "corpora"
MANIFEST = CORPORA / "manifest.yaml"
RAW = CORPORA / "raw"              # downloads, exactly as served (gitignored)
PREPARED = CORPORA / "prepared"    # what analyses read (gitignored)

ANNOTATIONS = ROOT / "annotations"
PREREGISTRATIONS = ROOT / "preregistrations"
RESULTS = ROOT / "results"
REPORTS = ROOT / "reports"


def prepared(*parts: str) -> Path:
    """Path to a prepared corpus file, with a clear error if it isn't fetched."""
    p = PREPARED.joinpath(*parts)
    if not p.exists():
        raise FileNotFoundError(f"{p.relative_to(ROOT)} is missing; run `uv run bomstylo fetch`")
    return p
