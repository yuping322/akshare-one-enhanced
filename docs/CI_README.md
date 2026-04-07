# CI Documentation Index

This directory contains comprehensive documentation for the CI/CD pipeline.

## Quick Links

### For Developers

- **[CI_QUICK_REFERENCE.md](CI_QUICK_REFERENCE.md)** - One-page reference card
  - Common test commands
  - Test markers quick reference
  - Debug steps
  - Workflow triggers

### For Detailed Understanding

- **[CI_GUIDE.md](CI_GUIDE.md)** - Comprehensive CI/CD guide
  - Workflow structure
  - Test categories
  - Viewing results
  - Debugging failures
  - Best practices
  - Troubleshooting

### For Badge Configuration

- **[BADGES.md](BADGES.md)** - Badge setup guide
  - Current badges explanation
  - Codecov setup
  - Badge troubleshooting
  - Custom badges

### For Validation

- **[CI_VALIDATION_REPORT.md](CI_VALIDATION_REPORT.md)** - Validation results
  - Task completion status
  - Verification results
  - Acceptance criteria check

## CI Files Overview

### Workflow Configuration

- `.github/workflows/test.yml` - Main multi-platform test workflow
- `.github/workflows/ci.yml` - Legacy CI workflow
- `.github/workflows/standardization.yml` - Field standardization checks

### Supporting Files

- `requirements-dev.txt` - Development dependencies
- `scripts/validate_ci_config.py` - CI configuration validator
- `tests/conftest.py` - Test markers and fixtures

## Quick Start

1. Run tests locally: `uv run pytest tests/ -v`
2. Run linting: `uv run ruff check .`
3. Run coverage: `uv run pytest tests/ --cov=akshare_one --cov-report=html`
4. Validate CI config: `python scripts/validate_ci_config.py`

## Getting Help

1. Check CI_QUICK_REFERENCE.md for common commands
2. Check CI_GUIDE.md for detailed troubleshooting
3. Search existing GitHub Issues
4. Create new issue with CI workflow link and error details