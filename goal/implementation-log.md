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

## 2026-08-18 — Goal v0.7 对话意图与完成定义复审

### 范围

- 以用户原始确认而不是 v0.6 自身作为最高层依据，逐条复核住址、岗位范围、三闭环隔离、输入优先级、日报周报、自动化权限、本地优先和 Demo 完成定义；
- 关联需求：全部 `REQ-*`，但本轮不扩大产品功能。

### 审计结论

- 11 类明确意图均能映射到 Goal 条款、实现入口和直接验证证据；新增 `goal/intent-audit.md` 固化映射；
- 岗位匹配评分、投递跟踪、最终雷达视觉、真实偏好、多用户和外部写入仍保持非目标；
- 发现 v0.6 把“允许受控远端 AI”扩大成“真实远端调用阻塞 Demo”，与“本地优先、先完成 Demo、模型细节暂不纠结”的原始意图不一致；
- v0.7 保留 OpenAI Provider、schema、配置门、审计和未来真实调用能力，只把真实调用恢复为非阻塞可选验证；没有删除用户要求的三个闭环。

### 当前完成判定

- 根 `goal.md` 的 Demo 必选项全部勾选；
- 真实地标/长期公司白名单、远端模型、最终视觉、tag 和公开 push 是配置、增强或发布决策，不是当前运行缺口；
- 是否创建 tag 或公开 push 仍留给用户审阅后决定。

### 最终验证

- `bash -n scripts/verify-demo.sh` 与 `git diff --check` 通过；
- `./scripts/test-local.sh` 通过：17 项后端测试，Ruff、Mypy、Ty、前端生产构建和 3 项 Playwright 均通过；Biome 无错误并保留 8 条已知 CSS 风格 warning；
- `./scripts/test.sh` 通过四服务重建、三闭环、Worker、PostgreSQL checkpoint 恢复、容器重启和回环端口验证；最近一次为 `jobs=3 facts=110 reports=25 checkpoints=620`；
- 容器验收脚本重复运行前后，业务计数均为 `jobs/facts/resumes/work/reports=3/110/33/24/25`；只新增预期的运行/checkpoint 账本，不再重复导入演示材料、工作记录或报告；
- 本地位置 API 只返回 `••••••（仅保存在本机）`，不含地址或坐标字段；Git 候选、前端 bundle 和 Docker 日志扫描未发现真实 secret、地址、坐标或本机绝对路径；
- secret-like 扫描仅命中 README 的 `replace-locally`、单元测试的 `sk-example-*` 与 bundle 中的字段名 `exact_address`，均经人工确认是占位符/输入契约，不是用户数据；
- scope guard 的产品/代码变更全部位于 T-008 声明范围；报告中的范围外变化仅为测试工具清理的忽略缓存文件，不属于提交内容。

### Git

- 审计修正和治理提交待创建；
- 未 tag、未 push。

---

## 2026-08-19 — 岗位雷达呈现调研与实施计划

### 范围

- 关联 `REQ-RADAR`、`REQ-PRIVACY` 和 `REQ-RUNTIME`；
- 只完成开源模块、离线底图、桌面悬浮窗与渲染接口的选型和计划，不实现岗位数据来源或真实地图运行。

### 已完成

- 复核当前 React 19/Vite 前端、纯 CSS 雷达占位、位置 API 隐私契约与 Jobs 数据结构；
- 核验 MapLibre GL JS、PMTiles、Protomaps Basemaps、Leaflet、Tauri 2 和 OSMF Tile Usage Policy 的官方资料；
- 选择 Tauri 2 + MapLibre GL JS + PMTiles + Protomaps 本地矢量底图；Leaflet 保留为低配回退评估；
- 将用户明确的悬浮窗、街道地图、中心 HOME 与黄色闪光岗位点写入 Goal v0.8，并形成 Phase 7 的接口、数据流、降级、测试和提交边界。

### 未完成

- 尚未安装依赖、下载或生成地图包、创建 Radar 组件、场景 API 或 Tauri 宿主；
- 尚未选择真实城市/区域地图包；选择必须使用公开区域或附近地标，不能向外部地图服务发送精确住址或家庭坐标；
- 岗位数据接入按用户要求暂缓，首个原型使用明确标记的虚构坐标。

### 验证

- 官方 MapLibre 文档确认 TypeScript/WebGL 矢量瓦片渲染、style/source/layer 与 Vite ESM worker 接入；
- PMTiles 文档确认单文件、HTTP Range、本地服务器和 MapLibre/Leaflet/OpenLayers 集成；
- Protomaps Basemaps README 确认 OSM/Natural Earth → PMTiles、MapLibre 主题样式和 BSD-3/CC0/ODbL attribution；
- Leaflet 官方页确认约 42 KB、无外部依赖及 Marker/GeoJSON/CSS 能力；
- Tauri 2 配置文档确认 `alwaysOnTop`、`resizable`、`minWidth/minHeight`、`decorations` 与 macOS 透明窗口限制；
- OSMF policy 确认标准瓦片服务禁止离线预取，离线应用应使用自托管或明确允许离线的瓦片。

### 偏差与决策

- 不采用“在线 OSM 栅格 + Leaflet”作为默认方案：它会把住所视口发送给外部服务，且标准 OSM 瓦片不能用于离线预取；
- 不采用 deck.gl/Cesium：当前岗位点规模和二维街道需求不足以证明额外复杂度；
- 首版不做透明、点击穿透悬浮窗，避免 macOS 私有 API、发布与交互可靠性风险。

### Git

- 分支：`codex/bootstrap-langgraph`；
- 本轮仅修改 Goal、研究、架构、计划、决策和治理记录；未安装依赖、未 tag、未 push。

### 下一步

- 按 Phase 7.1 使用虚构区域 PMTiles 和虚构岗位点实现可在浏览器审阅的离线 Radar 原型，再进入场景 API 与 Tauri 原生窗口。

---

## 2026-08-19 — Phase 7.1 离线岗位雷达原型

### 范围

- 关联 `REQ-RADAR`、`REQ-PRIVACY` 和 `REQ-RUNTIME`；
- 只使用 Firenze 公共示例地图包、虚构 HOME 中心和 4 个虚构岗位坐标，不接入真实地址或岗位数据。

### 已完成

- 固定 `maplibre-gl@6.4.1`、`pmtiles@4.5.0`、`@protomaps/basemaps@5.7.2` 与 GeoJSON 类型，`/radar` 以懒加载模块隔离于主看板首包；
- 实现深色街道、建筑和水系底图、固定中心 HOME、GeoJSON 黄色实心点与外扩脉冲光晕、扫描扇区、距离圈和岗位摘要；
- 主看板可打开 420×420 可缩放浏览器审阅窗；该入口是原生窗口前的原型，不冒充 Tauri 悬浮窗；
- 新增只允许 `.pmtiles` 的 localhost Range 端点，以及带 SHA256 校验的 `scripts/fetch-radar-demo-map.sh`；地图运行文件位于 Git 忽略的 `runtime-data/maps/`；
- 增加 PMTiles 可用性 Range 预检、明确缺图提示和 Vite MapLibre worker 优化排除，修复开发服务器永久 loading 的真实集成问题；
- 新增 Radar Playwright 覆盖 HOME 几何居中、黄色信号、320×320、420×420、900×700、缺图状态和零外部地图请求。

### 未完成

- 尚未实现 `/api/v1/radar/scene`、真实本地位置/岗位过滤、未解析计数、无岗位状态或 WebGL 不可用状态；这些属于 Phase 7.2；
- 尚未创建 Tauri 宿主、原生置顶/拖动/关闭/尺寸持久化；浏览器弹窗不能作为 `goal.md` 10.8 的原生验收证据；
- 地图包仍是 Firenze 公共示例，不代表用户真实城市或长期地图包选择。

### 验证

- `uv run --project backend pytest backend/tests/test_api_privacy.py -q`：6 passed；`uv run --project backend ruff check backend/app backend/tests`：通过；
- `bun run build`：通过，主看板与 Radar 分块输出；`bun run lint`：零错误，保留 8 条既有 CSS warning；
- `bun run test`：5 passed，其中 Radar 2 项覆盖三档尺寸、缺图和网络边界；
- PMTiles 为 6,601,156 bytes，SHA256 `7190f3d807a62f4f012b574007c96b809f6842f45a6b0c508639331fc68fd30a`，`git check-ignore` 确认不进入版本库；
- 本地 QA 截图位于忽略目录 `output/playwright/radar-qa/`；像素检查确认三档尺寸街道可读、HOME 居中、黄色岗位信号和 OSM attribution 可见；
- `git diff --check` 通过。

### 偏差与决策

- 将 Tauri npm/Rust 依赖固定移到真正创建原生宿主的 Phase 7.3，避免 Phase 7.1 原型携带未使用依赖；产品目标、版本选择与隐私边界不变；
- MapLibre 的 `load` 事件不能可靠证明 PMTiles 存在，因此增加独立 Range 预检作为缺图状态依据。

### Git

- 分支：`codex/bootstrap-langgraph`；
- 本轮工作树尚未提交；未 tag、未 push。

### 下一步

- 单独声明 Phase 7.2 场景 API 与隐私范围，以本机已保存位置和岗位数据替换虚构场景，同时保留虚构 Demo 回退和地址不回显。

---

## 2026-08-19 — Phase 7.2 本地雷达场景与隐私门

### 范围

- 关联 `REQ-RADAR` 与 `REQ-PRIVACY`；
- 实现场景渲染契约和降级状态，不扩大岗位采集来源，不使用真实地址或真实岗位材料。

### 已完成

