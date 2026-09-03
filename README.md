# MiniWorld Agent

MiniWorld Agent 是一个面向本机唯一用户的本地优先个人工作台，也是后续个人 Agent 工具的统一呈现平台。

当前项目采用双层结构：`apps/miniworld-shell/` 中的 unibest/uni-app 负责统一入口、跨端呈现和模块导航；现有 FastAPI、React 看板、LangGraph 工作流与 Tauri 岗位雷达继续作为可独立运行的业务工具。后续新功能先作为独立工具实现，再通过明确的接口、数据边界和审批门接入呈现平台，不把尚未完成的能力伪装成已交付功能。

MiniWorld Agent 当前围绕以下三个独立闭环建设：

1. 岗位发现、整理、去重与到本地住址的直线距离计算；
2. 文件、公开 GitHub 信息和 GPT 对话材料导入，形成可追溯档案事实与简历草稿；
3. 每日工作记录以及日报、周报生成。

根目录 [`goal.md`](goal.md) 是产品范围、隐私边界和验收标准的最高优先级契约。当前实现严格区分确定性 `demo` 模式与真实联网 `live` 模式：固定演示岗位不会被描述成互联网实时结果。

## 项目定位与功能备案

unibest 是项目的统一呈现平台，不等同于某一个业务模块。它提供 Web 入口，并为未来 Android 与微信小程序端保留扩展位；当前只验收 Web，微信小程序和 Android/HBuilderX 出包暂缓。业务能力仍由各自工具负责，平台层不跨边界读写岗位、档案和工作沉淀数据。

所有功能都必须在本 README 的“功能备案”表中登记。功能完成后补充入口、运行方式、验证证据和延期事项；未完成的功能必须保留状态，不得只依赖代码目录或聊天记录管理。

| 功能/工具 | 当前状态 | 呈现入口 | 责任边界 | 验证与说明 |
| --- | --- | --- | --- | --- |
| unibest 统一呈现平台 | Web 已验证 | [`apps/miniworld-shell/`](apps/miniworld-shell/)；`http://127.0.0.1:9000/` | 负责跨端入口、导航和页面承载；业务数据仍由独立模块/API 管理 | `pnpm type-check`、27 项单测、H5 构建和桌面/手机浏览器验收通过 |
| 健身训练记录 | H5 Demo 已验证，生产部署中 | 首页 `04 健身记录` → `/pages/fitness/index`；生产入口 `https://103-52-153-212.sslip.io` | 独立 Fitness 数据表、后端包和前端模块；生产只公开受 Basic Auth 保护的 Fitness H5/API，不接入三个 Agent 闭环或模型 Provider | 逐组保存、恢复、历史、日历、重量趋势和下次默认值均通过自动化与浏览器验收；生产验收完成后补记 SHA 与数据核对 |
| 岗位发现闭环 | Demo 与 Live 只读验证完成 | React 看板“岗位信号”；后续接入 unibest “岗位” | 公开岗位读取、标准化、去重和本地直线距离；不得改写档案/简历 | Lever 公开 GET、岗位 Graph、隐私测试和岗位雷达均有记录 |
| 岗位雷达 | 本地 Demo 已验证 | Tauri 原生悬浮窗；后续接入统一入口 | 本地地图包、岗位坐标呈现和窗口状态；不发送家庭中心到外部地图 | MapLibre/PMTiles、Tauri ARM64 构建及无外网请求验证通过 |
| 个人档案与简历 | 本地 Demo 已验证 | React 看板“个人档案”；后续接入 unibest “档案” | 只处理用户主动导入的材料，保留来源和事实证据 | 文件/GitHub/GPT 材料入口、事实和简历草稿测试通过 |
| 每日工作沉淀 | 本地 Demo 已验证 | React 看板“工作沉淀”；后续接入 unibest “工作” | 只读取用户主动记录；日报/周报进入档案前必须确认 | 日报、周报、来源追溯和跨模块隔离验证通过 |
| Agent 运行与审批 | 已实现基础能力 | React 看板“Agent 运行”；统一入口待接入 | 展示 Graph 状态、失败原因、恢复和权限阻断 | PostgreSQL checkpoint、失败恢复和重复重试阻断已有证据 |
| 微信小程序 | 暂缓 | 未配置 | 不在当前验收范围 | 按用户指令暂不配置 AppID 或构建链路 |
| Android/HBuilderX 出包 | 暂缓 | 未配置 | 不在当前验收范围 | 按用户指令暂不安装或验证原生打包链路 |

