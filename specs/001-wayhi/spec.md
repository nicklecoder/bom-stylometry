# Feature Specification: "And it came to pass" (*wayhi*) analyses and report

**Feature Branch**: `001-wayhi`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "A clean, developer-structured repository for the
Book of Mormon stylometry tests that focus on *wayhi* counts, with a generated
markdown report. The report explains the methods and why they were chosen,
including what was left out on the Book of Mormon side (Isaiah chapters, New
Testament quotations, Malachi, and similar), how genre is controlled, and which
source texts were used and where to find them. It gives every number, test,
reason and technical detail a peer reviewer would need. Requirements and results
are tracked in Requiem, so an agent can tell from Requiem alone whether a result
is current. The structure must later take in the project's other test families."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reviewer checks every number in the report (Priority: P1)

A reader of the blog post opens the linked report. They want to know where
"2.7×" or "70% straight to the event" comes from, which texts were used, what
was excluded and why. Then they want to reproduce the numbers themselves.

**Why this priority**: The report is the half of the blog post that carries the
evidence. If the report can't be checked, the post makes unsupported claims.

**Independent Test**: On a clean machine, follow the README. Fetch the corpora,
run all *wayhi* analyses and build the report. The result is identical to the
committed `reports/wayhi.md`.

**Acceptance Scenarios**:

1. **Given** a fresh clone and network access, **When** the reviewer runs
   `uv run bomstylo fetch`, **Then** every source text is downloaded from its
   original publisher, checked against its pinned sha256 and prepared into the
   form the analyses read. Any mismatch stops with a message naming the source.
2. **Given** fetched corpora, **When** the reviewer runs
   `uv run bomstylo run --family wayhi` and `uv run bomstylo report wayhi`,
   **Then** the regenerated report differs from the committed one only in its
   generation timestamp.
3. **Given** the report, **When** the reviewer looks up any number in it,
   **Then** the report names the analysis that produced it and the result file
   that holds it.

---

### User Story 2 - An agent learns what's known without rerunning anything (Priority: P1)

An AI agent is asked a question about the *wayhi* results. It wants the current
numbers, and it wants to know whether they are still valid, without loading the
code or rerunning hours of analysis.

**Why this priority**: The user asked for this explicitly. It is also what keeps
later work from repeating finished tests.

**Independent Test**: With no analysis rerun, `requiem list --kind result
--namespace results/wayhi` and `requiem get` return each headline number and a
`stale` flag. Editing an input (a rule, an annotation or a corpus file) and
running `uv run bomstylo fingerprint` turns the affected results stale, and
only those.

**Acceptance Scenarios**:

1. **Given** up-to-date results, **When** an agent runs `requiem get
   results/wayhi/genre-ladder/headline`, **Then** it receives the headline
   numbers with their intervals, the analysis label (registered or
   exploratory), and `stale: false`.
2. **Given** a change to the English classification rule, **When**
   fingerprints are refreshed, **Then** every analysis that uses the rule is
   stale, and analyses that don't use it (for example the Greek hand labels'
   totals) are not.
3. **Given** a stale result that has been rerun, **When** `bomstylo record` runs,
   **Then** it reports, for each headline number, whether the new value falls
   inside the old interval. It then updates the statement, and the change waits
   for `requiem commit`.
4. **Given** a proposal to change a method, **When** an agent runs
   `requiem check --text "<proposal>"`, **Then** the relevant method decisions
   and rejections are returned. Examples: pooling *wayhi* with *wehayah*;
   counting ordinary-verb *wayhi*; using the "too old" cut-off for Egyptian
   texts.

---

### User Story 3 - A developer adds the next test family (Priority: P2)

The project's other families need homes later: chiasmus, *wherefore*/*therefore*,
Early Modern English and authorship. A developer adding one should find the
pattern obvious and shared code reusable.

**Why this priority**: The user wants this repository to grow. Its structure
has to make that easy, but nothing outside *wayhi* is built now.