- 新增 `GET /api/v1/radar/scene`，返回 `[longitude, latitude]` 中心、GeoJSON 岗位点、未解析/总数、地图包名称和本地可用状态，并设置 `Cache-Control: no-store`；
- `demo` 模式集中返回 Firenze 虚构场景；非 demo 本地模式只映射 `distance_status=calculated` 且经纬度完整的岗位；
- 场景属性只含岗位 ID、标题、公司、距离、来源和链接，不含精确住址文本、`location_text` 或未解析岗位正文；
- Radar 改为场景 API 驱动，地图名和中心不再硬编码在前端；保留 PMTiles Range 预检；
- 增加零岗位/未解析计数状态、无本地位置/场景请求失败状态、地图包缺失状态和 WebGL2 不可用状态；
- WebGL2 在创建 MapLibre 前主动探测，避免初始化失败后 ResizeObserver 访问未完成 painter。

### 验证

- `uv run --project backend pytest backend/tests/test_api_privacy.py -q`：8 passed；默认 Demo 与非 demo 本地过滤均验证 `no-store` 和地址不回显；
- `bun run test tests/radar.spec.ts`：4 passed，覆盖三档中心/黄色点/无外部请求、未解析空态、WebGL2 降级和缺图状态；
- `bun run build`：通过，Radar 继续保持独立懒加载块。

### 偏差与决策

- 用户已明确岗位数据接入暂缓，因此默认场景仍为虚构 Demo；非 demo 过滤契约已有测试，但不把它宣称为真实岗位雷达数据已完成；
- 当前地图包名为本地配置基线 `demo-firenze.pmtiles`；真实城市/区域包仍需用户以后选择公开区域，不能从精确家庭坐标向外部地图服务生成请求。

### Git

- 分支：`codex/bootstrap-langgraph`；
- 本轮工作树尚未提交；未 tag、未 push。

### 下一步

- 创建 Tauri 2 原生宿主，仅承载现有 `/radar`，完成置顶、拖动、尺寸/位置持久化和 macOS ARM64 构建验收。

---

## 2026-08-19 — Phase 7.3 Tauri 原生岗位雷达与 v0.8 验收闭合

### 范围

- 关联 `REQ-RADAR`、`REQ-PRIVACY` 与 `REQ-RUNTIME`；
- 只新增本机原生呈现、最小窗口控制、geometry 持久化、降级状态和验收证据，不接入真实地址、真实岗位、外部瓦片、投递或消息能力。

### 已完成

- 固定 `@tauri-apps/api@2.11.1`、`@tauri-apps/cli@2.11.4`、Rust `tauri@2.11.3` 与 `tauri-build@2.6.3`，生成并保留 `Cargo.lock`；
- 创建只承载 `index.html?surface=radar` 的 Tauri 2 窗口：初始 420×420、最小 320×320、最大 900×700、可缩放、无边框、不透明且默认置顶；
- capability 只开放窗口居中、关闭、读取/设置置顶和开始拖动；应用内控制条完成拖动、图钉、重新居中和关闭桥接，浏览器 `/radar` 仍可独立审阅；
- Rust 只把逻辑坐标和尺寸保存到 `~/Library/Application Support/com.zshining219.miniworld.radar/radar-window.json`，当前内容为 `{"x":120.0,"y":120.0,"width":900.0,"height":700.0}`，没有地图中心、地址、岗位或坐标；
- 本地 API、地图包和 WebGL2 三类失败分别显示 `LOCAL API UNAVAILABLE`、`LOCAL MAP UNAVAILABLE` 和 `WEBGL UNAVAILABLE`；API 状态给出 `docker-compose up -d`，地图状态只指向本地资源脚本；
- 未解析岗位继续不落图，空态显示待解析数量和明确的“返回岗位列表”动作；HOME 场景坐标不进入可见文本；
- Tauri CSP 的网络连接只允许 IPC 和 `http://127.0.0.1:8000`，后端允许 Tauri 本地 origin 与 PMTiles `Range` 请求，不增加外部地图连接。

### 验证

- `./scripts/test-local.sh`：22 项后端测试通过；Ruff、Mypy、Ty、Vite 生产构建通过；Biome 零错误并保留 8 条既有 CSS warning；Playwright 9 项通过；
- Radar 专项 6 项覆盖 320×320、420×420、900×700、HOME 居中、黄色脉冲点、岗位点击摘要、坐标不回显、未解析计数/列表入口、API 503、WebGL2 和地图包缺失，网络拦截确认无外部请求；
- `cargo fmt --check` 与 `cargo check` 通过；`bun run tauri:build` 生成未签名 `MiniWorld Job Radar.app`；`file` 确认为 `Mach-O 64-bit executable arm64`；
- 最终 release 原生运行的 Quartz 窗口为 `layer=5`、`900×700 @ (120,120)`，证明浮动层与 geometry 恢复；同一 T-012 的首次原生 QA 记录为 420×420；
- release/bundle 扫描未发现 debug QA 开关、测试端口、测试家庭坐标或演示地址；`MINIWORLD_RADAR_QA_EXPANDED` 只在 debug 编译中存在；
- Firenze PMTiles 为 6,601,156 bytes，SHA256 `7190f3d807a62f4f012b574007c96b809f6842f45a6b0c508639331fc68fd30a`；地图、`frontend/dist` 与 Tauri `target` 均由 Git 忽略；
- `git diff --check` 通过，第三方版本、BSD-3、Apache-2.0/MIT、OSM attribution 与 ODbL 已记录。

### 偏差与决策

- release 使用 `--no-sign`，仅作为本机 Demo 产物，不宣称签名、公证或可分发发布包；
- 系统鼠标自动化无法稳定进入无边框 WebView，因此原生缩放证据由 Tauri 配置、真实 420/900 窗口、geometry 恢复和三档渲染回归共同构成，不把自动化限制误报为产品故障；
- 默认继续使用 Firenze 公共示例地图和明确标记的虚构岗位；真实城市地图包与真实岗位坐标接入仍由用户后续选择，不属于本阶段完成门。

### Git

- 分支：`codex/bootstrap-langgraph`；
- Phase 7 当前工作树尚未提交；未创建 tag，未执行 push。

### 下一步

- 用户审阅原生岗位雷达后，再决定公开城市/区域地图包与真实岗位数据接入；任何 tag、公开 push 或真实个人数据操作仍需单独确认。

---

## 2026-08-25 — v0.8 状态整理与本地提交

### 范围

- 关联 `REQ-RADAR`、`REQ-PRIVACY` 与 `REQ-RUNTIME`；
- 审核并提交既有 Phase 7.1—7.3 工作树，不新增真实岗位、真实位置、远端模型、tag 或公开 push。

### 已完成

- 逐项复核岗位雷达后端场景接口、React/MapLibre 前端、Tauri 2 原生宿主、依赖锁、第三方许可、Goal v0.8 文档和治理事件；
- 发现并修复标准 Compose 启动路径未把宿主 `runtime-data/maps/` 提供给 API 容器的问题：API 现在以只读方式挂载 `/data/radar-maps`，不会把 PMTiles 写入镜像或 Git；
- 确认 PMTiles、前端 `dist`、Playwright 输出和 Tauri `target` 均保持 Git 忽略，提交候选不包含运行数据或构建产物；
- 按 D-021 将共同验证、共享场景契约与隐私证据的 Phase 7.1—7.3 收口为一个真实的本地 Git 检查点，不伪造历史拆分。

### 验证

- `./scripts/test-local.sh`：22 项后端测试、Ruff、Mypy、Ty、Vite 生产构建和 9 项 Playwright 测试通过；Biome 零错误，保留 8 条既有 CSS warning；
- `cargo fmt --manifest-path frontend/src-tauri/Cargo.toml --check` 与 `cargo check --manifest-path frontend/src-tauri/Cargo.toml`：通过；
- `bun run tauri:build`：未签名 macOS `.app` 打包通过，二进制仍为 Mach-O arm64；
- `docker-compose config`：确认 `runtime-data/maps` 只读绑定到 API `/data/radar-maps`，并由 `RADAR_MAP_DIR` 指向该路径；
- 地图 SHA256 仍为 `7190f3d807a62f4f012b574007c96b809f6842f45a6b0c508639331fc68fd30a`；候选 secret/PII 扫描只命中明确测试占位符；`git diff --check` 通过。

### 偏差与决策

- 首次沙箱内 Playwright 因禁止绑定 `127.0.0.1:4173` 而未启动；在获准的本机执行环境重跑同一完整命令后 9 项全部通过，未归类为产品故障；
- scope guard 的范围外变化仅为被忽略的测试、类型检查、前端构建和 Tauri 构建缓存；没有范围外源文件变化；
- Compose 地图挂载属于让既有 README 与已验收本地运行契约一致的缺口修复，不扩大产品范围。

### Git

- 分支：`codex/bootstrap-langgraph`；
- Goal v0.8 Phase 7 源码、测试、文档和治理状态由 T-013 收口为一个本地提交；
- 未创建 tag，未执行 push。

### 下一步

- 用户可启动本地 API 与 Tauri 窗口审阅 Firenze 虚构 Demo；后续是否选择真实公共城市地图、接入本地真实岗位坐标、验证远端 Provider、创建 tag 或 push 均需独立决定。

---

## 2026-08-25 — unibest 多端系统壳本地配置（进行中）

### 范围
- 关联 `REQ-RUNTIME`、`REQ-JOB`、`REQ-PROFILE`、`REQ-WORK` 与 `REQ-PRIVACY`；
- 只新增独立系统壳和 Web 配置，不迁移既有业务模块，不构建微信小程序或 Android 包。

