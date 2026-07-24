---
name: loop-engineering-bootstrap
description: >
  Initialize or upgrade a project's Loop Engineering operating layer. Use this
  whenever the user asks to create, complete, standardize, extract, migrate,
  or reuse .agent documents, agent memory, knowledge lifecycle, task state,
  model routing, Knowledge Compiler, project constitution, hooks, acceptance
  rules, or frontend E2E gates. Read the target project's existing docs,
  CLAUDE.md, README, and agent configuration first; extract portable process
  rules instead of copying project-specific technology, business, paths, model
  names, or team responsibilities. Produce a reusable .agent system and
  validate it before claiming completion.
compatibility: Requires Python 3.10+, a writable project root, and PyYAML plus jsonschema for compiler execution.
---

# Loop Engineering Bootstrap

After initialization, a normal bug or feature request is enough. Do not make
the user repeat task creation, planning, delegation, testing, state updates,
or reporting as separate prompts. Read the project rules and state, create or
resume the task, plan, decide delegation, implement when the user requested a
change, verify, update state, and report. Ask only questions that materially
change scope, safety, permission, or expected behavior. `L1/report_only`
prevents unattended mutation, merge, push, and deployment; it does not prevent
implementation in an explicitly requested interactive conversation.

Read `references/delegation-runtime.md`. Users must not be required to know
the routing levels or Agent roles. When the router returns S2/S3, automatically
dispatch bounded child work through the host Agent's available delegation
mechanism, run the independent closer/verifier, and report the actual mode. A
`delegate: true` result is not complete until delegation evidence exists; if
delegation is unavailable, record `blocked_delegation` instead of pretending
the task was orchestrated.

Read `references/execution-gates.md` and
`references/final-report-contract.md`. Every executable request is a Task,
including service startup, log inspection, test execution, and diagnosis.
Debug mode is never a protocol bypass. Before mutation or runtime commands,
create or resume the Task and route it. Before claiming completion, record
Task status, Event, run log, state, evidence, and the structured final report.

## Design Reference

The runtime patterns are informed by
`cobusgreyling/loop-engineering`: CLI front door, L1 report-only rollout,
budgets, gates, bounded context, run evidence, delegation, and independent
verification. This Skill deliberately implements a smaller document-plus-CLI
layer and does not require the reference project's Fleet, MCP, scheduler, or
unattended automation stack.

Use this skill to create a portable `.agent` operating layer from an existing
project. The goal is a small, auditable system that helps future agents load
the right context, plan work, verify behavior, and compile durable knowledge.

## Safety And Boundaries

- Inspect before editing. Preserve unrelated user changes.
- Do not overwrite existing project documents or application source.
- Treat project documents as input, not as a template to copy wholesale.
- Keep project facts in project docs; keep reusable process rules in `.agent`.
- Never copy secrets, credentials, private reasoning, or temporary logs.
- Use a compiler patch for changes to protected knowledge after initialization.

## Workflow

For cross-conversation continuity, follow `docs/continuation-guide.md`. It is
the canonical sequence for starting, resuming, delegating, verifying, and
closing a task. The generated project's `.agent/README.md` contains the same
operational contract in project-local form.

### 1. Discover

Read, when present:

- `CLAUDE.md`, `AGENTS.md`, `README.md`
- `docs/` standards, architecture, API, testing, and deployment documents
- existing `.agent/`, `.claude/`, or equivalent agent configuration
- package manifests and test configuration only when needed to identify commands

Also detect the host agent's instruction entry. Use the first applicable
existing file from this adapter list, and inspect all applicable files when a
project uses more than one agent:

