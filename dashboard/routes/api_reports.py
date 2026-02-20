"""Reports API — list and serve markdown reports."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify
from config_paths import REPORTS_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.reports")
bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@bp.route("", methods=["GET"])
def list_reports():
    reports = []
    if REPORTS_DIR.exists():
        for md_file in sorted(REPORTS_DIR.glob("*.md")):
            reports.append({
                "filename": md_file.name,
                "size_bytes": md_file.stat().st_size,
                "modified": md_file.stat().st_mtime,
            })
    return jsonify(reports)


@bp.route("/<filename>", methods=["GET"])
def get_report(filename: str):
    report_path = REPORTS_DIR / filename
    if not report_path.exists() or not report_path.suffix == ".md":
        return jsonify({"error": "Report not found"}), 404
    content = report_path.read_text(encoding="utf-8", errors="replace")
    return jsonify({"filename": filename, "content": content})
