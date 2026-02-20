"""Pipeline API — run fetch/filter/merge steps."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from dashboard.services.pipeline_runner import get_pipeline_status, run_step, run_all, get_progress
from logging_config import setup_logger

logger = setup_logger("dashboard.pipeline")
bp = Blueprint("pipeline", __name__, url_prefix="/api/pipeline")


@bp.route("/status", methods=["GET"])
def pipeline_status():
    return jsonify(get_pipeline_status())


@bp.route("/run", methods=["POST"])
def pipeline_run():
    data = request.get_json() or {}
    step = data.get("step")  # None = run all

    if step:
        logger.info("Running pipeline step: %s", step)
        result = run_step(step)
    else:
        logger.info("Running full pipeline")
        result = run_all()

    return jsonify(result)


@bp.route("/progress", methods=["GET"])
def pipeline_progress():
    """Polled by the frontend to update the progress bar during a run."""
    return jsonify(get_progress())
