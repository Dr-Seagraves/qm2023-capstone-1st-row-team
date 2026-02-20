"""Chart Builder Service — load CSV data and generate Plotly exports."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "code"))
from config_paths import PROCESSED_DATA_DIR, FINAL_DATA_DIR, RAW_DATA_DIR
from logging_config import setup_logger

logger = setup_logger("dashboard.charts")

try:
    import pandas as pd
except ImportError:
    pd = None

SCAN_DIRS = [FINAL_DATA_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR]


def get_available_datasets() -> list[dict]:
    """Scan data directories for CSV files and return metadata."""
    datasets = []
    seen = set()
    for d in SCAN_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.csv")):
            if f.name in seen:
                continue
            seen.add(f.name)
            try:
                if pd:
                    df = pd.read_csv(f, nrows=5)
                    cols = []
                    for col in df.columns:
                        dtype = str(df[col].dtype)
                        cols.append({"name": col, "dtype": dtype})
                else:
                    # Fallback: just read header
                    with open(f, encoding="utf-8", errors="replace") as fh:
                        header = fh.readline().strip().split(",")
                    cols = [{"name": c.strip().strip('"'), "dtype": "unknown"} for c in header]
                datasets.append({
                    "key": f.name,
                    "filename": f.name,
                    "path": str(f),
                    "folder": d.name,
                    "columns": cols,
                })
            except Exception as exc:
                logger.warning("Failed to scan %s: %s", f.name, exc)
    return datasets


def load_chart_data(dataset_filename: str, x_col: str, y_cols: list[str],
                    limit: int = 5000) -> dict:
    """Load specific columns from a CSV and return as JSON-ready dict."""
    if not pd:
        return {"error": "pandas is not installed"}

    # Find the file
    target = None
    for d in SCAN_DIRS:
        candidate = d / dataset_filename
        if candidate.exists():
            target = candidate
            break
    if not target:
        return {"error": f"Dataset not found: {dataset_filename}"}

    try:
        all_cols = [x_col] + [c for c in y_cols if c != x_col]
        df = pd.read_csv(target, usecols=all_cols, nrows=limit)
        # Drop rows where x is null
        df = df.dropna(subset=[x_col])
        # Return records-oriented data for Recharts
        rows = df.to_dict(orient="records")
        return {
            "rows": rows,
            "x_column": x_col,
            "y_columns": [c for c in y_cols if c in df.columns],
            "count": len(df),
        }
    except Exception as exc:
        return {"error": str(exc)}


def export_plotly_chart(dataset_filename: str, x_col: str, y_cols: list[str],
                        chart_type: str = "line", title: str = "",
                        fmt: str = "png") -> bytes | None:
    """Generate a chart image using Plotly (server-side)."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        logger.warning("plotly not installed — cannot export charts")
        return None

    data = load_chart_data(dataset_filename, x_col, y_cols)
    if "error" in data:
        logger.error("Chart export error: %s", data["error"])
        return None

    fig = go.Figure()
    # Extract x and y values from rows-oriented data
    rows = data["rows"]
    x_vals = [r.get(x_col) for r in rows]

    chart_map = {
        "line": go.Scatter,
        "scatter": go.Scatter,
        "bar": go.Bar,
        "area": go.Scatter,
    }

    for col_name in data["y_columns"]:
        y_vals = [r.get(col_name) for r in rows]
        trace_cls = chart_map.get(chart_type, go.Scatter)
        kwargs = {"x": x_vals, "y": y_vals, "name": col_name}
        if chart_type == "scatter":
            kwargs["mode"] = "markers"
        elif chart_type == "area":
            kwargs["fill"] = "tozeroy"
            kwargs["mode"] = "lines"
        fig.add_trace(trace_cls(**kwargs))

    fig.update_layout(
        title=title or f"{', '.join(y_cols)} vs {x_col}",
        xaxis_title=x_col,
        template="plotly_dark",
        paper_bgcolor="#000000",
        plot_bgcolor="#0a0a0a",
        font=dict(family="Inter, sans-serif", color="#f5f5f5"),
        margin=dict(t=60, b=40, l=50, r=30),
    )

    try:
        img_bytes = fig.to_image(format=fmt, width=1200, height=600, scale=2)
        return img_bytes
    except Exception as exc:
        logger.error("Plotly export failed: %s", exc)
        return None
