from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run_script(name: str, *args: str, cwd: Path) -> str:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def test_bootstrap_is_additive(tmp_path: Path) -> None:
    first = run_script("bootstrap_loop.py", "--root", str(tmp_path), cwd=tmp_path)
    second = run_script("bootstrap_loop.py", "--root", str(tmp_path), cwd=tmp_path)
    assert "created=" in first
    assert "created=0" in second
    assert "preserved=" in second


def test_generated_runtime_is_report_first_and_validates(tmp_path: Path) -> None:
    run_script("bootstrap_loop.py", "--root", str(tmp_path), cwd=tmp_path)
    cli = tmp_path / ".agent" / "compiler" / "cli.py"
    result = subprocess.run([sys.executable, str(cli), "validate", "--root", str(tmp_path), "--json"], capture_output=True, text=True)
    assert result.returncode == 0
    assert '"status": "healthy"' in result.stdout
    runtime = (tmp_path / ".agent/runtime.yaml").read_text(encoding="utf-8")
    assert "mode: report_only" in runtime
    assert "max_subagents: 3" in runtime
    assert "max_subagents: 3" in (tmp_path / ".agent/loop-budget.yaml").read_text(encoding="utf-8")


def test_generated_runtime_gate_blocks_secrets(tmp_path: Path) -> None:
    run_script("bootstrap_loop.py", "--root", str(tmp_path), cwd=tmp_path)
    cli = tmp_path / ".agent" / "compiler" / "cli.py"
    result = subprocess.run([sys.executable, str(cli), "gate", "--root", str(tmp_path), ".env"], capture_output=True, text=True)
    assert result.returncode == 2


def test_runtime_routes_simple_and_cross_boundary_tasks(tmp_path: Path) -> None:
    run_script("bootstrap_loop.py", "--root", str(tmp_path), cwd=tmp_path)
    cli = tmp_path / ".agent" / "compiler" / "cli.py"
    simple = subprocess.run([sys.executable, str(cli), "route", "--root", str(tmp_path), "--task", "rename a label", "--json"], capture_output=True, text=True)
    cross = subprocess.run([sys.executable, str(cli), "route", "--root", str(tmp_path), "--task", "fix frontend API and database bug", "--json"], capture_output=True, text=True)
    assert '"level": "S0"' in simple.stdout
    assert '"level": "S2"' in cross.stdout


def test_runtime_task_start_is_idempotent(tmp_path: Path) -> None:
    run_script("bootstrap_loop.py", "--root", str(tmp_path), cwd=tmp_path)
    cli = tmp_path / ".agent" / "compiler" / "cli.py"
    args = [sys.executable, str(cli), "task-start", "--root", str(tmp_path), "--task", "fix checkout bug", "src/checkout.py", "--json"]
    first = subprocess.run(args, capture_output=True, text=True)
    second = subprocess.run(args, capture_output=True, text=True)
    assert '"status": "created"' in first.stdout
    assert '"status": "resumed"' in second.stdout

    task_id = __import__("json").loads(first.stdout)["task_id"]
    finish = subprocess.run([sys.executable, str(cli), "task-finish", "--root", str(tmp_path), "--task-id", task_id, "--checkpoint", "tests-passed", "--json"], capture_output=True, text=True)
    assert finish.returncode == 0
    assert '"status": "completed"' in finish.stdout
    assert (tmp_path / ".agent/events/events.jsonl").read_text(encoding="utf-8").count("task_completed") == 1


def test_host_entry_integration_is_idempotent(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Existing rules\n", encoding="utf-8")
    first = run_script("integrate_agent_entry.py", "--root", str(tmp_path), cwd=tmp_path)
    second = run_script("integrate_agent_entry.py", "--root", str(tmp_path), cwd=tmp_path)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "updated" in first
    assert "unchanged" in second
    assert content.count("LOOP-ENGINEERING:START") == 1
