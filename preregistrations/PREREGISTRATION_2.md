# Pre-registration 2: what the narrative particle introduces

**Written 2026-10-11, before any Egyptian particle was classified by what follows it.**

## Background, and what is already known

`REASSESSMENT.md` ("Is the formula forced into a fixed slot?") found that 70% of
the Book of Mormon's narrative-frame "it came to pass" lead straight into an
event ("…that the Jews did mock him"), and 29% into a time setting ("…that
when my father had read…"). Hebrew *wayhi*, used as a narrative marker,
introduces a time setting. That suggested the book's dominant usage
resembles Egyptian narrative particles more than *wayhi*. That observation
was made **after** looking at the data, so it is a lead. This document turns
it into a test.

Stated plainly, so the result is not oversold:

- **The Book of Mormon figure is already known** (789 event, 323 time setting,
  from the narrative frame as defined by `annotations/embedded.tsv`). It is
  recomputed below with the same rule, not re-chosen.
- **The Hebrew figure is close to known**: no *wayhi* followed directly by a
  conjunction-plus-verb was found. It is recomputed with the rule below.
- **Egyptian grammars already describe ꜥḥꜥ.n as opening main narrative
  clauses** ("then he did X"). So rule R1 below is expected to pass, and
  passing it says little. The informative parts are R2 (how close the
  proportions are) and R3 (whether a 19th-century imitator does the same thing).

## Fixed definitions

### Markers (unchanged from §22 of FINDINGS.md, not re-chosen)

| Language | marker |
|---|---|
| Egyptian | TLA lemma 40111 (ꜥḥꜥ.n) and 650007 (wn.ꞽn) |
| Hebrew | lemma 1961 with morphology `HC/Vqw3ms` (*wayhi*) |
| English | "it came to pass" (optional comma, optional "that") |

### What follows: EVENT or TIME

**Egyptian** (AED-TEI, within the same `<s>` sentence as the marker):
- **TIME** if either of the next two tokens is one of these:
  - a temporal preposition: m-ḫt 65300, ḥr-sꜣ 851455, r-sꜣ 851453,
    ḫft 116761;
  - a simple preposition (m 64360, ḥr 107520, r 91900, n 78870) immediately
    followed by a time noun: hrw 99060, rnp.t 94920, rnp.t-zp 850581,
    ꜣbd 93, dwꜣ.w 178000, grḥ 167920, tr 172700, rk 96390, ꜣ.t 5, nw 80840,
    ꜥḥꜥ.w 40480, sp 854543.
- **EVENT** otherwise, if the next token is a verb, a substantive, a pronoun,
  or a particle (the clause the marker opens).
- **OTHER** if the marker ends the sentence or none of the above applies.
  Excluded from the share.

**Hebrew** (Westminster Leningrad Codex):
- **TIME**: the next word is a preposition-plus-infinitive or b-/k-/m-
  prepositional phrase, or carries lemma 310, 3588, 834, 7093 or 6256. This is
  the rule `wayhi_use` already uses for "marker".
- **EVENT**: the next word is a finite verb (morphology `V` + stem + `p`, `q`,
  `w` or `i`), with or without the conjunction.
- Anything else is *wayhi* as the ordinary verb ("and there was X"). It is
  excluded, because then *wayhi* is not a particle.

**English** (Book of Mormon narrative frame, and every control): the rule
already used in `REASSESSMENT.md`, unchanged. TIME if the 40 characters after
the formula begin with when / after / as / while / in the / on the / in that /
in this / in those / at the / at that / about / before / until / on the
morrow / the next / the day. Otherwise EVENT.

**Event share** = EVENT / (EVENT + TIME), for every text.

### Texts

- Egyptian: the 17 named narrative texts of `EGYPT_TEXTS`, pooled over those
  with at least 500 tokens (the existing `MIN_TOKENS`), also reported per text
  and by period. Piye (~727 BC) is flagged as the text nearest Lehi's date.
- Hebrew: whole Hebrew Bible, and the 17 named narrative units.
- Book of Mormon: narrative frame; per claimed narrator as a secondary result.
- English controls under the same rule: KJV Old Testament, KJV New Testament,
  Hunt's *The Late War* (1819).

## Decision rule, fixed now

Let E = Egyptian pooled event share, H = Hebrew, B = Book of Mormon.

- **R0, boundary check.** If |E − H| < 0.30, the feature does not separate the
  two languages, and **the test gives no information**. Reported as such.
- **R1.** If E < 0.50, Egyptian particles do not mainly lead into events, and
  the lead **fails**.
- **R2, match.** The book matches the Egyptian pattern if |B − E| ≤ 0.15. A
  larger gap is a **miss**, and will not be re-described as "consistent with
  translation" or "consistent with drift".
- **R3, discrimination.** A match counts as evidence for an Egyptian-pattern
  source only if the KJV Old Testament **and** *The Late War* are each more
  than 0.15 from B. If either is within 0.15 of B, the feature **does not
  separate an Egyptian-pattern source from English biblical style or
  imitation**, and is reported that way. A control with fewer than 30
  occurrences is reported as underpowered, not as passing or failing.

### What a pass would and would not mean

A full pass (R0, R1, R2 and R3) would mean this one feature of the book's
narrative grammar follows the Egyptian pattern, and that neither the KJV nor
the one available imitator produces it. It would not establish an Egyptian
source. It is one feature with one imitator control. Joseph Smith's English
and any revelatory process remain unmeasured layers between any source and
the text.

A failure would mean this lead does not hold up, and nothing more.

---

## Amendment 1 — 2026-10-11, after the run (implementation note, verdict unchanged)

The Egyptian EVENT rule listed verb / substantive / pronoun / particle as the
following token. AED-TEI tags personal names separately (`entity_name`,
`epitheton_title`), so 111 particles followed by a named subject ("then Khnum
…", "then Horus said …") fell into OTHER and were excluded. None of the 111 is
a time setting. Counted either way, the Egyptian event share is 1.00 (438 of
438, or 549 of 549), so no rule outcome changes. The script is left as
registered, and this note records the gap.

## Result (as computed, `out/event_share.json`)

| | event share |
|---|---|
| Egyptian narrative particles (E) | **1.00** (438 event, 0 time) |
| Hebrew *wayhi* as marker (H) | **0.00** (0 event, 239 time) |
| Book of Mormon narrative frame (B) | **0.71** (800 event, 323 time) |
| KJV Old Testament | 0.14 |
| KJV New Testament | 0.40 |
| *The Late War* (1819) | 0.35 (n = 77) |

- R0 passes: the feature separates the two languages completely.
- R1 passes (expected from the grammars).
- **R2 fails: |B − E| = 0.29 > 0.15. MISS.**
- R3 (both controls more than 0.15 from B) is not reached as a verdict, since
  R2 failed. It is recorded descriptively: the KJV and the imitator are both
  well below the book.

Verdict as fixed in advance: **MISS. The book does not match the Egyptian
proportion.** Per the rule, this is not re-described as a mixture or as a
translation effect.

## Amendment 2 — 2026-10-11, implementation bug in the English rule

The English rule did not skip punctuation after the formula. The KJV writes
"it came to pass, that, when …", so the comma before "when" made a time
setting read as an event. The book's text seldom has that comma, so the bug
inflated the controls far more than the book. Fixed by skipping `[\s,;:]`
after the formula and after "that". The definitions of TIME and EVENT are
unchanged. Effect:

| | before fix | after fix |
|---|---|---|
| Book of Mormon (B) | 0.712 | 0.711 |
| KJV Old Testament | 0.14 | 0.12 |
| KJV New Testament | 0.40 | **0.22** |
| *The Late War* | 0.35 | 0.35 |

The verdict is unchanged: MISS on R2. The controls are now further from B.
The same punctuation issue is not present in the earlier non-registered book
counts (70% / 29%), which change by one occurrence.
