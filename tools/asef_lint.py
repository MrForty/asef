#!/usr/bin/env python3
"""Consistency linter for the ASEF framework documents.

ASEF is Markdown, not software: this script does not test a program, it checks
the invariants the documents promise each other. Run it from anywhere:

    python3 tools/asef_lint.py [--root PATH] [-v]

Exit code 0 when every invariant holds, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

# --------------------------------------------------------------------------
# Contracts declared by the framework documents themselves.
# --------------------------------------------------------------------------

KERNEL_FILES = [
    "ASEF.md",
    "ROUTER.md",
    "DECISION-ENGINE.md",
    "CONTEXT-MANAGER.md",
    "ARTIFACTS.md",
]

ACTIVATION_PROMPT = "prompt universale ASEF.txt"

# ASEF.md "Module contract", in the order it requires.
MODULE_SECTIONS = [
    "Trigger",
    "Purpose",
    "Requires",
    "Optional",
    "Do not load",
    "Procedure",
    "Exit criteria",
    "Outputs",
    "Next",
]

MODULE_MODES = {"NATIVE", "HYBRID"}

# `research` is a subroutine invoked in place, never a route node (ROUTER.md).
SUBROUTINE_MODULES = {"research"}

ROUTE_NAMES = [
    "GREENFIELD",
    "MODIFY",
    "DIAGNOSE",
    "IMPROVE",
    "REUSE",
    "REVIEW_ONLY",
    "QA_ONLY",
]

# Graph nodes that are not modules. `fix` is review's internal cycle.
NON_MODULE_NODES = {"DONE", "fix"}

# Artifacts a target project generates, and the template that seeds each.
CORE_ARTIFACTS = {
    "PROJECT.md": "PROJECT.template.md",
    "SPEC.md": "SPEC.template.md",
    "PLAN.md": "PLAN.template.md",
    "STATE.md": "STATE.template.md",
    "TASK-NNN.md": "TASK.template.md",
    "DECISIONS.md": "DECISIONS.template.md",
}

DECISION_RECORD_TEMPLATE = "DECISION.template.md"

# Template rows CLAUDE.md declares mandatory: filled or marked N/A, never deleted.
SPEC_NFR_ROWS = [
    "Performance / latency",
    "Scale / volume",
    "Compatibility / versioning",
    "Authentication / authorization",
    "Data, privacy, retention",
    "Observability",
    "Accessibility / i18n",
    "Licensing / compliance",
]

PROJECT_COMMAND_ROWS = ["Install", "Build", "Test", "Lint / typecheck", "Run"]

# Evidence and gap labels are contracts with the framework files (prompt txt).
EVIDENCE_LABELS = ["FACT", "INFERENCE", "ASSUMPTION", "DECISION", "OPEN"]
GAP_LABELS = ["KNOWN", "INFERABLE", "RESEARCHABLE", "USER-DECISION"]

# Referenced names that belong to a target project or to the outside world and
# therefore must not be resolved against this repository.
REFERENCE_ALLOWLIST = {
    *CORE_ARTIFACTS,
    "ARCHITECTURE.md",
    "RESEARCH.md",
    "CLAUDE.md",
    "tasks/TASK-NNN.md",
}


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    def ok(self, name: str) -> None:
        self.checks.append(name)

    def fail(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------


def headings(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.M)]


def section(text: str, title: str) -> str:
    """Body of a `## title` section, up to the next heading of any level."""
    pattern = rf"^##\s+{re.escape(title)}\s*$\n(.*?)(?=^#{{1,3}}\s|\Z)"
    match = re.search(pattern, text, re.M | re.S)
    return match.group(1) if match else ""


def backticked(text: str) -> list[str]:
    return re.findall(r"`([^`\n]+)`", text)


def module_mode(text: str) -> str | None:
    match = re.search(r"^\*\*MODE:\*\*\s*(\w+)\s*$", text, re.M)
    return match.group(1) if match else None


def table_first_column(text: str) -> list[str]:
    """First cell of every markdown table row, minus header and separator."""
    cells = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.match(r"^\|[\s:|-]+\|$", line):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if parts:
            cells.append(parts[0].strip("`").strip())
    return cells[1:] if cells else []


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def check_structure(root: Path, report: Report) -> dict[str, str]:
    """Expected files exist. Returns {module name: text} for later checks."""
    for name in KERNEL_FILES + [ACTIVATION_PROMPT, "CHANGELOG.md", "README.md"]:
        if not (root / name).is_file():
            report.fail("structure", f"missing `{name}`")

    modules_dir = root / "modules"
    if not modules_dir.is_dir():
        report.fail("structure", "missing `modules/` directory")
        return {}

    modules = {p.stem: read(p) for p in sorted(modules_dir.glob("*.md"))}
    if not modules:
        report.fail("structure", "`modules/` contains no module")

    templates_dir = root / "templates"
    if not templates_dir.is_dir():
        report.fail("structure", "missing `templates/` directory")
    else:
        expected = set(CORE_ARTIFACTS.values()) | {DECISION_RECORD_TEMPLATE}
        present = {p.name for p in templates_dir.glob("*.md")}
        for missing in sorted(expected - present):
            report.fail("structure", f"missing template `templates/{missing}`")

    report.ok(f"structure ({len(modules)} modules)")
    return modules


def check_module_contract(modules: dict[str, str], report: Report) -> None:
    """ASEF.md: every module declares the ten sections, in order."""
    for name, text in sorted(modules.items()):
        where = f"modules/{name}.md"

        mode = module_mode(text)
        if mode is None:
            report.fail(where, "missing `**MODE:**` declaration")
        elif mode not in MODULE_MODES:
            report.fail(where, f"MODE `{mode}` is not NATIVE or HYBRID")

        found = headings(text)
        missing = [s for s in MODULE_SECTIONS if s not in found]
        if missing:
            report.fail(where, "missing section(s): " + ", ".join(f"`{m}`" for m in missing))
            continue

        ordered = [s for s in found if s in MODULE_SECTIONS]
        if ordered != MODULE_SECTIONS:
            report.fail(
                where,
                "sections out of contract order: got "
                + " → ".join(ordered)
                + "; expected "
                + " → ".join(MODULE_SECTIONS),
            )

    report.ok("module contract (10 sections, ordered, valid MODE)")


def parse_routes(
    router_text: str, known_nodes: set[str]
) -> tuple[dict[str, list[list[str]]], set[str]]:
    """Route graphs from ROUTER.md as {route: [path, ...]}.

    A path is the ordered node sequence of one graph line; `?` marks an optional
    node and is kept as a trailing marker on the node name. Nodes reached only
    through `⇄` are internal cycles, not forward edges, and are returned apart.
    """
    body = section(router_text, "Routes")
    block = re.search(r"```text\n(.*?)```", body, re.S)
    if not block:
        return {}, set()

    routes: dict[str, list[list[str]]] = {}
    current: str | None = None
    pending: list[str] = []
    cycles: set[str] = set()

    def flush() -> None:
        if current and pending:
            routes.setdefault(current, []).append(list(pending))
        pending.clear()

    for raw in block.group(1).splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line in ROUTE_NAMES:
            flush()
            current = line
            continue
        if current is None:
            continue

        # A line that does not continue the previous one starts a new path.
        starts_continuation = line.startswith(("→", "⇄"))
        if pending and not starts_continuation:
            flush()

        # Split on arrows while keeping them: `⇄` introduces an internal cycle
        # (review ⇄ fix), not a forward edge, so its target is not a successor.
        parts = re.split(r"(→|⇄)", line)
        separators = ["→"] + [p for p in parts if p in {"→", "⇄"}]
        for separator, token in zip(separators, [p for p in parts if p not in {"→", "⇄"}]):
            token = token.strip()
            if not token:
                continue
            optional = token.endswith("?")
            token = token.rstrip("?").strip()
            # Trim trailing prose such as "DONE when the fix is not authorized".
            words = token.split()
            node = next((w for w in words if w in known_nodes), None)
            if node is None:
                continue
            if separator == "⇄":
                cycles.add(node)
                continue
            pending.append(node + ("?" if optional else ""))
    flush()
    return routes, cycles


def check_router_graph(root: Path, modules: dict[str, str], report: Report) -> None:
    router_text = read(root / "ROUTER.md")
    known_nodes = set(modules) | NON_MODULE_NODES
    routes, cycle_nodes = parse_routes(router_text, known_nodes)

    if not routes:
        report.fail("ROUTER.md", "no route graph parsed from the `## Routes` block")
        return

    for route in ROUTE_NAMES:
        if route not in routes:
            report.fail("ROUTER.md", f"route `{route}` has no graph")

    # Every graph node is a real module (or an allowed non-module node).
    graph_nodes: set[str] = set(cycle_nodes)
    for paths in routes.values():
        for path in paths:
            graph_nodes.update(n.rstrip("?") for n in path)

    for node in sorted(graph_nodes - known_nodes):
        report.fail("ROUTER.md", f"graph node `{node}` has no module file")

    for name in sorted(set(modules) - SUBROUTINE_MODULES - graph_nodes):
        report.fail("ROUTER.md", f"module `{name}` is never reached by any route graph")

    for name in sorted(SUBROUTINE_MODULES & graph_nodes):
        report.fail("ROUTER.md", f"subroutine `{name}` must not appear as a route node")

    # The invariant: every graph edge is honoured by the source module's `Next`.
    for route, paths in sorted(routes.items()):
        for path in paths:
            for index, raw_source in enumerate(path[:-1]):
                source = raw_source.rstrip("?")
                if source in NON_MODULE_NODES or source not in modules:
                    continue

                # Optional successors may be skipped, so accept the first
                # mandatory node reachable through a run of optional ones.
                reachable: list[str] = []
                for raw_target in path[index + 1 :]:
                    reachable.append(raw_target.rstrip("?"))
                    if not raw_target.endswith("?"):
                        break

                declared_next = module_next_targets(modules[source])
                if not declared_next & set(reachable):
                    report.fail(
                        f"modules/{source}.md",
                        f"route `{route}` goes {source} → {'|'.join(reachable)}, "
                        f"but `Next` declares {sorted(declared_next) or 'nothing'}",
                    )

    report.ok(f"route graph ({len(routes)} routes, edges match module `Next`)")


def module_next_targets(text: str) -> set[str]:
    """Node names a module's `Next` section actually points to."""
    body = section(text, "Next")
    tokens = set(backticked(body))
    noise = set(EVIDENCE_LABELS) | set(GAP_LABELS) | set(ROUTE_NAMES)
    return {t for t in tokens if t not in noise}


