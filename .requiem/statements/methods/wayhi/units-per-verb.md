---
id: units-per-verb
namespace: methods/wayhi
kind: design
status: active
tags:
    - wayhi
provenance:
    type: code-derived
    file: analyses/wayhi/per_verb.py
    line_range:
        start: 1
        end: 1
    hash: f55fd6924e06c7b2e2023915c0f3e128e7978b45f5404719479d838e21de8ebd
created_at: 2026-10-19T14:34:13.642785026Z
relationships:
    - to: principles/like-for-like
      type: refines
      via: link
---

Per 1,000 words is not a shared scale across languages. Every cross-language rate is re-measured per 100 verbs (spaCy for English, morphology for Hebrew and Demotic). Validation: KJV has 1.026 verbs per Hebrew verb in the same passages, but 1.83 words per Hebrew word.
