# Last Summary

[Quick Link]
- TASK: T-036 — Fitness Coach Agent 本地实现与完整质量门已验证，待 API-only 发布
- TASK: T-037 — GitHub Actions CI 已实现，本地 Compose 链路已跑通
- DECISION: T-027 — Fitness Coach 独立 Graph 与 DeepSeek deepseek-chat 配置

[Current Focus]
- T-037 已新增 `.github/workflows/ci.yml`，覆盖后端、React、H5、敏感文件和 Compose 集成五道 CI 门；所有 Action 固定 SHA，生产部署不由 CI 自动触发。
- 本地等价 Compose 验证已通过，当前输出为 `jobs=3 facts=110 reports=25 checkpoints=788`；工作流安全审计无 findings。
- `goal/frontend-presentation-rules.md` 已成为所有手机端和 PC 端开发的强制完成门。
- 手机端已接入并固定 unibest + Wot UI 2.3.2；PC 端选定现有 React/Vite + Ant Design/按需 ProComponents，尚未开始通用页面迁移。
- 桌面窄视口模拟只允许作为预检；适用的移动端变更没有真实设备证据时不得再标记为已验证或部署完成。
- T-035 已完成 Fitness 七页、共享组件、主题令牌、Wot UI resolver 和状态一致性重构；未修改 API、数据库或生产服务器。
- T-036 已完成独立 Fitness Coach Graph、DeepSeek Provider 配置、只读工具、结构化建议表和自动触发；真实模型调用留待用户明日确认。

[Active Locks]
- T-037 lock released；T-036 lock 仍覆盖独立 backend、Goal、生产配置、提交、push 与 API-only 发布范围。

[Open Issues]
- ISS-016: `mitigated_pending_physical_validation`；本地多状态浏览器预检通过，真实手机验收仍未完成。

[Pending Review]
- 真实 iOS/Android 手机验收：系统字体放大、浏览器底栏、虚拟键盘、主要操作、返回、失败恢复和危险确认。
- Android and WeChat Mini Program remain structure-compatible only and are not acceptance-complete.
- DeepSeek 真实 Key、模型质量、延迟与成本验证：用户确认后再执行，今天不发起真实请求。

[Next Step]
- T-036 下一步：按白名单创建本地提交并 push；基于服务器真实部署版本仅替换 API 容器，自动迁移后做只读健康、认证、配置状态和 Fitness 计数核验。
