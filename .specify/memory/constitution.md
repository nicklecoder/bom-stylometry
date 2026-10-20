# bom-stylometry Constitution

## Core Principles

### I. Conclusion-agnostic, symmetric reporting

The project measures claims about the Book of Mormon. It does not argue for any
conclusion about where the book came from.

- Every result MUST be reported in the same plain terms whichever way it points.
  This covers results that weaken a claim made by believers and results that
  weaken a claim made by critics.
- A result that is inconclusive MUST be called inconclusive. It MUST NOT be
  rounded up into support for either side, or rounded down into a refutation.
- Every analysis that tests a hypothesis MUST also run that hypothesis's
  strongest available competitor through the same measurement. For example,
  any Egyptian-source comparison is accompanied by Joseph Smith's own
  1830–33 English and by period pastiches.
- Prose in reports MUST describe what was measured and what it does or does not
  rule out. It MUST NOT editorialise about believers, critics or scholars.

Rationale: the work is useful only if readers on every side can trust that the
numbers would have been reported the same way had they come out differently.

### II. Like-for-like comparison, shown one step at a time

- A rate comparison between two texts MUST control genre on both sides in the
  same way. It MUST show the effect of each control step, not only the final
  number.
- A count MUST be taken from the source language whenever one exists (the
  Hebrew, not the KJV's English). Where translation affects a measure, the
  report MUST say how.
- Units that don't carry across languages (such as words) MUST be checked
  against a unit that does (such as verbs). Any disagreement between the two
  MUST be reported.
- Comparison texts MUST be matched on genre and date before a rate mismatch is
  read as evidence against a hypothesis. When no matched text exists, the
  result is inconclusive.

### III. Pre-registration is immutable; exploration is labelled

- Pre-registered tests keep their original documents byte for byte, together
  with the hash taken before the test ran (`preregistrations/`). A change after
  the fact MUST be an amendment that is dated and reported. It MUST NOT be an
  edit.
- Every result MUST carry one of two labels. `registered` means it was decided
  by a rule fixed in advance. `exploratory` means it was found by looking.
- When a later improvement changes a registered measure (for example a fixed
  English rule), both versions MUST be reported, and the registered verdict
  MUST stay as it was.
- Corrections to earlier published numbers MUST be stated where the number
  appears, with the reason.

### IV. Reproducible from public sources

- Source texts MUST NOT be committed. Each one is listed in
  `corpora/manifest.yaml` with its edition, URL, pinned version, licence and
  sha256. `bomstylo fetch` reproduces the exact files.
- Data made by hand for this project (annotations and hand labels) MUST be
  committed, as plain-text tables, with a note on how it was made.
- Every number in a report MUST come from a result file written by an
  analysis. Reports are generated and MUST NOT be edited by hand.
- Each analysis MUST record a fingerprint of its inputs: its code, the shared
  modules it imports, the corpus files it reads and its parameters. A result
  whose fingerprint no longer matches is stale.

### V. Results are recorded where agents look first

- Every analysis's headline result MUST be recorded in Requiem
  (`--kind result`, namespace `results/<family>/<analysis>`). The body is
  plain-language prose giving the numbers and their intervals.
- A result statement is anchored to its analysis's fingerprint file, so
  `requiem get` reports `stale: true` when any input changes.
- An agent MUST check Requiem before rerunning an analysis, and SHOULD NOT
  rerun one whose result is not stale.
- Method decisions, and the alternatives that were rejected, MUST be recorded
  in Requiem as statements and rejections. Re-proposing a rejected method
  requires saying why the rejection no longer holds.

## Repository structure

- `analyses/<family>/` holds one module per question. Each module's docstring
  states the question, why it is asked, its inputs and its label
  (`registered` or `exploratory`). `analyses/<family>/README.md` indexes the
  family.
- `src/bomstylo/` holds shared code only: loaders, the exclusion lists,
  classification rules, statistics, fingerprinting, the Requiem bridge and the
  report builder. An analysis MUST NOT copy a rule that a shared module
  already defines.
- `ANALYSES.md` at the root is generated from the analysis registry. It lists
  every analysis in every family, with where it lives and why it exists.
- A new family (chiasmus, *wherefore*/*therefore*, authorship, and so on) MUST
  get its own `analyses/<family>/`, its own `specs/NNN-<family>/` and its own
  report. It MUST NOT change another family's results without saying so in
  that family's report.

## Development workflow

- New work starts with a Spec Kit spec (`/speckit-specify`), then a plan and
  tasks. The spec states the question, the comparison and the controls before
  any code is written.
- Before changing a method, run `requiem check --text "<the change>"`, and read
  any rejections it returns.
- `uv run pytest` MUST pass before a result is recorded. The calibration tests
  (the English rule against the Hebrew, and the hand audit) are part of the
  suite.
- `uv run bomstylo status` lists stale results. `uv run bomstylo run <id>`
  reruns an analysis. `uv run bomstylo record <id>` updates its Requiem
  statement and reports whether any headline number moved outside its
  previous interval. `requiem commit` approves the change.

## Governance

This constitution overrides other practice in the repository. Amendments are
made by editing this file in a dated commit that states the reason. A principle
that is removed or redefined bumps the major version; a new principle or a
material expansion bumps the minor version; wording changes bump the patch
version. Changes to a constitution principle are also recorded in Requiem under
`principles/`. Reviews check new analyses against Principles I–V.

**Version**: 1.0.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19
