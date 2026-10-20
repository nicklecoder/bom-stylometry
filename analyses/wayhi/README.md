# The *wayhi* family: "and it came to pass"

Each module here answers one question. Its docstring says what the question is,
why it is asked, what it reads, how it measures and whether it is `registered`
or `exploratory`. The generated catalogue with inputs and status is in
[`ANALYSES.md`](../../ANALYSES.md); the results are in
[`reports/wayhi.md`](../../reports/wayhi.md).

## Reading order

The questions build on each other. A reviewer new to the family can read them
in this order:

| step | analysis | what it settles |
|---|---|---|
| 1 | [`published_claims.py`](published_claims.py) | Do the published counts (Parry: 1,204 *wayhi*; KJV 727; Book of Mormon 1,404) reproduce from the texts? |
| 2 | [`hebrew_forms.py`](hebrew_forms.py) | What exactly is being counted on the Hebrew side: every "and + *hayah*" form, and *wayhi* split into setting-first, straight-to-event and ordinary-verb uses. |
| 3 | [`kjv_rendering.py`](kjv_rendering.py) | Which Hebrew uses the KJV renders as "came to pass", and how well the English rule recovers the Hebrew bucket (the calibration). |
| 4 | [`english_rule_audit.py`](english_rule_audit.py) | The same English rule against 120 hand-read Book of Mormon cases. |
| 5 | [`exclusions.py`](exclusions.py) | Which Book of Mormon passages parallel the KJV, and at which genre step each leaves the comparison. |
| 6 | [`bom_buckets.py`](bom_buckets.py) | The Book of Mormon by bucket and genre step, current text and 1830 text. |
| 7 | [`genre_ladder.py`](genre_ladder.py) | Book of Mormon against Hebrew at each matched genre step, and which use of the formula carries the difference. |
| 8 | [`per_verb.py`](per_verb.py) | Whether the comparison survives with verbs, not English words, as the unit. |
| 9 | [`greek_egeneto.py`](greek_egeneto.py) | The Greek New Testament's ἐγένετο, the other biblical source of the English phrase. |
| 10 | [`egyptian.py`](egyptian.py) | Egyptian narrative openings, and a Hebrew + Egyptian additive model, with genre and date matching. |
| 11 | [`event_shares.py`](event_shares.py) | How often English biblical-style texts (the KJV, period pastiches, Joseph Smith's JST, Moses and Abraham) go straight to the event. |
| 12 | [`prereg_event_share.py`](prereg_event_share.py) | PREREG 2, run as registered. |
| 13 | [`prereg_jst_then.py`](prereg_jst_then.py) | PREREG 30, run as registered. |

## Dependencies between analyses

Some analyses read another's result file (`depends` in the declaration):

- `genre-ladder` ← `bom-buckets`
- `egyptian` ← `genre-ladder`
- `per-verb` ← `bom-buckets`, `egyptian`
- `greek-egeneto` ← `per-verb`
- `published-claims` ← `hebrew-forms`

A dependency is fingerprinted by its result data. When an upstream result
changes, the downstream analyses go stale; `uv run bomstylo run --stale-only`
reruns them in order.

## Shared rules

Nothing here defines a rule another analysis needs. The rules live in
`src/bomstylo/`, labelled with the Requiem statement they carry:

- Hebrew buckets: `bomstylo.hebrew.classify` (`methods/wayhi/hebrew-rule`)
- English rule, registered and revised: `bomstylo.english` (`methods/wayhi/english-rule-registered`, `-revised`)
- Genre steps on both sides: `bomstylo.genre`; Book of Mormon spans: `bomstylo.spans`
- 1830 alignment: `bomstylo.edition1830` (`methods/wayhi/1830-false-removals`)
- Egyptian texts and their genre/date: `bomstylo.egyptian` (`methods/wayhi/egyptian-comparability`)
- Verb counts: `bomstylo.verbs` (`methods/wayhi/units-per-verb`)