### 已完成
- 固定并审查 unibest 4.4.1 `base` commit `a3bd15128c4f86bb0ce00723ec4cbf66d3932f1d`，保留 MIT 许可证；
- 导入到 `apps/miniworld-shell/`，排除上游 `.git`、`AGENTS.md`、`.agents/`、`.cursor/`、`.vscode/`、`.github/`；
- 移除示例远端 API/AppID、嵌套 `git init`、开发期远端 Eruda、构建自动打开分析页和 Android 默认敏感权限；开发服务器绑定 `127.0.0.1`，API 默认 `127.0.0.1:8000`；
- 建立总览、岗位、档案、工作四入口的响应式空白系统壳，三个闭环保持独立并标明尚未接入。

### 未完成
- pnpm 依赖安装、类型检查、测试、H5 构建和浏览器验收尚未完成；用户明确授权后，两次相同的联网安装仍在进程启动前因审批服务 `503 auth_unavailable` 被拦截，离线缓存不足且未改用镜像或其他工具绕过审批。
- 微信小程序和 Android/HBuilderX 按用户指令暂缓。

### 验证
- 固定提交、许可证、导入排除项、JSON 配置与敏感示例值已静态检查；完整运行证据等待依赖安装。

### Git
- 分支：`codex/bootstrap-langgraph`；未提交、未 tag、未 push。

### 下一步
- 在项目根目录执行 `cd apps/miniworld-shell && pnpm install --ignore-scripts --frozen-lockfile`，随后恢复类型/测试/构建与桌面/手机浏览器验收。

---

## 2026-08-25 — unibest Web 壳安装与本地验收完成

### 范围
- 续作 T-014，仅完成 `apps/miniworld-shell/` 的依赖安装、Web 构建和本地浏览器验收；未构建微信小程序或 Android 包。

### 已完成
- 从获批的 `registry.npmjs.org` 完成锁定依赖安装，共链接 2245 个包；生命周期脚本保持禁用，并在 `pnpm-workspace.yaml` 明确忽略上游 `@uni-helper/unocss-preset-uni` 构建脚本；
- 将构建插件直接使用的 `fs-extra@10.1.0` 声明为开发依赖；
- 修正标签栏类型引用，改用 `virtual:uni-pages` 导出的公开 `LocationUrl`，并将备用原生标签栏的已删除示例路径更新为现有档案页；
- H5 开发服务已在 `http://127.0.0.1:9000/` 拉起并保持运行。

### 验证
- `pnpm install --ignore-scripts --frozen-lockfile`：通过；
- `pnpm type-check`：通过；
- `pnpm test:run`：4 个测试文件、21 项测试全部通过；
- `pnpm build:h5`：H5 production 构建通过；
- 应用内浏览器：`1440x900` 桌面总览与 `390x844` 手机视口通过；手机端真实点击总览、岗位、档案、工作四个入口，路由与占位内容正确，所有页面均无横向溢出；
- 浏览器控制台无 warning/error；运行页只加载 `@vite/client`、本地 favicon 和本地 `src/main.ts`，没有非 localhost 页面资产请求或业务 API 请求。

### 偏差与决策
- pnpm 11 的脚本审批预检会把未明确处理的上游构建脚本视为错误；本轮按既定安全边界显式忽略该脚本，没有批准执行；
- 首轮类型检查暴露两个上游遗留类型问题，均以现有生成路由类型为来源完成最小修正，没有放宽类型检查；
- 微信小程序 AppID/构建和 Android/HBuilderX 出包继续延期。

### Git
- 分支：`codex/bootstrap-langgraph`；本轮未 commit、未 tag、未 push。

### 下一步
- 将现有 Demo 作为独立工具逐步接入四入口；接入前分别定义模块接口、数据边界与审批门，不在壳层内混合三个业务闭环。

---

## 2026-08-25 — 明确统一呈现平台与功能备案规则

### 范围
- 更新根目录 README 的项目定位和功能台账，不新增业务行为。

### 已完成
- 明确 `apps/miniworld-shell/` 中的 unibest 是统一呈现平台，现有 React、FastAPI、LangGraph 和 Tauri 能力继续作为可独立运行的工具；
- 在 README 增加岗位发现、岗位雷达、个人档案、工作沉淀、Agent 运行、微信小程序和 Android/HBuilderX 的状态、入口、边界及验证说明；
- 增加后续功能备案规则，要求记录状态、入口、启动方式、验证证据、延期事项和隐私/授权边界。

### 验证
- `git diff --check`：通过；
- README 中的功能状态与 Phase 8 Web 验收记录、Goal v0.8 和现有实现日志一致。

### Git
- 未 commit、未 tag、未 push。

---

## 2026-08-25 — Fitness H5 Demo 实现与验收完成

### 范围

- 关联 `REQ-FITNESS` 与 D-023；
- 在现有 unibest H5 壳和本地 FastAPI/PostgreSQL 中增加独立 Fitness 辅助工具，不接入 Jobs、Profile/Resume、Work、LangGraph 或模型 Provider。

### 已完成

- 数据库增加 `fitness_plan`、`fitness_exercise`、`fitness_session`、`fitness_set` 四张表和 Alembic migration `20260825_0003_fitness.py`；计划/动作使用归档删除，Session/Set 保存名称快照，Set 使用幂等标识，Active Session 和常用顺序/日期/进度查询均有约束或索引；
- Demo seed 初始化“胸、背、肩、臀腿”，并为“胸”提供杠铃卧推和上斜哑铃卧推；按每年数百次训练、数千条 Set 估算，十年以上仍为数万行级别，继续使用现有 PostgreSQL 足够；
- 后端建立独立 `backend/app/fitness/`，封装 models、schemas、repository、service、router 和 seed，通过 `/api/v1/fitness/*` 提供计划/动作、Session、Set、历史、日历和重量趋势接口；
- service 集中实现单一 Active Session、同计划恢复、异计划冲突、后端生成 Set 顺序、Active-only 写入和 Completed-only 统计；
- 首页增加静态模块注册表和 `04 健身记录 → /pages/fitness/index` 入口；Fitness 不进入主 TabBar；
- 前端 `modules/fitness` 负责 API、类型、状态和未提交草稿，`pages/fitness` 提供首页、计划训练、动作记录、历史、统计和计划管理六个页面；
- HTTP 封装新增 FastAPI 原始 JSON 模式且保留原业务信封模式；重量趋势使用 uni-app Canvas，不引入图表依赖；
- 浏览器验收中修复 `2.5 kg` 步进被取整和保存成功后草稿残留两个问题，草稿键升级为 `miniworld-fitness-draft-v2:*`。

### 验证

- 新 SQLite 执行 Alembic `upgrade → downgrade → upgrade`：通过；现有 PostgreSQL 容器迁移：通过；API 容器重建并在 `127.0.0.1:8000` 健康运行；
- `UV_CACHE_DIR=.cache/uv uv run --project backend pytest backend/tests -q`：27 passed；
- Fitness 相关 Ruff、Mypy、Ty：通过。包含原模板 Alembic 文件的扩展 Ruff 命令仍会报告其既有未使用 `os` 导入，不属于 Fitness 代码回归；
- `pnpm type-check`、`pnpm test:run`、Fitness/入口/HTTP 限定范围 ESLint、`pnpm build:h5`：通过；Shell 为 7 个测试文件、27 项测试；
- 全仓 `pnpm lint` 仍受上游 Shell 的 `package.json`、旧脚本、旧组件/测试既有 lint 问题影响；本轮变更范围 lint 为零错误，没有借 Fitness 任务清理上游无关文件；
- 浏览器实际录入杠铃卧推 `80×8、80×8、75×10`，上斜哑铃卧推 `25×10、25×10`；History 显示 2 个动作/5 组，2026-08-25 日历标记已训练，卧推进度最大 80 kg；
- 下一次“胸”训练显示上次卧推三组并默认带出 `75 kg × 10`，Fitness 首页能恢复新的空 Active Session；
- 桌面 `1440×900` 与手机 `390×844` 均无横向溢出，浏览器控制台无 warning/error，H5 当前可从 `http://127.0.0.1:9000/` 审阅。

### 参考审计与许可

- 只读审计 OpenWorkout `25e485766118fa0466cd6bdcaf9aeba3f629473f`（MIT）、Zenith Fitness `7b171a0ae73ce0d860dbaf1557002cae61c17694`（未发现根许可证）和 Forme `c1f583a76975521602136d38151f4666931ce345`（未发现根许可证）；
- 只采用模型和交互思想，没有复制源码或资源。

### 未完成

- Android 与微信小程序只保留 uni-app 结构兼容性；本轮没有安装原生工具链、配置 AppID、构建包或做真机验收；
- 本轮未创建 tag、未提交、未 push，也未操作真实个人材料或任何外部写入。

### Git

- 分支：`codex/bootstrap-langgraph`；T-015 工作树待用户决定提交边界；未 tag、未 push。

### 下一步

- 用户可在 `http://127.0.0.1:9000/` 从首页 `04 健身记录` 审阅 H5 Demo；跨端出包应作为独立任务分别补齐微信小程序和 Android 工具链及真机验收。

---

## 2026-08-26 — v0.9 Git 收口与远端发布

### 范围

- 收口 T-014 unibest Web Shell 与 T-015 Fitness H5 Demo 的已验证工作树；
- 只发布源码、测试、迁移、许可证、占位配置、产品文档与精简治理记录，不发布数据库、地图运行数据、构建产物、依赖目录、日志、密钥或真实个人材料。

### 已完成

- 确认远端 `origin` 为 `https://github.com/ZShining219/miniworld.git`，发布前远端没有任何 heads 或 tags；
- 增加 `.ai/runtime/windows/*.json` 忽略规则，新生成的本机 scope manifest 不进入 Git；既有已跟踪治理历史不做重写；
- 将 unibest Shell、Fitness 数据库/后端/前端、v0.9 Goal 和许可证记录收口为提交 `1de73ce feat: add multi-end shell and fitness demo`；
- 创建远端分支 `origin/codex/bootstrap-langgraph` 并建立 upstream；发布后远端与本地 commit SHA 均为 `1de73ceeea0025b04ad7992c6ee6131a99420d0b`。