def check_module_next(modules: dict[str, str], report: Report) -> None:
    known = set(modules) | NON_MODULE_NODES
    for name, text in sorted(modules.items()):
        if name in SUBROUTINE_MODULES:
            continue  # returns to its caller; no fixed target
        targets = module_next_targets(text)
        if not targets:
            report.fail(f"modules/{name}.md", "`Next` declares no target")
        for target in sorted(targets - known):
            report.fail(f"modules/{name}.md", f"`Next` points to unknown node `{target}`")
    report.ok("module `Next` targets resolve")


def check_traits(root: Path, modules: dict[str, str], report: Report) -> None:
    """ASEF.md: a trait with no consumer is dead weight."""
    asef = read(root / "ASEF.md")
    traits = [t for t in table_first_column(section(asef, "Project traits")) if t]
    if not traits:
        report.fail("ASEF.md", "no traits parsed from the `Project traits` table")
        return

    consumers = {
        "modules/review.md": modules.get("review", ""),
        "modules/qa.md": modules.get("qa", ""),
        "modules/planning.md": modules.get("planning", ""),
        "templates/SPEC.template.md": read(root / "templates" / "SPEC.template.md"),
        "templates/PLAN.template.md": read(root / "templates" / "PLAN.template.md"),
    }

    project_template = read(root / "templates" / "PROJECT.template.md")
    for trait in traits:
        if f"`{trait}`" not in project_template:
            report.fail(
                "templates/PROJECT.template.md",
                f"trait `{trait}` is declared in ASEF.md but absent from the Traits section",
            )
        if not any(f"`{trait}`" in text for text in consumers.values()):
            report.fail(
                "ASEF.md",
                f"trait `{trait}` switches on rigor nowhere: no consumer in "
                + ", ".join(consumers),
            )

    report.ok(f"traits ({len(traits)} declared, each with a consumer)")


