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


def desync_readme_badge(work: Path) -> None:
    """Leave the README badge on an older version."""
    version = current_version(work)
    target = work / "README.md"
    text = target.read_text(encoding="utf-8")
    if f"ASEF-{version}-" not in text:
        raise AssertionError("README badge does not carry the current version")
    target.write_text(text.replace(f"ASEF-{version}-", "ASEF-0.9-", 1), "utf-8")


# (label, mutation, substring the linter output must contain)
CASES: list[tuple[str, Callable[[Path], None], str]] = [
    (
        "guides: missing guide",
        drop_file("guides/web-experience.md"),
        "missing `guides/web-experience.md`",
    ),
    (
        "guides: load condition removed",
        mutate("guides/existing-projects.md", "## When to load", "## Other"),
        "missing load condition",
    ),
    (
        "guides: consumer disconnected",
        mutate("modules/qa.md", "`guides/web-experience.md`", "the visual checklist"),
        "missing conditional guide",
    ),
    (
        "guides: budget exceeded",
        append_text("guides/existing-projects.md", "x" * 4801),
        "guide budget",
    ),
    (
        "guides: internal reference broken",
        append_text("guides/web-experience.md", "\nSee `guides/missing.md`.\n"),
        "references `guides/missing.md`",
    ),
    (
        "templates: website delivery removed",
        mutate("templates/SPEC.template.md", "## Website delivery", "## Other"),
        "mandatory section `Website delivery`",
    ),
    (
        "templates: existing baseline removed",
        mutate("templates/SPEC.template.md", "## Current State", "## Other"),
        "mandatory section `Current State`",
    ),
    (
        "graph: bare optional marker reports without traceback",
        mutate("ROUTER.md", "review → DONE", "review → ? → DONE"),
        "has no module file",
    ),
    (
        "structure: missing kernel reports without traceback",
        drop_file("ROUTER.md"),
        "missing `ROUTER.md`",
    ),
    (
        "structure: missing consumed template reports without traceback",
        drop_file("templates/SPEC.template.md"),
        "missing template `templates/SPEC.template.md`",
    ),
    (
        "graph: unknown intermediate node is not discarded",
        mutate("ROUTER.md", "review → DONE", "review → nonexistent → DONE"),
        "graph node `nonexistent` has no module file",
    ),
    (
        "graph: unknown optional node is not discarded",
        mutate("ROUTER.md", "review → DONE", "review → nonexistent? → DONE"),
        "graph node `nonexistent` has no module file",
    ),
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
    (
        "one fact, one home: promotion test restated in a module",
        append_text("modules/research.md", "\nPromote only when credible sources diverge materially.\n"),
        "promotion test",
    ),
    (
        "vocabulary: reversibility class shortened in a template",
        mutate("templates/DECISIONS.template.md", "Expensive to reverse", "Expensive"),
        "reversibility class shortened",
    ),
    (
        "vocabulary: reversibility class dropped from its table",
        mutate("DECISION-ENGINE.md", "| One-way/high risk |", "| Irreversible |"),
        "missing from its table",
    ),
    (
        "router: first-output block loses a field",
        mutate("ROUTER.md", "Human actions: <none | single list>", ""),
        "lacks the `Human actions` field",
    ),
    (
        "readme: version badge behind the kernel",
        desync_readme_badge,
        "version badge",
    ),
    (
        "readme: request block drifted from the prompt",
        mutate("README.md", "Richiesta: <una frase: cosa deve fare>", "Richiesta: <cosa deve fare>"),
        "request block differs",
    ),
    (
        "skill: SKILL.md missing",
        drop_file("skills/asef/SKILL.md"),
        "missing `skills/asef/SKILL.md`",
    ),
    (
        "skill: renamed so `/asef` no longer invokes it",
        mutate("skills/asef/SKILL.md", "name: asef", "name: asef-framework"),
        "skill name must be `asef`",
    ),
    (
        "skill: stops pointing at the prompt builder",
        mutate_all("skills/asef/SKILL.md", "`scripts/asef_prompt.py`", "the builder script"),
        "does not point the agent at `scripts/asef_prompt.py`",
    ),
    (
        "skill: restates the uncertainty ladder",
        append_text("skills/asef/SKILL.md", "\nResolve gaps as known → inferable → ask.\n"),
        "restates the uncertainty ladder",
    ),
    (
        "skill: dangling reference",
        append_text("skills/asef/SKILL.md", "\nSee `scripts/missing.py`.\n"),
        "references `scripts/missing.py`",
    ),
    (
        "skill: over its token ceiling",
        append_text("skills/asef/SKILL.md", "\n" + ("Read the kernel once more. " * 250)),
        "skill budget",
    ),
]


def run_linter(work: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(work / LINTER), "--verbose"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
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
            caught = result.returncode == 1 and expected in result.stdout and not result.stderr
            print(f"{'PASS' if caught else 'FAIL'}  {label}")
            if not caught:
                failures.append(f"{label}\nexit {result.returncode}\n{result.stdout.strip()}\n{result.stderr.strip()}")

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
