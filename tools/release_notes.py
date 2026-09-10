#!/usr/bin/env python3
"""Derive a GitHub release from the documents that already declare the version.

`ASEF.md` owns the version and `CHANGELOG.md` owns what changed, so a release
must not restate either: this script reads both, checks they agree, and emits
the tag, the title and the notes the release workflow publishes.

    python3 tools/release_notes.py --ref v1.8.0 --out notes.md
    python3 tools/release_notes.py --requested 1.8.0 --title "ASEF 1.8.0 - ..."
    python3 tools/release_notes.py --self-test

Exit code 0 when the release is coherent, 1 when it is not.
Python 3.11+, standard library only.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_LINK = "https://github.com/MrForty/asef#readme"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def kernel_version(root: Path) -> str:
    match = re.search(r"^\s*version:\s*([0-9]+(?:\.[0-9]+)*)\s*$", read(root / "ASEF.md"), re.M)
    if not match:
        raise SystemExit("release: ASEF.md declares no version")
    return match.group(1)


def changelog_section(root: Path, version: str) -> str:
    """Body of the `## <version>` entry, up to the next version heading."""
    text = read(root / "CHANGELOG.md")
    pattern = rf"^##\s+{re.escape(version)}\s*$\n(.*?)(?=^##\s+[0-9]|\Z)"
    match = re.search(pattern, text, re.M | re.S)
    if not match:
        raise SystemExit(f"release: CHANGELOG.md has no `## {version}` entry")
    body = match.group(1).strip()
    if not body:
        raise SystemExit(f"release: the `## {version}` entry in CHANGELOG.md is empty")
    return body


def resolve_version(root: Path, requested: str, ref: str) -> str:
    """An explicit request wins, then the tag being pushed, then the kernel."""
    version = requested.strip() or (ref.strip()[1:] if ref.strip().startswith("v") else "")
    version = version or kernel_version(root)
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version):
        raise SystemExit(f"release: `{version}` is not a version number")
    return version


def tag_for(version: str) -> str:
    """Tags carry three components; the kernel declares two (1.8 -> v1.8.0)."""
    parts = version.split(".")
    while len(parts) < 3:
        parts.append("0")
    return "v" + ".".join(parts)


def check_alignment(root: Path, version: str) -> None:
    """A release may only ship the version the kernel itself declares."""
    declared = kernel_version(root)
    if not version.startswith(declared):
        raise SystemExit(
            f"release: asked to release {version} but ASEF.md declares {declared}; "
            "bump the kernel first, or release the declared version"
        )


def build(root: Path, version: str, title: str) -> tuple[str, str, str]:
    check_alignment(root, version)
    notes = changelog_section(root, version)
    notes += f"\n\n---\n\nInstallation and usage: [README]({README_LINK}).\n"
    return tag_for(version), title.strip() or f"ASEF {tag_for(version)[1:]}", notes


def self_test() -> int:
    """Exercise the rules on a scratch copy: the workflow has no other test."""
    failures: list[str] = []

    def check(label: str, condition: bool) -> None:
        print(f"{'PASS' if condition else 'FAIL'}  {label}")
        if not condition:
            failures.append(label)

    check("tag pads the kernel version to three components", tag_for("1.8") == "v1.8.0")
    check("tag keeps a full version untouched", tag_for("1.8.2") == "v1.8.2")

    with tempfile.TemporaryDirectory() as raw:
        work = Path(raw)
        (work / "ASEF.md").write_text("```yaml\nasef:\n  version: 1.8\n```\n", encoding="utf-8")
        (work / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 1.8\n\nSummary line.\n\n- entry\n\n## 1.7\n\nOlder.\n", encoding="utf-8"
        )

        check("version falls back to the kernel", resolve_version(work, "", "") == "1.8")
        check("a pushed tag names the version", resolve_version(work, "", "v1.8.0") == "1.8.0")
        check("an explicit request wins", resolve_version(work, "1.8", "v9.9.9") == "1.8")

        tag, title, notes = build(work, "1.8", "")
        check("tag derived from the version", tag == "v1.8.0")
        check("default title names the release", title == "ASEF 1.8.0")
        check("notes carry the changelog entry", "Summary line." in notes and "- entry" in notes)
        check("notes stop at the previous version", "Older." not in notes)
        check("notes link the README", README_LINK in notes)

        _, custom, _ = build(work, "1.8", "ASEF 1.8.0 - The skill")
        check("an explicit title is kept", custom == "ASEF 1.8.0 - The skill")

        for label, version in (("a version the kernel does not declare", "2.0"),
                               ("a version with no changelog entry", "1.8.5")):
            try:
                build(work, version, "")
            except SystemExit:
                check(f"refuses {label}", True)
            else:
                check(f"refuses {label}", False)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed.")
        return 1
    print("Release notes checks passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Derive a release from ASEF.md and CHANGELOG.md.")
    parser.add_argument("--root", type=Path, default=ROOT, help="framework root")
    parser.add_argument("--requested", default="", help="version to release (workflow input)")
    parser.add_argument("--ref", default="", help="tag being pushed, when there is one")
    parser.add_argument("--title", default="", help="release title (default: ASEF <version>)")
    parser.add_argument("--out", type=Path, help="write the notes to this file")
    parser.add_argument("--github-output", action="store_true", help="emit tag and title for GITHUB_OUTPUT")
    parser.add_argument("--self-test", action="store_true", help="check the rules and exit")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    version = resolve_version(args.root, args.requested, args.ref)
    tag, title, notes = build(args.root, version, args.title)

    if args.out:
        args.out.write_text(notes, encoding="utf-8")
    if args.github_output:
        target = os.environ.get("GITHUB_OUTPUT")
        line = f"tag={tag}\ntitle={title}\n"
        if target:
            with open(target, "a", encoding="utf-8") as handle:
                handle.write(line)
        else:
            sys.stdout.write(line)
    elif not args.out:
        sys.stdout.write(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
