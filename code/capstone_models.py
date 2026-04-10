"""
QM 2023 Capstone Project: Milestone 3 Econometric Models

This script estimates:
1) Model A: Panel fixed-effects regression (entity + time effects)
2) Model B Option 2: ARIMA forecast on aggregate outcome
3) Model B Option 3: OLS vs Random Forest prediction comparison

It also runs required diagnostics, robustness checks, and exports tables/figures.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from matplotlib import pyplot as plt
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.regression.linear_model import OLS
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "final" / "housing_master_dataset_long.csv"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
REPORTS_DIR = PROJECT_ROOT / "results" / "reports"

for d in (FIGURES_DIR, TABLES_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def load_panel_wide() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run: python code/capstone_data_pipeline.py"
        )

    df_long = pd.read_csv(DATA_PATH, parse_dates=["Date"])
    df = (
        df_long.pivot_table(
            index=["Metro", "Date"],
            columns="metric",
            values="value",
            aggfunc="first",
        )
        .reset_index()
        .sort_values(["Metro", "Date"])
    )

    required = [
        "ZHVI",
        "ZORI",
        "Inventory",
        "Income_Needed",
        "hurricane_total_cost_billion",
        "hurricane_count",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in wide panel: {missing}")

    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.sort_values(["Metro", "Date"]).reset_index(drop=True)

    # Outcome and controls in growth form for stationarity and comparability.
    out["zhvi_log"] = np.log(out["ZHVI"])
    out["zori_log"] = np.log(out["ZORI"])
    out["income_log"] = np.log(out["Income_Needed"])

    out["zhvi_growth"] = out.groupby("Metro")["zhvi_log"].diff()
    out["zori_growth"] = out.groupby("Metro")["zori_log"].diff()
    out["inventory_growth"] = out.groupby("Metro")["Inventory"].pct_change()

    # Metro-specific affordability interaction creates cross-sectional variation
    # while preserving the hurricane driver in the model.
    out["hurricane_cost_l1"] = out.groupby("Metro")["hurricane_total_cost_billion"].shift(1)
    out["hurricane_count_l1"] = out.groupby("Metro")["hurricane_count"].shift(1)
    out["storm_x_income_l1"] = out["hurricane_cost_l1"] * out["income_log"]

    out["month"] = out["Date"].dt.month
    out["year"] = out["Date"].dt.year

    # Additional lags for robustness checks.
    for lag in (2, 3):
        out[f"hurricane_cost_l{lag}"] = out.groupby("Metro")["hurricane_total_cost_billion"].shift(lag)
        out[f"storm_x_income_l{lag}"] = out[f"hurricane_cost_l{lag}"] * out["income_log"]

    return out


def fit_fe_model(df: pd.DataFrame, driver_col: str, clustered: bool = True) -> PanelOLS:
    model_df = df[[
        "Metro",
        "Date",
        "zhvi_growth",
        driver_col,
        "income_log",
        "zori_growth",
        "inventory_growth",
    ]].dropna()

    panel_df = model_df.set_index(["Metro", "Date"])
    y = panel_df["zhvi_growth"]
    X = panel_df[[driver_col, "income_log", "zori_growth", "inventory_growth"]]

    model = PanelOLS(y, X, entity_effects=True, time_effects=True, drop_absorbed=True)
    if clustered:
        result = model.fit(cov_type="clustered", cluster_entity=True)
    else:
        result = model.fit(cov_type="unadjusted")
    return result


def run_diagnostics(
    fe_result,
    fe_input_df: pd.DataFrame,
    driver_col: str,
) -> Dict[str, float]:
    panel_df = fe_input_df[[
        "Metro",
        "Date",
        "zhvi_growth",
        driver_col,
        "income_log",
        "zori_growth",
        "inventory_growth",
    ]].dropna().set_index(["Metro", "Date"])

    # Breusch-Pagan test using pooled OLS proxy as recommended for panel settings.
    y = panel_df["zhvi_growth"].values
    X = panel_df[[driver_col, "income_log", "zori_growth", "inventory_growth"]]
    X_const = add_constant(X)
    ols_proxy = OLS(y, X_const).fit()
    bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(ols_proxy.resid, X_const)

    # VIF diagnostics for regressors.
    vif_df = pd.DataFrame({"Variable": X.columns})
    vif_df["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    vif_df.to_csv(TABLES_DIR / "M3_vif_table.csv", index=False)

    # Residual diagnostic plots from FE model.
    residuals = np.asarray(fe_result.resids)
    fitted = np.asarray(fe_result.fitted_values)

    plt.figure(figsize=(10, 6))
    plt.scatter(fitted, residuals, alpha=0.3)
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Fitted Values")
    plt.ylabel("Residuals")
    plt.title("Residuals vs Fitted Values (Fixed Effects Model)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_residuals_vs_fitted.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    stats.probplot(residuals, dist="norm", plot=plt)
    plt.title("Q-Q Plot: Residual Normality Check")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_qq_plot.png", dpi=300)
    plt.close()

    diag = {
        "breusch_pagan_lm": float(bp_lm),
        "breusch_pagan_lm_pvalue": float(bp_lm_p),
        "breusch_pagan_f": float(bp_f),
        "breusch_pagan_f_pvalue": float(bp_f_p),
    }
    pd.DataFrame([diag]).to_csv(TABLES_DIR / "M3_diagnostics_summary.csv", index=False)
    return diag


def compile_regression_table(models: Dict[str, object], key_vars: List[str]) -> pd.DataFrame:
    rows = []
    for var in key_vars:
        row = {"variable": var}
        for model_name, result in models.items():
            coef = result.params.get(var, np.nan)
            se = result.std_errors.get(var, np.nan)
            pval = result.pvalues.get(var, np.nan)
            row[f"{model_name}_coef"] = coef
            row[f"{model_name}_se"] = se
            row[f"{model_name}_pvalue"] = pval
        rows.append(row)

    footer = {
        "variable": "N",
    }
    for model_name, result in models.items():
        footer[f"{model_name}_coef"] = float(result.nobs)
        footer[f"{model_name}_se"] = np.nan
        footer[f"{model_name}_pvalue"] = np.nan

    r2_row = {"variable": "R2_within"}
    for model_name, result in models.items():
        r2_row[f"{model_name}_coef"] = float(getattr(result, "rsquared_within", np.nan))
        r2_row[f"{model_name}_se"] = np.nan
        r2_row[f"{model_name}_pvalue"] = np.nan

    out = pd.DataFrame(rows + [footer, r2_row])
    out.to_csv(TABLES_DIR / "M3_regression_table.csv", index=False)
    return out


def run_robustness_checks(df: pd.DataFrame) -> pd.DataFrame:
    checks = []

    # 1) Clustered vs non-clustered SE already compared in model table.
    base_unadj = fit_fe_model(df, "storm_x_income_l1", clustered=False)
    base_clust = fit_fe_model(df, "storm_x_income_l1", clustered=True)
    checks.append({
        "check": "clustered_vs_unadjusted_se",
        "driver": "storm_x_income_l1",
        "coef_unadjusted": float(base_unadj.params.get("storm_x_income_l1", np.nan)),
        "se_unadjusted": float(base_unadj.std_errors.get("storm_x_income_l1", np.nan)),
        "coef_clustered": float(base_clust.params.get("storm_x_income_l1", np.nan)),
        "se_clustered": float(base_clust.std_errors.get("storm_x_income_l1", np.nan)),
    })

    # 2) Alternative lag structures.
    for lag in (1, 2, 3):
        var = f"storm_x_income_l{lag}"
        lag_result = fit_fe_model(df, var, clustered=True)
        checks.append({
            "check": "alternative_lag",
            "driver": var,
            "coef_clustered": float(lag_result.params.get(var, np.nan)),
            "se_clustered": float(lag_result.std_errors.get(var, np.nan)),
            "pvalue_clustered": float(lag_result.pvalues.get(var, np.nan)),
            "nobs": float(lag_result.nobs),
        })

    # 3) Exclude outlier period (COVID shock window).
    no_covid = df.loc[~df["Date"].between("2020-03-01", "2020-05-31")].copy()
    no_covid_result = fit_fe_model(no_covid, "storm_x_income_l1", clustered=True)
    checks.append({
        "check": "exclude_outlier_period_2020_03_to_2020_05",
        "driver": "storm_x_income_l1",
        "coef_clustered": float(no_covid_result.params.get("storm_x_income_l1", np.nan)),
        "se_clustered": float(no_covid_result.std_errors.get("storm_x_income_l1", np.nan)),
        "pvalue_clustered": float(no_covid_result.pvalues.get("storm_x_income_l1", np.nan)),
        "nobs": float(no_covid_result.nobs),
    })

    # 4) Group subsamples by affordability (high vs low income-needed metros).
    metro_afford = df.groupby("Metro")["Income_Needed"].median()
    cutoff = metro_afford.median()
    high_group = metro_afford.index[metro_afford >= cutoff]
    low_group = metro_afford.index[metro_afford < cutoff]

    high_df = df[df["Metro"].isin(high_group)].copy()
    low_df = df[df["Metro"].isin(low_group)].copy()

    high_res = fit_fe_model(high_df, "storm_x_income_l1", clustered=True)
    low_res = fit_fe_model(low_df, "storm_x_income_l1", clustered=True)

    checks.append({
        "check": "subsample_high_income_needed",
        "driver": "storm_x_income_l1",
        "coef_clustered": float(high_res.params.get("storm_x_income_l1", np.nan)),
        "se_clustered": float(high_res.std_errors.get("storm_x_income_l1", np.nan)),
        "pvalue_clustered": float(high_res.pvalues.get("storm_x_income_l1", np.nan)),
        "nobs": float(high_res.nobs),
    })
    checks.append({
        "check": "subsample_low_income_needed",
        "driver": "storm_x_income_l1",
        "coef_clustered": float(low_res.params.get("storm_x_income_l1", np.nan)),
        "se_clustered": float(low_res.std_errors.get("storm_x_income_l1", np.nan)),
        "pvalue_clustered": float(low_res.pvalues.get("storm_x_income_l1", np.nan)),
        "nobs": float(low_res.nobs),
    })

    robustness_df = pd.DataFrame(checks)
    robustness_df.to_csv(TABLES_DIR / "M3_robustness_checks.csv", index=False)
    return robustness_df


def select_arima_order(y_train: pd.Series) -> Tuple[int, int, int]:
    try:
        from pmdarima import auto_arima

        model = auto_arima(
            y_train,
            seasonal=False,
            stepwise=True,
            suppress_warnings=True,
            error_action="ignore",
            max_p=4,
            max_q=4,
            max_d=2,
        )
        return model.order
    except Exception:
        best_order = (1, 1, 0)
        best_aic = np.inf
        for p in range(0, 4):
            for d in range(0, 3):
                for q in range(0, 4):
                    try:
                        candidate = ARIMA(y_train, order=(p, d, q)).fit()
                        if candidate.aic < best_aic:
                            best_aic = candidate.aic
                            best_order = (p, d, q)
                    except Exception:
                        continue
        return best_order


def run_arima_forecast(df: pd.DataFrame) -> Dict[str, float]:
    ts = (
        df.groupby("Date", as_index=True)["zhvi_growth"]
        .mean()
        .dropna()
        .asfreq("ME")
    )

    adf_stat, adf_p, _, _, _, _ = adfuller(ts.values)

    holdout = 12
    y_train = ts.iloc[:-holdout]
    y_test = ts.iloc[-holdout:]

    order = select_arima_order(y_train)
    arima = ARIMA(y_train, order=order).fit()

    pred_res = arima.get_forecast(steps=holdout)
    pred_mean = pred_res.predicted_mean
    pred_ci = pred_res.conf_int(alpha=0.05)

    naive = pd.Series(y_train.iloc[-1], index=y_test.index)

    rmse_arima = float(np.sqrt(mean_squared_error(y_test, pred_mean)))
    rmse_naive = float(np.sqrt(mean_squared_error(y_test, naive)))

    forecast_df = pd.DataFrame(
        {
            "date": y_test.index,
            "actual": y_test.values,
            "arima_forecast": pred_mean.values,
            "arima_ci_lower": pred_ci.iloc[:, 0].values,
            "arima_ci_upper": pred_ci.iloc[:, 1].values,
            "naive_forecast": naive.values,
        }
    )
    forecast_df.to_csv(TABLES_DIR / "M3_arima_forecast_vs_naive.csv", index=False)

    plt.figure(figsize=(11, 6))
    plt.plot(y_train.index, y_train.values, label="Train", color="black")
    plt.plot(y_test.index, y_test.values, label="Actual", color="blue")
    plt.plot(y_test.index, pred_mean.values, label="ARIMA Forecast", color="darkorange")
    plt.fill_between(
        y_test.index,
        pred_ci.iloc[:, 0].values,
        pred_ci.iloc[:, 1].values,
        color="orange",
        alpha=0.2,
        label="95% CI",
    )
    plt.plot(y_test.index, naive.values, label="Naive (No Change)", color="green", linestyle="--")
    plt.title("M3 ARIMA Forecast vs Naive Baseline (ZHVI Growth)")
    plt.xlabel("Date")
    plt.ylabel("Aggregate Monthly log(ZHVI) Growth")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "M3_arima_forecast.png", dpi=300)
    plt.close()

    summary = {
        "adf_stat": float(adf_stat),
        "adf_pvalue": float(adf_p),
        "arima_p": int(order[0]),
        "arima_d": int(order[1]),
        "arima_q": int(order[2]),
        "rmse_arima": rmse_arima,
        "rmse_naive": rmse_naive,
    }
    pd.DataFrame([summary]).to_csv(TABLES_DIR / "M3_arima_summary.csv", index=False)
    return summary


def run_ml_comparison(df: pd.DataFrame) -> pd.DataFrame:
    model_df = df[[
        "Metro",
        "Date",
        "zhvi_growth",
        "storm_x_income_l1",
        "hurricane_count_l1",
        "zori_growth",
        "inventory_growth",
        "income_log",
    ]].dropna().copy()

    model_df = model_df.sort_values("Date")

    feature_cols = [
        "storm_x_income_l1",
        "hurricane_count_l1",
        "zori_growth",
        "inventory_growth",
        "income_log",
    ]

    split_date = model_df["Date"].quantile(0.8)
    train = model_df[model_df["Date"] <= split_date]
    test = model_df[model_df["Date"] > split_date]

    X_train = train[feature_cols]
    y_train = train["zhvi_growth"]
    X_test = test[feature_cols]
    y_test = test["zhvi_growth"]

    ols = OLS(y_train, add_constant(X_train)).fit()
    ols_pred = ols.predict(add_constant(X_test, has_constant="add"))

    rf = RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        min_samples_leaf=5,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)

    out = pd.DataFrame(
        [
            {
                "model": "OLS",
                "r2_test": float(r2_score(y_test, ols_pred)),
                "rmse_test": float(np.sqrt(mean_squared_error(y_test, ols_pred))),
            },
            {
                "model": "RandomForest",
                "r2_test": float(r2_score(y_test, rf_pred)),
                "rmse_test": float(np.sqrt(mean_squared_error(y_test, rf_pred))),
            },
        ]
    )
    out.to_csv(TABLES_DIR / "M3_ml_comparison.csv", index=False)

    feature_importance = pd.DataFrame(
        {
            "feature": feature_cols,
            "importance": rf.feature_importances_,
        }
    ).sort_values("importance", ascending=False)
    feature_importance.to_csv(TABLES_DIR / "M3_random_forest_feature_importance.csv", index=False)

    return out


def main() -> None:
    print("=" * 72)
    print("M3 Econometric Models")
    print("=" * 72)

    wide = load_panel_wide()
    model_df = add_features(wide)

    print("Fitting fixed-effects models...")
    fe_baseline = fit_fe_model(model_df, "storm_x_income_l1", clustered=False)
    fe_clustered = fit_fe_model(model_df, "storm_x_income_l1", clustered=True)

    no_covid_df = model_df.loc[~model_df["Date"].between("2020-03-01", "2020-05-31")].copy()
    fe_no_covid = fit_fe_model(no_covid_df, "storm_x_income_l1", clustered=True)

    print("Running diagnostics...")
    diagnostics = run_diagnostics(fe_clustered, model_df, "storm_x_income_l1")
    print(f"Diagnostics summary: {diagnostics}")

    print("Running robustness checks...")
    robustness_df = run_robustness_checks(model_df)
    print(robustness_df.to_string(index=False))

    print("Saving publication-style regression table...")
    models = {
        "Model1_FE": fe_baseline,
        "Model2_FE_Clustered": fe_clustered,
        "Model3_FE_NoCovid": fe_no_covid,
    }
    key_vars = ["storm_x_income_l1", "income_log", "zori_growth", "inventory_growth"]
    reg_table = compile_regression_table(models, key_vars)
    print(reg_table.to_string(index=False))

    print("Running ARIMA forecast option...")
    arima_summary = run_arima_forecast(model_df)
    print(arima_summary)

    print("Running OLS vs RandomForest comparison option...")
    ml_summary = run_ml_comparison(model_df)
    print(ml_summary.to_string(index=False))

    print("\nAll M3 outputs saved:")
    print(f"- Tables: {TABLES_DIR}")
    print(f"- Figures: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
