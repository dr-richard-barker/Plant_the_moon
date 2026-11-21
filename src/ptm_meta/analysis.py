"""Reproducible ML & statistical meta-analysis helpers (leak-free grouped validation)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def wilson_ci(successes: int, total: int, z: float = 1.96) -> tuple[float, float, float]:
    """Compute proportion and 95% Wilson score interval."""
    if total == 0:
        return 0.0, 0.0, 0.0
    p = successes / total
    denom = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denom
    half = (z / denom) * np.sqrt((p * (1.0 - p) / total) + (z * z / (4.0 * total * total)))
    return float(p), float(max(0.0, center - half)), float(min(1.0, center + half))


def bootstrap_metric_ci(
    y_true: np.ndarray,
    y_score: np.ndarray,
    metric_fn: Any,
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Compute point estimate and 95% percentile bootstrap CI."""
    rng = np.random.default_rng(seed)
    point = float(metric_fn(y_true, y_score))
    vals: list[float] = []
    n = len(y_true)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        if len(np.unique(yt)) < 2:
            continue
        vals.append(float(metric_fn(yt, y_score[idx])))
    if not vals:
        return point, point, point
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return point, float(lo), float(hi)


def build_modeling_dataset(arms_df: pd.DataFrame, reports_df: pd.DataFrame) -> pd.DataFrame:
    """Build treatment-arm dataset for predicting positive growth response vs regolith control."""
    trt = arms_df[(~arms_df["is_control"]) & (arms_df["outcome_vs_regolith_control"].isin(["improved", "neutral", "reduced"]))].copy()
    if trt.empty:
        return trt

    rep_cols = [
        "report_id",
        "season_order",
        "year",
        "track",
        "division_norm",
        "experimental_duration_days",
        "has_earth_soil_control",
        "has_unamended_regolith_control",
        "has_statistical_test",
        "table_count",
        "page_count",
    ]
    avail_rep_cols = [c for c in rep_cols if c in reports_df.columns]
    merged = trt.merge(
        reports_df[avail_rep_cols].drop_duplicates("report_id"),
        on="report_id",
        how="left",
        suffixes=("", "_rep"),
    )
    for col in ("experimental_duration_days", "has_earth_soil_control", "has_unamended_regolith_control", "has_statistical_test"):
        rep_c = f"{col}_rep"
        if rep_c in merged.columns:
            merged[col] = merged[col].fillna(merged[rep_c])
            merged = merged.drop(columns=[rep_c])

    merged["target_improved"] = (merged["outcome_vs_regolith_control"] == "improved").astype(int)
    merged["missing_duration"] = merged["experimental_duration_days"].isna().astype(int)
    merged["missing_regolith_pct"] = merged["regolith_pct"].isna().astype(int)
    return merged


def _make_preprocessor(num_cols: list[str], cat_cols: list[str], dense: bool = False) -> ColumnTransformer:
    num_pipe = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    cat_pipe = Pipeline(
        [
            ("imp", SimpleImputer(strategy="constant", fill_value="missing")),
            ("ohe", OneHotEncoder(handle_unknown="ignore", max_categories=14, sparse_output=not dense)),
        ]
    )
    return ColumnTransformer([("num", num_pipe, num_cols), ("cat", cat_pipe, cat_cols)])


