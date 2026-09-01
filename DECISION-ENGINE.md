# Decision Engine

## Purpose

Resolve uncertainty with the least interruption consistent with safety and outcome quality.

## Default ladder

For each material unknown, stop at the first successful step:

1. **Known:** use an authoritative artifact or explicit instruction.
2. **Inferable:** derive from goals, constraints and established conventions.
3. **Answerable from code:** inspect current implementation, tests, schema, history or runtime evidence.
4. **Researchable:** resolve through `modules/research.md`; never conduct raw research inside the calling context.
5. **Safe default:** choose the conventional, reversible and lowest-cost option; record it as an assumption if material.
6. **Ask:** request only the decision that cannot safely be resolved above.

## Decision test

Assess:

- impact on product behavior or success;
- reversibility and cost to reverse;
- security, privacy, compliance and data integrity;
- external side effects or destructive action;
- uncertainty of evidence;
- difference between viable outcomes.

## AUTO policy

Proceed when the choice is reversible, contained, supported by evidence and does not materially alter the product. Prefer existing project conventions, then the simplest option that meets current requirements.

Ask when an unresolved choice is:

- destructive, irreversible or expensive to reverse;
- a material product, legal, security or business trade-off;
- an external action lacking authorization;
- impossible to infer without meaningfully changing the result.

## Question round

A question reaches the user only when both hold:

1. it survives rungs 1-5, including the promotion test in `modules/research.md`; and
2. different answers produce a different product, not a different implementation.

Taste, naming, library choice, reversible technical detail and cost preference never qualify.

Collect surviving questions and ask them once, in a single round, each with a recommended default and its consequence. Never drip questions across turns and never pad the round with speculative questions. If the user does not answer, apply the stated default, label it `ASSUMPTION` and continue.

**Demand exemption.** A gap whose only possible source is the user's own experience — real demand, the observed status quo, who specifically asked, what a user did rather than said — is never researched, never batched and never defaulted. Ask one at a time, push past the first answer, and leave it `OPEN` until answered. A default here would fabricate the very evidence the gap exists to obtain.

## Evidence labels

- `FACT`: directly supported.
- `INFERENCE`: derived from facts.
- `ASSUMPTION`: adopted to proceed; include validation or reversal point.
- `DECISION`: chosen direction and rationale.
- `OPEN`: genuinely unresolved and blocking or intentionally deferred.

## Reversibility classes

| Class | Behavior |
|---|---|
| Trivial | Decide and proceed; no durable record needed. |
| Reversible | Decide; record only if it affects later work. |
| Expensive to reverse | Verify evidence and record a decision; ask if outcomes differ materially. |
| One-way/high risk | Require explicit authority and safeguards. |

## Output

Update the relevant artifact. Use `DECISIONS.md` or `DECISION.template.md` only for cross-cutting, costly or durable decisions. Never store internal deliberation.
