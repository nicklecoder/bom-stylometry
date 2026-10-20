---
id: 1830-false-removals
namespace: methods/wayhi
kind: design
status: active
tags:
    - wayhi
provenance:
    type: code-derived
    file: src/bomstylo/edition1830.py
    line_range:
        start: 28
        end: 29
    hash: f6e8f9419ba71409b421d046db96b40cfa3d315950d68729e5c1083f3c6fa9d0
created_at: 2026-10-19T14:34:12.837740769Z
---

The 1830 aligner reports uses present in the 1830 OCR but absent from the current text. Mosiah 6:2 is a hand-checked false hit (a wording change in Mosiah 5:10 shifts the anchor) and is excluded. The reverse direction (51 current-text uses not found in the 1830 OCR) was hand-checked earlier as OCR damage or misalignment, but per-case labels weren't kept.
