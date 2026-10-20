"""Pre-registrations are never edited (constitution III): each file must still
have the hash recorded as current in preregistrations/README.md."""
import re

from bomstylo import paths
from bomstylo.results import sha_file


def test_each_preregistration_has_its_current_hash():
    readme = (paths.PREREGISTRATIONS / "README.md").read_text(encoding="utf-8")
    current = {}
    for name, h, state in re.findall(r"\| (PREREGISTRATION_\d+\.md) \| `([0-9a-f]{64})` \| [^|]+ \| ([^|]+) \|", readme):
        if "current" in state:
            current[name] = h
    files = sorted(p.name for p in paths.PREREGISTRATIONS.glob("PREREGISTRATION_*.md"))
    assert sorted(current) == files
    for name, h in current.items():
        assert sha_file(paths.PREREGISTRATIONS / name) == h, f"{name} was edited"
