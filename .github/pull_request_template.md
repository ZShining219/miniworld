## Summary

<!-- What changed and why? Keep product behavior and implementation scope explicit. -->

## Scope and product alignment

- [ ] Task is recorded in `.ai/task_pool.ndjson` with a declared scope.
- [ ] Change is aligned with `goal.md` and does not merge Jobs, Profile/Resume, Work, or Fitness data flows.
- [ ] No exact address, exact coordinates, secrets, real personal materials, databases, logs, or generated resumes are included.

## Verification

- Local preflight: `scripts/agent-delivery-preflight.sh`
- Additional commands/results:

<!-- List focused tests, integration checks, visual/device evidence, or explain why not applicable. -->

## CI and release

- [ ] Five required CI checks are expected to pass.
- [ ] Production deployment is not implied by this PR.
- [ ] If production is appropriate, a separate deployment request will name the merged `main` SHA, backup, rollback, and post-deploy checks.

## User-facing notes

<!-- Mention behavior changes, known limitations, pending review, and follow-up work. -->
