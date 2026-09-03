# Last Summary

[Quick Link]
- TASK: T-037 — GitHub Actions CI 已实现，本地 Compose 链路已跑通
- TASK: T-035 — Fitness H5 呈现体系重构已完成本地实现
- DECISION: T-026 — Wot UI 2.3.2 resolver 与当前 uni 类型兼容边界
- ISSUE: ISS-017 — T-036 Coach 改动使完整 Ty 门当前失败

[Current Focus]
- T-037 已新增 `.github/workflows/ci.yml`，覆盖后端、React、H5、敏感文件和 Compose 集成五道 CI 门；所有 Action 固定 SHA，生产部署不由 CI 自动触发。
- 本地等价 Compose 验证已通过，当前输出为 `jobs=3 facts=110 reports=25 checkpoints=788`；工作流安全审计无 findings。
- `goal/frontend-presentation-rules.md` 已成为所有手机端和 PC 端开发的强制完成门。
- 手机端已接入并固定 unibest + Wot UI 2.3.2；PC 端选定现有 React/Vite + Ant Design/按需 ProComponents，尚未开始通用页面迁移。
- 桌面窄视口模拟只允许作为预检；适用的移动端变更没有真实设备证据时不得再标记为已验证或部署完成。
- T-035 已完成 Fitness 七页、共享组件、主题令牌、Wot UI resolver 和状态一致性重构；未修改 API、数据库或生产服务器。

[Active Locks]
- T-037 lock released; T-036 backend Coach task remains independent and is not included in this commit.

[Open Issues]
- ISS-016: `mitigated_pending_physical_validation`；本地多状态浏览器预检通过，真实手机验收仍未完成。
- ISS-017: 当前 `./scripts/test-local.sh` 的 Ty 阶段在 T-036 `backend/app/fitness/coach/graph.py` 和 `tools.py` 报两条字典索引类型错误；pytest 31 项、Ruff、Mypy 已通过，待 T-036 owner 修复后 CI 可全绿。

[Pending Review]
- 真实 iOS/Android 手机验收：系统字体放大、浏览器底栏、虚拟键盘、主要操作、返回、失败恢复和危险确认。
- Android and WeChat Mini Program remain structure-compatible only and are not acceptance-complete.

[Next Step]
- T-037 已完成本地提交；将该提交推送后，在 GitHub Actions 中观察一次 PR/push 运行。T-036 owner 需先修复 ISS-017，再将完整 Ty 门恢复为绿色。
