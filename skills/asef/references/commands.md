# ASEF skill: occasional commands

Read only when the user invokes one of these commands, or when `scan` fails. `SCRIPT` is `scripts/asef_prompt.py` in the skill directory; use `python` instead of `python3` on Windows. Each command stops after its report.

## Where the framework is found

`scan` resolves the root in this order:

1. `asef/` inside the project;
2. the project itself, when it is the framework repository;
3. `framework/` bundled next to the skill by `scripts/install.py --bundle-framework`;
4. the repository the skill lives in.

## Commands

| Argument | Action |
|---|---|
| `init` | `python3 SCRIPT init`: copy the framework (from 3 or 4 above) into `asef/` if missing; report the version. If no copy exists, tell the user to copy https://github.com/MrForty/asef into `asef/` |
| `upgrade` | `python3 SCRIPT init --upgrade`: refresh the framework files in `asef/` from the skill's newer copy; refuses a downgrade; project artifacts are untouched; report old → new version |
| `doctor` | `python3 SCRIPT doctor`: report framework, prompt versions, runtime set, installed skill copies and activation; relay each warning with its fix; change nothing |
| `status` | Read `STATE.md` (and `LEARNINGS.md` if present); report route, verified state, next action, open gaps, human actions; change nothing |

## Install the skill elsewhere

`python3 scripts/install.py --agent claude|codex|agents|cursor|copilot|gemini|opencode [--user] [--bundle-framework]`, or `--dest DIR` for any other agent; `--list` shows the paths.
