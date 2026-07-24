# Interactive Task Contract

After initialization, the user does not need to send separate prompts for task creation, planning, delegation, testing, state updates, or reporting.

The normal user request is enough:

```text
Fix the checkout total bug: coupon discounts produce the wrong total.
```

The Agent must automatically:

1. Read host rules and `.agent` state.
2. Create or resume the task and plan.
3. Build bounded context and decide whether delegation is useful.
4. Implement the change in the interactive session when the user requested a fix.
5. Run focused tests and frontend E2E when applicable.
6. Run the gate and validator.
7. Update state, record evidence and Event, and report remaining work.

The Agent asks questions only when scope, safety, permission, or expected behavior cannot be inferred responsibly. `L1/report_only` prevents unattended mutation, merge, push, and deployment; it does not prevent implementation during an explicitly requested interactive conversation.
