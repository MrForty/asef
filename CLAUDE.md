# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

ASEF (v1) is a **prompt framework, not software**. Every file under the framework root is Markdown; there is no application source, no dependencies, no build.

Two exceptions. [tools/](tools/) is *about* the framework, not part of it: a linter that checks the invariants these documents promise each other, its mutation tests, and the tests of the skill scripts. It is never loaded into an agent's context. [skills/asef/](skills/asef/) is the third activation method: an Agent Skills file, `skills/asef/SKILL.md` (loaded into context when `/asef` is invoked) plus two scripts that are executed, never loaded. Run all three before committing any change to a framework document:

```bash
python3 tools/asef_lint.py -v      # invariants hold
python3 tools/test_asef_lint.py    # the linter still catches breakage
python3 tools/test_asef_skill.py   # the skill scripts keep their promise
python3 tools/release_notes.py --self-test   # a release still follows the documents
```

They need only Python 3.11 and the standard library, and run in CI on every push. A green linter is necessary, not sufficient: it cannot judge whether a rule is *right*, only whether the documents still agree. Re-read the affected documents for internal consistency against the contracts described below.

The folder is designed to be dropped into a target project as `asef/` and activated with the invocation text in `prompt universale ASEF.txt` (written in Italian; the framework documents themselves are in English — keep that split). That file ends with a fill-in request block the user completes before pasting; its reading rules (an empty field is a gap, filled first-party fields already satisfy the demand exemption, constraints and non-goals are binding) are part of the contract, not decoration.

## Architecture

Five kernel documents at the root; start with ASEF.md and load the others as its runtime requires:

| File | Owns |
|---|---|
| [ASEF.md](ASEF.md) | Kernel: config block, defaults (`AUTO` + `ECONOMY`), 10-step runtime, core principles, gap policy (`KNOWN`/`INFERABLE`/`RESEARCHABLE`/`HUMAN-ACTION`/`USER-DECISION`), project traits, risk classes, module contract, version control, build loop, Definition of Done |
| [ROUTER.md](ROUTER.md) | Intent → route classification (`GREENFIELD`, `MODIFY`, `DIAGNOSE`, `IMPROVE`, `REUSE`, `REVIEW_ONLY`, `QA_ONLY`, `RELEASE`) and the route graphs |
| [DECISION-ENGINE.md](DECISION-ENGINE.md) | Uncertainty ladder `known → inferable → answerable from code → researchable → safe default → ask`, evidence labels, reversibility classes with their alternatives rule, the single batched question round, the human-action block |
| [CONTEXT-MANAGER.md](CONTEXT-MANAGER.md) | Memory levels, progressive load order, do-not-load list, handoff packet, parallel contexts and the single `STATE.md` writer, exit compression |
| [ARTIFACTS.md](ARTIFACTS.md) | Which artifacts exist, authority order, update policy, evidence freshness, quality gate |

[modules/](modules/) holds the 13 modules: 12 workflow nodes referenced by the router graphs, plus [research.md](modules/research.md), a subroutine any module invokes in place (never a route node). [templates/](templates/) holds the skeletons for the artifacts a target project generates (`PROJECT`, `SPEC`, `PLAN`, `STATE`, `TASK`, `DECISIONS` log, `DECISION` record, `RESEARCH` ledger, `LEARNINGS`) plus `AGENTS.template.md`, the activation block a target project pastes into its own `AGENTS.md` so sessions resume without the prompt. `RESEARCH` and `LEARNINGS` are read at route start, so they carry a row cap and an Archive section that `CONTEXT-MANAGER.md` never loads.

### Module contract

Every file in [modules/](modules/) must declare, in this order: `MODE` (`NATIVE` or `HYBRID`), `Trigger`, `Purpose`, `Requires`, `Optional`, `Do not load`, `Procedure`, `Exit criteria`, `Outputs`, `Next`. Adding or editing a module without all ten sections breaks the contract stated in `ASEF.md`.

