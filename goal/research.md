# 技术与开源项目调研

> 调研日期：2026-08-18  
> 目标：寻找成熟、市场认可度高且不会改变项目意图的实现基座与组件

> 运行结论：本机可以直接运行 LangGraph OSS。LangGraph 是 Python 编排库，不要求使用云服务；本项目将它安装在本地 API/Worker 环境，以 PostgreSQL 提供持久 checkpoint。

## 1. 选择结论

| 能力 | 选择 | 使用方式 | 结论 |
| --- | --- | --- | --- |
| 全栈工程基座 | [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template) | 固定 commit 后选择性导入并裁剪 | 采用 |
| Agent 编排 | [LangGraph](https://github.com/langchain-ai/langgraph) | Python 依赖，三个独立 Graph | 采用 |
| 职位采集 | [JobSpy](https://github.com/speedyapply/JobSpy) | 首个 `JobSourceAdapter`，必须有限流和失败治理 | 采用为候选适配器 |
| 公司 ATS 公开职位 | [Lever Postings API](https://github.com/lever/postings-api) | 只读 GET 适配器，按公司 site/location 读取 | 已采用并完成 Live 证据 |
| 多模态文件转文本 | [Microsoft MarkItDown](https://github.com/microsoft/markitdown) | 本地依赖，只调用最窄的本地转换接口 | 采用 |
| 简历结构标准 | [JSON Resume](https://github.com/jsonresume/jsonresume.org/tree/master/packages/schema) | 作为内部简历草稿 schema 的参考 | 采用为参考 |
| 简历产品参考 | [Reactive Resume](https://github.com/AmruthPillai/Reactive-Resume) | 只参考交互、预览和导出思路 | 不作为基座 |
| 个人 AI 参考 | [Khoj](https://github.com/khoj-ai/khoj) | 只参考本地知识和定时研究思路 | 不作为基座 |

Star 数量是 2026-08-18 的页面快照，仅用于判断社区规模，不作为安全或质量保证：FastAPI 模板约 44.9k、LangGraph 约 39.9k、JobSpy 约 4.1k、MarkItDown 约 174k、Reactive Resume 约 40.8k、Khoj 约 36.5k。

### 1.1 2026-08-18 公开资料复核

| 资料 | 实际用于决策的信息 | 边界 |
| --- | --- | --- |
| [LangGraph OSS overview](https://docs.langchain.com/oss/python/langgraph/overview) | 可直接 `pip install -U langgraph`；定位为支持 durable execution、persistence 和 human-in-the-loop 的低层编排框架 | 官方同时强调它是低层编排，不代替应用、权限和数据层 |
| [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template) | FastAPI、SQLModel、PostgreSQL、React/TypeScript、Vite、Tailwind/shadcn、Docker Compose、Pytest 和 Playwright 组合仍由上游明确提供 | 上游还包含认证、邮件和云部署，本项目必须裁剪 |
| [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) | Responses API 的 `responses.parse` 可用 Pydantic schema 得到结构化结果，官方建议在可用时优先于仅保证 JSON 合法的 JSON mode | schema 约束不代替本地数据最小化、授权检查和业务验证 |
| [Lever Postings API](https://github.com/lever/postings-api) | 公开 GET API 可返回 JSON 职位、稳定 posting ID、hosted URL、location、commitment 和 workplace type | 它是按公司 site 分区的 Job Board，不是全网搜索；POST 申请端点属外部写入，当前禁止 |

调研结论因此是：本机运行 LangGraph 既可行也已经由当前容器实现证明；就作品集和岗位认可度而言，“持久状态 + 隐私策略 + 全栈产品 + 自动化验证”比增加无约束的 Agent 数量更符合本项目意图。

## 2. 为什么采用 FastAPI 官方模板

模板提供 FastAPI、SQLModel、PostgreSQL、React、TypeScript、Vite、Tailwind/shadcn、Pytest、Playwright 和 Docker 的成熟组合，能减少工程脚手架工作，并有较高的就业市场可识别性。

采用时不完整照搬：

- 保留 API、前端、数据库迁移、类型生成、测试和容器结构；
- 移除公开注册、多用户角色、邮件找回、云部署和 Demo 不需要的代理服务；
- 默认只暴露 localhost；
- 用当前项目的 `goal.md`、`.ai/` 和 Git 历史作为主权来源；
- 不复制上游 `.git`、`.agents`、`.claude` 或与本项目无关的工作流指令。

## 3. 为什么 LangGraph 作为核心

LangGraph 是编排库，不是完整应用基座。它提供长期状态、持久执行、checkpoint 和 human-in-the-loop，适合把三个业务闭环实现为隔离、可审计的状态图。

本项目只使用 OSS Python 包和本地 PostgreSQL checkpoint，不依赖 LangGraph 云平台。模型调用通过项目自己的 `ModelProvider` 网关进入，LangGraph 节点不能直接读取任意文件、密钥或绕过出站策略。

### 3.1 本机运行结论

- 编排层：`langgraph` 在普通 Python 进程中执行，适配 Apple Silicon；
- 状态层：测试可使用内存 checkpointer，Docker Demo 使用 PostgreSQL checkpointer；
- 模型层：Graph 可以调用远端 GPT Provider、本机 Ollama Provider 或确定性测试 Provider，三者均不改变 Graph 的业务边界；
- 调度层：APScheduler 只负责定时触发，Graph 自己保存运行状态；
- 托管产品：LangSmith/Deployment 可用于未来观测或部署评估，但不进入本地 Demo 的启动依赖。

因此，“本机运行 Agent”与“调用远端大模型”是两层独立问题：前者由本地 Python、数据库和 Worker 完成，后者只是受策略控制的可替换推理能力。

### 3.2 工作市场与作品集价值

采用 LangGraph 的价值来自可展示的工程问题，而不是库名本身：

- 用显式 State/Node/Edge 表达三个业务流程；
- 用 checkpoint 证明长任务可恢复，而不是只做同步聊天；
- 用 interrupt/approval 表达 human-in-the-loop；
- 用 Provider、Pydantic schema 和策略层约束不可信模型输出；
- 用 FastAPI、PostgreSQL、React、Docker、Pytest、Playwright 形成完整交付链；
- 用真实来源适配器和确定性替身同时证明外部集成与可测试性。

这些能力比堆叠多个自由对话 Agent 更符合本项目的隐私约束，也更容易通过代码、测试和 Demo 解释。

未采用方案：

- CrewAI：多 Agent 演示直观，但当前任务以确定性工作流和权限边界为主；
- AutoGen：适合研究型多 Agent 会话，当前会增加不必要的自治复杂度；
- Temporal：通用 durable workflow 工程价值高，但对本轮 Demo 过重；
- Dify/n8n：工作流搭建快，但难以精确实现本地地址隔离、专用数据模型和自定义看板。

## 4. 岗位来源适配器策略

JobSpy 上游目标是为多个招聘站点提供统一 Python 接口。但本项目当前锁定的 `python-jobspy==1.1.13` 在实际运行时只暴露 `linkedin`、`indeed`、`zip_recruiter` 三个 Site 枚举，不得把上游新版功能当成当前锁定依赖已具备的能力。

2026-08-18 的有限 Live 只读验证结果是：

- Indeed 返回 HTTP 403；
- LinkedIn China 返回 HTTP 451；
- 未绕过限制，也未将失败冒充为公开来源已完成。

必须把它封装为可替换适配器，而不是写进领域逻辑，原因包括：

- 招聘站点会限流或改变页面；
- 不同国家和来源的支持程度不同；
- 部分站点可能需要代理或会返回 429；
- 项目禁止绕过验证码、安全拦截或登录限制；
- Demo 只承诺至少一个合法可用来源，不承诺 JobSpy 的全部来源持续可用。

Live 接入优先级因此调整为：

1. 优先公司公开 ATS/Job Board GET API，首个已实现来源为 Lever Postings API；
2. JobSpy 保留为最善努力的可替换适配器；
3. 任何来源都必须限频、标注来源和失败，不绕过登录、验证码或区域/合规限制；
4. Lever 的申请 POST API 不属于当前 Demo，即使技术上可用也禁止调用。

### 4.1 v0.7 保留的实际验证

`LeverJobAdapter` 已按上述方案实现。一次性验证脚本使用虚构香港位置、公开地标 `Hong Kong`、临时数据库和 `binance` 公开 Job Board，取得 3 条公开职位。请求只包含 `mode`、结果上限和附近地标；响应未包含可靠坐标，因此系统保留职位并标记 `location_unresolved`，没有把地点文本猜成坐标。`binance` 只是可复现的公开技术样例，不代表用户长期目标公司；正式白名单和频率仍是本地配置。

## 5. MarkItDown 与材料导入

MarkItDown 支持 PDF、Word、PowerPoint、Excel、图片 OCR、音频转录、HTML、JSON、ZIP 等格式，并可将结构保留为 Markdown。它拥有当前进程的 I/O 权限，因此实现必须：

- 只使用 `convert_local` 或流式本地转换等最窄入口；
- 把上传材料复制到受控临时目录；
- 校验大小、扩展名、MIME、哈希和解压边界；
- 禁止由材料内容触发任意 URL 访问或文件路径读取；
- 本地转换完成后再决定是否把最小文本片段交给远端模型。

## 6. JSON Resume 与 Reactive Resume

旧的 `jsonresume/resume-schema` 仓库已于 2026-06-12 归档，持续维护已迁移到 `jsonresume/jsonresume.org/packages/schema`。实现不能依赖旧仓库地址。

内部简历草稿参考 JSON Resume 的 `basics`、`work`、`education`、`skills`、`projects` 等结构，但额外保留 provenance、置信状态和变更历史。Reactive Resume 的实时预览、多格式导出和自托管能力值得参考，但完整项目体量过大，不作为本项目基座。

## 7. 为什么不以 Khoj 为基座

Khoj 已具备本地知识、Agent、互联网研究和自动化能力，但它面向通用“第二大脑”，范围远大于当前三个闭环；其 AGPL-3.0 许可证也会扩大后续分发约束。直接基于 Khoj 修改会迫使业务迁就上游架构，因此只作为产品和能力参考。

## 8. 上游引入操作

实施阶段按以下方式引入 FastAPI 模板：

1. 先提交本项目的 goal 与治理基线；
2. 将上游仓库 clone 到 `/tmp` 下的唯一临时目录；
3. 读取上游许可证、Agent 指令、依赖和最新 commit；
4. 把选定 commit SHA 记录到实现日志；
5. 只导入已声明的 backend、frontend、测试和容器相关路径；
6. 不复制上游 `.git`、密钥、示例 `.env` 值或工作区 Agent 指令；
7. 单独提交“上游基座导入”，再开始本地裁剪；
8. 保留 MIT 许可证归属和来源说明。

JobSpy、LangGraph、MarkItDown 和 JSON Resume schema 通过依赖管理器固定版本，不复制其完整仓库。

## 9. 2026-08-19 岗位雷达呈现选型

### 9.1 候选结论

| 候选 | 优点 | 局限 | 本项目结论 |
| --- | --- | --- | --- |
| [Leaflet](https://leafletjs.com/) | 官方说明核心约 42 KB、无外部依赖，Marker/GeoJSON/CSS 定制成熟 | 最顺手的是栅格瓦片；深色矢量街道样式与高频动态层需要额外插件或自建方案 | 最轻回退候选，不作为首选 |
| [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/) | TypeScript + WebGL 直接渲染矢量瓦片；样式、source/layer、marker 和事件完整；官方给出 Vite ESM/worker 接入 | 比 Leaflet 重，需要 WebGL 和 worker；必须控制本地资产与 CSP | **首选渲染器** |
| [OpenLayers](https://openlayers.org/) | GIS 能力最完整，投影、栅格/矢量分析丰富 | 当前只需街道底图与点层，能力和 API 面过大 | 不采用 |
| deck.gl / Cesium | 大规模可视化或 3D 能力强 | 不是轻量街道底图的最短路径，增加 GPU 与集成复杂度 | 不采用 |
| 自绘 Canvas/SVG 雷达 | 极轻、视觉完全可控 | 需要自行处理街道拓扑、缩放、标注、裁剪和命中测试，不是可复用地图模块 | 只用于扫描扇区等覆盖效果 |

### 9.2 本地底图与隐私

[PMTiles](https://docs.protomaps.com/pmtiles/) 是只读的单文件瓦片金字塔格式，浏览器通过 HTTP Range 请求按需读取。官方文档明确列出 MapLibre、Leaflet 和 OpenLayers 集成，并把 MapLibre 推荐为平滑体验和自定义样式的方案。单文件比海量 `z/x/y` 文件更适合本机安装、版本和删除管理。

[Protomaps Basemaps](https://github.com/protomaps/basemaps) 可以从 OpenStreetMap 与 Natural Earth 生成 PMTiles，并提供 MapLibre 多主题样式、可下载的字体和 sprite。代码为 BSD-3、地图设计为 CC0、基于 OSM 的瓦片为 ODbL Produced Work，界面必须可见标注 `© OpenStreetMap contributors`，派生代码须保留许可证声明。

不能把 `tile.openstreetmap.org` 当成离线资源来源：OSMF 的 [Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/) 明确禁止批量预取和离线使用，要求离线场景使用自托管瓦片或明确允许离线的 Provider；其隐私章节也要求不要向服务提交个人或机密信息。本项目因此不把精确住所视口请求发送给 OSM、MapTiler 或其他外部地图服务。

底图包采用“用户选择公开城市/区域 → 一次性下载或本地生成 → 本机 Range 读取”的方式。下载条件只使用公开区域名或附近地标，不使用精确住址或以住所为中心的窄边界。地图包属于运行数据，不进入 Git。

### 9.3 悬浮窗选型

[Tauri 2 WindowConfig](https://v2.tauri.app/reference/config/#windowconfig) 原生提供 `alwaysOnTop`、`resizable`、`minWidth`、`minHeight`、`decorations` 和 `visibleOnAllWorkspaces`。它能直接复用当前 React/Vite 构建，并比 Electron 更适合作为单一雷达窗口的轻量宿主。

首版采用不透明、无标准标题栏但有应用内拖动/置顶/关闭控制的 420×420 窗口，最小 320×320。Tauri 文档说明 macOS 透明窗口需要 `macOSPrivateApi`，会影响 App Store 接受，因此透明/点击穿透不进入首版。

### 9.4 推荐组合

最终组合为：**Tauri 2 + 现有 React/Vite + MapLibre GL JS + PMTiles JS + Protomaps Basemaps + MapLibre GeoJSON/circle layer + CSS 扫描覆盖层**。2026-08-19 核验并计划固定的包版本是 [`maplibre-gl@6.4.1`](https://www.npmjs.com/package/maplibre-gl)、[`pmtiles@4.5.0`](https://www.npmjs.com/package/pmtiles)、[`@protomaps/basemaps@5.7.2`](https://www.npmjs.com/package/@protomaps/basemaps)、[`@tauri-apps/cli@2.11.4`](https://www.npmjs.com/package/@tauri-apps/cli) 和 [`@tauri-apps/api@2.11.1`](https://www.npmjs.com/package/@tauri-apps/api)；Rust 依赖使用同一 Tauri 2.11 发行线并由 `Cargo.lock` 固定。

直接使用 MapLibre API，不增加 `react-map-gl` 等包装层；这样依赖更少，也便于显式管理实例销毁、窗口 resize 和本地协议。岗位闪光点不引入 deck.gl，使用单一 GeoJSON source 与 circle paint 属性完成；岗位数量增长到数万且出现性能证据后再评估 deck.gl。
