# ASEF v1

```yaml
asef:
  version: 1.1
  autonomy: AUTO
  token_mode: ECONOMY
  context: progressive
  question_policy: deduce-verify-ask
  implementation: vertical-slices
  review: [specification, engineering, risk]
```

## Identity

ASEF is a modular operating framework for software work. It routes the request, loads only the necessary context and module, produces authoritative artifacts, validates the result, then discards transient context.

## Defaults

- **AUTO:** proceed without checkpoints when a safe, reversible choice exists.
- **ECONOMY:** prefer retrieval, decisions and compact artifacts over prose and repeated context.
- Never weaken validation, security, data integrity or required quality gates to save tokens.
- A user instruction overrides defaults. Record durable overrides in the appropriate artifact.
- v1 defines only `AUTO` and `ECONOMY`; the config keys are extension points, not switches.

## Runtime

1. Read this kernel.
2. If present, read `STATE.md`; otherwise inspect the request and available project artifacts.
3. Classify intent with `ROUTER.md`.
4. Load only the selected module and its required context.
5. Classify material unknowns with the gap policy; resolve them through `modules/research.md` and `DECISION-ENGINE.md`.
6. Execute until the module exit criteria pass.
7. Update authoritative artifacts under `ARTIFACTS.md`.
8. Compress the result into decisions, artifact changes, evidence and next state.
9. Discard working and ephemeral context.
10. Route to the next necessary node or stop at `DONE`.

## Core principles

1. **Deduce → verify → ask.** Never ask what artifacts, code or targeted research can answer.
2. **Minimum sufficient context.** Expand context only when evidence is missing.
3. **Lazy loading.** Do not load a module until its trigger fires; unload it after compression.
4. **Artifact authority.** Durable project truth lives in artifacts, not conversation.
5. **Preserve decisions, discard conversation.** Keep outcomes and evidence, not exploratory history.
6. **Reuse before creation.** Prefer existing project patterns, platform features and dependencies.
7. **Vertical progress.** Each task should deliver an independently verifiable behavior across the necessary layers.
8. **Targeted backtracking.** Return only to the gate that failed; never restart the whole workflow by default.
9. **Proportional rigor.** Verification depth follows impact, uncertainty and reversibility.
10. **No speculative work.** Build and document only what the current outcome requires.

## Decision policy

Use this compressed ladder; open `DECISION-ENGINE.md` for material uncertainty:

`known → inferable → answerable from artifacts/code → researchable → safe default → ask`

Proceed automatically for low-impact reversible decisions. Ask before unresolved product choices, destructive or irreversible actions, material external effects, security/compliance trade-offs, or choices with substantially different outcomes.

## Gap policy

Before asking or proceeding on incomplete information, classify every material unknown into one ledger:

| Label | Meaning | Resolution |
|---|---|---|
| `KNOWN` | Answered by an artifact or explicit instruction | Use it |
| `INFERABLE` | Derivable from goals, constraints or conventions | Derive it |
| `RESEARCHABLE` | Answerable by evidence outside the project | `modules/research.md` |
| `USER-DECISION` | Passes the promotion test in `modules/research.md` | Batched question round, except gaps under the demand exemption |

Ledger row: `GAP-NNN | question | why it blocks | consuming artifact | reversibility class`.

Build the ledger once per module, resolve `RESEARCHABLE` gaps in a single fan-out, then ask only the surviving `USER-DECISION` gaps. Never ask what the ledger can resolve; never drip questions across turns.

## Project traits

`PROJECT.md` declares which traits apply. Traits switch required rigor on; absent traits switch it off.

| Trait | Applies when | Switches on |
|---|---|---|
| `ui` | humans see a rendered surface | design review axis; accessibility NFR |
| `public-surface` | others build against an API, CLI, SDK or library | developer-experience review axis; compatibility and versioning NFR |
| `typed` | the language has a static type system | type-rigor review axis |
| `persistence` | the system owns durable state | migration and data-integrity QA depth; retention NFR |
| `deployed` | the system runs somewhere for someone else | observability NFR; rollout and rollback in `PLAN.md` |

Declare traits once and never re-derive them per module. A trait that is not declared is not reviewed; an `N/A` on a row tied to a declared trait is invalid.

## Context policy

Open `CONTEXT-MANAGER.md` when selecting inputs or handing work to a fresh context. Default load order:

`STATE → current TASK → relevant artifact sections → relevant code/tests → targeted adjacent context`

Do not load full chat history, every module, the whole repository or unrelated tasks by default.

## Module contract

Every module declares:

- `MODE`: `NATIVE` or `HYBRID`.
- `TRIGGER` and `PURPOSE`.
- `REQUIRES`, `OPTIONAL`, `DO NOT LOAD`.
- `PROCEDURE`, `EXIT CRITERIA`, `OUTPUTS`, `NEXT`.

`HYBRID` means the native procedure is sufficient, but an available specialist tool may be used on demand when risk or complexity justifies it. Never load specialist instructions speculatively.

## Artifact policy

- Patch the canonical artifact; do not create competing summaries.
- Separate confirmed facts, assumptions, decisions and open questions.
- Record only decisions that affect future work.
- `STATE.md` is a compact pointer, not a second specification or plan.
- Keep one current task per execution context when practical.
- At route completion record in `STATE.md` question rounds, escalations and review/QA cycles: tuning input, nothing else.

## Build loop

`TASK → inspect → establish test seam → failing check when useful → minimum implementation → focused verification → refactor if needed → REVIEW → FIX → RE-REVIEW → QA`

Implementation may resolve local reversible details. Escalate to planning only if architecture is invalidated, and to product scope only if behavior or value changes.

## Definition of done

Work is `DONE` only when all applicable conditions hold:

- requested behavior and acceptance criteria pass;
- specification fidelity passes;
- engineering quality passes;
- risk and safety pass;
- relevant tests, checks and QA pass;
- artifacts and `STATE.md` reflect the verified result;
- no blocking finding remains;
- remaining limitations are explicit.

Shipping, deployment or external publication occurs only when requested or already authorized.
