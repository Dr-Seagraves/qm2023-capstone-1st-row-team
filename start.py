"""
Start the Hurricane x Real-Estate dashboard.

Usage
-----
    python start.py          # dev mode: Vite + Flask
    python start.py --prod   # serve built React bundle from Flask
    python start.py --port 8080
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DASHBOARD = ROOT / "dashboard"
FRONTEND = DASHBOARD / "frontend"
DIST = FRONTEND / "dist"

# Force unbuffered output so the user sees lines immediately
os.environ["PYTHONUNBUFFERED"] = "1"


def _print(*args, **kwargs):
    """Print with flush so output is visible immediately in VS Code terminals."""
    print(*args, **kwargs, flush=True)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

# Common Node.js install locations on Windows that may not be in PATH
_WIN_NODE_DIRS = [
    r"C:\Program Files\nodejs",
    r"C:\Program Files (x86)\nodejs",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\nodejs"),
    os.path.expandvars(r"%APPDATA%\nvm\current"),
    os.path.expandvars(r"%LOCALAPPDATA%\fnm_multishells"),
]


def _find_node_on_disk():
    """Try to locate node/npm even if they're not on PATH (Windows)."""
    if sys.platform != "win32":
        return False
    for d in _WIN_NODE_DIRS:
        node_exe = Path(d) / "node.exe"
        npm_cmd = Path(d) / "npm.cmd"
        if node_exe.exists() and npm_cmd.exists():
            # Prepend to PATH so child processes can find them
            os.environ["PATH"] = d + ";" + os.environ.get("PATH", "")
            _print(f"[start] Found Node.js at {d} (added to PATH)")
            return True
    return False


def _node_is_available():
    """Return True if node and npm are on PATH."""
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        subprocess.run([npm, "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _ensure_node():
    """Make sure node/npm are available; search common dirs first."""
    if _node_is_available():
        return True
    # On Windows, Node may be installed but missing from this session's PATH
    if _find_node_on_disk() and _node_is_available():
        return True
    # Refresh PATH from registry (picks up recently installed packages)
    _refresh_path_windows()
    if _node_is_available():
        return True
    # Last resort: try winget (don't try MSI - it needs admin)
    if sys.platform == "win32":
        try:
            _print("[start] Node.js not found. Trying winget install ...")
            subprocess.check_call(
                ["winget", "install", "--id", "OpenJS.NodeJS.LTS",
                 "--accept-package-agreements", "--accept-source-agreements"],
                timeout=120,
            )
            _refresh_path_windows()
            if _node_is_available():
                _print("[start] Node.js installed via winget.")
                return True
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
    _print("[start] WARNING: Node.js could not be found or installed.")
    _print("         Install it from https://nodejs.org/ and restart this script.")
    return False


def _refresh_path_windows():
    """Re-read PATH from the Windows registry so a freshly-installed node is found."""
    if sys.platform != "win32":
        return
    try:
        import winreg
    except ImportError:
        return
    path_parts = []
    for hive, sub_key in [
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        (winreg.HKEY_CURRENT_USER, r"Environment"),
    ]:
        try:
            with winreg.OpenKey(hive, sub_key) as key:
                val, _ = winreg.QueryValueEx(key, "Path")
                path_parts.extend(val.split(";"))
        except OSError:
            continue
    if path_parts:
        os.environ["PATH"] = ";".join(dict.fromkeys(p for p in path_parts if p))


def _pip_install():
    """Install Python requirements if flask is not importable."""
    try:
        import flask          # noqa: F401
        import flask_cors     # noqa: F401
    except ImportError:
        _print("[start] Installing Python dependencies ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r",
                               str(ROOT / "requirements.txt")])


def _npm(cmd, cwd=FRONTEND):
    """Run an npm command inside the frontend directory."""
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    subprocess.check_call([npm] + cmd, cwd=str(cwd))


def _npm_install():
    """Install Node dependencies if node_modules is missing."""
    if not (FRONTEND / "node_modules").exists():
        _print("[start] Installing frontend dependencies (npm install) ...")
        _npm(["install"])


def _build_frontend():
    """Build the React production bundle if dist/ doesn't exist."""
    if not (DIST / "index.html").exists():
        _print("[start] Building React frontend (npm run build) ...")
        _npm(["run", "build"])


# ---------------------------------------------------------------------------
# launchers
# ---------------------------------------------------------------------------

def _start_flask(port, host="0.0.0.0"):
    """Import and run the Flask app."""
    # Make code/ importable for config_paths, logging_config, etc.
    code_dir = str(ROOT / "code")
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    # Make project root importable for dashboard package
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from dashboard.app import create_app
    app = create_app()
    _print(f"[start] Flask API running on http://localhost:{port}")
    app.run(host=host, port=port, debug=False)


def _start_dev(api_port):
    """Start Vite dev server + Flask API in parallel."""
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    vite = subprocess.Popen(
        [npm, "run", "dev"], cwd=str(FRONTEND),
        env={**os.environ, "BROWSER": "none"},
    )
    time.sleep(3)
    _print("[start] Vite dev server starting at http://localhost:5173")
    webbrowser.open("http://localhost:5173")
    try:
        _start_flask(api_port)
    finally:
        vite.terminate()


def _start_flask_only(api_port):
    """Run Flask alone when Node.js is unavailable."""
    _print("[start] Running Flask API only (no frontend dev server).")
    _print(f"[start] API will be at http://localhost:{api_port}")
    _print("[start] To use the dashboard, install Node.js and run again.")
    webbrowser.open(f"http://localhost:{api_port}")
    _start_flask(api_port)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Launch the dashboard")
    ap.add_argument("--prod", action="store_true",
                    help="Serve built React bundle from Flask (no Vite dev server)")
    ap.add_argument("--port", type=int, default=5000,
                    help="Flask API port (default 5000)")
    args = ap.parse_args()

    _print("=" * 50)
    _print("  Hurricane x Real-Estate Dashboard")
    _print("=" * 50)

    _pip_install()

    has_node = _ensure_node()

    if args.prod:
        if has_node:
            _npm_install()
            _build_frontend()
        _print(f"[start] Opening http://localhost:{args.port}")
        webbrowser.open(f"http://localhost:{args.port}")
        _start_flask(args.port)
    else:
        if has_node:
            _npm_install()
            _start_dev(args.port)
        else:
            _start_flask_only(args.port)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        _print(f"\n[start] ERROR: {exc}")
        _print("[start] Press Enter to exit...")
        input()
