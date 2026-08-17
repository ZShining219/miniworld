# Last Summary

[Quick Link]
- TASK: T-006 — Goal v0.5 and the local deterministic three-loop Demo are verified; seven freeze items remain
- ISSUE: ISS-003 — a successful lawful Live public job source is still missing
- DECISION: D-014 — prefer read-only company ATS/Job Board APIs, starting with Lever, before best-effort JobSpy

[Current Focus]
- Application commit `c649ae0` provides the local single-user FastAPI/React/PostgreSQL/Worker Demo with three independent LangGraph workflows; Goal v0.5 and user operations are committed as `2d6c1d2`.
- `./scripts/test-local.sh` passes 13 backend tests, Ruff/Mypy/Ty, frontend build, Biome with eight CSS warnings, and two Playwright tests. `./scripts/test.sh` passes the rebuilt four-service container flow with `jobs=3 facts=60 reports=12 checkpoints=300`.
- Goal v0.5 truthfully checks 29 evidence-backed items and leaves seven items unchecked. No real address, personal material, API key, external write, public push, or false Live-source claim was used.

[Active Locks]
- None. The Goal v0.5 finalization window released its `GLOBAL_REFACTOR` lock.

[Open Issues]
- ISS-003: Indeed returned 403 and LinkedIn China returned 451; a successful public-source run still requires a lawful read-only adapter such as Lever Postings.

[Pending Review]
- User review of Goal v0.5 and its seven explicitly unchecked freeze items.
- Selection of permitted Lever company Job Boards/query frequency for the next Live-source step.
- OpenAI Provider/model/data-category authorization before any real personal-material inference.
- Public push remains unperformed and requires explicit confirmation.

[Next Step]
- Implement a read-only `LeverJobAdapter` using public Job Board data, then add an unresolved-location UI sample and a checkpoint-safe retry path. Keep matching scores, application tracking, radar visuals, real external writes, and public push out of scope.
