# 跨对话执行指南

这份文档是给下一次对话中的 AI 看的。它定义了任务开始、执行、分派和收尾时的固定动作。用户不需要再次解释 Loop Engineering 规则；AI 必须先读取本文件对应的 Skill，以及目标项目中的 `.agent/README.md` 和 `.agent/constitution.md`。

## 每次新对话开始

1. 确认当前工作目录和目标项目。
2. 读取宿主规则入口：`CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、Copilot 或 Cursor 规则，实际存在什么就读取什么。
3. 读取 `.agent/README.md`、`.agent/constitution.md`、`.agent/runtime.yaml`、`.agent/state/current.yaml`、`.agent/index/knowledge-index.yaml`。
4. 运行 `python .agent/compiler/cli.py doctor --json` 和 `status --json`。
5. 如果存在 `current_task_id`，先恢复该任务，不要创建重复任务；读取对应的 `.agent/tasks/`、最近 Event、Review 和 blocker。

## 接收新任务

先把用户请求转换为任务记录，至少写清目标、范围、排除范围、验收标准、风险和证据命令。涉及代码或文档变更时，先建立 PLAN，再修改文件。只问会改变范围或安全性的必要问题；其余信息按项目现有规则作最小假设并记录。

上下文必须通过 `context --task "..."` 生成。优先读取索引命中的文件、任务文件和当前状态；禁止把整个仓库、整个 `docs/` 或历史日志一次性塞进上下文。秘密、构建产物、无关模块和 superseded 文档默认排除。

## 执行和分派

默认运行时是 `L1/report_only`，可以发现、计划、生成上下文、检查和报告，但不能自动修改业务代码、合并、推送或部署。只有项目明确批准并满足 `runtime.yaml`、门禁、预算和 verifier 条件时才升级到 L2；L3 必须有人类批准。

主 Agent 保持全局状态、任务依赖、验收和最终汇总。只有任务可以独立、范围可限制、输入输出明确时才分派子 Agent。子 Agent 必须返回 changed files、测试命令及结果、证据、风险、阻塞项和 next action；不能直接修改全局状态。子任务结果先由独立 verifier 检查，verifier 只能返回 `APPROVE`、`REJECT` 或 `ESCALATE_HUMAN`，不能修改实现文件。

## 完成任务前

1. 执行与改动匹配的单元、集成和前端 E2E 测试；前端用户流程必须有浏览器、viewport、断言和报告/截图/trace 证据。
2. 执行 `python .agent/compiler/cli.py gate ...` 和 `validate`。
3. 更新 `.agent/state/current.yaml`，记录完成项、风险、阻塞项和下一步。
4. 写入 Event；只有经过审查的稳定经验才升级为 Lesson、Rule、Skill 或 Memory。
5. 最终报告必须说明改动、验证命令、证据、未完成项和下一次可直接继续的任务。

## 中断恢复

如果对话中断，下一次只从 `current.yaml`、当前 task、最近 Event 和 blocker 恢复。不要重新读取全部历史对话，也不要重新扫描全部仓库。若状态与工作区不一致，先报告差异并暂停高风险操作。预算达到 80% 时只做收尾和报告，达到 100% 或出现 `.agent/STOP` 时停止自动执行。
