# 实现记录

本文件只追加事实，不重写历史。每次实现任务结束时记录范围、结果、验证、偏差和下一步。讨论和计划不冒充已实现能力。

## 2026-08-18 — Goal v0.2 技术化

### 范围

- 把根目录 `goal.md` 从产品基线升级为产品与 Demo 执行契约；
- 建立 `goal/` 文档目录；
- 固定 LangGraph + FastAPI 全栈模板 + PostgreSQL + React + Docker Compose 路线；
- 记录 JobSpy、MarkItDown、JSON Resume、Reactive Resume 和 Khoj 调研结论；
- 编写架构、分阶段计划和人类可读决策记录。

### 已完成

- 产品意图、模块隔离、地址隐私和外部确认边界已写成强约束；
- 三个独立 LangGraph 的节点、写权限和失败路径已定义；
- 本地容器拓扑、REST API 分组、领域接口和数据表已定义；
- 上游导入方式、Git 提交策略和 Demo 验收阶段已定义。

### 当前仓库事实

- 仓库尚无 Git commit；
- 当前分支为 `master`；
- 本地尚未配置 `origin`；
- 远端 `https://github.com/ZShining219/miniworld` 已确认存在且为空；
- 当前尚未 clone 或导入 FastAPI 模板代码；
- 当前尚未安装项目依赖或启动容器。

### 当前机器事实

- 架构：Apple Silicon ARM64；
- Docker：已安装；
- Compose：`docker-compose 5.1.4` 可用，`docker compose` 子命令不可用；
- Node.js：v24.14.0；
- npm：11.9.0；
- uv：0.11.24；
- 系统 Python：3.14.3，项目应在容器或 uv 中固定兼容版本，不直接依赖系统 Python；
- Ollama：0.17.4，本机存在 `qwen2.5:3b`，但远端 AI 是当前主要语义能力方向。

### 验证

- 已对照用户确认内容检查三个闭环；
- 已明确技术方案不得反向改变 `goal.md`；
- 已检查目录文件、标题层级和相对文档链接；
- 项目治理 scope audit 显示 7 个文档变更全部在声明范围内，没有范围外修改。

### 下一步

- 用户审阅 Goal v0.2；
- 进入 Phase 0：Git 基线与 FastAPI 模板固定 commit 导入。

## 2026-08-18 — Phase 0 Git 基线与上游导入

### 已完成

- 将默认分支从 `master` 重命名为 `main`；
- 创建 goal/治理基线提交 `d0029b5`；
- 添加本地 `origin`：`https://github.com/ZShining219/miniworld.git`；
- 创建实现分支 `codex/bootstrap-langgraph`；
- Git 协议 clone 因当前网络连接失败，改用 GitHub 官方 codeload 获取同一上游快照；
- 通过 GitHub API 固定 FastAPI 模板 commit `162344da111e833b30892728372ab95331f06873`；
- 导入 backend、frontend、工作区清单、Compose 骨架和测试脚本；
- 排除上游 Git 历史、`.agents`、`.env`、云部署文件和无关资产；
- 保留 MIT 许可证与第三方来源说明。

### 未执行

- 未向 GitHub `origin` push；
- 未使用真实地址、个人材料或模型密钥；
- 尚未裁剪多用户、邮件和云端模板能力。

### 下一步

- 提交纯上游导入；
- 裁剪为本地单用户四容器结构；
- 建立 LangGraph 与三个业务闭环。

## 2026-08-18 — Goal v0.3 执行闭环补强

### 范围

- 在不改变用户意图的前提下，补齐本地 LangGraph 可运行性、双模式运行、用户主路径、数据分级、需求追踪和 Demo 冻结门；
- 将已经发生的 Git 基线与上游导入写入计划当前状态，避免计划文档继续把已完成事项描述为未来动作。

### 已完成

