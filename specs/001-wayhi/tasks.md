# Tasks: "And it came to pass" (*wayhi*) analyses and report

**Input**: [spec.md](spec.md), [plan.md](plan.md)

Format: `[ID] [P?] [Story] Description`. `[P]` = can run in parallel (different
files, no dependency). `[X]` = done. Stories: US1 reviewer checks every number;
US2 agent learns what's known from Requiem; US3 developer adds the next family.

## Phase 1: Setup

- [X] T001 Create the repository, `pyproject.toml` (Python 3.12, pinned deps, optional `verbs` extra) and `uv.lock`
- [X] T002 Spec Kit init; constitution v1.0.0 in `.specify/memory/constitution.md`
- [X] T003 Requiem init (`.requiem/config.yaml`, hooks); `.gitignore` for corpora, caches, `.venv`
- [X] T004 [P] `LICENSE` (MIT) and `LICENSE-REPORTS` (CC BY 4.0)

## Phase 2: Foundational

- [X] T010 `src/bomstylo/paths.py`, `analysis.py` (declaration + registry in dependency order), `results.py` (inputs, fingerprints, status, save/load)
- [X] T011 `corpora/manifest.yaml` with pinned URLs and sha256 for all 12 sources; `fetch.py`, `prepare.py`, `checksums.py`; `bomstylo fetch` / `verify` / `checksums`
- [X] T012 Verify a from-scratch fetch reproduces every prepared file byte for byte (FR-002)
- [X] T013 [P] Shared rules: `hebrew.py`, `english.py` (registered + revised), `greek.py`, `egyptian.py`, `genre.py`, `spans.py`, `web.py`, `edition1830.py`, `verbs.py`, `controls.py`, `jst.py`, `pgp.py`, `stats.py`
- [X] T014 [P] Annotations: `embedded.tsv`, `records.tsv`, `wayhi_audit_bom.tsv`, `egeneto_labels.tsv` (FR-004, FR-030)
- [X] T015 Pre-registrations 2 and 30 copied byte for byte, with the hash chain README (Principle III)
- [X] T016 CLI: `run`, `fingerprint`, `status`, `record`, `report`, `index`, `install-hooks`

## Phase 3: US1, a reviewer checks every number (P1) 🎯 MVP

- [X] T020 [P] [US1] `published-claims` (FR-010)
- [X] T021 [P] [US1] `hebrew-forms` (FR-011)
- [X] T022 [P] [US1] `kjv-rendering` (FR-012)
- [X] T023 [P] [US1] `english-rule-audit` (FR-013)
- [X] T024 [US1] `bom-buckets`, with the 1830 alignment and the Zeniff sensitivity (FR-014)
- [X] T025 [US1] `genre-ladder` (FR-015), after T024
- [X] T026 [US1] `egyptian` (FR-019), after T025
- [X] T027 [US1] `per-verb` (FR-016), after T024 and T026
- [X] T028 [US1] `greek-egeneto` (FR-017), after T027
- [X] T029 [P] [US1] `event-shares` (FR-018)
- [X] T030 [P] [US1] `prereg-event-share`, `prereg-jst-then` (FR-020, FR-021), including the PREREG 30 robustness note
- [X] T031 [P] [US1] `exclusions` (FR-022, FR-031)
- [X] T032 [US1] Parity tests against the earlier figures in `tests/test_results.py` (SC-001)
- [X] T033 [US1] Report template `reports/templates/wayhi.md`, sections 1–8 (FR-050, FR-051)
- [X] T034 [US1] Report generators `src/bomstylo/report/build.py`, `report/wayhi.py` (FR-052)
- [X] T035 [US1] Corrections section: Isaiah span end (2 Ne 24:23 → 24:32), Moses/Abraham figures, 1830 "added" wording, Egyptian comparability

## Phase 4: US2, an agent learns what's known without rerunning (P1)

- [X] T040 [US2] `requiem_bridge.py`: record, compare with the previous record, re-anchor, refuse stale results (FR-041)
- [X] T041 [US2] Principles under `principles/`, rules under `repo/`, methods and rejections under `methods/wayhi/` (FR-043)
- [X] T042 [US2] Record all 13 results (`uv run bomstylo record`)
- [X] T043 [US2] Code labels (`# requiem: …`) on the rules that carry method decisions
- [ ] T044 [US2] Human review and `requiem commit` of the statements (the approval step; not for an agent)
- [ ] T045 [US2] Decide the open question `methods/wayhi/zeniff-classification`

## Phase 5: US3, a developer adds the next family (P2)

- [X] T050 [US3] `ANALYSES.md` generated from the registry, with status (`bomstylo index`)
- [X] T051 [US3] `analyses/wayhi/README.md` (reading order, dependencies, shared rules)
- [X] T052 [US3] Pre-commit hook: fingerprints and index current (`bomstylo install-hooks`)
- [X] T053 [US3] Test: an input change marks exactly its readers stale (SC-004)
- [ ] T054 [US3] Prove SC-005 by adding a second family (chiasmus or *wherefore*/*therefore*) without touching `analyses/wayhi/`

## Phase 6: Polish

- [X] T060 README, `annotations/README.md`, `CLAUDE.md`/`AGENTS.md` project notes
- [ ] T061 Verify the remaining literature citations in the report (GKC §111f–g, Joüon–Muraoka, Lambdin, Skousen, Halverson 2020, *Charting the Book of Mormon*, Vittmann)
- [ ] T062 SC-002 on a second machine: fresh clone → fetch → run → report, diff against the committed report
- [ ] T063 First commit and push to GitHub (public); then link the report and repository from the blog post

## Dependencies

Phase 2 blocks everything. Within US1: T024 → T025 → T026 → T027 → T028;
the `[P]` analyses are independent. US2 needs US1's results. US3 needs only
Phase 2.
