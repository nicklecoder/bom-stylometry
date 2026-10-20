---
id: headline
namespace: results/wayhi/event-shares
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:660531ccd4aa
provenance:
    type: code-derived
    file: results/wayhi/event-shares.fingerprint
    line_range:
        start: 1
        end: 1
    hash: 7184673bcf5b3f508324a51dfae547a97d1e956242855a0b7a7a6e0302fd7e75
created_at: 2026-10-19T14:34:27.695815224Z
---

Event-first share in English comparison texts, the JST, Moses and Abraham. Exploratory result. Question: Do English texts in biblical style reach the Book of Mormon's event-first share and rate?

Pastiche event-first shares (revised rule): Snowden 43% of 113, First Book of Napoleon 77% of 13, The Late War 29% of 77, Book of Nullification 38% of 16; rates 0.65–2.10 per 1,000 words, at most a third of the Book of Mormon's.
KJV Old Testament: 4% event-first (14/388); New Testament 12%.
JST additions, revised rule, boundary-corrected: 38/47 event-first (81%); formulas kept from the KJV 5%.
Abraham (claims an Egyptian source) 15/16 event-first at 2.91 per 1,000; Moses 34/43 at 3.42. Fisher p = 0.26: no difference.

Recorded values: pastiche_max_share=0.769231; kjv_ot_share=0.0360825; jst_added_share=0.808511 [0.667403, 0.908508]; abraham_vs_moses_p=0.259219
Change from the previous record: first record.
Data: results/wayhi/event-shares.json (fingerprint sha256:660531ccd4aa49e3e6a9f1a3bf99d089a163644a925f03bc81c94c6af1293cd9). Code: analyses/wayhi/event_shares.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run event-shares` and `uv run bomstylo record event-shares`.
