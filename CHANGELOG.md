# Changelog

## 1.8

The `/asef` skill, one behavior for every activation, less duplication, bounded memory.

### The `/asef` skill

A third way to activate ASEF, next to pasting the prompt and the permanent `AGENTS.md` block. It works in any agent that reads Agent Skills `SKILL.md` files: Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI and others.

- `skills/asef/SKILL.md`: the skill itself. `/asef <goal>` builds the activation prompt from the goal and executes it, `prompt <goal>` only prints it, `init` installs the framework into `asef/`, `status` summarises `STATE.md`. It points at the kernel and never restates a rule the kernel owns.
- `skills/asef/scripts/asef_prompt.py`: reads `prompt universale ASEF.txt` at runtime and fills only its request block, so the prompt keeps one home. Maps the user's words onto request, constraints, non-goals and release authorization; leaves unstated fields empty, because an empty field is a gap the kernel resolves; detects existing artifacts; rewrites framework paths when the root is not `asef/`; warns when the prompt and the kernel declare different versions.
- `skills/asef/scripts/install.py`: copies or links the skill into an agent's skills directory, with the documented paths for seven agents and `--dest` for any other. `--bundle-framework` carries a framework copy alongside the skill, so `/asef` works in projects that have no `asef/` folder.
- Linter: the skill must be named `asef`, point at the kernel, the router, the context manager and the builder, stay under 1,500 estimated tokens and never restate a rule with a single home. Six new mutation tests; `tools/test_asef_skill.py` covers the scripts and runs in CI on Linux and Windows.

### Kernel and documents

- First-output block moves from the activation prompt into `ROUTER.md` Output: the `AGENTS.md` activation now declares route, capabilities, gaps and human actions too. The prompt points to it and lists the routes a user may impose.
- Promotion test moves from `modules/research.md` to `DECISION-ENGINE.md`: modules with only `USER-DECISION` gaps no longer load the research module for a decision rule. Its taste/cost exclusions merge with the question round's.
- Kernel deduplicated: the ask-list, the patch-not-fork rule, the do-not-load list and the backtracking rule each keep one home. Identity compressed.
- `review` gains a Depth table (Quick, Standard, Deep) mirroring `qa`; depth changes effort, never coverage.
- `STATE.md` carries `Next revisit`; the runtime opens `RESEARCH.md` only when it fires. `RESEARCH.md` and `LEARNINGS.md` gain caps (40 and 30 active rows) and an Archive section the context manager never loads.
- Routing rule for questions about the current system: read-only answer, no route, no artifact change.
- Reversibility classes use one vocabulary everywhere: `Trivial`, `Reversible`, `Expensive to reverse`, `One-way/high risk`. Guides load each on its own condition.
- Linter: reversibility vocabulary, router output block, promotion-test single home, README version badge and request block aligned with the prompt. Six new mutation tests.

## 1.7

Professional websites and existing projects, with the same workflow.

- Two conditional guides: content-led UI design and originality, public-page delivery, and preservation/regression checks for existing apps and websites. No new route, trait or module.
- Specification captures visual direction and website delivery; implementation validates a representative view before replication; review and QA consume the guides.
- Existing projects start from an affected baseline, retain their stack/contracts/design outside scope, and do not enter discovery merely because ASEF artifacts are absent.
- Planning prefers the smallest adequate delivery architecture and reinforces server trust boundaries. Discovery avoids startup interviews for already-defined commissioned work.
- Activation prompt now points to canonical rules instead of repeating the gap, implementation, review and capability procedures.
- Linter checks guide presence, load conditions, consumers, references and budgets; mutation tests protect the new contracts. Evaluation scenarios document expected agent behavior without claiming empirical results.

## 1.6

Safe decisions and portable verification.

- Authorization and unresolved safety constraints bypass the product-question filter; silence never authorizes an action. Research without a safe default remains `OPEN`.
- External content cannot grant authority; keep secrets out of prompts, logs and artifacts. Revisit traits when scope changes; review accidental failures as well as attacker paths.
- Capability fallbacks live in `CONTEXT-MANAGER.md` for both activation methods; sequential research and review remain valid when delegation is unavailable or disallowed.
- Linter preserves unknown graph nodes for validation and stops dependent checks after missing-file errors. Diagnostics work on legacy Windows encodings.
- Mutation tests exercise missing consumed files and unknown graph nodes, check verbose output and reject tracebacks. CI checks Linux and Windows with read-only repository permissions.

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