### 功能备案规则

新增功能完成时，至少更新以下内容：

1. 本表中的功能名称、状态、呈现入口和责任边界；
2. 对应的启动命令、配置前置条件和本地访问地址；
3. 可复现的测试、构建或浏览器验证命令；
4. 尚未完成的部分、延期原因和下一步，不用“待完善”代替具体说明；
5. 涉及隐私、外部读取或外部写入时，记录数据范围、授权门和是否实际执行。

README 只登记项目级事实；详细设计、决策和逐次验证记录分别放在 [`goal/`](goal/)、[`goal/decisions.md`](goal/decisions.md) 和 [`goal/implementation-log.md`](goal/implementation-log.md)。当 README 与 `goal.md` 冲突时，以 `goal.md` 为准。

## 当前状态

- `demo` 模式：四服务可在 Apple Silicon/ARM64 本机通过 `docker-compose` 构建和启动；三条 LangGraph 闭环、PostgreSQL checkpoint、Worker 定时触发和容器重启持久性已有自动化验证。
- `live` 岗位来源：Lever 公开 Postings GET 适配器已完成一次临时库端到端验证；JobSpy 保留为默认关闭的最善努力回退。代码中没有申请 POST 执行器。
- 岗位雷达：MapLibre + 本地 PMTiles 场景已接入 Tauri 2 原生悬浮窗；窗口可缩放、置顶、拖动和关闭，HOME 固定中心，虚构岗位以黄色脉冲点显示。
- 远端模型：OpenAI Responses Provider 已实现但默认关闭；未配置时 Graph 明确暂停，非法 schema 不落库。真实调用是可选增强，不阻塞本地 Demo。
- 未执行真实投递、消息、文件外传或第三方登录授权；源码已发布到远端 `codex/bootstrap-langgraph` 分支，远端 `main` 与 release tag 尚未建立。

详见 [`PROGRESS.md`](PROGRESS.md) 和 [`goal/implementation-log.md`](goal/implementation-log.md)。

## 运行内容注册表

本节是项目可运行内容的统一注册入口。后续开发应先按任务选择最小运行组合，再使用对应的验证命令；新增、删除或改变端口、依赖、启动方式时，必须同步更新本节。表中的“已验证”表示已有可复现证据，不表示服务当前正在运行。

### 长期运行单元

| 运行 ID | 内容与任务 | 依赖 | 启动命令 | 入口/健康检查 | 停止方式 | 验证状态 |
| --- | --- | --- | --- | --- | --- | --- |
| `RUN-DB` | PostgreSQL 正式数据源；保存三个 Agent 闭环、运行审计、LangGraph checkpoint 和 Fitness 数据 | Docker | `docker-compose up -d db` | 仅 Compose 内网 `db:5432`；`docker-compose ps db` | `docker-compose stop db` | PostgreSQL 17、迁移和重启持久性已验证 |
| `RUN-API` | FastAPI 统一后端；提供 Jobs、Profile/Resume、Work、Agent Runs、Approval、Radar 和 `/api/v1/fitness/*` | `RUN-DB` | `docker-compose up -d --build api` | `http://127.0.0.1:8000/docs`；`curl -fsS http://127.0.0.1:8000/api/v1/health` | `docker-compose stop api` | API、迁移、隐私边界和 Fitness 接口已验证 |
| `RUN-WORKER` | APScheduler 后台任务；执行启用的定时公开读取和限定本地更新，不执行未确认的外部写入 | `RUN-DB`、`RUN-API` | `docker-compose up -d --build worker` | 无宿主端口；`docker-compose ps worker`、`docker-compose logs --tail=100 worker` | `docker-compose stop worker` | Demo 定时触发和本地写入边界已验证 |
| `RUN-REACT` | React/Nginx 完整 Agent 看板；承载岗位、档案/简历、工作沉淀、Agent Runs、审批、设置和浏览器 Radar | `RUN-API` | `docker-compose up -d --build frontend` | `http://127.0.0.1:5173`；Radar 为 `http://127.0.0.1:5173/radar` | `docker-compose stop frontend` | 生产构建和 9 项 Playwright E2E 已验证 |
| `RUN-H5` | unibest/uni-app 统一 Web 壳；首页模块导航和完整 Fitness H5 工作流，Jobs/Profile/Work 目前仍为占位入口 | `RUN-API`；首次运行需要 pnpm 依赖 | `cd apps/miniworld-shell && pnpm dev:h5` | `http://127.0.0.1:9000`；Fitness 为首页 `04 健身记录` | 前台终端 `Ctrl-C` | TypeScript、65 项单测、H5 build 和桌面/手机浏览器验收已通过 |
| `RUN-RADAR-NATIVE` | Tauri 2 本机岗位雷达；显示本地 PMTiles、HOME 中心、岗位信号和原生窗口控制 | `RUN-API`；本地地图包；前端依赖 | `cd frontend && bun run tauri:dev` | 本机 `MiniWorld Job Radar` 窗口；API/地图/WebGL 失败均有明确状态 | 关闭窗口并在启动终端 `Ctrl-C` | macOS ARM64 开发运行和未签名 `.app` 构建已验证 |
| `RUN-FITNESS-PROD` | 手机使用的单用户 Fitness 生产栈；Caddy HTTPS、H5、FastAPI、PostgreSQL | Ubuntu 服务器、Docker Compose、`600` 权限生产环境文件、固定 Git SHA | 服务器 root 执行 `/srv/miniworld/scripts/deploy-production.sh <40位SHA>` | `https://103-52-153-212.sslip.io`；未认证必须为 `401` | `docker compose --env-file /etc/miniworld/production.env -f /srv/miniworld/deploy/production/compose.yml down` | T-033 已固定 SHA 发布；自动备份、迁移、健康与认证边界通过，只公开 80/443；新增交互等待真实手机复测 |

