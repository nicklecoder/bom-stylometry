---
id: headline
namespace: results/wayhi/bom-buckets
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:e1f0dbbc663e
provenance:
    type: code-derived
    file: results/wayhi/bom-buckets.fingerprint
    line_range:
        start: 1
        end: 1
    hash: 5112901731f3b402116a3023827b95a83896d1b2ac20843558593932f178651c
created_at: 2026-10-19T14:34:25.765550565Z
---

Book of Mormon uses by bucket and genre step, current and 1830 texts. Exploratory result. Question: How often does the Book of Mormon use the formula, setting-first vs straight to the event, at each genre step, in the current and 1830 texts?

Narrative frame, current text: 7.76 past-tense uses per 1,000 words (336 setting-first, 788 straight to the event, 144,801 words).
Narrative frame, 1830 text: 8.01 per 1,000 words.
Straight-to-the-event share, narrative frame, current text: 70% (67%–73%), 788 of 1,124.
Uses removed after 1830: 42 (12 past setting-first, 30 past straight-to-event, 0 future); current-text uses not found in the 1830 OCR by the aligner: 51 (an earlier hand check found these present but garbled or misaligned; its per-case labels weren't kept).

Recorded values: frame_rate_current=7.76238; frame_rate_1830=8.00971; frame_event_share=0.701068 [0.673359, 0.72772]; removed_after_1830=42
Change from the previous record: changed, within the previous interval or with none to compare: frame_rate_current 7.763→7.762, frame_rate_1830 8.014→8.01, frame_event_share 0.6982→0.7011.
Data: results/wayhi/bom-buckets.json (fingerprint sha256:e1f0dbbc663e2fa39fef61f801f1a087515e568f2518f13971efa4f8dac5dc39). Code: analyses/wayhi/bom_buckets.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run bom-buckets` and `uv run bomstylo record bom-buckets`.
