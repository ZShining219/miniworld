# 实施计划

## 执行原则

- 严格按阶段推进；前一阶段验收未通过，不进入后一阶段；
- 每阶段使用独立 `codex/` 分支和可回滚提交；
- 功能以三个端到端闭环为单位交付，不以“安装了框架”作为完成；
- 新增功能必须对应根目录 `goal.md` 的范围或验收项；
- 外部依赖固定版本，上游导入固定 commit；
- 精确住址、个人材料、API 密钥和运行数据不得提交 Git。

## Phase 0：文档、Git 与上游基线

操作：

1. 审阅并确认 `goal.md` v0.2 与 `goal/` 文档；
2. 新增 `.gitignore`，覆盖 `.env*`、本地数据卷、上传材料、导出简历、日志、模型缓存和 IDE 临时文件；
3. 将当前分支从 `master` 重命名为 `main`；
4. 以当前 goal、`.project_id` 和 `.ai/` 状态创建本地初始提交；
5. 添加空仓库 `https://github.com/ZShining219/miniworld.git` 为 `origin`；
6. 创建 `codex/bootstrap-langgraph` 实现分支；
7. clone FastAPI 官方模板到 `/tmp` 唯一目录，读取上游指令、许可证、依赖和 commit；
8. 在实现日志记录上游 URL、commit、许可证和选定导入路径；
9. 选择性导入 backend、frontend、测试与 Docker 结构，单独提交；
10. 删除公开注册、邮件、云部署和无关配置，保留本地单用户路径；
11. 在任何首次公开 push 前运行 secret/PII 检查，并向用户确认。

阶段验收：

- Git 历史能清晰区分“本项目目标基线”“上游基座导入”“本地裁剪”；
- 工作树不包含上游 `.git`、`.agents`、`.claude` 或真实 `.env`；
- 上游来源和许可证可追溯；
- Docker 文件和依赖在 ARM64 上具有可构建路径。

## Phase 1：本地基础设施与领域骨架

操作：

1. 将 Compose 收敛为 `frontend`、`api`、`worker`、`db`；
2. 所有映射端口绑定 `127.0.0.1`；
3. 保留 PostgreSQL 和 Alembic，建立第一版领域表；
4. 增加统一运行状态、错误码、审计元数据和幂等键；
5. 接入 LangGraph 与 PostgreSQL checkpointer；
6. 在独立 Worker 中接入 APScheduler，并从 PostgreSQL 读取持久化调度配置；
7. 建立空的三个 Graph 和独立状态模型；
8. 实现 `JobSourceAdapter`、`ModelProvider`、`ArtifactConverter` 协议；
9. 实现精确位置与附近地标的分表存储和掩码 API；
10. 实现出站策略骨架和禁止字段扫描；
11. 增加健康检查、迁移检查和容器启动顺序。

阶段验收：

- `docker-compose up --build` 可启动四个服务；
- API、Worker 和数据库重启后 Graph checkpoint 仍存在；
- 前端只能获得精确位置“已配置/未配置”和掩码，不返回完整值；
- 三个 Graph 无跨模块写权限；
- 远端 Provider 未配置时不会产生网络调用。

## Phase 2：岗位发现闭环

操作：

1. 建立统一 `JobPosting`、`JobObservation` 和 `JobRun` schema；
2. 将 JobSpy 封装为首个适配器，配置来源白名单、速率和最大结果数；
3. 提供测试用固定数据适配器，保证不依赖互联网也可回归；
4. 实现附近地标轮换；
5. 实现标准化、链接规范化、三层去重和观察记录；
6. 实现公开职位地点解析接口；
7. 使用本地 Haversine 节点计算公里距离；
8. 实现手动运行 API 和 Worker 定时触发；
9. 实现 Jobs、Job Runs 前端页面；
10. 为 429、超时、页面变化、地点缺失和部分成功增加错误处理。

阶段验收：

- 固定数据和至少一个公开来源均能完成端到端运行；
- 相同输入重复执行不产生重复职位；
- 精确住址/坐标不会出现在适配器参数、网络请求或普通日志；
- 前端能按直线距离排序并解释无距离职位；
- 定时运行只使用已启用来源和附近地标。

## Phase 3：个人档案与简历闭环

操作：

