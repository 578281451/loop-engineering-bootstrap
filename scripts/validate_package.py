from __future__ import annotations
import argparse
from pathlib import Path

REQUIRED = ["SKILL.md", "README.md", "VERSION", "CHANGELOG.md", "scripts/bootstrap_loop.py", "scripts/loop_cli.py"]

def validate(root: Path) -> list[str]:
    errors = [f"missing: {p}" for p in REQUIRED if not (root / p).exists()]
    # Git metadata and local caches are excluded by the packaging command.
    return errors

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("root", type=Path, nargs="?", default=Path(".")); a = p.parse_args()
    errors = validate(a.root.resolve())
    print("package healthy" if not errors else "\n".join(errors))
    raise SystemExit(1 if errors else 0)
