# MiniWorld Agent 进度

> 更新时间：2026-08-18
>
> 分支：`codex/bootstrap-langgraph`
> 目标基线：`goal.md` v0.6

## 已完成并有证据

| 范围 | 状态 | 证据 |
| --- | --- | --- |
| Goal 与意图对齐 | 完成当前轮 | `goal.md` v0.6；v0.5 commit `2d6c1d2`；只剩真实远端模型授权验收未勾选 |
| 上游基座固定 | 完成 | FastAPI 模板 commit `162344da111e833b30892728372ab95331f06873`；本地 commit `0ff0ea0` |
| 单用户本地架构 | 完成 | `frontend`、`api`、`worker`、`db` 四服务；宿主端口仅回环绑定 |
| LangGraph 本地运行 | 完成 | 三个独立 Graph；PostgreSQL checkpoint；不依赖 LangGraph Cloud |
| 确定性岗位闭环 | 完成 | 3 个固定岗位、幂等去重、Haversine 距离、手动与 Worker 触发 |
| 档案与简历闭环 | 完成 | 文件、GitHub、GPT 对话材料；事实证据；版本化 JSON 草稿 |
| 工作沉淀闭环 | 完成 | 主动记录、日报、周报、来源记录；不自动写入档案 |
| 本地看板 | 完成 | Overview、Jobs、Profile、Work、Agent Runs、Settings |
| 容器持久性 | 完成 | PostgreSQL、API、Worker、前端重启后业务数据和 checkpoint 保持 |
| 自动化测试 | 完成当前范围 | Pytest、Ruff、Mypy、Ty、前端构建、Biome、Playwright、容器 E2E |
| Lever Live 公开读取 | 完成 | 虚构位置 + `Hong Kong` 公开地标 + 临时数据库；返回 3 条职位，无精确位置泄漏或外部写入 |
| 失败恢复 | 完成 | PostgreSQL 同线程 checkpoint 恢复、失败历史、成功后重复重试 409、业务写入计数验证 |

## 已验证的最近结果

- `./scripts/test.sh` / `./scripts/verify-demo.sh`：重建、三闭环、Worker 定时、真实 checkpoint 恢复、端口与重启均通过；最近记录 `jobs=3 facts=110 reports=25 checkpoints=548`；
- `scripts/verify-live-lever.py`：真实 Lever 公开 GET 通过，`source=lever`、`execution_mode=live`、`job_count=3`、`exact_location_exposed=false`、`external_write_performed=false`；
- 后端：17 项测试通过，包含 Lever 请求边界、Provider 配置门、非法 schema 和内存 checkpoint 恢复；Ruff、Mypy、Ty 通过；
- 前端：生产构建通过；Biome 无错误、保留 8 条 CSS 风格 warning；Playwright 3 项通过；
- 真实浏览器：六个页面可访问；实际容器数据可见；控制台无 error/warning；请求仅访问本机 API；
- Docker：经典 builder 下可构建，不再要求 BuildKit cache mount；源码增量构建不再临时下载 Hatchling。

- 泄漏扫描：Git 候选文件、前端 bundle、公开 API 和 Docker 日志未发现非占位符 secret-like 值、精确演示位置或本机绝对路径；
- 真实浏览器：六个页面已在最新容器上复核，console 无 error/warning，设置页不回显精确坐标。

## 尚未完成

| 项目 | 原因 | 下一步 |
| --- | --- | --- |
| 真实附近地标 | 用户尚未提供，且不应写入 Git | 用户醒后只在本机 Settings 配置 |
| OpenAI 真实结构化调用 | 未提供 API Key 和数据类别授权 | 用户决定 Provider、模型和允许外发材料后本地配置 |
| 最终雷达/地图视觉 | 明确不阻塞 Demo | 后续产品阶段再决定 |
| 公开 Git push | 必须确认 | 完成最终 secret/PII 扫描后由用户决定 |

## 待用户决策

1. 求职目标地区及可用于公开查询的附近地标；精确门牌地址仍只在本机填写；
2. 长期允许的 Lever 公司 Job Board 名单，以及可接受的查询频率（当前 `binance` 仅作为公开验收默认值）；
3. 是否启用 OpenAI Provider、使用哪个模型、哪些材料类别允许外发；
4. 是否在最终审计后推送到公开 `origin`；
5. Demo 后优先推进匹配评分、投递跟踪还是雷达视觉。

## 当前安全边界

- 未提交或外发真实地址、坐标、个人材料、API Key、对话、数据库、日志或生成简历；
- 未执行职位投递、外部消息、文件上传、账号授权或平台修改；
- `demo` 与 `live` 结果在配置、运行记录和界面中分开标记。
