# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

ASEF (v1) is a **prompt framework, not software**. Every file under the framework root is Markdown; there is no application source, no dependencies, no build.

The one exception is [tools/](tools/), which is *about* the framework, not part of it: a linter that checks the invariants these documents promise each other, and its mutation tests. It is never loaded into an agent's context. Run both before committing any change to a framework document:

```bash
python3 tools/asef_lint.py -v      # invariants hold
python3 tools/test_asef_lint.py    # the linter still catches breakage
```

They need only Python 3.11 and the standard library, and run in CI on every push. A green linter is necessary, not sufficient: it cannot judge whether a rule is *right*, only whether the documents still agree. Re-read the affected documents for internal consistency against the contracts described below.

The folder is designed to be dropped into a target project as `asef/` and activated with the invocation text in `prompt universale ASEF.txt` (written in Italian; the framework documents themselves are in English — keep that split). That file ends with a fill-in request block the user completes before pasting; its reading rules (an empty field is a gap, filled first-party fields already satisfy the demand exemption, constraints and non-goals are binding) are part of the contract, not decoration.

## Architecture

Five kernel documents at the root, loaded in this order, each with a single non-overlapping responsibility:

| File | Owns |
|---|---|
| [ASEF.md](ASEF.md) | Kernel: config block, defaults (`AUTO` + `ECONOMY`), 10-step runtime, core principles, gap policy (`KNOWN`/`INFERABLE`/`RESEARCHABLE`/`USER-DECISION`), project traits, module contract, build loop, Definition of Done |
| [ROUTER.md](ROUTER.md) | Intent → route classification (`GREENFIELD`, `MODIFY`, `DIAGNOSE`, `IMPROVE`, `REUSE`, `REVIEW_ONLY`, `QA_ONLY`) and the route graphs |
| [DECISION-ENGINE.md](DECISION-ENGINE.md) | Uncertainty ladder `known → inferable → answerable from code → researchable → safe default → ask`, evidence labels, reversibility classes, the single batched question round |
| [CONTEXT-MANAGER.md](CONTEXT-MANAGER.md) | Memory levels, progressive load order, do-not-load list, handoff packet, exit compression |
| [ARTIFACTS.md](ARTIFACTS.md) | Which artifacts exist, authority order, update policy, quality gate |

[modules/](modules/) holds the 12 modules: 11 workflow nodes referenced by the router graphs, plus [research.md](modules/research.md), a subroutine any module invokes in place (never a route node). [templates/](templates/) holds the skeletons for the artifacts a target project generates (`PROJECT`, `SPEC`, `PLAN`, `STATE`, `TASK`, `DECISIONS` log, `DECISION` record).

### Module contract

Every file in [modules/](modules/) must declare, in this order: `MODE` (`NATIVE` or `HYBRID`), `Trigger`, `Purpose`, `Requires`, `Optional`, `Do not load`, `Procedure`, `Exit criteria`, `Outputs`, `Next`. Adding or editing a module without all ten sections breaks the contract stated in `ASEF.md`.

`NATIVE` (discovery, product-scope, specification, planning, slicing) means the written procedure is sufficient. `HYBRID` (implementation, diagnose, review, qa, reuse-integration, architecture-improvement, research) means a specialist tool may be invoked on demand — but its instructions are never loaded speculatively.

### The graph is the invariant

Module `Next` fields and the route graphs in `ROUTER.md` must agree. Current wiring:

```
discovery → product-scope → specification → planning → slicing → implementation → review ⇄ fix → qa → DONE
diagnose → implementation (when authorized)
architecture-improvement → implementation | slicing
reuse-integration → implementation | specification | planning
review → qa, or the precise failed upstream gate
qa → DONE | authorized shipping | diagnose on failure

research: invoked in place by discovery, product-scope, specification, planning; returns to caller
```

Gap resolution is the one flow that is not a graph edge: a module builds the gap ledger, sends `RESEARCHABLE` entries to `research` as a single parallel fan-out, and only gaps passing that module's promotion test reach the user — batched into one question round. Raw research never enters the calling context; only the answer packet does. Changing the promotion test or the termination rule in [modules/research.md](modules/research.md) changes how often the framework interrupts the user, so treat both as load-bearing.

Changing a `Next` in a module means updating `ROUTER.md`, and vice versa — `tools/asef_lint.py` fails the build when they disagree, including the optional-node runs marked `?`. Backtracking is targeted: return only to the gate that failed, never restart the route.

### Traits are the conditional axis

`PROJECT.md` declares traits (`ui`, `public-surface`, `typed`, `persistence`, `deployed`); the table in `ASEF.md` maps each to the rigor it switches on — a review axis in [review.md](modules/review.md), a QA floor in [qa.md](modules/qa.md), a mandatory NFR row in `SPEC.template.md`. This is how the framework covers UI, API and typed-language rigor without a module per discipline. Adding a trait means adding its consequence everywhere the table promises one; a trait with no consumer is dead weight.

Note the deliberate asymmetry it balances: every gate here can only remove scope. Step 5 of [product-scope.md](modules/product-scope.md) is the single gate allowed to add it, and it fires once. Do not add a second one.

## Editing conventions

- **Compression is the point.** These documents are loaded into a context budget. Prefer tables and terse imperatives over prose; do not add examples, rationale essays, or restated principles.
- **One fact, one home.** Each rule lives in exactly one kernel file; other files reference it by name (e.g. modules say "apply `DECISION-ENGINE.md`", they do not re-explain the ladder). Duplicating a rule across files is the main failure mode here.
- **Terminology is fixed.** `FACT` / `INFERENCE` / `ASSUMPTION` / `DECISION` / `OPEN`; route names in caps; artifact filenames exactly as in `ARTIFACTS.md`. Introducing a synonym silently forks the framework.
- **Templates carry HTML comments as instructions**, not placeholder content. Keep them; they are what a fresh agent reads when filling the artifact.
- **Template rows are mandatory.** The NFR table in `SPEC.template.md` and the command table in `PROJECT.template.md` are filled or marked `N/A`; deleting a row to dodge the question is the failure this framework exists to prevent.
- **Bumping the kernel means bumping three files.** `asef.version` in `ASEF.md`, the `kernel vX.Y` line in `prompt universale ASEF.txt`, and a new top entry in `CHANGELOG.md`. The linter fails on any mismatch; the activation prompt defers to the kernel when it finds one.
- **`prompt universale ASEF.txt` loads the kernel, it does not mirror it.** It carries only what cannot be discovered before `ASEF.md` is read: bootstrap order, the invariants, a capability-degradation table, the first-output block, the label-language rule, and the user request template. Rules owned by a kernel file are referenced there, never restated — re-summarising the gap policy or the fan-out mechanics in this file is the duplication the framework forbids. Update it when defaults, the runtime order, or the review axes change in `ASEF.md`.
- **The capability table is the portability contract.** A missing capability (no subagents, no web, no file writes, no execution) changes the path, never the gates. Adding a step that silently requires a capability means adding its degraded form to that table.

## Inherited instructions

A parent `CLAUDE.md` at `../CLAUDE.md` describes an unrelated WAT (Workflows/Agents/Tools) framework with `tools/`, `workflows/`, and `.tmp/` directories. That structure does not exist here and does not apply to ASEF work; ASEF's own runtime in `ASEF.md` governs this folder.
