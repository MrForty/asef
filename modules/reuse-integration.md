# Reuse Integration

**MODE:** HYBRID

## Trigger

Work may reuse or integrate code, patterns or components from another repository or system.

## Purpose

Reuse proven capability without importing accidental architecture, hidden risk or unnecessary surface area.

## Requires

- target outcome and target-system constraints;
- accessible source component or pattern;
- applicable license and provenance information.

## Optional

Tests, dependency graph, version history, security evidence and integration tooling.

## Do not load

Entire external repositories when a bounded component suffices, unrelated history or copied documentation without code relevance.

## Procedure

1. Search the target codebase for an existing solution first.
2. Define the exact capability and boundary to reuse.
3. Inspect external code, callers, dependencies, state assumptions, tests, license and trust boundaries.
4. Choose in order: direct reuse, thin adaptation, extraction, or reimplementation only when reuse costs more.
5. Import the smallest coherent unit and preserve target conventions.
6. Add integration checks at the target system's observable seam.
7. Record provenance and material divergence; avoid maintaining a speculative sync system.

## Exit criteria

- reused unit has a clear boundary and justified advantage;
- licensing, dependencies and security are acceptable;
- integration behavior and failure modes are verified;
- no unnecessary external architecture was copied.

## Outputs

Reuse decision/map when durable, specification or plan updates, integration task and `STATE.md`.

## Next

`implementation`, or `specification`/`planning` if integration changes behavior or architecture.
