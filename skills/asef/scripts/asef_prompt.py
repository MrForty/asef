#!/usr/bin/env python3
"""Build the ASEF activation prompt from a one-line goal.

The `asef` skill calls this so the user never pastes the framework prompt by
hand. The script never carries a copy of the prompt: it reads
`prompt universale ASEF.txt` from the framework root it resolves and fills
only the request block at its end. Everything before the block is emitted
verbatim, so the prompt stays one file with one home.

    python3 asef_prompt.py build --request "..." [fields]   # full prompt on stdout
    python3 asef_prompt.py scan                              # root, versions, artifacts
    python3 asef_prompt.py init                              # copy the framework into ./asef

Exit codes: 0 ok, 1 bad arguments, 2 no framework found.
Python 3.11+, standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

PROMPT_FILE = "prompt universale ASEF.txt"
KERNEL_FILE = "ASEF.md"

ROUTES = ["GREENFIELD", "MODIFY", "DIAGNOSE", "IMPROVE", "REUSE", "REVIEW_ONLY", "QA_ONLY", "RELEASE"]
RELEASE_LEVELS = ["nessuna", "commit", "pull request", "merge", "deploy"]

# Canonical ASEF artifacts (ARTIFACTS.md) plus the project documents ASEF reuses.
ARTIFACT_FILES = [
    "PROJECT.md", "SPEC.md", "PLAN.md", "STATE.md", "DECISIONS.md",
    "RESEARCH.md", "LEARNINGS.md", "AGENTS.md", "CLAUDE.md", "README.md",
]
ARTIFACT_DIRS = ["tasks", "docs"]

# Request-block context fields, matched by their leading words.
CONTEXT_FIELDS = {
    "who": "chi ha il problema",
    "today": "come lo risolve oggi",
    "asked": "chi me l'ha chiesto",
    "verify": "come capisco che funziona",
}

SKILL_DIR = Path(__file__).resolve().parent.parent


def die(message: str, code: int = 1) -> "NoReturn":  # noqa: F821 - typing only
    print(f"asef_prompt: {message}", file=sys.stderr)
    raise SystemExit(code)


def is_root(path: Path) -> bool:
    return (path / KERNEL_FILE).is_file() and (path / PROMPT_FILE).is_file()


def resolve_root(project: Path, explicit: Path | None) -> Path:
    """Framework root, in the order SKILL.md documents."""
    if explicit is not None:
        if not is_root(explicit):
            die(f"{explicit} is not an ASEF framework root", 2)
        return explicit.resolve()
    candidates = [
        project / "asef",             # framework dropped into the project
        project,                      # the project is the framework repository
        SKILL_DIR / "framework",      # copy bundled by install.py --bundle-framework
        SKILL_DIR.parent.parent,      # skill living inside the repository (skills/asef)
    ]
    for candidate in candidates:
        if is_root(candidate):
            return candidate.resolve()
    die(
        "no ASEF framework found: expected `asef/ASEF.md` in the project "
        "(run `asef_prompt.py init`, or copy the repository into `asef/`)",
        2,
    )


def kernel_version(root: Path) -> str | None:
    match = re.search(r"^\s*version:\s*([0-9]+(?:\.[0-9]+)*)\s*$", read(root / KERNEL_FILE), re.M)
    return match.group(1) if match else None


def prompt_version(prompt: str) -> str | None:
    match = re.search(r"kernel\s+v([0-9]+(?:\.[0-9]+)*)", prompt)
    return match.group(1) if match else None


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def scan_artifacts(project: Path) -> list[str]:
    found = [name for name in ARTIFACT_FILES if (project / name).is_file()]
    for name in ARTIFACT_DIRS:
        folder = project / name
        if folder.is_dir() and any(folder.iterdir()):
            found.append(f"{name}/")
    return found


def display_root(root: Path, project: Path) -> str:
    try:
        return root.relative_to(project.resolve()).as_posix()
    except ValueError:
        return root.as_posix()


def rewrite_paths(prompt: str, root_display: str) -> str:
    """The prompt names the framework as `asef/`; point it at the real root."""
    if root_display in ("asef", ""):
        return prompt
    return prompt.replace("`asef/", f"`{root_display}/")


def fill_request_block(block: str, args: argparse.Namespace, artifacts: list[str]) -> str:
    """Fill the block line by line; unknown lines pass through unchanged."""
    out: list[str] = []
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("Richiesta:"):
            out.append(f"Richiesta: {args.request}")
        elif stripped.startswith("Autorizzazioni di rilascio:"):
            out.append(f"Autorizzazioni di rilascio: {args.release}")
        elif stripped.startswith("Artefatti già esistenti:"):
            out.append("Artefatti già esistenti: " + (", ".join(artifacts) if artifacts else "nessuno"))
        elif stripped in ("Vincoli non negoziabili:", "Non-goal:"):
            items = args.constraint if stripped.startswith("Vincoli") else args.non_goal
            out.append(line)
            i += 1
            while i < len(lines) and lines[i].strip() == "-":  # template placeholder rows
                i += 1
            out.extend(f"- {item}" for item in items) if items else out.append("-")
            continue
        elif stripped.startswith("- ") and stripped.endswith(":"):
            value = ""
            for key, prefix in CONTEXT_FIELDS.items():
                if stripped[2:].startswith(prefix):
                    value = getattr(args, key) or ""
            out.append(f"{line} {value}".rstrip())
        else:
            out.append(line)
        i += 1
    return "\n".join(out)


def build_prompt(root: Path, project: Path, args: argparse.Namespace) -> str:
    prompt = read(root / PROMPT_FILE)
    match = re.search(r"```\n(Richiesta:.*?)```", prompt, re.S)
    if not match:
        die(f"{PROMPT_FILE} has no request block starting with `Richiesta:`")

    artifacts = list(dict.fromkeys(scan_artifacts(project) + list(args.artifact)))
    block = fill_request_block(match.group(1).strip(), args, artifacts)
    filled = prompt[: match.start(1)] + block + "\n" + prompt[match.end(1) :]

    trailer: list[str] = []
    if args.spec:
        trailer.append(f"Esiste già una specifica deliberata: `{args.spec}`. Route: partire da `specification`.")
    if args.route:
        trailer.append(f"Route imposta dall'utente: `{args.route}`.")
    if trailer:
        filled = filled.rstrip("\n") + "\n\n" + "\n".join(trailer) + "\n"

    filled = rewrite_paths(filled, display_root(root, project))
    return block + "\n" if args.block_only else filled


def cmd_scan(root: Path, project: Path) -> int:
    prompt = read(root / PROMPT_FILE)
    info = {
        "root": display_root(root, project),
        "kernel_version": kernel_version(root),
        "prompt_version": prompt_version(prompt),
        "artifacts": scan_artifacts(project),
        "state": (project / "STATE.md").is_file(),
    }
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def cmd_init(project: Path, source: Path | None) -> int:
    target = project / "asef"
    if is_root(target):
        print(f"asef_prompt: `{display_root(target, project)}` already holds an ASEF framework", file=sys.stderr)
        return 0
    if target.exists():
        die(f"{target} exists but is not an ASEF framework root")
    candidates = [source] if source else [SKILL_DIR / "framework", SKILL_DIR.parent.parent]
    origin = next((c for c in candidates if c and is_root(c)), None)
    if origin is None:
        die(
            "no framework copy to install from: clone https://github.com/MrForty/asef into `asef/`, "
            "or reinstall the skill with `install.py --bundle-framework`",
            2,
        )
    shutil.copytree(origin, target, ignore=shutil.ignore_patterns(".git", "__pycache__", "skills"))
    print(f"asef_prompt: framework v{kernel_version(target)} installed in `asef/`", file=sys.stderr)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the ASEF activation prompt from a goal.")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="project directory (default: cwd)")
    parser.add_argument("--root", type=Path, help="framework root (default: auto-detect)")
    sub = parser.add_subparsers(dest="command")

    build = sub.add_parser("build", help="print the full activation prompt")
    build.add_argument("--request", required=True, help="one sentence: what must be done")
    build.add_argument("--who", help="who has the problem")
    build.add_argument("--today", help="how they solve it today")
    build.add_argument("--asked", help="who asked, and what they did")
    build.add_argument("--verify", help="how success is observed")
    build.add_argument("--constraint", action="append", default=[], help="non-negotiable constraint (repeatable)")
    build.add_argument("--non-goal", action="append", default=[], help="explicit non-goal (repeatable)")
    build.add_argument("--release", choices=RELEASE_LEVELS, default="nessuna", help="release authorization")
    build.add_argument("--artifact", action="append", default=[], help="extra existing artifact (repeatable)")
    build.add_argument("--spec", help="path of an already deliberated specification")
    build.add_argument("--route", choices=ROUTES, help="route imposed by the user")
    build.add_argument("--block-only", action="store_true", help="print only the filled request block")

    sub.add_parser("scan", help="report framework root, versions and artifacts as JSON")
    init = sub.add_parser("init", help="copy the framework into <project>/asef")
    init.add_argument("--source", type=Path, help="framework copy to install from")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.error("choose a command: build, scan or init")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    project = args.project.resolve()

    if args.command == "init":
        return cmd_init(project, args.root or args.source)

    root = resolve_root(project, args.root)
    if args.command == "scan":
        return cmd_scan(root, project)

    kernel = kernel_version(root)
    declared = prompt_version(read(root / PROMPT_FILE))
    if kernel != declared:
        print(
            f"asef_prompt: warning: prompt activates kernel v{declared} but {KERNEL_FILE} declares v{kernel}; "
            "the kernel wins",
            file=sys.stderr,
        )
    sys.stdout.write(build_prompt(root, project, args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