`RUN-RADAR-WEB` 不是独立进程，而是 `RUN-REACT` 的 `/radar` 页面。Fitness 正式数据依赖 `RUN-API` 和 `RUN-DB`；只启动 `RUN-H5` 可以查看壳，但不能完成训练数据读写。

### 按任务启动

| 任务 | 最小组合 | 命令 |
| --- | --- | --- |
| 完整 Agent Demo | `RUN-DB` + `RUN-API` + `RUN-WORKER` + `RUN-REACT` | `docker-compose up -d --build` |
| 后端/API 开发 | `RUN-DB` + `RUN-API` | `docker-compose up -d --build db api` |
| Fitness H5 开发 | `RUN-DB` + `RUN-API` + `RUN-H5` | 先执行 `docker-compose up -d --build db api`，再执行 `cd apps/miniworld-shell && pnpm dev:h5` |
| 浏览器岗位雷达 | `RUN-DB` + `RUN-API` + `RUN-REACT` | 准备地图后执行 `docker-compose up -d --build db api frontend`，打开 `/radar` |
| 原生岗位雷达 | `RUN-DB` + `RUN-API` + `RUN-RADAR-NATIVE` | 准备地图并启动 API，再执行 `cd frontend && bun run tauri:dev` |

Radar 首次运行前执行 `./scripts/fetch-radar-demo-map.sh`。该脚本只准备被 Git 忽略的本地 Demo 地图包；不要使用精确家庭坐标请求外部地图。

### 验证任务注册表

| 验证 ID | 覆盖内容 | 命令 | 前置条件/副作用 |
| --- | --- | --- | --- |
| `VERIFY-LOCAL` | 后端 Pytest/Ruff/Mypy/Ty，以及 React build/lint/test | `./scripts/test-local.sh` | 不要求 Compose；生成的缓存和构建目录被 Git 忽略 |
| `VERIFY-FITNESS-BACKEND` | Fitness 与共享后端回归 | `UV_CACHE_DIR=.cache/uv uv run --project backend pytest backend/tests -q` | 使用测试数据库，不写正式 PostgreSQL |
| `VERIFY-H5` | Shell TypeScript、27 项单测和 H5 production build | `cd apps/miniworld-shell && pnpm type-check && pnpm test:run && pnpm build:h5` | 需要已安装锁定的 pnpm 依赖；生成 `dist/` |
| `VERIFY-DEMO` | 四服务、三 Graph、Worker、checkpoint、持久性和隐私端到端验证 | `./scripts/verify-demo.sh` | 要求完整 Compose 已运行；只写入明确的虚构 Demo 数据 |
| `VERIFY-ALL` | 构建并启动四个 Compose 服务，然后执行 `VERIFY-DEMO` | `./scripts/test.sh` | 完成后服务仍保持运行，需要手动执行 `docker-compose down` |
| `VERIFY-LIVE-JOBS` | Lever 公开职位 GET 的一次性 Live 只读验证 | `UV_CACHE_DIR=.cache/uv uv run --package app python scripts/verify-live-lever.py` | 会访问互联网；使用虚构位置和临时数据库，不执行申请 POST |
| `VERIFY-FITNESS-PROD` | 生产脚本、Compose/Caddy 边界与 H5 同源构建 | `./scripts/test-production-deployment.sh`，再按 [`deploy/production/README.md`](deploy/production/README.md) 做公网、数据、备份恢复验收 | 公网验收会读取生产 Fitness 数据；功能写操作仅在用户正式使用或明确的验收训练中执行 |

