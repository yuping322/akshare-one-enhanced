# CI Quick Reference Card

## Test Commands

### Run Tests Locally

```bash
# Offline tests (default - fast, no network)
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_stock.py -v

# Run specific test
uv run pytest tests/test_stock.py::test_get_stock_data -v

# Run with coverage
uv run pytest tests/ --cov=akshare_one --cov-report=html

# Integration tests (requires network)
uv run pytest tests/ -m integration --run-integration

# Contract tests
uv run pytest tests/test_api_contract.py -m contract

# Slow tests
uv run pytest tests/ -m slow --run-slow

# Run all tests including integration
uv run pytest tests/ --run-integration --run-slow
```

### Run Linting

```bash
# Check linting
uv run ruff check .

# Check formatting
uv run ruff format --check .

# Auto-fix formatting
uv run ruff format .
```

## Test Markers

| Marker | Purpose | When to Use |
|--------|---------|-------------|
| `@pytest.mark.integration` | Requires network | External API calls |
| `@pytest.mark.contract` | Golden sample tests | API schema validation |
| `@pytest.mark.slow` | Long-running tests | Performance tests |

Example:
```python
import pytest

@pytest.mark.integration
def test_external_api():
    """Test that calls external API."""
    pass

@pytest.mark.contract
def test_api_schema():
    """Test API response schema."""
    pass

@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset."""
    pass
```

## CI Workflow Triggers

| Trigger | Runs Offline Tests | Runs Integration Tests | Runs Contract Tests |
|---------|-------------------|----------------------|-------------------|
| Push to main/master | ✅ | ❌ | ✅ |
| Pull Request | ✅ | ❌* | ✅ |
| Scheduled (Daily) | ❌ | ✅ | ❌ |
| Manual Dispatch | ✅ | Optional** | Optional** |

*Integration tests run on PRs with `run-integration` label
**Can be toggled in workflow dispatch UI

## Platform Matrix

| Platform | Python Versions | Status |
|----------|----------------|--------|
| ubuntu-latest | 3.10, 3.11, 3.12 | ✅ Full support |
| macos-latest | 3.10, 3.11, 3.12 | ✅ Full support |
| windows-latest | 3.11, 3.12 | ⚠️ Python 3.10 excluded |

## Coverage Thresholds

| Metric | Current Target | Future Goal |
|--------|---------------|-------------|
| Overall | 30% | 50%+ |
| Core modules* | - | 75% |
| Important modules** | - | 60% |
| Extension modules | - | 50% |

*Core: `client.py`, `modules/base.py`, `modules/factory_base.py`
**Important: etf, bond, futures, index, financial, historical, realtime

## Common Issues & Solutions

### Tests fail in CI but pass locally

```bash
# 1. Match CI Python version
python --version  # Check version
pyenv local 3.11  # Set version if using pyenv

# 2. Reinstall dependencies
uv sync --dev

# 3. Clear cache
rm -rf .pytest_cache .coverage htmlcov/
uv run pytest tests/ -v
```

### Coverage too low

```bash
# Generate coverage report
uv run pytest tests/ --cov=akshare_one --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Find uncovered lines
uv run coverage report -m
```

### Integration tests failing

```bash
# Run locally with network
uv run pytest tests/ -m integration --run-integration -v

# Check if API is accessible
curl -I https://api.example.com

# Run with verbose output
uv run pytest tests/ -m integration --run-integration -v -s
```

### Import errors

```bash
# Check module structure
uv run python -c "from akshare_one import get_hist_data; print('OK')"

# Reinstall package
uv pip install -e .

# Check Python path
uv run python -c "import sys; print('\n'.join(sys.path))"
```

## Quick Debug Steps

1. **Check failing job** in Actions UI
2. **Copy error message** from logs
3. **Reproduce locally:**
   ```bash
   uv sync --dev
   uv run pytest tests/test_file.py::test_name -v
   ```
4. **Fix issue** and push new commit
5. **Verify** CI passes

## Useful CI URLs

- **Actions**: `https://github.com/OWNER/REPO/actions`
- **Coverage**: `https://codecov.io/gh/OWNER/REPO`
- **Workflow file**: `.github/workflows/test.yml`

## Best Practices

### 1. Write Fast Offline Tests

```python
# Good: Fast, no network
def test_data_processing():
    """Test with mock data."""
    mock_data = pd.DataFrame({"close": [1, 2, 3]})
    result = process_data(mock_data)
    assert not result.empty

# Bad: Slow, network-dependent
def test_real_api():
    """Test with real API."""
    data = get_real_data()  # Fails offline
    assert not data.empty
```

### 2. Use Fixtures for Reusable Data

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=10),
        "close": [100 + i for i in range(10)]
    })

def test_with_fixture(sample_data):
    """Use fixture in test."""
    assert len(sample_data) == 10
```

### 3. Skip Platform-Specific Tests

```python
import platform
import pytest

@pytest.mark.skipif(platform.system() == "Windows", reason="Unix-only")
def test_unix_feature():
    pass

@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-only")
def test_windows_feature():
    pass
```

## Workflow Structure

```
┌─────────────────┐
│   Push/PR       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Lint Check    │──FAIL──▶ Stop
└────────┬────────┘
         │ PASS
         ▼
┌─────────────────┐
│ Offline Tests   │──FAIL──▶ Stop
│ (Multi-Platform)│
└────────┬────────┘
         │ PASS
         ▼
┌─────────────────┐
│ Coverage Report │
│ Codecov Upload  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build Package  │──FAIL──▶ Stop
└────────┬────────┘
         │ PASS
         ▼
┌─────────────────┐
│ Ready to Merge  │
└─────────────────┘
```

Parallel jobs:
- Integration Tests (scheduled/manual)
- Contract Tests (every push/PR)

## Manual Workflow Dispatch

1. Go to Actions tab
2. Select "Multi-Platform Tests"
3. Click "Run workflow"
4. Configure:
   - ☑️ Run integration tests
   - ☑️ Run contract tests
5. Click "Run workflow"

## Support

- **CI Guide**: `docs/CI_GUIDE.md`
- **Issues**: GitHub Issues
- **Actions**: Check workflow logs