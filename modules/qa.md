# QA

**MODE:** HYBRID

## Trigger

Reviewed or existing behavior requires product-level verification, including `QA_ONLY` and `RELEASE` entries without prior review.

## Purpose

Prove the requested outcome in the closest safe environment with depth proportional to risk.

## Requires

- acceptance criteria;
- reviewed implementation or artifact;
- runnable environment or best available verification surface.

## Optional

Specialist QA/browser tooling, operational logs, fixtures, `LEARNINGS.md` and rollback procedure.

## Do not load

Unrelated product areas, full research history or destructive production credentials unless explicitly authorized and necessary.

## Depth

- **Quick:** small, low-risk, localized and reversible change.
- **Standard:** default for user-facing features and multi-layer changes.
- **Deep:** central flows and any risk class declared in the task.

Select automatically from impact and failure cost. A declared `persistence` or `deployed` trait raises the floor to `Standard`.

## Procedure

1. Map acceptance criteria to concrete checks.
2. Verify the happy path and boundary/failure paths; for existing work apply the regression gate in `guides/existing-projects.md`, separating pre-existing failures from new regressions.
3. With `ui` and a browser, verify the rendered acceptance path under `guides/web-experience.md`: responsive views, content, accessibility, real actions and applicable website delivery checks. Compare before/after for existing UI. Without a browser, visual criteria stay `OPEN`, never `FACT`.
4. Use isolated or backed-up data for destructive scenarios.
5. Confirm real integration behavior, not only mocked internals, when feasible.
6. On failure: capture minimal evidence, route to `diagnose`, fix, review and repeat affected QA. A defect surviving two QA cycles is evidence of a wrong seam: escalate to `planning`, `specification` or the user instead of repeating.
7. Record environment, commands, results and the tree verified, without dumping raw logs.

## Exit criteria

- every applicable acceptance criterion passes;
- required regression and failure paths pass;
- environment and limitations are known;
- no unresolved defect blocks the requested outcome.

## Outputs

Compact QA evidence, defects if unresolved, updated `STATE.md`, and `DONE` or release readiness.

## Next

`DONE`; `ship` when release is requested or authorized; `diagnose` on failure.
