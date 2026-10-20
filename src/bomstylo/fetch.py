"""`bomstylo fetch`: download each source, check it, prepare it, verify it.

For each source in `corpora/manifest.yaml`, in file order:
1. download every `raw:` entry into `corpora/raw/<id>/` (skipped if already
   there, unless --force). An entry is either one file (`url`, or `urls` tried
   in order, saved as `save_as`, checked against `sha256`), or many files from
   a `url_template` filled with each name in `files` (checked afterwards
   through the prepared checksums, since they're used unchanged);
2. run the source's `prepare:` step (`bomstylo.prepare`);
3. check the prepared files against `corpora/checksums/<id>.sha256`.

A mismatch stops with the source id and file. It means the upstream text
changed: see the manifest entry's notes before re-pinning anything.
"""
from __future__ import annotations

import hashlib
import sys
import time
import urllib.request
from pathlib import Path

from . import checksums, paths, prepare, results

UA = "bom-stylometry/0.1 (reproducibility fetch; +https://github.com/)"


def _get(url: str, dest: Path, tries: int = 3) -> None:
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return
        except OSError as e:
            if k == tries - 1:
                raise RuntimeError(f"download failed: {url}: {e}") from e
            time.sleep(2 * (k + 1))


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def download(src: dict, force: bool) -> list[str]:
    probs = []
    for r in src.get("raw", []):
        if "url_template" in r:
            for name in r["files"]:
                dest = prepare.raw(src["id"], Path(name).name)
                if force or not dest.exists():
                    _get(r["url_template"].format(file=name), dest)
            continue
        dest = prepare.raw(src["id"], r["save_as"])
        if force or not dest.exists():
            for k, url in enumerate(r.get("urls") or [r["url"]]):
                try:
                    _get(url, dest)
                except RuntimeError:
                    if k == len(r.get("urls") or [r["url"]]) - 1:
                        raise
                    continue
                if "sha256" not in r or _sha(dest) == r["sha256"]:
                    break
        if "sha256" in r and _sha(dest) != r["sha256"]:
            probs.append(f"{src['id']}: {r['save_as']} has sha256 {_sha(dest)}, pinned {r['sha256']}")
    return probs


def main(ids: list[str] | None = None, force: bool = False) -> None:
    sources = results.manifest()["sources"]
    unknown = set(ids or []) - {s["id"] for s in sources}
    if unknown:
        sys.exit(f"unknown source: {', '.join(sorted(unknown))}")
    failed = False
    for src in sources:
        if ids and src["id"] not in ids:
            continue
        print(f"{src['id']}: downloading")
        probs = download(src, force)
        if probs:
            print("\n".join("  " + p for p in probs))
            failed = True
            continue
        print(f"{src['id']}: preparing ({src['prepare']})")
        prepare.STEPS[src["prepare"]](src)
        probs = checksums.verify(src)
        print("\n".join("  " + p for p in probs) if probs else f"{src['id']}: verified")
        failed |= bool(probs)
    if failed:
        sys.exit("some sources did not match their pins; nothing downstream of them can be trusted")
