from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
try:
    import yaml
except ImportError:
    yaml = None

EXIT_OK, EXIT_WARN, EXIT_BLOCKED = 0, 1, 2

def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())

def route(task: str, files: list[str]) -> dict[str, Any]:
    text = normalize(task + " " + " ".join(files)); reasons = []
    high = any(x in text for x in ("production", "migration", "security", "delete data", "architecture", "生产", "迁移", "安全", "删除数据", "架构"))
    cross = any(x in text for x in ("frontend", "backend", "api", "database", "cross-module", "multiple services", "前端", "后端", "接口", "api 地址", "采集插件", "浏览器插件", "本地", "redis", "服务依赖"))
    e2e = any(x in text for x in ("e2e", "user flow", "browser", "page", "frontend", "前端", "浏览器", "页面", "插件"))
    if high:
        level, mode, closer = "S3", "orchestrated", "independent_human_gate"; reasons.append("high_risk")
    elif cross:
        level, mode, closer = "S2", "orchestrated", "independent_verifier"; reasons.append("cross_boundary")
    elif any(x in text for x in ("bug", "fix", "regression")) or e2e:
        level, mode, closer = "S1", "single_agent", "lightweight_verifier"; reasons.append("verification_required")
    else:
        level, mode, closer = "S0", "single_agent", "inline"; reasons.extend(["one_scope", "low_risk"])
    return {"level": level, "mode": mode, "delegate": level in {"S2", "S3"}, "closer": closer,
            "reason_codes": reasons, "required_evidence": ["focused_test"] + (["frontend_e2e"] if e2e else [])}

def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def update_state(root: Path, task_id: str | None, phase: str, **extra: Any) -> None:
    path = root / ".agent/state/current.yaml"
    state = load_yaml(path)
    state.update({"version": 1, "updated_at": now(), "phase": phase, "current_task_id": task_id, **extra})
    if yaml is not None:
        path.write_text(yaml.safe_dump(state, allow_unicode=True, sort_keys=False), encoding="utf-8")

def log_run(root: Path, task_id: str | None, outcome: str, **extra: Any) -> None:
    append_jsonl(root / ".agent/loop-run-log.jsonl", {"timestamp": now(), "task_id": task_id, "outcome": outcome, **extra})

def task_key(root: Path, goal: str, scope: list[str]) -> str:
    raw = normalize(goal) + "|" + "|".join(sorted(normalize(x) for x in scope))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def task_start(root: Path, goal: str, scope: list[str]):
    tasks = root / ".agent/tasks/index.jsonl"; key = task_key(root, goal, scope); rows = []
    if tasks.exists(): rows = [json.loads(x) for x in tasks.read_text(encoding="utf-8").splitlines() if x.strip()]
    existing = next((x for x in rows if x.get("task_key") == key and x.get("status") in {"active", "interrupted"}), None)
    if existing: return {"command":"task_start", **existing, "status":"resumed"}, EXIT_OK
    task_id = "TASK-" + key; attempt_id = "ATT-1"; timestamp = now()
    value = {"id":task_id, "task_id":task_id, "attempt_id":attempt_id, "task_key":key, "title":goal, "goal":goal, "created_at":timestamp, "owner":"orchestrator", "model_tier":"medium", "scope":{"included":scope, "excluded":[]}, "acceptance":[], "status":"active", "phase":"discovery", "checkpoint":"created"}
    event = {"type":"task_started", "timestamp":timestamp, "task_id":task_id, "checkpoint":"created"}
    append_jsonl(tasks, value); append_jsonl(root/".agent/events/events.jsonl", event); update_state(root, task_id, "DISCOVERY", goal=goal, in_progress=[task_id], next_actions=["create plan"]); log_run(root, task_id, "started", attempt_id=attempt_id)
    return {"command":"task_start", **value, "status":"created", "routing":route(goal, scope)}, EXIT_OK

def task_status(root: Path, task_id: str):
    path = root / ".agent/tasks/index.jsonl"
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []
    found = [x for x in rows if x.get("task_id") == task_id]
    return {"command":"task_status", "status":"healthy" if found else "missing", "tasks":found}, EXIT_OK if found else EXIT_BLOCKED

def task_update(root: Path, task_id: str, state: str, checkpoint: str):
    path = root / ".agent/tasks/index.jsonl"; rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []
    found = next((x for x in rows if x.get("task_id") == task_id), None)
    if not found: return {"command":"task_update", "status":"missing", "task_id":task_id}, EXIT_BLOCKED
    found.update({"status":state, "checkpoint":checkpoint, "phase":"completed" if state == "completed" else found.get("phase")})
    path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    event_type = "task_completed" if state == "completed" else "task_failed"
    append_jsonl(root/".agent/events/events.jsonl", {"type":event_type, "timestamp":now(), "task_id":task_id, "checkpoint":checkpoint})
    update_state(root, None if state == "completed" else task_id, "DONE" if state == "completed" else "BLOCKED", completed=[task_id] if state == "completed" else [], in_progress=[] if state == "completed" else [task_id], next_actions=[] if state == "completed" else ["inspect failure"])
    log_run(root, task_id, state, checkpoint=checkpoint)
    return {"command":"task_update", "status":state, "task_id":task_id, "checkpoint":checkpoint}, EXIT_OK

def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists(): return {}
    if yaml is None: raise RuntimeError("PyYAML is required for .agent runtime files")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

def root_from_cli() -> Path:
    here = Path(__file__).resolve()
    return here.parents[2] if here.parent.name == "compiler" else Path.cwd()

def emit(value: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2) if as_json else "\n".join(f"{k}: {v}" for k, v in value.items()))