`NATIVE` (discovery, product-scope, specification, planning, slicing) means the written procedure is sufficient. `HYBRID` (implementation, diagnose, review, qa, ship, reuse-integration, architecture-improvement, research) means a specialist tool may be invoked on demand — but its instructions are never loaded speculatively.

### The graph is the invariant

Module `Next` fields and the route graphs in `ROUTER.md` must agree. Current wiring:

```
discovery → product-scope → specification → planning → slicing → implementation → review ⇄ fix → qa → ship? → DONE
diagnose → implementation (when authorized)
architecture-improvement → planning | implementation | slicing
reuse-integration → implementation | specification | planning
review → qa, or the precise failed upstream gate
qa → DONE | ship when release is requested or authorized | diagnose on failure
ship → DONE | diagnose when post-release verification fails
RELEASE: qa? → ship → DONE

research: invoked in place by any module with a researchable gap; returns to caller
```

`ship?` is optional by authorization, not by evidence: it runs only when the user requested or pre-authorized a release step (the request block carries `Autorizzazioni di rilascio`). Push, merge, deploy and publication happen nowhere else.

Gap resolution is the one flow that is not a graph edge: a module builds the gap ledger, sends `RESEARCHABLE` entries to `research` at the depth their reversibility class requires, with capability fallbacks from `CONTEXT-MANAGER.md`, batches `HUMAN-ACTION` entries into one instruction block, and only gaps passing that module's promotion test reach the user — batched into one question round. Raw research never enters the calling context; only the answer packet does, and its row lands in `RESEARCH.md` so later routes deduplicate; the earliest due revisit trigger is mirrored in `STATE.md`, the only file the runtime reads for it. Changing the promotion test in `DECISION-ENGINE.md`, or the depth table or termination rule in [modules/research.md](modules/research.md), changes how often the framework interrupts the user, so treat all three as load-bearing. The linter fails when a module restates the promotion test.

Changing a `Next` in a module means updating `ROUTER.md`, and vice versa — `tools/asef_lint.py` fails the build when they disagree, including the optional-node runs marked `?`. Backtracking is targeted: return only to the gate that failed, never restart the route.

### Traits and risk classes are the conditional axes

`PROJECT.md` declares traits (`ui`, `public-surface`, `typed`, `persistence`, `deployed`); the table in `ASEF.md` maps each to the rigor it switches on — a review axis in [review.md](modules/review.md), a QA floor in [qa.md](modules/qa.md), a mandatory NFR row or section in `SPEC.template.md`, environments in `PROJECT.template.md`, rollout in `PLAN.template.md`, deploy verification in [ship.md](modules/ship.md). This is how the framework covers UI, API and typed-language rigor without a module per discipline. Adding a trait means adding its consequence everywhere the table promises one; the linter resolves every backticked file or module in the "Switches on" cell and fails when that file does not carry the trait.

Traits are per project; **risk classes** (`auth`, `payments`, `tenant`, `pii`, `migration`, `concurrency`) are per task. Each task file declares the classes its change touches; `planning` owes a trust-boundary row, `review` owes the threat pass in its table, `qa` raises its floor to `Deep`. A class with no threat pass in `modules/review.md` fails the linter. Keep the class list short: it is the SaaS-specific rigor the framework offers, and every class costs a table row in three files.

Note the deliberate asymmetry it balances: every gate here can only remove scope. Step 5 of [product-scope.md](modules/product-scope.md) is the single gate allowed to add it, and it fires once. Do not add a second one.

## Conditional guides

`guides/web-experience.md` owns the UI design/originality and public-page delivery checks; `guides/existing-projects.md` owns baseline and preservation checks. They are loaded by scope from ASEF Runtime, not new modules or routes. Record results in existing SPEC/task artifacts. No new trait or mandatory specialist tool is needed. Keep guides within 1,200 estimated tokens and retain their load sites; the linter checks both. `examples/scenarios.md` is evaluation material, never runtime context.

## Editing conventions

