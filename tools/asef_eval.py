#!/usr/bin/env python3
"""Run the evaluation scenarios of `examples/scenarios.md` against any agent.

No agent is driven from here: every agent has its own CLI, and a harness that
knew them all would pick favourites. The script prepares a run folder the
agent works in, then judges the record a human (or a grader agent) fills from
what the agent observably did.

    python3 tools/asef_eval.py list
    python3 tools/asef_eval.py prepare W4 --out runs/w4-claude [--activation prompt|agents|skill]
                                          [--lang it|en] [--fixture DIR] [--skill-agent NAME]
    python3 tools/asef_eval.py check runs/w4-claude
    python3 tools/asef_eval.py report runs/

Without `--fixture`, a case with a built-in fixture in `examples/fixtures/<CASE>/`
uses it: `base/` becomes the fixture's first commit and `dirty/`, when present,
is copied over it uncommitted, so cases such as A2 start with the unrelated
changes they describe.

A run folder holds `project/` (the agent's working directory: the fixture, the
runtime framework in `asef/`, the activation), `MESSAGE.txt` (what to send the
agent) and `RESULT.md` (the record to fill). `check` reads the route from
`project/STATE.md`, so the route criterion is never self-reported.

Exit codes: 0 ok, 1 incomplete or invalid record, 2 bad arguments.
Python 3.11+, standard library only. Never loaded into an agent's context.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "examples" / "scenarios.md"
FIXTURES = ROOT / "examples" / "fixtures"
SCRIPTS = ROOT / "skills" / "asef" / "scripts"
BUILDER = SCRIPTS / "asef_prompt.py"
INSTALLER = SCRIPTS / "install.py"
AGENTS_TEMPLATE = ROOT / "templates" / "AGENTS.template.md"

sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
from asef_prompt import AGENTS, ROUTES, copy_runtime  # noqa: E402 - one home for each

ACTIVATIONS = ["prompt", "agents", "skill"]
VERDICTS = ["PASS", "FAIL", "OPEN"]
UNFILLED = {"", "?"}
REQUIRED_FIELDS = ["agent/version", "tools"]
GIT_IDENTITY = ["-c", "user.name=asef-eval", "-c", "user.email=asef-eval@localhost"]


@dataclass
class Scenario:
    case: str
    fixture: str
    request: str
    expected: list[str]
    fail_if: list[str]
    route: str | None


@dataclass
class Record:
    path: Path
    fields: dict[str, str] = field(default_factory=dict)
    criteria: list[dict[str, str]] = field(default_factory=list)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cells(line: str) -> list[str]:
    """Cells of a Markdown table row; `\\|` inside a cell is not a separator."""
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def split_items(text: str) -> list[str]:
    return [item.strip().rstrip(".") for item in text.split(";") if item.strip()]


def load_scenarios(path: Path = SCENARIOS) -> dict[str, Scenario]:
    scenarios: dict[str, Scenario] = {}
    header: list[str] | None = None
    for line in read(path).splitlines():
        if not line.startswith("|"):
            header = None
            continue
        row = cells(line)
        if row[0] == "ID":
            header = row
            continue
        if header is None or set(line) <= set("|-: "):
            continue
        entry = dict(zip(header, row))
        expected = split_items(entry["Expected behavior"])
        routes = [item for item in expected if item in ROUTES]
        scenarios[entry["ID"]] = Scenario(
            case=entry["ID"],
            fixture=entry["Fixture"],
            request=entry["Request"],
            expected=[item for item in expected if item not in ROUTES],
            fail_if=split_items(entry["Fail if"]),
            route=routes[0] if routes else None,
        )
    return scenarios


def framework_commit() -> str:
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def agents_block() -> str:
    """The activation block of `AGENTS.template.md`, without its instructions comment."""
    return re.sub(r"<!--.*?-->", "", read(AGENTS_TEMPLATE), flags=re.S).strip() + "\n"


def git(project: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *GIT_IDENTITY, *args], cwd=project, capture_output=True, text=True, check=check)


def isolate_git(project: Path, fixture: Path) -> str | None:
    """Replace a copied `.git` pointer file with a repository of the project's own.

    A linked worktree or a submodule keeps its metadata elsewhere: `.git` is a
    file naming an absolute `gitdir`. Copied as is, the agent's git commands
    would stage, commit or reset in the source fixture. The new repository
    holds the fixture's HEAD commit; the copied files, dirty state included,
    stay as they are.
    """
    marker = project / ".git"
    if not marker.is_file():
        return None
    marker.unlink()
    if shutil.which("git") is None:
        return "fixture git pointer removed; git unavailable"
    git(project, "init", "-q")
    if git(project, "fetch", "-q", str(fixture.resolve()), "HEAD", check=False).returncode != 0:
        return "fixture git pointer replaced by an empty repository (fixture HEAD unreadable)"
    git(project, "reset", "-q", "FETCH_HEAD")
    return "fixture git metadata isolated at its HEAD"


def git_baseline(project: Path, harness: list[str]) -> str:
    """Commit what the harness added, so the agent starts from a clean baseline.

    A fresh repository commits everything. A fixture repository commits only
    the harness paths, so its own dirty state (staged or not) stays exactly
    as the case requires.
    """
    if shutil.which("git") is None:
        return "git unavailable: no baseline commit"
    if not (project / ".git").exists():
        git(project, "init", "-q")
        git(project, "add", "-A")
        git(project, "commit", "-q", "--allow-empty", "-m", "asef-eval baseline")
        return "baseline commit created"
    paths = [p for p in harness if (project / p).exists()]
    git(project, "add", "-f", "--", *paths)
    if git(project, "diff", "--cached", "--quiet", "--", *paths, check=False).returncode == 0:
        return "harness already committed in the fixture repository; its own changes left as they were"
    git(project, "commit", "-q", "--only", "-m", "asef-eval harness", "--", *paths)
    return "harness committed on the fixture repository; its own changes left as they were"


def builtin_fixture(case: str, project: Path) -> str | None:
    """Materialise `examples/fixtures/<case>`: `base/` committed, `dirty/` left uncommitted."""
    source = FIXTURES / case
    if not (source / "base").is_dir():
        return None
    ignore = shutil.ignore_patterns("__pycache__")
    shutil.copytree(source / "base", project, ignore=ignore)
    if shutil.which("git") is not None:
        git(project, "init", "-q")
        git(project, "add", "-A")
        git(project, "commit", "-q", "-m", "fixture baseline")
    if (source / "dirty").is_dir():
        shutil.copytree(source / "dirty", project, ignore=ignore, dirs_exist_ok=True)
    return f"built-in fixture examples/fixtures/{case}"


def result_template(s: Scenario, activation: str, lang: str, baseline: str) -> str:
    rows = [
        ("case", s.case), ("activation", activation), ("language", lang),
        ("agent/version", "?"), ("framework commit", framework_commit()), ("tools", "?"),
        ("expected route", s.route or "not checked"), ("fixture", s.fixture), ("request", s.request),
        ("baseline", baseline), ("limitation", "none"),
    ]
    lines = [f"# ASEF evaluation run: {s.case}", "", "| Field | Value |", "|---|---|"]
    lines += [f"| {k} | {v.replace('|', chr(92) + '|')} |" for k, v in rows]
    lines += [
        "",
        "<!-- Fill `agent/version` and `tools` (the capabilities the agent actually had).",
        "     Verdict per row: PASS, FAIL or OPEN. For `expect` rows PASS means observed;",
        "     for `fail-if` rows PASS means it did not happen. Every verdict needs",
        "     evidence: a file, a command and its output, a screenshot path. Judge",
        "     observable actions only; text that mentions a rule is not evidence.",
        "     The route is read from project/STATE.md by `check`, not filled here. -->",
        "",
        "## Criteria",
        "",
        "| # | Kind | Criterion | Verdict | Evidence |",
        "|---|---|---|---|---|",
    ]
    lines += [f"| E{i} | expect | {c} | ? |  |" for i, c in enumerate(s.expected, 1)]
    lines += [f"| F{i} | fail-if | {c} | ? |  |" for i, c in enumerate(s.fail_if, 1)]
    return "\n".join(lines) + "\n"


def cmd_list(scenarios: dict[str, Scenario]) -> int:
    for s in scenarios.values():
        print(f"{s.case:<4}{s.route or '-':<13}{s.request}")
    return 0


def cmd_prepare(s: Scenario, args: argparse.Namespace) -> int:
    out: Path = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        print(f"asef_eval: {out} is not empty", file=sys.stderr)
        return 2
    project = out / "project"
    fixture_note = None
    harness = ["asef"]
    if args.fixture:
        shutil.copytree(args.fixture, project, ignore=shutil.ignore_patterns("asef"))
        fixture_note = isolate_git(project, args.fixture)
    elif (fixture_note := builtin_fixture(s.case, project)) is None:
        project.mkdir(parents=True)
        print(f"asef_eval: no --fixture, the project starts empty; {s.case} describes: {s.fixture}", file=sys.stderr)
    copy_runtime(ROOT, project / "asef")

    if args.activation == "agents":
        target = project / "AGENTS.md"
        prefix = read(target).rstrip("\n") + "\n\n" if target.is_file() else ""
        target.write_text(prefix + agents_block(), encoding="utf-8")
        harness.append("AGENTS.md")
        message = s.request + "\n"
    elif args.activation == "skill":
        installed = run_script(INSTALLER, "--agent", args.skill_agent, "--project", str(project))
        if installed.returncode != 0:
            print(installed.stderr, file=sys.stderr)
            return 1
        harness.append(f"{AGENTS[args.skill_agent][0]}/asef")
        message = f"/asef {s.request}\n"
    else:
        built = run_script(BUILDER, "--project", str(project), "build", "--request", s.request, "--lang", args.lang)
        if built.returncode != 0:
            print(built.stderr, file=sys.stderr)
            return 1
        message = built.stdout

    baseline = git_baseline(project, harness)
    if fixture_note:
        baseline = f"{fixture_note}; {baseline}"
    (out / "MESSAGE.txt").write_text(message, encoding="utf-8")
    (out / "RESULT.md").write_text(result_template(s, args.activation, args.lang, baseline), encoding="utf-8")
    print(f"asef_eval: {s.case} prepared in {out}")
    print(f"  1. start a fresh agent session in {project}")
    print(f"  2. send the content of {out / 'MESSAGE.txt'}")
    print(f"  3. fill {out / 'RESULT.md'}, then run: asef_eval.py check {out}")
    return 0


def parse_record(path: Path) -> Record:
    record = Record(path)
    section = "fields"
    for line in read(path).splitlines():
        if line.startswith("## Criteria"):
            section = "criteria"
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        row = cells(line)
        if section == "fields" and len(row) == 2 and row[0] != "Field":
            record.fields[row[0]] = row[1]
        elif section == "criteria" and len(row) == 5 and row[0] != "#":
            record.criteria.append(dict(zip(["id", "kind", "criterion", "verdict", "evidence"], row)))
    return record


def observed_route(project: Path) -> str | None:
    """The route the agent recorded, or None when `STATE.md` names none or several."""
    state = project / "STATE.md"
    if not state.is_file():
        return None
    intent = re.search(r"^\*\*Intent:\*\*(.*)$", read(state), re.M)
    found = [r for r in ROUTES if re.search(rf"\b{r}\b", intent.group(1))] if intent else []
    return found[0] if len(found) == 1 else None


def canonical_criteria(s: Scenario) -> list[tuple[str, str, str]]:
    """The rows `prepare` writes for a case: the only rows a record may judge."""
    return [(f"E{i}", "expect", c) for i, c in enumerate(s.expected, 1)] + [
        (f"F{i}", "fail-if", c) for i, c in enumerate(s.fail_if, 1)
    ]


def evaluate(run: Path, scenarios: dict[str, Scenario] | None = None) -> tuple[list[str], dict[str, str]]:
    """Problems that make the record incomplete, and the judged summary.

    Criteria and expected route come from `examples/scenarios.md`, never from
    the editable record: a deleted, reworded or added row, or an edited route,
    makes the record incomplete instead of silently changing the verdict.
    """
    record = parse_record(run / "RESULT.md")
    problems = [f"`{name}` is not filled" for name in REQUIRED_FIELDS if record.fields.get(name, "") in UNFILLED]
    scenario = (scenarios or load_scenarios()).get(record.fields.get("case", ""))
    if scenario is None:
        problems.append(f"case `{record.fields.get('case', '')}` is not in examples/scenarios.md")
    else:
        rows = [(r["id"], r["kind"], r["criterion"]) for r in record.criteria]
        if rows != canonical_criteria(scenario):
            problems.append(f"criteria differ from case {scenario.case} in examples/scenarios.md; re-run `prepare`")
        if record.fields.get("expected route", "") != (scenario.route or "not checked"):
            problems.append(f"expected route differs from case {scenario.case} in examples/scenarios.md")
    for row in record.criteria:
        if row["verdict"] not in VERDICTS:
            problems.append(f"{row['id']}: verdict `{row['verdict']}` is not PASS, FAIL or OPEN")
        elif not row["evidence"]:
            problems.append(f"{row['id']}: {row['verdict']} without evidence")

    expected = (scenario.route or "") if scenario else ""
    route = observed_route(run / "project")
    verdicts = [row["verdict"] for row in record.criteria]
    if expected in ROUTES:
        verdicts.append("OPEN" if route is None else ("PASS" if route == expected else "FAIL"))
    verdict = "FAIL" if "FAIL" in verdicts else "OPEN" if "OPEN" in verdicts or problems else "PASS"
    summary = {
        "case": record.fields.get("case", "?"),
        "activation": record.fields.get("activation", "?"),
        "agent": record.fields.get("agent/version", "?"),
        "commit": record.fields.get("framework commit", "?"),
        "tools": record.fields.get("tools", "?"),
        "route": f"{route or 'none recorded'} (expected {expected or 'not checked'})",
        "evidence": f"{sum(v == 'PASS' for v in verdicts)} pass, {verdicts.count('FAIL')} fail, {verdicts.count('OPEN')} open",
        "verdict": verdict,
        "limitation": record.fields.get("limitation", ""),
    }
    return problems, summary


def record_line(summary: dict[str, str]) -> str:
    """One row in the result-record format `examples/scenarios.md` defines."""
    keys = ["case", "activation", "agent", "commit", "tools", "route", "evidence", "verdict", "limitation"]
    return " | ".join(summary[k] for k in keys)


def cmd_check(run: Path) -> int:
    if not (run / "RESULT.md").is_file():
        print(f"asef_eval: {run} has no RESULT.md", file=sys.stderr)
        return 2
    problems, summary = evaluate(run)
    for problem in problems:
        print(f"  incomplete  {problem}")
    print(record_line(summary))
    return 1 if problems else 0


def cmd_report(paths: list[Path]) -> int:
    runs = sorted({r.parent for p in paths for r in ([p / "RESULT.md"] if (p / "RESULT.md").is_file() else p.rglob("RESULT.md"))})
    if not runs:
        print("asef_eval: no RESULT.md found", file=sys.stderr)
        return 2
    rows = []
    incomplete = 0
    scenarios = load_scenarios()
    for run in runs:
        problems, summary = evaluate(run, scenarios)
        incomplete += bool(problems)
        rows.append(summary)
    columns = sorted({f"{r['agent']} / {r['activation']}" for r in rows})
    cases = sorted({r["case"] for r in rows})
    grid = {(r["case"], f"{r['agent']} / {r['activation']}"): r["verdict"] + ("*" if r["verdict"] == "OPEN" else "") for r in rows}
    print("| case | " + " | ".join(columns) + " |")
    print("|---|" + "---|" * len(columns))
    for case in cases:
        print(f"| {case} | " + " | ".join(grid.get((case, c), "-") for c in columns) + " |")
    print()
    for r in rows:
        print(record_line(r))
    if incomplete:
        print(f"\n{incomplete} record(s) incomplete; run `check` on each for details.")
    return 1 if incomplete else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate ASEF scenarios against any agent.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list the scenarios")
    prepare = sub.add_parser("prepare", help="build a run folder for one scenario")
    prepare.add_argument("case", help="scenario ID, e.g. W1")
    prepare.add_argument("--out", type=Path, required=True, help="run folder to create")
    prepare.add_argument("--activation", choices=ACTIVATIONS, default="prompt")
    prepare.add_argument("--lang", choices=["it", "en"], default="it", help="prompt language (prompt activation)")
    prepare.add_argument("--fixture", type=Path, help="project to copy as the starting state")
    prepare.add_argument("--skill-agent", choices=sorted(AGENTS), default="agents", help="skill path (skill activation)")
    check = sub.add_parser("check", help="validate a filled record and print its result line")
    check.add_argument("run", type=Path)
    report = sub.add_parser("report", help="aggregate runs into a case x agent matrix")
    report.add_argument("paths", type=Path, nargs="+")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    scenarios = load_scenarios()
    if args.command == "list":
        return cmd_list(scenarios)
    if args.command == "prepare":
        if args.case not in scenarios:
            print(f"asef_eval: unknown case `{args.case}`; known: {', '.join(scenarios)}", file=sys.stderr)
            return 2
        if args.fixture and not args.fixture.is_dir():
            print(f"asef_eval: fixture {args.fixture} is not a directory", file=sys.stderr)
            return 2
        return cmd_prepare(scenarios[args.case], args)
    if args.command == "check":
        return cmd_check(args.run)
    return cmd_report(args.paths)


if __name__ == "__main__":
    raise SystemExit(main())
