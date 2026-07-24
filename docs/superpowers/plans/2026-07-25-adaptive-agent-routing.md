# Adaptive Agent Routing Implementation Plan

> **For agentic workers:** Implement task-by-task. Each task ends with an independently testable result.

**Goal:** Add a lightweight task router and recovery contract so S0 work stays single-agent while S1-S3 work gets bounded execution and closing responsibilities.

**Current status:** Phase 1 is implemented in `scripts/loop_cli.py` and the generated runtime. Routing, root-task identity, basic resume behavior, task finish/fail records, and Event append are available. Full delegation, locking, verifier enforcement, knowledge promotion, and budget enforcement remain planned work.

**Architecture:** Keep the runtime dependency-light and project-local. Add a pure Python router for deterministic complexity decisions, JSONL task/attempt/event records for idempotency and recovery, and generated protocol documents for Orchestrator, Worker, and Closer roles. Do not add a scheduler or unattended execution.

**Tech Stack:** Python 3.10+, argparse, pathlib, JSONL, PyYAML, pytest.

## Global Constraints

- Default route is S0 when risk and evidence requirements allow it.
- Interactive user requests may modify code; unattended mutation, merge, push, and deployment remain disabled.
- Workers cannot change root state or durable knowledge.
- S2/S3 requires an independent verdict; S3 requires human approval.
- Every attempt has a root task id, attempt id, phase, checkpoint, status, and evidence.
- Knowledge changes remain proposals until review and compiler application.

### Task 1: Routing Contract `[x] implemented`

**Files:** `references/routing-contract.md`, `scripts/loop_cli.py`, `tests/test_routing.py`

- [x] Define S0-S3 signals and reason codes.
- [x] Implement `route(task) -> {level, mode, delegate, closer, reason_codes}`.
- [x] Cover one-label frontend rename, single-module bug, cross-module bug, and production migration.
- [x] Run focused routing tests.

### Task 2: Task Identity And Attempts `[x] foundation implemented`

**Files:** `scripts/loop_cli.py`, `tests/test_task_identity.py`

- [x] Normalize goal and scope to calculate a stable root task key.
- [x] Add `task-start`, `task-status`, `task-finish`, and `task-fail` commands.
- [x] Resume active matching tasks instead of creating duplicate root tasks.
- [ ] Create a new attempt under a failed task while preserving the previous attempt.
- [ ] Reject concurrent active attempts for the same root task with an active lock.

### Task 3: Events, Checkpoints And Recovery `[ ] next`

**Files:** `scripts/loop_cli.py`, `tests/test_recovery.py`

- [x] Add basic append-only Event records for task start, finish, and failure.
- [ ] Add append-only attempt records separate from the task index.
- [ ] Record failure before retry and preserve the failed attempt.
- [ ] Add checkpoint updates and bounded retry decisions.
- [ ] Stop and escalate after repeated safety, permission, or data-loss failures.

### Task 4: Generated Role Protocols `[x] documentation implemented; runtime enforcement pending`

**Files:** `scripts/bootstrap_loop.py`, `.agent` generated templates, `tests/test_bootstrap_routing.py`

- [x] Generate Orchestrator, Worker, and Closer protocols.
- [x] Generate routing configuration and task/attempt/event directories.
- [x] Preserve existing valid project files and remain idempotent.
- [ ] Add machine-validated delegation records and bounded child scope enforcement.
- [ ] Add machine-validated Closer/verifier verdicts for S2/S3.

### Task 5: Knowledge Upgrade Boundary `[ ] pending`

**Files:** `references/knowledge-upgrade.md`, generated `.agent/README.md`, `tests/test_knowledge_boundary.py`

- [ ] Define S0 Event-only, S1 Lesson proposal, S2 Rule/Skill proposal, S3 human approval.
- [ ] Ensure worker results cannot directly apply durable knowledge.
- [ ] Add proposal records with review status.

### Task 6: Integration And Release `[x] phase 1 released`

**Files:** `SKILL.md`, `README.md`, `CHANGELOG.md`, CI and package tests

- [x] Document the single-agent fast path and escalation rules.
- [x] Run the test suite; current result: `6 passed`.
- [x] Synchronize GitHub and Gitee to the same commit `9124ff2`.
- [ ] Add tests for recovery, delegation, verifier, knowledge boundary, and budget stops.

## Next Execution Order

1. Implement separate attempt records, active locks, and checkpoint resume.
2. Implement delegation/result schemas and parent aggregation.
3. Enforce Closer/verifier verdicts for S2/S3.
4. Implement Event -> Lesson -> Rule/Skill proposal records and review gates.
5. Add budget accounting, kill-switch enforcement, and recovery tests.
6. Update generated README, Skill docs, version, and release both remotes.

Do not enable unattended execution while these items are incomplete. The
current runtime is interactive and report-first, with basic task idempotency;
it is not yet a fully autonomous multi-agent scheduler.
