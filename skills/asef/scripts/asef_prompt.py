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
    python3 asef_prompt.py init --upgrade                    # refresh ./asef from a newer copy
    python3 asef_prompt.py doctor [--json]                   # diagnose the installation

Exit codes: 0 ok, 1 bad arguments (or a failed doctor check), 2 no framework found.
Python 3.11+, standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

# The activation prompt in each language it ships in. Italian is the original
# and the default; every other file mirrors it line for line (the linter checks
# the request blocks share one shape).
PROMPT_FILES = {"it": "prompt universale ASEF.txt", "en": "ASEF universal prompt.txt"}
PROMPT_FILE = PROMPT_FILES["it"]
KERNEL_FILE = "ASEF.md"

ROUTES = ["GREENFIELD", "MODIFY", "DIAGNOSE", "IMPROVE", "REUSE", "REVIEW_ONLY", "QA_ONLY", "RELEASE"]
RELEASE_LEVELS = ["none", "nessuna", "commit", "pull request", "merge", "deploy"]

# Canonical ASEF artifacts (ARTIFACTS.md) plus the project documents ASEF reuses.
ARTIFACT_FILES = [
    "PROJECT.md", "SPEC.md", "PLAN.md", "STATE.md", "DECISIONS.md",
    "RESEARCH.md", "LEARNINGS.md", "AGENTS.md", "CLAUDE.md", "README.md",
]
ARTIFACT_DIRS = ["tasks", "docs"]

# Request-block labels per language. Context fields match by their leading words.
LABELS = {
    "it": {
        "request": "Richiesta:",
        "constraints": "Vincoli non negoziabili:",
        "non_goals": "Non-goal:",
        "release": "Autorizzazioni di rilascio:",
        "artifacts": "Artefatti già esistenti:",
        "none_release": "nessuna",
        "none_artifacts": "nessuno",
        "context": {
            "who": "chi ha il problema",
            "today": "come lo risolve oggi",
            "asked": "chi me l'ha chiesto",
            "verify": "come capisco che funziona",
        },
        "spec": "Esiste già una specifica deliberata: `{}`. Route: partire da `specification`.",
        "route": "Route imposta dall'utente: `{}`.",
    },
    "en": {
        "request": "Request:",
        "constraints": "Non-negotiable constraints:",
        "non_goals": "Non-goals:",
        "release": "Release authorizations:",
        "artifacts": "Existing artifacts:",
        "none_release": "none",
        "none_artifacts": "none",
        "context": {
            "who": "who has the problem",
            "today": "how they solve it today",
            "asked": "who asked me",
            "verify": "how I know it works",
        },
        "spec": "A deliberate specification already exists: `{}`. Route: start from `specification`.",
        "route": "Route imposed by the user: `{}`.",
    },
}

# What an agent needs at runtime. `init`, `init --upgrade` and
# `install.py --bundle-framework` copy exactly this, so a target project never
# receives the maintainers' CLAUDE.md, linter or CI, which agents that load
# nested instruction files would otherwise read as project rules.
RUNTIME_FILES = [
    KERNEL_FILE, "ROUTER.md", "DECISION-ENGINE.md", "CONTEXT-MANAGER.md", "ARTIFACTS.md",
    *PROMPT_FILES.values(), "CHANGELOG.md", "LICENSE",
]
RUNTIME_DIRS = ["modules", "templates", "guides"]

# Entries of the repository that are not runtime. Found inside a project's
# `asef/` (a full clone), agents that load nested instruction files read them.
MAINTAINER_ENTRIES = ["CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", ".github", "tools", "skills"]

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

SKILL_DIR = Path(__file__).resolve().parent.parent


def die(message: str, code: int = 1) -> "NoReturn":  # noqa: F821 - typing only
    print(f"asef_prompt: {message}", file=sys.stderr)
    raise SystemExit(code)


def is_root(path: Path) -> bool:
    return (path / KERNEL_FILE).is_file() and (path / PROMPT_FILE).is_file()


def find_root(project: Path) -> Path | None:
    """Framework root, in the order SKILL.md documents."""
    candidates = [
        project / "asef",             # framework dropped into the project
        project,                      # the project is the framework repository
        SKILL_DIR / "framework",      # copy bundled by install.py --bundle-framework
        SKILL_DIR.parent.parent,      # skill living inside the repository (skills/asef)
    ]
    return next((c.resolve() for c in candidates if is_root(c)), None)


def resolve_root(project: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        if not is_root(explicit):
            die(f"{explicit} is not an ASEF framework root", 2)
        return explicit.resolve()
    root = find_root(project)
    if root is not None:
        return root
    die(
        "no ASEF framework found: expected `asef/ASEF.md` in the project "
        "(run `asef_prompt.py init`, or copy the repository into `asef/`)",
        2,
    )


def version_key(version: str | None) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split(".")) if version else ()


def bundled_root() -> Path | None:
    """The framework copy the skill carries, if any: the source of `init`."""
    for candidate in (SKILL_DIR / "framework", SKILL_DIR.parent.parent):
        if is_root(candidate):
            return candidate.resolve()
    return None


