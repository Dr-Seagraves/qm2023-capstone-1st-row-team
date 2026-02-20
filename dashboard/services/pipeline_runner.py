"""
Pipeline Runner — execute fetch/filter/merge scripts via subprocess.
"""
from __future__ import annotations
import subprocess
import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))
from config_paths import CODE_DIR, FETCH_DIR, CLEAN_DIR, FILTER_DIR, MERGE_DIR, BUILD_DIR, LOGS_DIR
from logging_config import setup_logger

logger = setup_logger("pipeline.runner")

# Status file to persist run history across server restarts
STATUS_FILE = LOGS_DIR / "pipeline_status.json"

PIPELINE_STEPS = {
    "fetch": {
        "label": "Fetch Data",
        "script": str(FETCH_DIR / "fetch_all.py"),
        "description": "Download all data sources to data/raw/",
    },
    "clean": {
        "label": "Clean Data",
        "script": str(CLEAN_DIR / "clean_all.py"),
        "description": "Validate formats, remove nulls, detect outliers",
    },
    "build": {
        "label": "Build Dataset",
        "script": str(BUILD_DIR / "build_master.py"),
        "description": "Filter to Florida, merge all sources → master_dataset.csv",
    },
}


def _load_status() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {step: {"status": "idle", "last_run": None, "output": ""} for step in PIPELINE_STEPS}


def _save_status(status: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=2)


def get_pipeline_status() -> dict:
    status = _load_status()
    steps = []
    for step_id, step_info in PIPELINE_STEPS.items():
        s = status.get(step_id, {"status": "idle", "last_run": None, "output": ""})
        steps.append({
            "id": step_id,
            "label": step_info["label"],
            "description": step_info["description"],
            **s,
        })
    return {"steps": steps}


def run_step(step_id: str) -> dict:
    if step_id not in PIPELINE_STEPS:
        return {"status": "error", "message": f"Unknown step: {step_id}"}

    step_info = PIPELINE_STEPS[step_id]
    status = _load_status()

    status[step_id] = {"status": "running", "last_run": time.time(), "output": ""}
    _save_status(status)

    logger.info("Running step: %s (%s)", step_id, step_info["script"])

    try:
        result = subprocess.run(
            [sys.executable, step_info["script"]],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(Path(step_info["script"]).parent),
        )
        output = result.stdout + ("\n" + result.stderr if result.stderr else "")
        step_status = "success" if result.returncode == 0 else "error"
    except subprocess.TimeoutExpired:
        output = "Timed out after 600 seconds"
        step_status = "error"
    except Exception as exc:
        output = str(exc)
        step_status = "error"

    status[step_id] = {
        "status": step_status,
        "last_run": time.time(),
        "output": output[-5000:],  # keep last 5000 chars
    }
    _save_status(status)
    logger.info("Step %s: %s", step_id, step_status)

    return {"step": step_id, "status": step_status, "output": output[-5000:]}


def run_all() -> dict:
    results = []
    step_ids = list(PIPELINE_STEPS.keys())
    total = len(step_ids)

    # Write a progress marker so the frontend can poll
    status = _load_status()
    status["_progress"] = {"running": True, "current": 0, "total": total, "current_step": ""}
    _save_status(status)

    for idx, step_id in enumerate(step_ids):
        status = _load_status()
        status["_progress"] = {"running": True, "current": idx, "total": total, "current_step": step_id}
        _save_status(status)

        r = run_step(step_id)
        results.append(r)
        if r["status"] == "error":
            logger.warning("Pipeline stopped at %s due to error", step_id)
            break

    # Clear progress
    status = _load_status()
    status["_progress"] = {"running": False, "current": total, "total": total, "current_step": ""}
    _save_status(status)

    return {"results": results}


def get_progress() -> dict:
    """Return current pipeline progress for polling."""
    status = _load_status()
    return status.get("_progress", {"running": False, "current": 0, "total": 0, "current_step": ""})
