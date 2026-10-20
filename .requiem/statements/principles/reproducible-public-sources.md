---
id: reproducible-public-sources
namespace: principles
kind: principle
modality: must
abstract: true
status: active
tags:
    - constitution
provenance:
    type: dialogue
created_at: 2026-10-19T14:34:11.199301411Z
---

Source texts are never committed: corpora/manifest.yaml pins each one (edition, URL, version, licence, sha256) and `bomstylo fetch` reproduces the exact files. Hand-made data (annotations, hand labels) is committed as plain-text tables with a note on how it was made. Every report number comes from a result file; reports are generated, never hand-edited. Each analysis fingerprints its inputs (code, imported shared modules, corpus files, parameters). Constitution IV.
