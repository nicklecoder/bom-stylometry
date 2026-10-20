"""Fill a family's report template with tables and numbers from its result files.

The template (`reports/templates/<family>.md`) holds all fixed prose. It refers
to generated content with placeholders:

    {{name}}        a fragment: a table or list, from `bomstylo.report.<family>.FRAGMENTS`
    {{v:name}}      a single number or short phrase, from the same module's `values()`

A placeholder with no generator is an error, and so is a stale or missing
result: the report is only ever built from current results.
"""
from __future__ import annotations

import importlib
import re

from .. import paths, results
from ..analysis import registry

PLACEHOLDER = re.compile(r"\{\{(v:)?([\w-]+)\}\}")


def about(a, rec: dict) -> str:
    """The standard header of a results subsection: {{about-<analysis id>}}."""
    lab = a.label + (f", as fixed by [`{a.preregistration}`](../preregistrations/{a.preregistration})"
                     if a.preregistration else "")
    src = a.source_path.relative_to(paths.ROOT).as_posix()
    return (f"<a id=\"{a.id}\"></a>**Question.** {a.question}  \n**Why.** {a.why}  \n**Label.** {lab}.  \n"
            f"**Code.** [`{src}`](../{src}); result [`results/{a.family}/{a.id}.json`](../results/{a.family}/{a.id}.json), "
            f"fingerprint `{rec['fingerprint'][:12]}`; Requiem record `{a.requiem_id}`.")


def main(family: str = "wayhi") -> str:
    reg = {i: a for i, a in registry().items() if a.family == family}
    bad = [f"{i} ({results.status(a)[0]})" for i, a in reg.items() if results.status(a)[0] != "current"]
    if bad:
        raise SystemExit(f"results not current: {', '.join(bad)}; run `uv run bomstylo run --stale-only` first")
    mod = importlib.import_module(f"bomstylo.report.{family}")
    data = {i: results.load(a) for i, a in reg.items()}
    frags, vals = mod.FRAGMENTS, mod.values(data)
    tpl = (paths.REPORTS / "templates" / f"{family}.md").read_text(encoding="utf-8")

    def fill(m):
        is_v, name = m.group(1), m.group(2)
        if is_v:
            if name not in vals:
                raise KeyError(f"template value {{{{v:{name}}}}} has no generator")
            return str(vals[name])
        if name.startswith("about-") and name[6:] in reg:
            return about(reg[name[6:]], data[name[6:]])
        if name not in frags:
            raise KeyError(f"template fragment {{{{{name}}}}} has no generator")
        return frags[name](data, reg).rstrip("\n")

    out = PLACEHOLDER.sub(fill, tpl)
    dest = paths.REPORTS / f"{family}.md"
    dest.write_text(out, encoding="utf-8")
    return str(dest.relative_to(paths.ROOT))
