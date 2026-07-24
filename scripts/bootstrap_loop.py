from __future__ import annotations

import argparse
from pathlib import Path


FILES = {
    ".agent/VERSION": "1\n",
    ".agent/runtime.yaml": "version: 1\nlevel: L1\nmode: report_only\nauto_fix: false\nauto_merge: false\nhuman_gate: false\nmax_subagents: 3\ninteractive_mutation:\n  allowed_with_user_request: true\n",
    ".agent/gate.yaml": "version: 1\nmax_changed_files: 50\ndenylist:\n  - .env\n  - .git\n  - secrets/\n  - credentials/\nprotected_operations:\n  - migrations\n  - production\n  - security\n",
    ".agent/loop-budget.yaml": "version: 1\nmax_tokens: 100000\nmax_duration_minutes: 60\nmax_subagents: 3\nstop_at_percent: 100\nreport_only_at_percent: 80\nkill_switch: .agent/STOP\n",
    ".agent/loop-run-log.jsonl": "",
    ".agent/routing.yaml": "version: 1\ndefault_level: S0\nlevels: [S0, S1, S2, S3]\nmax_child_agents: 3\nrequire_independent_verifier_for: [S2, S3]\nrequire_human_gate_for: [S3]\n",
    ".agent/constitution.md": """# Loop Engineering Constitution\n\nThis file contains portable process rules only. Project facts remain in project documents.\n\n## Rules\n\n- Plan before mutation and define testable acceptance.\n- A normal user-requested Bug or feature starts the complete interactive loop automatically.\n- L1/report_only blocks unattended mutation, merge, push, and deployment; it permits implementation in the explicitly requested interactive conversation.\n- Separate observed facts, assumptions, and recommendations.\n- Match verification and review to risk; S2/S3 requires an independent verifier.\n- Load the smallest sufficient context through the knowledge index.\n- Change protected knowledge only through Event -> Patch -> Validate -> Review -> Apply -> Audit.\n- Preserve superseded knowledge and never silently overwrite it.\n- User-facing frontend workflows require browser E2E evidence or a reviewed, time-limited exception.\n""",
    ".agent/README.md": """# Loop Engineering\n\n## Every new task or conversation\n\nRead the host instruction entry, this file, `constitution.md`, `runtime.yaml`, `state/current.yaml`, and `index/knowledge-index.yaml`. Run `python .agent/compiler/cli.py doctor --json` and `status --json`. Resume `current_task_id` when present; do not create a duplicate task.\n\nAfter initialization, the user only needs to describe the goal or Bug. The Agent automatically creates or resumes the task, plans, decides delegation, implements an explicitly requested change, tests, verifies, updates state, and reports. Ask only questions that materially change scope, safety, permission, or expected behavior.\n\nCreate a task record and PLAN before mutation. Build bounded context with `python .agent/compiler/cli.py context --task \"...\"`; never load the whole repository or all history.\n\nThe default is L1/report_only. This prevents unattended mutation, merge, push, and deployment; it does not prevent implementation during an explicitly requested interactive conversation. The parent Agent owns global state. A child task must have explicit scope and return files, tests, evidence, risks, blockers, and next action. An independent verifier returns APPROVE, REJECT, or ESCALATE_HUMAN and never edits implementation files.\n\nBefore completion, run relevant tests and frontend E2E when applicable, run `gate` and `validate`, update state, record an Event, and report evidence and remaining work. At 80% budget finish and report; at 100% or `.agent/STOP`, stop.\n""",
    ".agent/config.yaml": """version: 1\nproject:\n  name: project-name\n  purpose: project-purpose\nauthoritative_documents: []\noptional_documents: []\nworkflow:\n  require_plan: true\n  require_root_cause_for_bug: true\n  compiler_required_for_knowledge_changes: true\nrecords:\n  event_log: append_only\n  knowledge_patches: review_before_apply\n""",
    ".agent/context/builder.yaml": """version: 1\nload_order:\n  - .agent/constitution.md\n  - project_authority_relevant_to_scope\n  - .agent/state/current.yaml\n  - task_record\n  - acceptance_criteria\nexclude_by_default:\n  - secrets\n  - unrelated_modules\n  - superseded_knowledge\nknowledge_index: .agent/index/knowledge-index.yaml\n""",
    ".agent/index/knowledge-index.yaml": """version: 1\nprinciple: Load the smallest sufficient context.\ndocuments: []\nstores:\n  events: .agent/events\n  lessons: .agent/lessons\n  rules: .agent/rules\n  skills: .agent/skills\n  memory: .agent/memory\n  decisions: .agent/decisions\n""",
    ".agent/state/current.yaml": """version: 1\nupdated_at: 1970-01-01T00:00:00Z\nphase: DISCOVERY\ncurrent_task_id: null\ngoal: null\ncompleted: []\nin_progress: []\nnext_actions: []\nrisks: []\nopen_questions: []\n""",
    ".agent/state/roadmap.yaml": """version: 1\nitems: []\n""",
    ".agent/state/blockers.yaml": """version: 1\nblockers: []\n""",
    ".agent/tasks/_template.yaml": """id: TASK-YYYYMMDD-N\ntitle: Task title\nstatus: draft\ncreated_at: 1970-01-01T00:00:00Z\nowner: agent-or-human\nmodel_tier: medium\nscope:\n  included: []\n  excluded: []\nacceptance:\n  - id: AC-1\n    statement: Testable acceptance criterion\n    evidence: command or artifact\n""",
    ".agent/acceptance/frontend-e2e.md": """# Frontend E2E Acceptance\n\nRecord workflow, route, preconditions, test data, browser, viewport, observable actions, assertions, command, and evidence artifact. A blocked run needs an independent reviewer, alternate evidence, and an expiry date.\n""",
    ".agent/compiler/cli.py": Path(__file__).with_name("loop_cli.py").read_text(encoding="utf-8"),
    ".agent/coordination/protocol.md": "# Coordination\n\nThe parent owns global state. Child tasks receive explicit scope and dependencies, write only their isolated worktree, and return changed files, tests, evidence, risks, blockers, and next action. A verifier returns APPROVE, REJECT, or ESCALATE_HUMAN without editing implementation files. When routing returns S2 or S3, the Orchestrator MUST create the child task and invoke the available Agent delegation mechanism automatically; the user must not need to know these roles.\n",
    ".agent/coordination/orchestrator.md": "# Orchestrator\n\nRead rules and state, compute task identity, route S0-S3, create bounded delegations, own retries and global state, and produce the final report. S0 may be completed directly. For S2/S3, do not silently complete the work alone: automatically dispatch Worker task(s), collect results, invoke the Closer/verifier, and aggregate the verdict. Ask the user only for scope, safety, permission, or expected behavior decisions.\n",
    ".agent/coordination/worker.md": "# Worker\n\nWork only inside the assigned scope. Return changed files, tests, evidence, risks, blockers, and next action. Do not edit root state, gates, or durable knowledge.\n",
    ".agent/coordination/closer.md": "# Closer\n\nIndependently check acceptance and evidence. Return APPROVE, REJECT, or ESCALATE_HUMAN. Update task/event/review records only; never edit implementation files.\n",
    ".agent/skills/loop-verifier/SKILL.md": "# Loop Verifier\n\nAct independently of the implementer. Inspect the result, diff, acceptance criteria, and evidence. Return APPROVE, REJECT, or ESCALATE_HUMAN with concrete reasons. Never modify implementation files.\n",
    ".agent/patterns/feature-development.yaml": "name: feature-development\nlevel: L1\noutputs: [task, plan, tests, evidence, verifier-result]\n",
    ".agent/patterns/bug-fix.yaml": "name: bug-fix\nlevel: L1\nrequired: [reproduction, root_cause, regression_test]\n",
    ".agent/patterns/frontend-e2e.yaml": "name: frontend-e2e\nlevel: L1\nrequired: [route, browser, viewport, assertions, artifact]\n",
    ".agent/patterns/code-review.yaml": "name: code-review\nlevel: L1\noutputs: [findings, risks, evidence]\n",
    ".agent/patterns/documentation-sync.yaml": "name: documentation-sync\nlevel: L1\noutputs: [updated_source_of_truth, reference_validation]\n",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a portable Loop Engineering skeleton.")
    parser.add_argument("--root", default=".", help="Target project root")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    created = 0
    conflicts = 0
    for relative, content in FILES.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            conflicts += 1
            print(f"preserved: {relative}")
            continue
        path.write_text(content, encoding="utf-8")
        created += 1
        print(f"created: {relative}")
    for directory in ("events", "lessons", "rules", "skills", "memory", "decisions", "reviews", "hooks", "requirements", "schemas", "compiler", "audit", "coordination", "patterns", "metrics"):
        (root / ".agent" / directory).mkdir(parents=True, exist_ok=True)
    print(f"created={created} preserved={conflicts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
