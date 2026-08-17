# 实现记录

本文件只追加事实，不重写历史。每次实现任务结束时记录范围、结果、验证、偏差和下一步。讨论和计划不冒充已实现能力。

## 2026-08-18 — Goal v0.2 技术化

### 范围

- 把根目录 `goal.md` 从产品基线升级为产品与 Demo 执行契约；
- 建立 `goal/` 文档目录；
- 固定 LangGraph + FastAPI 全栈模板 + PostgreSQL + React + Docker Compose 路线；
- 记录 JobSpy、MarkItDown、JSON Resume、Reactive Resume 和 Khoj 调研结论；
- 编写架构、分阶段计划和人类可读决策记录。

### 已完成

- 产品意图、模块隔离、地址隐私和外部确认边界已写成强约束；
- 三个独立 LangGraph 的节点、写权限和失败路径已定义；
- 本地容器拓扑、REST API 分组、领域接口和数据表已定义；
- 上游导入方式、Git 提交策略和 Demo 验收阶段已定义。

### 当前仓库事实

- 仓库尚无 Git commit；
- 当前分支为 `master`；
- 本地尚未配置 `origin`；
- 远端 `https://github.com/ZShining219/miniworld` 已确认存在且为空；
- 当前尚未 clone 或导入 FastAPI 模板代码；
- 当前尚未安装项目依赖或启动容器。

### 当前机器事实

- 架构：Apple Silicon ARM64；
- Docker：已安装；
- Compose：`docker-compose 5.1.4` 可用，`docker compose` 子命令不可用；
- Node.js：v24.14.0；
- npm：11.9.0；
- uv：0.11.24；
- 系统 Python：3.14.3，项目应在容器或 uv 中固定兼容版本，不直接依赖系统 Python；
- Ollama：0.17.4，本机存在 `qwen2.5:3b`，但远端 AI 是当前主要语义能力方向。

### 验证

- 已对照用户确认内容检查三个闭环；
- 已明确技术方案不得反向改变 `goal.md`；
- 已检查目录文件、标题层级和相对文档链接；
- 项目治理 scope audit 显示 7 个文档变更全部在声明范围内，没有范围外修改。

### 下一步

- 用户审阅 Goal v0.2；
- 进入 Phase 0：Git 基线与 FastAPI 模板固定 commit 导入。

---

## 后续记录模板

```md
## YYYY-MM-DD — 任务名称

### 范围
- 声明的文件与能力范围

### 已完成
- 实际完成内容

### 未完成
- 明确未完成或延期内容

### 验证
- 命令、测试、截图或人工检查结果

### 偏差与决策
- 与计划不同之处、原因、关联 decision ID

### Git
- 分支、提交、上游 commit、是否 push

### 下一步
- 唯一推荐的安全下一步
```
