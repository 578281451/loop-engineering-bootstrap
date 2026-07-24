# Independent Verifier Protocol

The implementer submits a result containing task id, changed files, commands,
evidence artifacts, risks, blockers, and next action. A verifier reads the
result and repository independently and returns exactly one of `APPROVE`,
`REJECT`, or `ESCALATE_HUMAN` with reasons and evidence. The verifier never
edits implementation files. The parent agent applies the verdict to global
state and records it in the run log.
