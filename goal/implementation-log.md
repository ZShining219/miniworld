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
