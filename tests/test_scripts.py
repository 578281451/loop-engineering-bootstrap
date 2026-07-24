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
    assert "created=10" in first
    assert "created=0" in second
    assert "preserved=10" in second


def test_host_entry_integration_is_idempotent(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# Existing rules\n", encoding="utf-8")
    first = run_script("integrate_agent_entry.py", "--root", str(tmp_path), cwd=tmp_path)
    second = run_script("integrate_agent_entry.py", "--root", str(tmp_path), cwd=tmp_path)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "updated" in first
    assert "unchanged" in second
    assert content.count("LOOP-ENGINEERING:START") == 1
