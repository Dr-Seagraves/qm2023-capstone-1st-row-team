"""Project root entrypoint for full reproducibility.

This wrapper runs code/reproduce_all.py so `python reproduce_all.py` works
from the repository root.
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    script_path = project_root / "code" / "reproduce_all.py"
    runpy.run_path(str(script_path), run_name="__main__")