- 明确 LangGraph OSS 运行在本地 API/Worker 容器，不依赖 LangGraph Cloud 或 LangSmith；
- 定义无密钥、无真实材料的 `demo` 模式，以及需用户配置后才启用的 `live` 模式；
- 增加 `REQ-JOB`、`REQ-PROFILE`、`REQ-WORK`、`REQ-PRIVACY`、`REQ-RUNTIME` 五类需求追踪编号；
- 增加精确位置、授权个人材料、公开查询和公开结果四级数据处理规则；
- 将“市场认可度”落实为可验证的状态图、checkpoint、确认节点、schema、测试和完整全栈交付证据，不扩大为复杂多 Agent 系统。

### 未改变

- 仍然只有岗位、档案/简历、每日工作三个独立闭环；
- 岗位 Demo 仍只做查找整理、去重和直线距离；
- 精确住址仍禁止外发，外部写入仍需确认；
- 匹配评分、投递跟踪、自动投递和最终雷达视觉仍不属于当前 Demo。

### 当前实现事实

- FastAPI 上游模板已固定并导入；
- 单用户裁剪与 LangGraph 领域骨架处于未验证的进行中状态；
- 本次只修改目标文档，没有把尚未测试的代码标记为完成。

### 下一步

- 按 `REQ-RUNTIME` 完成并验证本地依赖、PostgreSQL checkpointer、迁移、API、Worker 和无密钥 `demo` 模式；
- 在上述骨架可启动后，按三个需求编号逐个完成端到端闭环。

---

## 2026-08-18 — Goal v0.4 意图锁定与实现事实同步

### 范围

- 不改变既有产品边界，集中记录用户已经逐项确认的解释；
- 区分真实操作入口、确定性 Demo、Live 只读集成和隐私证据；
- 将当前实现与尚未通过的 Compose/ARM64 验收同步到计划。

### 已完成

- 根目标新增“用户意图锁定矩阵”，明确住址含义、岗位当前范围、三闭环隔离、手动输入优先级、自动化权限和前端延期项；
- 将用户所称的多模态能力准确落实为可扩展的多来源、多格式输入，当前优先文件、公开 GitHub 信息和 GPT 对话材料；
- 增加动作权限判定表，明确公开只读、本地写入、个人材料外发推理和外部写入的不同确认要求；
- 强制区分 `demo` 替身数据与 `live` 互联网结果，防止将框架安装、静态页面或固定数据误报为目标完成；
- 更新 ARM64 冷启动验收，使 README/脚本必须显式处理旧式 Compose 与 BuildKit 兼容。

### 当前实现事实

- 后端已有三个独立 LangGraph、单用户 API、领域表、确定性与 OpenAI Provider、Demo/JobSpy 适配器、Worker 调度和 Alembic 迁移；
- 前端已有 Overview、Jobs、Profile、Work、Agent Runs 和 Settings 六个入口；
- 已有验证记录包括后端 Pytest `12 passed`、Ruff、Mypy、Ty、前端生产构建、Playwright `2 passed`、SQLite Alembic 升级和 Compose 配置校验；
- 上述本地测试不替代 PostgreSQL 容器重启、checkpoint 持久化、定时 Worker 和完整容器 E2E 证据。

### 未完成

- 首次 Docker 镜像构建在后端依赖安装阶段因旧式 builder 未启用 BuildKit 中止；四服务尚未完成启动与重启验收；
- Live JobSpy 公开来源和真实远端模型尚未验证；两者默认保持关闭；
- 尚未执行真实地址、真实个人材料、真实 API 密钥、外部写入或公开 Git push。

### 偏差与决策

- 新增 `T-013`：验收证据分层；这是对完成定义的澄清，不增加产品功能；
- 雷达/地图、匹配评分、投递跟踪、自动投递、图片/OCR 和音频仍未进入当前 Demo 完成条件。

### 下一步

- 先修复 Compose 的 BuildKit 启动兼容并完成四服务容器验收，再根据可复现证据更新 `goal.md` 勾选项；
- 在不使用精确住址的前提下验证一个允许访问的公开职位来源；任何真实个人材料或远端模型数据授权由用户后续决定。

---

## 2026-08-18 — Goal v0.5 本地 Demo 验收与证据收口

### 范围

