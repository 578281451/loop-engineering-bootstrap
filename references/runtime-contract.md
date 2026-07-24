# Runtime Contract

The generated runtime is deliberately L1-first. `report_only` is the default
and may inspect, plan, build context, run gates, and record evidence; it does
not edit application files, merge, push, deploy, or start sub-agents.

L2 requires explicit project configuration, isolated worktree execution, a
budget, and an independent verifier. L3 additionally requires human approval.
The parent agent owns global state and delegates bounded child tasks only when
the child scope, dependencies, evidence, and result record are explicit.

Every task follows: discover -> plan -> bounded context -> implement -> test ->
verify -> record Event -> review durable knowledge. Context manifests are
bounded and hash selected files; they are evidence, not a repository dump.