### 验证

- 后端：27 项 Pytest 通过，Fitness 相关 Ruff 通过；
- unibest Shell：TypeScript、7 个测试文件/27 项测试和 H5 production build 通过；
- 索引级检查确认没有私钥、真实 API key、数据库、日志、地图运行数据或超过 1 MB 的新增 Git blob；`OPENAI_API_KEY=replace-locally` 与 `sk-example-value-1234567890` 仅为文档/安全测试占位；
- `git diff --cached --check`、`git fsck --no-dangling` 通过；
- scope guard 报告的范围外路径全部是已忽略的 H5 dist、node_modules 缓存、Pytest 缓存和 uni-app 自动生成文件，不是 Git 候选。

### 运行状态

- Docker Compose 的 PostgreSQL、FastAPI API、APScheduler Worker 和 React/Nginx 看板正在运行；
- `127.0.0.1:8000/api/v1/health` 与 `127.0.0.1:5173` 实测可访问；
- unibest H5 开发服务当前未运行，但 `pnpm dev:h5` 可恢复 `127.0.0.1:9000`；
- Tauri Radar 是按需启动的本机窗口，不作为常驻 Compose 服务。

### 未完成

- 远端仍没有 `main` 分支或 tag；本轮按当前分支原样发布，没有擅自创建、合并或改写 `main`；
- Android、微信小程序、真实远端模型、真实岗位地图、签名发布包仍需独立授权与验收。

---

## 2026-08-26 — 根 README 运行注册表与统一停服

### 范围

- 将所有已支持的长期运行单元、按任务最小组合、验证任务和停服边界注册到根 README；
- 停止当前所有 MiniWorld 服务，但保留 PostgreSQL 和上传数据卷。

### 已完成

- 注册 `RUN-DB`、`RUN-API`、`RUN-WORKER`、`RUN-REACT`、`RUN-H5` 和 `RUN-RADAR-NATIVE`，明确任务、依赖、启动命令、入口/健康检查、停止方式和验证状态；
- 明确浏览器 Radar 是 `RUN-REACT` 的 `/radar` 页面而非独立进程，Fitness H5 的正式读写依赖 API 与 PostgreSQL；
- 增加完整 Agent、后端/API、Fitness H5、浏览器 Radar 和原生 Radar 五种最小启动组合；
- 注册本地全量、Fitness 后端、H5、容器 Demo、全启动和 Lever Live 只读六类验证命令；
- 统一规定常规停服使用 `docker-compose down`，H5/Tauri 使用前台 `Ctrl-C`；`down -v` 仅允许在明确永久删除数据时使用。

### 停服结果

- `docker-compose down` 成功停止并移除 frontend、worker、api、db 四个容器及项目网络；
- 端口 5173、8000、9000 均无监听，未发现 MiniWorld Tauri Radar 或 H5 开发进程；
- `miniworld-agent_miniworld-db` 和 `miniworld-agent_miniworld-uploads` 两个 local volume 仍存在，业务数据与上传数据未删除。

### 验证

- `docker-compose config --services` 与注册表四个 Compose 服务一致；
- README 的运行 ID、验证 ID、按任务组合和停服章节均可检索；
- `git diff --check` 通过。

### Git

- 本轮形成单独本地文档/治理检查点；未获得新的远端写入指令，因此不执行额外 push。

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

## 2026-08-26 — T-019 Fitness 移动端训练流优化

### 变更
- 仅修改 unibest H5 前端：首页部位选择、部位详情动作管理、动作记录页的重量/次数与当日完成组呈现。
- 新增 `apps/miniworld-shell/src/pages/fitness/plan-preview.vue`，复用已有 Fitness API 支持任意部位进入、添加动作和移除动作；未修改后端接口、数据库或部署配置。
- 动作页将“今天已完成”前移，并将“当前调整”作为大尺寸主控区，保留上一次训练作为低优先级参考。

### 验证
- `cd apps/miniworld-shell && pnpm type-check` 通过。
- `cd apps/miniworld-shell && pnpm test:run`：27 passed。
- `cd apps/miniworld-shell && pnpm build:h5` 通过。
- 本地 H5 `http://127.0.0.1:9000/` 在 390×844 手机视口验证：首页、部位详情和动作记录页均正常渲染。

### 偏差与决策
- 部位详情页点击具体动作时会先复用现有“开始训练”接口，再直接进入该动作记录页；点击底部主按钮则进入本次训练动作列表。

### Git
- 分支：`codex/bootstrap-langgraph`；本轮未提交、未 push。

### 下一步
- 用户在手机端体验首页、部位详情和动作记录页后，再决定是否继续优化历史/统计页面。

## 2026-08-26 — T-020 进行中训练动作管理

### 变更
- 在“本次训练”页新增统一的动作管理入口；训练进行中可展开管理、添加动作或移除动作。
- 新增动作复用现有 `createExercise` API，完成后刷新 active session；服务端已有按当前计划动态返回动作的行为，因此未改后端。
- 保留当前训练的组数、已完成组记录和任意顺序进入动作记录的交互。

### 验证
- `cd apps/miniworld-shell && pnpm type-check` 通过。
- `cd apps/miniworld-shell && pnpm test:run`：27 passed。
- 本地 H5 390×844 视口已验证进行中训练页的管理展开、动作列表和添加表单呈现。

### Git
- 分支：`codex/bootstrap-langgraph`；本轮未提交、未 push。

### 下一步
- 用户实际新增一个训练中动作，确认手机端输入习惯后再微调表单默认值或快捷操作。

## 2026-08-26 — T-021 Fitness 数据安全与输入标注

### 变更
- 进行中训练的动作管理改为追加优先：移除入口不再显示，避免误操作归档当前动作。
- 动作管理表单明确标注“动作名称”“默认重量（kg）”“默认次数（次）”。
- 部位详情保留显式“停用”操作，并提示停用只影响今后计划、不会删除历史训练记录。
- 动作记录成功后显示“已保存到本地数据库”；请求失败时继续保留草稿输入，允许重试。

### 验证
- `cd apps/miniworld-shell && pnpm type-check` 通过。
- `cd apps/miniworld-shell && pnpm test:run`：27 passed。
- 本地 H5 390×844 视口验证进行中训练页标签、追加表单和安全提示。

### Git
- 分支：`codex/bootstrap-langgraph`；本轮未提交、未 push。

### 下一步
- 用户实际体验追加动作和完成一组后的保存反馈，再讨论历史/统计的数据呈现优化。

## 2026-08-26 — T-022 Fitness 前端优化生产发布

### 变更
- 完成 T-019 至 T-021 的 Fitness H5 前端优化收口，未修改后端、API 合约或数据库结构。
- 生产发布固定到 commit `d5a56e4f3c7064b1e445965f12a153752dba8564`，通过既有 `scripts/deploy-production.sh` 部署。

### 验证
- 生产静态检查、TypeScript、27 项前端单测、H5 production build、暂存区 secret/PII 与文件大小扫描均通过。
- GitHub `origin/codex/bootstrap-langgraph` 与本地发布 SHA 一致。
- 服务器 `/srv/miniworld-deployed-sha` 与发布 SHA 一致；生产 API、PostgreSQL、Caddy/H5 容器均为 healthy。
- 未认证 HTTPS 根地址、Fitness API 和文档路径均返回 `401`；部署脚本内部健康检查通过。

### Git
- 提交：`d5a56e4 feat: harden fitness mobile logging flow`
- 已推送并部署；工作区仅保留本次治理记录变更，待下一次治理收口提交。

### 下一步
- 使用手机验证线上新增动作、训练中追加动作和“已保存到本地数据库”反馈；之后再决定是否优化历史/统计页面。

## 2026-08-27 — T-023 Fitness 数据保护回归修复

### 问题
- 功能回归发现动作记录页仍暴露“删除已保存组”按钮，与训练过程避免误清理数据的要求冲突。

### 修复
- 移除动作记录页已保存组的删除入口，完成组改为只读展示。
- 保留现有保存成功提示、失败重试和草稿输入保留机制；未修改后端、API 合约或数据库结构。

### 验证
- 本地 API 与 PostgreSQL healthy，active session 查询正常。
- 定向 ESLint、TypeScript、27 项前端单测、生产静态检查、H5 production build 通过。
- 390×844 浏览器回归确认保存组无删除控件。

### 下一步
- 发布固定 SHA 到 GitHub 并更新生产服务器，部署后复测认证边界与容器健康。

## 2026-08-27 — T-023 Fitness 数据保护 bug 修复与生产发布

### 问题与修复
- 功能回归发现动作记录页仍允许删除已保存训练组，存在训练过程中误清理数据的风险。
- 移除该删除入口，已保存组改为只读；保存成功提示、失败重试和草稿保留继续有效。

### 验证与发布
- active session、API 与 PostgreSQL 健康检查通过。
- 定向 ESLint、TypeScript、27 项前端测试、生产静态检查和 H5 production build 通过。
- 390×844 浏览器回归确认已保存组不再显示删除控件。
- 提交 `7a5934db6a5d4382088cc3556c6719eace609edf` 已推送并通过生产部署脚本发布。
- 服务器部署 SHA 与本地/远端一致；API、数据库、Caddy/H5 容器均 healthy；未认证根、Fitness API、文档均返回 `401`。

## 2026-08-27 — T-024 Fitness 停用动作后新增冲突修复

