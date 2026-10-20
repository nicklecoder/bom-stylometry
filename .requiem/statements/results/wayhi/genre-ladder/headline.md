---
id: headline
namespace: results/wayhi/genre-ladder
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:0baf9613f408
provenance:
    type: code-derived
    file: results/wayhi/genre-ladder.fingerprint
    line_range:
        start: 1
        end: 1
    hash: 21f0c5be5ea23c1c5386addc54b774551d76f5fd58c35f75ecbe56e2a921ee89
created_at: 2026-10-19T14:34:26.468208982Z
---

Genre ladder: Hebrew setting-first wayhi vs the Book of Mormon. Exploratory result. Question: How does the Book of Mormon's rate compare with Hebrew wayhi at each matched genre step, and which use of the formula carries the difference?

Whole Old Testament vs whole Book of Mormon: 7.3x the Hebrew setting-first wayhi rate (7.9x the KJV's English).
17 Hebrew narrative units vs Book of Mormon narrative frame: 2.7x (2.3-3.1) current text, 2.7x (2.4-3.2) 1830 text, per 1,000 KJV-scale words.
Setting-first uses alone: Book of Mormon 2.34 vs Hebrew 2.92 per 1,000 = 0.80x (0.68-0.95). Hebrew has 0 straight-to-the-event wayhi; the Book of Mormon 775.
Densest Hebrew unit (setting-first): Elijah cycle at 5.81 per 1,000, against the Book of Mormon frame's 7.76.

Recorded values: ratio_whole=7.31097; ratio_matched=2.66098 [2.31724, 3.06541]; setting_ratio=0.80309 [0.67958, 0.950054]; densest_unit=5.80805
Change from the previous record: first record.
Data: results/wayhi/genre-ladder.json (fingerprint sha256:0baf9613f408ccc6afdf763aca321c46831ce0da566831f6d46474cd3c0cc3aa). Code: analyses/wayhi/genre_ladder.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run genre-ladder` and `uv run bomstylo record genre-ladder`.
