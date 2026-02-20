"""Logs API — serve log file contents."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from config_paths import LOGS_DIR

bp = Blueprint("logs", __name__, url_prefix="/api/logs")

VALID_LOGS = ["fetch", "filter", "merge", "dashboard", "pipeline", "general"]


@bp.route("", methods=["GET"])
def list_logs():
    logs = []
    if LOGS_DIR.exists():
        for log_file in sorted(LOGS_DIR.glob("*.log")):
            logs.append({
                "name": log_file.stem,
                "filename": log_file.name,
                "size_bytes": log_file.stat().st_size,
                "modified": log_file.stat().st_mtime,
            })
    return jsonify(logs)


@bp.route("/<module>", methods=["GET"])
def get_log(module: str):
    if module not in VALID_LOGS:
        return jsonify({"error": f"Invalid log module: {module}"}), 400

    log_path = LOGS_DIR / f"{module}.log"
    if not log_path.exists():
        return jsonify({"module": module, "content": "", "lines": 0})

    tail = request.args.get("tail", default=200, type=int)
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail_lines = lines[-tail:] if len(lines) > tail else lines
    return jsonify({
        "module": module,
        "content": "\n".join(tail_lines),
        "lines": len(lines),
        "showing": len(tail_lines),
    })
