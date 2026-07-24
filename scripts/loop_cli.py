from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
try:
    import yaml
except ImportError:
    yaml = None

EXIT_OK, EXIT_WARN, EXIT_BLOCKED = 0, 1, 2

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
    p.add_argument("command", choices=["doctor","status","validate","context","gate"]); p.add_argument("--root", type=Path); p.add_argument("--json", action="store_true"); p.add_argument("--task", default="unspecified"); p.add_argument("--budget", type=int, default=50000); p.add_argument("files", nargs="*")
    a, unknown = p.parse_known_args(argv)
    if a.command == "gate": a.files.extend(unknown)
    elif unknown: p.error("unrecognized arguments: " + " ".join(unknown))
    root = (a.root or root_from_cli()).resolve()
    fn = {"doctor":lambda:doctor(root), "status":lambda:status(root), "validate":lambda:validate(root), "context":lambda:context(root,a.task,a.budget), "gate":lambda:gate(root,a.files)}[a.command]
    value, code = fn(); emit(value, a.json); return code

if __name__ == "__main__": raise SystemExit(main())
