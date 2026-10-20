"""The repository's own bookkeeping: registry, fingerprints, index, report template."""
import re
import shutil

from bomstylo import analysis, index, paths, results
from bomstylo.report import wayhi as report_wayhi


def test_registry_is_consistent():
    reg = analysis.registry()
    assert reg, "no analyses found"
    srcs = {s["id"] for s in results.manifest()["sources"]}
    for a in reg.values():
        assert a.module.__doc__ and len(a.module.__doc__) > 200, f"{a.id}: docstring must explain the analysis"
        assert set(a.corpora) <= srcs, f"{a.id}: unknown corpus"
        for n in a.annotations:
            assert (paths.ANNOTATIONS / n).exists(), f"{a.id}: missing annotation {n}"
        if a.label == "registered":
            assert (paths.PREREGISTRATIONS / a.preregistration).exists()


def test_fingerprints_are_current():
    """Every fingerprint file matches its inputs (the pre-commit hook keeps this true)."""
    for a in analysis.registry().values():
        want = f"sha256:{results.fingerprint(results.inputs(a))}"
        assert a.fingerprint_path.read_text().strip() == want, f"{a.id}: run `uv run bomstylo fingerprint`"


def test_fingerprint_moves_with_its_inputs(monkeypatch):
    a = analysis.registry()["hebrew-forms"]
    before = results.fingerprint(results.inputs(a))
    monkeypatch.setitem(a.params, "probe", 1)
    assert results.fingerprint(results.inputs(a)) != before


def test_index_is_up_to_date():
    assert (paths.ROOT / "ANALYSES.md").read_text(encoding="utf-8") == index.render()


def test_template_placeholders_have_generators():
    tpl = (paths.REPORTS / "templates" / "wayhi.md").read_text(encoding="utf-8")
    reg = {i for i, a in analysis.registry().items() if a.family == "wayhi"}
    for is_v, name in re.findall(r"\{\{(v:)?([\w-]+)\}\}", tpl):
        if is_v:
            continue
        assert name in report_wayhi.FRAGMENTS or (name.startswith("about-") and name[6:] in reg), name
    # every analysis has a results subsection
    assert {n[6:] for n in re.findall(r"\{\{(about-[\w-]+)\}\}", tpl)} == reg


def test_no_corpus_text_is_tracked():
    """Constitution IV: corpora/raw and corpora/prepared are never committed."""
    gi = (paths.ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "corpora/raw/" in gi and "corpora/prepared/" in gi


def test_an_input_change_marks_exactly_its_readers(monkeypatch, tmp_path):
    """SC-004: editing one annotation changes the fingerprint of the analyses
    that read it and no others. (Dependents follow once the reader is rerun,
    because a dependency is hashed by its result data.)"""
    reg = analysis.registry()
    before = {i: results.fingerprint(results.inputs(a)) for i, a in reg.items()}
    for src in sorted(paths.ANNOTATIONS.glob("*.tsv")):
        shutil.copytree(paths.ANNOTATIONS, tmp_path / src.stem)
        (tmp_path / src.stem / src.name).write_text(src.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        monkeypatch.setattr(paths, "ANNOTATIONS", tmp_path / src.stem)
        changed = {i for i, a in reg.items() if results.fingerprint(results.inputs(a)) != before[i]}
        assert changed == {i for i, a in reg.items() if src.name in a.annotations}, src.name
        monkeypatch.undo()
