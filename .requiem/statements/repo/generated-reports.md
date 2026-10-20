---
id: generated-reports
namespace: repo
kind: rule
modality: must_not
status: active
tags:
    - repo
provenance:
    type: code-derived
    file: src/bomstylo/report/build.py
    line_range:
        start: 1
        end: 11
    hash: 968f5bce654421813c9fed122dafb59853cf8b469c86deed2244620a498e70fd
created_at: 2026-10-19T14:34:11.715667088Z
relationships:
    - to: principles/reproducible-public-sources
      type: refines
      via: link
---

reports/<family>.md and ANALYSES.md are generated (`bomstylo report <family>`, `bomstylo index`) and are not edited by hand. Fixed prose lives in reports/templates/<family>.md; numbers come from {{v:...}} and {{fragment}} placeholders filled from current results. The builder refuses stale or missing results.
