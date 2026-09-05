# Review

**MODE:** HYBRID

## Trigger

An implementation, plan or diff requires validation before QA or completion.

## Purpose

Review independently across specification, engineering and risk; automatically fix clear in-scope findings.

## Requires

- current task, its acceptance criteria and declared risk classes;
- relevant diff or changed artifacts;
- applicable project conventions.

## Optional

Relevant plan, `LEARNINGS.md`, specialist review tooling, runtime evidence and adjacent callers.

## Do not load

Unchanged repository areas without a dependency path, unrelated tasks or historical deliberation.

## Procedure

Review three independent axes always:

1. **Specification fidelity:** required behavior, scope and acceptance criteria.
2. **Engineering quality:** correctness, simplicity, reuse, maintainability, error handling and tests.
3. **Risk and safety:** security, privacy, data integrity, migrations, concurrency, side effects, trust boundaries, dependency provenance and licensing, failure and rollback.

Add one axis per trait declared in `PROJECT.md`, and only those:

| Trait | Axis |
|---|---|
| `ui` | Matches the `SPEC.md` UI section; empty, loading and error states covered; visual hierarchy; accessibility basics; no generic template pattern where the spec chose a specific one |
| `public-surface` | Surface shape, naming, defaults, error messages, breaking-change exposure, documented seam |
| `typed` | Types express the contract, illegal states unrepresentable, validation at trust boundaries, escape hatches justified in place |

Add one threat pass per declared risk class; require a concrete attacker or operational failure path, including accidental data loss and race conditions:

| Class | Threat pass |
|---|---|
| `auth` | authorization checked per resource, not per route; session fixation and privilege escalation; secrets never logged |
| `payments` | webhook signature verified; charges idempotent; amount and currency decided server-side; reconciliation path |
| `tenant` | every query and cache key scoped by tenant; ids not guessable across tenants; background jobs carry tenant context |
| `pii` | minimization; retention, export and deletion paths; no personal data in logs or analytics |
| `migration` | reversible; backfill order; dual-read or dual-write window; rollback tested |
| `concurrency` | idempotent retries; ordering; locks or versions; no duplicate side effect |

Use permitted parallel contexts when useful; otherwise review axes sequentially under `CONTEXT-MANAGER.md`. Return findings with comparable impact and evidence across axes.

A finding names file and line, quotes the code and states the failure scenario; anything less is a note and opens no fix cycle. Rank findings by impact and evidence. Ignore style preferences without consequence. Fix clear authorized findings, rerun focused checks, then re-review the affected axis. Escalate only findings requiring a product decision, new authority or unsafe destructive action.

Under `REVIEW_ONLY` report fixes instead of applying them; applying a fix routes the work to `MODIFY`.

Cap the loop at two fix cycles per finding. A finding surviving the second cycle is evidence of a wrong seam, not a wrong patch: escalate it to `planning` or the user instead of iterating.

## Exit criteria

- all applicable axes pass, fixed, trait and threat pass alike;
- no blocking or high-impact finding remains;
- fixes are verified and re-reviewed;
- residual limitations are explicit.

## Outputs

Verified fixes; concise findings only when unresolved or requested; updated task and `STATE.md`.

## Next

`qa`; `DONE` under `REVIEW_ONLY`; otherwise the precise failed upstream gate.
