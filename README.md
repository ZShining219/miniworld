# MiniWorld Agent

MiniWorld Agent 是一个面向本机唯一用户的本地优先个人工作台。它使用本地 LangGraph OSS、FastAPI、PostgreSQL 和 React，把以下能力保持为三个独立闭环：

1. 岗位发现、整理、去重与到本地住址的直线距离计算；
2. 文件、公开 GitHub 信息和 GPT 对话材料导入，形成可追溯档案事实与简历草稿；
3. 每日工作记录以及日报、周报生成。

根目录 [`goal.md`](goal.md) 是产品范围、隐私边界和验收标准的最高优先级契约。当前实现严格区分确定性 `demo` 模式与真实联网 `live` 模式：固定演示岗位不会被描述成互联网实时结果。

## 当前状态

- `demo` 模式：四服务可在 Apple Silicon/ARM64 本机通过 `docker-compose` 构建和启动；三条 LangGraph 闭环、PostgreSQL checkpoint、Worker 定时触发和容器重启持久性已有自动化验证。
- `live` 岗位来源：Lever 公开 Postings GET 适配器已完成一次临时库端到端验证；JobSpy 保留为默认关闭的最善努力回退。代码中没有申请 POST 执行器。
- 远端模型：OpenAI Responses Provider 已实现但默认关闭；未配置时 Graph 明确暂停，非法 schema 不落库。一次经授权的真实模型调用仍待用户决定。
- 未执行真实投递、消息、文件外传、第三方登录授权或公开 Git push。

详见 [`PROGRESS.md`](PROGRESS.md) 和 [`goal/implementation-log.md`](goal/implementation-log.md)。

## 架构

```text
浏览器 127.0.0.1:5173
        │
        ▼
React / TypeScript 看板
        │ localhost REST
        ▼
FastAPI API ─────────────── PostgreSQL
        │                       │
        ├─ JobDiscoveryGraph    ├─ 业务数据
        ├─ ProfileIngestionGraph├─ Agent 运行记录
        └─ WorkReportGraph      └─ LangGraph checkpoints
                                ▲
APScheduler Worker ─────────────┘
```

LangGraph 是普通 Python 依赖，运行在本地 API/Worker 容器内，不要求 LangGraph Cloud 或 LangSmith。远端模型只是受策略控制的可替换推理 Provider。

## 快速启动

前置条件：

- Apple Silicon/ARM64 macOS 是当前已验证平台；
- Docker daemon 已启动，当前验证环境使用 Colima；
- `docker-compose` 可用；
- 首次构建需要下载基础镜像和锁定依赖。

准备本地配置：

```bash
cp .env.example .env
```

建议将 `.env` 中的 `POSTGRES_PASSWORD` 改为本机专用随机值。`.env` 已被 Git 忽略。

构建并启动：

```bash
docker-compose up -d --build
```

打开：

- 看板：<http://127.0.0.1:5173>
- API 文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/api/v1/health>

查看状态和日志：

```bash
docker-compose ps
docker-compose logs --tail=100 api worker
```

停止服务但保留本地数据：

```bash
docker-compose down
```

只有确认要删除所有本地业务数据、导入材料和 checkpoint 时，才使用 `docker-compose down -v`。

## Demo 操作路径

1. 在“雷达总览”确认界面显示 `DEMO MODE · 本地确定性`；
2. 在“岗位信号”运行 Demo 扫描，查看来源、状态和 Haversine 直线距离；
3. 在“个人档案”选择本地文件，或手动粘贴公开 GitHub/GPT 对话材料，保存后触发处理；
4. 查看每条事实的材料证据 ID 和新的结构化简历草稿版本；
5. 在“工作沉淀”添加记录并生成日报、周报；
6. 在“Agent 运行”查看 Graph、触发方式、执行模式、节点和失败原因；失败 Graph 可从同一持久 checkpoint 安全重试；
7. 在“本地设置”查看掩码位置、附近地标和定时公开读取状态。

演示数据库只包含虚构位置和固定演示材料。设置页不会回显已保存的精确地址或坐标；位置输入保存后立即清空。

## 自动化验证

在四服务运行时执行完整容器验证：

```bash
./scripts/verify-demo.sh
```

该脚本只写入虚构测试数据，并验证：

