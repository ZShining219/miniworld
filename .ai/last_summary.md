# Last Summary

[Quick Link]
- TASK: T-034 — 前端呈现硬性规则与 AGENTS 强制入口已完成
- DECISION: D-028 — 手机 Wot UI 2、PC Ant Design 与真实设备验收门
- ISSUE: ISS-016 — 当前 Fitness 生产移动端呈现待体系化重构

[Current Focus]
- `goal/frontend-presentation-rules.md` 已成为所有手机端和 PC 端开发的强制完成门。
- 手机端选定 unibest + Wot UI 2，PC 端选定现有 React/Vite + Ant Design/按需 ProComponents；两者尚未执行依赖接入。
- 桌面窄视口模拟只允许作为预检；适用的移动端变更没有真实设备证据时不得再标记为已验证或部署完成。

[Active Locks]
- None after T-034 handoff.

[Open Issues]
- ISS-016: 当前 Fitness 生产移动端呈现不符合新的组件、状态和真实设备验收规则。

[Pending Review]
- Wot UI 2 与主题令牌接入后，按页面模板和状态矩阵重构 Fitness，再进行真实手机验收。
- Android and WeChat Mini Program remain structure-compatible only and are not acceptance-complete.

[Next Step]
- Start a separately scoped frontend refactor: integrate Wot UI 2 first, then resolve ISS-016 without changing API or production data.
