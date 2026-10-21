# dqcheck

A small Python library and command-line tool for catching common data quality
problems in tabular data before they reach anyone downstream: missing values,
duplicate rows, type mismatches, and statistical outliers.

## Why

Reporting pipelines break quietly. A column that's supposed to be numeric
picks up a stray text value, a join produces duplicate rows, or a sensor
starts reporting impossible numbers, and nobody notices until a stakeholder
asks why a dashboard looks wrong. `dqcheck` runs a handful of focused checks
against a dataset and reports exactly what it found and where, so those
problems get caught before the data gets used.

## Install

```bash
git clone https://github.com/<your-username>/dqcheck.git
cd dqcheck
pip install -e ".[dev]"
```

## Usage

### Command line

```bash
dqcheck path/to/data.csv
```

```
Rows: 1000   Columns: 6

Missing values: 1 column(s) affected
  - email: 12 missing (1.2%)

Duplicate rows: 3

Outliers (IQR method): 1 column(s) affected
  - order_total: 4 outlier(s) outside [-18.5, 212.5]
```

Add `--json` to get the same report as machine-readable JSON:

```bash
dqcheck path/to/data.csv --json
```

### As a library

```python
import pandas as pd
from dqcheck import run_all_checks

df = pd.read_csv("data.csv")
report = run_all_checks(df, expected_types={"order_total": "numeric"})
```

Each check is also importable on its own: `missing_value_report`,
`duplicate_row_report`, `type_consistency_report`, `outlier_report`.

## Running the tests

```bash
pytest
```

## License

MIT
