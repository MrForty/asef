#!/usr/bin/env python3
"""Tests for `tools/asef_eval.py`: the scenario harness keeps its promise.

The harness promises that every scenario is parsed into judgeable criteria,
that a run folder carries the runtime framework and exactly one activation,
and that a record is judged from evidence, with the route read from
`STATE.md` rather than self-reported. Standard library only.

    python3 tools/test_asef_eval.py
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL = ROOT / "tools" / "asef_eval.py"

sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
import asef_eval  # noqa: E402 - module under test

FAILURES: list[str] = []


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(EVAL), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def check(label: str, condition: bool, detail: str = "") -> None:
    print(f"{'PASS' if condition else 'FAIL'}  {label}")
    if not condition:
        FAILURES.append(f"{label}\n{detail.strip()}")


def fill(record: Path, verdict: str = "PASS", evidence: str = "screenshots/menu-narrow.png") -> None:
    text = record.read_text(encoding="utf-8")
    text = text.replace("| agent/version | ? |", "| agent/version | test-agent 1.0 |")
    text = text.replace("| tools | ? |", "| tools | files, execution, git |")
    text = re.sub(r"^(\| [EF][0-9]+ \| [^|]+ \| [^|]+ \| )[^|]+ \| [^|]*\|$", rf"\g<1>{verdict} | {evidence} |", text, flags=re.M)
    record.write_text(text, encoding="utf-8")


def write_state(project: Path, route: str) -> None:
    (project / "STATE.md").write_text(f"# State\n\n**Status:** `DONE`  \n**Intent:** `{route}`  \n", encoding="utf-8")


def test_scenarios() -> None:
    scenarios = asef_eval.load_scenarios()
    check("scenarios: every case of the table is parsed", len(scenarios) == 10 and {"W1", "W4", "E1"} <= set(scenarios), ", ".join(scenarios))
    check("scenarios: every case has a request and criteria of both kinds", all(s.request and s.expected and s.fail_if for s in scenarios.values()))
    check("scenarios: expected routes are real routes", all(s.route in (None, *asef_eval.ROUTES) for s in scenarios.values()))
    check("scenarios: the route is taken out of the criteria", scenarios["W4"].route == "DIAGNOSE" and "DIAGNOSE" not in scenarios["W4"].expected)
    listing = run("list")
    check("list: names every case", listing.returncode == 0 and all(case in listing.stdout for case in scenarios))


def test_prepare(tmp: Path) -> None:
    prompt_run = tmp / "w4-prompt"
    result = run("prepare", "W4", "--out", str(prompt_run))
    project = prompt_run / "project"
    check("prepare: builds the run folder", result.returncode == 0 and (project / "asef" / "ASEF.md").is_file() and (prompt_run / "RESULT.md").is_file(), result.stderr)
    check("prepare: the framework copy is the runtime set only", not (project / "asef" / "CLAUDE.md").exists() and not (project / "asef" / "tools").exists())
    message = (prompt_run / "MESSAGE.txt").read_text(encoding="utf-8")
    check("prepare: prompt activation sends the filled prompt", "## Bootstrap" in message and "Richiesta: Fix the mobile menu." in message)
    check("prepare: warns when no fixture is given", "no --fixture" in result.stderr)
    record = (prompt_run / "RESULT.md").read_text(encoding="utf-8")
    check("prepare: record lists the criteria of the case", "| F1 | fail-if | GREENFIELD solely because STATE/SPEC is absent | ? |  |" in record and "| expected route | DIAGNOSE |" in record)

    english = run("prepare", "W4", "--out", str(tmp / "w4-en"), "--lang", "en")
    check("prepare: --lang en sends the English prompt", english.returncode == 0 and "Request: Fix the mobile menu." in (tmp / "w4-en" / "MESSAGE.txt").read_text(encoding="utf-8"), english.stderr)

    fixture = tmp / "fixture"
    fixture.mkdir()
    (fixture / "index.html").write_text("<nav></nav>\n", encoding="utf-8")
    (fixture / "AGENTS.md").write_text("# Project rules\n", encoding="utf-8")
    agents_run = tmp / "w4-agents"
    result = run("prepare", "W4", "--out", str(agents_run), "--activation", "agents", "--fixture", str(fixture))
    agents_md = (agents_run / "project" / "AGENTS.md").read_text(encoding="utf-8")
    check("prepare: fixture copied", result.returncode == 0 and (agents_run / "project" / "index.html").is_file(), result.stderr)
    check("prepare: agents activation appends the block to the fixture's AGENTS.md", agents_md.startswith("# Project rules") and "asef/ASEF.md" in agents_md and "<!--" not in agents_md)
    check("prepare: agents activation sends the bare request", (agents_run / "MESSAGE.txt").read_text(encoding="utf-8") == "Fix the mobile menu.\n")

    skill_run = tmp / "w4-skill"
    result = run("prepare", "W4", "--out", str(skill_run), "--activation", "skill", "--skill-agent", "claude")
    check(
        "prepare: skill activation installs the skill and sends /asef",
        result.returncode == 0 and (skill_run / "project" / ".claude" / "skills" / "asef" / "SKILL.md").is_file()
        and (skill_run / "MESSAGE.txt").read_text(encoding="utf-8") == "/asef Fix the mobile menu.\n",
        result.stderr,
    )

    again = run("prepare", "W4", "--out", str(prompt_run))
    check("prepare: refuses a non-empty run folder", again.returncode == 2 and "not empty" in again.stderr)
    unknown = run("prepare", "Z9", "--out", str(tmp / "z9"))
    check("prepare: rejects an unknown case", unknown.returncode == 2 and "unknown case" in unknown.stderr)


def test_check(tmp: Path) -> None:
    run_dir = tmp / "judged"
    run("prepare", "W4", "--out", str(run_dir))
    project = run_dir / "project"

    empty = run("check", str(run_dir))
    check("check: an unfilled record is incomplete", empty.returncode == 1 and "`agent/version` is not filled" in empty.stdout and "is not PASS, FAIL or OPEN" in empty.stdout)

    fill(run_dir / "RESULT.md", evidence="")
    no_evidence = run("check", str(run_dir))
    check("check: a verdict without evidence is incomplete", no_evidence.returncode == 1 and "PASS without evidence" in no_evidence.stdout)

    fill(run_dir / "RESULT.md")
    missing_state = run("check", str(run_dir))
    check("check: without STATE.md the route stays OPEN", missing_state.returncode == 0 and "| OPEN |" in missing_state.stdout and "none recorded" in missing_state.stdout, missing_state.stdout)

    write_state(project, "DIAGNOSE")
    passed = run("check", str(run_dir))
    check("check: all criteria and the route observed is a PASS", passed.returncode == 0 and "| PASS |" in passed.stdout and "DIAGNOSE (expected DIAGNOSE)" in passed.stdout, passed.stdout)

    write_state(project, "GREENFIELD")
    wrong_route = run("check", str(run_dir))
    check("check: a wrong route in STATE.md is a FAIL", "| FAIL |" in wrong_route.stdout and "GREENFIELD (expected DIAGNOSE)" in wrong_route.stdout, wrong_route.stdout)

    write_state(project, "GREENFIELD | MODIFY | DIAGNOSE")
    template = run("check", str(run_dir))
    check("check: an unfilled Intent line records no route", "none recorded" in template.stdout, template.stdout)

    other = tmp / "other"
    run("prepare", "R1", "--out", str(other))
    fill(other / "RESULT.md", verdict="FAIL", evidence="src/app.css changed")
    write_state(other / "project", "REVIEW_ONLY")
    failed = run("check", str(other))
    check("check: one failed criterion fails the run", failed.returncode == 0 and "| FAIL |" in failed.stdout)

    run("prepare", "W1", "--out", str(tmp / "unfilled"))
    report = run("report", str(tmp))
    check(
        "report: aggregates every run into one matrix",
        "| case | ? / prompt | test-agent 1.0 / prompt |" in report.stdout and "| R1 | - | FAIL |" in report.stdout and "record(s) incomplete" in report.stdout,
        report.stdout,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp).resolve()
        test_scenarios()
        test_prepare(tmp / "prepare")
        test_check(tmp / "check")

    print()
    if FAILURES:
        for failure in FAILURES:
            print(f"--- {failure}\n")
        print(f"{len(FAILURES)} check(s) failed.")
        return 1
    print("All evaluation harness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
