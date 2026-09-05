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
- relevant `PROJECT.md` constraints;
- `RESEARCH.md`, if present.

## Optional

Existing decisions, current code evidence, specialist research tooling.

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

1. Deduplicate against `RESEARCH.md`; reuse the recorded answer unless its revisit trigger has fired.
2. Cluster related gaps so one subagent covers one coherent question set.
3. Dispatch one fan-out at the required depth; apply capability fallbacks in `CONTEXT-MANAGER.md` when delegation is unavailable or disallowed.
4. Each subagent returns only the answer packet below; discard its context on return.
5. Adjudicate conflicts, apply the promotion test, label every answer.
6. Patch the consuming artifact with the source inline; append the row to `RESEARCH.md`.
7. Return the resolved ledger to the calling module.

## Depth

| Reversibility class | Depth |
|---|---|
| Trivial, Reversible | first primary source that passes the evidence rules; stop |
| Expensive to reverse | two independent primary sources; version or date; one explicit search for counter-evidence; a comparison of the viable options against the criteria used |
| One-way/high risk | as above, plus failure mode and exit cost per option; promote if sources still diverge |

Stack, dependency and hosting choices for a new baseline are `Expensive to reverse` at least. Compare on: fit to constraints and declared traits; maturity and maintenance signals; licence; hosting fit and cost; open security advisories; familiarity stated in `PROJECT.md`.

## Answer packet

One row per gap, no prose.

| Field | Rule |
|---|---|
| Answer | The decision or fact, stated for use |
| Label | `FACT`, `INFERENCE` or `ASSUMPTION` |
| Source | Origin and date; required for `FACT` |
| Confidence basis | What would change the answer |
| Revisit trigger | Concrete and checkable: a version, a date, a metric or an event |

## Termination

With no source, use a safe reversible option as `ASSUMPTION` with a revisit trigger. If none exists, return `OPEN` and block the dependent decision under `DECISION-ENGINE.md`; missing evidence never makes a high-risk choice safe.

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

Declare per invocation: maximum subagents, depth per gap, stop point. ECONOMY
defaults: three subagents, depth from the table above, stop as soon as the
class is satisfied. On exhaustion return the best available answer under
`Termination`. Never extend a fan-out to chase certainty a reversible decision
does not need.

## Exit criteria

- every gap has a labelled answer and revisit trigger, or an explicit `OPEN` blocker;
- every `FACT` carries a source;
- promoted `USER-DECISION` gaps pass the promotion test;
- answers are patched into their consuming artifacts and `RESEARCH.md`;
- no raw research material entered the calling context.

## Outputs

Resolved gap ledger, patched artifacts, `RESEARCH.md` rows, durable decisions when reversal is
costly, `STATE.md` update.

## Next

The calling module, with the resolved ledger. Remaining `USER-DECISION` gaps
go to a single batched question round.
