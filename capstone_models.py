"""Project root entrypoint for Milestone 3 models.

This wrapper runs the main M3 script in code/capstone_models.py so that
`python capstone_models.py` works from the repository root.
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    script_path = project_root / "code" / "capstone_models.py"
    runpy.run_path(str(script_path), run_name="__main__")
