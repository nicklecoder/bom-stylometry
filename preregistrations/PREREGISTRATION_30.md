# Pre-registration 30: is "it came to pass that" Joseph Smith's all-purpose "then"?

**Written 2026-10-14, before any formula in the Joseph Smith Translation was
counted or classified.**
- Script: `scripts/jst_then_test.py` (written after this file is hashed).
- Hashes are in `out/prereg.sha256`.

**Already seen.** While checking the OCR, one JST formula was read: the
opening of JST Genesis 1 (= Moses 2:1), "AND it came to pass, that the Lord
spake unto Moses", which is not in the KJV. No other formula was looked at.

## The question

The Book of Mormon's narrative frame uses "it came to pass" at 7.76 per 1,000
words, and 71% of uses lead straight to an event (PREREG 2). Hebrew *wayhi* is
0% event-first, Egyptian narrative particles are 100%, the KJV is 12–22%, and
*The Late War* is 35%.

**H_then (the rival explanation).** The formula is the English producer's
stock narrative connective, a general "then", and it is not tied to any source
word. If so, the habit belongs to the producer, and it should show wherever the
same producer writes narrative in the same register.

**The test case: the Joseph Smith Translation (JST) of the Bible, 1830–33.**
- Smith revised KJV narrative within months to four years of the Book of Mormon
  dictation, and in the same register.
- Unlike the Book of Mormon, the source text is known: every formula he
  **added** can be found by aligning the JST with the KJV.
- No account puts an Egyptian-pattern source behind those additions. On the
  believer's account the JST restores the original Bible text, and for
  Genesis–Kings that original is Hebrew, where *wayhi* is time-first. So
  event-first additions would come from the producer, under either account.

Under H_then, the added formulas should be predominantly event-first. If the
Book of Mormon's event-first share has some other origin, Smith's additions
should look like the KJV, time-first or mixed.

## Texts (fixed)

- **JST:** *The Holy Scriptures* (Inspired Version), 1867, archive.org
  `holyscriptures00smit`, OCR text (`corpus/jst_src/holyscriptures00smit_djvu.txt`).
  The 1867 edition was printed from Smith's 1830–33 manuscripts. Its editorial
  differences from the manuscripts are a known limit, not corrected here.
