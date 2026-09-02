# Changelog

## 1.5

Memory, portability, enforcement.

- `LEARNINGS.md` core artifact with template: pitfalls, quirks and command fixes; read at runtime step 2; route metrics gain a consumer (two escalations or a repeated question round write an entry). `diagnose`, `review`, `qa`, `ship` consult it.
- `RESEARCH.md` core artifact with template: the resolved gap ledger `research` deduplicates against; revisit triggers checked at route start, required to be concrete.
- `PROJECT.md` Domain Terms table; artifacts, identifiers and questions use the terms verbatim.
- `templates/AGENTS.template.md`: activation block for the target project's `AGENTS.md`/`CLAUDE.md`, so sessions resume without pasting the prompt.
- `SPEC.md` UI section, switched on by `ui`; `review` checks against it and flags generic template patterns.
- Version control section in `ASEF.md`: branch per route, one commit per task, no history rewrite, release actions only in `ship`; `CONTEXT-MANAGER.md` defines parallel contexts and the single `STATE.md` writer.
- Documentation currency enters the Definition of Done.
- Activation prompt: `browser` and `git` capability rows, `Azioni umane` in the first output, release authorizations in the request block, `HUMAN-ACTION` label.
- Linter: promised trait consumers, risk-class consumers, mandatory template sections and environment rows, prompt ↔ kernel alignment for routes, traits and labels, per-file token budgets. Six new mutation tests.
- README and CLAUDE.md updated: eight routes, thirteen modules, nine templates, budgets.

## 1.4

Decisions, evidence, security.

- Risk classes (`auth`, `payments`, `tenant`, `pii`, `migration`, `concurrency`) declared per task; consumed by `planning` (trust-boundary row), `review` (threat pass with concrete attacker path) and `qa` (`Deep` floor).
- `research` depth follows the reversibility class; stack, dependency and hosting choices compare on stated criteria.
- Finding contract in `review`: file, line, quoted code and failure scenario, or it is a note and opens no fix cycle; axes run in isolated contexts when available.
- `diagnose`: rerunnable reproduction before any fix; three rejected hypotheses escalate; edits confined to the traced path.
- `DECISION-ENGINE.md`: `Expensive` and `One-way` decisions record alternatives including no change; `DECISION.template.md` gains Alternatives Considered, `DECISIONS.template.md` the column.
- `product-scope` compares the wedge with doing nothing and the closest existing product.
- Evidence freshness in `ARTIFACTS.md`: command, result and tree; evidence older than the last code change is stale. `STATE.md` records the tree verified.
- `slicing`: expand, migrate, contract for wide mechanical changes; risk classes per task.

## 1.3

Release.

- `modules/ship.md`: authorized-scope release with base sync, fresh evidence, bounded change set, docs and changelog, commit and pull request, rollout with post-deploy verification and rollback.
- `RELEASE` route (`qa? → ship → DONE`); `ship?` after `qa` on every implementing route; `qa` and `ship` Next agree with the graph.
- `HUMAN-ACTION` gap label: steps only the user can perform, delivered once as an instruction block; `PLAN.md` Human Actions table, task header field, `implementation` blocks only the dependent steps.
- `PROJECT.md` Environments table, mandatory with `deployed`.
- Rendered-surface QA under `ui` when a browser exists; without one, criteria stay `OPEN`.
- Trait table promises now name their consumers: `persistence` and `deployed` reach `PLAN.md`, `planning` and `ship`; NFR rows carry the trait they are tied to.
- Activation prompt invariant 9 names the three traits with a review axis instead of "one per trait".

## 1.2

- `tools/asef_lint.py`: consistency linter for the invariants the documents promise each other — module contract, router graph vs module `Next`, trait consumers, mandatory template rows, artifact/template pairing, version alignment, cross-references, single-home rule.
- `tools/test_asef_lint.py`: 15 mutation tests proving the linter catches each class of breakage.
- CI runs both on every push.
- `modules/review.md` Next declares the `REVIEW_ONLY` exit at `DONE`; graph and Next agree.
- `templates/DECISIONS.template.md` added: `ARTIFACTS.md` promised a compact log format and shipped only the full record.
- `prompt universale ASEF.txt` declares the kernel version it activates and defers to the kernel on mismatch.
- `README.md` documents purpose, usage, structure and the verification commands.

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
