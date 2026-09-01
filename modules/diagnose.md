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

Recent changes, runtime configuration, specialist diagnostic tooling and production evidence within authorization.

## Do not load

Whole repository, unrelated logs or speculative redesigns.

## Procedure

1. Reproduce or establish reliable evidence of the failure.
2. Trace the real path through callers, shared functions, state and boundaries.
3. Form the smallest falsifiable hypothesis; test it against evidence.
4. Distinguish root cause from downstream symptoms and correlated noise.
5. Add or identify a check that fails for the cause.
6. Define the smallest shared fix point and regression boundary.

Do not implement unless the request includes a fix. If fixing, route to `implementation` with the proven cause and regression check.

## Exit criteria

- failure is reproduced or bounded by strong evidence;
- root cause and affected paths are identified;
- competing hypotheses are rejected sufficiently;
- fix seam and verification are clear.

## Outputs

Root-cause statement, evidence, affected scope, regression check and `STATE.md` update.

## Next

`implementation` when authorized; otherwise `DONE` with diagnosis.
