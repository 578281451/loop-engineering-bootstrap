from __future__ import annotations

import argparse
from pathlib import Path


FILES = {
    ".agent/constitution.md": """# Loop Engineering Constitution\n\nThis file contains portable process rules only. Project facts remain in project documents.\n\n## Rules\n\n- Plan before mutation and define testable acceptance.\n- Separate observed facts, assumptions, and recommendations.\n- Match verification and review to risk.\n- Load the smallest sufficient context through the knowledge index.\n- Change protected knowledge only through Event -> Patch -> Validate -> Review -> Apply -> Audit.\n- Preserve superseded knowledge and never silently overwrite it.\n- User-facing frontend workflows require browser E2E evidence or a reviewed, time-limited exception.\n""",
    ".agent/README.md": """# Loop Engineering\n\nRead the constitution, project authority, current state, and task record before work.\nLoad context through `index/knowledge-index.yaml`; record evidence; review durable knowledge; apply patches through the compiler.\n\nRun `python .agent/compiler/cli.py validate` before completion.\n""",
    ".agent/config.yaml": """version: 1\nproject:\n  name: project-name\n  purpose: project-purpose\nauthoritative_documents: []\noptional_documents: []\nworkflow:\n  require_plan: true\n  require_root_cause_for_bug: true\n  compiler_required_for_knowledge_changes: true\nrecords:\n  event_log: append_only\n  knowledge_patches: review_before_apply\n""",
    ".agent/context/builder.yaml": """version: 1\nload_order:\n  - .agent/constitution.md\n  - project_authority_relevant_to_scope\n  - .agent/state/current.yaml\n  - task_record\n  - acceptance_criteria\nexclude_by_default:\n  - secrets\n  - unrelated_modules\n  - superseded_knowledge\nknowledge_index: .agent/index/knowledge-index.yaml\n""",
    ".agent/index/knowledge-index.yaml": """version: 1\nprinciple: Load the smallest sufficient context.\ndocuments: []\nstores:\n  events: .agent/events\n  lessons: .agent/lessons\n  rules: .agent/rules\n  skills: .agent/skills\n  memory: .agent/memory\n  decisions: .agent/decisions\n""",
    ".agent/state/current.yaml": """version: 1\nupdated_at: 1970-01-01T00:00:00Z\nphase: DISCOVERY\ncurrent_task_id: null\ngoal: null\ncompleted: []\nin_progress: []\nnext_actions: []\nrisks: []\nopen_questions: []\n""",
    ".agent/state/roadmap.yaml": """version: 1\nitems: []\n""",
    ".agent/state/blockers.yaml": """version: 1\nblockers: []\n""",
    ".agent/tasks/_template.yaml": """id: TASK-YYYYMMDD-N\ntitle: Task title\nstatus: draft\ncreated_at: 1970-01-01T00:00:00Z\nowner: agent-or-human\nmodel_tier: medium\nscope:\n  included: []\n  excluded: []\nacceptance:\n  - id: AC-1\n    statement: Testable acceptance criterion\n    evidence: command or artifact\n""",
    ".agent/acceptance/frontend-e2e.md": """# Frontend E2E Acceptance\n\nRecord workflow, route, preconditions, test data, browser, viewport, observable actions, assertions, command, and evidence artifact. A blocked run needs an independent reviewer, alternate evidence, and an expiry date.\n""",
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
    for directory in ("events", "lessons", "rules", "skills", "memory", "decisions", "reviews", "hooks", "requirements", "schemas", "compiler", "audit"):
        (root / ".agent" / directory).mkdir(parents=True, exist_ok=True)
    print(f"created={created} preserved={conflicts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