### 问题与复现
- 生产手机请求已正常认证并到达 `POST /api/v1/fitness/exercises`，但在同一部位存在已停用动作时返回 `409 Exercise order already exists`。
- 回归用例稳定复现“空部位新增动作 → 停用该动作 → 再新增动作”的冲突：停用记录仍保留并占用 `sort_order=0`，旧实现却只按有效动作计算下一个排序号，再次分配了 `0`。

### 修复
- 自动新增动作时按同一部位的全部动作（含已停用记录）计算历史最大排序号，从下一个未占用值继续分配。
- 动作重新排序时将有效动作排在同一部位全部停用动作的最大排序号之后，避免管理页面重新排序时再次与历史记录冲突。
- 不修改数据库结构，不删除、恢复或改写任何停用动作及历史训练组。

### 验证
- 修复前定向回归：第二次新增返回 `409`，用例按预期失败。
- 修复后定向回归：`1 passed`；第二个动作以 `sort_order=1` 创建，并可正常重新排序。
- `uv run pytest backend/tests/test_fitness.py -q`：`6 passed`。
- `uv run pytest backend/tests -q`：`28 passed`。
- `uv run ruff check backend/app/fitness backend/tests/test_fitness.py`：通过。
- `uv run mypy backend/app/fitness backend/tests/test_fitness.py`：通过。

### Git 与部署
- T-024 任务关闭时尚未提交、未 push、未部署；后续由 T-025 完成发布。

## 2026-08-27 — T-025 Fitness 动作排序修复生产发布

### 发布
- 修复提交 `aca89ad71f6aa5e3f51f833bc91e73a256045ab4` 已推送，包含停用动作后新增及重新排序冲突修复。
- 发布核验发现既有部署脚本的备份预检未传入 `RELEASE_SHA`，导致 Compose 探测失败后跳过自动备份；生产数据未受影响，并立即手工补做备份。
- 修复部署脚本并增加静态回归检查，最终提交 `80542f203d2637e39d353cc76f2cb0c550d331cd` 已推送并部署。

### 验证
- 发布前：后端 `28 passed`，Fitness Ruff/Mypy、生产部署静态契约、Shell 语法、暂存区 secret/PII 与文件范围检查通过。
- 修复后的部署脚本对同一 SHA 执行幂等发布时，自动备份数量由 3 增至 4，最新备份为 `fitness-20260827T015642Z-80542f203d26.dump`。
- 服务器部署文件、服务器仓库、本地和远端均包含最终 SHA `80542f203d2637e39d353cc76f2cb0c550d331cd`。
- PostgreSQL、FastAPI 和 Caddy/H5 均为 `running/healthy`；API 内部健康检查返回 `ok`。
- 生产数据只读计数在发布前后保持 4 个部位、3 个动作、1 个停用动作、3 次训练、8 个训练组；未在生产创建或删除测试动作。
- 未认证根地址、Fitness API 和文档路径均返回 `401`。

## 2026-08-27 — T-026 Fitness 训练部位组件与长按排序

### 变更
- 将首页训练部位拆分为无 API 依赖的 `FitnessPlanCard` 和负责手势编排的 `ReorderablePlanList`；移除 `01/02` 等顺序编号，保留名称、动作数量、进入提示和低调拖动点阵。
- 整张卡片轻点进入，静止长按 350ms 后激活拖动；长按前移动超过 8px 按页面滚动处理。被拖卡片中心跨过相邻卡片中线时让位，松手仅提交一次，拖动后的点击被抑制，取消、隐藏页面或计划数据刷新时清理状态。
- Fitness Store 复用现有 `PUT /api/v1/fitness/plans/order`：本地乐观排序，服务端响应校准，失败恢复原顺序并显示“排序保存失败，已恢复”。
- 计划管理页移除训练部位的上下移动按钮；动作的上下移动按钮保持不变。未修改后端接口、数据库结构、训练历史或进行中训练逻辑。

### 验证
- `pnpm type-check`、限定范围 ESLint 和 `pnpm build:h5` 通过。
- `pnpm test:run`：9 个测试文件、39 项测试通过；覆盖移动算法、短按、滚动阈值、卡片中心越线、长按单次提交、点击抑制、取消/刷新复位、Store 成功校准、失败回滚与并发锁定。
- `uv run pytest backend/tests/test_fitness.py -q`：6 passed，现有后端排序与历史保护行为保持通过。
- 本地 API 临时交换前两个部位后刷新确认持久化，随后恢复为“胸 → 背 → 肩 → 臀腿”。
- 本地 H5 在 390×844 与 1440×900 验证：首页无部位编号、无横向溢出、短按正常进入，控制台无 warning/error；管理页部位排序按钮为 0，动作排序按钮为 6。

### Git 与部署
- 功能提交 `3264bbfb7511dad9787272bb638bf398aa33a9a4` 已推送到 `origin/codex/bootstrap-langgraph` 并由生产部署脚本发布；脚本在切换代码前创建自动备份 `fitness-20260827T025807Z-80542f203d26.dump`。
- 第一次部署调用因手工补全了错误的 40 位 SHA，在服务端 commit 存在性检查阶段安全中止；未切换代码、未执行备份或数据库操作。随后使用 `git rev-parse` 与远端分支一致的完整 SHA 成功发布。
- 部署后服务器记录 SHA 与仓库 HEAD 均为 `3264bbfb7511dad9787272bb638bf398aa33a9a4`；PostgreSQL、FastAPI、Caddy/H5 均为 `running/healthy`，内部健康检查返回 `ok`。
- 生产数据只读计数在部署前后保持 4 个部位、2 个有效动作、1 个停用动作、3 次训练、8 个训练组；未通过生产 API 改动用户部位顺序。
- 未认证根页面、Fitness API 和 docs 均返回 `401`；生产备份数量从 3 增至 4。

## 2026-08-27 — T-027 Fitness 前端组件边界重构

### 评估与边界
- 抽取跨页面稳定且重复的展示职责：`FitnessPageShell`、`FitnessSectionHeader`、`ExerciseDefaultsFields`、`FitnessExerciseRow`、`WorkoutSetList`、`FitnessChoiceChips`、`FitnessPlanEditorRow` 和 `FitnessExerciseEditorRow`。
- 首页日期、历史训练详情和统计日历属于单页语义，继续保留在对应页面；API、Store、训练状态、保存/归档编排和数据库均未进入展示组件。
- 七个 Fitness 页面统一使用页面框架；部位页和进行中训练共用动作默认值表单与动作行；动作记录页共用训练组列表；统计页共用选择 chips；设置页计划/动作编辑行独立封装。
- `FitnessPageShell` 统一加载 Fitness 全局设计样式，页面与子组件只保留自身 scoped 样式，避免组件拆分后重复复制整套 SCSS。

### 可读性与数据安全
- 设置页所有计划和动作字段明确显示“计划名称 / 动作名称 / 默认重量（kg）/ 默认次数（次）”；排序、保存、归档仍通过显式事件交给页面调用既有 API。
- 展示组件不直接读取 API、不写 Store、不操作草稿或数据库；训练中追加动作、保存训练组、历史只读和部位排序语义保持不变。

### 验证
- `pnpm test:run`：11 个测试文件、47 项测试通过；新增 8 项组件契约测试，覆盖页面/区块标题、筛选状态、字段标签与数值回传、动作选择与独立停用事件、训练组格式、计划/动作编辑事件与排序边界。
- `pnpm type-check`、限定 Fitness 页面/组件 ESLint、`pnpm build:h5` 和 `git diff --check` 通过。
- 本地 H5 在 390×844 验证七个页面无横向溢出：首页 4 张部位卡、部位页 3 个动作、进行中训练 3 个动作并可展开管理、动作页 2 个步进器与训练组列表、统计 2 组选择器、历史 2 条记录、管理页 4 个计划与 3 个动作编辑器。
- 管理页和训练中追加表单均显示完整字段标签；1440×900 下首页和管理页保持 680px 内容栏；浏览器控制台无 warning/error。

### 发布状态
- 本地提交 `755b14de6577ce22911116bf5f87facd9140a9c1` 已形成；本轮只做前端组件重构和本地验证，未修改后端/API/数据库，未 push，未部署生产。

## 2026-08-27 — T-028 Fitness 前端组件版生产发布

### 发布前验证
- `pnpm test:run`：11 个测试文件、47 项测试通过；`pnpm type-check`、限定 Fitness ESLint、`pnpm build:h5` 和生产部署契约检查通过。
- `uv run pytest backend/tests/test_fitness.py -q`：6 passed，现有后端排序接口和历史保护继续通过。
- 390×844 内置浏览器验收确认 4 张部位卡无数字编号、提示及可访问标签完整、轻点进入正确、无横向溢出且控制台无 warning/error。
- 推送差异的文件范围、体积、secret/PII 与禁止文件类型检查通过。

### Git 与部署
- 前端重构提交 `755b14de6577ce22911116bf5f87facd9140a9c1` 及治理提交已推送，生产固定发布 SHA 为 `3d0e02a9c60d3743c308c91c56e1add431099bce`。
- 部署脚本在切换前创建自动备份 `fitness-20260827T035941Z-3264bbfb7511.dump`，备份数从 5 增至 6。
- 服务器记录 SHA 和仓库 HEAD 均为 `3d0e02a9c60d3743c308c91c56e1add431099bce`；PostgreSQL、FastAPI 和 Caddy/H5 均为 `running/healthy`。
- 生产数据只读计数在发布前后保持 4 个部位、7 个有效动作、1 个停用动作、4 次训练和 8 个训练组；未通过生产 API 修改部位顺序或其他 Fitness 数据。
- 未认证根页面、Fitness API 和 docs 均返回 `401`。

## 2026-08-27 — T-029 Fitness 真实手机首页布局修复

