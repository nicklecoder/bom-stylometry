"""What an analysis declares, and how the registry finds analyses.

Each module in `analyses/<family>/` defines:

    ANALYSIS = Analysis(id=..., family=..., title=..., question=..., why=...,
                        label="registered" | "exploratory",
                        corpora=[manifest ids], annotations=[file names],
                        depends=[ids of analyses whose results it reads],
                        params={...},
                        preregistration="PREREGISTRATION_N.md")  # registered only

    def run() -> dict:                 # computes; returns JSON-safe data
    def headline(data) -> list[Headline]:   # the numbers worth recording

The registry imports every such module. Fingerprints, `bomstylo status`,
Requiem records, ANALYSES.md and the reports all come from these declarations,
so there's one place to look for what an analysis is and what it reads.
"""
from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any, Callable

from . import paths

LABELS = ("registered", "exploratory")


@dataclass
class Headline:
    """One recorded number. `text` is the plain-language sentence for Requiem."""
    key: str
    value: float
    low: float | None = None
    high: float | None = None
    text: str = ""

    def inside(self, other: "Headline") -> bool:
        """Is this value inside the other's interval (or equal, if it has none)?"""
        if other.low is None or other.high is None:
            return abs(self.value - other.value) < 1e-9
        return other.low <= self.value <= other.high


@dataclass
class Analysis:
    id: str
    family: str
    title: str
    question: str
    why: str
    label: str
    corpora: list[str] = field(default_factory=list)
    annotations: list[str] = field(default_factory=list)
    depends: list[str] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    needs_verbs: bool = False          # needs the optional spaCy model
    preregistration: str | None = None  # file in preregistrations/ (registered analyses)
    module: ModuleType | None = None   # filled in by the registry

    def __post_init__(self):
        if self.label not in LABELS:
            raise ValueError(f"{self.id}: label must be one of {LABELS}")
        if (self.label == "registered") != (self.preregistration is not None):
            raise ValueError(f"{self.id}: a registered analysis names its preregistration, and only it does")

    @property
    def run(self) -> Callable[[], dict]:
        return self.module.run

    @property
    def headline(self) -> Callable[[dict], list[Headline]]:
        return self.module.headline

    @property
    def requiem_id(self) -> str:
        return f"results/{self.family}/{self.id}/headline"

    @property
    def result_path(self):
        return paths.RESULTS / self.family / f"{self.id}.json"

    @property
    def fingerprint_path(self):
        return paths.RESULTS / self.family / f"{self.id}.fingerprint"

    @property
    def source_path(self):
        return paths.ROOT / (self.module.__name__.replace(".", "/") + ".py")


def registry() -> dict[str, Analysis]:
    """Every analysis in every family, keyed by id, in dependency order."""
    import analyses
    found: dict[str, Analysis] = {}
    for fam in pkgutil.iter_modules(analyses.__path__):
        if not fam.ispkg:
            continue
        pkg = importlib.import_module(f"analyses.{fam.name}")
        for m in pkgutil.iter_modules(pkg.__path__):
            mod = importlib.import_module(f"analyses.{fam.name}.{m.name}")
            a = getattr(mod, "ANALYSIS", None)
            if a is None:
                continue
            if a.id in found:
                raise ValueError(f"duplicate analysis id {a.id}")
            a.module = mod
            found[a.id] = a
    order: list[str] = []

    def visit(i, seen=()):
        if i in order:
            return
        if i in seen:
            raise ValueError(f"dependency cycle at {i}")
        for d in found[i].depends:
            if d not in found:
                raise ValueError(f"{i} depends on unknown analysis {d}")
            visit(d, seen + (i,))
        order.append(i)
    for i in sorted(found):
        visit(i)
    return {i: found[i] for i in order}
