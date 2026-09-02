#!/usr/bin/env python3
"""Negative tests for `asef_lint.py`.

A linter that never fails is worse than no linter. Each case mutates a copy of
the framework to break exactly one invariant and asserts the linter catches it.
Uses only the standard library; no test runner required.

    python3 tools/test_asef_lint.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINTER = "tools/asef_lint.py"


def mutate(rel_path: str, old: str, new: str) -> Callable[[Path], None]:
    def apply(work: Path) -> None:
        target = work / rel_path
        text = target.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"anchor {old!r} not found in {rel_path}")
        target.write_text(text.replace(old, new, 1), encoding="utf-8")

    return apply


def mutate_all(rel_path: str, old: str, new: str) -> Callable[[Path], None]:
    def apply(work: Path) -> None:
        target = work / rel_path
        text = target.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"anchor {old!r} not found in {rel_path}")
        target.write_text(text.replace(old, new), encoding="utf-8")

    return apply


def append_text(rel_path: str, text: str) -> Callable[[Path], None]:
    def apply(work: Path) -> None:
        target = work / rel_path
        target.write_text(target.read_text(encoding="utf-8") + text, encoding="utf-8")

    return apply


def drop_file(rel_path: str) -> Callable[[Path], None]:
    return lambda work: (work / rel_path).unlink()


def rename_file(rel_path: str, new_name: str) -> Callable[[Path], None]:
    return lambda work: (work / rel_path).rename((work / rel_path).with_name(new_name))


def current_version(work: Path) -> str:
    text = (work / "ASEF.md").read_text(encoding="utf-8")
    match = re.search(r"^\s*version:\s*([0-9.]+)\s*$", text, re.M)
    if match is None:
        raise AssertionError("ASEF.md has no version")
    return match.group(1)


def desync_kernel_version(work: Path) -> None:
    """Bump the kernel without touching the changelog."""
    version = current_version(work)
    target = work / "ASEF.md"
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(f"version: {version}", f"version: {version}9", 1), "utf-8")


def desync_prompt_version(work: Path) -> None:
    """Leave the activation prompt pointing at an older kernel."""
    version = current_version(work)
    target = work / "prompt universale ASEF.txt"
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(f"kernel v{version}", "kernel v0.9"), "utf-8")


# (label, mutation, substring the linter output must contain)
CASES: list[tuple[str, Callable[[Path], None], str]] = [
    (
        "module contract: section removed",
        mutate("modules/qa.md", "## Exit criteria", "## Exit criteriaX"),
        "modules/qa.md",
    ),
    (
        "module contract: invalid MODE",
        mutate("modules/qa.md", "**MODE:** HYBRID", "**MODE:** SEMI"),
        "MODE",
    ),
    (
        "module contract: sections out of order",
        mutate("modules/planning.md", "## Outputs", "## Zoutputs"),
        "modules/planning.md",
    ),
    (
        "graph: module `Next` contradicts the route",
        mutate("modules/planning.md", "`slicing` when multiple", "`qa` when multiple"),
        "route",
    ),
    (
        "graph: `Next` points at a node with no module",
        mutate("modules/discovery.md", "`product-scope` or `DONE`", "`product-scoping` or `DONE`"),
        "unknown node",
    ),
    (
        "graph: module unreachable from every route",
        rename_file("modules/slicing.md", "slicing-v2.md"),
        "slicing",
    ),
    (
        "graph: research promoted to a route node",
        mutate("ROUTER.md", "review → DONE", "research → DONE"),
        "research",
    ),
    (
        "traits: declared trait switches on nothing",
        mutate(
            "ASEF.md",
            "| `typed` | the language has a static type system |",
            "| `observable` | it emits telemetry |",
        ),
        "observable",
    ),
    (
        "templates: mandatory NFR row deleted",
        mutate("templates/SPEC.template.md", "| Observability | `deployed` |  |", ""),
        "Observability",
    ),
    (
        "templates: mandatory environment row deleted",
        mutate("templates/PROJECT.template.md", "| Production |  |  |  |", ""),
        "Production",
    ),
    (
        "templates: mandatory section removed",
        mutate("templates/DECISION.template.md", "## Alternatives Considered", "## Options"),
        "Alternatives Considered",
    ),
    (
        "traits: promised consumer does not carry the trait",
        mutate_all("templates/PLAN.template.md", "`persistence`", "`persisted`"),
        "persistence",
    ),
    (
        "risk classes: class with no threat pass",
        mutate("ASEF.md", "| `tenant` |", "| `tenancy` |"),
        "tenancy",
    ),
    (
        "prompt: route missing from the activation prompt",
        mutate_all("prompt universale ASEF.txt", "RELEASE", "SHIP_IT"),
        "RELEASE",
    ),
    (
        "budget: module over its token ceiling",
        append_text("modules/qa.md", "\n" + ("Repeat the procedure once more. " * 300)),
        "budget",
    ),
    (
        "templates: mandatory command row deleted",
        mutate("templates/PROJECT.template.md", "| Test |  |", ""),
        "Test",
    ),
    (
        "artifacts: core artifact loses its template",
        drop_file("templates/DECISIONS.template.md"),
        "DECISIONS.template.md",
    ),
    (
        "version: changelog behind the kernel",
        desync_kernel_version,
        "ASEF.md declares",
    ),
    (
        "version: activation prompt loads a stale kernel",
        desync_prompt_version,
        "activates kernel",
    ),
    (
        "references: dangling framework path",
        mutate("ARTIFACTS.md", "`modules/research.md`", "`modules/reasearch.md`"),
        "reasearch",
    ),
    (
        "one fact, one home: ladder restated in a module",
        mutate(
            "modules/implementation.md",
            "## Purpose",
            "## Purpose\n\nknown → inferable → ask.\n",
        ),
        "ladder",
    ),
]


def run_linter(work: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(work / LINTER)], capture_output=True, text=True
    )


def fresh_copy(tmp: Path) -> Path:
    work = tmp / "repo"
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return work


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)

        for label, apply, expected in CASES:
            work = fresh_copy(tmp)
            apply(work)
            result = run_linter(work)
            caught = result.returncode == 1 and expected in result.stdout
            print(f"{'PASS' if caught else 'FAIL'}  {label}")
            if not caught:
                failures.append(f"{label}\nexit {result.returncode}\n{result.stdout.strip()}")

        work = fresh_copy(tmp)
        result = run_linter(work)
        control_ok = result.returncode == 0
        print(f"{'PASS' if control_ok else 'FAIL'}  control: unmutated framework is green")
        if not control_ok:
            failures.append(f"control\nexit {result.returncode}\n{result.stdout.strip()}")

    print()
    if failures:
        for failure in failures:
            print(f"--- {failure}\n")
        print(f"{len(failures)} test(s) failed.")
        return 1

    print(f"All {len(CASES)} mutations caught, control green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
