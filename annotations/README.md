# Annotations

Hand-made data: everything an analysis reads that isn't a fetched source text.
Each file is a plain tab-separated table with a header row, committed so that
it can be reviewed and disputed line by line (constitution IV). Changing a
file here changes the fingerprint of every analysis that reads it, and only
those (`tests/test_repository.py::test_an_input_change_marks_exactly_its_readers`).

References use the Book of Mormon's book names and chapter:verse
("2 Nephi 24:32"); a bare chapter ("Jacob 7") means the whole chapter.

## `records.tsv`: whose record each verse belongs to

15 spans covering every verse of the Book of Mormon: the narrator of each
record (Nephi, Jacob, Enos, … Mormon, Moroni), as the book itself announces
them ("I, Nephi", the colophons and the hand-offs of the plates). Columns:
`start_ref`, `end_ref`, `layer` (`record`), `speaker`, `kind` (`narration`),
`confidence`, `note`. Used for the event-first share by narrator
(`bom-buckets`, `prereg-event-share`).

## `embedded.tsv`: speech, letters and quotations inside the narrative

73 spans that the narrative frame excludes. Columns as above, with `layer`
`embedded`, the `speaker`, and a `kind`:

| kind | spans | leaves the comparison at |
|---|---|---|
| `quotation` (KJV block quotations: Isaiah and Malachi) | 6 | step 2 |
| `discourse` (sermons, speeches) | 46 | step 4 |
| `epistle` | 9 | step 4 |
| `prophecy` | 7 | step 4 |
| `liturgy` | 3 | step 4 |
| `allegory` (Zenos's olive tree) | 1 | step 4 |
| `narration` (Zeniff's first-person record, Mosiah 9–10) | 1 | stays in the frame (as in PREREG 2); counted as speech in the sensitivity check |

How it was made: the spans were marked one by one, not by a rule, from the book's own framing:
the places where it says someone speaks, writes or is quoted, and where that
ends. `confidence` is `explicit` (67) when the book marks both ends, and
`inferred` (6) when one end is read from context, e.g. Lehi's dream as Nephi
reports it. A formula scan for attribution phrases ("and thus spake …",
"saying") was used to find candidates; each was given its end by hand. Spans
may nest (2 Nephi 3:7 is Joseph of Egypt quoted by Lehi in Nephi's record).

The `exclusions` analysis checks these spans against the texts: it finds every
passage sharing 8-word runs with the KJV and reports which step removes it.
That check found one error, now fixed: the Isaiah 2–14 quotation was marked as
ending at 2 Nephi 24:23 instead of 24:32, which left Isaiah 14:24–32 (236
words, no formulas) in the narrative frame. The fix is noted on the row and in
the report's corrections section.

## `wayhi_audit_bom.tsv`: the English rule against a hand reading

120 Book of Mormon narrative-frame uses of "it came to pass", drawn at random
(seed 20261018) and each read in context. Columns: `ref`, `before` (the word
before the formula), `follows` (the first 40 characters after it),
`rule_registered` and `rule_revised` (what each English rule says), `hand`
(`time` = setting-first, `event` = straight to the event) and `note`. The
rule columns are written by the code; `hand` was filled in by one reader. Result: 76 event, 44 time; both rules agree on 119.
The one miss is Alma 49:28 ("on the other hand" is a connective). Three
"the Nth year ended" statements were labelled `event`, because they are main
clauses; calling them settings would lower the event share by about 2.5 points.

## `egeneto_labels.tsv`: Greek ἐγένετο by bucket

The 202 ἐγένετο in the SBLGNT (201 aorist middle indicative third singular of
γίνομαι, plus the historic-present γίνεται of Mark 2:15) were each read in
context by one reader. The file lists 70 of them:
56 `setting`, 8 `event`, 3 `sub` (ἐγένετο + infinitive inside a ὡς/ὅτε clause)
and 3 `verb` listed because they are judgement calls. Every instance not listed is `verb`
(ἐγένετο with its own subject or complement, "there arose a calm").
`bomstylo.greek.instances()` asserts the total of 202. Columns: `ref`,
`form` (`aorist` or `present`), `bucket`, `note`. The judgement calls are in
the notes: Acts 9:43, 11:26 and 14:1 are `event` (a duration or place comes
first, not a setting); Acts 9:32 is `setting` (a circumstantial participle);
Luke 1:5, Acts 8:1 and 19:23 are `verb` (ἐγένετο has its own subject although
a time phrase follows).

## Licence

CC BY 4.0, like the reports ([`LICENSE-REPORTS`](../LICENSE-REPORTS)).
