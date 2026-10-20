"""`uv run bomstylo <command>`. Run `uv run bomstylo --help` for the list."""
from __future__ import annotations

import argparse
import sys
import time

from . import paths


def _select(reg, ids, family):
    if ids:
        missing = [i for i in ids if i not in reg]
        if missing:
            sys.exit(f"unknown analysis: {', '.join(missing)}")
        return [reg[i] for i in reg if i in ids]
    return [a for a in reg.values() if family is None or a.family == family]


def cmd_run(args):
    from . import results
    from .analysis import registry
    reg = registry()
    todo = _select(reg, args.ids, args.family)
    for a in todo:
        if args.stale_only and results.status(a)[0] == "current":
            print(f"{a.id:<22} current, skipped")
            continue
        t = time.time()
        data = a.run()
        heads = a.headline(data)
        comp = results.inputs(a)
        results.save(a, data, heads, comp)
        results.write_fingerprint(a)
        print(f"{a.id:<22} done in {time.time() - t:5.1f}s")
        for h in heads:
            print(f"    {h.text}")


def cmd_fingerprint(args):
    from . import results
    from .analysis import registry
    changed = []
    for a in registry().values():
        old = a.fingerprint_path.read_text().strip() if a.fingerprint_path.exists() else ""
        fp, _ = results.write_fingerprint(a)
        if old != f"sha256:{fp}":
            changed.append(a.id)
    for i in changed:
        print(f"fingerprint changed: {i}")
    if args.check and changed:
        sys.exit("fingerprints were out of date; they have been refreshed, so stage them and commit again")


def cmd_status(args):
    from . import results
    from .analysis import registry
    for a in _select(registry(), args.ids, args.family):
        st, changed = results.status(a)
        print(f"{a.id:<22} {st:<8} {a.label}")
        for c in changed:
            print(f"    changed: {c}")


def cmd_record(args):
    from . import requiem_bridge
    from .analysis import registry
    for a in _select(registry(), args.ids, args.family):
        print(requiem_bridge.record(a))


def cmd_verify(args):
    from . import checksums, results
    probs = []
    for s in results.manifest()["sources"]:
        probs += checksums.verify(s)
    print("\n".join(probs) if probs else "all prepared corpus files match their pinned hashes")
    sys.exit(1 if probs else 0)


def cmd_checksums(args):
    """Maintainer step: pin what is on disk (after checking it is what you mean to pin)."""
    import re
    from . import checksums, results
    text = paths.MANIFEST.read_text(encoding="utf-8")
    for s in results.manifest()["sources"]:
        if args.ids and s["id"] not in args.ids:
            continue
        digest = checksums.write(s)
        block = re.search(rf"(  - id: {re.escape(s['id'])}\n(?:    .*\n|      .*\n|\n(?!  - id))*)", text).group(1)
        new = re.sub(r"      digest: \w+\n", "", block)
        new = re.sub(r"(      paths: .*\n)", rf"\1      digest: {digest}\n", new)
        text = text.replace(block, new)
        print(f"{s['id']:<18} {digest}")
    paths.MANIFEST.write_text(text, encoding="utf-8")


def cmd_fetch(args):
    from . import fetch
    fetch.main(args.ids, force=args.force)


def cmd_report(args):
    from .report import build
    print(build.main(args.family))


def cmd_index(args):
    from . import index
    print(index.write())


def cmd_install_hooks(args):
    from . import hooks
    print(f"installed the bomstylo block in {hooks.install()}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="bomstylo", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_, ids=True, family=True):
        s = sub.add_parser(name, help=help_)
        if ids:
            s.add_argument("ids", nargs="*", help="analysis ids (default: all)")
        if family:
            s.add_argument("--family", help="limit to one family, e.g. wayhi")
        s.set_defaults(fn=fn)
        return s

    s = add("run", cmd_run, "run analyses and write their results and fingerprints")
    s.add_argument("--stale-only", action="store_true", help="skip analyses whose result is current")
    s = add("fingerprint", cmd_fingerprint, "refresh every fingerprint file without running anything",
            ids=False, family=False)
    s.add_argument("--check", action="store_true", help="exit 1 if any fingerprint changed (git hook)")
    add("status", cmd_status, "show which results are current, stale or missing")
    add("record", cmd_record, "write each result's headline to Requiem (then `requiem commit`)")
    add("verify", cmd_verify, "check prepared corpus files against their pinned hashes", ids=False, family=False)
    s = sub.add_parser("checksums", help="maintainers: pin the prepared files on disk in the manifest")
    s.add_argument("ids", nargs="*")
    s.set_defaults(fn=cmd_checksums)
    s = sub.add_parser("fetch", help="download, verify and prepare source texts")
    s.add_argument("ids", nargs="*", help="source ids from corpora/manifest.yaml (default: all)")
    s.add_argument("--force", action="store_true", help="re-download even if present")
    s.set_defaults(fn=cmd_fetch)
    s = sub.add_parser("report", help="build reports/<family>.md from the result files")
    s.add_argument("family", nargs="?", default="wayhi")
    s.set_defaults(fn=cmd_report)
    add("index", cmd_index, "regenerate ANALYSES.md from the registry", ids=False, family=False)
    add("install-hooks", cmd_install_hooks, "add the fingerprint/index check to .git/hooks/pre-commit",
        ids=False, family=False)

    args = p.parse_args(argv)
    paths.RESULTS.mkdir(exist_ok=True)
    args.fn(args)


if __name__ == "__main__":
    main()
