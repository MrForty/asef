#!/usr/bin/env python3
"""Tests for the `asef` skill scripts: the prompt builder and the installer.

The skill promises that the generated prompt is the activation prompt with
only its request block filled. Each case runs the scripts as a user would and
checks that promise. Standard library only; no test runner required.

    python3 tools/test_asef_skill.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "asef"
BUILDER = SKILL / "scripts" / "asef_prompt.py"
INSTALLER = SKILL / "scripts" / "install.py"
PROMPT = (ROOT / "prompt universale ASEF.txt").read_text(encoding="utf-8")
PROMPT_HEAD = PROMPT[: PROMPT.index("```\nRichiesta:")]

FAILURES: list[str] = []


def run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd, env=env,
    )


def check(label: str, condition: bool, detail: str = "") -> None:
    print(f"{'PASS' if condition else 'FAIL'}  {label}")
    if not condition:
        FAILURES.append(f"{label}\n{detail.strip()}")


def fresh_project(tmp: Path, name: str, with_framework: bool = True) -> Path:
    project = tmp / name
    project.mkdir()
    if with_framework:
        shutil.copytree(ROOT, project / "asef", ignore=shutil.ignore_patterns(".git", "__pycache__", "skills"))
    return project


def request_block(prompt: str) -> str:
    match = re.search(r"```\n(Richiesta:.*?)```", prompt, re.S)
    return match.group(1) if match else ""


def test_builder(tmp: Path) -> None:
    project = fresh_project(tmp, "with-framework")
    (project / "STATE.md").write_text("# State\n", encoding="utf-8")
    (project / "PROJECT.md").write_text("# Project\n", encoding="utf-8")
    (project / "tasks").mkdir()
    (project / "tasks" / "TASK-001.md").write_text("# Task\n", encoding="utf-8")

    result = run(
        BUILDER, "--project", str(project), "build",
        "--request", "Aggiungi un filtro alla lista fatture",
        "--who", "operatori amministrativi",
        "--constraint", "stack esistente", "--constraint", "API pubbliche invariate",
        "--non-goal", "redesign della pagina",
        "--release", "commit",
        "--artifact", "src/invoices/",
        "--spec", "docs/spec-fatture.md", "--route", "MODIFY",
    )
    out = result.stdout
    check("builder: exits 0", result.returncode == 0, result.stderr)
    check("builder: everything before the block is the prompt verbatim", out.startswith(PROMPT_HEAD))
    block = request_block(out)
    check("builder: request filled", "Richiesta: Aggiungi un filtro alla lista fatture\n" in block)
    check("builder: stated context filled", "- chi ha il problema: operatori amministrativi\n" in block)
    check("builder: unstated context left empty", "- come lo risolve oggi:\n" in block)
    check(
        "builder: constraints listed",
        "Vincoli non negoziabili:\n- stack esistente\n- API pubbliche invariate\n" in block,
    )
    check("builder: non-goals listed", "Non-goal:\n- redesign della pagina\n" in block)
    check("builder: release authorization", "Autorizzazioni di rilascio: commit\n" in block)
    artifacts = re.search(r"Artefatti già esistenti: (.*)", block)
    listed = artifacts.group(1) if artifacts else ""
    check(
        "builder: artifacts detected and merged",
        all(a in listed for a in ("PROJECT.md", "STATE.md", "tasks/", "src/invoices/")), listed,
    )
    check("builder: spec and route trailers", "`docs/spec-fatture.md`" in out and "`MODIFY`" in out)
    check("builder: no version warning when aligned", "warning" not in result.stderr, result.stderr)
    check("builder: paths untouched when the root is `asef/`", "`asef/ASEF.md`" in out)

    minimal = run(BUILDER, "--project", str(project), "build", "--request", "Correggi il menu mobile")
    block = request_block(minimal.stdout)
    check("builder: defaults to no release authorization", "Autorizzazioni di rilascio: nessuna\n" in block)
    check("builder: empty lists keep the placeholder row", "Vincoli non negoziabili:\n-\n\nNon-goal:\n-\n" in block)

    only = run(BUILDER, "--project", str(project), "build", "--request", "x", "--block-only")
    check("builder: --block-only prints just the block", only.stdout.startswith("Richiesta: x\n") and "## Bootstrap" not in only.stdout)

    bad = run(BUILDER, "--project", str(project), "build", "--request", "x", "--release", "publish")
    check("builder: rejects an unknown release level", bad.returncode == 2 and "invalid choice" in bad.stderr)

    scan = run(BUILDER, "--project", str(project), "scan")
    info = json.loads(scan.stdout or "{}")
    check("scan: reports root, versions and artifacts", info.get("root") == "asef" and info.get("kernel_version") == info.get("prompt_version") and "STATE.md" in info.get("artifacts", []) and info.get("state") is True, scan.stdout)


def test_builder_roots(tmp: Path) -> None:
    bare = fresh_project(tmp, "bare", with_framework=False)
    missing = run(BUILDER, "--project", str(bare), "--root", str(bare), "scan")
    check("roots: explicit root without a framework fails with exit 2", missing.returncode == 2 and "not an ASEF framework root" in missing.stderr)

    elsewhere = tmp / "elsewhere"
    shutil.copytree(ROOT, elsewhere, ignore=shutil.ignore_patterns(".git", "__pycache__", "skills"))
    result = run(BUILDER, "--project", str(bare), "--root", str(elsewhere), "build", "--request", "x")
    check("roots: prompt paths rewritten to an external root", result.returncode == 0 and f"`{elsewhere.as_posix()}/ASEF.md`" in result.stdout and "`asef/" not in result.stdout)

    drifted = fresh_project(tmp, "drifted")
    prompt_file = drifted / "asef" / "prompt universale ASEF.txt"
    prompt_file.write_text(re.sub(r"kernel v[0-9.]+", "kernel v0.9", prompt_file.read_text(encoding="utf-8"), 1), encoding="utf-8")
    result = run(BUILDER, "--project", str(drifted), "build", "--request", "x")
    check("roots: kernel/prompt mismatch warns and still builds", result.returncode == 0 and "warning" in result.stderr and "kernel wins" in result.stderr)

    init_target = fresh_project(tmp, "init-target", with_framework=False)
    result = run(BUILDER, "--project", str(init_target), "init")
    check("init: installs the framework from the repository", result.returncode == 0 and (init_target / "asef" / "ASEF.md").is_file() and not (init_target / "asef" / "skills").exists(), result.stderr)
    again = run(BUILDER, "--project", str(init_target), "init")
    check("init: is idempotent", again.returncode == 0 and "already holds" in again.stderr)
    after = run(BUILDER, "--project", str(init_target), "scan")
    check("init: installed root is detected", '"root": "asef"' in after.stdout)


def test_installer(tmp: Path) -> None:
    project = tmp / "install-project"
    project.mkdir()
    listing = run(INSTALLER, "--list")
    check("installer: --list names the agents", listing.returncode == 0 and "claude" in listing.stdout and "codex" in listing.stdout)

    result = run(INSTALLER, "--agent", "claude", "--project", str(project))
    target = project / ".claude" / "skills" / "asef"
    check("installer: copies to the agent's project path", result.returncode == 0 and (target / "SKILL.md").is_file() and (target / "scripts" / "asef_prompt.py").is_file(), result.stderr)

    repeat = run(INSTALLER, "--agent", "claude", "--project", str(project))
    check("installer: refuses to overwrite without --force", repeat.returncode != 0 and "--force" in repeat.stderr)

    dest = tmp / "any-agent"
    result = run(INSTALLER, "--dest", str(dest), "--bundle-framework")
    bundled = dest / "asef" / "framework"
    check("installer: --dest with bundled framework", result.returncode == 0 and (bundled / "ASEF.md").is_file() and not (bundled / "skills").exists() and not (bundled / ".git").exists(), result.stderr)

    bare = tmp / "bare-project"
    bare.mkdir()
    scan = run(dest / "asef" / "scripts" / "asef_prompt.py", "--project", str(bare), "scan")
    check("installer: bundled framework is found from a bare project", scan.returncode == 0 and bundled.as_posix() in scan.stdout, scan.stdout + scan.stderr)
    built = run(dest / "asef" / "scripts" / "asef_prompt.py", "--project", str(bare), "build", "--request", "x")
    check("installer: prompt from a bundled root names that root", built.returncode == 0 and f"`{bundled.as_posix()}/ASEF.md`" in built.stdout)

    none = run(INSTALLER)
    check("installer: needs an agent or a destination", none.returncode == 2 and "--agent" in none.stderr)


def test_installer_link(tmp: Path) -> None:
    """`--force` over a `--link` install must delete the link, never its source.

    The destination is a symlink back to the skill directory, so resolving it
    would point the replacement at the source and `shutil.rmtree` would delete
    the installed skill itself. The installer under test is a throwaway copy,
    so a regression cannot reach the real skill.
    """
    sandbox = tmp / "sandbox" / "asef"
    shutil.copytree(SKILL, sandbox, ignore=shutil.ignore_patterns("__pycache__", "framework"))
    installer = sandbox / "scripts" / "install.py"

    probe = tmp / "symlink-probe"
    try:
        os.symlink(tmp, probe, target_is_directory=True)
    except (OSError, NotImplementedError):
        print("SKIP  installer: --link needs symlink privileges on this host")
        return
    probe.unlink()

    project = tmp / "link-project"
    project.mkdir()
    target = project / ".claude" / "skills" / "asef"

    linked = run(installer, "--agent", "claude", "--project", str(project), "--link")
    check("installer: --link creates a symlink", linked.returncode == 0 and target.is_symlink(), linked.stderr)

    refreshed = run(installer, "--agent", "claude", "--project", str(project), "--link", "--force")
    check(
        "installer: --force over a link replaces the link, not its source",
        refreshed.returncode == 0 and (sandbox / "SKILL.md").is_file() and target.is_symlink(),
        refreshed.stderr,
    )


def test_skill_file() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    front = re.match(r"---\n(.*?)\n---\n", text, re.S)
    check("skill: frontmatter present", front is not None)
    body = front.group(1) if front else ""
    check("skill: name is asef", re.search(r"^name:\s*asef\s*$", body, re.M) is not None)
    check("skill: description under the 1536-character listing cap", 0 < len(re.search(r"^description:\s*(.*)$", body, re.M).group(1)) <= 1536)
    check("skill: takes the request from $ARGUMENTS", "$ARGUMENTS" in text)
    check("skill: builder flags documented match the script", all(f"--{flag}" in text for flag in ("request", "who", "constraint", "non-goal", "release", "artifact", "spec", "route")))


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        # The scripts print resolved paths. Windows hands out the 8.3 short form
        # of the temp directory (`RUNNER~1`), so an unresolved path here would
        # never match the `runneradmin` the scripts print.
        tmp = Path(raw_tmp).resolve()
        test_skill_file()
        test_builder(tmp)
        test_builder_roots(tmp)
        test_installer(tmp)
        test_installer_link(tmp)

    print()
    if FAILURES:
        for failure in FAILURES:
            print(f"--- {failure}\n")
        print(f"{len(FAILURES)} check(s) failed.")
        return 1
    print("All skill checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