def check_templates(root: Path, report: Report) -> None:
    """Mandatory rows are filled or `N/A`, never deleted."""
    spec = read(root / "templates" / "SPEC.template.md")
    nfr_rows = table_first_column(section(spec, "Non-Functional Requirements"))
    for row in SPEC_NFR_ROWS:
        if row not in nfr_rows:
            report.fail("templates/SPEC.template.md", f"NFR row `{row}` was removed")

    project = read(root / "templates" / "PROJECT.template.md")
    command_rows = table_first_column(section(project, "Commands"))
    for row in PROJECT_COMMAND_ROWS:
        if row not in command_rows:
            report.fail("templates/PROJECT.template.md", f"command row `{row}` was removed")

    state = read(root / "templates" / "STATE.template.md")
    for label in ROUTE_NAMES:
        if label not in state:
            report.fail("templates/STATE.template.md", f"intent `{label}` missing from Intent line")

    report.ok("template mandatory rows present")


def check_artifacts(root: Path, report: Report) -> None:
    """Every artifact ARTIFACTS.md names has a template that seeds it."""
    artifacts_text = read(root / "ARTIFACTS.md")
    for artifact, template in sorted(CORE_ARTIFACTS.items()):
        if artifact not in artifacts_text and artifact != "TASK-NNN.md":
            report.fail("ARTIFACTS.md", f"core artifact `{artifact}` is not documented")
        if not (root / "templates" / template).is_file():
            report.fail("templates", f"`{artifact}` has no template `{template}`")
    report.ok("artifacts ↔ templates")


