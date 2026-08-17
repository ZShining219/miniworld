# Goal 文档目录

本目录把根目录 [`goal.md`](../goal.md) 中已经确认的产品意图转换为可执行的技术与操作指导。

当前对齐版本：`goal.md` v0.6。本地三闭环、四服务、Lever 公开只读来源、未解析地点、Provider 失败门和 PostgreSQL checkpoint 恢复已有证据；只剩“经用户授权的真实远端模型调用”未勾选。实现状态以 [`plan.md`](plan.md) 的“当前阶段事实”和 [`implementation-log.md`](implementation-log.md) 的最新追加记录为准；旧日志只代表当时事实。

## 文档优先级

发生冲突时从高到低处理：

1. 用户最新的明确指令；
2. 根目录 `goal.md`；
3. `decisions.md` 中状态为 Accepted 的决策；
4. `architecture.md`；
5. `plan.md`；
6. `research.md` 和 `implementation-log.md`。

任何下级文档不得静默放宽上级文档中的产品范围、隐私规则或外部确认边界。

## 目录内容

- [`architecture.md`](architecture.md)：容器、LangGraph、接口、数据模型、数据流和故障处理；
- [`research.md`](research.md)：成熟开源项目调研、选择、排除和引入方式；
- [`plan.md`](plan.md)：分阶段实施计划、验收门和 Git 操作；
- [`decisions.md`](decisions.md)：用户意图和技术路线的可追溯决策；
- [`implementation-log.md`](implementation-log.md)：只追加的实现、验证、偏差和后续动作记录。

## 使用方式

开始任务前：

1. 阅读根目录 `goal.md`；
2. 阅读本目录索引和当前任务对应文档；
3. 检查 `.ai/last_summary.md` 与最新事件；
4. 声明文件范围并取得治理锁；
5. 只实现 `plan.md` 中当前阶段允许的内容。

结束任务前：

1. 对照 `goal.md` 验收项；
2. 运行与变更风险相称的测试；
3. 在 `implementation-log.md` 追加事实记录；
4. 如发生决策变化，先更新 `decisions.md`；
5. 更新 `.ai/` 交接状态并释放锁。

## 防偏移检查

每次合并前必须能回答“是”：

- 是否仍然只服务本机唯一用户？
- 是否仍然保留三个独立闭环？
- 精确住址是否从未外发？
- 岗位发现是否没有直接修改简历？
- 远端模型是否只接收已授权、最小化的数据？
- 外部写入是否仍需用户确认？
- 新增技术是否解决当前阶段问题，而不是扩大产品范围？
- 确定性 Demo、真实联网结果和未来规划是否被清楚区分？
- 文件、GitHub 与 GPT 对话是否仍是当前优先的手动输入入口？
