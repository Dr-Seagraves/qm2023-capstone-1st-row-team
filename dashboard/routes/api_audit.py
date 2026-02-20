"""AI Audit API — stub for future AI audit functionality."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request
from config_paths import REPORTS_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.audit")
bp = Blueprint("audit", __name__, url_prefix="/api/audit")

AUDIT_FILE = REPORTS_DIR / "ai_audit_notes.md"


@bp.route("", methods=["GET"])
def get_audit():
    content = ""
    if AUDIT_FILE.exists():
        content = AUDIT_FILE.read_text(encoding="utf-8", errors="replace")
    return jsonify({"content": content})


@bp.route("", methods=["PUT"])
def save_audit():
    data = request.get_json()
    content = data.get("content", "")
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_FILE.write_text(content, encoding="utf-8")
    logger.info("Saved AI audit notes (%d chars)", len(content))
    return jsonify({"status": "ok"})
