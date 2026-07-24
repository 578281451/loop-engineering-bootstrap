from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


def run(command: list[str]) -> str:
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or safely update an installed Skill.")
    parser.add_argument("--target", required=True, help="Installed Skill directory")
    parser.add_argument(
        "--source",
        default="https://github.com/578281451/loop-engineering-bootstrap.git",
    )
    parser.add_argument("--ref", default="main")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    remote_commit = run(["git", "ls-remote", args.source, f"refs/heads/{args.ref}"]).split()[0]
    print(f"remote: {remote_commit}")
    if not args.apply:
        print("check only; use --apply to install the remote version")
        return 0
    if not target.parent.exists():
        raise SystemExit(f"target parent does not exist: {target.parent}")
    with tempfile.TemporaryDirectory(prefix="loop-skill-update-") as staging_name:
        staging = Path(staging_name) / "source"
        run(["git", "clone", "--depth", "1", "--branch", args.ref, args.source, str(staging)])
        backup = target.with_name(
            f"{target.name}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        if target.exists():
            target.rename(backup)
            print(f"backup: {backup}")
        try:
            shutil.copytree(staging, target, ignore=shutil.ignore_patterns(".git"))
        except Exception:
            if target.exists():
                shutil.rmtree(target)
            if backup.exists():
                backup.rename(target)
            raise
    print(f"updated: {target}")
    print("restart the host agent before using the new Skill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
