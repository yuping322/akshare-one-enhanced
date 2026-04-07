# GitHub Badges Configuration

This document describes the badges displayed in the README and how to configure them.

## Current Badges

### 1. Tests Badge
![Tests](https://github.com/zwldarren/akshare-one/actions/workflows/test.yml/badge.svg)

**Source**: GitHub Actions workflow status
**Workflow**: `.github/workflows/test.yml`
**Status**: Shows pass/fail status of the most recent workflow run

**Configuration**:
- Automatically updates based on workflow results
- No manual configuration needed
- Link: `https://github.com/OWNER/REPO/actions/workflows/test.yml`

### 2. Coverage Badge
![Coverage](https://codecov.io/gh/zwldarren/akshare-one/branch/main/graph/badge.svg)

**Source**: Codecov coverage service
**Configuration**:
1. Connect repository to Codecov (https://codecov.io)
2. Add `CODECOV_TOKEN` to GitHub Secrets
3. Coverage uploads happen automatically in CI workflow

**Thresholds**:
- Current: 30%
- Display shows actual coverage percentage
- Color changes based on coverage:
  - 🟢 Green: ≥70%
  - 🟡 Yellow: 50-70%
  - 🔴 Red: <50%

### 3. PyPI Badge
![PyPI](https://img.shields.io/pypi/v/akshare-one.svg)

**Source**: PyPI package registry
**Configuration**: Automatic once package is published to PyPI
**Link**: `https://pypi.org/project/akshare-one/`

### 4. License Badge
![License](https://img.shields.io/github/license/zwldarren/akshare-one.svg)

**Source**: GitHub repository license detection
**Configuration**: Automatic if LICENSE file exists in repository

### 5. Python Versions Badge
![Python](https://img.shields.io/pypi/pyversions/akshare-one.svg)

**Source**: PyPI package metadata
**Configuration**: Based on `requires-python` in `pyproject.toml`
```toml
[project]
requires-python = ">=3.10"
```

## Adding Additional Badges

### Quality Badge (Ruff)

```markdown
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
```

Add to lint job output for automatic updates.

### Pre-commit Badge

```markdown
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
```

### Documentation Badge

```markdown
![Documentation](https://img.shields.io/badge/docs-mkdocs-material-blue)
```

### Stars Badge

```markdown
![Stars](https://img.shields.io/github/stars/zwldarren/akshare-one.svg?style=social)
```

### Issues Badge

```markdown
![Issues](https://img.shields.io/github/issues/zwldarren/akshare-one.svg)
```

### Last Commit Badge

```markdown
![Last Commit](https://img.shields.io/github/last-commit/zwldarren/akshare-one.svg)
```

## Badge Configuration in README

Current badge section in README.md:

```markdown
<div align="center">
  <h1>AKShare One</h1>
  <p>中国金融市场数据的标准化接口</p>
  <p>
    <a href="https://github.com/zwldarren/akshare-one/actions/workflows/test.yml">
      <img src="https://github.com/zwldarren/akshare-one/actions/workflows/test.yml/badge.svg" alt="Tests">
    </a>
    <a href="https://codecov.io/gh/zwldarren/akshare-one">
      <img src="https://codecov.io/gh/zwldarren/akshare-one/branch/main/graph/badge.svg" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/akshare-one/">
      <img src="https://img.shields.io/pypi/v/akshare-one.svg" alt="PyPI">
    </a>
    <a href="https://github.com/zwldarren/akshare-one/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/zwldarren/akshare-one.svg" alt="License">
    </a>
    <a href="https://python.org">
      <img src="https://img.shields.io/pypi/pyversions/akshare-one.svg" alt="Python">
    </a>
  </p>
</div>
```

## Codecov Configuration

### Setup Steps

1. **Create Codecov Account**
   - Visit https://codecov.io
   - Sign up with GitHub
   - Authorize access to repository

2. **Add Repository**
   - Click "Add new repository"
   - Select `zwldarren/akshare-one`
   - Get `CODECOV_TOKEN`

3. **Configure GitHub Secret**
   - Go to repository Settings → Secrets and variables → Actions
   - Add `CODECOV_TOKEN` as repository secret

4. **Workflow Integration**
   Already configured in `.github/workflows/test.yml`:
   ```yaml
   - name: Upload coverage to Codecov
     uses: codecov/codecov-action@v4
     with:
       files: ./coverage.xml
       flags: unittests
       name: codecov-umbrella
       fail_ci_if_error: false
       token: ${{ secrets.CODECOV_TOKEN }}
   ```

### Codecov YAML Configuration

Create `.codecov.yml` (optional):

```yaml
coverage:
  status:
    project:
      default:
        target: 30%
        threshold: 5%
        if_not_found: success
    patch:
      default:
        target: 50%
        threshold: 10%

comment:
  layout: "reach,diff,flags,files,footer"
  behavior: default
  require_changes: false

ignore:
  - "src/akshare_one/mcp/*"
  - "src/akshare_one/logging_config.py"
  - "src/akshare_one/health/*"
```

## Badge Status Colors

### GitHub Actions Badge
- 🟢 **Green**: Workflow passed
- 🔴 **Red**: Workflow failed
- 🟡 **Yellow**: Workflow running or no status

### Coverage Badge
- 🟢 **Green**: ≥70% coverage
- 🟡 **Yellow**: 50-70% coverage
- 🔴 **Red**: <50% coverage

### PyPI Badge
- 🟢 **Green**: Latest version published
- Shows version number

## Troubleshooting Badges

### Tests Badge Shows Failed

1. Check workflow runs in Actions tab
2. Fix failing tests locally
3. Push fix and verify badge updates

### Coverage Badge Not Showing

1. Verify Codecov is connected
2. Check `CODECOV_TOKEN` secret exists
3. Verify coverage upload in workflow
4. Check Codecov dashboard for errors

### PyPI Badge Shows Old Version

1. Publish new version to PyPI
2. Badge updates automatically within hours
3. Can force cache refresh by appending `?cacheSeconds=3600`

### Badge Not Updating

GitHub caches badges for performance:
- Updates typically within 1-24 hours
- Force refresh: Add random query parameter
- Example: `badge.svg?r=123`

## Custom Badge Creation

Use shields.io for custom badges:

```markdown
![Custom](https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>)
```

Examples:
- `![Build](https://img.shields.io/badge/build-passing-brightgreen)`
- `![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)`
- `![Status](https://img.shields.io/badge/status-active-green)`

## Resources

- [Shields.io](https://shields.io) - Badge generation service
- [Codecov Documentation](https://docs.codecov.com)
- [GitHub Actions Badges](https://docs.github.com/en/actions/managing-workflow-runs/adding-a-workflow-status-badge)