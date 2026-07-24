# Loop Runtime Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve `loop-engineering-bootstrap` from a document generator into a report-first, observable, budgeted and verifier-backed Loop Engineering runtime.

**Architecture:** Keep `.agent` as project-local state and policy. Add a small Python CLI front door that reads the project configuration and dispatches deterministic operations: doctor, status, context, gate, task, event, patch, and cost. Keep autonomous behavior disabled by default; L1 report-only is the first supported mode, while L2/L3 require explicit configuration and safety gates.

**Tech Stack:** Python 3.10+, argparse, pathlib, PyYAML, jsonschema, pytest, Git worktree commands, JSONL run logs, GitHub Actions.

## Global Constraints

- Existing project rules and host-agent instruction files remain authoritative.
- Default mode is L1 report-only; no automatic code changes, merge, push, or deployment.
- Every write operation is scoped, observable, auditable, and reversible where possible.
- Protected knowledge changes require `Event -> Patch -> Validate -> Review -> Apply -> Audit`.
- A verifier must be independent from an implementer for medium or high-risk work.
- User-facing frontend work requires browser E2E evidence or a reviewed, expiring exception.
- Context loading uses explicit budgets and manifests; full repository dumps are prohibited.
- New generated files must be additive and idempotent.

---

## Reference Decisions

The reference `loop-engineering` project establishes the following patterns to
adopt: one CLI front door, `doctor` and `status`, report-only L1 operation,
explicit L2/L3 escalation, `loop-budget.md`, append-only run logs, machine-
readable denylist gates, worktree isolation, maker/checker verification,
pattern-specific starters, and CI readiness audits.

## File Map

| Area | Files | Responsibility |
|---|---|---|
| Front door | `.agent/compiler/cli.py`, `.agent/compiler/front_door.py` | Stable commands and exit codes |
| Safety | `.agent/gate.yaml`, `.agent/loop-budget.yaml` | Denylist, file limits, levels, budgets, kill switch |
| Observability | `.agent/loop-run-log.jsonl`, `.agent/metrics/` | Run, cost, outcome, and escalation records |
| Context | `.agent/context/budget.yaml`, `.agent/context/manifest.yaml`, `.agent/context/context_pack.py` | Budgeted context selection and evidence of loaded files |
| Coordination | `.agent/coordination/` | Parent/child tasks, delegation, result and aggregate schemas |
| Verification | `.agent/skills/loop-verifier/`, `.agent/coordination/verifier.py` | Independent maker/checker review |
| Patterns | `.agent/patterns/` | Feature, bug-fix, frontend E2E, review and documentation workflows |
| Worktrees | `.agent/compiler/worktree.py` | Isolated implementation attempts |
| CI | `.github/workflows/loop-audit.yml`, `.github/workflows/loop-test.yml` | Offline validation and readiness checks |

---

### Task 1: Versioned Runtime Contract

**Files:**
- Create: `.agent/VERSION`
- Create: `.agent/runtime.yaml`
- Modify: `.agent/README.md`
- Modify: `schemas/runtime.schema.json`
- Test: `tests/test_runtime_contract.py`

**Produces:** `runtime.yaml` with `version`, `level`, `mode`, `auto_fix`,
`auto_merge`, `human_gate`, and `max_subagents`; validator rejects L2/L3 when
the required gates are absent.

- [ ] Add failing tests for default L1 report-only mode, invalid levels, and L3 without a human gate.
- [ ] Run `python -m pytest tests/test_runtime_contract.py -q`; expect failure before implementation.
- [ ] Implement schema and load/validate helpers.
- [ ] Run the focused test; expect all assertions to pass.
- [ ] Update README with the level transition rule: L1 first, L2 after stable evidence, L3 only with explicit approval.

### Task 2: CLI Front Door And Doctor

**Files:**
- Create: `.agent/compiler/front_door.py`
- Modify: `.agent/compiler/cli.py`
- Test: `tests/test_front_door.py`

**Produces:** Commands `doctor`, `status`, `validate`, `context`, `gate`,
`task`, `event`, `patch`, and `cost`, with exit codes 0 healthy, 1 warnings,
2 blocked.

- [ ] Add tests for command parsing, JSON output, missing files, warnings and blocked state.
- [ ] Implement `doctor(root, json_output=False) -> DoctorReport`.
- [ ] Implement `status(root) -> StatusReport` from current state and run log.
- [ ] Route existing compiler operations through the front door without breaking old commands.
- [ ] Run `python -m pytest tests/test_front_door.py -q`.

### Task 3: Gates, Denylist And Human Levels

**Files:**
- Create: `.agent/gate.yaml`
- Create: `.agent/compiler/gate.py`
- Test: `tests/test_gate.py`

**Produces:** `gate(root, changed_files, level) -> GateReport` that enforces
denylist, maximum changed files, protected operations, and human-gate rules.

- [ ] Add tests for `.env`, secrets, migrations, production paths, file-count overflow, and allowed documentation changes.
- [ ] Implement normalized path matching relative to repository root.
- [ ] Require explicit human approval for security, data-loss, migration, production and architecture changes.
- [ ] Return machine-readable reasons and remediation actions.
- [ ] Run `python -m pytest tests/test_gate.py -q`.

### Task 4: Budget And Run Observability

**Files:**
- Create: `.agent/loop-budget.yaml`
- Create: `.agent/loop-run-log.jsonl`
- Create: `.agent/compiler/budget.py`
- Modify: `.agent/metrics/learning.yaml`
- Test: `tests/test_budget.py`

**Produces:** `budget.check(run) -> BudgetDecision` and append-only structured
run records with token estimate, duration, subagent count, files changed,
outcome and escalations.

