# Automatic Delegation Runtime

The user only supplies a goal, symptom, or Bug. The host Agent owns the workflow and must not require the user to name S0-S3 or Agent roles.

After reading the project rules, the Orchestrator calls the router. For S0 it completes the work inline. For S1 it may complete inline and run lightweight verification. For S2 it MUST create bounded Worker task records, invoke the host Agent's sub-agent mechanism, collect results, and invoke an independent Closer/verifier. For S3 it additionally requires the human gate.

`delegate: true` is an execution requirement, not a suggestion or a report-only label. If the host cannot create a child Agent, the Orchestrator must record a blocked delegation, explain the limitation, and not claim that S2 verification happened.

The final report must state which mode actually ran: `single_agent`, `orchestrated`, or `blocked_delegation`.
