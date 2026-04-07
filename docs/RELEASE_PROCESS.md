# Release Process

This document describes the release process for AKShare One, including version numbering, release steps, and rollback procedures.

## Version Numbering

We follow [Semantic Versioning (SemVer)](https://semver.org/spec/v2.0.0.html) with the format `MAJOR.MINOR.PATCH`:

- **MAJOR version** (`X.0.0`): Incompatible API changes
  - Breaking changes to public APIs
  - Major architecture refactoring
  - Removal of deprecated features
  
- **MINOR version** (`0.Y.0`): New features, backward-compatible
  - New modules or data sources
  - New API endpoints
  - Enhanced functionality
  - Deprecation notices (but not removal)
  
- **PATCH version** (`0.0.Z`): Bug fixes, backward-compatible
  - Bug fixes
  - Performance improvements
  - Documentation updates
  - Test improvements

### Version Examples

| Version | Type | Example Changes |
|---------|------|-----------------|
| `1.0.0` | Major | Removed old factory pattern, breaking API changes |
| `0.5.0` | Minor | Added 14 new market data modules, multi-source routing |
| `0.5.1` | Patch | Fixed upstream API drift, improved caching |
| `0.5.2` | Patch | Enhanced error handling, documentation updates |

### Pre-release Versions

Pre-release versions use the format `X.Y.Z-alpha.N`, `X.Y.Z-beta.N`, `X.Y.Z-rc.N`:

- **alpha**: Early testing, unstable, may have breaking changes
- **beta**: Feature complete, testing phase, no major changes
- **rc**: Release candidate, final testing, ready for production

Example: `0.6.0-alpha.1`, `0.6.0-beta.2`, `0.6.0-rc.1`

## Release Checklist

### 1. Pre-release Preparation (1-2 days before)

#### Code Quality Checks

```bash
# Run all tests
pytest tests/ -v --cov=akshare_one --cov-report=term-missing

# Check coverage threshold (currently 30%)
# Ensure coverage meets fail_under requirement in pyproject.toml

# Run linting
ruff check src/ tests/

# Run type checking (if configured)
ty check

# Check documentation builds
mkdocs build
```

#### Version Updates

1. **Update `pyproject.toml` version**:
   ```toml
   [project]
   name = "akshare-one"
   version = "0.6.0"  # Update this
   ```

2. **Update `CHANGELOG.md`**:
   - Move `[Unreleased]` section to new version
   - Add version header with release date
   - Ensure all changes are documented
   - Add version comparison link at bottom

3. **Update `__init__.py` version** (if applicable):
   ```python
   __version__ = "0.6.0"
   ```

#### Documentation Review

- [ ] All new APIs have docstrings
- [ ] README.md reflects current features
- [ ] CHANGELOG.md is complete and accurate
- [ ] VERSION_MATRIX.md updated for new dependencies
- [ ] UPGRADE_GUIDE.md updated for breaking changes

### 2. Testing Phase

#### Automated Testing

```bash
# Run full test suite
pytest tests/ -v --cov --cov-report=html

# Run contract tests specifically
pytest tests/test_api_contract.py -v

# Run multi-source tests
pytest tests/test_multi_source_comprehensive.py -v

# Run edge case tests
pytest tests/test_edge_cases.py -v
```

#### Manual Testing

- [ ] Test critical paths manually
- [ ] Test multi-source failover scenarios
- [ ] Test new features with real data
- [ ] Test backward compatibility
- [ ] Test upgrade from previous version

#### Integration Testing

- [ ] Test with real AKShare API calls
- [ ] Test with different Python versions (3.10, 3.11, 3.12)
- [ ] Test on different OS (macOS, Linux, Windows)
- [ ] Test with optional dependencies (ta-lib, mcp)

### 3. Release Execution

#### Git Tagging

```bash
# Create release branch
git checkout -b release/0.6.0

# Commit version updates
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.6.0"

# Create annotated tag
git tag -a v0.6.0 -m "Release 0.6.0: Multi-source routing and 14 new modules"

# Push tag to remote
git push origin v0.6.0

# Merge to main
git checkout main
git merge release/0.6.0
git push origin main
```

#### PyPI Publishing

```bash
# Build distribution
python -m build

# Check distribution
twine check dist/*

# Upload to TestPyPI first (optional but recommended)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ akshare-one==0.6.0

# Upload to PyPI
twine upload dist/*
```

#### GitHub Release

1. Go to [GitHub Releases](https://github.com/zwldarren/akshare-one/releases)
2. Click "Draft a new release"
3. Select tag `v0.6.0`
4. Fill release title: "v0.6.0 - Multi-source Routing and Market Data Extensions"
5. Copy CHANGELOG section for this version
6. Attach distribution files (optional)
7. Publish release

### 4. Post-release Tasks

#### Documentation Update

```bash
# Build and deploy documentation
mkdocs build
mkdocs gh-deploy
```

#### Announcements

- [ ] Update GitHub README badges
- [ ] Post release announcement on GitHub Discussions
- [ ] Update PyPI project description
- [ ] Notify users via email/social media (if applicable)

#### Monitoring

- [ ] Monitor PyPI download stats
- [ ] Monitor GitHub issues for bug reports
- [ ] Check CI/CD pipeline status
- [ ] Verify documentation deployment

#### Version Branch Maintenance

For major/minor releases, create maintenance branch:

```bash
# Create maintenance branch for patches
git checkout -b maintenance/0.6.x v0.6.0
git push origin maintenance/0.6.x
```

Future patch releases (0.6.1, 0.6.2) will be based on this branch.

## Rollback Procedure

### Scenario 1: Critical Bug Found After Release

#### Immediate Response

1. **Assess severity**:
   - Critical: Data corruption, security vulnerability, breaking production
   - High: Major functionality broken
   - Medium: Minor functionality issues
   - Low: Cosmetic issues, documentation errors

2. **For critical/high severity**:

```bash
# Yank the release from PyPI
twine upload --repository pypi dist/* --yank akshare-one==0.6.0

# Create hotfix branch from previous stable tag
git checkout -b hotfix/0.5.3 v0.5.2

# Apply minimal fix
# ... fix the critical bug ...

# Update version to patch
# pyproject.toml: version = "0.5.3"
# CHANGELOG.md: Add hotfix entry

# Test the hotfix
pytest tests/ -v

# Release hotfix
git tag -a v0.5.3 -m "Hotfix 0.5.3: Critical bug fix"
git push origin v0.5.3
twine upload dist/*
```

3. **For medium/low severity**:
   - Document in GitHub Issues
   - Schedule fix for next patch release
   - Add workaround to documentation

### Scenario 2: PyPI Distribution Issues

```bash
# If upload failed or files corrupted
twine upload --repository pypi dist/* --skip-existing

# If need to replace files
# 1. Yank the version
twine upload --repository pypi --yank akshare-one==0.6.0

# 2. Rebuild
python -m build --clean

# 3. Re-upload
twine upload dist/*
```

### Scenario 3: Breaking Change Without Major Version

This should never happen if following SemVer, but if it does:

1. Acknowledge the mistake in GitHub Issues
2. Create patch release reverting breaking change
3. Properly version the breaking change in next major release
4. Update UPGRADE_GUIDE.md with migration instructions

## Release Automation

### GitHub Actions Workflow

We use GitHub Actions for automated testing and release preparation:

```yaml
# .github/workflows/release.yml (to be created)
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e .[dev]
      - run: pytest tests/ -v --cov
      
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          
  publish:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

### Automation Checklist

- [ ] GitHub Actions CI passes on release tag
- [ ] Coverage threshold met
- [ ] Documentation builds successfully
- [ ] PyPI upload automated
- [ ] GitHub release created automatically

## Release Schedule

### Regular Releases

- **Major releases**: Every 6-12 months (planned features, breaking changes)
- **Minor releases**: Every 1-2 months (new features, enhancements)
- **Patch releases**: As needed (bug fixes, hotfixes)

### Release Planning

1. **Feature roadmap**: Maintained in GitHub Projects
2. **Release milestones**: Created for each major/minor release
3. **Release candidates**: 1-2 weeks before major/minor releases
4. **Beta releases**: 2-4 weeks before major releases

### Dependency Updates

- **AkShare updates**: Monitor upstream releases, test compatibility
- **Python version support**: Follow [Python release schedule](https://www.python.org/downloads/)
- **Dependency security**: Monitor security advisories, update as needed

## Post-release Support

### Version Support Policy

| Version Type | Support Duration | Example |
|-------------|------------------|---------|
| Latest major | Active development | 0.5.x - 6 months |
| Previous major | Security fixes only | 0.4.x - 3 months |
| Older majors | Community support | 0.3.x and older - best effort |

### Deprecation Policy

1. **Deprecation notice**: Added to CHANGELOG and code comments
2. **Grace period**: 2 minor releases (e.g., deprecated in 0.5.0, removed in 0.7.0)
3. **Migration guide**: Provided in UPGRADE_GUIDE.md
4. **Final removal**: In major release with clear documentation

## Emergency Release Procedure

For critical security vulnerabilities or data corruption issues:

1. **Immediate assessment** (within 1 hour)
2. **Hotfix branch creation** (within 2 hours)
3. **Fix implementation** (within 4-6 hours)
4. **Testing** (within 2 hours)
5. **Release** (within 1 hour)
6. **Announcement** (immediately after release)

Total time: 8-10 hours from discovery to release.

## Release History

| Version | Release Date | Type | Key Changes |
|---------|-------------|------|-------------|
| 0.5.0 | 2026-04-04 | Minor | Multi-source routing, 14 new modules |
| 0.4.0 | 2026-02-15 | Minor | Market data extensions, multi-source foundation |
| 0.3.0 | 2026-01-20 | Minor | ETF/Bond/Index/Valuation modules |
| 0.2.0 | 2025-12-15 | Minor | Financial data, HK/US stocks |
| 0.1.0 | 2025-11-10 | Initial | Core modules, basic infrastructure |

---

For questions about the release process, please open a GitHub Issue or Discussion.