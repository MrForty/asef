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

Relevant decisions, schemas, deployment constraints and operational evidence.

## Do not load

Unrelated modules, speculative future requirements or complete repository context.

## Procedure

1. Reuse current patterns and components before proposing new ones.
2. With no existing baseline, resolve stack, dependency and hosting gaps through `research` and record the outcome as a decision.
3. Apply scope and complexity gates; remove architecture not required by the spec.
4. Trace end-to-end data and control flow, ownership and trust boundaries.
5. Define persistence, interfaces, failure handling and compatibility only where relevant.
6. Define test strategy, rollout, rollback and operational checks proportionate to risk.
7. Validate security, data integrity, performance and deployment implications where applicable.
8. Confirm every planned element maps to an acceptance criterion or risk control.

## Exit criteria

- data/control flow and affected components are clear;
- important failures and trust boundaries have handling;
- verification and rollback are executable;
- every declared trait has its planned consequence;
- no unjustified service, abstraction, dependency or artifact remains;
- plan is ready to slice or directly implement.

## Outputs

Canonical `PLAN.md`; durable decisions; `STATE.md` update.

## Next

`slicing` when multiple independently verifiable increments are needed; otherwise `implementation`.
