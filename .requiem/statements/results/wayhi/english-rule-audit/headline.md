---
id: headline
namespace: results/wayhi/english-rule-audit
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:229ef35b2450
provenance:
    type: code-derived
    file: results/wayhi/english-rule-audit.fingerprint
    line_range:
        start: 1
        end: 1
    hash: d60987de7be59961adcf0f5abd02c7672107e2d95faf46ea548caba251c9aa2a
created_at: 2026-10-19T14:34:27.382533801Z
---

English rule vs hand labels, 120 Book of Mormon cases. Exploratory result. Question: How often does the English rule agree with a hand reading of Book of Mormon instances?

English rule vs hand labels on 120 Book of Mormon cases: revised rule agrees on 119 (95%-100%), registered rule on 119. Disagreements (revised): Alma 49:28.

Recorded values: agreement_revised=0.991667 [0.954444, 0.999789]
Change from the previous record: first record.
Data: results/wayhi/english-rule-audit.json (fingerprint sha256:229ef35b24508314fba2ae001f341446f88f9fe681c61279dcf43f90ab343adf). Code: analyses/wayhi/english_rule_audit.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run english-rule-audit` and `uv run bomstylo record english-rule-audit`.
