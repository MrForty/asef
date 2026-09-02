# Implementation

**MODE:** HYBRID

## Trigger

An executable task or small well-defined change is ready.

## Purpose

Implement one vertical outcome with the smallest correct change and leave runnable evidence.

## Requires

- current task or explicit request;
- relevant `STATE.md`;
- directly affected source and tests.

## Optional

Relevant sections of `SPEC.md`, `PLAN.md`, decisions and `LEARNINGS.md`; specialist implementation or TDD tooling when justified.

## Do not load

Full chat, all tasks, all artifacts, complete repository or unrelated modules.

## Procedure

1. Inspect the actual end-to-end flow, existing helpers, conventions and callers.
2. Confirm the task's acceptance criteria, risk classes and test seam; a seam is a public boundary, never a private internal.
3. For non-trivial behavior, establish the smallest failing automated check when practical.
4. Implement the minimum root-cause change using existing code, platform features and dependencies first.
5. Run focused tests and static checks; refactor only to remove present duplication or risk.
6. Re-read the diff for unintended scope, debug artifacts and leaked secrets; preserve unrelated working changes.
7. Commit the task under the version-control rules in `ASEF.md`.
8. Update task/state evidence with command, result and tree; do not redesign upstream product decisions locally.

Tasks marked `parallel-safe` may run in separate contexts under `CONTEXT-MANAGER.md`.

A pending `HUMAN-ACTION` blocks only the steps that need it: complete the rest, deliver the action block once, mark the task `BLOCKED` on it.

If evidence invalidates architecture, return to `planning`. If it invalidates behavior or value, return to `specification` or `product-scope`.

## Exit criteria

- task behavior works at the agreed seam;
- focused checks pass;
- failure handling and trust boundaries remain sound;
- diff contains no speculative work;
- the task is committed, or its change set recorded when git is unavailable;
- relevant artifacts match reality.

## Outputs

Working increment, focused checks, commit, task evidence and updated `STATE.md`.

## Next

`review`.
