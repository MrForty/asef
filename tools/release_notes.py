#!/usr/bin/env python3
"""Derive a GitHub release from the documents that already declare the version.

`ASEF.md` owns the version and `CHANGELOG.md` owns what changed, so a release
must not restate either: this script reads both, checks they agree, and emits
the tag, the title and the notes the release workflow publishes.

    python3 tools/release_notes.py --ref v1.8.0 --out notes.md
    python3 tools/release_notes.py --requested 1.8.0 --title "ASEF 1.8.0 - ..."
    python3 tools/release_notes.py --self-test

Tags may or may not carry the leading `v`: this repository has both forms in
its history, so a pushed tag is published exactly as pushed, and only a
release with no tag to go by gets the preferred `vX.Y.Z` form.

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


def changelog_section(root: Path, version: str, fallback: str = "") -> str:
    """Body of the `## <version>` entry, up to the next version heading.

    A tag carries three components while the kernel declares two, so `v1.8.0`
    looks for `## 1.8.0` and then falls back to the entry the kernel names.
    """
    text = read(root / "CHANGELOG.md")
    candidates = [version] + ([fallback] if fallback and fallback != version else [])
    for candidate in candidates:
        pattern = rf"^##\s+{re.escape(candidate)}\s*$\n(.*?)(?=^##\s+[0-9]|\Z)"
        match = re.search(pattern, text, re.M | re.S)
        if not match:
            continue
        body = match.group(1).strip()
        if not body:
            raise SystemExit(f"release: the `## {candidate}` entry in CHANGELOG.md is empty")
        return body
    named = " or ".join(f"`## {c}`" for c in candidates)
    raise SystemExit(f"release: CHANGELOG.md has no {named} entry")


def strip_prefix(tag: str) -> str:
    """`v1.8.0` and `1.8.0` name the same version; both forms are in use here."""
    tag = tag.strip()
    return tag[1:] if tag[:1].lower() == "v" else tag


def resolve_version(root: Path, requested: str, ref: str) -> str:
    """An explicit request wins, then the tag being pushed, then the kernel."""
    version = requested.strip() or strip_prefix(ref) or kernel_version(root)
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version):
        raise SystemExit(f"release: `{version}` is not a version number")
    return version


def padded(version: str) -> str:
    """Three components, since the kernel declares two (1.8 -> 1.8.0)."""
    parts = version.split(".")
    return ".".join(parts + ["0"] * (3 - len(parts))) if len(parts) < 3 else version


def tag_for(version: str) -> str:
    """The form a release is given when no pushed tag names it already."""
    return "v" + padded(version)


def release_tag(version: str, ref: str = "") -> str:
    """A pushed tag is authoritative: publishing under any other spelling
    would leave its release detached and create a second tag."""
    return ref.strip() or tag_for(version)


def equivalent_versions(version: str) -> list[str]:
    """Numbers naming the same release, longest first.

    A trailing zero component is optional, so `1.8.0` and `1.8` are one
    release however the caller spelled it. Derived from the number rather than
    from the requested string, or asking for `1.8.0` would miss a release
    already published as `1.8`. Never trimmed below two components, so a bare
    `2` cannot collide with an unrelated tag.
    """
    forms = [padded(version)]
    trimmed = version.split(".")
    while len(trimmed) > 2 and trimmed[-1] == "0":
        trimmed.pop()
        forms.append(".".join(trimmed))
    forms.append(version)
    return list(dict.fromkeys(forms))


def tag_candidates(version: str, ref: str = "") -> list[str]:
    """Spellings that would name this same release, preferred one first.

    Without a pushed tag the workflow has to find an existing release before
    inventing a tag for it, or a release already published as `1.8` would be
    duplicated as `v1.8.0`.
    """
    if ref.strip():
        return [ref.strip()]
    spellings = [f"{prefix}{form}" for form in equivalent_versions(version) for prefix in ("v", "")]
    return list(dict.fromkeys(spellings))


def check_alignment(root: Path, version: str) -> None:
    """A release may only ship the version the kernel itself declares."""
    declared = kernel_version(root)
    if not version.startswith(declared):
        raise SystemExit(
            f"release: asked to release {version} but ASEF.md declares {declared}; "
            "bump the kernel first, or release the declared version"
        )


def build(root: Path, version: str, title: str, ref: str = "") -> tuple[str, str, str]:
    check_alignment(root, version)
    notes = changelog_section(root, version, fallback=kernel_version(root))
    notes += f"\n\n---\n\nInstallation and usage: [README]({README_LINK}).\n"
    # The title names the version, never the tag: a tag without the `v` would
    # otherwise lose its first digit to the prefix strip.
    return release_tag(version, ref), title.strip() or f"ASEF {padded(version)}", notes


def self_test() -> int:
    """Exercise the rules on a scratch copy: the workflow has no other test."""
    failures: list[str] = []

    def check(label: str, condition: bool) -> None:
        print(f"{'PASS' if condition else 'FAIL'}  {label}")
        if not condition:
            failures.append(label)

    check("tag pads the kernel version to three components", tag_for("1.8") == "v1.8.0")
    check("tag keeps a full version untouched", tag_for("1.8.2") == "v1.8.2")
    check("the `v` prefix is optional when reading a tag",
          strip_prefix("v1.8.0") == "1.8.0" and strip_prefix("1.8.0") == "1.8.0")
    check("a pushed tag is published exactly as pushed",
          release_tag("1.8", "1.8") == "1.8" and release_tag("1.8", "v1.8.0") == "v1.8.0")
    check("without a pushed tag the preferred form is used", release_tag("1.8") == "v1.8.0")
    check("candidates cover both spellings, preferred first",
          tag_candidates("1.8") == ["v1.8.0", "1.8.0", "v1.8", "1.8"])
    check("a padded request still covers the short spellings",
          tag_candidates("1.8.0") == ["v1.8.0", "1.8.0", "v1.8", "1.8"])
    check("a patch version has no shorter spelling",
          tag_candidates("1.8.2") == ["v1.8.2", "1.8.2"])
    check("candidates never trim below two components",
          tag_candidates("2.0.0") == ["v2.0.0", "2.0.0", "v2.0", "2.0"])
    check("a pushed tag is the only candidate", tag_candidates("1.8", "1.8") == ["1.8"])

    with tempfile.TemporaryDirectory() as raw:
        work = Path(raw)
        (work / "ASEF.md").write_text("```yaml\nasef:\n  version: 1.8\n```\n", encoding="utf-8")
        (work / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 1.8\n\nSummary line.\n\n- entry\n\n## 1.7\n\nOlder.\n", encoding="utf-8"
        )

        check("version falls back to the kernel", resolve_version(work, "", "") == "1.8")
        check("a pushed tag names the version", resolve_version(work, "", "v1.8.0") == "1.8.0")
        check("a tag without the prefix names it too", resolve_version(work, "", "1.8.0") == "1.8.0")
        check("an explicit request wins", resolve_version(work, "1.8", "v9.9.9") == "1.8")

        tag, title, notes = build(work, "1.8", "")
        check("tag derived from the version", tag == "v1.8.0")
        check("default title names the release", title == "ASEF 1.8.0")
        check("notes carry the changelog entry", "Summary line." in notes and "- entry" in notes)
        check("notes stop at the previous version", "Older." not in notes)
        check("notes link the README", README_LINK in notes)

        _, custom, _ = build(work, "1.8", "ASEF 1.8.0 - The skill")
        check("an explicit title is kept", custom == "ASEF 1.8.0 - The skill")

        # Pushing `v1.8.0` resolves to 1.8.0, which the changelog never names.
        tag, title, notes = build(work, "1.8.0", "")
        check("a three-component tag finds the entry the kernel names",
              tag == "v1.8.0" and "Summary line." in notes and "Older." not in notes)

        # A tag without the prefix must not be republished under another name,
        # and must not lose its first digit to the title.
        tag, title, notes = build(work, "1.8", "", ref="1.8")
        check("a prefixless tag keeps its name and gets a sane title",
              tag == "1.8" and title == "ASEF 1.8.0" and "Summary line." in notes)
        tag, title, _ = build(work, "1.8.0", "", ref="v1.8.0")
        check("a prefixed tag keeps its name", tag == "v1.8.0" and title == "ASEF 1.8.0")

        for label, version in (("a version the kernel does not declare", "2.0"),
                               ("a version outside the declared line", "1.90")):
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
    tag, title, notes = build(args.root, version, args.title, args.ref)
    candidates = tag_candidates(version, args.ref)

    if args.out:
        args.out.write_text(notes, encoding="utf-8")
    if args.github_output:
        target = os.environ.get("GITHUB_OUTPUT")
        line = f"tag={tag}\ntitle={title}\ntags={' '.join(candidates)}\n"
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