- [ ] Add tests for below 80%, report-only at 80%, stop at 100%, kill-switch file, and zero-action early exit.
- [ ] Implement daily and per-run limits without requiring a model provider.
- [ ] Ensure logging failure blocks unattended mode but does not erase task evidence.
- [ ] Run `python -m pytest tests/test_budget.py -q`.

### Task 5: Budgeted Context Engine

**Files:**
- Create: `.agent/context/budget.yaml`
- Create: `.agent/context/manifest.yaml`
- Create: `.agent/context/context_pack.py`
- Modify: `.agent/context/builder.yaml`
- Test: `tests/test_context_pack.py`

**Produces:** `build_context(root, task) -> ContextPack` with selected files,
excluded files, byte/token estimates, reasons, and a stable manifest.

- [ ] Add tests for domain relevance, required documents, superseded knowledge, secret exclusion, and byte budget overflow.
- [ ] Implement index-first selection; never recursively load all `docs/` by default.
- [ ] Add summaries for documents over the configured size threshold and include source hashes.
- [ ] Run `python -m pytest tests/test_context_pack.py -q`.

### Task 6: Parent/Child Coordination And Verifier

**Files:**
- Create: `.agent/coordination/delegation.schema.json`
- Create: `.agent/coordination/result.schema.json`
- Create: `.agent/coordination/aggregate.schema.json`
- Create: `.agent/coordination/protocol.md`
- Create: `.agent/skills/loop-verifier/SKILL.md`
- Test: `tests/test_coordination.py`

**Produces:** Structured parent task, child delegation, implementer result and
verifier verdict. The parent owns global state; children may write only their
worktree and result record.

- [ ] Add tests for parent/child IDs, dependency ordering, scope limits, missing evidence, and verifier rejection.
- [ ] Define result fields: changed files, tests, risks, blockers, artifacts and next action.
- [ ] Define verdicts `APPROVE`, `REJECT`, and `ESCALATE_HUMAN`; verifier never edits implementation files.
- [ ] Add aggregate logic that updates global state only after child results are validated.
- [ ] Run `python -m pytest tests/test_coordination.py -q`.

### Task 7: Worktree Isolation And Patterns

**Files:**
- Create: `.agent/compiler/worktree.py`
- Create: `.agent/patterns/feature-development.yaml`
- Create: `.agent/patterns/bug-fix.yaml`
- Create: `.agent/patterns/frontend-e2e.yaml`
- Create: `.agent/patterns/code-review.yaml`
- Create: `.agent/patterns/documentation-sync.yaml`
- Test: `tests/test_worktree_and_patterns.py`

**Produces:** `worktree.create(task_id)`, `worktree.discard(task_id)`, and
pattern selection with level, inputs, outputs, verifier and acceptance rules.

- [ ] Add tests using a temporary Git repository; verify each attempt has an isolated path and cleanup metadata.
- [ ] Reject worktree creation for dirty or unsafe roots unless explicitly configured.
- [ ] Make L1 patterns report-only and reserve implementation worktrees for L2+.
- [ ] Run `python -m pytest tests/test_worktree_and_patterns.py -q`.

### Task 8: Initialization, Doctor Matrix And Host Integration

**Files:**
- Modify: `scripts/bootstrap_loop.py`
- Modify: `scripts/integrate_agent_entry.py`
- Create: `scripts/doctor_loop.py`
- Create: `tests/test_bootstrap_matrix.py`
- Modify: `docs/install.md`

**Produces:** Idempotent initialization that creates the runtime contract,
budget, gate, context, coordination and pattern files, integrates the host
entry, and reports a readiness score plus top three actions.

- [ ] Add fresh-project tests for Claude, generic `AGENTS.md`, Gemini and Copilot entries.
- [ ] Add an existing-project test proving valid files are preserved and only missing files are created.
- [ ] Implement doctor output and exit codes.
- [ ] Run `python -m pytest tests/test_bootstrap_matrix.py -q`.

### Task 9: CI, Release And Update Hygiene

**Files:**
- Create: `.github/workflows/test.yml`
- Create: `.github/workflows/skill-audit.yml`
- Modify: `VERSION`
- Modify: `CHANGELOG.md`
- Modify: `CONTRIBUTING.md`
- Test: CI workflow validation and local full suite

**Produces:** Pull-request validation for Skill format, scripts, schemas,
tests, forbidden files and package contents; release tags remain the source of
installed versions.

- [ ] Add CI for `quick_validate.py`, `pytest`, package build and cache exclusion.
- [ ] Add an audit that checks required files, host adapters, update docs and version consistency.
- [ ] Run `python -m pytest tests -q` and package the clean Skill.
- [ ] Verify both GitHub and Gitee point to the same release commit.

## Rollout Order

1. Tasks 1-3: contract, CLI and safety gates.
2. Tasks 4-5: budget, observability and context control.
3. Tasks 6-7: coordination, verifier and isolated worktrees.
4. Task 8: make the initializer generate the complete runtime.
5. Task 9: enforce quality in CI and publish versioned releases.

Do not enable L2 or L3 automatically after implementation. Run the generated
system in L1 report-only mode for at least one real project cycle, review false
positives, context size, cost and verifier quality, then request an explicit
level upgrade.

## Acceptance Criteria

- A fresh project receives a complete, idempotent runtime scaffold.
- `doctor` reports healthy, warning or blocked status with actionable output.
- `gate` rejects denylisted paths and unsafe levels before mutation.
- `context` produces a bounded manifest and never loads secrets by default.
- Parent/child results and verifier decisions are schema-valid and auditable.
- L1 runs do not modify application source.
- L2 runs use isolated worktrees and independent verification.
- Every run has budget and outcome evidence.
- CI rejects malformed Skill packages and missing runtime files.
