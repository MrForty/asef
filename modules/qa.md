# QA

**MODE:** HYBRID

## Trigger

Reviewed or existing behavior requires product-level verification.

## Purpose

Prove the requested outcome in the closest safe environment with depth proportional to risk.

## Requires

- acceptance criteria;
- reviewed implementation or artifact;
- runnable environment or best available verification surface.

## Optional

Specialist QA/browser tooling, operational logs, fixtures and rollback procedure.

## Do not load

Unrelated product areas, full research history or destructive production credentials unless explicitly authorized and necessary.

## Depth

- **Quick:** small, low-risk, localized and reversible change.
- **Standard:** default for user-facing features and multi-layer changes.
- **Deep:** auth, payments, security, critical data, migrations, concurrency or central flows.

Select automatically from impact and failure cost. A declared `persistence` or `deployed` trait raises the floor to `Standard`.

## Procedure

1. Map acceptance criteria to concrete checks.
2. Verify the happy path and applicable boundary/failure paths.
3. Use isolated or backed-up data for destructive scenarios.
4. Confirm real integration behavior, not only mocked internals, when feasible.
5. On failure: capture minimal evidence, route to `diagnose`, fix, review and repeat affected QA. A defect surviving two QA cycles is evidence of a wrong seam: escalate to `planning`, `specification` or the user instead of repeating.
6. Record environment, checks and results without dumping raw logs.

## Exit criteria

- every applicable acceptance criterion passes;
- required regression and failure paths pass;
- environment and limitations are known;
- no unresolved defect blocks the requested outcome.

## Outputs

Compact QA evidence, defects if unresolved, updated `STATE.md`, and `DONE` or ship readiness.

## Next

`DONE`, authorized shipping, or `diagnose` on failure.
