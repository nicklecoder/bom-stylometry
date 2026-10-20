---
id: headline
namespace: results/wayhi/bom-buckets
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:08cea6e295d4
provenance:
    type: code-derived
    file: results/wayhi/bom-buckets.fingerprint
    line_range:
        start: 1
        end: 1
    hash: c48b06ebe32a1c80e53bf0e3beaae6df891e8d2fce2e8beaf4ced264b03f5f2f
created_at: 2026-10-19T14:34:25.765550565Z
---

Book of Mormon uses by bucket and genre step, current and 1830 texts. Exploratory result. Question: How often does the Book of Mormon use the formula, setting-first vs straight to the event, at each genre step, in the current and 1830 texts?

Narrative frame, current text: 7.76 past-tense uses per 1,000 words (335 setting-first, 775 straight to the event, 142,980 words).
Narrative frame, 1830 text: 8.01 per 1,000 words.
Straight-to-the-event share, narrative frame, current text: 70% (67%–73%), 775 of 1,110.
Uses removed after 1830: 42 (12 past setting-first, 30 past straight-to-event, 0 future); current-text uses not found in the 1830 OCR by the aligner: 51 (an earlier hand check found these present but garbled or misaligned; its per-case labels weren't kept).

Recorded values: frame_rate_current=7.76332; frame_rate_1830=8.01381; frame_event_share=0.698198 [0.670243, 0.725098]; removed_after_1830=42
Change from the previous record: none (same values, new inputs).
Data: results/wayhi/bom-buckets.json (fingerprint sha256:08cea6e295d4738d08c5c1eef086b4770ae368860ee0b7d364ebd35b998c9759). Code: analyses/wayhi/bom_buckets.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run bom-buckets` and `uv run bomstylo record bom-buckets`.
