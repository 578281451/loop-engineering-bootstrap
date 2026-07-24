# Execution Gates

These are mandatory host-Agent gates, not optional suggestions.

## Preflight Gate

Every executable user request is a task. This includes starting or stopping a
service, checking logs, running tests, diagnosing an HTTP error, changing code,
changing documentation, and deployment preparation. Before any command that
changes runtime state or repository state, the Agent must create or resume a
Task, compute its route, and record scope and acceptance. Pure explanations and
read-only answers may use no Task.

Debug mode is never a protocol bypass. S0 is a fast path, not a skip path:
create the lightweight Task, run the operation, record evidence, update state,
and close the Task.

## Delegation Gate

If routing returns S2 or S3, `delegate: true` is mandatory execution behavior.
The Orchestrator must create bounded child work and run the host's available
sub-agent mechanism, then collect a Worker result and an independent verdict.
If the host has no delegation mechanism, record `blocked_delegation` and do not
claim that orchestration or independent verification happened.

## Completion Gate

A task cannot be reported as complete until Task status, Event, run log,
current state, verification evidence, and the structured final report exist.
On failure, use `task-fail`; on an external blocker, use `task-interrupt`.

## Required Final Report

```text
Task ID / Attempt ID
Status / route / actual execution mode
Delegation and verifier result
Root cause
Changed files or runtime actions
Commands and evidence
State, Event, and run-log records
Unfinished work and next action
```
