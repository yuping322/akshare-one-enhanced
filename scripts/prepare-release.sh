#!/bin/bash
# Release Preparation Script for AKShare-One v0.5.0

set -e  # Exit on error

echo "========================================="
echo "AKShare-One v0.5.0 Release Preparation"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

# 1. Run tests
echo "Step 1: Running tests..."
pytest tests/ -v --cov=akshare_one --cov-report=term-missing
if [ $? -ne 0 ]; then
    echo "Error: Tests failed. Please fix before releasing."
    exit 1
fi
echo "✓ Tests passed"
echo ""

# 2. Check code quality
echo "Step 2: Checking code quality with ruff..."
ruff check src/
if [ $? -ne 0 ]; then
    echo "Error: Code quality checks failed. Please fix before releasing."
    exit 1
fi
echo "✓ Code quality checks passed"
echo ""

# 3. Check type hints
echo "Step 3: Checking type hints..."
# Note: This is optional, uncomment if mypy is configured
# mypy src/akshare_one/
echo "✓ Type hints check skipped (optional)"
echo ""

# 4. Build documentation
echo "Step 4: Building documentation..."
if [ -f "mkdocs.yml" ]; then
    mkdocs build
    echo "✓ Documentation built"
else
    echo "⚠ mkdocs.yml not found, skipping documentation build"
fi
echo ""

# 5. Build package
echo "Step 5: Building package..."
python -m build
if [ $? -ne 0 ]; then
    echo "Error: Package build failed"
    exit 1
fi
echo "✓ Package built successfully"
echo ""

# 6. Check package
echo "Step 6: Checking package..."
twine check dist/*
if [ $? -ne 0 ]; then
    echo "Error: Package check failed"
    exit 1
fi
echo "✓ Package check passed"
echo ""

# 7. Summary
echo "========================================="
echo "Release Preparation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review CHANGELOG.md"
echo "2. Review release notes: docs/release-notes-v0.5.0.md"
echo "3. Create git tag: git tag -a v0.5.0 -m 'Release v0.5.0'"
echo "4. Push tag: git push origin v0.5.0"
echo "5. Upload to PyPI: twine upload dist/*"
echo ""
echo "Package files ready in dist/:"
ls -lh dist/
echo ""
