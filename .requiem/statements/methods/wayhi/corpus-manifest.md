---
id: corpus-manifest
namespace: methods/wayhi
kind: decision
status: active
tags:
    - wayhi
    - repo
provenance:
    type: code-derived
    file: corpora/manifest.yaml
    line_range:
        start: 1
        end: 1
    hash: 54d172dcc9a44c29a2cd1dca0fbff2d4b5805ebdae725fa9d755a1aeb656a992
created_at: 2026-10-19T14:34:13.861350247Z
relationships:
    - to: principles/reproducible-public-sources
      type: refines
      via: link
---

Corpora are reproduced by a manifest-driven fetch (pinned URLs + sha256 for raw and prepared files), and report citations are generated from the same manifest. Chosen over citation-only references because it is reproducible.
