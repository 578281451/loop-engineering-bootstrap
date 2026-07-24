# Output Contract

The generated layer must provide:

- one portable `.agent/constitution.md`;
- an operational README and project mapping;
- config, context builder, and knowledge index with valid references;
- state and task records;
- event -> lesson -> rule -> skill -> memory lifecycle;
- patch schemas and a review-before-apply compiler;
- append-only audit records;
- requirements and acceptance templates;
- frontend E2E acceptance when a frontend exists;
- a host-agent instruction bridge that makes `.agent` operational;
- offline validation and focused tests.

## File Responsibilities

`constitution.md` is the portable rule boundary. `README.md` explains how an
agent uses the layer. `project.md`, `config.yaml`, and the knowledge index map
the target project without duplicating its facts. State and task files describe
what is happening now; events preserve what happened. Lessons, rules, skills,
memory, and decisions represent progressively more durable knowledge.

Hooks describe when checks happen. Requirements describe what a change must
consider. Acceptance describes what proves it is complete. Schemas make
machine-readable records rejectable. The compiler is the only path for
protected knowledge changes, and audit files explain what it did.

## Creation Modes

When the Skill is invoked, the AI reads the target project and creates or
updates the complete layer above. The bundled `bootstrap_loop.py` is only an
additive skeleton generator: it creates safe starter files and directories but
does not perform project analysis or fill project-specific references.

Do not require `AGENTS.md` unless the target project actually contains it.
Do not create a second copy of an existing project constitution.

## Skill Distribution And Updates

The Skill repository is the source of truth. An installed Skill is a local
copy, so updates require checking the remote repository and replacing the
installed copy. The bundled updater supports check-only mode, GitHub/Gitee
sources, timestamped backups, and restoration when copying fails. A host Agent
must be restarted after an update to load the new Skill contents.

## Host Integration Contract

The generated `.agent` directory is not sufficient by itself. The bootstrap
must identify the target host's instruction entry and add one marked bridge
block. The block must reference the constitution, README, current state,
knowledge index, task record, plan, verification, Event, Review, and Compiler.
The bridge must be idempotent and preserve all unrelated host instructions.
