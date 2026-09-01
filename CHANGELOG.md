# Changelog

## 1.1

- DIAGNOSE: diagnosis-only exit added to the graph, matching `modules/diagnose.md`.
- `public-surface` trait: NFR table gains the Compatibility / versioning row.
- `modules/architecture-improvement.md` Next includes `planning`; graph and Next agree.
- `REVIEW_ONLY` reports fixes without applying them; applying a fix routes to `MODIFY`.
- `fix` documented as review's internal cycle, not a module.
- PLAN readiness checklist gains the trait-consequence row.
- QA escalates after two cycles on the same defect.
- No-file-read degradation paste list gains `modules/research.md`, `DECISION-ENGINE.md` and the needed templates.
- `modules/qa.md` trigger covers `QA_ONLY` entries without prior review.
- `modules/research.md` declares ECONOMY budget defaults.
- `ARTIFACTS.md` discriminates `DECISIONS.md` log vs single decision records.
- `AUTO` and `ECONOMY` declared the only v1 modes; config keys are extension points.
- Research-only requests route via `discovery` with early `DONE`.
- Diff re-read checks for leaked secrets.
- Route metrics (question rounds, escalations, review/QA cycles) recorded in `STATE.md` at route completion.
- Stable kernel text noted as prompt-caching input in `CONTEXT-MANAGER.md`.

## 1.0

- Initial framework: kernel, router, decision engine, context manager, artifacts, 12 modules, 6 templates, universal prompt.
