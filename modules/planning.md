# Planning

**MODE:** NATIVE

## Trigger

The specification is ready but implementation needs durable technical coordination.

## Purpose

Define the minimum safe architecture and execution strategy that satisfies the specification.

## Requires

- relevant `PROJECT.md` constraints;
- canonical `SPEC.md`;
- current architecture/code evidence for existing systems.

## Optional

Relevant decisions, schemas, deployment constraints, `LEARNINGS.md` and operational evidence.

## Do not load

Unrelated modules, speculative future requirements or complete repository context.

## Procedure

1. Reuse current patterns and components before proposing new ones.
2. With no existing baseline, resolve stack, dependency and hosting gaps through `research` at the depth their reversibility class requires; record the outcome as a decision with the alternatives rejected.
3. Apply scope and complexity gates; remove architecture not required by the spec.
4. Trace end-to-end data and control flow, ownership and trust boundaries.
5. Define persistence, interfaces, failure handling and compatibility only where relevant; for every risk class the change touches, state boundary, failure and idempotency handling.
6. Define test strategy, rollout, rollback and operational checks proportionate to risk; with `deployed`, name environments, rollout order and rollback; with `persistence`, migration order, backfill and reversibility.
7. List every `HUMAN-ACTION` prerequisite with location, value to capture and destination.
8. Validate security, data integrity, performance and deployment implications where applicable.
9. Confirm every planned element maps to an acceptance criterion or risk control.

## Exit criteria

- data/control flow and affected components are clear;
- important failures and trust boundaries have handling;
- every risk class touched has boundary, failure and idempotency handling;
- verification and rollback are executable;
- every declared trait has its planned consequence;
- human actions are listed, or `None`;
- no unjustified service, abstraction, dependency or artifact remains;
- plan is ready to slice or directly implement.

## Outputs

Canonical `PLAN.md`; durable decisions; `STATE.md` update.

## Next

`slicing` when multiple independently verifiable increments are needed; otherwise `implementation`.
