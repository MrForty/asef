# Architecture Improvement

**MODE:** HYBRID

## Trigger

Refactor, technical debt or structural quality limits current outcomes.

## Purpose

Improve a proven architectural pain with minimal behavioral change.

## Requires

- concrete pain, risk or maintenance evidence;
- relevant architecture, code and tests.

## Optional

Change history, runtime metrics, `LEARNINGS.md` and specialist architecture tooling.

## Do not load

Unrelated domains, speculative scale requirements or fashionable patterns without evidence.

## Procedure

1. State the observed problem, affected flow and measurable improvement.
2. Trace ownership, coupling, duplication and failure boundaries.
3. Reuse an existing project pattern where possible.
4. Compare the no-change option with the smallest structural change.
5. Preserve external behavior unless the specification explicitly changes it.
6. Define migration order, compatibility, rollback and regression checks; declare the risk classes the change touches.
7. Split into vertical or expand-migrate-contract slices under `modules/slicing.md` only if needed.

## Exit criteria

- improvement addresses evidenced pain;
- change is smaller than the complexity it removes;
- behavior, migration and rollback are verifiable;
- no speculative abstraction or new dependency remains.

## Outputs

Updated `PLAN.md` or focused decision; tasks if needed; `STATE.md` update.

## Next

`planning` if the change requires durable coordination beyond the improvement; otherwise `implementation` or `slicing`.
