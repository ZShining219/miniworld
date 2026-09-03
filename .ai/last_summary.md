# Last Summary

[Quick Link]
- TASK: T-035 — Fitness H5 呈现体系重构已完成本地实现
- DECISION: T-026 — Wot UI 2.3.2 resolver 与当前 uni 类型兼容边界
- ISSUE: ISS-016 — 已缓解，等待真实手机验收

[Current Focus]
- `goal/frontend-presentation-rules.md` 已成为所有手机端和 PC 端开发的强制完成门。
- 手机端已接入并固定 unibest + Wot UI 2.3.2；PC 端选定现有 React/Vite + Ant Design/按需 ProComponents，尚未开始通用页面迁移。
- 桌面窄视口模拟只允许作为预检；适用的移动端变更没有真实设备证据时不得再标记为已验证或部署完成。
- T-035 已完成 Fitness 七页、共享组件、主题令牌、Wot UI resolver 和状态一致性重构；未修改 API、数据库或生产服务器。

[Active Locks]
- T-035 lock released; independent T-036 backend Coach task remains active in its declared backend scope.

[Open Issues]
- ISS-016: `mitigated_pending_physical_validation`；本地多状态浏览器预检通过，真实手机验收仍未完成。

[Pending Review]
- 真实 iOS/Android 手机验收：系统字体放大、浏览器底栏、虚拟键盘、主要操作、返回、失败恢复和危险确认。
- Android and WeChat Mini Program remain structure-compatible only and are not acceptance-complete.

[Next Step]
- T-035 feature commit: `a0c3df0` (`refactor: rebuild fitness mobile presentation system`). Obtain physical-device evidence before any production release; do not push or deploy this UI-only checkpoint yet.