### 问题与修复
- 用户提供的真实手机截图显示首页“记录 / 历史 / 统计 / 管理”区域发生纵向挤压，计划卡片文案和右侧操作缺少稳定的窄屏约束。
- 记录区改为专用单行 Flex 布局，标题不参与收缩，三个导航入口保持同一基线；360px 以下使用更紧凑间距。
- 计划卡片正文增加明确的可收缩、换行和溢出规则，避免较长计划名或动作数量挤压拖动点和进入入口。
- 未修改 API、Store、训练业务逻辑、后端或数据库。

### 验证与发布状态
- `pnpm type-check` 通过；`pnpm test:run` 为 11 个文件、47 项测试通过；`pnpm build:h5` 通过。
- 限定前端 ESLint 和 `git diff --check` 通过。
- 390×844 与 360×800 H5 浏览器回归确认记录导航保持同一行；360px 下 `scrollWidth=innerWidth=360`，控制台无 warning/error。
- 修复已提交为 `7ccb86e`，尚未 push 或部署；线上仍运行 `3d0e02a9c60d3743c308c91c56e1add431099bce`，需用户明确确认生产发布。

## 2026-08-27 — T-031 Fitness 训练中交互增强

### 数据库
- 新增 Alembic migration `20260827_0004_fitness_weight_step.py`，为 `fitness_exercise` 增加 `NUMERIC(4,2) NOT NULL DEFAULT 2.50` 的 `weight_step`，并限制为 `1 / 2 / 2.5 / 5`。
- SQLite 与 PostgreSQL 共用同一模型约束；一次性 SQLite 迁移验证确认旧动作回填 `2.5`、档位 `3` 被拒绝、downgrade 删除字段。
- Session、Set 和历史表未改动；档位不写入 Set 快照，历史重量仍以 Set 实际值为准。

### 后端
- `backend/app/fitness/` 继续独立封装 Fitness；`FitnessExercise` 模型及 Create/Update/Public schema 新增 `weightStep`，创建默认 `2.5`，非法档位返回 `422`。
- 复用现有动作更新接口持久化档位；SessionDetail 与 ExerciseLog 内的动作对象自动返回 `weightStep`。
- Session、Set、历史、统计 API 和单 Active Session 约束均未改变。

### 前端
- 七个 Fitness H5 页面统一使用训练状态条，展示今日训练中、跨日未结束、今日已完成或今日未开始；首页旧的重复继续区块已移除。
- 动作页新增同部位横向动作条，按计划顺序显示“今日 X 组”，使用 `redirectTo` 切换并在 Set/档位保存期间禁用。
- 重量组件支持 `0–9999`、最多两位小数的手动输入，以及竖排 `1 / 2 / 2.5 / 5` 档位；加减采用整数化计算，次数组件继续使用固定步长 `1`。
- 每个动作的未提交草稿独立保留重量、次数和失败请求 ID；同一幂等请求的返回 Set 不会在本地列表和计数重复追加。

### 业务逻辑
- 同部位动作可任意交替训练；切换只替换当前页面，不结束 Session、不创建 Set。
- Active Session 优先于今日已完成状态；跨日 Active Session 明确标记为未结束旧训练。
- 完成一组后同步当前动作、横向动作条、Session 总组数和全局状态条；档位保存失败时回滚 UI，不影响已保存 Set。

### 验证结果
- `uv run pytest backend/tests -q`：`28 passed`；Fitness 定向测试 `6 passed`。
- Fitness Ruff 与 Mypy 通过；`pnpm test:run`：13 个文件、`62 passed`；TypeScript、Fitness ESLint 和 H5 production build 通过。
- 360×800、390×844 与桌面视口验证七个 Fitness 页面无横向溢出、无控制台错误；档位触控区约 `45.75 × 44.64px`，手动输入 `82.25`、`1 kg` 档位的 `75 → 76` 和跨动作草稿恢复均通过。
- 浏览器验收未新增 Set，动作档位已恢复为 `2.5`；本地正式训练记录未被测试改写。

### 未完成事项
- 本轮只完成 H5 实现与本地验收；Android 和微信小程序仍只具备结构兼容性。
- 未 push、未部署生产；真实手机复测需在用户另行授权发布后进行。

## 2026-08-28 — T-032 Fitness 动作重量趋势图

### 调研与依赖
- 按用户确认接入成熟组件，采用 DCloud `lime-echart` 2.0.7；源码固定于 Gitee commit `88bdd1dd3ccc541c8d645e464ab04264dbd68ca1`，仅导入 `l-echart.vue`、`canvas.js` 和 `utils.js`。
- 使用 npm Apache ECharts `5.4.3`，H5 Vue 3 采用官方预打包 `echarts/dist/echarts.esm.js` 入口以兼容 uni-app Rollup；来源和 MIT/Apache-2.0 归属追加到 `THIRD_PARTY_NOTICES.md`。

### 数据库与后端
- 未新增表或迁移；复用现有 Fitness Set/Completed Session 数据。
- `GET /api/v1/fitness/stats/exercises/{exercise_id}/progress?mode=set` 返回完成组的日期、时间、组序、重量和次数，按远到近的时间顺序排列。
- `mode=day` 按 `workout_date` 聚合平均、最低、最高重量、组数和训练次数，仅统计 Completed Session；不传 `mode` 保留旧的最大重量响应兼容。

### 前端与业务
- 新增 `FitnessProgressChart` 与纯函数 option builder，统计页增加按天/按次数和折线/柱状切换；默认按天折线。
- 按次数横轴展示日期与组序，按天横轴展示日期；Tooltip 分别显示组重量×次数或日均/范围/组数；ECharts `dataZoom` 提供较多历史点的时间轴缩放。
- 正式历史仍来自 PostgreSQL；图表组件只接收页面传入的数据，不读取 API、Store 或本地 storage。

### 验证与边界
- `uv run pytest backend/tests/test_fitness.py -q`: 6 passed；覆盖旧兼容响应、按组、按天聚合和非法 mode 422。
- `uv run ruff check ...`、`uv run mypy ...`、`pnpm test:run`（14 文件、65 tests）、`pnpm type-check` 和 Fitness ESLint 全部通过。
- `pnpm build:h5` 通过；初始 ECharts 源入口曾触发 zrender 解析错误，改用预打包 ESM 后构建成功。
- 本地 API 写入临时 SQLite 演示数据后，浏览器统计页在桌面和 360×800 视口验证了真实 Canvas、按次/柱状切换、无横向溢出（Canvas 约 314px）和无控制台错误；临时数据库已移除，未修改正式训练库。
- 本轮只完成 H5；Android 与微信小程序保持结构兼容，不宣称已验收；未 push、未部署生产。
- 功能已本地提交为 `13e8333842411dd8085932c28c6591a855f6133a`；生产仍运行 `3d0e02a9c60d3743c308c91c56e1add431099bce`。

## 2026-09-03 — T-033 Fitness 已验证更新生产发布

### 发布授权与预检
- 用户明确要求将现有更新提交并推送到 GitHub，同时更新生产服务器；本轮授权覆盖 T-029、T-031、T-032 及 `weight_step` 迁移的生产发布。
- 发布前生产固定在 `3d0e02a9c60d3743c308c91c56e1add431099bce`；PostgreSQL、FastAPI、Caddy/H5 均为 `running/healthy`，Fitness 数据只读计数为 4 个计划、8 个动作、5 次训练和 32 个训练组，已有 13 份备份。
- 本地后端 `28 passed`；前端 14 个测试文件、`65 passed`；TypeScript 与 H5 production build 通过。
- 生产部署静态契约、Shell 语法、Git 连通性、`git diff --check`、推送文件类型/体积和凭据候选扫描通过；49 个待推送文件中无数据库、日志、私钥、真实环境文件或超过 1 MiB 的文件。

### 发布状态
- 发布提交 `542b15842c2c4e2811bd9e29c532c880e773e2e2` 已推送到 GitHub `origin/codex/bootstrap-langgraph`。
- 服务器已完成自动备份 `fitness-20260903T130007Z-3d0e02a9c60d.dump`，备份总数由 13 增至 14；API 与 H5 镜像构建、Compose 切换和 Alembic 迁移均通过。
- 生产 `/srv/miniworld-deployed-sha`、服务器仓库 HEAD 和已部署镜像均固定为 `542b15842c2c4e2811bd9e29c532c880e773e2e2`。
- PostgreSQL、FastAPI 和 Caddy/H5 均为 `running/healthy`；API 健康检查返回 `ok`；Alembic 当前为 `20260827_0004 (head)`，`fitness_exercise.weight_step` 为 `numeric NOT NULL DEFAULT 2.50`。
- 生产 Fitness 只读计数发布前后保持 4 个计划、8 个动作、5 次训练和 32 个训练组；未写入训练数据。
- 未认证 `/`、`/fg-api/api/v1/fitness/plans`、`/api/v1/health` 和 `/docs` 均返回 `401`；生产备份定时器与 fail2ban 均为 active。
- 该发布包含 T-029 手机布局修复、T-031 训练交互与 `weight_step` 迁移、T-032 趋势图；Android/微信小程序和真实手机复测仍未验收。
- 为使服务器部署记录与 GitHub 最新发布记录一致，随后将生产再次固定到治理提交 `6708dfecc757738976079c81c50fea7213973452`；缓存构建和健康检查通过，并新增安全备份 `fitness-20260903T130745Z-542b15842c2c.dump`，备份总数为 15。最终只读计数仍为 4/8/5/32，三个容器均 healthy。

## 2026-09-03 — T-034 前端呈现硬性规则

