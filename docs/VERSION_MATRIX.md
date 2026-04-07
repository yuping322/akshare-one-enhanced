# Version Compatibility Matrix

This document provides a comprehensive overview of AKShare One's compatibility with different Python versions, AkShare versions, operating systems, and dependencies.

## Python Version Compatibility

### Supported Python Versions

| Python Version | Support Status | Tested | Notes |
|---------------|---------------|--------|-------|
| **3.10** | ✅ Full Support | Yes | Recommended for production |
| **3.11** | ✅ Full Support | Yes | Best performance, recommended |
| **3.12** | ✅ Full Support | Yes | Latest features, fully compatible |
| **3.9** | ⚠️ Not Supported | No | Below minimum requirement |
| **3.13** | 🔜 Experimental | Limited | Future support planned |

### Python Version Requirements

**Minimum requirement**: Python 3.10+

```toml
# pyproject.toml
requires-python = ">=3.10"
```

**Reasons for Python 3.10+ requirement**:

1. **Modern type hints**: Use of `list[str]`, `dict[str, Any]` (no need for `List`, `Dict` from typing)
2. **Match statements**: Potential use of structural pattern matching
3. **Better error messages**: Improved debugging and error handling
4. **Performance improvements**: Faster execution compared to 3.9

### Python Feature Usage

| Feature | Python Version | Usage in Code |
|---------|---------------|---------------|
| Union operators (`X | Y`) | 3.10+ | Type hints: `str | None` |
| Generic type hints | 3.9+ | `list[str]`, `dict[str, Any]` |
| Positional-only parameters | 3.8+ | Limited use |
| Assignment expressions (`:=`) | 3.8+ | Not currently used |
| Dataclasses | 3.7+ | Used in field naming models |
| Async/await | 3.5+ | Not currently used (sync only) |

### Testing Matrix

Our CI/CD pipeline tests against multiple Python versions:

```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, macos-latest, windows-latest]
```

**Test coverage**:
- ✅ Python 3.10 on Ubuntu, macOS, Windows
- ✅ Python 3.11 on Ubuntu, macOS, Windows
- ✅ Python 3.12 on Ubuntu, macOS, Windows

## AkShare Version Compatibility

### Supported AkShare Versions

| AkShare Version | Support Status | Tested | Compatibility Notes |
|-----------------|---------------|--------|---------------------|
| **1.17.80 - 1.18.x** | ✅ Full Support | Yes | Current stable range |
| **1.17.0 - 1.17.79** | ⚠️ Partial Support | Limited | May have field naming issues |
| **< 1.17.0** | ❌ Not Supported | No | API incompatibility |
| **1.19.x (future)** | 🔜 Planned | No | Will be tested when released |

### AkShare Version Requirements

**Minimum requirement**: AkShare >= 1.17.80

```toml
# pyproject.toml
dependencies = [
    "akshare>=1.17.80",
]
```

**Reasons for AkShare 1.17.80+ requirement**:

1. **Stable API**: Function signatures stabilized in 1.17.80
2. **Field naming**: Consistent field naming conventions
3. **Data quality**: Improved data validation and cleaning
4. **Bug fixes**: Critical fixes for upstream issues
5. **Compatibility adapter**: Designed for 1.17.80+ API structure

### AkShare Function Compatibility

AKShare One includes an **AkShare Compatibility Adapter** to handle upstream API drift:

```python
from akshare_one import AkShareAdapter, call_akshare

# Check if function exists
if check_akshare_function("stock_zh_a_hist"):
    # Call with fallback handling
    df = call_akshare("stock_zh_a_hist", symbol="600000")
```

**Adapter features**:

- Function existence checking before calls
- Fallback to alternative functions when primary fails
- Parameter mapping for changed signatures
- Error handling for upstream changes

### Known AkShare API Changes

