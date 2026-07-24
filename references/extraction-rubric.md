# Extraction Rubric

| Category | Keep in `.agent`? | Examples |
|---|---:|---|
| portable_loop | Yes | plan before mutation, evidence, review, rollback, lifecycle |
| project_constraint | Reference only | product rules, domain acceptance, release policy |
| technology_detail | Reference only | FastAPI, Vue, database, provider URLs, ports |
| historical_or_local | No | one-off incident, temporary workaround, personal preference |

A rule is portable only when it remains useful after changing the repository's
business domain, framework, deployment target, model provider, and team names.
When uncertain, keep the source reference and put the rule in a reviewed
project-level rule instead of the portable constitution.
