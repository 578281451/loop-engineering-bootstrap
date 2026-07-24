# Final Report Contract

Do not end an executable task with an informal summary only. Use these fields:

```yaml
task_id:
attempt_id:
status: completed|failed|interrupted|blocked_delegation
route: S0|S1|S2|S3
execution_mode: single_agent|orchestrated|blocked_delegation
delegation:
  requested: false
  child_tasks: []
  worker_results: []
verifier:
  verdict: inline|APPROVE|REJECT|ESCALATE_HUMAN|not_run
root_cause:
changed_files: []
commands: []
evidence: []
state_record:
event_record:
run_log_record:
unfinished: []
next_action:
```

If a record is unavailable, state why. Never claim a verifier, child Agent, or
E2E run happened without its evidence.
