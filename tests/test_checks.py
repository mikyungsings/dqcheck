import pandas as pd

from dqcheck.checks import (
    missing_value_report,
    duplicate_row_report,
    type_consistency_report,
    outlier_report,
    run_all_checks,
)


def test_missing_value_report_finds_missing_cells():
    df = pd.DataFrame({"a": [1, None, 3], "b": [1, 2, 3]})
    report = missing_value_report(df)
    assert "a" in report
    assert report["a"]["missing_count"] == 1
    assert "b" not in report


def test_duplicate_row_report_finds_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [1, 1, 2]})
    report = duplicate_row_report(df)
    assert report["duplicate_row_count"] == 1
    assert report["duplicate_row_indices"] == [1]


def test_duplicate_row_report_handles_no_duplicates():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3]})
    report = duplicate_row_report(df)
    assert report["duplicate_row_count"] == 0


def test_type_consistency_report_flags_non_numeric_values():
    df = pd.DataFrame({"amount": ["10", "20", "oops"]})
    report = type_consistency_report(df, expected_types={"amount": "numeric"})
    assert "amount" in report
    assert report["amount"]["mismatched_count"] == 1


def test_type_consistency_report_without_expected_types_is_informational_only():
    df = pd.DataFrame({"amount": ["10", "20", "oops"]})
    report = type_consistency_report(df)
    assert report == {}


def test_outlier_report_flags_values_outside_iqr_bounds():
    df = pd.DataFrame({"value": [10, 11, 12, 13, 14, 1000]})
    report = outlier_report(df)
    assert "value" in report
    assert report["value"]["outlier_count"] == 1


def test_run_all_checks_returns_combined_report():
    df = pd.DataFrame({"a": [1, None, 3, 3], "b": [1, 2, 3, 3]})
    report = run_all_checks(df)
    assert report["row_count"] == 4
    assert report["column_count"] == 2
    assert "missing_values" in report
    assert "duplicate_rows" in report
    assert "type_consistency" in report
    assert "outliers" in report
