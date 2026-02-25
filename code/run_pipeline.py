#!/usr/bin/env python3
"""Run the full data pipeline: fetch -> clean -> build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_step(script_path: Path) -> None:
    if not script_path.exists():
        raise FileNotFoundError(f"Missing script: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)], check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    steps = [
        repo_root / "code" / "fetch" / "fetch_all.py",
        repo_root / "code" / "clean" / "clean_all.py",
        repo_root / "code" / "build" / "build_master.py",
    ]

    for step in steps:
        print(f"Running {step}...")
        run_step(step)

    print("Pipeline complete.")


if __name__ == "__main__":
    main()
