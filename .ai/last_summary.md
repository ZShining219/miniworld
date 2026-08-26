# Last Summary

[Quick Link]
- TASK: T-017 — root README runtime registry completed and all project services stopped with data preserved
- TASK: T-016 — v0.9 remains published on `origin/codex/bootstrap-langgraph`
- TASK: T-015 — Fitness H5 Demo remains verified; native packaging is deferred

[Current Focus]
- Root `README.md` is now the canonical runtime registry for Compose services, H5, native Radar, task-oriented startup combinations, verification commands and stop rules.
- All Compose containers and the project network are stopped and removed. Ports 5173, 8000 and 9000 have no listeners; no H5 or Tauri process remains.
- PostgreSQL and upload volumes remain intact, so later task-oriented startup can resume existing local data.

[Active Locks]
- None after T-017 handoff.

[Open Issues]
- None for runtime registration or shutdown.

[Pending Review]
- The local runtime-registry checkpoint has not been pushed; remote `origin/codex/bootstrap-langgraph` remains at `7ae7d3c` until a later explicit push.
- Remote `main`, release tags, Android, WeChat, optional remote Provider and real map/job data remain separate decisions.

[Next Step]
- For future work, select the smallest combination from the root README `运行内容注册表`; do not start the full Compose stack unless the task needs it.
