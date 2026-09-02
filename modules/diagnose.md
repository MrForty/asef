# Diagnose

**MODE:** HYBRID

## Trigger

Bug, regression, failing check or unknown operational failure.

## Purpose

Find and prove the root cause before changing behavior.

## Requires

- observable symptom and expected behavior;
- relevant code, tests, logs or reproduction surface.

## Optional

Recent changes, runtime configuration, `LEARNINGS.md`, specialist diagnostic tooling and production evidence within authorization.

## Do not load

Whole repository, unrelated logs or speculative redesigns.

## Procedure

1. Build a reproduction first: a check that fails on the symptom, deterministically, fast enough to rerun and runnable without the user. No reproduction, no fix: request the missing evidence, logs or access instead.
2. Check `LEARNINGS.md` for a known pitfall in the same files.
3. Trace the real path through callers, shared functions, state and boundaries; edit nothing outside it until the cause is proven.
4. Form the smallest falsifiable hypothesis; test it against evidence, one variable at a time.
5. Distinguish root cause from downstream symptoms and correlated noise.
6. Define the smallest shared fix point and regression boundary; the reproduction becomes the regression check.

Three rejected hypotheses are evidence of a wrong model of the system, not of a hard bug: stop and escalate to `planning` or the user with the evidence gathered.

Do not implement unless the request includes a fix. If fixing, route to `implementation` with the proven cause and regression check.

## Exit criteria

- failure is reproduced by a rerunnable check or bounded by strong evidence;
- root cause and affected paths are identified;
- competing hypotheses are rejected sufficiently;
- fix seam and verification are clear.

## Outputs

Root-cause statement, evidence, affected scope, regression check and `STATE.md` update.

## Next

`implementation` when authorized; otherwise `DONE` with diagnosis.
