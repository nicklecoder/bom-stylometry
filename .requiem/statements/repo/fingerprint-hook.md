---
id: fingerprint-hook
namespace: repo
kind: rule
modality: must
status: active
tags:
    - repo
provenance:
    type: code-derived
    file: src/bomstylo/hooks.py
    line_range:
        start: 1
        end: 12
    hash: e92770ad389a4918a528472e9425f2693a0d27c9ecfe0e555530a006060cf2f7
created_at: 2026-10-19T14:34:11.921406908Z
relationships:
    - to: principles/results-in-requiem
      type: refines
      via: link
---

The pre-commit hook (`bomstylo install-hooks`) runs `bomstylo fingerprint --check` and regenerates ANALYSES.md, failing the commit if either is out of date. Requiem staleness reflects the fingerprint file, so a code edit is not seen as stale in Requiem until fingerprints are refreshed (`bomstylo fingerprint`).
