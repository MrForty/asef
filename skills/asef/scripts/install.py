#!/usr/bin/env python3
"""Install the `asef` skill where a coding agent discovers skills.

    python3 install.py --agent claude                 # ./.claude/skills/asef
    python3 install.py --agent codex --user           # ~/.agents/skills/asef
    python3 install.py --dest path/to/skills          # any agent, any path
    python3 install.py --agent claude --bundle-framework
    python3 install.py --list

Copies by default; `--link` symlinks instead so the skill follows the
repository. `--bundle-framework` copies the framework next to the skill, so
`/asef init` and `/asef <goal>` work in projects that carry no `asef/` folder.
Agent paths are the documented defaults; use `--dest` when yours differ.
Python 3.11+, standard library only.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_NAME = "asef"

# agent: (project-level skills directory, user-level skills directory)
AGENTS: dict[str, tuple[str, str]] = {
    "claude": (".claude/skills", "~/.claude/skills"),
    "codex": (".agents/skills", "~/.agents/skills"),
    "agents": (".agents/skills", "~/.agents/skills"),
    "cursor": (".cursor/skills", "~/.cursor/skills"),
    "copilot": (".github/skills", "~/.copilot/skills"),
    "gemini": (".gemini/skills", "~/.gemini/skills"),
    "opencode": (".opencode/skills", "~/.config/opencode/skills"),
}


def framework_root() -> Path | None:
    for candidate in (SKILL_DIR / "framework", SKILL_DIR.parent.parent):
        if (candidate / "ASEF.md").is_file() and (candidate / "prompt universale ASEF.txt").is_file():
            return candidate
    return None


def destinations(args: argparse.Namespace) -> list[Path]:
    targets: list[Path] = []
    for agent in args.agent:
        project_dir, user_dir = AGENTS[agent]
        base = Path(user_dir).expanduser() if args.user else args.project / project_dir
        targets.append(base / SKILL_NAME)
    if args.dest:
        targets.append(args.dest / SKILL_NAME)
    return [t.resolve() for t in dict.fromkeys(targets)]


def install(target: Path, link: bool, force: bool, bundle: bool) -> None:
    if target.exists() or target.is_symlink():
        if not force:
            raise SystemExit(f"install: {target} exists; pass --force to replace it")
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    if link:
        os.symlink(SKILL_DIR, target, target_is_directory=True)
        print(f"install: linked {target} -> {SKILL_DIR}")
        return

    shutil.copytree(SKILL_DIR, target, ignore=shutil.ignore_patterns("__pycache__", "framework"))
    if bundle:
        root = framework_root()
        if root is None:
            raise SystemExit("install: no framework to bundle; run from a clone of the ASEF repository")
        shutil.copytree(
            root, target / "framework",
            ignore=shutil.ignore_patterns(".git", ".github", "__pycache__", "skills", "docs", "examples"),
        )
    print(f"install: copied skill to {target}" + (" (framework bundled)" if bundle else ""))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install the asef skill for a coding agent.")
    parser.add_argument("--agent", action="append", choices=sorted(AGENTS), default=[], help="target agent (repeatable)")
    parser.add_argument("--dest", type=Path, help="skills directory of any other agent")
    parser.add_argument("--user", action="store_true", help="install at user level instead of project level")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="project directory (default: cwd)")
    parser.add_argument("--link", action="store_true", help="symlink instead of copy")
    parser.add_argument("--force", action="store_true", help="replace an existing installation")
    parser.add_argument("--bundle-framework", action="store_true", help="copy the framework next to the skill")
    parser.add_argument("--list", action="store_true", help="print the known agent paths and exit")
    args = parser.parse_args(argv)

    if args.list:
        print(f"{'agent':<10}{'project level':<22}user level")
        for agent, (project_dir, user_dir) in AGENTS.items():
            print(f"{agent:<10}{project_dir + '/asef':<22}{user_dir}/asef")
        return 0
    if not args.agent and not args.dest:
        parser.error("choose at least one --agent, or a --dest directory")
    if args.link and args.bundle_framework:
        parser.error("--bundle-framework copies files; it cannot be combined with --link")

    for target in destinations(args):
        install(target, args.link, args.force, args.bundle_framework)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
