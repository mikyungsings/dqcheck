"""Command-line entry point: run `dqcheck path/to/file.csv`."""

from __future__ import annotations

import argparse
import json
import sys

import pandas as pd

from .checks import run_all_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dqcheck",
        description="Check a CSV file for missing values, duplicate rows, type mismatches, and outliers.",
    )
    parser.add_argument("csv_path", help="Path to the CSV file to check")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON instead of a human-readable summary",
    )
    return parser


def print_summary(report: dict) -> None:
    print(f"Rows: {report['row_count']}   Columns: {report['column_count']}")

    missing = report["missing_values"]
    print(f"\nMissing values: {len(missing)} column(s) affected")
    for column, info in missing.items():
        print(f"  - {column}: {info['missing_count']} missing ({info['missing_pct']}%)")

    duplicates = report["duplicate_rows"]
    print(f"\nDuplicate rows: {duplicates['duplicate_row_count']}")

    type_issues = report["type_consistency"]
    if type_issues:
        print(f"\nType mismatches: {len(type_issues)} column(s) affected")
        for column, info in type_issues.items():
            print(f"  - {column}: {info['mismatched_count']} values not {info['expected_type']}")

    outliers = report["outliers"]
    if outliers:
        print(f"\nOutliers (IQR method): {len(outliers)} column(s) affected")
        for column, info in outliers.items():
            print(f"  - {column}: {info['outlier_count']} outlier(s) outside [{info['lower_bound']}, {info['upper_bound']}]")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        df = pd.read_csv(args.csv_path)
    except FileNotFoundError:
        print(f"File not found: {args.csv_path}", file=sys.stderr)
        return 1

    report = run_all_checks(df)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_summary(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