- PostgreSQL 迁移和健康状态；
- 三个独立 LangGraph 的成功运行记录；
- 岗位去重、来源和直线距离；
- 文件、GitHub、GPT 对话三类材料证据；
- 版本化简历草稿；
- 日报、周报及其工作记录来源；
- 工作报告不会修改个人档案；
- Live 模式默认配置门；
- APScheduler Worker 的实际定时触发；
- LangGraph PostgreSQL checkpoint 表和记录；
- 一次真实节点失败、修复本地前置条件后从同一 PostgreSQL checkpoint 恢复，以及成功后的重复重试阻断；
- 宿主机端口仅绑定 `127.0.0.1`；
- PostgreSQL、API、Worker、前端重启后的数据和 checkpoint 持久性；
- 公开 API 响应不包含精确演示住址或家庭坐标。

本地代码测试：

```bash
./scripts/test-local.sh
```

当前证据：后端 17 项测试、Ruff、Mypy、Ty、前端生产构建和 Playwright 3 项 E2E 通过；Biome 无 error，保留 8 条 CSS 风格 warning。

一条命令构建、启动并执行完整容器验证：

```bash
./scripts/test.sh
```

## 运行模式

### Demo（默认）

```dotenv
EXECUTION_MODE=demo
MODEL_PROVIDER_MODE=demo
ALLOW_LIVE_JOB_SEARCH=false
```

不需要 API Key；岗位和模型结果均明确标记为 `demo`。该模式用于冷启动、回归测试和隐私边界验证。

### Live（尚未冻结）

Live 岗位查询需要显式设置：

```dotenv
EXECUTION_MODE=live
ALLOW_LIVE_JOB_SEARCH=true
LIVE_JOB_SOURCE=lever
LEVER_SITES=binance
```

`LEVER_SITES` 是逗号分隔的公开公司 Job Board site 白名单。系统把本地配置的附近地标作为 Lever `location` 参数，不发送精确住址或家庭坐标；来源不提供可验证坐标时，职位会标记为 `location_unresolved` 并显示原因。不要通过验证码绕过、登录绕过或高频抓取解决来源限制。

可用虚构位置和一次性临时数据库复核公开 GET，不会修改正式本地数据：

```bash
UV_CACHE_DIR=.cache/uv uv run --package app python scripts/verify-live-lever.py
```

该命令会访问互联网，但只读取公开职位；不会调用 Lever 申请 POST，也不会执行其他外部写入。

远端 OpenAI Provider 还需要：

```dotenv
MODEL_PROVIDER_MODE=openai
OPENAI_API_KEY=replace-locally
OPENAI_MODEL=gpt-5.6
```

密钥只能保存在本机 `.env`，不得进入数据库、前端、日志或 Git。真实个人材料发给远端 Provider 前，需要按数据类别获得用户授权。

## 隐私和权限边界

- 精确住址与家庭坐标只保存在本地 PostgreSQL；普通 API 只返回配置状态和掩码；
- 外部岗位查询只使用附近地标文本，不使用精确门牌地址；
- 职位地点到家庭坐标的距离只在本地计算，并明确标记为直线距离；
- 岗位 Graph 无权修改个人档案或简历；
- 工作报告不会自动进入档案；
- 远端模型只接收当前任务所需、已授权并经过最小化的文本；
- 投递、消息、上传、第三方登录授权、平台修改和公开推送必须在实际执行前获得确认。

## 目录

```text
backend/                 FastAPI、SQLModel、LangGraph、Worker、迁移和测试
frontend/                React/TypeScript 看板与 Playwright 测试
goal.md                  产品目标、强约束和验收清单
goal/                    架构、调研、计划、决策和实现记录
scripts/verify-demo.sh   容器端到端和重启持久性验证
scripts/verify-live-lever.py  一次性 Lever 公开 GET 集成证明
compose.yml              frontend / api / worker / db 四服务
PROGRESS.md              当前证据、未完成项和待决事项
```

## 上游与 Git

- 工程基座固定自 FastAPI `full-stack-fastapi-template` commit `162344da111e833b30892728372ab95331f06873`；
- 来源与许可证记录见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)；
- 当前实现分支为 `codex/bootstrap-langgraph`；
- 真实地址、个人材料、API Key、数据库卷、日志和生成简历均不得提交；
- 公开 push 必须在 secret/PII 扫描后由用户确认。

## 当前非目标

匹配评分、投递跟踪、自动投递、最终地图/雷达视觉、精确通勤时间、多用户和云 SaaS 均不属于当前 Demo。完整边界以 [`goal.md`](goal.md) 为准。
