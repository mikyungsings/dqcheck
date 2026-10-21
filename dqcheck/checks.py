"""Core data quality check functions.

Each function takes a pandas DataFrame and returns a plain Python
dict describing what it found, so the results are easy to print,
log, or serialize to JSON.
"""

from __future__ import annotations

import pandas as pd


def missing_value_report(df: pd.DataFrame) -> dict:
    """Count and percentage of missing values per column."""
    counts = df.isna().sum()
    total_rows = len(df)
    report = {}
    for column, count in counts.items():
        if count > 0:
            report[column] = {
                "missing_count": int(count),
                "missing_pct": round(100 * count / total_rows, 2) if total_rows else 0.0,
            }
    return report


def duplicate_row_report(df: pd.DataFrame) -> dict:
    """Find fully duplicated rows."""
    duplicated_mask = df.duplicated(keep="first")
    duplicate_count = int(duplicated_mask.sum())
    return {
        "duplicate_row_count": duplicate_count,
        "duplicate_row_indices": df.index[duplicated_mask].tolist(),
    }


def type_consistency_report(df: pd.DataFrame, expected_types: dict | None = None) -> dict:
    """Flag columns whose values don't match an expected dtype.

    expected_types maps column name -> one of "numeric", "string", "datetime".
    If expected_types is not given, this only reports the inferred dtype
    for each column so a caller can decide what "expected" means for them.
    """
    report = {}
    for column in df.columns:
        inferred = str(df[column].dtype)
        entry = {"inferred_dtype": inferred}

        if expected_types and column in expected_types:
            expected = expected_types[column]
            if expected == "numeric":
                bad_mask = pd.to_numeric(df[column], errors="coerce").isna() & df[column].notna()
            elif expected == "datetime":
                bad_mask = pd.to_datetime(df[column], errors="coerce").isna() & df[column].notna()
            else:
                bad_mask = pd.Series([False] * len(df), index=df.index)

            bad_count = int(bad_mask.sum())
            if bad_count > 0:
                entry["expected_type"] = expected
                entry["mismatched_count"] = bad_count
                entry["mismatched_indices"] = df.index[bad_mask].tolist()
                report[column] = entry

    return report


def outlier_report(df: pd.DataFrame, columns: list[str] | None = None) -> dict:
    """Flag numeric outliers using the IQR method (values outside 1.5*IQR)."""
    numeric_columns = columns or df.select_dtypes(include="number").columns.tolist()
    report = {}

    for column in numeric_columns:
        series = df[column].dropna()
        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
        outlier_count = int(outlier_mask.sum())

        if outlier_count > 0:
            report[column] = {
                "outlier_count": outlier_count,
                "lower_bound": round(float(lower_bound), 4),
                "upper_bound": round(float(upper_bound), 4),
                "outlier_indices": df.index[outlier_mask].tolist(),
            }

    return report


def constant_column_report(df: pd.DataFrame) -> dict:
    """Flag columns where every non-null value is identical.

    A column that never changes is often a sign something upstream broke
    (a sensor stuck on one reading, a default value nobody overwrote).
    """
    report = {}
    for column in df.columns:
        non_null = df[column].dropna()
        if len(non_null) > 0 and non_null.nunique() == 1:
            report[column] = {"constant_value": non_null.iloc[0]}
    return report


def run_all_checks(df: pd.DataFrame, expected_types: dict | None = None) -> dict:
    """Run every check and return one combined report."""
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_values": missing_value_report(df),
        "duplicate_rows": duplicate_row_report(df),
        "type_consistency": type_consistency_report(df, expected_types=expected_types),
        "outliers": outlier_report(df),
        "constant_columns": constant_column_report(df),
    }