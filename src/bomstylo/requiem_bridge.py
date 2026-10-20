"""Record an analysis's headline in Requiem (`bomstylo record`).

One statement per analysis, `results/<family>/<id>/headline`, kind `result`:
- body: the question, the label, every headline sentence, a machine-readable
  "Recorded values" line, and how this record compares with the previous one;
- provenance code-derived, anchored to line 1 of the analysis's fingerprint
  file. When any input changes, `bomstylo fingerprint` (the pre-commit hook)
  rewrites that line, and `requiem get` reports the statement `stale: true`.
  So "is this result still current?" is answered from Requiem alone.
- tags: family, label, and `fp:<first 12 hex of the fingerprint>`.

Re-recording after a rerun updates the body and re-anchors the provenance
hash. Requiem has no command for the second step yet, so the bridge rewrites
the `hash:` field in the statement file and runs `requiem reindex`. Nothing is
permanent until `requiem commit`, which is the human approval step; the
bridge never runs it.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess

from . import paths, results
from .analysis import Analysis, Headline

STATEMENTS = paths.ROOT / ".requiem" / "statements"
VALUES = re.compile(r"^Recorded values: (.*)$", re.M)


def _requiem(*args: str) -> dict | list | None:
    p = subprocess.run(["requiem", *args], cwd=paths.ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"requiem {' '.join(args[:2])} failed: {p.stderr.strip()}")
    return json.loads(p.stdout) if p.stdout.strip() else None


def _get(rid: str) -> dict | None:
    p = subprocess.run(["requiem", "get", rid], cwd=paths.ROOT, capture_output=True, text=True)
    return json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else None


def _fmt(h: Headline) -> str:
    s = f"{h.key}={h.value:.6g}"
    if h.low is not None and h.high is not None:
        s += f" [{h.low:.6g}, {h.high:.6g}]"
    return s


def _parse(body: str) -> dict[str, Headline]:
    m = VALUES.search(body or "")
    out = {}
    for part in (m.group(1).split("; ") if m else []):
        mm = re.match(r"(\w+)=([-\d.e+]+|nan|inf)(?: \[([-\d.e+]+), ([-\d.e+]+)\])?$", part)
        if mm:
            k, v, lo, hi = mm.groups()
            out[k] = Headline(k, float(v), float(lo) if lo else None, float(hi) if hi else None)
    return out


def _sans_change(body: str) -> str:
    return "\n".join(l for l in body.split("\n") if not l.startswith("Change from the previous record:"))


def compare(old: dict[str, Headline], new: list[Headline]) -> str:
    """Plain-language change line: what moved, and whether outside the old interval."""
    if not old:
        return "Change from the previous record: first record."
    moved, outside = [], []
    for h in new:
        o = old.get(h.key)
        if o is None:
            moved.append(f"{h.key} new")
        elif f"{o.value:.6g}" != f"{h.value:.6g}":   # compared at the recorded precision
            has_ci = o.low is not None and o.high is not None
            (outside if has_ci and not h.inside(o) else moved).append(f"{h.key} {o.value:.4g}→{h.value:.4g}")
    gone = [k for k in old if k not in {h.key for h in new}]
    if not (moved or outside or gone):
        return "Change from the previous record: none (same values, new inputs)."
    parts = []
    if outside:
        parts.append("OUTSIDE the previous interval (a substantive change; re-read the report): " + ", ".join(outside))
    if moved:
        parts.append("changed, within the previous interval or with none to compare: " + ", ".join(moved))
    if gone:
        parts.append("headlines removed: " + ", ".join(gone))
    return "Change from the previous record: " + "; ".join(parts) + "."


def body(a: Analysis, heads: list[Headline], fp: str, change: str) -> str:
    lines = [f"{a.title}. {a.label.capitalize()} result"
             + (f" ({a.preregistration})" if a.preregistration else "") + f". Question: {a.question}",
             "", *[h.text for h in heads], "",
             f"Recorded values: {'; '.join(_fmt(h) for h in heads)}",
             change,
             f"Data: results/{a.family}/{a.id}.json (fingerprint sha256:{fp}). Code: "
             f"{a.source_path.relative_to(paths.ROOT)}. If `requiem get` shows stale, an input changed: "
             f"run `uv run bomstylo run {a.id}` and `uv run bomstylo record {a.id}`."]
    return "\n".join(lines)


def _reanchor(a: Analysis) -> None:
    """Point the statement's provenance hash at the current fingerprint line
    (Requiem's hash: sha256 of the source lines joined by newlines)."""
    line = a.fingerprint_path.read_text(encoding="utf-8").split("\n")[0]
    h = hashlib.sha256(line.encode()).hexdigest()
    ns, sid = a.requiem_id.rsplit("/", 1)
    f = STATEMENTS / ns / f"{sid}.md"
    text = f.read_text(encoding="utf-8")
    new = re.sub(r"(\n\s+hash: )(?:sha256:)?[0-9a-f]{64}", lambda m: m.group(1) + _hash_prefix(text) + h, text, count=1)
    if new != text:
        f.write_text(new, encoding="utf-8")
        subprocess.run(["git", "add", str(f)], cwd=paths.ROOT, check=True)
        _requiem("reindex")


def _hash_prefix(text: str) -> str:
    return "sha256:" if re.search(r"\n\s+hash: sha256:", text) else ""


def record(a: Analysis) -> str:
    if not a.result_path.exists():
        raise FileNotFoundError(f"{a.id}: no result yet; run `uv run bomstylo run {a.id}`")
    st, changed = results.status(a)
    if st != "current":
        raise RuntimeError(f"{a.id}: result is {st} ({', '.join(changed)}); run it before recording")
    rec = results.load(a)
    heads = [Headline(**h) for h in rec["headline"]]
    fp = rec["fingerprint"]
    existing = _get(a.requiem_id)
    old = _parse(existing.get("body", "")) if existing else {}
    change = compare(old, heads)
    text = body(a, heads, fp, change)
    ns, sid = a.requiem_id.rsplit("/", 1)
    tags = f"{a.family},{a.label},fp:{fp[:12]}"
    if existing is None:
        _requiem("add", "--namespace", ns, "--id", sid, "--kind", "result", "--body", text,
                 "--provenance", "code-derived", "--source",
                 f"{a.fingerprint_path.relative_to(paths.ROOT)}:1-1", "--tags", tags, "--duplicate-ok")
        return f"{a.requiem_id}: recorded. {change}"
    if existing.get("stale") is False and _sans_change(existing.get("body", "")) == _sans_change(text):
        return f"{a.requiem_id}: unchanged"
    _requiem("update", a.requiem_id, "--body", text)
    _reanchor(a)
    _retag(a, tags)
    return f"{a.requiem_id}: updated. {change}"


def _retag(a: Analysis, tags: str) -> None:
    ns, sid = a.requiem_id.rsplit("/", 1)
    f = STATEMENTS / ns / f"{sid}.md"
    text = f.read_text(encoding="utf-8")
    new = re.sub(r"fp:[0-9a-f]{12}", tags.split(",")[-1], text)
    if new != text:
        f.write_text(new, encoding="utf-8")
        subprocess.run(["git", "add", str(f)], cwd=paths.ROOT, check=True)
        _requiem("reindex")
