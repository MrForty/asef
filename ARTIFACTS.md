# Artifact System

## Rule

**Conversation is temporary. Artifacts are project memory.** The canonical artifact wins over recollection or summaries. When reality changes, patch the canonical artifact and state together.

## Core artifacts

| Artifact | Authority | Create when |
|---|---|---|
| `PROJECT.md` | Goal, users, success, constraints, baseline, non-goals | Project identity matters beyond one task |
| `SPEC.md` | Required behavior, scope, test seams, acceptance criteria | Behavior is non-trivial or shared |
| `PLAN.md` | Architecture, data flow, rollout and verification strategy | Execution needs coordination or durable technical choices |
| `STATE.md` | Current verified state, active task, next gate and blockers | Always for multi-step work |
| `tasks/TASK-NNN.md` | One executable vertical slice | Work needs decomposition |
| `DECISIONS.md` or decision records | Durable cross-cutting decisions | Reversal is costly or future agents need the rationale |

Optional artifacts such as `ARCHITECTURE.md`, `RESEARCH.md`, ADRs or a reuse map exist only when their content cannot stay clear in the core artifacts.

Use one `DECISIONS.md` log for compact entries, seeded from `DECISIONS.template.md`; open a `DECISION.template.md` record when a decision needs full context, alternatives and rationale.

## Authority order

1. Explicit current user instruction.
2. Verified external constraints and runtime reality.
3. Canonical project artifacts.
4. Current code and tests, interpreted as evidence of present behavior.
5. `STATE.md` pointers and summaries.
6. Conversation or agent memory.

If sources conflict, do not silently merge them. Resolve under `DECISION-ENGINE.md`, then patch the authoritative source.

## Update policy

- Patch, do not recreate or fork a canonical document.
- Keep each fact in one authoritative place; link elsewhere.
- Mark `FACT`, `INFERENCE`, `ASSUMPTION`, `DECISION` and `OPEN` when ambiguity matters.
- Record source and date inline with any fact obtained through `modules/research.md`.
- Remove or supersede stale statements when confirmed; do not accumulate contradictory history.
- Store outcomes and rationale, not long deliberation.
- Record evidence sufficient for a fresh agent to verify the claim.

## Lifecycle

```text
request/evidence → artifact update → module execution → verification
→ state update → compression → fresh context can resume
```

## Quality gate

An artifact is ready when it is current, internally consistent, compact, executable by a fresh agent, and contains no unresolved ambiguity that would materially change the next action.
