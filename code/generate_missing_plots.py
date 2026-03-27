"""
Generate missing plots for M2 EDA Dashboard
Plots 3 and 7: Dual-axis and scatter plots
"""
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FINAL = PROJECT_ROOT / "data" / "final" / "housing_analysis_panel.csv"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_FINAL.exists():
    raise FileNotFoundError(
        f"Expected dataset not found: {DATA_FINAL}. Run code/capstone_data_pipeline.py first."
    )

# Plot defaults
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.2)
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "figure.figsize": (14, 6),
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "lines.linewidth": 2,
})

def save_fig(fig, *names):
    """Save a figure using one or more output names (without extension)."""
    if not names:
        raise ValueError("At least one output figure name is required.")

    for name in names:
        path = FIGURES_DIR / f"{name}.png"
        fig.savefig(path)
        print(f"Saved → {path.relative_to(PROJECT_ROOT)}")

# ---------------------------------------------------------------------------
# Load data and convert from long to wide format
# ---------------------------------------------------------------------------
df_long = pd.read_csv(DATA_FINAL, parse_dates=["Date"])

# Pivot from long to wide format (Metro × Date × metric values)
df = df_long.pivot_table(
    index=["Metro", "Date"],
    columns="metric",
    values="value",
    aggfunc="first"
).reset_index()

# Sort and reset index
df.sort_values(["Metro", "Date"], inplace=True)
df.reset_index(drop=True, inplace=True)

# Add derived columns
df["Year"] = df["Date"].dt.year
df["YearMonth"] = df["Date"].dt.to_period("M")

# Drop ZHVF_Growth if present (too many missing values)
if "ZHVF_Growth" in df.columns:
    df.drop(columns=["ZHVF_Growth"], inplace=True)

print(f"Data shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# ---------------------------------------------------------------------------
# PLOT 3: Dual-Axis — ZHVI vs. Hurricane Cost
# ---------------------------------------------------------------------------
print("\n--- Generating Plot 3: Dual-Axis Plot ---")
required_plot3_cols = {"ZHVI", "hurricane_total_cost_billion"}
missing_plot3_cols = [c for c in required_plot3_cols if c not in df.columns]
if missing_plot3_cols:
    raise KeyError(f"Missing required columns for Plot 3: {missing_plot3_cols}")

state_zhvi = (
    df.dropna(subset=["ZHVI"])
    .groupby("Date")["ZHVI"]
    .mean()
    .sort_index()
)

state_hurr_cost = (
    df.groupby("Date")["hurricane_total_cost_billion"]
    .mean()
    .sort_index()
)

fig, ax1 = plt.subplots(figsize=(14, 7))

# Left axis: ZHVI
color_zhvi = "#1f77b4"
ax1.set_xlabel("Year", fontsize=13, fontweight="bold")
ax1.set_ylabel("Mean ZHVI ($ dollars)", fontsize=13, fontweight="bold", color=color_zhvi)
line1 = ax1.plot(state_zhvi.index, state_zhvi.values, linewidth=2.5, color=color_zhvi, 
                  marker="o", markersize=3, label="ZHVI", zorder=3)
ax1.tick_params(axis="y", labelcolor=color_zhvi, labelsize=11)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))

# Right axis: Hurricane cost
ax2 = ax1.twinx()
color_hurr = "#d62728"
ax2.set_ylabel("Mean Annual Hurricane Cost ($ billions)", fontsize=13, fontweight="bold", color=color_hurr)
line2 = ax2.plot(state_hurr_cost.index, state_hurr_cost.values, linewidth=2.5, color=color_hurr, 
                 marker="s", markersize=3, label="Hurricane Cost", zorder=2)
ax2.tick_params(axis="y", labelcolor=color_hurr, labelsize=11)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:.1f}B"))

ax1.set_title("Co-Movement: Home Values vs. Hurricane Costs (Annual Averages, Florida MSAs)", 
              fontsize=15, fontweight="bold", pad=20)
ax1.grid(True, alpha=0.4, linestyle="--")
ax1.xaxis.set_major_locator(mdates.YearLocator(2))
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax1.tick_params(axis="x", labelsize=11)

# Combined legend
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="upper left", fontsize=11, framealpha=0.9, edgecolor="black")

fig.tight_layout()
save_fig(fig, "dual_axis_zhvi_vs_hurricane_cost", "plot3_dual_axis_outcome_vs_driver")
plt.close()

# ---------------------------------------------------------------------------
# PLOT 7: Scatter Plots — ZHVI vs. Control Variables (Strong Correlations Only)
# ---------------------------------------------------------------------------
print("\n--- Generating Plot 7: Control Variable Scatter Plots ---")
control_vars = ["ZORI", "Income_Needed", "Sales_Count"]
control_vars = [c for c in control_vars if c in df.columns]

if not control_vars:
    raise KeyError("No control variables found for Plot 7. Expected at least one of ZORI, Income_Needed, Sales_Count.")

# Prepare data
plot_df = df[["ZHVI"] + control_vars].dropna()
print(f"Data for scatter plots: {plot_df.shape}")

n_cols = len(control_vars)
fig, axes = plt.subplots(1, n_cols, figsize=(6 * n_cols, 5.5))
if n_cols == 1:
    axes = [axes]

for idx, var in enumerate(control_vars):
    ax = axes[idx]
    
    # Format variable names for axis labels
    var_labels = {
        "ZORI": "Monthly Rent Index ($)",
        "Income_Needed": "Income Required to Buy ($)",
        "Sales_Count": "Monthly Sales Count"
    }
    
    # Scatter plot
    ax.scatter(plot_df[var], plot_df["ZHVI"], alpha=0.4, s=25, color="#1f77b4", edgecolors="none")
    
    # Regression line with thicker appearance
    x = plot_df[var].dropna()
    y = plot_df.loc[plot_df[var].notna(), "ZHVI"]
    if x.nunique() > 1 and len(x) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(plot_df[var].min(), plot_df[var].max(), 100)
        ax.plot(x_line, p(x_line), "r--", linewidth=2.5, label=f"Linear Fit (slope={z[0]:.2f})", zorder=5)
    else:
        ax.text(0.03, 0.97, "Insufficient variation for linear fit", transform=ax.transAxes,
                fontsize=9, verticalalignment="top", bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"})
    
    # Correlation
    corr = plot_df[var].corr(plot_df["ZHVI"])
    
    # Better axis labeling
    ax.set_xlabel(var_labels.get(var, var), fontsize=12, fontweight="bold")
    ax.set_ylabel("Home Value Index (ZHVI, $)", fontsize=12, fontweight="bold")
    ax.set_title(f"ZHVI vs. {var.replace('_', ' ')}\nCorrelation: r = {corr:.3f}", 
                 fontsize=13, fontweight="bold", pad=15)
    ax.legend(fontsize=10, framealpha=0.95, loc="upper left", edgecolor="black")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.tick_params(labelsize=10)
    
    # Format axis labels with commas for large numbers
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:,.0f}"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))

fig.suptitle("Control Variable Relationships: Home Values vs. Key Housing Market Indicators (Strong Correlates)", 
             fontsize=15, fontweight="bold", y=1.00)
fig.tight_layout()
save_fig(fig, "control_variables_scatter_plots", "plot7_control_scatter_regplots")
plt.close()

print("\n✓ All missing plots generated successfully!")
