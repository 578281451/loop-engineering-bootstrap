# Adaptive Agent Routing Implementation Plan

> **For agentic workers:** Implement task-by-task. Each task ends with an independently testable result.

**Goal:** Add a lightweight task router and recovery contract so S0 work stays single-agent while S1-S3 work gets bounded execution and closing responsibilities.

**Architecture:** Keep the runtime dependency-light and project-local. Add a pure Python router for deterministic complexity decisions, JSONL task/attempt/event records for idempotency and recovery, and generated protocol documents for Orchestrator, Worker, and Closer roles. Do not add a scheduler or unattended execution.

**Tech Stack:** Python 3.10+, argparse, pathlib, JSONL, PyYAML, pytest.

## Global Constraints

- Default route is S0 when risk and evidence requirements allow it.
- Interactive user requests may modify code; unattended mutation, merge, push, and deployment remain disabled.
- Workers cannot change root state or durable knowledge.
- S2/S3 requires an independent verdict; S3 requires human approval.
- Every attempt has a root task id, attempt id, phase, checkpoint, status, and evidence.
- Knowledge changes remain proposals until review and compiler application.

### Task 1: Routing Contract

**Files:** `references/routing-contract.md`, `scripts/loop_cli.py`, `tests/test_routing.py`

- [ ] Define S0-S3 signals and reason codes.
- [ ] Implement `route(task) -> {level, mode, delegate, closer, reason_codes}`.
- [ ] Cover one-label frontend rename, single-module bug, cross-module bug, and production migration.
- [ ] Run focused routing tests.

### Task 2: Task Identity And Attempts

**Files:** `scripts/loop_cli.py`, `tests/test_task_identity.py`

- [ ] Normalize goal and scope to calculate a stable root task key.
- [ ] Add `task start`, `task status`, `task resume`, and `task finish` commands.
- [ ] Resume active/interrupted tasks and create attempts under failed tasks.
- [ ] Reject concurrent active attempts for the same root task.

### Task 3: Events, Checkpoints And Recovery

**Files:** `scripts/loop_cli.py`, `tests/test_recovery.py`

- [ ] Add append-only event and attempt record helpers.
- [ ] Record failure before retry and preserve the failed attempt.
- [ ] Add checkpoint updates and bounded retry decisions.
- [ ] Stop and escalate after repeated safety, permission, or data-loss failures.

### Task 4: Generated Role Protocols

**Files:** `scripts/bootstrap_loop.py`, `.agent` generated templates, `tests/test_bootstrap_routing.py`

- [ ] Generate Orchestrator, Worker, and Closer protocols.
- [ ] Generate routing configuration and task/attempt/event directories.
- [ ] Preserve existing valid project files and remain idempotent.

### Task 5: Knowledge Upgrade Boundary

**Files:** `references/knowledge-upgrade.md`, generated `.agent/README.md`, `tests/test_knowledge_boundary.py`

- [ ] Define S0 Event-only, S1 Lesson proposal, S2 Rule/Skill proposal, S3 human approval.
- [ ] Ensure worker results cannot directly apply durable knowledge.
- [ ] Add proposal records with review status.

### Task 6: Integration And Release

**Files:** `SKILL.md`, `README.md`, `CHANGELOG.md`, CI and package tests

- [ ] Document the single-agent fast path and escalation rules.
- [ ] Run the full test suite and clean package validation.
- [ ] Synchronize GitHub and Gitee to the same commit.