**Independent Test**: `ANALYSES.md` and `analyses/README.md` explain how to add
a family. A stub family can be registered by following them, without editing any
*wayhi* code.

**Acceptance Scenarios**:

1. **Given** the repository, **When** a developer reads `ANALYSES.md`, **Then**
   they see every analysis grouped by family, with its question, its label, its
   module path, its result file and its Requiem id.
2. **Given** a new `analyses/<family>/` module with an `ANALYSIS` declaration,
   **When** `bomstylo index` runs, **Then** it appears in `ANALYSES.md` and in
   `bomstylo status`.

---

### Edge Cases

- **Remote file changed.** A source's remote file no longer matches its pinned
  hash, for example because a repository's master branch moved. The fetch fails
  for that source, naming the expected and found hashes and the pinned version
  to use. It does not silently accept new content.
- **Source can't be downloaded automatically.** The manifest marks it `manual`,
  and the fetch prints the exact instructions and the expected hash.
- **Optional heavy dependency missing.** If the spaCy English model is absent,
  the per-verb analyses stop with an install instruction. The other analyses
  still run.
- **Versification differences.** Hebrew and KJV versification differ in places
  (Malachi 4, Joel 2–3, Psalm headings). These verses are counted as unmatched
  and reported, not dropped silently.
- **OCR sources.** The 1830 edition, the JST and *The Late War* are OCR scans.
  Unmatched alignments are counted and reported.

## Requirements *(mandatory)*

### Functional Requirements

#### Corpora

- **FR-001**: The repository MUST NOT contain source texts. `corpora/manifest.yaml`
  MUST list each source with: id, title, edition, publisher or URL, pinned
  version (a commit, a dataset revision or an archive.org identifier), licence,
  the sha256 of the raw download and of the prepared file, the preparation
  step, the citation, and the analyses that use it.
- **FR-002**: `bomstylo fetch` MUST reproduce every prepared corpus file byte
  for byte from the manifest. It MUST verify the hashes and MUST stop on a
  mismatch.
- **FR-003**: The report's sources section MUST be generated from the manifest,
  so the citations and the fetched texts cannot diverge.
- **FR-004**: Hand-made data MUST be committed under `annotations/` with a
  README saying how it was made. This covers the Book of Mormon speech and
  quotation spans, the record (narrator) spans, the 120-case hand audit and the
  202 Greek hand labels.

#### Analyses (the *wayhi* family)

Each analysis MUST be one module under `analyses/wayhi/`. Its docstring MUST
state the question, why it is asked, its inputs, its method and its label. It
MUST write `results/wayhi/<id>.json` and `results/wayhi/<id>.fingerprint`.

- **FR-010 `published-claims`**: Compare the published figures (Parry 1992 and
  2020: *wayhi* about 1,204; KJV "came to pass" 727; Book of Mormon 1,404; 1830
  text 1,494) with counts measured from the texts. Report which counting rule
  could produce 1,204.
- **FR-011 `hebrew-forms`**: Count every "and + *hayah*" form by morphology and
  by unpointed spelling. Classify each *wayhi* and *wehayah* into the buckets
  `setting`, `event` and `verb` with the Hebrew rule.
- **FR-012 `kjv-rendering`**: For verses with exactly one *wayhi* or
  *wehayah*, report how often the KJV renders each Hebrew bucket as "came / shall
  come to pass". Report KJV uses of the phrase with no Hebrew form behind them.
  Report how often the English rule agrees with the Hebrew bucket, under both
  the registered and the revised English rule.
- **FR-013 `english-rule-audit`**: Compare the English rule with the 120-case
  hand audit of Book of Mormon narrative instances, under both rules.
