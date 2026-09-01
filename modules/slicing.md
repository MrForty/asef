# Slicing

**MODE:** NATIVE

## Trigger

The work is too large or coupled for one safe implementation context.

## Purpose

Convert the plan into ordered vertical slices, each small enough for one focused context and independently verifiable.

## Requires

- relevant `SPEC.md` acceptance criteria;
- relevant `PLAN.md` sections.

## Optional

Repository structure, dependencies and existing task conventions.

## Do not load

Conversation history, unrelated backlog or detailed future slices while executing the current one.

## Procedure

1. Identify the thinnest end-to-end path that produces observable value or reduces decisive risk.
2. For `GREENFIELD`, make the first task a walking skeleton: one thin end-to-end path carrying the repository, the test seam and the verification commands recorded in `PROJECT.md`.
3. Create slices across required layers rather than horizontal component batches.
4. Give each task one outcome, bounded scope, dependencies, test seam and pass/fail criteria.
5. Order tasks by risk reduction and enablement; minimize cross-task coupling.
6. Mark a task `parallel-safe` only when it shares no file, schema or contract with another ready task.
7. Ensure each task can be resumed from artifacts without prior conversation.
8. Avoid placeholder infrastructure unless a current slice exercises it.

## Exit criteria

- every acceptance criterion maps to one or more tasks;
- each task is independently verifiable and context-sized;
- dependencies are explicit and acyclic where practical;
- the first task delivers behavior or validates the highest-risk assumption;
- for `GREENFIELD`, the first task leaves a runnable verification command;
- every `parallel-safe` mark is justified by disjoint files, schema and contracts.

## Outputs

`tasks/TASK-NNN.md` files and task pointers in `STATE.md`.

## Next

`implementation` for the first ready task.
