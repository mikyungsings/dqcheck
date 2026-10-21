"""dqcheck: a small library for checking common data quality issues in tabular data."""

from .checks import (
    missing_value_report,
    duplicate_row_report,
    type_consistency_report,
    outlier_report,
    constant_column_report,
    run_all_checks,
)

__version__ = "0.1.0"

__all__ = [
    "missing_value_report",
    "duplicate_row_report",
    "type_consistency_report",
    "outlier_report",
    "constant_column_report",
    "run_all_checks",
]