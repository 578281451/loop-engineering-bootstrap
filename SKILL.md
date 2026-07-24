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

### 1. Discover

Read, when present:

- `CLAUDE.md`, `AGENTS.md`, `README.md`
- `docs/` standards, architecture, API, testing, and deployment documents
- existing `.agent/`, `.claude/`, or equivalent agent configuration
- package manifests and test configuration only when needed to identify commands

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

## Bundled Resources

- `references/extraction-rubric.md`: classification rules for separating
  portable process principles from project-specific constraints.
- `references/output-contract.md`: required files and validation invariants.
- `scripts/bootstrap_loop.py`: additive directory and starter-file generator.
- `evals/evals.json`: representative skill test prompts.