def check_version(root: Path, report: Report) -> None:
    asef = read(root / "ASEF.md")
    match = re.search(r"^\s*version:\s*([0-9]+(?:\.[0-9]+)*)\s*$", asef, re.M)
    if not match:
        report.fail("ASEF.md", "no `version:` in the config block")
        return
    version = match.group(1)

    changelog = read(root / "CHANGELOG.md")
    entries = re.findall(r"^##\s+([0-9]+(?:\.[0-9]+)*)\s*$", changelog, re.M)
    if not entries:
        report.fail("CHANGELOG.md", "no version entry found")
    elif entries[0] != version:
        report.fail(
            "CHANGELOG.md",
            f"latest entry is `{entries[0]}` but ASEF.md declares `{version}`",
        )

    prompt = read(root / ACTIVATION_PROMPT)
    declared = re.search(r"kernel\s+v([0-9]+(?:\.[0-9]+)*)", prompt)
    if not declared:
        report.fail(ACTIVATION_PROMPT, "does not declare the kernel version it activates")
    elif declared.group(1) != version:
        report.fail(
            ACTIVATION_PROMPT,
            f"activates kernel v{declared.group(1)} but ASEF.md declares v{version}",
        )

    report.ok(f"version alignment (v{version})")


def check_references(root: Path, report: Report) -> None:
    """Every framework path a document names must exist."""
    docs = [root / n for n in KERNEL_FILES]
    docs += [root / "CLAUDE.md", root / "README.md", root / ACTIVATION_PROMPT]
    docs += sorted((root / "modules").glob("*.md"))
    docs += sorted((root / "templates").glob("*.md"))

    link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
    path_re = re.compile(r"`([A-Za-z0-9_./ -]+\.(?:md|txt|py|yml))`")

    for doc in docs:
        if not doc.is_file():
            continue
        text = read(doc)
        # Markdown links may percent-encode spaces; resolve against the real name.
        candidates = {unquote(c) for c in link_re.findall(text)} | set(path_re.findall(text))
        for candidate in sorted(candidates):
            if candidate.startswith(("http://", "https://", "#", "../")):
                continue
            target = candidate[len("asef/") :] if candidate.startswith("asef/") else candidate
            if target in REFERENCE_ALLOWLIST or Path(target).name in REFERENCE_ALLOWLIST:
                continue
            if (root / target).exists():
                continue
            if (root / "templates" / Path(target).name).exists():
                continue
            report.fail(
                doc.relative_to(root).as_posix(),
                f"references `{candidate}`, which does not exist",
            )

    report.ok("cross-references resolve")


def check_single_home(root: Path, modules: dict[str, str], report: Report) -> None:
    """CLAUDE.md: each rule lives in one kernel file; modules reference it."""
    ladder = "known → inferable"
    owners = {"ASEF.md", "DECISION-ENGINE.md"}
    for name, text in sorted(modules.items()):
        if ladder in text:
            report.fail(
                f"modules/{name}.md",
                "restates the uncertainty ladder owned by DECISION-ENGINE.md",
            )
    for name in KERNEL_FILES:
        if name in owners:
            continue
        if ladder in read(root / name):
            report.fail(name, "restates the uncertainty ladder owned by DECISION-ENGINE.md")
    report.ok("one fact, one home (uncertainty ladder)")


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def run(root: Path, verbose: bool) -> int:
    report = Report()

    modules = check_structure(root, report)
    if modules:
        check_module_contract(modules, report)
        check_module_next(modules, report)
        check_router_graph(root, modules, report)
        check_traits(root, modules, report)
        check_single_home(root, modules, report)
    check_templates(root, report)
    check_artifacts(root, report)
    check_version(root, report)
    check_references(root, report)

    if verbose:
        for name in report.checks:
            print(f"  ok  {name}")

    if report.errors:
        print(f"\nASEF consistency: {len(report.errors)} problem(s)\n")
        for error in report.errors:
            print(f"  ✗ {error}")
        return 1

    print(f"\nASEF consistency: {len(report.checks)} checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check ASEF document invariants.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="framework root (default: the repository containing this script)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="list every check")
    args = parser.parse_args()

    root = args.root.resolve()
    if not (root / "ASEF.md").is_file():
        print(f"error: {root} does not look like an ASEF framework root", file=sys.stderr)
        return 2
    return run(root, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
