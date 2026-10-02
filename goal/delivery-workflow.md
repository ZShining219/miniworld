# Agent 交付流程

本文件是 MiniWorld 的项目管理与 Vibe Coding 交付协议。它把一次“想法 → 修改 → 可运行结果 → 可审阅变更 → 可发布版本”拆成可追踪状态，并定义 Agent 可以自主完成的动作和必须停下来请求用户确认的动作。

## 1. 角色与责任

| 角色 | 负责事项 |
| --- | --- |
| 用户/产品负责人 | 确认目标、范围、外部账号/数据授权、合并与生产发布批准 |
| Agent/实现负责人 | 读取目标和治理状态、声明范围、实现、测试、提交、推送分支、创建 PR、观察 CI、整理证据和提出部署请求 |
| GitHub Actions | 在 push/PR 上运行五道 CI 门，并将结果作为 `main` 合并条件 |
| 生产发布脚本 | 只从 `origin/main` 的祖先提交发布；备份、构建、健康检查、认证边界和失败回滚 |

Agent 可以代替执行重复的工程动作，但不能代替产品负责人批准改变线上状态或向第三方发送敏感数据。

## 2. 标准状态机

每个任务在 `.ai/task_pool.ndjson` 中按事件推进，`.ai/current_state.json` 只作为缓存：

`proposed` → `claimed` → `implementing` → `local_verified` → `committed` → `pushed` → `pr_open` → `ci_verified` → `ready_for_merge` → `merged` → `deploy_requested` → `deployed` → `post_deploy_verified` → `closed`

允许的异常状态：

- `blocked`：缺少用户决定、授权、环境或外部服务；必须记录阻塞原因和解除条件。
- `pending_review`：代码或视觉/真实设备证据不足，不能宣称完成或部署。
- `failed`：测试、CI、部署或回滚失败；保留日志摘要和下一步，不删除失败历史。

每个窗口必须执行：生成 `session_token` → `TASK_CLAIMED` → `LOCK_ACQUIRED` → 捕获 scope manifest → 修改 → 作用域审计 → 更新日志/状态 → `LOCK_RELEASED` → `WINDOW_CLOSED`。

## 3. Agent 自主权限矩阵

| 动作 | 默认行为 | 停止并请求用户确认的条件 |
| --- | --- | --- |
| 读取仓库、目标、治理事件 | 自动 | 发现锁冲突、目标不清或状态矛盾 |
| 创建 `codex/<task-name>` 分支 | 自动 | 需要改写已有分支或从非 `origin/main` 开始 |
| 本地编辑、测试、生成临时文件 | 自动（限声明 scope） | 超出 scope、触碰真实个人材料/密钥/数据库/日志 |
| 本地 commit | 自动 | preflight 失败、diff 含敏感或不明文件 |
| push 代码分支到 GitHub | 自动 | 仅限通过 preflight 的代码/文档；若含个人数据、密钥或其他敏感内容必须确认 |
| 创建/更新 PR | 自动 | PR 将包含敏感信息、外部上传或需要改变权限/仓库设置 |
| 等待并核对 CI | 自动 | CI 失败、分支落后或检查名称与保护规则不一致 |
| 合并 PR 到 `main` | 请求确认 | 永远不能静默合并；需要用户明确批准 |
| 生产部署请求 | 主动提出 | 只有全部发布条件满足时提出，不自动执行 |
| 执行生产部署 | 请求确认后执行 | 必须有用户对目标 SHA 和服务器发布的明确批准；脚本还要求 `MINIWORLD_DEPLOY_APPROVED=1` |

本矩阵是对“常规、无敏感数据的项目源代码推送”的窄授权，不包括求职投递、消息、上传、登录授权、远端模型数据外发或其他第三方写入。

## 4. 每次 Vibe Coding 任务的执行清单

### 4.1 开始前

1. 读取 `goal.md`、`goal/README.md`、相关实现文档、`.ai/last_summary.md`。
2. 检查最新任务事件、活动锁和 `origin/main`；有冲突时不接管。
3. 声明目标、验收标准、排除范围和需求编号，写入 `TASK_CLAIMED`/`LOCK_ACQUIRED`。
4. 从 `origin/main` 创建 `codex/<task-name>`，不直接在 `main` 开发。