### 统一停服

停止 Compose 服务并保留 PostgreSQL 与上传数据：

```bash
docker-compose down
```

`RUN-H5` 和 `RUN-RADAR-NATIVE` 是前台按需进程，应在各自启动终端使用 `Ctrl-C`，原生 Radar 同时关闭窗口。只有明确要永久删除所有本地业务数据、导入材料和 checkpoint 时才允许执行 `docker-compose down -v`；常规开发和测试不得使用 `-v`。

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

## 岗位雷达悬浮窗

岗位雷达是现有浏览器看板之外的独立本机入口，不替换四服务或三个业务闭环。默认使用 Firenze 公共示例区域和虚构岗位，真实岗位数据接入仍按产品计划暂缓。

首次准备被 Git 忽略的本地地图包：

```bash
./scripts/fetch-radar-demo-map.sh
```

确认本地 API 正在 `127.0.0.1:8000` 运行，然后启动原生开发窗口：

```bash
cd frontend
bun run tauri:dev
```

窗口初始为 420×420，允许缩放到 320×320—900×700；顶部空白区域可拖动，图钉按钮切换置顶，十字按钮让窗口回到屏幕中心。关闭/重开会恢复窗口尺寸和位置，但不会把地图中心、精确坐标或岗位内容写入窗口状态文件。API 不可用、地图包缺失或 WebGL2 不可用时，窗口只显示本地启动说明，不会回退到外部地图服务。

地图运行文件位于 `runtime-data/maps/demo-firenze.pmtiles`；窗口状态位于 `~/Library/Application Support/com.zshining219.miniworld.radar/radar-window.json`，只包含 `x`、`y`、`width`、`height`。两者均不进入 Git，许可证和地图数据归属见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

构建本机 ARM64 `.app`：

```bash
cd frontend
bun run tauri:build
```

产物位于 `frontend/src-tauri/target/release/bundle/macos/MiniWorld Job Radar.app`。当前命令明确使用 `--no-sign`，用于本机 Demo，不构成签名或公证发布包。

## 多端系统壳（unibest）

新的 Web/Android/未来小程序统一入口位于 `apps/miniworld-shell/`。它与现有 React 看板和 Tauri Radar 并存，不替换已经验证的业务模块。

```bash
cd apps/miniworld-shell
pnpm install --ignore-scripts --frozen-lockfile
pnpm init-baseFiles
pnpm dev:h5
```

Web 默认只监听 `http://127.0.0.1:9000/`，API 默认指向 `http://127.0.0.1:8000`。本阶段只验证 Web；微信小程序 AppID、构建和 Android/HBuilderX 出包暂缓。

Fitness 从壳首页工具列表的 `04 健身记录` 进入，不占用主 TabBar。先确保本地 API 已迁移并运行，再启动 H5：

```bash
docker-compose up -d --build api db
cd apps/miniworld-shell
pnpm dev:h5
```

Demo 初始化“胸、背、肩、臀腿”四个计划，“胸”包含杠铃卧推和上斜哑铃卧推。正式历史保存在 PostgreSQL；浏览器 storage 只保存还没有提交成功的重量和次数草稿。

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

当前证据：后端 27 项测试、Ruff、Mypy、Ty、React 前端生产构建和 Playwright 9 项 E2E 通过；unibest Shell 27 项测试、TypeScript、限定范围 ESLint 和 H5 production build 通过；Biome 无 error，保留 8 条 CSS 风格 warning；Tauri ARM64 debug 链接与未签名 release `.app` 打包通过，最终二进制为 Mach-O arm64。

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

### Live 岗位读取（已验证、默认关闭）

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

远端模型调用不是本地 Demo 的启动或冻结条件。未配置时继续使用明确标记的确定性 Provider；用户日后如启用，再把真实调用作为单独的可选验收，不得把替身结果描述为真实推理。

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
frontend/src-tauri/      Tauri 2 原生岗位雷达宿主与窗口几何持久化
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

匹配评分、投递跟踪、自动投递、真实岗位地图接入、精确通勤时间、多用户和云 SaaS 均不属于当前岗位雷达呈现阶段。完整边界以 [`goal.md`](goal.md) 为准。
