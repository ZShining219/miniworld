# 实施计划

> 对齐基线：根目录 `goal.md` v0.9
>
> 当前执行分支：`codex/bootstrap-langgraph`
>
> 当前阶段：Phase 1—9 已验证；Phase 10 Fitness 生产栈已发布 T-033，T-035 H5 呈现体系已在本地完成，等待真实手机复测；微信小程序与 Android/HBuilderX 仍只具备结构兼容性

## 当前阶段事实

| 项目 | 状态 | 证据/说明 |
| --- | --- | --- |
| Goal 与治理基线 | 已完成 | v0.7 意图审计 commit `fcb58c5`；v0.8 岗位雷达目标、实现、验证和治理证据已由 T-013 收口为本地检查点 |
| FastAPI 模板固定与导入 | 已完成 | upstream `162344da111e833b30892728372ab95331f06873`；commit `0ff0ea0` |
| 单用户裁剪 | 已验证 | 多用户/邮件路径已移除；当前 22 项后端测试与四服务容器 E2E 通过 |
| LangGraph 三闭环 | 已验证 | 三个独立 Graph、PostgreSQL checkpoint、失败历史和同线程可恢复重试均有证据 |
| 前端与 Worker | 已验证 | 六个看板页面和独立 Radar 可访问，Playwright 9 项通过，Worker 完成真实定时触发 |
| Compose/ARM64 | 已验证 | 经典 builder 可冷构建；`frontend/api/worker/db` 启动、回环端口、迁移和重启持久性通过 |
| Live 岗位 | 已验证 | Lever 公开 Job Board GET 以虚构位置和公开地标完成临时库端到端验证；3 条公开职位，无外部写入 |
| 真实远端模型 | 可选、待授权 | OpenAI Responses Provider 与 schema 已实现；真实调用不是 Demo 门，只有用户选择 Provider、模型和数据类别后才验证 |
| 公开 push | 已执行 | 用户授权后完成 secret/PII/文件范围检查；`origin/codex/bootstrap-langgraph` 已包含 T-033 发布提交 |
| 岗位雷达 | Phase 7 已验证 | `/radar`、本地 PMTiles Range、最小化场景 API、HOME 中心、黄色脉冲、未解析过滤、API/WebGL/缺图状态、三档窗口与 Tauri 2 ARM64 原生悬浮窗均已通过 |
| 多端系统壳 | Phase 8 Web 已验证 | unibest 4.4.1 已按固定 commit 导入；锁定安装、类型检查、21 项单测、H5 构建及桌面/手机浏览器验收通过，本地服务只绑定 `127.0.0.1:9000` |
| Fitness 辅助工具 | Phase 9 H5 已验证 | 首页 `04 健身记录`；独立 Fitness 数据表、后端包、前端模块和六个页面；27 项后端测试与 27 项 Shell 测试通过 |
| Fitness 生产部署 | Phase 10 已运行 | 临时域名 `103-52-153-212.sslip.io`；T-033 固定 SHA 发布、自动备份、迁移、健康/认证边界和数据计数通过；新增动作切换、重量输入/档位和趋势图等待真实手机复测 |
| Fitness H5 呈现体系 | T-035 本地完成，待真实手机验收 | `@wot-ui/ui` 2.3.2、官方 resolver、语义主题令牌、七页模板与状态一致性重构已完成；TypeScript、65 项前端测试、scoped ESLint、H5 构建及 320/360/390/430/1280/1440 浏览器预检通过；真实设备与生产发布仍未完成 |
| Fitness Coach Agent | T-036 后端已部署，真实 Provider 待验证 | 独立 `FitnessCoachGraph`、DeepSeek `deepseek-chat` 配置、只读工具、结构化建议、自动触发、审计与 `20260903_0005` 迁移已在 API-only 生产发布中验证；生产未配置 Key，保持 `awaiting_configuration`，未发起真实模型请求，Web 容器未替换 |

以上状态只陈述仓库事实。“本地 Demo 已验证”不等于“Live 互联网能力已完成”，也不等于已可执行投递或其他外部写入。