- **KJV:** `corpus/kjv_ot.jsonl`, `corpus/kjv_nt.jsonl` (the study's KJV).
- **Primary panel (OT narrative):** Genesis, Exodus, Numbers, Joshua, Judges,
  Ruth, 1 Samuel, 2 Samuel, 1 Kings, 2 Kings, 1 Chronicles, 2 Chronicles,
  Ezra, Nehemiah, Esther. Genesis includes the Book of Moses material (JST
  Genesis 1–8).
- **Secondary panel (NT narrative):** Matthew, Mark, Luke, John, Acts.
- **Excluded:** the Book of Abraham. It claims an Egyptian source, so under
  the source reading it could legitimately be event-first. Its shares are
  reported descriptively only.

## Procedure (fixed)

1. **Book segmentation.** Split the JST OCR into books at the running book
   headers. Join words hyphenated across line ends. Lowercase, and tokenise on
   letters and apostrophes. Drop chapter-summary lines (the italic one-line
   headnotes printed under each "CHAPTER" heading) and verse numbers.
2. **Alignment.** For each book, align JST tokens to KJV tokens with
   `difflib.SequenceMatcher(autojunk=False)`.
3. **Formula.** Past-tense "it came to pass" (optional comma, optional "that").
   The future "it shall come to pass" is excluded.
4. **Classification of each JST formula:**
   - **retained:** the KJV contains "came to pass" within ±10 tokens of the
     aligned position (this tolerates OCR noise);
   - **added:** otherwise.
   - **KJV formulas removed** by Smith are counted the same way in reverse,
     for description.
5. **Event or time:** the English rule of PREREG 2 (Amendment 2), unchanged.
   TIME if the 40 characters after the formula (punctuation and "that"
   skipped) begin with when / after / as / while / in the / on the / in that /
   in this / in those / at the / at that / about / before / until / on the
   morrow / the next / the day. Otherwise EVENT.
6. **Composition vs revision (secondary).** An added formula lies in **new
   composition** if it falls inside an inserted JST run (an `insert` or
   `replace` opcode) of 50 or more tokens with no KJV counterpart. Otherwise
   it is a **revision** of KJV wording.

## Statistics

- **S** = event-first share of **added** formulas, primary panel. Exact 95%
  interval (Clopper–Pearson).
- Reported alongside, with no verdict:
  - S for retained formulas (should resemble the KJV's ~12%, which acts as a
    check on the classifier);
  - S for the secondary panel, and split by new composition vs revision;
  - the added-formula rate per 1,000 JST words, and the formula rate before
    and after revision for each book.

## Decision rule (fixed now)

Book of Mormon reference value: B = 0.71 (PREREG 2).

- **R0, power.** If the primary panel has fewer than 30 added formulas, the
  share test is **underpowered**, and no verdict on H_then is drawn from S.
  The added-formula rate is still reported. A low rate is descriptive evidence
  that Smith, revising narrative, did not reach for the formula as a general
  connective.
- **R1, habit transfers.** If S ≥ 0.56 (within 0.15 of B, the PREREG 2
  tolerance): the event-first habit appears in Smith's own revision of a known
  text, where no Egyptian-pattern source lies behind it. **H_then is then a
  sufficient explanation of the Book of Mormon's event-first share**, and the
  Egyptian reading of that share (FINDINGS §22, PREREG 2,
  CAME_TO_PASS_DEMOTIC.md) loses its distinctive support.
- **R2, habit does not transfer.** If S ≤ 0.35 (at or below the highest
  English control, *The Late War*): Smith, revising narrative in the same
  register and the same years, does not use the formula the Book of Mormon
  way. **H_then, as Smith's general narrative habit, is not supported.** The
  Book of Mormon's event-first share is specific to the Book of Mormon.
- **R3, undecided.** 0.35 < S < 0.56: reported as undecided, and not
  re-described as leaning either way.

The interval is reported but does not enter the rule. If the interval
straddles a threshold, that is said plainly.

## What each outcome would and would not mean

- **R1** would not show that the Book of Mormon has no ancient source. It would
  show that this feature does not need one, because the producer has the habit
  independently.
- **R2** would not show an Egyptian source. A habit specific to the Book of
  Mormon project, whether a composer's or a translator's, is still possible.
  What R2 removes is the simplest form of H_then: "this is just how Joseph
  Smith wrote biblical narrative".
- **Limits, fixed in advance:**
  - Revision is not composition. Smith kept most KJV wording, so the rate of
    additions cannot be expected to reach the Book of Mormon's level even
    under H_then. Rate therefore has no verdict.
  - The 1867 print may differ from the manuscripts.
  - OCR damage can hide a formula, or misplace an alignment.
  - On the believer's account the JST is also revelatory. That does not
    affect the logic above, because its claimed originals are Hebrew.

---

## Amendment 1 — 2026-10-14, after a first run (implementation bug; rule unchanged)

The first run printed JST books 25–45% shorter than the KJV (Exodus 23,825
words against 32,768, while the raw OCR segment has 33,481). The cause was the
headnote filter in step 1. It dropped every line after a "CHAPTER" heading
until a line opening with a capitalised word. Where the OCR did not render
verse 1's opening word in capitals, it dropped the whole chapter: 1,529 lines
in Exodus alone. The missing text also inflated "removed" counts.

**Fix:** a headnote is at most 4 lines, and it ends at the first line ending
in a full stop, or at a line opening with a word in capitals. Nothing else
changes: definitions, statistics and the decision rule are as registered.

**Results of the buggy run, recorded because they were seen:** primary panel
24 added formulas (15 event, 9 time), S = 0.62 (0.41–0.81), so R0
(underpowered). 252 retained, with event share 0.18. Added per 1,000 JST words:
0.11.

**One implementation interpretation, made before the first run:** for step 6,
"no KJV counterpart" was read as a pure `insert`, or a `replace` whose KJV
side is under a fifth of the JST side.

---

## Result (2026-10-14, after Amendment 1)

**Primary panel: 52 added formulas, 39 event-first and 13 time-first.
S = 0.75 (0.61–0.86). Verdict as registered: R1, the habit transfers.** The
interval lies wholly above 0.56. Retained formulas are 0.13 event-first
(KJV OT 0.12), so the classifier behaves.

## Amendment 2 — post-run checks (do not change the verdict)

1. **Boundary spill-over.** Five "added" formulas are KJV formulas from the
   start of the next book, which falls before that book's first running head:
   Ruth 1:1 and 1:19 (assigned to Judges), Esther 1:1 and 9:1 (to Nehemiah),
   and Exodus 1:21 (to Genesis). Without them: 47 added, 38 event, 9 time,
   **S = 0.81 (0.67–0.91)**. The verdict is unchanged.
2. **Where the additions are.** 43 of the 47 genuine additions are in
   material Smith newly wrote: Moses 1, the Enoch, Methuselah and Noah
   chapters (Moses 6–8), and the JST Genesis 14–15, 17 and 21 expansions.
   Revising existing KJV narrative, Exodus to Esther (~270,000 words), he
   added none. The step-6 composition/revision split is unreliable here,
   because difflib pairs new passages with unrelated KJV lines, so it labels
   new material "revision". It is not used.
3. **Rate, descriptive (current Pearl of Great Price text, speech not
   removed):**

   | text | words | formulas | per 1,000 | event-first |
   |---|---|---|---|---|
   | Moses 1 (wholly new) | 1,456 | 10 | 6.87 | 70% |
   | Moses 2–4 (Genesis 1–3 parallel) | 1,916 | 1 | 0.52 | 0% |
   | Moses 5–8 (Genesis 4–6 + Enoch/Noah) | 7,290 | 29 | 3.98 | 86% |
   | Abraham (claims an Egyptian source; descriptive only) | 5,085 | 16 | 3.15 | 94% |
   | *Book of Mormon, whole text (for scale)* | | | *≈5.1* | *72%* |
   | *KJV OT, whole text* | | | *≈0.6* | *12%* |

## Reading

- **What R1 establishes.** When Joseph Smith produced new narrative in
  scripture register in 1830–31, the formula is event-first at the Book of
  Mormon's share (81%, against 71%). New Moses material also runs at a rate of
  the Book of Mormon's order. No account puts an Egyptian-pattern source behind
  Moses 1 or the Enoch chapters. So the event-first share **does not need** an
  Egyptian source: the producer has the habit independently. By the
  registered rule, the Egyptian reading of the share loses its distinctive
  support.
- **What R1 does not establish.**
  - That the Book of Mormon lacks an ancient source. The share is now
    explained either way, so it no longer bears on that question.
  - That the formula was a "then" applied mechanically. When Smith revised
    existing KJV narrative he almost never added it. The habit appears where
    new narrative is being produced, not as a find-and-replace on the KJV.
- **The strongest objection, stated at full weight.** On the believer's
  account Moses 1 and the Enoch chapters are revealed restorations, so they
  share the Book of Mormon's channel (as the D&C did in the chiasm tests). The
  registered logic answers this: the claimed originals of Genesis are Hebrew,
  and Hebrew *wayhi* is time-first, so no claimed source predicts 81%
  event-first. A believer can still hold that the revelatory channel renders
  narrative in a fixed English idiom. That is a "loose control" view of the
  translation, and on that view the event-first share describes the English
  idiom rather than the source. Either way, the share stops being evidence
  about the source language.

---

## Amendment 3 — 2026-10-14, a gap in the design (verdict as computed unchanged; its reading corrected)

**The gap (raised by the user after the result).** The design assumed that
Smith's habit in 1830–31 shows his habit before the Book of Mormon. It does
not. Every Smith narrative text we have was written *after* he dictated
~270,000 words of the Book of Mormon. A rival account predicts R1 just as
well as H_then:

- **Carryover.** The event-first idiom entered Smith's English *from* the Book
  of Mormon translation (on the believer's account, from its source), and he
  kept it when he wrote new scripture narrative a year later.

Both accounts predict event-first additions in the JST. So R1 cannot tell them
apart, and the reading above overstated it in two places:
- "the producer has the habit **independently**": not shown. What is shown is
  that Smith had the habit by June 1830. Where he got it is untested.
- "the Egyptian reading of the share loses its distinctive support": that
  follows only if the habit predates the Book of Mormon. Under carryover the
  JST share is downstream of the Book of Mormon, and it is not independent
  evidence either way.

**Corrected reading.** R1 stands as computed: S = 0.81, above the registered
threshold. What it establishes is narrower. The event-first idiom is Joseph
Smith's own by 1830, and it appears in his new narrative where no source text
lies behind it. It does **not** establish whether he had the idiom before the
Book of Mormon. It therefore does not, on its own, remove the share as
evidence about the Book of Mormon's source.

**Can carryover be ruled out?** Not with surviving texts. A decisive test
needs scripture-register narrative by Smith from before April 1828. None
survives: the 116 pages are lost, and the 1828–29 revelations are not
narrative. Later texts cannot separate the two accounts, because all of them
come after the exposure.

**A check that does not depend on Smith (descriptive, post hoc).** Did
English pseudo-biblical narrative *without* exposure to the Book of Mormon
ever have the event-first share? The same rule (PREREG 2 EN_TIME), whole text:

| pastiche, before or independent of the Book of Mormon | n | event-first | 95% interval | per 1,000 words |
|---|---|---|---|---|
| *The First Book of Napoleon* (1809) | 13 | 85% | 0.55–0.98 | 0.65 |
| *The Book of Nullification* (1830, Charleston) | 16 | 75% | 0.48–0.93 | 1.07 |
| Snowden, *American Revolution* (1793) | 113 | 48% | 0.38–0.57 | 2.10 |
| *The Late War* (1816/1819) | 78 | 35% | | ≈1.7 |
| pooled | 220 | 47% | | |
| *Book of Mormon* | | *71%* | | *≈5.3 (whole text)* |

- Two short pastiches reach the Book of Mormon's share. The two long ones do
  not. The share is within what English pastiche can produce, but it is at
  the top of that range, and every pastiche uses the formula at a third or
  less of the Book of Mormon's rate.
- Rule caveat: Napoleon's "in these latter days" counts as event-first under
  the fixed rule, which lists "in those" but not "in these". Corrected by
  hand, it is 10 of 13 (77%).
- This corrects an earlier statement (REASSESSMENT, PREREG 2) that the Book of
  Mormon's share is far from "any English text". That held for the controls
  then measured (KJV, *The Late War*). It does not hold for all English
  pastiche.

**Exposure does not automatically transmit the rate (descriptive).** Writers
who read the Book of Mormon closely seldom use the formula in their own
writing:
- Strang's *Book of the Law* (1851, scripture register): fewer than 3 uses in
  12,500 words.
- Pratt's *Voice of Warning*: 10 uses in 47,500 words (60% event-first).
- Smith's D&C: 5 uses in 110,000 words, but that text is mostly not
  narrative.

This bears on carryover only weakly. Strang was a reader, not a dictator of
the text, and his Book of the Law is mostly law, not story.

---

## Note — 2026-10-14, robustness of the Amendment 1 fix (verdict unchanged)

The fix in Amendment 1 was made after the buggy run had been seen (R0). To
check that the verdict does not depend on the exact fix chosen, the
headnote limit was varied. Before the five boundary corrections:

| headnote limit | added | S |
|---|---|---|
| 2 lines | 53 | 0.755 |
| 3 lines | 53 | 0.755 |
| 4 lines (registered fix) | 52 | 0.75 |
| 6 lines | 52 | 0.75 |
| 8 lines | 52 | 0.75 |

R1 holds under every setting. The buggy run had S = 0.62. That was already
above 0.56, but it rested on 24 added formulas, under the 30-formula power
floor.