### 原因
- 真实手机截图证明既有“桌面浏览器窄视口、无横向溢出、控制台无错误”不足以代表移动端视觉验收；Fitness 暴露出手写通用控件、任意 `rpx` 字号、表单挤压、状态重复和空计划训练死路。
- 仓库虽然使用 unibest 壳，但 `apps/miniworld-shell/package.json` 没有其当前默认推荐的 Wot UI；Fitness 通用呈现主要由自定义 Vue/SCSS 承担。PC React 看板同样缺少成熟的通用组件体系。

### 决策与规则
- 新增 `goal/frontend-presentation-rules.md`，以“必须/禁止/例外”定义手机端 Wot UI 2、PC 端 Ant Design/ProComponents、设计令牌、六类页面模板、状态矩阵、响应式、输入、可访问性、自动截图回归和真实设备验收门。
- 根 `AGENTS.md` 增加前端强制入口；任何前端任务必须先读规则，未获得适用证据时不得标记 verified、push 或 deploy。
- 明确桌面视口模拟只能做预检；涉及结构、表单、响应式、手势、Canvas/图表或主题的移动端变更，生产发布前必须记录真实设备、截图、系统字体、浏览器底栏和虚拟键盘结果。
- 后续手机呈现先接入 `@wot-ui/ui` 2.x 与项目主题，不继续给现有手写 SCSS 逐页打补丁；PC 保留 React/Vite，只在后续页面工作中渐进接入 Ant Design，不做无授权的构建系统重写。

### 验证与边界
- 规则文件、AGENTS 入口、Goal 索引、计划与 Accepted 技术决策已互相链接；本轮只修改文档与治理状态，不修改前端源码、API、数据库或生产服务器。
- Wot UI/Ant Design 版本将在实际接入任务中固定并完成许可证、构建、体积和平台验证；本轮不把“已选型”误报为“已接入”。

## 2026-09-03 — T-035 Fitness H5 呈现体系重构

### 范围与实现
- 仅修改 `apps/miniworld-shell` 的 Fitness H5 呈现、共享组件、测试与主题；未修改 Fitness API、Store、后端、数据库、Jobs/Profile/Work 或生产服务器。
- 固定 `@wot-ui/ui@2.3.2`，采用 unibest 官方 Wot UI 2 resolver 形式；`pages.config.ts` 使用 `^wd-(.*)` easycom，`vite.config.ts` 通过 `WotResolver()` 完成运行时解析，许可证已追加到 `THIRD_PARTY_NOTICES.md`。
- 新增 `src/style/theme.scss` 作为唯一主题入口：语义颜色、有限间距、字号层级、触控尺寸、圆角、阴影、系统字体、安全区和 H5 `text-size-adjust` 均集中定义；Fitness 页面与组件改为引用令牌，去除页面级裸通用控件、任意 `rpx` 字号、负字距和装饰性渐变背景。
- 七个页面按列表、详情、任务、统计和设置模板统一使用 `FitnessPageShell`、状态条、Wot UI 按钮/输入/空态/加载态和领域组件；空计划不能开始训练、Active Session 不显示冲突的开始入口、无动作 Active Session 可添加动作继续，结束训练独立为危险区并二次确认。
- 添加/编辑表单改为明确展开区；训练动作切换、重量/次数输入、增减档位、历史只读记录和趋势图保持既有数据语义，正式训练数据仍只来自 PostgreSQL。

### 类型兼容边界
- Wot UI 2.3.2 上游 `wd-button.vue` 的微信 `ButtonOpenType` 与当前 uni 类型对 `getRealtimePhoneNumber` 的定义不兼容，`vue-tsc` 会在上游 SFC 内报错。未修改 `node_modules` 或上游包；项目以局部 `GlobalComponents` any 声明承接实际使用组件，并在 `tsconfig.json` 排除自动生成的 `src/types/components.d.ts`，避免类型检查再次深入该上游 SFC。运行时仍由官方 resolver 加载实际组件。
- 该折中仅解决当前类型检查边界，未来 App/小程序构建必须另行验证；不得将其表述为所有目标平台已兼容。

### 验证证据
- `pnpm type-check`：通过；`pnpm test:run`：14 个测试文件、65 项测试通过；`pnpm eslint src/pages/fitness src/modules/fitness --ext .ts,.vue`：通过；`pnpm build:h5`：通过；`git diff --check`：通过。
- Playwright mock API 状态回归覆盖正常首页、空计划、正常计划详情、进行中训练、无动作进行中 Session、动作记录和统计页；截图保存于 `output/playwright/fitness-*-{320,360,390,430,1280,1440}.png` 及对应状态文件。320、360、390、430、1280、1440 CSS px 均满足 `scrollWidth === clientWidth`，控制台无新增 error/warning。
- 人工审阅 390px 正常首页、计划详情、进行中训练、无动作进行中 Session、动作记录、统计页和 1440px 首页截图；布局层级、危险操作降权、图表可见性和单一主要操作符合当前规则。

### 未完成与发布边界
- 本轮达到“本地实现完成，等待真实手机视觉验收”；尚未完成真实 iOS/Android 手机、系统字体放大、浏览器底栏收缩、虚拟键盘和实际触控验收，因此 ISS-016 仅缓解，不能标记为移动端最终验证。
- 未 push、未部署生产；生产仍保持 T-033 固定 SHA。后续发布必须在真实手机证据和用户明确发布授权后另行执行。

## 2026-09-03 — T-036 Fitness Coach Agent 最小服务器纵切面

### 范围

- 关联 `REQ-FITNESS`、T-036 与 T-027；
- 在现有 Fitness 后端增加独立 `FitnessCoachGraph`、DeepSeek Provider 配置入口、只读分析工具、结构化建议表和 API；不改 Jobs、Profile/Resume、Work 的业务数据或 Graph。

### 已完成

- 新增 `backend/app/fitness/coach/`：Provider、工具、Graph、Schema 和 Service；Graph 节点为 `load_fitness_context` → `agent_select_tools` → `execute_read_only_tools` → `agent_recommend`；
- DeepSeek 使用 OpenAI-compatible Chat Completions JSON 输出，Provider 默认模型为 `deepseek-chat`，密钥只从 `FITNESS_AGENT_API_KEY` 读取，请求超时固定为可配置的 30 秒；未配置时运行状态为 `awaiting_configuration`；
- 训练完成接口后台触发一次 Agent；同时提供 `POST /api/v1/fitness/coach/analyze` 手动入口和 `GET /api/v1/fitness/coach/recommendations` 查询入口；
- 新增 `fitness_coach_recommendation` 表和 Alembic migration `20260903_0005_fitness_coach.py`；建议只保存结构化动作、原因、证据、置信度、Provider/模型和复核时机；
- Agent 只能执行 `completed_session` 与 `exercise_history` 两个 Fitness 只读工具；未完成训练、目标动作越界、引用未执行工具、缺少目标重量/次数、非法结构化结果或 Provider 配置缺失均不会写入 Recommendation；每个 Session 最多保存一条正式建议；

### 受控验证

- `cd backend && uv run pytest tests/test_fitness_coach.py -q`：7 passed；
- 测试覆盖自动触发并保存 Agent Run/Recommendation/ModelCallAudit、无 DeepSeek Key 的 `awaiting_configuration`、越界动作建议的安全拒绝、未完成 Session 拒绝、动作数值约束和 DeepSeek OpenAI-compatible 请求/JSON 解析契约；测试 Provider 与 DeepSeek 客户端均为受控内存替身，不发起外部网络请求；
- `./scripts/test-local.sh`：通过；后端 35 项测试、完整 Ruff/Mypy/Ty、React 构建与 9 项 Playwright 测试均通过，T-037 记录的 ISS-017 已解决；
- 空 SQLite 数据库执行 `uv run alembic upgrade head` 并读取 `alembic current`：成功升级到 `20260903_0005 (head)`；`scripts/test-production-deployment.sh`：通过；
- 原有 Fitness 测试包含在完整测试中；训练 Session/Set 数量在 Agent 分析前后保持不变；

### 未完成与下一步

- 未配置真实 DeepSeek Key，未执行真实模型调用；Provider 具体质量、延迟和成本留待用户明日确认后验证；
- 本轮未修改前端呈现，建议卡片接入待 Fitness UI 重构任务完成后单独实施；

### 生产 API-only 发布

- 功能提交 `824060dbbe736b63486c8ea5195260b3b9c7b083` 已 push 到 `origin/codex/bootstrap-langgraph`；发布前自动备份为 `fitness-20260903T160852Z-6095d7a08ed3.dump`；
- 生产仓库检出的 API SHA 与 `/srv/miniworld-api-deployed-sha` 均为 `824060dbbe736b63486c8ea5195260b3b9c7b083`；仅重建并替换 API，Web 容器继续运行 `miniworld-fitness-web:6095d7a08ed3aeb4413b214afcdfd80cb97bfb92`，未触发新的前端发布；
- API、DB、Web 均 healthy；PostgreSQL migration 为 `20260903_0005 (head)`；Fitness 行数在发布前后保持 plan/exercise/session/set=`4/8/6/32`，Recommendation=0、Fitness Coach Run=0；
- 生产配置只读核验为 `deepseek|deepseek-chat|key_configured=False|timeout=30.0`；无 Key 的 Provider 状态为 `FITNESS_AGENT_API_KEY is not configured`，未发起真实模型请求；
- 内部只读 `GET /api/v1/fitness/coach/recommendations` 返回 `200 []`；公开根路径和公开 Coach 查询均继续返回 `401`；
- 发布时发现 `git fetch origin <branch>` 只更新 `FETCH_HEAD`、未推进远端跟踪引用；`scripts/deploy-production.sh` 已改为显式分支 refspec，并由 `scripts/test-production-deployment.sh` 固化检查。