1. 建立受控上传目录、文件大小/MIME/哈希校验和清理策略；
2. 通过 MarkItDown 支持第一批本地格式，首批至少 PDF、DOCX、TXT/Markdown；
3. 增加 GitHub 公开 URL/导出材料和 GPT 对话文件导入器；
4. 实现材料片段、事实、证据、冲突和简历草稿 schema；
5. 实现 Provider 配置状态与 secret 注入；
6. 实现本地分类、最小化、禁止字段检查和首次数据类别授权；
7. 通过远端 Provider 请求 schema 约束的结构化事实；
8. 校验模型输出，冲突进入待确认，不静默覆盖；
9. 从事实生成版本化 JSON Resume 风格草稿；
10. 实现 Imports、Profile Facts、Resume Drafts 前端页面。

阶段验收：

- 三类入口至少各完成一个成功样例；
- 每条事实能定位到材料和片段；
- 非法模型输出不会进入事实表；
- 精确位置、密钥和未选择材料不能进入模型请求；
- 职位模块无法调用简历更新写接口；
- 远端模型不可用时材料和本地解析结果仍保留，可安全重试。

## Phase 4：每日工作与报告闭环

操作：

1. 实现 `WorkEntry` CRUD 和按日期查询；
2. 实现日报、周报输入范围与版本 schema；
3. 实现 WorkReportGraph 和 Provider 策略；
4. 增加无记录、部分日期缺失、模型失败和重试处理；
5. 在报告中保存输入记录 ID、Provider、模型和生成时间；
6. 实现 Work 与 Reports 前端页面；
7. 提供“建议转入个人档案”入口，但 Demo 只创建 Approval，不自动写入。

阶段验收：

- 单日记录可生成日报，多日记录可生成周报；
- 报告不捏造原记录不存在的成果；
- 报告能追溯输入记录；
- 未确认时不会产生个人档案事实。

## Phase 5：统一看板、权限与可观测性

操作：

1. 完成 Overview 和 Agent Runs 页面；
2. 统一 Graph 状态：`queued`、`running`、`awaiting_configuration`、`awaiting_approval`、`blocked_by_policy`、`partial_success`、`succeeded`、`failed`；
3. 提供安全重试和错误详情；
4. 完成模型调用审计、外部请求分类和敏感字段阻断事件；
5. 添加设置页：精确位置、附近地标、职位来源、Provider 和授权；
6. 实现所有未来外部写入的统一 Approval 门，Demo 不实现实际投递；
7. 检查前端 bundle、API 响应和日志不含密钥与精确地址。

阶段验收：

- 用户能从前端理解每个 Agent 正在做什么、失败在哪里、是否等待确认；
- 任何外部写入路径都无法绕过 Approval；
- 审计记录足以定位运行但不保存敏感正文；
- 三个模块在导航和数据权限上均可明确区分。

## Phase 6：测试、文档与 Demo 冻结

测试矩阵：

- 单元：Haversine、去重、链接规范化、地标轮换、schema 校验、出站字段阻断；
- Graph：正常、部分成功、暂停确认、网络失败、模型非法输出和 checkpoint 恢复；
- API：掩码位置、上传校验、幂等触发、状态轮询、跨模块拒绝；
- 集成：PostgreSQL 迁移、JobSpy 测试替身、Provider 测试替身、Worker 调度；
- E2E：首次设置 → 岗位运行 → 查看距离；材料导入 → 档案事实 → 简历草稿；工作记录 → 日报/周报；
- 安全回归：精确地址、坐标和密钥不出现在网络模拟器、日志、前端和 Git；
- 容器：ARM64 构建、冷启动、重启持久化和迁移。

文档：

1. 编写根目录 `README.md`；
2. 提供 `.env.example`，只包含占位符；
3. 记录模型 Provider 配置、数据外发说明和撤销方式；
4. 记录已知来源限制和合法使用边界；
5. 逐项执行 `goal.md` 验收清单；
6. 更新实现日志和决策记录；
7. 生成 `demo-v0.1` 本地 tag；
8. secret/PII 检查通过并获得用户确认后才 push 到公开 origin。

## Git 提交策略

推荐提交边界：

1. `docs: establish product goal and governance baseline`
2. `chore: import pinned FastAPI full-stack template`
3. `refactor: reduce template to local single-user runtime`
4. `feat: add LangGraph runtime and domain contracts`
5. `feat: complete job discovery distance loop`
6. `feat: complete profile and resume ingestion loop`
7. `feat: complete daily and weekly report loop`
8. `feat: add unified dashboard and approval gates`
9. `test: cover privacy and end-to-end demo flows`
10. `docs: finalize local demo operations`

每次提交必须可构建或明确标记为仅文档/脚手架提交。禁止把真实数据、导入文件、数据库卷、日志、密钥或生成简历提交到任何分支。
