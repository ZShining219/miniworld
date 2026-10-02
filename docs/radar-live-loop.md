# 求职雷达「主动获取」闭环 — 交接说明

本文件描述 v0.9 引入的雷达主动获取链路：定时抓取 → 结构化输出 → 雷达呈现更新 → 对接面试项目。验收证据见 `output/acceptance/radar-loop/`（不入库）。

## 架构入口

```
worker tick (apscheduler, backend/app/worker.py)
  └─ run_schedule_tick()               # 读 ScheduleConfig(1)，到期才跑，回写 last_run_*
       └─ run_job_discovery()          # backend/app/agent/runner.py（LangGraph checkpoint）
            └─ job_discovery graph     # backend/app/agent/graphs.py
                 ├─ fetch_sources      # JOB_ADAPTER_FACTORIES 注册表 adapters.py
                 ├─ resolve_locations  # 纯本地 gazetteer（agent/gazetteer.py + geocode.py）
                 ├─ enrich_jobs        # provider 网关（agent/jobs_enrich.py）
                 └─ persist            # JobPosting 指纹去重 + AgentRun 计数
GET /api/v1/radar/scene                # 已定位岗位 → GeoJSON；未解析 → pending_jobs
POST /api/v1/jobs/{id}/interview-handoff  # interview_handoff.py → 文件导出 + 可选推送
```

前端：`frontend/src/radar/RadarApp.tsx`（MapLibre+PMTiles 保留；antd Drawer 列表/详情、Badge 新岗位、轮询刷新）；共享动作 `frontend/src/components/InterviewHandoff.tsx`。

## 启停定时任务

- Worker 是独立进程：`SCHEDULER_ENABLED=true` 才跑调度（compose 中 worker 服务已开，API 服务关闭）。
- 调度参数持久化在 `ScheduleConfig`（`GET/PUT /api/v1/schedule`）：`job_discovery_enabled`、`interval_minutes`、`sources`、`query_text`、`live_enabled`。
- `POST /api/v1/schedule/run-once` 立即手动触发一轮（不回改周期）。
- 前端「设置 → 求职雷达调度」面板可开关、改间隔、选来源；「上次运行」计数同时显示在雷达窗底部。
- 本地验收技巧：`JOB_SCHEDULE_MINUTES=0 SCHEDULER_POLL_SECONDS=4` 可让每 tick 到期。

## 如何加新 provider

1. 在 `backend/app/agent/adapters.py` 实现 `JobSourceAdapter`（`source` 名 + `fetch(query) -> list[JobDraft]`），`JobDraft` 字段含公司/职位/地点文本/薪资/URL/发布时间。
2. 注册进 `JOB_ADAPTER_FACTORIES`。demo 源确定性数据直接进 `demo` adapter；公开 GET 源参照 `lever.py`/`greenhouse` adapter（只读、可超时、错误进 `source_errors` 不炸整轮）。
3. `live_enabled` 的源只有 `EXECUTION_MODE=live` 且 `ALLOW_LIVE_JOB_SEARCH=true` 才会执行；worker 无法自我升级到 live。
4. 岗位摘要走 `jobs_enrich.py` 的 provider 网关：`JOB_AGENT_PROVIDER=demo|deepseek|disabled`，DeepSeek 走 `JOB_AGENT_API_KEY/BASE_URL/MODEL`（本地 `.env`，不入库；`JOB_LLM_MAX_PER_RUN` 限每轮调用数，材料最小化只送公开字段）。

## 对接面试项目的接口约定

面试项目：`/Users/zfh/Documents/ChatGPT/New project 2`（FastAPI，`127.0.0.1:8788`）。

- **导出（始终）**：每次 handoff 写 `runtime-data/interview-handoff/job-<id8>.json`，内含 `knowledge_import.records`（`ImportDocument` 形状）+ `interview_plan_request`（`POST /api/interview/plan` 模板）。
- **推送（显式确认）**：`push=true` 时先试 `POST {INTERVIEW_AGENT_BASE_URL}/api/admin/login`（`X-Admin-Request: 1` + `data/admin-access.key`，经 `INTERVIEW_AGENT_KEY_FILE` 配置）→ `POST /api/admin/acquisition/import`；失败回退 CLI `python -m app.knowledge.cli --db data/knowledge.db import`（需 `INTERVIEW_AGENT_DIR`）。httpx 客户端 `trust_env=False`——本机回环不走系统代理。
- **审批语义**：记录以 `status=pending` 进对方语料库，MiniWorld 不能审核/发布；相同内容对方去重并保持原审核状态。
- **角色/级别映射**：`agent/interview_mapping.py` 按职位标题映射对方 role_id/level（默认 `llm_app`/`unspecified`）；非法组合报 `HandoffError` → API 422。
- 前端在雷达抽屉和岗位页都有「去练面试」：`Popconfirm` 确认后才推送（外部写确认点）。

## 隐私边界

- 精确家庭地址/坐标不出本机：`/radar/scene` 只回 center 供地图定位；features 只含已解析岗位坐标；未解析岗位进 `pending_jobs` 计数与列表。
- 地理编码纯本地（`gazetteer.py` 内置公开地名+用户地标），live 抓取也不外发 home。
- demo 源与 live 源严格分离；live 只允许公开 GET；一切外部写仍需用户确认。

## 已验证

- 后端 `pytest` 50 项全过（`test_radar_loop.py` 覆盖调度计数/去重/scene/pending/隐私/handoff/间隔回归）；`ruff`/`mypy`/`ty` 全绿。
- 前端 `bun run build`（tsc+vite）、`biome check` exit 0（8 个 `styles.css` 历史 `!important` a11y warning）、Playwright 11/11、实机截图无应用层 console 错误。
- 实跑：worker 连续 tick 日志 `new=3 → updated=3 → 0/0/0`；admin_api 推送落对方面试项目 pending（`miniworld_radar` 1 条）。