| Version | Change | Impact | Mitigation |
|---------|---------|--------|------------|
| 1.17.80 | Field naming stabilization | Low | Standardized naming in adapter |
| 1.18.0 | New function additions | None | Adapter handles new functions |
| Future | Potential signature changes | Medium | Compatibility adapter in place |

### AkShare Data Source Coverage

AKShare One wraps **100+ AkShare functions** across categories:

| Category | AkShare Functions | AKShare One Modules |
|----------|------------------|---------------------|
| Historical data | `stock_zh_a_hist`, `stock_zh_a_hist_min_em` | `historical` |
| Realtime data | `stock_zh_a_spot_em`, `stock_individual_info_em` | `realtime`, `info` |
| Financial data | `stock_balance_sheet_by_report`, `stock_profit_sheet_by_report` | `financial` |
| Fund flow | `stock_individual_fund_flow`, `stock_sector_fund_flow` | `fundflow` |
| Northbound | `stock_hsgt_individual_em`, `stock_hsgt_hold_stock_em` | `northbound` |
| Dragon tiger | `stock_lhb_detail_em`, `stock_lhb_statistic_em` | `lhb` |
| Block deal | `stock_block_trade_em`, `stock_block_trade_statistic` | `blockdeal` |
| Macro | `macro_china_lpr`, `macro_china_pmi_yearly` | `macro` |
| Options | `option_sina_sse_list`, `option_current_em` | `options` |
| Futures | `futures_sina_main_sina`, `futures_zh_spot` | `futures` |

## Operating System Support

### Supported Operating Systems

| Operating System | Support Status | Tested | Notes |
|------------------|---------------|--------|-------|
| **macOS (Intel)** | ✅ Full Support | Yes | Primary development platform |
| **macOS (Apple Silicon)** | ✅ Full Support | Yes | M1/M2 chips, native support |
| **Linux (Ubuntu)** | ✅ Full Support | Yes | Server deployment, CI/CD |
| **Linux (CentOS/RHEL)** | ✅ Full Support | Limited | Server deployment |
| **Linux (Debian)** | ✅ Full Support | Limited | Server deployment |
| **Windows 10/11** | ✅ Full Support | Yes | Desktop usage |
| **Windows Server** | ✅ Full Support | Limited | Server deployment |
| **FreeBSD** | ⚠️ Community Support | No | Best effort |

### OS-specific Considerations

#### macOS

```bash
# Installation on macOS
pip install akshare-one

# With TA-Lib (requires Homebrew)
brew install ta-lib
pip install akshare-one[talib]
```

**Notes**:
- ✅ Full native support for Apple Silicon (M1/M2/M3)
- ✅ No Rosetta 2 required
- ✅ All features tested and working

#### Linux

```bash
# Installation on Linux
pip install akshare-one

# With TA-Lib (requires system package)
sudo apt-get install -y ta-lib  # Ubuntu/Debian
sudo yum install -y ta-lib      # CentOS/RHEL
pip install akshare-one[talib]
```

**Notes**:
- ✅ Primary deployment platform for servers
- ✅ Docker container support
- ✅ Tested on Ubuntu 20.04, 22.04, 24.04

#### Windows

```powershell
# Installation on Windows
pip install akshare-one

# With TA-Lib (requires precompiled binary)
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.6.4-cp311-win_amd64.whl
pip install akshare-one[talib]
```

**Notes**:
- ✅ Full support for Windows 10 and 11
- ⚠️ TA-Lib installation requires precompiled wheel
- ✅ PowerShell and Command Prompt both supported

### Platform-specific Features

| Feature | macOS | Linux | Windows | Notes |
|---------|-------|-------|---------|-------|
| Core data fetching | ✅ | ✅ | ✅ | All platforms |
| Multi-source routing | ✅ | ✅ | ✅ | All platforms |
| Caching system | ✅ | ✅ | ✅ | File-based cache |
| Technical indicators | ✅ | ✅ | ⚠️ | TA-Lib may need manual install |
| MCP server | ✅ | ✅ | ✅ | Optional dependency |
| SSL verification | ✅ | ✅ | ⚠️ | Windows may need cert config |