| Host | Instruction entry |
|---|---|
| Claude Code | `CLAUDE.md` or `.claude/CLAUDE.md` |
| Codex / generic agents | `AGENTS.md` or `.agents/AGENTS.md` |
| Gemini | `GEMINI.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Cursor | `.cursor/rules/` |

Do not assume the host from the user's wording alone. Read the existing entry,
preserve its rules, and add the Loop Engineering bridge described below.

Classify each rule as `portable_loop`, `project_constraint`, `technology_detail`,
or `historical_or_local`. Only the first category belongs in the reusable
constitution. Project constraints remain referenced from their original files.

Create an extraction report at `.agent/reviews/initial-extraction.md` that
lists the source file, extracted rule, category, and destination. Do not turn
this report into a second copy of project documentation.

### 2. Plan The Layer

Use `scripts/bootstrap_loop.py` from this skill to create missing directories
and safe starter files. Run it from the target project root:

```powershell
python <skill-path>/scripts/bootstrap_loop.py --root .
```

The script is additive: it creates only missing files and reports conflicts.
It does not fill project-specific values automatically. The AI must then edit
the generated index, project mapping, and config using the discovery report.

After the `.agent` layer exists, integrate it into the detected host entry.
Use `scripts/integrate_agent_entry.py --root .` or make the equivalent focused
edit. The integration is part of bootstrapping, not a follow-up instruction for
the user.

The bridge must be short and host-neutral. It must tell the host Agent to read
`.agent/constitution.md`, `.agent/README.md`, current state, the task record,
and relevant indexed knowledge before work; to create a task and plan before
mutation; to update state during work; and to record evidence, Event, review,
and any Knowledge Patch after work. It must also state that `.agent` documents
are operational instructions for this project, not optional reference notes.

Use stable markers so repeated Skill runs update one block instead of appending
duplicates. Show the host-entry diff in the final report.

### 3. Generate Portable Documents

Ensure these exist and are coherent:

- `.agent/constitution.md`: portable planning, evidence, review, context,
  testing, lifecycle, compiler, and recovery rules.
- `.agent/README.md`: task loop, directory map, commands, and recovery.
- `.agent/config.yaml`, `context/builder.yaml`, and `index/knowledge-index.yaml`.
- `state/`, `tasks/`, `events/`, `lessons/`, `rules/`, `skills/`, `memory/`,
  `decisions/`, `reviews/`, `hooks/`, `requirements/`, and `acceptance/`.
- `schemas/` for events, tasks, knowledge, reviews, patches, and audit records.
- `compiler/` with validation, proposal, review, apply, rollback metadata, and
  append-only audit behavior.

The final output is the complete `.agent` layer, not merely the files created
by the helper script. Explain each generated file in the final report using the
output contract in `references/output-contract.md`. Distinguish files that were
created, files that were updated after reading project docs, and files that
were preserved.

Use placeholders only in files whose name begins with `_` or in explicitly
documented templates. Live state, config, and indexes must contain real paths
or empty collections, not angle-bracket placeholders.

### 4. Add Frontend E2E Acceptance

If the project has a frontend, identify its existing browser test framework.
Prefer the existing Playwright/Cypress setup; do not invent a second runner.
Add or update project testing standards so user-facing changes require:

- workflow, route, preconditions, test data, browser, and viewport;
- observable user actions and success/loading/empty/validation/error assertions;
- exact command and trace, screenshot, video, or HTML report evidence;
- a reviewed, time-limited exception only when execution is genuinely blocked.

Keep framework-specific commands in project docs. Keep the portable acceptance
contract in `.agent/acceptance/frontend-e2e.md`.

### 5. Validate

Run the generated compiler and tests:

```powershell
python .agent/compiler/cli.py validate
pytest .agent/tests -q
```

Also verify that every required document referenced by config or index exists,
schemas accept templates, no live file contains unresolved placeholders, and
the generated system does not reference a missing `AGENTS.md` or a duplicated
project constitution.

Report created files, preserved project-specific references, validation output,
and any user decisions still needed. Never claim E2E coverage was executed
unless a browser test actually ran and produced evidence.

## Updating This Skill

The Skill is distributed from the Git repository, not self-modified during a
running task. To check or update an installed copy, use the bundled script:

```powershell
python scripts/update_skill.py --target <installed-skill-directory>
python scripts/update_skill.py --target <installed-skill-directory> --apply
```

Pass the Gitee repository with `--source` when GitHub is unavailable. The
script stages the remote copy, backs up the current directory with a timestamp,
restores it if copying fails, and tells the user to restart the host Agent.

## Bundled Resources

- `references/extraction-rubric.md`: classification rules for separating
  portable process principles from project-specific constraints.
- `references/output-contract.md`: required files and validation invariants.
- `scripts/bootstrap_loop.py`: additive directory and starter-file generator.
- `scripts/integrate_agent_entry.py`: idempotently adds the host-agent bridge.
- `scripts/update_skill.py`: checks and safely updates an installed copy.
- `docs/install.md` and `docs/update.md`: installation and update procedures.
- `CHANGELOG.md` and `CONTRIBUTING.md`: release history and contribution rules.
- `evals/evals.json`: representative skill test prompts.