- **Compression is the point.** These documents are loaded into a context budget. Prefer tables and terse imperatives over prose; do not add examples, rationale essays, or restated principles. The linter enforces ceilings (kernel total, per module, per guide, activation prompt; estimated as characters ÷ 4) — a change that trips one is a signal to cut, not to raise the ceiling.
- **One fact, one home.** Each rule lives in exactly one kernel file; other files reference it by name (e.g. modules say "apply `DECISION-ENGINE.md`", they do not re-explain the ladder). Duplicating a rule across files is the main failure mode here.
- **Terminology is fixed.** `FACT` / `INFERENCE` / `ASSUMPTION` / `DECISION` / `OPEN`; gap labels `KNOWN` / `INFERABLE` / `RESEARCHABLE` / `HUMAN-ACTION` / `USER-DECISION`; reversibility classes `Trivial` / `Reversible` / `Expensive to reverse` / `One-way/high risk`, never shortened; route names in caps; artifact filenames exactly as in `ARTIFACTS.md`. Introducing a synonym silently forks the framework. The linter checks that the activation prompt names every route, trait and label the kernel defines, and that the README badge and request block match the kernel and the prompt.
- **Templates carry HTML comments as instructions**, not placeholder content. Keep them; they are what a fresh agent reads when filling the artifact.
- **Template rows and sections are mandatory.** The NFR table in `SPEC.template.md`, the command and environment tables in `PROJECT.template.md`, and the sections the linter lists per template (UI, Human Actions, Alternatives Considered, Domain Terms, …) are filled or marked `N/A`; deleting one to dodge the question is the failure this framework exists to prevent.
- **Bumping the kernel means bumping three files.** `asef.version` in `ASEF.md`, the `kernel vX.Y` line in `prompt universale ASEF.txt`, and a new top entry in `CHANGELOG.md`. The linter fails on any mismatch; the activation prompt defers to the kernel when it finds one.
- **A release restates nothing.** `.github/workflows/release.yml` publishes it, on a pushed `v*` tag or on manual dispatch, and `tools/release_notes.py` derives tag, title and notes from `ASEF.md` and `CHANGELOG.md`. It refuses to release a version the kernel does not declare or the changelog does not describe, so releasing is a consequence of the version bump, never a second place to describe the work. Never hand-write release notes: fix the changelog entry and republish.
- **`prompt universale ASEF.txt` loads the kernel, it does not mirror it.** It carries only what cannot be discovered before `ASEF.md` is read: bootstrap order, contract pointers, a capability declaration, the label-language rule, and the user request template (including the release authorizations `ship` honours). The first-output block is owned by `ROUTER.md` Output so both activation methods emit it; the prompt only points to it. Rules owned by a kernel file are referenced there, never restated — re-summarising the gap policy or the fan-out mechanics in this file is the duplication the framework forbids. Update it when defaults, the runtime order, the traits, the risk classes or the review axes change in `ASEF.md`. `templates/AGENTS.template.md` is the same idea at minimum size: a pointer to the kernel, never a second copy of its rules.
- **The skill activates, it does not restate.** `skills/asef/SKILL.md` locates the framework, maps the user's words onto the request block through `skills/asef/scripts/asef_prompt.py` (which reads `prompt universale ASEF.txt` at runtime and fills only that block), and executes the result from Bootstrap step 1. Route, stack and questions stay with the kernel; the skill never pre-classifies a project, invents context for an empty field, or grants a release authorization the user did not state. The linter requires its name to be `asef`, its pointers to the kernel files and the builder, a 1,500-token ceiling, and no single-home rule inside it. Changing the request block's fields means checking the builder's field mapping and `tools/test_asef_skill.py`.
- **The capability fallbacks in `CONTEXT-MANAGER.md` are the shared portability contract.** A missing capability (no subagents, no web, no file writes, no execution, no browser, no git) changes the path, never the gates. Keep the activation prompt pointing to those fallbacks; neither activation method may silently require a capability.