## Dependency Version Requirements

### Core Dependencies

| Dependency | Minimum Version | Maximum Version | Tested Range | Purpose |
|-----------|----------------|-----------------|--------------|---------|
| **akshare** | 1.17.80 | No upper bound | 1.17.80 - 1.18.x | Upstream data source |
| **pandas** | Implicit (via akshare) | No upper bound | 1.5.x - 2.x | Data manipulation |
| **cachetools** | 5.5.0 | No upper bound | 5.5.0+ | Caching system |
| **requests** | Implicit (via akshare) | No upper bound | 2.28.x+ | HTTP client |

### Optional Dependencies

#### Technical Indicators (TA-Lib)

| Dependency | Minimum Version | Maximum Version | Tested Range | Purpose |
|-----------|----------------|-----------------|--------------|---------|
| **ta-lib** | 0.6.4 | No upper bound | 0.6.4+ | Technical indicators |

```toml
# pyproject.toml
[project.optional-dependencies]
talib = ["ta-lib>=0.6.4"]
```

**Installation**:
```bash
# macOS/Linux
pip install ta-lib>=0.6.4

# Windows (requires precompiled wheel)
pip install TA_Lib-0.6.4-cp311-win_amd64.whl
```

#### MCP Server

| Dependency | Minimum Version | Maximum Version | Tested Range | Purpose |
|-----------|----------------|-----------------|--------------|---------|
| **fastmcp** | 2.11.3 | No upper bound | 2.11.3+ | MCP protocol |
| **pydantic** | 2.0.0 | No upper bound | 2.x+ | Data validation |
| **uvicorn** | 0.35.0 | No upper bound | 0.35.0+ | ASGI server |

```toml
# pyproject.toml
[project.optional-dependencies]
mcp = [
    "fastmcp>=2.11.3",
    "pydantic>=2.0.0",
    "uvicorn>=0.35.0",
]
```

**Installation**:
```bash
pip install akshare-one[mcp]
```

### Development Dependencies

| Dependency | Minimum Version | Maximum Version | Tested Range | Purpose |
|-----------|----------------|-----------------|--------------|---------|
| **pytest** | 8.4.1 | No upper bound | 8.4.1+ | Testing framework |
| **pytest-cov** | 6.2.1 | No upper bound | 6.2.1+ | Coverage reporting |
| **pytest-timeout** | Implicit | No upper bound | Latest | Test timeout |
| **ruff** | 0.12.1 | No upper bound | 0.12.1+ | Linting |
| **ty** | 0.0.10 | No upper bound | 0.0.10+ | Type checking |
| **mkdocs-material** | 9.6.15 | No upper bound | 9.6.15+ | Documentation |
| **pandas-stubs** | 2.3.0 | No upper bound | 2.3.0+ | Type stubs |
| **types-cachetools** | 6.1.0 | No upper bound | 6.1.0+ | Type stubs |
| **types-requests** | 2.32.4 | No upper bound | 2.32.4+ | Type stubs |
| **pre-commit** | 4.2.0 | No upper bound | 4.2.0+ | Git hooks |

```toml
# pyproject.toml
[dependency-groups]
dev = [
    "pytest>=8.4.1",
    "pytest-cov>=6.2.1",
    "ruff>=0.12.1",
    "ty>=0.0.10",
    "mkdocs-material>=9.6.15",
    ...
]
```

### Dependency Version Constraints Strategy

We follow a **minimal constraint** strategy:

1. **Minimum versions only**: Specify minimum tested versions
2. **No upper bounds**: Allow users to use latest versions
3. **Regular testing**: Test against latest versions in CI
4. **Quick fixes**: If breaking changes occur, release patch quickly

**Rationale**:
- ✅ Users get latest features and security fixes
- ✅ Reduces dependency conflicts
- ✅ Follows Python packaging best practices
- ⚠️ Requires monitoring upstream changes