def evaluate_grouped_models(df: pd.DataFrame, out_json: Path | None = None, seed: int = 42) -> dict[str, Any]:
    """Compare naive, linear, RF, and HistGradientBoosting models using report-grouped CV."""
    num_cols = ["year", "experimental_duration_days", "missing_duration", "has_earth_soil_control", "has_unamended_regolith_control", "has_statistical_test"]
    cat_cols = ["celestial_body", "regolith_simulant", "crop_guild", "amendment_category", "track"]
    num_cols = [c for c in num_cols if c in df.columns]
    cat_cols = [c for c in cat_cols if c in df.columns]
    feat_cols = num_cols + cat_cols

    work = df.dropna(subset=["target_improved", "report_id"]).reset_index(drop=True)
    for bcol in ("has_earth_soil_control", "has_unamended_regolith_control", "has_statistical_test"):
        if bcol in work.columns:
            work[bcol] = work[bcol].astype(float)

    X = work[feat_cols]
    y = work["target_improved"].to_numpy(dtype=int)
    groups = work["report_id"].to_numpy()

    # Hold out 20% of reports cleanly before CV for final test audit
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))

    X_train, y_train, g_train = X.iloc[train_idx], y[train_idx], groups[train_idx]
    X_test, y_test = X.iloc[test_idx], y[test_idx]

    models = {
        "Dummy (Majority)": Pipeline([("pre", _make_preprocessor(num_cols, cat_cols)), ("clf", DummyClassifier(strategy="most_frequent"))]),
        "Logistic Regression": Pipeline([("pre", _make_preprocessor(num_cols, cat_cols)), ("clf", LogisticRegression(max_iter=1000, C=0.5, random_state=seed))]),
        "Random Forest": Pipeline([("pre", _make_preprocessor(num_cols, cat_cols)), ("clf", RandomForestClassifier(n_estimators=200, max_depth=6, random_state=seed))]),
        "HistGradientBoosting": Pipeline([("pre", _make_preprocessor(num_cols, cat_cols, dense=True)), ("clf", HistGradientBoostingClassifier(max_depth=4, learning_rate=0.06, max_iter=150, random_state=seed))]),
    }

    cv = StratifiedGroupKFold(n_splits=5)
    results: list[dict[str, Any]] = []
    fitted_best: Pipeline | None = None
    best_auc = -1.0
    best_name = ""

    for name, pipe in models.items():
        oof_prob = np.zeros(len(y_train), dtype=float)
        for tr, va in cv.split(X_train, y_train, groups=g_train):
            pipe.fit(X_train.iloc[tr], y_train[tr])
            oof_prob[va] = pipe.predict_proba(X_train.iloc[va])[:, 1]

        auc, auc_lo, auc_hi = bootstrap_metric_ci(y_train, oof_prob, roc_auc_score, n_boot=500, seed=seed)
        pr, pr_lo, pr_hi = bootstrap_metric_ci(y_train, oof_prob, average_precision_score, n_boot=500, seed=seed)
        f1 = float(f1_score(y_train, (oof_prob >= 0.5).astype(int), zero_division=0))

        # Fit on full train and evaluate on held-out report test set
        pipe.fit(X_train, y_train)
        test_prob = pipe.predict_proba(X_test)[:, 1]
        test_auc = float(roc_auc_score(y_test, test_prob)) if len(np.unique(y_test)) > 1 else None
        test_f1 = float(f1_score(y_test, (test_prob >= 0.5).astype(int), zero_division=0))

        results.append(
            {
                "model": name,
                "cv_roc_auc": round(auc, 3),
                "cv_roc_auc_ci": [round(auc_lo, 3), round(auc_hi, 3)],
                "cv_pr_auc": round(pr, 3),
                "cv_pr_auc_ci": [round(pr_lo, 3), round(pr_hi, 3)],
                "cv_f1": round(f1, 3),
                "test_roc_auc": round(test_auc, 3) if test_auc is not None else None,
                "test_f1": round(test_f1, 3),
            }
        )
        if auc > best_auc and name != "Dummy (Majority)":
            best_auc = auc
            fitted_best = pipe
            best_name = name

    # Slice analysis on held-out test set for best model
    slices: dict[str, dict[str, Any]] = {}
    if fitted_best is not None:
        test_df = work.iloc[test_idx].copy()
        test_df["pred"] = fitted_best.predict(X_test)
        test_df["prob"] = fitted_best.predict_proba(X_test)[:, 1]
        for slice_col in ("celestial_body", "track"):
            if slice_col not in test_df.columns:
                continue
            for val, sub in test_df.groupby(slice_col):
                if len(sub) < 3:
                    continue
                slices[f"{slice_col}={val}"] = {
                    "n_arms": int(len(sub)),
                    "positive_rate": round(float(sub["target_improved"].mean()), 3),
                    "accuracy": round(float((sub["pred"] == sub["target_improved"]).mean()), 3),
                }

    payload = {
        "n_total_arms": int(len(work)),
        "n_unique_reports": int(work["report_id"].nunique()),
        "n_train_arms": int(len(train_idx)),
        "n_test_arms": int(len(test_idx)),
        "positive_rate": round(float(y.mean()), 3),
        "best_model": best_name,
        "models": results,
        "test_slices": slices,
    }
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