### 4.2 实现后

1. 运行 `scripts/agent-delivery-preflight.sh`。它至少检查分支、scope 变更、`git diff --check`、敏感文件和与变更面匹配的测试。
2. 失败时修复或记录 `failed`/`blocked`，不得通过删除测试、放宽扫描或强制提交绕过。
3. 只提交当前任务范围，提交信息使用 `feat:`, `fix:`, `test:`, `docs:`, `chore:` 等可读前缀。
4. 追加 `implementation-log.md`，记录命令、结果、未完成项和证据链接。

### 4.3 GitHub 链路

```bash
git fetch origin
git switch -c codex/<task-name> origin/main
scripts/agent-delivery-preflight.sh
git add <allowlisted-files>
git commit -m "<type>: <short summary>"
git push -u origin codex/<task-name>
```

Agent 随后创建目标为 `main` 的 PR，使用 `.github/pull_request_template.md`。PR 必须保持最新、解决讨论，并通过以下五项保护检查：`Backend checks`、`React checks`、`H5 shell checks`、`Sensitive file scan`、`Compose demo verification`。CI 失败时 Agent 只修复分支并等待新一轮结果，不绕过保护。

### 4.4 合并后

合并属于外部写入，必须得到用户确认。合并后 Agent 应：

1. `git fetch origin` 并确认目标 SHA 位于 `origin/main`；
2. 重新运行与发布相关的本地静态检查；
3. 判断是否满足第 5 节的生产发布条件；
4. 满足时发出结构化部署请求，否则明确说明为什么不部署。

## 5. 何时主动发出生产部署请求

Agent 只有在以下条件全部满足时才主动提出部署请求：

- 目标提交已合并到 `main`，且可由 `origin/main` 解析；
- PR 的五项必需 CI 全部成功，分支无冲突；
- `scripts/agent-delivery-preflight.sh`、敏感扫描和相关发布静态检查成功；
- 改动属于生产允许范围，并没有 `pending_review`、未完成迁移说明或未解决回滚风险；
- 若触及移动端呈现，`goal/frontend-presentation-rules.md` 要求的真实设备证据已经具备；
- 已准备目标 SHA、变更摘要、备份位置、健康检查和回滚 SHA。

以下情况不主动部署：仅文档/测试变更、CI/开发工具变更、真实手机验收未完成、远端 Provider/密钥未授权、数据库迁移缺少备份方案、任务仍有未解决的隐私或安全阻塞。

部署请求格式：

```text
部署请求
目标环境：production
目标 SHA：<40 位 SHA，必须来自 origin/main>
变更范围：<模块/迁移/前端呈现>
CI：<PR URL>；五项检查全部通过
本地验证：<命令与结果>
备份/回滚：<备份计划与 previous SHA>
风险与待审：<无，或明确列出>
请求：是否批准将该 SHA 发布到生产服务器？
```

只有用户明确批准后，才在服务器执行：

```bash
MINIWORLD_DEPLOY_APPROVED=1 \
  /srv/miniworld/scripts/deploy-production.sh <40-character-main-sha>
```

脚本会拒绝未批准执行、非 `origin/main` 祖先提交、无权限生产环境文件或失败健康检查，并在已有部署时保留数据库备份和应用回滚路径。部署完成后必须做只读健康、认证边界、迁移头和关键数据计数验证；失败则进入 `failed`，不宣称发布成功。

## 6. 证据与关闭标准

任务只有在以下证据齐全后才能关闭：

- scope 审计无未解释的越界文件；
- 本地 preflight 与风险匹配的测试结果已记录；
- Git commit、远端分支和 PR URL 可追溯；
- PR CI 运行 ID 与五项检查结果已记录；
- 合并/部署是否发生、批准人和目标 SHA 清楚；
- 未完成项进入 `pending_review` 或 `open_issues`，而不是写成“已完成”。

该协议不要求每个任务都部署生产；它要求 Agent 在能安全发布时主动提出请求，在不满足条件时明确停在可审阅状态。
