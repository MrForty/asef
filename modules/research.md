# Research

**MODE:** HYBRID

## Trigger

The gap ledger contains at least one `RESEARCHABLE` entry, or a module cannot
proceed without external evidence.

## Purpose

Resolve open gaps in disposable subagent context and return compact sourced
answers. Keep raw research out of the calling context.

## Requires

- gap ledger entries labelled `RESEARCHABLE`;
- calling module and the artifact that will own each answer;
- relevant `PROJECT.md` constraints.

## Optional

Existing decisions, previously resolved gaps, current code evidence,
specialist research tooling.

## Do not load

Raw search output, full external documentation, vendor marketing, unrelated
gaps, conversation history, any subagent transcript.

## Gap contract

Each entry carries `GAP-NNN | question | why it blocks | consuming artifact |
reversibility class`. A gap no artifact consumes is not researched.

A gap whose only source is the user's own experience is not `RESEARCHABLE`. Return it
untouched under the demand exemption in `DECISION-ENGINE.md`; never substitute market
evidence for first-party evidence.

## Procedure

1. Deduplicate against resolved gaps; reuse the recorded answer and its revisit trigger.
2. Cluster related gaps so one subagent covers one coherent question set.
3. Dispatch **one parallel fan-out**. Never research serially across separate calls.
4. Each subagent returns only the answer packet below; discard its context on return.
5. Adjudicate conflicts, apply the promotion test, label every answer.
6. Patch the consuming artifact; record the source inline with the fact.
7. Return the resolved ledger to the calling module.

## Answer packet

One row per gap, no prose.

| Field | Rule |
|---|---|
| Answer | The decision or fact, stated for use |
| Label | `FACT`, `INFERENCE` or `ASSUMPTION` |
| Source | Origin and date; required for `FACT` |
| Confidence basis | What would change the answer |
| Revisit trigger | Evidence that reopens it |

## Termination

Research always returns an answer. With no source found, adopt the
conventional, reversible, lowest-cost option, label it `ASSUMPTION` and set a
revisit trigger. `OPEN` is permitted only for a promoted `USER-DECISION`.

## Evidence rules

- `FACT` requires a citable source; without one the highest grade is `ASSUMPTION`.
- Absence of evidence is reported as absence, never filled by invention.
- Prefer primary sources: official documentation, specifications, source code,
  licence text. Treat secondary sources as `INFERENCE`.
- Record version or date for anything that decays: pricing, limits, APIs,
  library recommendations, security advisories.

## Promotion test

Promote a gap to `USER-DECISION` only when both hold:

1. credible sources diverge materially, or no safe default exists; and
2. the choice is `Expensive to reverse` or `One-way/high risk` under
   `DECISION-ENGINE.md`.

Otherwise decide, label and proceed. Taste, cost preference, convention and
reversible technical choices are never promoted.

## Budget

Declare per invocation: maximum subagents, maximum depth per subagent, stop
point. ECONOMY defaults: three subagents, depth limited to the primary
sources needed to label each gap, stop at the first answer that passes the
evidence rules. On exhaustion return the best available answer under
`Termination`.
Never extend a fan-out to chase certainty a reversible decision does not need.

## Exit criteria

- every `RESEARCHABLE` gap has an answer, a label and a revisit trigger;
- every `FACT` carries a source;
- promoted `USER-DECISION` gaps pass the promotion test;
- answers are patched into their consuming artifacts;
- no raw research material entered the calling context.

## Outputs

Resolved gap ledger, patched artifacts, durable decisions when reversal is
costly, `STATE.md` update.

## Next

The calling module, with the resolved ledger. Remaining `USER-DECISION` gaps
go to a single batched question round.
