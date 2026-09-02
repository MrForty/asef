# Context Manager

## Purpose

Provide minimum sufficient context for the active module and keep context growth reversible.

## Memory levels

- **Persistent:** goals, constraints, specification, plan, durable decisions, learnings and verified project state. Store in artifacts.
- **Working:** current task, relevant files, active hypothesis and focused evidence. Keep only for the active module.
- **Ephemeral:** raw outputs, rejected attempts and exploratory reasoning. Discard after use.

## Progressive loading

Load in this order and stop as soon as the task is answerable:

1. `ASEF.md`.
2. `STATE.md`, then `LEARNINGS.md`, if present.
3. Current task or explicit request.
4. Selected module.
5. Relevant sections of `PROJECT.md`, `SPEC.md`, `PLAN.md` and decisions.
6. Directly affected code, tests, schema and runtime evidence.
7. Callers, dependencies and adjacent context needed to validate the real flow.
8. Targeted research or broader repository context only when evidence remains insufficient.

## Do not load by default

- complete conversation history;
- all ASEF modules;
- whole artifacts when a section is sufficient;
- `RESEARCH.md` rows unrelated to the current gaps;
- complete repository trees or unrelated files;
- closed tasks, rejected alternatives or raw research logs;
- subagent transcripts or raw search output; keep only the returned answer packet.

## Context budget

In `ECONOMY` mode:

- retrieve before summarizing;
- quote identifiers and facts, not long passages;
- prefer one current vertical task per context;
- use links or paths to canonical sources rather than duplicating them;
- expand context only for a named uncertainty;
- keep kernel and module text stable across sessions so provider prompt caching can amortize them.

If the active task no longer fits cleanly, update artifacts and hand off a compact packet:

```text
Goal:
Current task:
Verified state (tree or commit):
Relevant artifacts/files:
Decisions/assumptions:
Checks run and results:
Next action:
Blockers:
```

## Parallel contexts

One task per context. A parallel context receives its task file and the handoff packet, isolates its changes under the version-control rules in `ASEF.md`, and returns only an evidence packet. The orchestrating context integrates results and is the single writer of `STATE.md`.

## Exit compression

At module completion retain only:

- artifact changes;
- durable decisions and assumptions;
- verification evidence;
- remaining blockers or limitations;
- next state.

Discard intermediate reasoning, duplicated source text, failed attempts without future value and stale hypotheses.

## Output

Update `STATE.md` to point to canonical artifacts and the next action. `STATE.md` must remain reconstructive, compact and current.
