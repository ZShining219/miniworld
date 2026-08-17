# 技术与开源项目调研

> 调研日期：2026-08-18  
> 目标：寻找成熟、市场认可度高且不会改变项目意图的实现基座与组件

## 1. 选择结论

| 能力 | 选择 | 使用方式 | 结论 |
| --- | --- | --- | --- |
| 全栈工程基座 | [FastAPI Full Stack Template](https://github.com/fastapi/full-stack-fastapi-template) | 固定 commit 后选择性导入并裁剪 | 采用 |
| Agent 编排 | [LangGraph](https://github.com/langchain-ai/langgraph) | Python 依赖，三个独立 Graph | 采用 |
| 职位采集 | [JobSpy](https://github.com/speedyapply/JobSpy) | 首个 `JobSourceAdapter`，必须有限流和失败治理 | 采用为候选适配器 |
| 多模态文件转文本 | [Microsoft MarkItDown](https://github.com/microsoft/markitdown) | 本地依赖，只调用最窄的本地转换接口 | 采用 |
| 简历结构标准 | [JSON Resume](https://github.com/jsonresume/jsonresume.org/tree/master/packages/schema) | 作为内部简历草稿 schema 的参考 | 采用为参考 |
| 简历产品参考 | [Reactive Resume](https://github.com/AmruthPillai/Reactive-Resume) | 只参考交互、预览和导出思路 | 不作为基座 |
| 个人 AI 参考 | [Khoj](https://github.com/khoj-ai/khoj) | 只参考本地知识和定时研究思路 | 不作为基座 |

Star 数量是 2026-08-18 的页面快照，仅用于判断社区规模，不作为安全或质量保证：FastAPI 模板约 44.9k、LangGraph 约 39.9k、JobSpy 约 4.1k、MarkItDown 约 174k、Reactive Resume 约 40.8k、Khoj 约 36.5k。

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

未采用方案：

- CrewAI：多 Agent 演示直观，但当前任务以确定性工作流和权限边界为主；
- AutoGen：适合研究型多 Agent 会话，当前会增加不必要的自治复杂度；
- Temporal：通用 durable workflow 工程价值高，但对本轮 Demo 过重；
- Dify/n8n：工作流搭建快，但难以精确实现本地地址隔离、专用数据模型和自定义看板。

## 4. JobSpy 的适用与限制

JobSpy 提供 LinkedIn、Indeed、Glassdoor、Google Jobs 等来源的统一 Python 接口，输出字段与本项目职位 schema 接近，并支持 location、distance、job type、发布时间等参数。

必须把它封装为可替换适配器，而不是写进领域逻辑，原因包括：

- 招聘站点会限流或改变页面；
- 不同国家和来源的支持程度不同；
- 部分站点可能需要代理或会返回 429；
- 项目禁止绕过验证码、安全拦截或登录限制；
- Demo 只承诺至少一个合法可用来源，不承诺 JobSpy 的全部来源持续可用。

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
