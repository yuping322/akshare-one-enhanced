#!/bin/bash
# AKShare One Quick Start Script for Linux/macOS
# This script helps you quickly set up and verify your AKShare One installation

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

# Check Python version
check_python_version() {
    print_msg "Checking Python version..." $BLUE

    if ! command -v python3 &> /dev/null; then
        print_msg "Error: Python 3 not found. Please install Python 3.10-3.13." $RED
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    # Check minimum version (3.10)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_msg "Error: Python version must be >= 3.10. Current version: $(python3 --version)" $RED
        exit 1
    fi

    # Check maximum version (< 3.14)
    if [ "$PYTHON_MAJOR" -gt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]); then
        print_msg "Error: Python version must be < 3.14 (3.10-3.13 supported). Current version: $(python3 --version)" $RED
        print_msg "Python 3.14+ is not yet supported. Please use Python 3.10, 3.11, 3.12, or 3.13." $YELLOW
        exit 1
    fi

    print_msg "✓ Python version OK: $(python3 --version)" $GREEN
}

# Create virtual environment (optional)
create_venv() {
    print_msg "\nWould you like to create a virtual environment? (y/n)" $YELLOW
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_msg "Creating virtual environment..." $BLUE

        if [ -d ".venv" ]; then
            print_msg "Virtual environment already exists. Using existing .venv" $YELLOW
        else
            python3 -m venv .venv
            print_msg "✓ Virtual environment created: .venv" $GREEN
        fi

        # Activate venv
        source .venv/bin/activate
        print_msg "✓ Virtual environment activated" $GREEN
    else
        print_msg "Skipping virtual environment creation" $YELLOW
    fi
}

# Install dependencies
install_dependencies() {
    print_msg "\nInstalling AKShare One..." $BLUE

    # Check if pip is available
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_msg "Error: pip not found. Please install pip." $RED
        exit 1
    fi

    # Use pip3 if available, otherwise pip
    PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi

    # Install in editable mode
    $PIP_CMD install -e .

    if [ $? -eq 0 ]; then
        print_msg "✓ AKShare One installed successfully" $GREEN
    else
        print_msg "Error: Installation failed" $RED
        exit 1
    fi

    # Optional: Install TA-Lib
    print_msg "\nWould you like to install TA-Lib for technical indicators? (y/n)" $YELLOW
    read -r response

    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_msg "Installing TA-Lib..." $BLUE

        # Try to install TA-Lib
        if $PIP_CMD install -e ".[talib]" 2>/dev/null; then
            print_msg "✓ TA-Lib installed successfully" $GREEN
        else
            print_msg "⚠ TA-Lib installation failed. This is optional and may require additional system dependencies." $YELLOW
            print_msg "  For macOS: brew install ta-lib" $YELLOW
            print_msg "  For Linux: sudo apt-get install ta-lib (or equivalent)" $YELLOW
        fi
    fi
}

# Run verification tests
run_verification() {
    print_msg "\nRunning verification tests..." $BLUE

    VERIFICATION_SCRIPT="scripts/verify_installation.py"

    if [ ! -f "$VERIFICATION_SCRIPT" ]; then
        print_msg "Warning: Verification script not found at $VERIFICATION_SCRIPT" $YELLOW
        print_msg "Skipping verification..." $YELLOW
        return
    fi

    python3 $VERIFICATION_SCRIPT

    if [ $? -eq 0 ]; then
        print_msg "✓ Verification passed" $GREEN
    else
        print_msg "⚠ Some verification tests failed. Please check the output above." $YELLOW
    fi
}

# Display success message and next steps
display_next_steps() {
    print_msg "\n========================================" $GREEN
    print_msg "✓ Setup Complete!" $GREEN
    print_msg "========================================" $GREEN

    print_msg "\nQuick Start Examples:" $BLUE
    echo "
  # Get historical data
  python3 -c \"from akshare_one import get_hist_data; df = get_hist_data('600000'); print(df.head())\"\"

  # Get real-time data
  python3 -c \"from akshare_one import get_realtime_data; df = get_realtime_data('600000'); print(df.head())\"\"

  # Calculate technical indicators
  python3 -c \"from akshare_one import get_hist_data; from akshare_one.indicators import get_sma; df = get_hist_data('600000'); sma = get_sma(df, window=20); print(sma.head())\"\"
"

    print_msg "\nNext Steps:" $BLUE
    echo "  1. Read the documentation: docs/quickstart.md"
    echo "  2. Explore examples: examples/"
    echo "  3. Check API reference: https://zwldarren.github.io/akshare-one/"
    echo "  4. Join discussions: https://github.com/zwldarren/akshare-one/discussions"

    print_msg "\nNeed help?" $YELLOW
    echo "  - Documentation: https://zwldarren.github.io/akshare-one/"
    echo "  - Issues: https://github.com/zwldarren/akshare-one/issues"
    echo "  - Email: support@example.com"

    # If venv was created, remind to activate
    if [ -d ".venv" ]; then
        print_msg "\nNote: Virtual environment created. To activate in future sessions:" $YELLOW
        echo "  source .venv/bin/activate"
    fi
}

# Main execution
main() {
    print_msg "========================================" $BLUE
    print_msg "AKShare One Quick Start Script" $BLUE
    print_msg "========================================" $BLUE

    # Get script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

    # Change to project root
    cd "$PROJECT_ROOT"

    # Run setup steps
    check_python_version
    create_venv
    install_dependencies
    run_verification
    display_next_steps

    print_msg "\nTotal time: ~2-3 minutes" $GREEN
}

# Run main function
main