def doctor(root: Path):
    required = ["constitution.md", "README.md", "runtime.yaml", "gate.yaml", "loop-budget.yaml", "config.yaml", "context/builder.yaml", "index/knowledge-index.yaml", "state/current.yaml"]
    missing = [f".agent/{p}" for p in required if not (root / ".agent" / p).exists()]
    runtime = load_yaml(root / ".agent/runtime.yaml")
    status = "blocked" if missing else ("warning" if runtime.get("mode") != "report_only" else "healthy")
    value = {"command":"doctor", "status":status, "missing":missing, "mode":runtime.get("mode", "unknown"), "level":runtime.get("level", "unknown")}
    return value, EXIT_BLOCKED if missing else (EXIT_WARN if status == "warning" else EXIT_OK)

def status(root: Path):
    state = load_yaml(root / ".agent/state/current.yaml")
    log = root / ".agent/loop-run-log.jsonl"
    runs = sum(1 for x in log.read_text(encoding="utf-8").splitlines() if x.strip()) if log.exists() else 0
    return {"command":"status", "status":"healthy", "phase":state.get("phase"), "task_id":state.get("current_task_id"), "runs":runs}, EXIT_OK

def validate(root: Path):
    _, code = doctor(root); errors = []
    required = ["constitution.md", "README.md", "runtime.yaml", "gate.yaml", "loop-budget.yaml", "config.yaml", "context/builder.yaml", "index/knowledge-index.yaml", "state/current.yaml"]
    errors.extend(f".agent/{p}" for p in required if not (root / ".agent" / p).exists())
    runtime = load_yaml(root / ".agent/runtime.yaml")
    if runtime.get("level") not in {"L1", "L2", "L3"}: errors.append("runtime.level must be L1, L2, or L3")
    if runtime.get("level") == "L3" and not runtime.get("human_gate", False): errors.append("L3 requires human_gate=true")
    if runtime.get("max_subagents", 0) < 0: errors.append("runtime.max_subagents cannot be negative")
    routing = load_yaml(root / ".agent/routing.yaml")
    if int(routing.get("max_child_agents", 0)) > int(runtime.get("max_subagents", 0)):
        errors.append("runtime.max_subagents must be >= routing.max_child_agents")
    tasks = root / ".agent/tasks/index.jsonl"
    if tasks.exists():
        for line in tasks.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            try: record = json.loads(line)
            except json.JSONDecodeError: errors.append("invalid task JSONL record"); continue
            for field in ("id", "title", "created_at", "owner", "model_tier", "scope", "acceptance", "status"):
                if field not in record: errors.append(f"task record missing {field}")
    events = root / ".agent/events/events.jsonl"
    if events.exists():
        for line in events.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            try: record = json.loads(line)
            except json.JSONDecodeError: errors.append("invalid event JSONL record"); continue
            for field in ("type", "timestamp", "task_id"):
                if field not in record: errors.append(f"event record missing {field}")
    return {"command":"validate", "status":"blocked" if errors else "healthy", "errors":errors}, EXIT_BLOCKED if errors else code

def context(root: Path, task: str, budget: int):
    selected, total = [], 0
    for path in [root/".agent/constitution.md", root/".agent/README.md", root/".agent/state/current.yaml"]:
        size = path.stat().st_size if path.exists() else 0
        if total + size > budget: continue
        selected.append({"path":str(path.relative_to(root)), "bytes":size, "sha256":hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None}); total += size
    manifest = {"task":task, "budget_bytes":budget, "selected":selected, "bytes":total}
    (root/".agent/context").mkdir(parents=True, exist_ok=True)
    (root/".agent/context/manifest.yaml").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"command":"context", "status":"healthy", **manifest}, EXIT_OK

def gate(root: Path, changed: list[str]):
    config = load_yaml(root/".agent/gate.yaml"); deny = config.get("denylist", [])
    blocked = [f for f in changed if any(f.lower().startswith(str(p).lower().removeprefix("./")) for p in deny)]
    maximum = int(config.get("max_changed_files", 50))
    if len(changed) > maximum: blocked.append(f"changed file count {len(changed)} exceeds {maximum}")
    return {"command":"gate", "status":"blocked" if blocked else "healthy", "changed":changed, "reasons":blocked}, EXIT_BLOCKED if blocked else EXIT_OK

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Loop Engineering report-first runtime")
    p.add_argument("command", choices=["doctor","status","validate","context","gate","route","task-start","task-status","task-finish","task-fail"]); p.add_argument("--root", type=Path); p.add_argument("--json", action="store_true"); p.add_argument("--task", default="unspecified"); p.add_argument("--task-id", default=""); p.add_argument("--checkpoint", default=""); p.add_argument("--budget", type=int, default=50000); p.add_argument("files", nargs="*")
    a, unknown = p.parse_known_args(argv)
    if a.command in {"gate", "route", "task-start"}: a.files.extend(unknown)
    elif unknown: p.error("unrecognized arguments: " + " ".join(unknown))
    root = (a.root or root_from_cli()).resolve()
    fn = {"doctor":lambda:doctor(root), "status":lambda:status(root), "validate":lambda:validate(root), "context":lambda:context(root,a.task,a.budget), "gate":lambda:gate(root,a.files), "route":lambda:(route(a.task,a.files), EXIT_OK), "task-start":lambda:task_start(root,a.task,a.files), "task-status":lambda:task_status(root,a.task_id), "task-finish":lambda:task_update(root,a.task_id,"completed",a.checkpoint), "task-fail":lambda:task_update(root,a.task_id,"failed",a.checkpoint)}[a.command]
    value, code = fn(); emit(value, a.json); return code

if __name__ == "__main__": raise SystemExit(main())
