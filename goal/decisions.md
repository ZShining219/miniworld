# 决策记录

## 规则

- `Accepted`：当前实现必须遵守；
- `Proposed`：尚未锁定，不得当成强制实现；
- `Superseded`：已被新决策替代，保留历史；
- 产品与隐私决策只能在用户明确确认后改变；
- 技术决策可调整，但必须证明不改变根目录 `goal.md`。

## 已接受决策

| ID | 状态 | 决策 | 理由与约束 |
| --- | --- | --- | --- |
| P-001 | Accepted | 项目长期包含岗位发现、个人档案/简历、每日工作三个闭环 | 用户原始意图；三个闭环不得被技术合并为不可分割的通用聊天 Agent |
| P-002 | Accepted | Demo 岗位能力只做查找、整理、去重、更新和距离 | 匹配评分、投递跟踪、自动投递属于后续阶段 |
| P-003 | Accepted | 岗位距离先使用直线距离 | 结果必须明确标记，不冒充通勤距离 |
| P-004 | Accepted | 精确住址只在本地；对外使用附近变动地标 | 精确住址、精确坐标不得进入外部请求或远端模型 |
| P-005 | Accepted | 职位搜索与个人档案/简历更新隔离 | 发现职位不能直接修改简历，当前也不依赖档案进行岗位匹配 |
| P-006 | Accepted | 个人材料优先支持文件、GitHub 和 GPT 对话手动导入 | 不直接读取在线 AI 账号历史 |
| P-007 | Accepted | 每日工作 Demo 只做主动记录、日报和周报 | 自动采集电脑活动暂缓 |
| P-008 | Accepted | 允许定时公开读取和限定本地更新；外部写入必须确认 | 投递、消息、上传、登录授权和平台修改不能自动执行 |
| P-009 | Accepted | 本地优先但允许受控远端 AI | 模型只获得已授权的最小材料；本地 Agent 保留权限和持久化主权 |
| T-001 | Accepted | 使用 Docker Compose 本地运行 | 当前本机存在 `docker-compose 5.1.4`，首个验证平台为 ARM64 |
| T-002 | Accepted | FastAPI 官方全栈模板作为应用基座 | 技术成熟、市场认可高；必须固定 commit 并裁剪多用户/云功能 |
| T-003 | Accepted | LangGraph OSS 作为本地 Agent 编排核心 | 支持持久状态、checkpoint 和确认节点；不使用其云平台作为必需项 |
| T-004 | Accepted | React/TypeScript + FastAPI + PostgreSQL | 延续成熟模板栈，适合前端看板、结构化数据和 Graph checkpoint |
| T-005 | Accepted | JobSpy 仅作为可替换职位适配器 | 来源不稳定且有限流；领域逻辑不能依赖单一抓取库 |
| T-006 | Accepted | MarkItDown 用于受控本地材料转换 | 支持多格式；必须限制文件权限、路径和网络行为 |
| T-007 | Accepted | JSON Resume 只作为简历草稿 schema 参考 | 保持可移植性，同时增加证据、置信与版本字段 |
| T-008 | Accepted | 远端模型通过统一 `ModelProvider` 接口注入 | 避免绑定单一厂商，并集中执行数据最小化、授权与审计 |
| T-009 | Accepted | PostgreSQL 同时承载业务数据和 LangGraph checkpoint | 减少 Demo 服务数量；Redis/Celery 暂不引入 |
| T-010 | Accepted | 独立 Worker 使用 APScheduler 触发 Graph | 调度配置保存在 PostgreSQL；不在前端或 API 请求进程中运行定时任务 |
| T-011 | Accepted | LangGraph 完全本地运行，不把 LangGraph Cloud 或 LangSmith 设为依赖 | OSS Python 包运行在 API/Worker 容器；PostgreSQL 保存 checkpoint，远端仅是可选模型推理 |
| T-012 | Accepted | Demo 同时提供无密钥确定性模式和显式启用的 Live 模式 | 确保本地冷启动可复现，同时不把替身数据冒充真实联网结果 |

## 尚未锁定但已明确不阻塞 Demo

| ID | 状态 | 事项 | 当前默认 |
| --- | --- | --- | --- |
| O-001 | Proposed | 最终前端雷达视觉形式 | 先实现表格、距离排序和运行状态 |
| O-002 | Proposed | 最终简历版式与导出格式 | 先实现版本化 JSON 草稿 |
| O-003 | Proposed | 长期职位来源组合 | Demo 以一个合法可用来源加测试适配器验收 |
| O-004 | Proposed | 具体远端模型厂商和模型名 | 首期实现 OpenAI/GPT 类 Provider，配置决定实际模型 |

## 技术价值与产品边界说明

本项目把 LangGraph、结构化模型输出、PostgreSQL checkpoint、FastAPI、React/TypeScript、Docker 和自动化测试作为可验证工程能力，而不是把“多 Agent 数量”当作先进程度。技术展示必须服从 `P-001`—`P-009`：不能为了作品复杂度增加自动投递、无限工具权限、未经授权的数据外发或三个闭环之间的隐式耦合。

## 变更模板

新增或替代决策时记录：

```text
ID:
日期:
状态:
主题:
原决策:
新决策:
用户确认依据:
影响范围:
如何证明不偏离 goal.md:
回滚方式:
```