def copy_runtime(origin: Path, target: Path) -> None:
    """Copy the runtime set only; replace any existing copy of each entry."""
    target.mkdir(parents=True, exist_ok=True)
    for name in RUNTIME_FILES:
        if (origin / name).is_file():
            shutil.copy2(origin / name, target / name)
    for name in RUNTIME_DIRS:
        if (target / name).exists():
            shutil.rmtree(target / name)
        if (origin / name).is_dir():
            shutil.copytree(origin / name, target / name, ignore=shutil.ignore_patterns("__pycache__"))


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


def request_block_span(prompt: str, lang: str) -> re.Match[str] | None:
    return re.search(rf"```\n({re.escape(LABELS[lang]['request'])}.*?)```", prompt, re.S)


def fill_request_block(block: str, args: argparse.Namespace, artifacts: list[str]) -> str:
    """Fill the block line by line; unknown lines pass through unchanged."""
    labels = LABELS[args.lang]
    release = labels["none_release"] if args.release in ("none", "nessuna") else args.release
    out: list[str] = []
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith(labels["request"]):
            out.append(f"{labels['request']} {args.request}")
        elif stripped.startswith(labels["release"]):
            out.append(f"{labels['release']} {release}")
        elif stripped.startswith(labels["artifacts"]):
            out.append(f"{labels['artifacts']} " + (", ".join(artifacts) if artifacts else labels["none_artifacts"]))
        elif stripped in (labels["constraints"], labels["non_goals"]):
            items = args.constraint if stripped == labels["constraints"] else args.non_goal
            out.append(line)
            i += 1
            while i < len(lines) and lines[i].strip() == "-":  # template placeholder rows
                i += 1
            out.extend(f"- {item}" for item in items) if items else out.append("-")
            continue
        elif stripped.startswith("- ") and stripped.endswith(":"):
            value = ""
            for key, prefix in labels["context"].items():
                if stripped[2:].startswith(prefix):
                    value = getattr(args, key) or ""
            out.append(f"{line} {value}".rstrip())
        else:
            out.append(line)
        i += 1
    return "\n".join(out)


def prompt_file(root: Path, lang: str) -> Path:
    path = root / PROMPT_FILES[lang]
    if not path.is_file():
        die(f"{root} has no `{PROMPT_FILES[lang]}`; upgrade the framework (`init --upgrade`) or use --lang it", 2)
    return path


def build_prompt(root: Path, project: Path, args: argparse.Namespace) -> str:
    name = PROMPT_FILES[args.lang]
    prompt = read(prompt_file(root, args.lang))
    match = request_block_span(prompt, args.lang)
    if not match:
        die(f"{name} has no request block starting with `{LABELS[args.lang]['request']}`")

    artifacts = list(dict.fromkeys(scan_artifacts(project) + list(args.artifact)))
    block = fill_request_block(match.group(1).strip(), args, artifacts)
    filled = prompt[: match.start(1)] + block + "\n" + prompt[match.end(1) :]

    trailer: list[str] = []
    if args.spec:
        trailer.append(LABELS[args.lang]["spec"].format(args.spec))
    if args.route:
        trailer.append(LABELS[args.lang]["route"].format(args.route))
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
        "languages": [lang for lang, name in PROMPT_FILES.items() if (root / name).is_file()],
        "artifacts": scan_artifacts(project),
        "state": (project / "STATE.md").is_file(),
    }
    source = bundled_root()
    if source is not None and source != root:
        info["bundled_version"] = kernel_version(source)
        info["upgrade_available"] = version_key(info["bundled_version"]) > version_key(info["kernel_version"])
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


def cmd_init(project: Path, source: Path | None, upgrade: bool) -> int:
    target = project / "asef"
    installed = is_root(target)
    if installed and not upgrade:
        print(f"asef_prompt: `{display_root(target, project)}` already holds an ASEF framework", file=sys.stderr)
        return 0
    if target.exists() and not installed:
        die(f"{target} exists but is not an ASEF framework root")
    if source is not None and not is_root(source):
        die(f"{source} is not an ASEF framework root", 2)
    origin = source or bundled_root()
    if origin is None:
        die(
            "no framework copy to install from: clone https://github.com/MrForty/asef into `asef/`, "
            "or reinstall the skill with `install.py --bundle-framework`",
            2,
        )
    if installed and origin.resolve() == target.resolve():
        print("asef_prompt: `asef/` is the only framework copy; nothing to upgrade from", file=sys.stderr)
        return 0

    before, after = (kernel_version(target) if installed else None), kernel_version(origin)
    if installed and version_key(after) < version_key(before):
        die(f"refusing to downgrade `asef/` from v{before} to v{after}")
    copy_runtime(origin, target)
    if installed:
        print(f"asef_prompt: framework in `asef/` upgraded v{before} -> v{after}; project artifacts untouched", file=sys.stderr)
    else:
        print(f"asef_prompt: framework v{after} installed in `asef/`", file=sys.stderr)
    return 0


