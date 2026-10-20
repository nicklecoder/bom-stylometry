"""`bomstylo install-hooks`: add a bomstylo block to .git/hooks/pre-commit.

The block refreshes every fingerprint and ANALYSES.md, and stops the commit if
either changed, so the change gets staged with the code that caused it. That
is what keeps Requiem's `stale` flag honest: a result's Requiem record is
anchored to line 1 of its fingerprint file, so once a changed fingerprint is
committed, `requiem get` reports the record stale until the analysis is re-run
and re-recorded. Requiem's own block in the same hook is left alone.
"""
from __future__ import annotations

import stat

from . import paths

BEGIN, END = "# >>> bomstylo >>>", "# <<< bomstylo <<<"
BLOCK = f"""{BEGIN}
if command -v uv >/dev/null 2>&1; then
  uv run --quiet bomstylo fingerprint --check || exit 1
  uv run --quiet bomstylo index >/dev/null
  git diff --quiet -- ANALYSES.md || {{ echo "ANALYSES.md was out of date and has been regenerated; stage it and commit again"; exit 1; }}
fi
{END}
"""


def install() -> str:
    hook = paths.ROOT / ".git" / "hooks" / "pre-commit"
    if not hook.parent.exists():
        raise SystemExit("not a git repository (no .git/hooks)")
    text = hook.read_text(encoding="utf-8") if hook.exists() else "#!/bin/sh\n"
    if BEGIN in text:
        a, b = text.index(BEGIN), text.index(END) + len(END) + 1
        text = text[:a] + BLOCK + text[b:]
    else:
        text = text.rstrip("\n") + "\n" + BLOCK
    hook.write_text(text, encoding="utf-8")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return str(hook.relative_to(paths.ROOT))
