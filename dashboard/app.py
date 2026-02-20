"""
Flask Application Factory
===========================

Creates the Flask app, registers API blueprints, configures CORS,
and serves the React production build in non-debug mode.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure code/ is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CODE_DIR = _PROJECT_ROOT / "code"
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from flask import Flask, send_from_directory
from flask_cors import CORS

from logging_config import setup_logger

logger = setup_logger("dashboard.app")


def create_app(debug: bool = False) -> Flask:
    """Create and configure the Flask application."""

    # React build output directory
    frontend_dist = Path(__file__).resolve().parent / "frontend" / "dist"

    app = Flask(
        __name__,
        static_folder=str(frontend_dist / "assets") if frontend_dist.exists() else None,
        static_url_path="/assets",
    )
    app.config["DEBUG"] = debug

    # CORS for React dev server (localhost:5173)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ---- Register API blueprints ----
    from dashboard.routes.api_settings import bp as settings_bp
    from dashboard.routes.api_dictionary import bp as dictionary_bp
    from dashboard.routes.api_pipeline import bp as pipeline_bp
    from dashboard.routes.api_reports import bp as reports_bp
    from dashboard.routes.api_charts import bp as charts_bp
    from dashboard.routes.api_audit import bp as audit_bp
    from dashboard.routes.api_logs import bp as logs_bp
    from dashboard.routes.api_clean import bp as clean_bp
    from dashboard.routes.api_merge import bp as merge_cfg_bp
    from dashboard.routes.api_data import bp as data_bp

    app.register_blueprint(settings_bp)
    app.register_blueprint(dictionary_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(charts_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(clean_bp)
    app.register_blueprint(merge_cfg_bp)
    app.register_blueprint(data_bp)

    # ---- Serve React SPA in production ----
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path: str):
        """Serve the React app. API routes are handled by blueprints above."""
        if path and (frontend_dist / path).is_file():
            return send_from_directory(str(frontend_dist), path)
        if frontend_dist.exists() and (frontend_dist / "index.html").exists():
            return send_from_directory(str(frontend_dist), "index.html")
        return (
            "<h1>Dashboard</h1>"
            "<p>React frontend not built yet. Run <code>npm run build</code> "
            "in <code>dashboard/frontend/</code> or use the React dev server "
            "at <a href='http://localhost:5173'>localhost:5173</a>.</p>"
        ), 200

    logger.info("Flask app created (debug=%s)", debug)
    return app
