# bom-stylometry

Reproducible measurements of claims about the language of the Book of Mormon.

The first family of tests, and the only one here so far, is **"and it came to
pass"**. Its Hebrew counterpart is *wayhi*. The Book of Mormon uses the phrase
far more often than the King James Bible. That is often offered as evidence of a
Hebrew original. These analyses count the Hebrew itself, compare the two texts
genre for genre, and split every use by what follows the formula. The same is
done for Greek ἐγένετο, Egyptian narrative openings, and English texts written
in biblical style.

- **The report:** [`reports/wayhi.md`](reports/wayhi.md) gives every number,
  every test, why each was run, and the methods in enough detail to review them.
- **The catalogue:** [`ANALYSES.md`](ANALYSES.md) lists every analysis, what it
  reads, and whether its result is current.
- **The rules of the project:** [`.specify/memory/constitution.md`](.specify/memory/constitution.md).
  In short: results are reported the same way whichever way they point; texts
  are compared like for like; pre-registrations are never edited; everything
  is reproducible from public sources.

The project measures claims. It does not argue for any conclusion about where
the book came from.

## Quick start

```sh
uv sync --extra verbs            # Python 3.12; the spaCy model is needed by per-verb and greek-egeneto
uv run bomstylo fetch            # download every source text, check its sha256, prepare it
uv run bomstylo run              # run every analysis (or: run <id>, run --stale-only)
uv run pytest -q                 # calibration and bookkeeping tests
uv run bomstylo report wayhi     # rebuild reports/wayhi.md from the results
```

`uv run bomstylo --help` lists every command. `bomstylo status` says which
results are current, stale (and why) or missing.

The source texts are not in the repository. [`corpora/manifest.yaml`](corpora/manifest.yaml)
pins each one (edition, URL, version, licence, sha256), and `fetch` reproduces
the prepared files byte for byte. One of them, the Brysbaert concreteness
norms used to build the period-pastiche vocabulary, is CC BY-NC-ND: it is
downloaded from its publisher and never redistributed.

## Layout

| path | what it holds |
|---|---|
| `analyses/<family>/` | one module per question. Each declares an `ANALYSIS` (question, why, label, inputs) and defines `run()` and `headline()`. [`analyses/wayhi/README.md`](analyses/wayhi/README.md) indexes the family. |
| `src/bomstylo/` | shared code only: corpus loaders, the Hebrew/English/Greek rules, genre steps, statistics, fingerprints, fetch, the Requiem bridge and the report builder. |
| `annotations/` | hand-made data (who is speaking where, hand labels). Committed, with [how each was made](annotations/README.md). |
| `corpora/` | the manifest and the pinned checksums. `raw/` and `prepared/` are fetched and gitignored. |
| `preregistrations/` | pre-registered tests, byte for byte, with their hash chain. |
| `results/<family>/` | one `<id>.json` and one `<id>.fingerprint` per analysis. |
| `reports/` | generated reports, and the templates that hold their fixed prose. |
| `specs/NNN-<family>/` | the Spec Kit spec, plan and tasks for each family. |
| `.requiem/` | Requiem statements: principles, method decisions, rejected alternatives, and each analysis's headline result. |
| `tests/` | the calibration tests, parity with the earlier figures, and repository bookkeeping. |

## Results in Requiem

Every analysis's headline is a Requiem statement of kind `result` at
`results/<family>/<id>/headline`. It gives the numbers in plain sentences and
is anchored to the analysis's fingerprint file, so

```sh
requiem get results/wayhi/genre-ladder/headline
```

answers both "what was found?" and "is it still current?" (`stale: true` means
an input has changed since it was recorded). Method decisions live under
`methods/<family>/`, repository rules under `repo/`, the constitution under
`principles/`, and the ideas that were considered and turned down are recorded
as rejections. Run `requiem check --text "<idea>"` before changing a method.

After a rerun, `uv run bomstylo record` updates the statements and says whether
any headline number moved outside its previous interval. `requiem commit` is
the human approval step.

## Adding an analysis or a family

1. Start with a spec: `/speckit-specify` in Claude Code (or write
   `specs/NNN-<family>/spec.md` by hand), then the plan and tasks.
2. Add `analyses/<family>/<name>.py` with an `ANALYSIS` declaration, `run()`
   and `headline()`. Put any rule another analysis might use in `src/bomstylo/`.
3. `uv run bomstylo run <id>`, `uv run pytest -q`, `uv run bomstylo index`,
   then `uv run bomstylo record <id>`.
4. A new family gets its own `analyses/<family>/`, its own spec, report
   template and `src/bomstylo/report/<family>.py`.

`uv run bomstylo install-hooks` adds a pre-commit check that fingerprints and
`ANALYSES.md` are up to date.

## Licences

Code: MIT ([`LICENSE`](LICENSE)). Reports, annotations and other prose:
CC BY 4.0 ([`LICENSE-REPORTS`](LICENSE-REPORTS)). Source texts keep their own
licences, listed in the manifest and the report.
