# Review

**MODE:** HYBRID

## Trigger

An implementation, plan or diff requires validation before QA or completion.

## Purpose

Review independently across specification, engineering and risk; automatically fix clear in-scope findings.

## Requires

- current task and acceptance criteria;
- relevant diff or changed artifacts;
- applicable project conventions.

## Optional

Relevant plan, specialist review tooling, runtime evidence and adjacent callers.

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
| `ui` | Visual hierarchy, state coverage for empty, loading and error, accessibility basics |
| `public-surface` | Surface shape, naming, defaults, error messages, breaking-change exposure, documented seam |
| `typed` | Types express the contract, illegal states unrepresentable, validation at trust boundaries, escape hatches justified in place |

Rank findings by impact and evidence. Ignore style preferences without consequence. Fix clear authorized findings, rerun focused checks, then re-review the affected axis. Escalate only findings requiring a product decision, new authority or unsafe destructive action.

Under `REVIEW_ONLY` report fixes instead of applying them; applying a fix routes the work to `MODIFY`.

Cap the loop at two fix cycles per finding. A finding surviving the second cycle is evidence of a wrong seam, not a wrong patch: escalate it to `planning` or the user instead of iterating.

## Exit criteria

- all applicable axes pass, fixed and trait alike;
- no blocking or high-impact finding remains;
- fixes are verified and re-reviewed;
- residual limitations are explicit.

## Outputs

Verified fixes; concise findings only when unresolved or requested; updated task and `STATE.md`.

## Next

`qa`, or the precise failed upstream gate.
