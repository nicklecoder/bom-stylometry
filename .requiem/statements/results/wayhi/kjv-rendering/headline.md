---
id: headline
namespace: results/wayhi/kjv-rendering
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:f5452bc09697
provenance:
    type: code-derived
    file: results/wayhi/kjv-rendering.fingerprint
    line_range:
        start: 1
        end: 1
    hash: 753e19240d9fa4d6139bf0b35224a8ebd8cc19f2240a23db0c8ea8c1a42f04ab
created_at: 2026-10-19T14:34:29.435903724Z
---

KJV rendering of each Hebrew bucket, and calibration of the English rule. Exploratory result. Question: How consistently did the KJV render each kind of wayhi/wehayah as 'came to pass', and how often does the English rule recover the Hebrew bucket?

The KJV renders 84% of setting-first wayhi as 'came to pass' (334 of 396 single-form verses); ordinary-verb wayhi 2.5%; future setting-first wehayah 49%.
KJV past 'it came to pass' with no wayhi in the verse: 31 of 388 (8%).
English rule (revised) agrees with the Hebrew on 331 of 334 rendered past settings (registered rule 302 of 334); future settings 77 of 85.

Recorded values: rendered_setting=0.843434; kjv_additions=31; rule_agreement=0.991018
Change from the previous record: first record.
Data: results/wayhi/kjv-rendering.json (fingerprint sha256:f5452bc09697f798046bca0be7a9d33da24d1bcde1fe0c346287853605520069). Code: analyses/wayhi/kjv_rendering.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run kjv-rendering` and `uv run bomstylo record kjv-rendering`.
