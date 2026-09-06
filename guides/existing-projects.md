# Existing Projects

## When to load

The request changes or assesses an existing application, SaaS or website. Load once for the affected flow; reuse the recorded baseline until changed evidence invalidates it. Missing ASEF artifacts never make an existing project greenfield.

## Baseline before edits

1. Read local instructions; inspect worktree changes, manifests, lockfiles, commands and the affected entry point. Do not overwrite another author's work or regenerate configuration blindly.
2. Trace the request through callers, components, APIs, permissions and storage as applicable. Inspect shared consumers before changing a shared contract. For UI, capture the affected current view when a browser is available.
3. Run the smallest relevant existing checks; distinguish pre-existing failures from regressions. Missing execution leaves the baseline `OPEN`, not green. Do not reset databases or run destructive checks on live data.
4. Record in the current task's Evidence, or the smallest existing artifact: baseline/tree, requested delta, invariants to preserve, affected paths, verification and rollback. Create only missing artifacts required by this change; use existing canonical docs instead of duplicating them.

## Change boundary

- Preserve the stack, dependency versions, routes, API/data contracts, permissions, content and design system outside the requested delta. Broken or unsafe behavior is evidence to fix or escalate, not a reason to preserve a vulnerability.
- Diagnose defects before patching. A redesign goes through `specification`; refactoring follows `IMPROVE`; review-only remains read-only. Add no discovery interview for a known change.
- Prefer a local patch or reusable existing primitive. Rewrite, framework migration, dependency replacement or redesign needs an evidenced limitation, explicit scope and a rollback path; being old is not a limitation.
- Where tests are absent, add the smallest characterization check at the changed public seam. Preserve valid observed behavior; define the intended result for the defect instead of freezing it into a test.
- Apply migrations in reversible increments. For websites retain working URLs, content and integrations; redirects and metadata changes are part of the requested delta, never collateral cleanup.

## Regression gate

Verify the requested change, one affected adjacent/shared consumer and applicable boundary/failure cases. For a shared component, cover each materially different consumer variant. Compare before/after with the same conditions; test data retention, authorization and URL continuity when touched. Re-run baseline checks after edits; record unrelated failures separately without claiming the whole project passes.

Review the final diff for collateral changes. Deliver the changed behavior, evidence, known limitations and rollback; update the canonical artifacts. Continue through the active route's review and QA, then release only within authorization.