- **FR-014 `bom-buckets`**: Count Book of Mormon uses by bucket and tense at
  each genre level, for the current text and the 1830 text separately. This
  includes the 1830 alignment (removals and additions). Report sensitivity to
  the frame definition (Zeniff's record counted as narrative).
- **FR-015 `genre-ladder`**: Compare the two texts at five matched genre steps,
  showing KJV English, Hebrew setting-first and the Book of Mormon rate (current
  and 1830), with exact 95% intervals on each ratio. Report each of the 17
  named Hebrew narrative units.
- **FR-016 `per-verb`**: Repeat the narrative-frame comparison per 100 verbs, each
  language counted in its own text. Report words per verb on each side and the
  KJV-to-Hebrew verb ratio as the check.
- **FR-017 `greek-egeneto`**: Using the hand labels, put every ἐγένετο in the
  SBLGNT into the same buckets. Report KJV rendering and English-rule agreement,
  and narrative-frame rates for the Gospels and Acts and for Luke–Acts.
  (Textus Receptus differences were in the first draft of this requirement and
  were dropped: neither the old project nor this one computed them. The
  report's limitations section says so.)
- **FR-018 `event-shares`**: Report the share of uses that go straight to the
  event, with Clopper–Pearson intervals, for the English comparison texts: the
  KJV OT and NT, *The Late War*, Snowden, *Napoleon*, *Nullification*, the JST's
  added and kept formulas, and the Book of Abraham against the Book of Moses.
  Report both English rules. The other shares live with the analysis that owns
  the text: Hebrew in `hebrew-forms` and `genre-ladder`, Greek in
  `greek-egeneto`, the Book of Mormon by narrator in `bom-buckets`.
- **FR-019 `egyptian`**: Report the Egyptian comparisons:
  - the old narrative particles (*ꜥḥꜥ.n*, *wn.ꞽn*) in the named AED-TEI texts;
  - Demotic *ḫpr* openings in the TLA Demotic sentences, under the four
    selection rules;
  - pRylands 9;
  - the additive Hebrew-plus-Egyptian model, per word and per verb.

  Each Egyptian text MUST carry its date, genre and register, and a
  matched/unmatched flag (Principle II). The family conclusion on rate MUST read
  "inconclusive" unless a matched text decides it.
- **FR-020 `prereg-event-share`** and **FR-021 `prereg-jst-then`**: Re-run the
  two pre-registered tests (PREREG 2 and PREREG 30) exactly as registered.
  Report their registered verdicts unchanged, and the revised-rule figures
  beside them.
- **FR-022 `exclusions`**: Find every Book of Mormon passage that shares long
  word runs (8-grams) with the KJV, place it by its best-matching KJV book, and
  report the genre step at which it leaves the comparison. This is the check
  behind FR-031; it also tests the hand-made spans of FR-030 against the texts.

#### Book of Mormon exclusions (must be explicit in code and in the report)

- **FR-030**: The exclusion layers MUST be data, under `annotations/`, never
  logic hidden in an analysis:
  - **KJV block quotations** (removed from step 2 on): 1 Nephi 20–21 (Isaiah
    48–49); 2 Nephi 7–8 (Isaiah 50–51); 2 Nephi 12–24 (Isaiah 2–14); Mosiah 14
    (Isaiah 53); 3 Nephi 22 (Isaiah 54); 3 Nephi 24–25 (Malachi 3–4).
  - **Embedded speech** (removed at step 4): sermons, epistles, prophecies and
    embedded records (67 spans). This includes the KJV parallels inside speech:
    the Sermon at the Temple (3 Nephi 12–14, Matthew 5–7), Isaiah 29 in 2 Nephi
    27, Isaiah 52 and Micah in 3 Nephi 20–21, and 1 Corinthians 13 in Moroni 7.
- **FR-031**: The report MUST list every KJV-parallel passage in the Book of
  Mormon and the genre step at which it leaves the comparison. It MUST flag any
  passage that stays in at the final step, for example Mark 16 in Mormon 9.
- **FR-032**: The report MUST say how the Hebrew side is cut at each step, and
  MUST give the reason for each cut:
  - law books removed;
  - speech removed per instance, using the quotation marks of the World English
    Bible verse the instance stands in;
  - the 17 named narrative units;
  - Daniel left out, because Daniel 2–7 is Aramaic.

#### Results and Requiem

- **FR-040**: Every analysis MUST have a fingerprint: a sha256 over its own
  source, the shared modules it uses, the annotation and corpus files it reads,
  its parameters, and the result files of any analysis it depends on.
  `bomstylo fingerprint` MUST rewrite all fingerprint files without running any
  analysis.
- **FR-041**: Every analysis MUST declare its headline numbers. `bomstylo record`
  MUST write or update a Requiem statement with kind `result` at
  `results/wayhi/<id>/headline`. The statement body gives the numbers in a plain
  sentence. The statement is anchored (code-derived provenance) to the
  analysis's fingerprint file, and tagged with the label and the fingerprint.
- **FR-042**: `bomstylo status` MUST list each analysis as `current`, `stale`
  (with which inputs changed) or `missing`.
- **FR-043**: Method decisions and rejected alternatives MUST be recorded in
  Requiem under `methods/wayhi/`, and repository rules under `repo/`.

#### Report

- **FR-050**: `bomstylo report wayhi` MUST write `reports/wayhi.md`, a
  self-contained markdown report in these sections:
  1. summary;
  2. questions and why each was asked;
  3. sources;
  4. methods: buckets, Hebrew and English rules, calibration, genre steps,
     exclusions, units, statistics;
  5. results, one subsection per analysis, giving each test, why it was run, the
     result and its label;
  6. corrections to earlier figures;
  7. limitations;
  8. how to reproduce.
- **FR-051**: The report's prose MUST follow Principle I: no argument for any
  conclusion. Inconclusive results are called inconclusive.
- **FR-052**: Every table in the report MUST be generated from result files.
  Fixed prose explaining the methods lives in a template under `reports/templates/`.

### Key Entities

- **Source**: an external text, with its edition, URL, pinned version, licence,
  hashes and preparation step.
- **Annotation**: hand-made data, with its author, method and date.
- **Analysis**: a question with a label, its inputs, its outputs and its
  headline numbers.
- **Result**: the output of an analysis, with its fingerprint and generation
  time.
- **Result statement**: the Requiem record of a result's headline, anchored to
  the fingerprint.
- **Method decision or rejection**: a Requiem record of how something is
  measured, and of what was considered and turned down.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every number the blog post cites appears in `reports/wayhi.md`,
  and matches the value in the current Stylometry outputs to the shown
  precision, or is listed under "Corrections" with the reason. The parity
  check is `tests/test_results.py`, against values copied from the old project
  (corrected where a correction is listed).
- **SC-002**: From a fresh clone, fetching, running and building the report
  reproduces `reports/wayhi.md` (apart from timestamps) with no manual steps
  beyond installing `uv`, the optional spaCy model and network access.
- **SC-003**: An agent can answer "what is the narrative-frame ratio and is it
  current?" with two Requiem commands and no file reads.
- **SC-004**: Changing one input marks stale exactly the analyses that depend
  on it. This is checked by `tests/test_repository.py`
  (`test_an_input_change_marks_exactly_its_readers`).
- **SC-005**: A new family can be added without changing any file under
  `analyses/wayhi/`.

## Assumptions

- Python 3.12 managed with `uv`. Dependencies: scipy, PyYAML, spaCy with
  `en_core_web_lg` (for the per-verb and Greek analyses only), and pytest.
- The numbers to reproduce are those of the 2026-10-18 versions of the
  Stylometry scripts (`wayhi_buckets.py` and related). Exact parity is the goal.
  Any deliberate change is listed under "Corrections" in the report.
- The pre-registration documents (PREREGISTRATION_2.md and
  PREREGISTRATION_30.md) are copied verbatim, with their original hashes.
- Licences: the code is MIT and the reports and annotations are CC BY 4.0.
  Source texts keep their own licences and are not redistributed.
- The repository will be public on GitHub once pushed.