## 2026-09-03 — T-037 GitHub Actions CI 与本地链路验证

### 范围与实现

- 新增 `.github/workflows/ci.yml`，覆盖分支 push、Pull Request 和手动触发；工作流拆分为 Backend、React、H5 Shell、Sensitive File Scan 和 Compose Integration 五个 Job，集成门通过 `needs` 等待前四道门完成后再执行。
- Backend Job 复用 `uv.lock` 和现有 `pytest`、Ruff、Mypy、Ty 命令；React Job 固定 Bun 1.3.13，执行构建、Biome 和 9 项 Playwright；H5 Job 固定 pnpm 10.10.0/Node 20，执行类型检查、65 项测试和 H5 production build。
- 所有第三方 Action 固定到已解析的 commit SHA，checkout 设置 `persist-credentials: false`，工作流权限仅保留 `contents: read`，并使用并发取消避免旧提交占用 Runner。
- 新增 `scripts/ci/check-sensitive-files.sh`，阻断 Git 索引中的运行数据/环境文件、私钥和非占位凭据格式；新增 `scripts/ci/docker-compose`，兼容本机旧版 `docker-compose` 与 GitHub Runner 的 `docker compose` 插件。
- `scripts/verify-demo.sh` 的 Alembic 检查改为默认读取源码中的最新 revision，同时保留 `EXPECTED_ALEMBIC_VERSION` 覆盖入口，避免新增合法迁移后 CI 固定比较旧版本。
- CI 不包含生产部署；真实模型、个人材料、精确住址和外部写入仍不进入自动化链路。生产发布继续使用独立的人工确认、备份、迁移、健康检查和回滚流程。

### 验证证据

- `scripts/ci/check-sensitive-files.sh`：通过；未发现被 Git 跟踪的运行数据、私钥或非占位 token。
- `UV_CACHE_DIR=.cache/uv uvx --from zizmor==1.28.0 zizmor .github/workflows/ci.yml`：通过，`No findings to report`。
- H5：`pnpm type-check`、`pnpm test:run`（14 个测试文件、65 项）和 `pnpm build:h5` 通过。
- React：生产构建、Biome（保留仓库既有 8 条 CSS warning）和 Playwright 9 项 E2E 通过。
- Compose 集成：`scripts/ci/docker-compose up -d --build` 后执行 `PATH="$PWD/scripts/ci:$PATH" ./scripts/verify-demo.sh` 通过；输出为 `jobs=3 facts=110 reports=25 checkpoints=788`，包含三 Graph、Worker 定时、checkpoint 恢复、重启持久性、回环端口和位置隐私检查。
- 后端完整 `./scripts/test-local.sh` 在当前工作树的 `ty check` 阶段仍有两条来自并行 T-036 `backend/app/fitness/coach/graph.py` 与 `tools.py` 的字典索引类型错误；pytest 31 项、Ruff 和 Mypy 已通过。T-036 修复该独立问题后，CI 五道门可达到全绿，T-037 不绕过 Ty 门。
- `git diff --check`、Shell 语法检查和工作流 YAML 解析通过。

### Git 与边界

- T-037 仅修改 CI 工作流、CI 辅助脚本、Demo 验收脚本、README、实施日志和治理池；未暂存或提交 T-036 的后端、Goal、生产部署和环境配置改动。
- 未执行 GitHub push、生产部署或任何外部写入；本地 Compose 临时数据在验证后按 CI 等价流程清理。

## 2026-09-04 — T-038 CI clean-runner follow-up

### 问题与修复

- 最终 CI 提交 `513948a35d05fcad651f18e6dc0424a07e38941b` 的 React Job 从仓库根目录使用 `bun run --filter frontend`，但根 workspace 未注册该包；H5 Job 在干净 Runner 先执行 `vue-tsc`，缺少 unibest 自动生成的 `src/types` 声明。
- React Job 已切换 `working-directory: frontend` 并执行包内 `bun run build/lint/test`；H5 Job 调整为先 `pnpm build:h5` 生成页面与类型声明，再执行 `pnpm type-check` 和 `pnpm test:run`。

### 受控验证

- 在本地移走全部忽略的 H5 生成物后执行 `pnpm init-baseFiles && pnpm build:h5 && pnpm type-check`：通过；React 包内 `bun run build && bun run lint && bun run test`：9 项 Playwright 通过。
- 修复仅涉及 CI 编排与治理记录，不改变 Fitness Agent、生产容器或用户数据；等待新的 GitHub Actions 运行确认。
- React 失败的第二个原因是 Radar E2E 依赖被 Git 忽略的 `runtime-data/maps/demo-firenze.pmtiles`；CI 已在 Playwright 前调用现有带 SHA-256 校验的 `scripts/fetch-radar-demo-map.sh`，只引入固定公开 Demo 夹具。

### T-038 追加修复

- Compose 验收在 GitHub Runner 的失败步骤退出码为 127；`scripts/verify-demo.sh` 末段隐式调用 `rg` 解析 Alembic 版本。为移除非标准工具依赖，改用系统 `grep -RhoE`，并将 `grep` 纳入显式命令检查。

## 2026-09-04 — T-039 GitHub PR 与必需 CI 配置

### GitHub 配置

- 从已验证提交 `9e3642f986ca38dde185f84f12a40863200d387a` 创建远端 `main`；`main` 首次 push 触发 GitHub Actions 运行 `33827004378`，Backend、React、H5 Shell、Sensitive File Scan 和 Compose Demo Verification 五项均成功。
- 将 GitHub 仓库默认分支从 `codex/bootstrap-langgraph` 切换为 `main`；GitHub REST 公开仓库信息和远端 symbolic HEAD 均确认默认分支为 `main`。
- 为 `main` 创建 classic branch protection：必须通过 Pull Request、必须保持分支最新、必须解决讨论，并要求五项 CI 检查全部通过；不允许 force push 或删除。
- 单人仓库未启用 mandatory approval，避免提交者无法自审导致永久阻塞；分支保护仍阻止绕过 PR 和失败 CI 的常规合并。

### 后续开发流程

- 新任务从 `origin/main` 创建 `codex/<task-name>`，本地验证后 push 到同名远端分支，再创建目标为 `main` 的 Pull Request。
- push 与 PR 都会运行 `.github/workflows/ci.yml`；PR 只有在最新 `main` 上通过 Backend、React、H5、敏感文件和 Compose 集成五道门后才允许合并。
- 本次 README/治理提交作为首个真实 PR 链路样例；PR #1（`https://github.com/ZShining219/miniworld/pull/1`）已创建并保持打开。

### 真实 PR 链路验证

- 提交 `b5b47baedbfa7c85cdefb1d698be426c493e8552` 推送到 `codex/bootstrap-langgraph` 后，push 运行 `33831040233` 成功。
- PR 事件运行 `33831520550` 成功，五个工作流 Job 均为 success：Backend checks、React checks、H5 shell checks、Sensitive file scan、Compose demo verification。
- PR 页面显示 `10 / 10 checks OK`、`All checks have passed`、`No conflicts with base branch` 和 `Ready to merge`；验证了 PR CI、最新分支和保护分支合并门已连通。
- 未执行合并或生产部署；后续正常开发按 `origin/main` → `codex/<task-name>` → PR → 五项检查 → 合并执行。

## 2026-09-04 — T-040 Agent 驱动的项目交付流程

### 固化内容

- 新增 [`goal/delivery-workflow.md`](delivery-workflow.md)，定义产品负责人、Agent、GitHub Actions 和生产脚本的职责边界，以及 `proposed` → `local_verified` → `pr_open` → `ci_verified` → `merged` → `deploy_requested` → `deployed` → `closed` 状态机。
- 更新 `AGENTS.md`、`goal/README.md`、`goal/plan.md` 和 `goal/decisions.md`：常规无敏感代码在 preflight 通过后可由 Agent 自主测试、commit、push 分支、创建 PR 和观察 CI；合并与生产部署仍要求用户确认。
- 新增 `.github/pull_request_template.md`，把 scope、Goal 对齐、隐私扫描、本地验证、五项 CI 和生产发布分离为 PR 必填检查项。
- 新增 `scripts/agent-delivery-preflight.sh`：拒绝直接在 `main` 开发，要求 `origin/main` 基线，执行 `git diff --check`、敏感扫描，并按变更面运行后端、React、H5 或生产静态检查；可用 `MINIWORLD_RUN_INTEGRATION=1` 追加完整 Compose 链路。
- 生产脚本改为只从 `origin/main` 验证目标 SHA，并要求 `MINIWORLD_DEPLOY_APPROVED=1`；生产 README、静态测试和部署请求模板同步更新。

### 受控验证

- `bash -n scripts/agent-delivery-preflight.sh scripts/deploy-production.sh scripts/test-production-deployment.sh`：通过。
- `scripts/agent-delivery-preflight.sh`：通过；识别治理/部署变更并执行 `scripts/test-production-deployment.sh`，输出 `Production deployment static checks passed.`。
- `git diff --check` 与 `scripts/ci/check-sensitive-files.sh`：通过；未发现运行数据、私钥或非占位 token。
- T-040 不修改业务数据、Fitness 功能或生产服务器；该变更只建立 Agent 交付协议和部署批准门。

### 远端链路

- 提交 `2c154c98107210f778ff29e313e989d921d9d911` 已推送到 `codex/bootstrap-langgraph` 并更新 PR #1。
- 该提交的 push 运行 `33833414675` 和 PR 运行 `33833418213` 均完成成功；Checks 页显示两组五项 Job 全部成功。
- PR #1 页面显示 `10 / 10 checks OK`、`All checks have passed`、`No conflicts with base branch` 和 `Ready to merge`。T-040 不合并 PR，也不触发生产部署。
