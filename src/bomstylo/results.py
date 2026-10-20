"""Result files and input fingerprints.

`results/<family>/<id>.json` holds an analysis's output, the fingerprint of
the inputs it was computed from, and its headline numbers.
`results/<family>/<id>.fingerprint` is one line, `sha256:<hex>`, holding the
fingerprint of the inputs as they are now. Requiem anchors each result
statement to that line, so `requiem get` reports `stale: true` as soon as
the fingerprint file is refreshed after an input changes.

A fingerprint covers, each hashed separately so `status` can say what moved:
  code:<path>        the analysis module
  lib:<path>         every bomstylo module it imports, transitively
  corpus:<id>        the pinned prepared-file hashes in corpora/manifest.yaml
  annotation:<name>  each hand-made file it reads
  depends:<id>       the data of each result it reads
  params             its declared parameters
  env                the pinned versions of the numeric libraries it relies on
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import paths
from .analysis import Analysis, Headline


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _json(o: Any) -> str:
    return json.dumps(o, sort_keys=True, ensure_ascii=False, default=_coerce)


def _coerce(o):
    if hasattr(o, "tolist"):
        return o.tolist()
    if hasattr(o, "item"):
        return o.item()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(f"not JSON serialisable: {type(o)}")


# --- which bomstylo modules an analysis uses -----------------------------------
def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = set()
    pkg = "bomstylo"
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level and path.parent.name == pkg:          # from . import x / from .x import y
                base = node.module or ""
                if base:
                    out.add(f"{pkg}.{base}")
                else:
                    out.update(f"{pkg}.{a.name}" for a in node.names)
            elif node.module and node.module.split(".")[0] == pkg:
                if node.module == pkg:
                    out.update(f"{pkg}.{a.name}" for a in node.names)
                else:
                    out.add(node.module)
        elif isinstance(node, ast.Import):
            out.update(a.name for a in node.names if a.name.split(".")[0] == pkg)
    return out


def _module_file(mod: str) -> Path | None:
    p = paths.ROOT / "src" / Path(*mod.split("."))
    for cand in (p.with_suffix(".py"), p / "__init__.py"):
        if cand.exists():
            return cand
    return None


def lib_closure(path: Path) -> list[Path]:
    """Every bomstylo source file reachable by imports from `path`."""
    seen: dict[str, Path] = {}
    todo = list(_imports(path))
    while todo:
        m = todo.pop()
        if m in seen:
            continue
        f = _module_file(m)
        if f is None:
            continue
        seen[m] = f
        todo.extend(_imports(f))
    return sorted(seen.values())


# --- pinned environment ------------------------------------------------------------
def _pins(extra: bool) -> list[str]:
    text = (paths.ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pins = re.findall(r'"((?:numpy|scipy)==[^"]+)"', text)
    if extra:
        pins += re.findall(r'"((?:spacy==|en_core_web_lg @ )[^"]+)"', text)
    return sorted(pins)


def manifest() -> dict:
    import yaml
    return yaml.safe_load(paths.MANIFEST.read_text(encoding="utf-8"))


def inputs(a: Analysis) -> dict[str, str]:
    """Component hashes of an analysis's current inputs."""
    comp: dict[str, str] = {}
    comp[f"code:{a.source_path.relative_to(paths.ROOT)}"] = sha_file(a.source_path)
    for f in lib_closure(a.source_path):
        comp[f"lib:{f.relative_to(paths.ROOT)}"] = sha_file(f)
    sources = {s["id"]: s for s in manifest()["sources"]}
    for cid in a.corpora:
        if cid not in sources:
            raise KeyError(f"{a.id}: corpus {cid!r} is not in corpora/manifest.yaml")
        comp[f"corpus:{cid}"] = sha(_json(sources[cid].get("prepared", {})).encode())
    for name in a.annotations:
        comp[f"annotation:{name}"] = sha_file(paths.ANNOTATIONS / name)
    for d in a.depends:
        from .analysis import registry
        dep = registry()[d]
        comp[f"depends:{d}"] = (sha(_json(load(dep)["data"]).encode())
                                if dep.result_path.exists() else "missing")
    if a.preregistration:
        comp[f"preregistration:{a.preregistration}"] = sha_file(paths.PREREGISTRATIONS / a.preregistration)
    comp["params"] = sha(_json(a.params).encode())
    comp["env"] = sha(_json(_pins(a.needs_verbs)).encode())
    return comp


def fingerprint(comp: dict[str, str]) -> str:
    return sha(_json(comp).encode())


def write_fingerprint(a: Analysis) -> tuple[str, dict[str, str]]:
    comp = inputs(a)
    fp = fingerprint(comp)
    a.fingerprint_path.parent.mkdir(parents=True, exist_ok=True)
    a.fingerprint_path.write_text(f"sha256:{fp}\n", encoding="utf-8")
    return fp, comp


# --- result files --------------------------------------------------------------------
def save(a: Analysis, data: dict, heads: list[Headline], comp: dict[str, str]) -> Path:
    rec = {
        "id": a.id, "family": a.family, "title": a.title, "label": a.label,
        "question": a.question,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fingerprint": fingerprint(comp), "inputs": comp, "params": a.params,
        "headline": [h.__dict__ for h in heads],
        "data": data,
    }
    a.result_path.parent.mkdir(parents=True, exist_ok=True)
    a.result_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False, default=_coerce) + "\n",
                             encoding="utf-8")
    return a.result_path


def load(a: Analysis | str) -> dict:
    if isinstance(a, str):
        from .analysis import registry
        a = registry()[a]
    return json.loads(a.result_path.read_text(encoding="utf-8"))


def data(analysis_id: str) -> dict:
    """The data block of another analysis's result (declare it in `depends`)."""
    return load(analysis_id)["data"]


def status(a: Analysis) -> tuple[str, list[str]]:
    """('current' | 'stale' | 'missing', [changed input components])."""
    if not a.result_path.exists():
        return "missing", []
    old = load(a)["inputs"]
    new = inputs(a)
    changed = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
    return ("stale" if changed else "current"), changed