def skill_installs(project: Path) -> list[tuple[str, Path]]:
    """Every `asef` skill in a known agent path, project and user level, once each."""
    found: dict[Path, str] = {}
    for agent, (project_dir, user_dir) in AGENTS.items():
        for level, base in (("project", project / project_dir), ("user", Path(user_dir).expanduser())):
            skill = base / "asef"
            if (skill / "SKILL.md").is_file():
                found.setdefault(skill.resolve(), f"{agent}/{level}")
    return [(label, path) for path, label in found.items()]


def cmd_doctor(project: Path, as_json: bool) -> int:
    """Report what works, what drifted and what to do; change nothing."""
    results: list[dict[str, str]] = []

    def add(level: str, check: str, message: str) -> None:
        results.append({"level": level, "check": check, "message": message})

    python = ".".join(map(str, sys.version_info[:3]))
    add("ok" if sys.version_info >= (3, 11) else "warn", "python", f"Python {python}" + ("" if sys.version_info >= (3, 11) else "; the scripts are tested on 3.11+"))

    root = find_root(project)
    if root is None:
        add("error", "framework", "no ASEF framework found; run `init`, or copy the repository into `asef/`")
    else:
        kernel = kernel_version(root)
        add("ok", "framework", f"`{display_root(root, project)}` declares kernel v{kernel}")
        for lang, name in PROMPT_FILES.items():
            if not (root / name).is_file():
                add("warn", "prompt", f"no `{name}` ({lang}); `init --upgrade` adds it")
                continue
            declared = prompt_version(read(root / name))
            add("ok" if declared == kernel else "error", "prompt", f"`{name}` activates v{declared}" + ("" if declared == kernel else f" but the kernel is v{kernel}"))
        missing = [n for n in RUNTIME_FILES if not (root / n).is_file()]
        missing += [f"{n}/" for n in RUNTIME_DIRS if not (root / n).is_dir() or not any((root / n).iterdir())]
        missing = [m for m in missing if m not in PROMPT_FILES.values()]  # reported above
        add("error" if missing else "ok", "runtime set", ("missing " + ", ".join(missing)) if missing else "complete")
        if root == (project / "asef").resolve():
            extra = [n for n in MAINTAINER_ENTRIES if (root / n).exists()]
            if extra:
                add("warn", "maintainer files", "`asef/` carries " + ", ".join(extra) + ": agents that load nested instruction files may read them as project rules; delete them")
        source = bundled_root()
        if source is not None and source != root and version_key(kernel_version(source)) > version_key(kernel):
            add("warn", "upgrade", f"the skill carries v{kernel_version(source)}; run `init --upgrade`")

    installs = skill_installs(project)
    if not installs:
        add("info", "skill", "no `asef` skill in a known agent path; the prompt and the AGENTS.md block still activate ASEF")
    for label, path in installs:
        bundled = path / "framework"
        version = f"framework v{kernel_version(bundled)} bundled" if is_root(bundled) else "no framework bundled"
        add("ok", "skill", f"{label}: {path.as_posix()} ({version})")
    if len({read(path / "SKILL.md") for _, path in installs}) > 1:
        add("warn", "skill", "installed copies differ; agents reading several paths may load either: reinstall with --force")

    activation = [n for n in ("AGENTS.md", "CLAUDE.md") if (project / n).is_file() and "asef/ASEF.md" in read(project / n)]
    add("ok" if activation else "info", "activation", ("permanent block in " + ", ".join(activation)) if activation else "no permanent block; paste the prompt or use /asef")
    add("info", "state", "STATE.md present: work resumes from it" if (project / "STATE.md").is_file() else "no STATE.md: a new route starts")
    add("ok" if shutil.which("git") else "info", "git", "available" if shutil.which("git") else "not found; CONTEXT-MANAGER.md fallbacks apply")

    failed = any(r["level"] == "error" for r in results)
    if as_json:
        print(json.dumps({"ok": not failed, "results": results}, ensure_ascii=False, indent=2))
    else:
        tags = {"ok": "  ok", "info": "info", "warn": "warn", "error": "FAIL"}
        for r in results:
            print(f"{tags[r['level']]}  {r['check']}: {r['message']}")
    return 1 if failed else 0


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
    build.add_argument("--lang", choices=sorted(PROMPT_FILES), default="it", help="language of the activation prompt (default: it)")

    sub.add_parser("scan", help="report framework root, versions and artifacts as JSON")
    init = sub.add_parser("init", help="copy the framework into <project>/asef")
    init.add_argument("--source", type=Path, help="framework copy to install from")
    init.add_argument("--upgrade", action="store_true", help="refresh an existing `asef/` from a newer copy")
    doctor = sub.add_parser("doctor", help="diagnose framework, prompts, skill installs and activation")
    doctor.add_argument("--json", action="store_true", help="machine-readable report")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.error("choose a command: build, scan, init or doctor")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    project = args.project.resolve()

    if args.command == "init":
        source = args.source or args.root
        return cmd_init(project, source.resolve() if source else None, args.upgrade)

    if args.command == "doctor":
        return cmd_doctor(project, args.json)

    root = resolve_root(project, args.root)
    if args.command == "scan":
        return cmd_scan(root, project)

    kernel = kernel_version(root)
    declared = prompt_version(read(prompt_file(root, args.lang)))
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