## 执行原则

- 严格按阶段推进；前一阶段验收未通过，不进入后一阶段；
- 每阶段使用独立 `codex/` 分支和可回滚提交；
- 功能以三个端到端闭环为单位交付，不以“安装了框架”作为完成；
- 新增功能必须对应根目录 `goal.md` 的范围或验收项；
- 外部依赖固定版本，上游导入固定 commit；
- 精确住址、个人材料、API 密钥和运行数据不得提交 Git。
- 所有功能提交和验证记录使用 `REQ-JOB`、`REQ-PROFILE`、`REQ-WORK`、`REQ-PRIVACY`、`REQ-RUNTIME` 中至少一个需求编号；
- 默认先让无密钥的 `demo` 模式稳定通过，再启用依赖真实来源或远端模型的 `live` 验证。
- 所有手机端和 PC 端界面变更必须通过 `goal/frontend-presentation-rules.md`；没有真实手机证据时不得宣称移动端已验证。
- 手机端后续呈现变更先接入 Wot UI 2 和主题令牌，PC 端后续通用页面变更先接入 Ant Design；禁止继续扩散页面级手写通用控件和任意视觉值。
- 所有 Vibe Coding 任务遵循 `goal/delivery-workflow.md`：Agent 可在 preflight 通过后自主完成代码分支 push、PR 创建和 CI 观察；合并与生产部署仍需用户确认。

## Phase 0：文档、Git 与上游基线

操作：

1. 以 `goal.md` v0.3 完成初始执行确认，并在后续实现中持续对齐当前 v0.8；
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
12. 建立明确的 `demo`/`live` 运行模式和界面标识，默认使用确定性适配器启动；
13. 为每次 Agent 运行保存 Graph 名称、模式、触发方式、checkpoint/thread ID、当前节点和错误码。

阶段验收：

- `docker-compose up --build` 可启动四个服务；
- API、Worker 和数据库重启后 Graph checkpoint 仍存在；
- 前端只能获得精确位置“已配置/未配置”和掩码，不返回完整值；
- 三个 Graph 无跨模块写权限；
- 远端 Provider 未配置时不会产生网络调用。
- 无 API 密钥时三个 Graph 仍可用确定性替身进入可演示状态，且所有替身结果带有 `demo` 标记。

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

v0.7 状态：固定数据、幂等、本地距离、手动/定时触发均通过；Lever Live 公开 GET 和“地点无法解析”的状态/原因也已通过一次性集成与前端 E2E 验收。

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
- 作品证据：三个 Graph 图示、一次 checkpoint 恢复、一次策略阻断、一次 schema 校验失败和三个端到端成功路径均有可复现记录。

文档：

1. 编写根目录 `README.md`；
2. 提供 `.env.example`，只包含占位符；
3. 记录模型 Provider 配置、数据外发说明和撤销方式；
4. 记录已知来源限制和合法使用边界；
5. 逐项执行 `goal.md` 验收清单；
6. 更新实现日志和决策记录；
7. 生成 `demo-v0.1` 本地 tag；
8. secret/PII 检查通过并获得用户确认后才 push 到公开 origin。

### Demo 冻结门

只有同时满足以下条件才能创建 `demo-v0.1` tag：

1. 根目录 `goal.md` 10.1—10.6 的每项都有通过证据或明确、经用户接受的延期记录；
2. `demo` 模式在全新本地数据卷上可按 README 冷启动；
3. 至少一个真实公开职位来源在 `live` 模式完成受规则约束的只读验证；如因来源合法可用性暂不可完成，必须记录阻塞，不能以固定数据冒充；
4. 所有精确地址、坐标、密钥和真实个人材料的泄漏扫描通过；
5. Git 工作树、第三方许可证、迁移和测试状态清楚；
6. 未执行任何未经用户确认的公开 push 或外部写入。

### v0.7 冻结判定

Demo 必选冻结门已全部通过：本地三闭环、Lever 公开只读来源、未解析地点、checkpoint 恢复、非法 schema、未配置 Provider 暂停、隐私扫描、四服务复现和测试均有证据。

