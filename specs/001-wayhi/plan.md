# Implementation Plan: "And it came to pass" (*wayhi*) analyses and report

**Branch**: `001-wayhi` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-wayhi/spec.md`

## Summary

Port the *wayhi* measurements from the exploratory Stylometry project into a
clean repository, one module per question, at exact parity with the earlier
figures except where a correction is listed. Every analysis declares what it
reads; that declaration drives the fingerprints, the staleness check, the
Requiem result records, the generated catalogue (`ANALYSES.md`) and the
generated report (`reports/wayhi.md`). Source texts are fetched from pinned
URLs and checked by sha256, never committed.

## Technical Context

**Language/Version**: Python 3.12, managed with `uv`.

**Primary Dependencies**: numpy, scipy (exact intervals), PyYAML (manifest);
optional spaCy 3.8 with `en_core_web_lg` 3.8.0 for verb counts.

**Storage**: files. Result JSON and fingerprints under `results/`; Requiem
statements under `.requiem/statements/`.

**Testing**: pytest. Calibration tests (the English rule against the Hebrew and
the hand audit), parity tests against the earlier figures, and repository
bookkeeping (fingerprints current, index current, placeholders resolvable, no
corpus text tracked, an input change marks exactly its readers).

**Target Platform**: Linux and macOS; a CLI (`bomstylo`).

**Project Type**: research codebase with a CLI.

**Performance Goals**: a full run of the family in minutes on a laptop.

**Constraints**: byte-identical prepared corpora from a fresh fetch; no
redistribution of texts whose licences forbid it (Brysbaert, CC BY-NC-ND).

**Scale/Scope**: 13 analyses, 12 sources, 4 annotation tables; designed for
further families (chiasmus, *wherefore*/*therefore*, authorship).

## Constitution Check

| Principle | How this plan meets it |
|---|---|
| I. Symmetric reporting | Report prose lives in one template, reviewed against Principle I; inconclusive results (Egyptian rate) are labelled as such in the headline. Each hypothesis has its competitor in the same measurement (Egyptian alongside the JST, Moses/Abraham and the period pastiches). |
| II. Like for like, step by step | `bomstylo.genre` defines the steps once for both sides; each step's figures are reported. Counts are Hebrew and Greek, not KJV English. `per-verb` re-measures across languages. Egyptian rows carry date/genre flags. |
| III. Pre-registration immutable | `preregistrations/` holds the documents byte for byte with a hash chain; `tests/test_preregistrations.py` checks the current hashes. Registered analyses must name their pre-registration, which is hashed into the fingerprint. |
| IV. Reproducible | `corpora/manifest.yaml` + `bomstylo fetch`/`verify`; annotations committed with a README; reports generated and refused when any result is stale. |
| V. Results in Requiem | `bomstylo record` writes `results/wayhi/<id>/headline` anchored to line 1 of the fingerprint file; methods and rejections under `methods/wayhi/`, rules under `repo/`, principles under `principles/`. |

Result: passes. One gap is tracked as a Requiem upstream suggestion, not a
violation: Requiem's `stale` reflects the fingerprint file, so it lags a code
edit until `bomstylo fingerprint` runs (the pre-commit hook runs it).

## Project Structure

### Documentation (this feature)

```text
specs/001-wayhi/
├── spec.md
├── plan.md      # this file
├── tasks.md
└── checklists/
```

### Source Code (repository root)

```text
analyses/wayhi/          # one module per question (13); README gives reading order
src/bomstylo/            # shared code: corpus, hebrew, english, greek, egyptian, genre,
│                        # spans, edition1830, verbs, controls, jst, pgp, web, stats,
│                        # analysis (registry), results (fingerprints), fetch, prepare,
│                        # checksums, requiem_bridge, index, hooks, cli
└── report/              # build.py (template filler) + wayhi.py (tables and values)
annotations/             # hand-made tables + README
corpora/                 # manifest.yaml, checksums/; raw/ and prepared/ gitignored
preregistrations/        # PREREG 2 and 30, hash chain
results/wayhi/           # <id>.json + <id>.fingerprint
reports/                 # templates/wayhi.md (prose) → wayhi.md (generated)
tests/
```

**Structure Decision**: a single Python package plus an `analyses` package of
families. Shared rules live only in `src/bomstylo/`, so that a later family
reuses them rather than copying them, and so that a rule change fingerprints
every analysis that depends on it.

## Design decisions

Each is a Requiem statement; the rejected alternatives are Requiem rejections.

- **Corpus provenance, one style**: manifest-driven fetch with pinned URLs and
  hashes; report citations generated from the manifest
  (`methods/wayhi/corpus-manifest`; rejected `repo/citation-only-corpora`,
  `repo/vendor-source-texts`).
- **Results in Requiem as they are**: one `result` statement per analysis,
  code-derived provenance on the fingerprint file. Re-anchoring after a rerun
  is done by the bridge (edit `hash:`, `git add`, `requiem reindex`), because
  Requiem has no re-anchor command yet.
- **Report as template + generators**: fixed prose in
  `reports/templates/wayhi.md`, numbers only through placeholders
  (`repo/generated-reports`).
- **Hebrew rule, two English rules, 1830 alignment, genre control, exclusions
  check, Egyptian comparability, units**: `methods/wayhi/*`.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected because |
|---|---|---|
| A Requiem bridge that rewrites the provenance hash | Requiem cannot re-anchor a statement | Deleting and re-adding the statement loses its history and links |
| A prepare step per source (`prepare.py`) | Several sources need parsing, OCR clean-up or a recorded patch (WEB John 3:2) to reach the exact files the analyses read | Committing prepared files breaks Principle IV and some licences |
