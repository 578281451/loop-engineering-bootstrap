# Adaptive Agent Routing Design

**Status:** Proposed
**Date:** 2026-07-25

## Goal

让 Loop Engineering 根据任务复杂度选择合适的 Agent 协作规模：简单任务快速完成，复杂任务由主 Agent 统筹、执行 Agent 实施、善后 Agent 验证和沉淀，避免固定启动一组 Agent 造成流程膨胀。

## Design Principles

1. 主 Agent 是唯一的全局协调者，拥有任务状态、依赖、预算和最终汇总权。
2. 主 Agent 具备 S0 快速执行能力，不因为简单任务强制派发子 Agent。
3. 执行 Agent 只修改被分配范围，不直接修改全局状态和长期知识。
4. 善后职责按风险触发，不默认创建独立 Agent。
5. 所有运行都有 task id、attempt id、checkpoint 和 append-only 证据。
6. 文档和知识升级必须经过审查，执行结果不能直接变成项目规则。

## Runtime Modes

| Level | Criteria | Execution | Closing |
|---|---|---|---|
| S0 | 单文件或单模块、低风险、无数据/安全/生产影响 | 主 Agent 直接完成 | 主 Agent 内置检查 |
| S1 | 单一模块但有明确 Bug、需要回归测试或用户流程验证 | 主 Agent 直接完成，必要时启 verifier | 主 Agent 或轻量 verifier |
| S2 | 跨模块、跨服务、前后端联动或多个独立验收点 | 主 Agent 分派一个或多个受限执行 Agent | 独立善后/verifier 必须启用 |
| S3 | 数据迁移、安全、生产、架构或不可逆操作 | 主 Agent 规划，专项 Agent 执行 | 独立验证和人工审批必须启用 |

S0 and S1 are the fast path. The router must prefer the lowest level that
satisfies the risk and evidence requirements. File count alone cannot upgrade
a task; security, data loss, production, and architecture signals can.

## Roles

### Orchestrator (主 Agent)

- reads host rules and `.agent` state;
- normalizes the request and computes an idempotency key;
- creates or resumes the root task;
- scores complexity and chooses S0-S3;
- creates bounded child delegations only for S2/S3 or explicitly useful S1 work;
- owns global state, dependencies, budget, retries, and final report;
- accepts or rejects verifier results;
- proposes human escalation when required.

### Worker (执行 Agent)

- receives task id, scope, exclusions, inputs, acceptance criteria, and budget;
- writes only implementation files in its assigned scope;
- records tests and evidence;
- returns changed files, tests, evidence, risks, blockers, and next action;
- cannot change root state, gate policy, or durable knowledge.

### Closer / Verifier (善后 Agent)

- checks the implementation against acceptance criteria independently;
- reruns or inspects evidence and identifies omissions;
- returns `APPROVE`, `REJECT`, or `ESCALATE_HUMAN`;
- may update task/event/review records but never implementation files;
- proposes knowledge changes without applying them.

For S0, all three responsibilities may be performed by the Orchestrator in one
interactive run. They are responsibilities first and separate processes only
when risk or independence requires it.

## Routing Signals

The router evaluates:

- number of affected modules and services;
- frontend user journey or E2E requirement;
- database schema, migration, security, production, or architecture impact;
- number of independent acceptance criteria;
- reversibility of the change;
- whether a previous failed or interrupted attempt exists;
- whether independent verification is required by project policy.

The result is a machine-readable decision:

```yaml
level: S0
mode: single_agent
delegate: false
closer: inline
reason_codes: [one_module, low_risk, reversible]
required_evidence: [focused_test]
```

## Idempotency and Recovery

The root task key is:

```text
project_id + normalized_goal + scope + bug_signature
```

The runtime keeps separate `task_id` and `attempt_id` values. Repeated input
must behave as follows:

- active matching task: resume it;
- completed matching task: report the existing result and ask before reopening;
- interrupted task: resume from the last checkpoint;
- failed task: create a new attempt under the same root task;
- explicit user retry: create a new attempt, never a duplicate root task.

Each attempt records phase, status, checkpoint, changed files, evidence, error,
and next action. A lock or active marker prevents two attempts for the same
root task from mutating the same scope concurrently.

## Error Handling

Every tool or Agent failure creates an Event before retry. Retries are bounded
and preserve the previous attempt. A second failure in the same phase escalates
to the Orchestrator; repeated safety, permission, or data-loss failures become
`ESCALATE_HUMAN`. Interrupted work is never silently restarted from discovery.

## Knowledge Lifecycle

```text
execution evidence -> Event -> Lesson proposal -> Review -> Rule/Skill/Memory patch
```

S0 normally records only Task and Event. S1 may propose a Lesson. S2 may
propose a Rule or reusable Skill after verifier approval. S3 requires human
approval for durable policy, security, data, or architecture knowledge.

## Acceptance Criteria

- A one-label frontend rename uses one Agent and one focused verification path.
- A cross-module Bug produces a root task and bounded child tasks.
- Duplicate input resumes an active task instead of creating another root task.
- Interrupted work resumes from a checkpoint and preserves the failed attempt.
- Workers cannot update global state or durable knowledge directly.
- S2/S3 work cannot finish without an independent verdict.
- Knowledge changes remain proposals until Review and Compiler application.
- Every completed attempt has tests, evidence, state update, and Event records.