当前不自行创建 `demo-v0.1` tag 或公开 push，因为二者属于发布动作而非运行缺口。用户审阅后可以依次选择：`创建本地 tag → 是否验证真实远端 Provider → 最终隐私复核 → 是否公开 push`。远端 Provider 验证可以跳过，不影响 Demo 完成结论。

## Phase 7：岗位雷达呈现

### 7.1 本地街道地图原型

1. 安装并固定 `maplibre-gl@6.4.1`、`pmtiles@4.5.0` 和 `@protomaps/basemaps@5.7.2`，记录 BSD-3 与 ODbL 归属，不引入 React 地图包装层；`@tauri-apps/cli@2.11.4`、`@tauri-apps/api@2.11.1` 和 Rust Tauri 2.11 发行线在 7.3 创建原生宿主时一并固定，避免原型阶段存在未使用的原生依赖；
2. 使用虚构区域的小型 PMTiles 与 3—8 个虚构岗位坐标建立 `/radar` 路由，先验证街道粒度、深色样式、HOME 中心和黄色脉冲；
3. 将 PMTiles、glyph、sprite 和 style 放入 Git 忽略的 `runtime-data/maps/`，通过支持 Range 的 localhost 端点读取，浏览器网络测试禁止任何外部瓦片请求；
4. Radar 组件在 mount 时创建 MapLibre、注册 PMTiles protocol，resize 时调用 `map.resize()`，unmount 时销毁实例；
5. 一个 GeoJSON source 承载岗位点；两个 circle layer 组成实心点和外扩光晕，动画只更新 paint 属性，不重复创建 DOM marker。

验收：Vite 生产构建通过；虚构中心的街道和岗位点可见；无外部地图请求；空岗位、地图包缺失、WebGL 不可用均有明确状态。

### 7.2 本地场景接口与隐私门

1. 新增 `GET /api/v1/radar/scene`，只返回本机渲染所需的中心经纬度、有可靠坐标的岗位 GeoJSON、未解析岗位计数和地图包状态，不返回精确地址文本；
2. 路由继续只通过 `127.0.0.1` 暴露并沿用同源/CORS 限制；响应设置 `Cache-Control: no-store`，前端不写 localStorage、日志或遥测；
3. 仅 `distance_status=calculated` 且坐标存在的岗位进入空间层；`location_unresolved` 只进入计数和列表入口；
4. 地图包的选择/下载只接受用户选择的公开城市或区域，不使用精确住址或家庭坐标生成外部请求；
5. 更新隐私测试：默认 `/location` 仍不回显原值；Radar 响应不含地址；前端、日志和网络记录中除 localhost 场景响应外不出现家庭坐标。

验收：场景 schema、过滤、空态和 no-store 测试通过；抓取所有非 localhost 请求，证明不存在精确地址、坐标或住所视口；普通 API/日志仍不泄漏地址。

### 7.3 Tauri 悬浮窗

1. 在仓库增加 Tauri 2 宿主，只承载 `/radar` 路由；不替换现有 Docker/浏览器看板；
2. 初始窗口 420×420、最小 320×320、最大建议 900×700、`alwaysOnTop=true`、`resizable=true`、`decorations=false`、不透明背景；
3. 顶部应用内控制条提供拖动、置顶切换、重新居中和关闭；保存窗口尺寸/位置，不保存地图中心或精确坐标；
4. 窗口尺寸变化后地图自适应，HOME 视觉锚点保持中心；首版不做透明窗口、点击穿透、全工作区兼容承诺或系统级开机启动；
5. Tauri 启动时若回环 API 不可用，显示启动说明而不是访问外部服务。

验收：macOS ARM64 原生开发构建与生产打包通过；人工验证置顶、拖动、320×320 与 900×700 resize、关闭/重开位置恢复；Playwright 验证 `/radar` 的响应式布局和无外网请求。

