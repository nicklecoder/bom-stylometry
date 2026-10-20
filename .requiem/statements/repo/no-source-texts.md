---
id: no-source-texts
namespace: repo
kind: rule
modality: must_not
status: active
tags:
    - repo
provenance:
    type: code-derived
    file: .gitignore
    line_range:
        start: 1
        end: 3
    hash: 19ecc10788d4fd0aa5b9bc1e27add480757eb8d72f5c8591e2382f5f9f16046e
created_at: 2026-10-19T14:34:11.501069358Z
relationships:
    - to: principles/reproducible-public-sources
      type: refines
      via: link
---

Nothing under corpora/raw/ or corpora/prepared/ is committed (both are gitignored). Corpus provenance is one style only: a manifest-driven fetch with pinned URLs and sha256, from which the report's citations are also generated.
