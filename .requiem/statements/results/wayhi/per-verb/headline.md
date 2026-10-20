---
id: headline
namespace: results/wayhi/per-verb
kind: result
status: active
tags:
    - wayhi
    - exploratory
    - fp:c2060ffad677
provenance:
    type: code-derived
    file: results/wayhi/per-verb.fingerprint
    line_range:
        start: 1
        end: 1
    hash: c60bf71be76037789e964c3b0714d2381a200157247b07c7af268b4b5b748892
created_at: 2026-10-19T14:34:28.518309742Z
---

'It came to pass' per verb and per source word. Exploratory result. Question: Do the Hebrew ratio and the additive model survive when the unit is verbs or source words rather than English words?

Per 100 verbs, Book of Mormon ÷ Hebrew = 2.55× (2.2–2.9) current, 2.63× 1830 (2.7× per KJV word).
Validation: KJV has 1.026 verbs per Hebrew verb in the same passages, but 1.83 words per Hebrew word.
Additive model per 100 verbs: 3.60–4.16 against the 1830 book's 5.60.

Recorded values: ratio_per_verb=2.549 [2.22009, 2.93594]; verbs_survive=1.02574; additive_per_verb_max=4.15591
Change from the previous record: changed, within the previous interval or with none to compare: ratio_per_verb 2.548→2.549.
Data: results/wayhi/per-verb.json (fingerprint sha256:c2060ffad677e7378765b7436539bee11089d90b7a1562c1eed7e9ad23b79616). Code: analyses/wayhi/per_verb.py. If `requiem get` shows stale, an input changed: run `uv run bomstylo run per-verb` and `uv run bomstylo record per-verb`.
