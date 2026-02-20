"""Charts API — dataset discovery, data loading, and Plotly export."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))

from flask import Blueprint, jsonify, request, Response
from dashboard.services.chart_builder import (
    get_available_datasets,
    load_chart_data,
    export_plotly_chart,
)
from logging_config import setup_logger

logger = setup_logger("dashboard.charts")
bp = Blueprint("charts", __name__, url_prefix="/api/charts")


@bp.route("/columns", methods=["GET"])
def list_datasets():
    """Return available datasets with their column names and dtypes."""
    datasets = get_available_datasets()
    return jsonify(datasets)


@bp.route("/data", methods=["POST"])
def chart_data():
    """Load column data from a dataset for client-side charting."""
    data = request.get_json() or {}
    dataset = data.get("dataset", "")
    x_col = data.get("x_column", "")
    y_cols = data.get("y_columns", [])
    limit = data.get("limit", 5000)

    if not dataset or not x_col or not y_cols:
        return jsonify({"error": "dataset, x_column, and y_columns are required"}), 400

    result = load_chart_data(dataset, x_col, y_cols, limit=limit)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@bp.route("/export", methods=["POST"])
def chart_export():
    """Generate a chart image using Plotly (server-side) and return PNG/SVG."""
    data = request.get_json() or {}
    dataset = data.get("dataset", "")
    x_col = data.get("x_column", "")
    y_cols = data.get("y_columns", [])
    chart_type = data.get("chart_type", "line")
    title = data.get("title", "")
    fmt = data.get("format", "png")

    if not dataset or not x_col or not y_cols:
        return jsonify({"error": "dataset, x_column, and y_columns are required"}), 400

    img_bytes = export_plotly_chart(dataset, x_col, y_cols,
                                    chart_type=chart_type, title=title, fmt=fmt)
    if img_bytes is None:
        return jsonify({"error": "Export failed. Plotly+kaleido may not be installed."}), 500

    mime = "image/png" if fmt == "png" else "image/svg+xml"
    return Response(img_bytes, mimetype=mime,
                    headers={"Content-Disposition": f"attachment; filename=chart.{fmt}"})
