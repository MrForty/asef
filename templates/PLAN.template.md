# Plan: <Outcome>

## Approach

<!-- Minimum technical approach and existing patterns reused. For each Expensive
     or One-way choice, the alternatives rejected, including no change. -->

## Affected Components

| Component | Change | Reason |
|---|---|---|
|  |  |  |

## Data and Control Flow

## Interfaces and Persistence

<!-- Include only if applicable. -->

## Trust Boundaries and Failure Handling

<!-- One row per risk class the change touches (`ASEF.md`); `none` when no
     class applies. -->

| Risk class | Boundary | Failure handling | Idempotency |
|---|---|---|---|
|  |  |  |  |

## Verification Strategy

<!-- Focused checks, integration checks and applicable QA depth. -->

## Rollout and Rollback

<!-- Mandatory with `deployed`: environments, rollout order, verification,
     rollback. Mandatory with `persistence`: migration order, backfill,
     reversibility. -->

## Human Actions

<!-- Steps only the user can perform (`HUMAN-ACTION`): accounts, credentials,
     DNS, payment setup, third-party consoles. Delivered once as a block.
     Write None when empty. -->

| # | Action | Where | Value to capture | Destination | Status |
|---|---|---|---|---|---|
|  |  |  |  |  | `PENDING \| DONE` |

## Risks and Mitigations

## Decisions and Assumptions

## Readiness

- [ ] Every planned change maps to scope, acceptance criteria or a risk control.
- [ ] Every declared trait has its planned consequence.
- [ ] Every risk class touched has boundary, failure and idempotency handling.
- [ ] Human actions are listed with destination, or None.
- [ ] Existing patterns and reuse opportunities were checked.
- [ ] No speculative component or dependency remains.
- [ ] Verification and rollback are executable.
