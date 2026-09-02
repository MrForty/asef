# Ship

**MODE:** HYBRID

## Trigger

Verified work must be committed, published or deployed, and release is requested or already authorized.

## Purpose

Turn verified work into a release with fresh evidence, a bounded change set and a verified rollout, without widening scope.

## Requires

- QA evidence on the current tree;
- `PROJECT.md` Commands and Environments;
- the task or change set to release;
- the authorized scope: commit, pull request, merge, deploy.

## Optional

`PLAN.md` rollout and rollback, changelog and documentation conventions, `LEARNINGS.md`, specialist release or deploy tooling.

## Do not load

Unrelated branches, full history, production credentials beyond the authorized step.

## Procedure

1. Fix the authorized scope; stop at its last step and report what remains.
2. Sync with the base branch; resolve conflicts by intent; rerun focused checks after any merge.
3. If evidence is stale under `ARTIFACTS.md`, rerun the verification commands from `PROJECT.md`; record command, result and tree.
4. Confirm the change set is one task: no unrelated file, debug artifact or secret.
5. Update documentation describing the changed behavior, and the changelog when the project keeps one; with `public-surface`, document the changed seam and any breaking change.
6. Commit under the version-control rules in `ASEF.md`; open or update the pull request with outcome, acceptance criteria, evidence and limitations.
7. With `deployed` and deploy authority, execute the `PLAN.md` rollout, then verify the target from `PROJECT.md` Environments: health check, the acceptance path, error output; record evidence.
8. On failed verification execute the `PLAN.md` rollback, record the failure and route to `diagnose`.
9. Record any release pitfall in `LEARNINGS.md`.

## Exit criteria

- evidence is fresh on the released tree;
- the change set is bounded and secret-free;
- documentation and changelog match the release;
- the release artifact exists at the authorized level: commit, pull request, merge or deployment;
- a deployed target is verified, or rollback is executed and recorded;
- `STATE.md` records the release state and what remains unauthorized.

## Outputs

Commits, pull request or deployment, release evidence, updated documentation, `STATE.md` update.

## Next

`DONE`; `diagnose` when post-release verification fails.