v0.8 状态：Tauri 2 原生宿主、最小 capability、几何持久化、原生浮动层、ARM64 未签名 release `.app`、本地 API 启动说明及浏览器隐私/响应式回归均已通过；默认仍使用明确标记的虚构 Demo 场景。

### 7.4 验证与提交边界

- 单元/API：场景 schema、坐标过滤、未解析计数、no-store、地址不回显；
- 前端：MapLibre 生命周期、resize、HOME 中心、黄色信号、空态/错误态；
- E2E：320×320、420×420、900×700 三档视口，点击岗位摘要并返回列表；
- 原生：Tauri macOS 构建、置顶与尺寸手工清单；
- 隐私/许可：网络拦截、bundle/log 扫描、地图包 Git 忽略、OSM attribution 可见；
- 提交顺序：`docs: select local job radar stack` → `feat: add offline radar map` → `feat: add local radar scene` → `feat: add tauri radar window` → `test: verify radar privacy and resizing`。

状态：Phase 7 验证门已全部通过，并由 T-013 完成提交前复核与本地检查点收口；未 tag、未 push。

## Phase 8：unibest 多端系统壳

1. 将 unibest 作为 `apps/miniworld-shell/` 独立 Vue 3/uni-app 工程导入，不替换 `frontend/` React 看板或 Tauri Radar；
2. 固定上游 `base` commit，保留 MIT 许可证，不复制上游 Git、Agent 与编辑器指令；
3. 移除示例远端 API、AppID、自动嵌套 Git 初始化、远端 Eruda 和 Android 默认敏感权限；Web 仅绑定 `127.0.0.1`；
4. 建立总览、岗位、档案和工作四个空白入口，三个业务模块保持独立边界并明确标注“待接入”；
5. 本轮验证依赖锁、类型检查、测试、H5 生产构建及手机/桌面响应式页面；微信小程序构建与 Android/HBuilderX 出包按用户指令暂缓。

阶段验收：`pnpm install --ignore-scripts --frozen-lockfile`、`pnpm type-check`、`pnpm test:run`、`pnpm build:h5` 已通过；浏览器确认四个入口、桌面与手机视口均无横向溢出，控制台无 warning/error，页面资产请求均为 localhost。微信小程序和 Android/HBuilderX 不属于本次验收。

## Phase 9：Fitness H5 Demo

1. 在现有 PostgreSQL 中增加计划、计划动作、训练 Session 和训练 Set 四张表；SQLite 继续用于测试，不新增数据库或缓存；
2. 以 `backend/app/fitness/` 独立封装模型、schema、repository、service、router 和 Demo seed，只通过 `/api/v1/fitness/*` 接入总 API；
3. 在首页模块注册表登记 `04 健身记录 → /pages/fitness/index`，Fitness 不进入主 TabBar；
4. 在 `modules/fitness` 和 `pages/fitness` 实现训练首页、计划训练、动作记录、历史、统计和计划管理；正式数据只来自 API，本地只留未提交输入草稿；
5. 完成 Active Session 单例/恢复、逐组即时保存、Set 幂等与顺序、历史快照、软删除保护、Completed-only 统计和下次训练默认值；
6. 用自动化与实际浏览器流程验证卧推 `80×8、80×8、75×10` 和上斜卧推两组，确认历史、日历、进度与下次默认值。

阶段验收：后端 27 项测试、Fitness Ruff/Mypy/Ty、Shell 27 项测试、TypeScript、限定范围 ESLint 和 H5 production build 均通过；桌面 `1440×900` 与手机 `390×844` 浏览器流程通过，控制台无 warning/error。Android 和微信小程序未构建或验收。

## Git 与 Agent 交付策略

完整状态机、责任分工、测试选择、PR 门禁和部署请求模板见 [`delivery-workflow.md`](delivery-workflow.md)。

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

每次提交必须可构建或明确标记为仅文档/脚手架提交。提交前运行 `scripts/agent-delivery-preflight.sh`；禁止把真实数据、导入文件、数据库卷、日志、密钥或生成简历提交到任何分支。生产脚本只接受已合并到 `main` 的 SHA，并要求显式批准环境变量。
