"""Checksums of prepared corpus files.

Each source in `corpora/manifest.yaml` names its prepared paths (a file or a
directory). `corpora/checksums/<id>.sha256` lists every prepared file with its
hash, in `sha256sum` format, so `sha256sum -c` works too. The manifest carries
one digest per source: the sha256 of that checksum file. That digest is what
analysis fingerprints use, so fingerprints can be computed without the corpora
present.
"""
from __future__ import annotations

from pathlib import Path

from . import paths
from .results import sha, sha_file

CHECKSUMS = paths.CORPORA / "checksums"


def files_for(source: dict) -> list[Path]:
    out = []
    for p in source["prepared"]["paths"]:
        full = paths.PREPARED / p
        if full.is_dir():
            out += sorted(f for f in full.rglob("*") if f.is_file())
        else:
            out.append(full)
    return out


def listing(source: dict) -> str:
    lines = [f"{sha_file(f)}  {f.relative_to(paths.PREPARED).as_posix()}" for f in files_for(source)]
    return "\n".join(lines) + "\n"


def write(source: dict) -> str:
    """Write the checksum file for a source from what is on disk; return its digest."""
    CHECKSUMS.mkdir(parents=True, exist_ok=True)
    text = listing(source)
    (CHECKSUMS / f"{source['id']}.sha256").write_text(text, encoding="utf-8")
    return sha(text.encode())


def verify(source: dict) -> list[str]:
    """Problems with the prepared files of a source (empty if all match)."""
    want_file = CHECKSUMS / f"{source['id']}.sha256"
    if not want_file.exists():
        return [f"{source['id']}: no checksum file"]
    want = want_file.read_text(encoding="utf-8")
    probs = []
    if sha(want.encode()) != source["prepared"]["digest"]:
        probs.append(f"{source['id']}: checksum file doesn't match the manifest digest")
    expected = dict(reversed(l.split("  ", 1)) for l in want.splitlines() if l)
    for rel, h in expected.items():
        f = paths.PREPARED / rel
        if not f.exists():
            probs.append(f"{source['id']}: missing {rel}")
        elif sha_file(f) != h:
            probs.append(f"{source['id']}: {rel} has sha256 {sha_file(f)}, expected {h}")
    return probs
