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


def test_generated_runtime_gate_blocks_secrets(tmp_path: Path) -> None:
    run_script("bootstrap_loop.py", "--root", str(tmp_path), cwd=tmp_path)
    cli = tmp_path / ".agent" / "compiler" / "cli.py"
    result = subprocess.run([sys.executable, str(cli), "gate", "--root", str(tmp_path), ".env"], capture_output=True, text=True)
    assert result.returncode == 2


def test_host_entry_integration_is_idempotent(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Existing rules\n", encoding="utf-8")
    first = run_script("integrate_agent_entry.py", "--root", str(tmp_path), cwd=tmp_path)
    second = run_script("integrate_agent_entry.py", "--root", str(tmp_path), cwd=tmp_path)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "updated" in first
    assert "unchanged" in second
    assert content.count("LOOP-ENGINEERING:START") == 1