- 关联需求：`REQ-RUNTIME`、`REQ-JOB`、`REQ-PROFILE`、`REQ-WORK`、`REQ-PRIVACY`；
- 用当前工作树重建四服务，复核后端、前端、容器、浏览器和泄漏证据；
- 对照根 `goal.md` 10.1—10.6 逐项勾选，未通过项继续保持未勾选；
- 复核 LangGraph、FastAPI 全栈模板、OpenAI Structured Outputs 与 Lever Postings API 公开资料。

### 已完成

- 使用 LangGraph OSS 的三个独立 Graph 在本地 API/Worker 容器中运行，PostgreSQL 保存 checkpoint，不依赖 LangGraph Cloud；
- 四服务在 Apple Silicon/ARM64 上由经典 Docker builder 成功构建并启动；
- 解决 Dockerfile 移除第二次 workspace 安装后的容器导入问题：明确设置 `PYTHONPATH=/app/backend`，并把预启动脚本改为 `python -m app...`；
- `scripts/test-local.sh` 与 `scripts/test.sh` 恢复可执行 Git mode，README 中的脚本命令可直接运行；
- 公开来源策略收敛为“公司 ATS/Job Board GET API 优先，JobSpy 最善努力”，不增加投递或其他外部写入。

### 验证

- `./scripts/test-local.sh`：后端 `13 passed`，Ruff/Mypy/Ty 通过，前端生产构建通过；Biome 无 error，保留 8 条 CSS 风格 warning；
- `bun run test`：Playwright `2 passed`；
- `docker-compose up -d --build`：当前源码镜像构建成功，`api`、`worker`、`frontend`、`db` 全部启动；
- `./scripts/test.sh`：按 README 原样执行“重建 + 启动 + 完整容器验收”通过，包含三闭环、三类材料、岗位幂等和距离、Worker 真实定时触发、Alembic、PostgreSQL checkpoint、回环端口与四服务重启持久性；最终输出为 `jobs=3 facts=60 reports=12 checkpoints=300`；
- 真实浏览器：Overview、Jobs、Profile、Work、Agent Runs、Settings 六页均可访问，页面不含精确演示坐标，console `0 error / 0 warning`；
- secret/PII 扫描：Git 候选文件中无非占位符 secret-like 值，无被 Git 追踪的 `.env`/数据库/日志，前端 bundle 无 secret-like 值、精确演示位置和本机绝对路径，Docker 日志无精确演示位置或 secret-like 值；
- `git diff --check`：通过。

### Live 证据与未完成

- 当前固定的 `python-jobspy==1.1.13` 实际 Site 枚举只有 `linkedin`、`indeed`、`zip_recruiter`；
- Indeed Live 请求返回 403，LinkedIn China 返回 451；没有绕过限制，Live 职位验收仍未通过；
- Lever 公开 Postings API 文档和公开板块可访问，但 `LeverJobAdapter` 尚未实现，不冒充为已集成；
- OpenAI Responses Provider 已使用 Pydantic Structured Outputs，但没有用户 API Key 和数据类别授权，因此未做真实远端调用；
- 地点无法解析的 UI 验收样例、checkpoint 恢复重试、非法模型 schema 负测试仍未完成；
- 未创建 `demo-v0.1` tag，未执行公开 push。

### 偏差与决策

- 本次没有扩展任何产品功能；只修正启动复现性和文档事实；
- 把 Architecture 中的目标节点与 v0.5 实际节点分开，防止将设计文档误读为全部实现；
- 匹配评分、投递跟踪、自动投递、最终雷达/地图视觉和真实外部写入仍不在 Demo 范围内。

### Git

- 分支：`codex/bootstrap-langgraph`；
- Goal v0.4 基线：`03f4106`；
- 当前实现与 Goal v0.5 尚待创建隔离的本地提交；
- 未 push。

### 下一步

- 先实现只读 `LeverJobAdapter`，使用公开演示/公司 Job Board 完成一次 Live 只读验收；
- 然后补齐未解析地点样例和 checkpoint 安全重试；
- 真实 OpenAI Provider 验证等待用户决定 Provider、模型与允许外发的材料类别。

---

## 2026-08-18 — Goal v0.6 Live 公开读取与恢复证据

