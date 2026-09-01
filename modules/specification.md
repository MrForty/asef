# Specification

**MODE:** NATIVE

## Trigger

Behavior must be made executable before planning or implementation.

## Purpose

Produce a compact specification that a fresh agent can implement without reinterpreting the request.

## Requires

- user outcome and scope;
- existing `SPEC.md`, if any;
- relevant current behavior when modifying a system.

## Optional

Relevant code, schema, APIs, tests, decisions and research.

## Do not load

Full chat history, entire repository, unrelated specifications or premature solution detail.

## Procedure

1. Harvest existing facts; do not re-interview.
2. Inspect code and artifacts before asking technical questions.
3. Build the gap ledger under the kernel gap policy.
4. Resolve `RESEARCHABLE` gaps through `research`; ask surviving `USER-DECISION` gaps in one round.
5. Define proposed behavior, boundaries, failure behavior and compatibility.
6. Select stable observable test seams, preferring existing high-level seams.
7. Write pass/fail acceptance criteria, risks and rollback where applicable.
8. Self-review: could a fresh agent implement this without material interpretation?

## Exit criteria

- behavior and non-goals are unambiguous;
- acceptance criteria are observable and pass/fail;
- edge and failure behavior are covered proportionally;
- test seams exist;
- material open decisions are resolved or explicitly blocking.

## Outputs

Canonical `SPEC.md`; relevant decisions; `STATE.md` update.

## Next

`planning`, or `implementation` for a small change whose technical path is already evident.