## Compatibility Testing

### CI/CD Testing Matrix

Our automated testing covers multiple combinations:

```yaml
# .github/workflows/test.yml
strategy:
  fail-fast: false
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest, macos-latest, windows-latest]
    akshare-version: ['1.17.80', '1.18.0']  # Tested versions
```

**Total test combinations**: 3 Python versions × 3 OS × 2 AkShare versions = 18 configurations

### Compatibility Verification Tests

| Test Type | Coverage | Frequency |
|-----------|----------|-----------|
| Unit tests | All modules | Every commit |
| Integration tests | Multi-source, API calls | Every PR |
| Contract tests | API stability | Every release |
| Edge case tests | Error handling | Weekly |
| Performance tests | Cache, routing | Monthly |
| Compatibility tests | Python/OS/AkShare matrix | Every release |

### Manual Compatibility Checks

Before each release, we manually verify:

- [ ] Installation on clean Python 3.10, 3.11, 3.12 environments
- [ ] All examples run successfully on macOS, Linux, Windows
- [ ] TA-Lib installation works with optional dependency
- [ ] MCP server starts and responds correctly
- [ ] Multi-source failover works with network issues
- [ ] Documentation builds on all platforms

## Compatibility Issues and Resolutions

### Known Issues

| Issue | Platform | Python Version | Status | Resolution |
|-------|----------|---------------|--------|------------|
| TA-Lib installation on Windows | Windows | All | ⚠️ Known | Use precompiled wheel |
| SSL certificate verification on Windows | Windows | All | ⚠️ Known | Configure SSL or use `configure_ssl_verification(False)` |
| AkShare field naming changes | All | All | ⚠️ Upstream | Use compatibility adapter |
| Large DataFrame memory usage | All | 3.10 | ⚠️ Known | Use `row_filter` to limit data |

### Resolution Procedures

#### TA-Lib Installation Issues

```bash
# macOS/Linux solution
brew install ta-lib  # macOS
sudo apt-get install ta-lib  # Ubuntu
pip install ta-lib

# Windows solution
# Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.6.4-cp311-win_amd64.whl
```

#### SSL Certificate Issues

```python
from akshare_one import configure_ssl_verification

# Disable SSL verification (not recommended for production)
configure_ssl_verification(False)

# Or configure custom CA bundle
configure_ssl_verification(ca_bundle_path="/path/to/certificates.pem")
```

#### AkShare API Drift

```python
from akshare_one import AkShareAdapter

# Use adapter for graceful handling
adapter = AkShareAdapter()
df = adapter.call("stock_zh_a_hist", symbol="600000", fallback=True)

# Check function existence
if adapter.check_function("some_function"):
    df = adapter.call("some_function")
else:
    # Use alternative
    df = adapter.call("alternative_function")
```

## Future Compatibility Plans

### Planned Support

| Feature/Version | Target Date | Notes |
|----------------|------------|-------|
| Python 3.13 support | 2026 Q4 | When Python 3.13 stable release |
| AkShare 1.19.x support | 2026 Q3 | Test and adapt when released |
| Async/await support | 2027 Q1 | Async data fetching (optional) |
| PyPy support | 2027 Q2 | Alternative Python implementation |

### Deprecation Schedule

| Version/Feature | Deprecation Date | Removal Date | Reason |
|----------------|-----------------|--------------|--------|
| Python 3.9 support | 2026 Q1 | Already removed | Below minimum |
| Old factory pattern | 2026 Q2 | Already removed | v0.5.0 refactoring |
| Undocumented APIs | 2026 Q3 | 2026 Q4 | Standardization |

---

For compatibility questions or issues, please:
1. Check this document first
2. Search existing GitHub Issues
3. Open a new Issue with your environment details:
   - Python version (`python --version`)
   - AkShare version (`pip show akshare`)
   - Operating system
   - Error message and traceback