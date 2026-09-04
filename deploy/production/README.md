# Fitness production deployment

This stack exposes only Caddy on ports 80/443. FastAPI and PostgreSQL stay on
an internal Docker network, and Caddy forwards only
`/fg-api/api/v1/fitness/*`.

## One-time server preparation

Run `scripts/bootstrap-production-host.sh` as root on Ubuntu 24.04. Create
`/etc/miniworld/production.env` with mode `600` from the example in this
directory. The real database password and Basic Auth hash must never enter Git.

## Release

Merge a verified PR into `main`, then prepare a deployment request containing the
merged SHA, CI evidence, backup plan, and rollback SHA. Only after explicit user
approval run as root on the server:

```sh
MINIWORLD_DEPLOY_APPROVED=1 \
  /srv/miniworld/scripts/deploy-production.sh <40-character-main-sha>
```

The script refuses an unapproved invocation or a SHA that is not an ancestor of
`origin/main`. It fetches the public origin, checks out exactly that SHA, backs
up an existing database, builds sequentially, starts the stack, verifies
internal health and the public authentication boundary, and records the deployed
SHA.
After the first deployment, run `scripts/install-production-operations.sh` as
root to enable the daily backup timer and failed-login banning.

## Data and backups

Use `scripts/export-fitness-data.sh` on the development machine only after
pausing local Fitness writes. Import that custom-format dump with
`scripts/import-fitness-data.sh` after production migrations. The importer
refuses to write unless all four production Fitness tables are empty.
Production backups are
written under `/var/backups/miniworld-fitness`, retained for seven days, and
can be tested with `scripts/restore-production-smoke.sh` without touching the
production database.

The production server database is the sole source of truth after go-live. The
local database remains development-only; there is no bidirectional merge.
