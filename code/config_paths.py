"""
Capstone Project - Centralized Path Configuration
==================================================

This module provides centralized path management for the capstone project.
Import this at the top of every script to ensure consistent, relative paths.

Usage:
    from config_paths import RAW_DATA_DIR, FINAL_DATA_DIR, FIGURES_DIR, TABLES_DIR

    df = pd.read_csv(RAW_DATA_DIR / 'my_data.csv')
    merged.to_csv(FINAL_DATA_DIR / 'analysis_panel.csv', index=False)
    plt.savefig(FIGURES_DIR / 'my_plot.png', dpi=300)
"""

from pathlib import Path
import sys

# ==============================================================================
# PROJECT ROOT DETECTION
# ==============================================================================

def find_project_root():
    """
    Find project root by looking for key indicators.
    Searches upward from current file location.
    """
    current = Path(__file__).resolve().parent

    # Check current directory first
    for indicator in ['README.md', 'requirements.txt', '.git']:
        if (current / indicator).exists():
            return current

    # Search up to 3 parent levels
    for parent in current.parents[:3]:
        for indicator in ['README.md', 'requirements.txt', '.git']:
            if (parent / indicator).exists():
                return parent

    # Fallback: assume parent of code/ is project root (when config_paths lives in code/)
    return current.parent

PROJECT_ROOT = find_project_root()

# ==============================================================================
# DIRECTORY PATHS
# ==============================================================================

# Config directory
CONFIG_DIR = PROJECT_ROOT / 'config'

# Code directory
CODE_DIR = PROJECT_ROOT / 'code'
FETCH_DIR = CODE_DIR / 'fetch'
CLEAN_DIR = CODE_DIR / 'clean'
FILTER_DIR = CODE_DIR / 'filter'
MERGE_DIR = CODE_DIR / 'merge'
BUILD_DIR = CODE_DIR / 'build'

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
FINAL_DATA_DIR = DATA_DIR / 'final'

# Results directories
RESULTS_DIR = PROJECT_ROOT / 'results'
FIGURES_DIR = RESULTS_DIR / 'figures'
TABLES_DIR = RESULTS_DIR / 'tables'
REPORTS_DIR = RESULTS_DIR / 'reports'

# Logs directory
LOGS_DIR = PROJECT_ROOT / 'logs'

# Dashboard directory
DASHBOARD_DIR = PROJECT_ROOT / 'dashboard'

# ==============================================================================
# DIRECTORY CREATION
# ==============================================================================

def ensure_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        CONFIG_DIR,
        CODE_DIR,
        FETCH_DIR,
        CLEAN_DIR,
        FILTER_DIR,
        MERGE_DIR,
        BUILD_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        FINAL_DATA_DIR,
        FIGURES_DIR,
        TABLES_DIR,
        REPORTS_DIR,
        LOGS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print(f"[OK] Project structure verified at: {PROJECT_ROOT}")

# ==============================================================================
# UTF-8 ENCODING (Windows PowerShell fix) — must run BEFORE any Unicode output
# ==============================================================================

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Auto-create directories on import
ensure_directories()

# ==============================================================================
# VERIFICATION
# ==============================================================================

if __name__ == "__main__":
    """Run this script to verify path configuration."""
    try:
        from rich.console import Console
        from rich.table import Table
        console = Console()
        table = Table(title="Capstone Project Path Configuration", show_header=True)
        table.add_column("Variable", style="cyan", no_wrap=True)
        table.add_column("Path", style="green")
        table.add_column("Exists?", style="yellow")

        paths = {
            'PROJECT_ROOT': PROJECT_ROOT,
            'CONFIG_DIR': CONFIG_DIR,
            'CODE_DIR': CODE_DIR,
            'FETCH_DIR': FETCH_DIR,
            'FILTER_DIR': FILTER_DIR,
            'MERGE_DIR': MERGE_DIR,
            'DATA_DIR': DATA_DIR,
            'RAW_DATA_DIR': RAW_DATA_DIR,
            'PROCESSED_DATA_DIR': PROCESSED_DATA_DIR,
            'FINAL_DATA_DIR': FINAL_DATA_DIR,
            'RESULTS_DIR': RESULTS_DIR,
            'FIGURES_DIR': FIGURES_DIR,
            'TABLES_DIR': TABLES_DIR,
            'REPORTS_DIR': REPORTS_DIR,
            'LOGS_DIR': LOGS_DIR,
            'DASHBOARD_DIR': DASHBOARD_DIR,
        }

        for name, path in paths.items():
            exists = "\u2713" if path.exists() else "\u2717"
            table.add_row(name, str(path), exists)

        console.print(table)
        console.print("\n[bold green]All paths verified![/bold green]")
    except ImportError:
        for name, path in [('PROJECT_ROOT', PROJECT_ROOT), ('RAW_DATA_DIR', RAW_DATA_DIR),
                          ('FINAL_DATA_DIR', FINAL_DATA_DIR), ('FIGURES_DIR', FIGURES_DIR),
                          ('TABLES_DIR', TABLES_DIR)]:
            print(f"  {name}: {path} ({'exists' if path.exists() else 'missing'})")
        print("\nAll paths verified.")
