---
id: headline
namespace: results/wayhi/genre-ladder
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:aa8a7d75317f
provenance:
    type: code-derived
    file: results/wayhi/genre-ladder.fingerprint
    line_range:
        start: 1
        end: 1
    hash: 5e307550805038c1dbc8bbd852a7be6b4e08b8c70ce436fb59f2f2b4345d1b11
created_at: 2026-10-19T14:34:26.468208982Z
---

Genre ladder: Hebrew setting-first wayhi vs the Book of Mormon. Exploratory result. Question: How does the Book of Mormon's rate compare with Hebrew wayhi at each matched genre step, and which use of the formula carries the difference?

Whole Old Testament vs whole Book of Mormon: 7.3x the Hebrew setting-first wayhi rate (7.9x the KJV's English).
17 Hebrew narrative units vs Book of Mormon narrative frame: 2.7x (2.3-3.1) current text, 2.7x (2.4-3.2) 1830 text, per 1,000 KJV-scale words.
Setting-first uses alone: Book of Mormon 2.32 vs Hebrew 2.92 per 1,000 = 0.80x (0.67-0.94). Hebrew has 0 straight-to-the-event wayhi; the Book of Mormon 788.
Densest Hebrew unit (setting-first): Elijah cycle at 5.81 per 1,000, against the Book of Mormon frame's 7.76.

Recorded values: ratio_whole=7.31097; ratio_matched=2.66066 [2.31734, 3.06455]; setting_ratio=0.795357 [0.673113, 0.940808]; densest_unit=5.80805
Change from the previous record: changed, within the previous interval or with none to compare: ratio_matched 2.661→2.661, setting_ratio 0.8031→0.7954.
Data: results/wayhi/genre-ladder.json (fingerprint sha256:aa8a7d75317f20317bbbb4f11537723b2b0ed5b907e7c7ff5ae7284280f2da8c). Code: analyses/wayhi/genre_ladder.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run genre-ladder` and `uv run bomstylo record genre-ladder`.
