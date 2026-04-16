"""Run the full capstone workflow from a clean clone.

Order:
1) Data pipeline (downloads/caches raw data and builds final dataset)
2) Milestone 3 models (regressions, diagnostics, robustness, forecasts, tables)
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent

    pipeline_script = project_root / "code" / "capstone_data_pipeline.py"
    models_script = project_root / "code" / "capstone_models.py"

    print("=" * 72)
    print("Reproducing full capstone outputs")
    print("=" * 72)
    print("Step 1/2: Running data pipeline...")
    runpy.run_path(str(pipeline_script), run_name="__main__")

    print("\nStep 2/2: Running M3 models...")
    runpy.run_path(str(models_script), run_name="__main__")

    print("\nDone. Outputs available under data/final/, results/tables/, and results/figures/.")
