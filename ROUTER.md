# Router

## Purpose

Select the smallest workflow that can complete the request. Routes are graphs: skip unnecessary nodes and return only to a failed gate.

## Classification

| Intent | Route |
|---|---|
| New product or materially undefined initiative | `GREENFIELD` |
| Feature or behavior change | `MODIFY` |
| Bug, failure or regression | `DIAGNOSE` |
| Refactor, debt or structural improvement | `IMPROVE` |
| External code, repository or component integration | `REUSE` |
| Review-only request | `REVIEW_ONLY` |
| Verification-only request | `QA_ONLY` |

When multiple intents exist, start with the one that removes the greatest uncertainty or risk. Do not force discovery onto a well-defined bug or task.

## Routes

```text
GREENFIELD
discovery → product-scope → specification → planning → slicing
→ implementation → review ⇄ fix → qa → DONE

MODIFY
specification? → planning? → slicing? → implementation
→ review ⇄ fix → qa → DONE

DIAGNOSE
diagnose → implementation → review ⇄ fix → qa → DONE
diagnose → DONE when the fix is not authorized

IMPROVE
architecture-improvement → planning? → slicing? → implementation
→ review ⇄ fix → qa → DONE

REUSE
reuse-integration → specification? → planning? → slicing?
→ implementation → review ⇄ fix → qa → DONE

REVIEW_ONLY
review → DONE

QA_ONLY
qa → DONE
```

`?` means load only if the preceding evidence cannot safely determine execution. `fix` is the fix cycle inside `review`, not a separate module.

`research` is not a route node. Any module invokes it in place to resolve `RESEARCHABLE` gaps, then continues.

## Routing rules

- Existing executable task with acceptance criteria: start at `implementation`.
- `RESEARCHABLE` gaps: invoke `research` from the active module; never open a separate route.
- Unknown cause: start at `diagnose`, not implementation.
- Product uncertainty: route to `discovery` or `product-scope` only for the unresolved portion.
- Research-only request: enter `discovery` and exit at `DONE` once the question is answered; no scoping follows.
- Architecture invalidated during implementation: return to `planning`.
- Requested behavior invalidated: return to `specification` or `product-scope`.
- Review finding: fix locally, then re-review the affected axis.
- QA failure: diagnose the failure, fix it, re-run focused review and QA.
- Stop when the request is satisfied and Definition of Done passes; do not traverse optional nodes for ceremony.

## Output

Record in `STATE.md`: intent, active module, reason, required inputs and next gate.