### 范围

- 关联需求：`REQ-JOB`、`REQ-PROFILE`、`REQ-PRIVACY`、`REQ-RUNTIME`；
- 关闭所有不需要用户秘密、真实个人材料或外部写入授权的 Demo 冻结缺口；
- 不增加匹配评分、投递跟踪、雷达地图、真实申请或跨模块写入。

### 已完成

- 新增 `LeverJobAdapter`，仅调用公开 `GET /v0/postings/{site}`，site 使用显式白名单，location 只接收附近地标；代码中没有 Lever 申请 POST；
- 对来源没有可验证坐标的职位保存 `location_unresolved` 和明确 `distance_reason`，前端展示原因，不伪造距离；
- 为 Agent 运行增加失败历史、重试次数和 `POST /agent-runs/{id}/retry`；失败 Graph 使用原 `checkpoint_thread_id` 和 `graph.invoke(None, config)` 恢复，成功后再次重试返回 409；
- 让内存 checkpointer 在同一进程内持久，以便本地开发和测试也能真实跨 API 调用恢复；Docker 仍使用 PostgreSQL checkpointer；
- 对 Pydantic `ValidationError` 保存不含模型原始输出的安全错误，非法 schema 不写事实或简历；
- 验证 OpenAI 模式无 Key 时状态为 `awaiting_configuration`，事实和简历不增长；
- 新增 Alembic `20260818_0002`，为职位增加距离原因，为 Agent 运行增加重试审计字段。

### 验证

- `./scripts/test-local.sh`：后端 `17 passed`，Ruff、Mypy、Ty、前端生产构建通过；Biome 无 error、8 条既有 CSS warning；Playwright `3 passed`；
- `UV_CACHE_DIR=.cache/uv uv run --package app python scripts/verify-live-lever.py`：使用一次性临时 SQLite、虚构香港位置和公开地标 `Hong Kong`，Lever Live GET 返回 3 条公开职位；输出确认 `exact_location_exposed=false`、`external_write_performed=false`；
- `./scripts/test.sh`：按 README 原样完成重建与验收；四服务、Alembic `20260818_0002`、三闭环、Worker 定时、回环端口和重启持久性通过；额外制造“无工作记录”节点失败，新增虚构记录后从同一 PostgreSQL checkpoint 恢复，第二次重试被 409 阻断；最近输出 `jobs=3 facts=110 reports=25 checkpoints=548`；
- `git diff --check`、后端静态检查和 Live 验收脚本 Ruff 检查均通过。

### 未完成

- 未进行真实 OpenAI/其他远端模型调用：用户尚未确认 Provider、模型和允许外发的数据类别；
- 未配置用户真实附近地标，未使用真实住址、坐标、个人材料或 API Key；
- 未创建 `demo-v0.1` tag，未执行公开 push。

### 偏差与决策

- Lever 默认公司 site `binance` 只用于公开集成证明，不代表替用户选择长期求职公司；长期白名单仍由用户配置；
- 公开来源不提供坐标时保留职位并显式标记，不引入外部地理编码服务，也不改变“直线距离只在本地计算”的约束；
- checkpoint 恢复复用原运行记录以保持原始 Graph state 的 `run_id` 一致，并保留失败历史；成功终态不可再次重试。

### Git

- 分支：`codex/bootstrap-langgraph`；
- 本轮实现、文档和治理提交待创建；
- 未 push。

### 下一步

- 等待用户决定 Provider、模型与允许外发的数据类别，再用明确选择的最小材料完成唯一剩余的真实远端模型验收；
- 完成最终隐私扫描后，由用户决定本地 tag 和公开 push。

---

## 后续记录模板

```md
## YYYY-MM-DD — 任务名称

### 范围
- 声明的文件与能力范围

### 已完成
- 实际完成内容

### 未完成
- 明确未完成或延期内容

### 验证
- 命令、测试、截图或人工检查结果

### 偏差与决策
- 与计划不同之处、原因、关联 decision ID

### Git
- 分支、提交、上游 commit、是否 push

### 下一步
- 唯一推荐的安全下一步
```
