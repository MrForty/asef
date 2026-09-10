---
name: asef
description: Run a software task under ASEF (Agentic Software Engineering Framework) — new web app, SaaS or professional website, a feature, a bug, a refactor, an integration, a review, QA or a release. Turns a one-line goal into the full ASEF activation prompt and executes it, so nobody pastes the framework prompt by hand. Use whenever the user invokes /asef, mentions ASEF or "the framework", or asks for project work in a repository that carries an `asef/` folder or ASEF artifacts (STATE.md, PROJECT.md, SPEC.md).
argument-hint: "<goal> | prompt <goal> | init | status"
metadata:
  framework: ASEF
  homepage: https://github.com/MrForty/asef
---

# ASEF skill

Request: $ARGUMENTS

If the line above is empty or still reads `$ARGUMENTS`, the request is the text the user wrote after the skill name. With no text at all, ask one question: what should be achieved? Then continue.

The framework owns every rule (routes, gaps, questions, review, release). This skill only locates it, fills the request block of `prompt universale ASEF.txt`, and hands the result over. Never restate or reconstruct framework rules from memory.

## 1. Locate the framework

`SCRIPT` = `scripts/asef_prompt.py` in this skill's directory (`${CLAUDE_SKILL_DIR}` in Claude Code; otherwise the path this file was loaded from).

Run `python3 SCRIPT scan` from the project root (`python` on Windows). It resolves the root in this order and prints it with versions and detected artifacts:

1. `asef/` inside the project;
2. the project itself, when it is the framework repository;
3. `framework/` bundled next to this skill by `scripts/install.py --bundle-framework`;
4. the repository this skill lives in.

Exit code 2 means no framework: run `python3 SCRIPT init` (copies from 3 or 4) or, when that fails too, tell the user to copy https://github.com/MrForty/asef into `asef/`. Do not proceed without it.

Without command execution, do the same by hand: find `asef/ASEF.md`, then copy `prompt universale ASEF.txt` verbatim and fill only its final block.

## 2. Commands

| Argument | Action |
|---|---|
| `<goal>` | Build the prompt (3) and execute it (4) |
| `prompt <goal>` | Build the prompt and print it verbatim inside a four-backtick fence (it contains three-backtick blocks); stop. For agents without skills, or for review before running |
| `init` | Install the framework into `asef/` if missing; report version; stop |
| `status` | Read `STATE.md` (and `LEARNINGS.md` if present); report route, verified state, next action, open gaps, human actions; change nothing |

## 3. Build the prompt

Map the user's words onto the request block. The block's reading rules (empty field = gap, constraints and non-goals binding, release authorization explicit) are the framework's contract, so:

- `--request`: one sentence, the user's goal in their words. Not a plan.
- `--who`, `--today`, `--asked`, `--verify`: only what the user actually stated. Empty is correct; the gap policy handles it. Never invent context.
- `--constraint` / `--non-goal` (repeatable): only explicit limits ("keep the stack", "no redesign", "must stay in Italian").
- `--release`: `commit` / `"pull request"` / `merge` / `deploy` only when the user said so ("and commit", "open a PR", "deploy it"). Otherwise omit: it defaults to `nessuna`. The skill never grants authorization.
- `--artifact` (repeatable): files or folders the user named; canonical ASEF artifacts are detected automatically.
- `--spec PATH` when the user points at an existing deliberate specification; `--route NAME` only when they impose one.

```
python3 SCRIPT build --request "..." [--who ...] [--constraint ...]... [--release ...] [--artifact ...]...
```

Do not pre-classify new vs existing project, stack, or route: `ROUTER.md` does that from the evidence, including the artifact list the script filled. Do not ask the user anything before building; the framework batches its own questions.

## 4. Execute the prompt

Treat the script output exactly as a prompt the user pasted: start at its Bootstrap step 1 (read `asef/ASEF.md`, or the root the prompt names), emit the first-output block from `ROUTER.md` in the user's language, then run the route. Missing capabilities follow `CONTEXT-MANAGER.md`; they never waive gates.

If the project already activates ASEF permanently (its `AGENTS.md` or `CLAUDE.md` carries the block from `templates/AGENTS.template.md`), still use the full prompt: it adds nothing the kernel does not own, and it carries the request block.

## Install elsewhere

`python3 scripts/install.py --agent claude|codex|agents|cursor|copilot|gemini|opencode [--user] [--bundle-framework]`, or `--dest DIR` for any other agent; `--list` shows the paths.
