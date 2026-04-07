# Regression Test Snapshots

This directory contains snapshot files for regression testing.

## What are Snapshots?

Snapshots capture the expected structure of API responses:
- Column names and count
- Row count
- Data types per column
- Sample values (first 3 rows)

## Directory Structure

Snapshots are organized by test class and test method:

```
snapshots/
├── TestETFRegression/
│   ├── test_etf_list_schema/
│   │   └── etf_list_schema.json
│   └── ...
├── TestBondRegression/
│   └── ...
└── ...
```

## How to Update Snapshots

Snapshots should only be updated when API changes are **intentional and verified**.

```bash
# Update all snapshots
pytest tests/test_regression.py --snapshot-update -v

# Update specific snapshot
pytest tests/test_regression.py::TestETFRegression::test_etf_list_schema --snapshot-update -v
```

## Important Notes

- ⚠️ **Never manually edit snapshot files**
- ⚠️ **Always review snapshot changes before committing**
- ⚠️ **Document the reason for snapshot updates in commit messages**
- ⚠️ **Run tests without --snapshot-update first to see differences**

## Example Snapshot File

```json
{
  "empty": false,
  "columns": ["symbol", "name", "price", "volume"],
  "column_count": 4,
  "row_count": 1234,
  "types": {
    "symbol": "str",
    "name": "str",
    "price": "float",
    "volume": "float"
  },
  "sample_values": {
    "symbol": ["159915", "510300", "510500"],
    "price": ["1.234", "5.678", "9.012"]
  },
  "sample_count": 3
}
```

## For More Information

See full documentation at: `docs/regression_testing.md`

Quick start guide: `docs/regression_quickstart.md`