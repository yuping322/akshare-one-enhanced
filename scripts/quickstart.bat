@echo off
REM AKShare One Quick Start Script for Windows
REM This script helps you quickly set up and verify your AKShare One installation

setlocal enabledelayedexpansion

REM Color codes (Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Print colored message
goto :main

:print_msg
echo %BLUE%%~1%NC%
exit /b

:print_success
echo %GREEN%%~1%NC%
exit /b

:print_error
echo %RED%%~1%NC%
exit /b

:print_warning
echo %YELLOW%%~1%NC%
exit /b

REM Check Python version
:check_python_version
call :print_msg "Checking Python version..."

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_error "Error: Python not found. Please install Python 3.10 or higher."
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do set PYTHON_MAJOR=%%a& set PYTHON_MINOR=%%b

if %PYTHON_MAJOR% lss 3 (
    call :print_error "Error: Python version must be >= 3.10. Current version: %PYTHON_VERSION%"
    exit /b 1
)

if %PYTHON_MAJOR% equ 3 if %PYTHON_MINOR% lss 10 (
    call :print_error "Error: Python version must be >= 3.10. Current version: %PYTHON_VERSION%"
    exit /b 1
)

call :print_success "OK: Python version %PYTHON_VERSION%"
exit /b 0

REM Create virtual environment
:create_venv
echo.
set /p response="Would you like to create a virtual environment? (y/n): "

if /i "%response%"=="y" (
    call :print_msg "Creating virtual environment..."

    if exist .venv (
        call :print_warning "Virtual environment already exists. Using existing .venv"
    ) else (
        python -m venv .venv
        call :print_success "OK: Virtual environment created: .venv"
    )

    REM Activate venv
    call .venv\Scripts\activate.bat
    call :print_success "OK: Virtual environment activated"
) else (
    call :print_warning "Skipping virtual environment creation"
)
exit /b 0

REM Install dependencies
:install_dependencies
echo.
call :print_msg "Installing AKShare One..."

REM Check if pip is available
where pip >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_error "Error: pip not found. Please install pip."
    exit /b 1
)

REM Install in editable mode
pip install -e .

if %ERRORLEVEL% equ 0 (
    call :print_success "OK: AKShare One installed successfully"
) else (
    call :print_error "Error: Installation failed"
    exit /b 1
)

REM Optional: Install TA-Lib
echo.
set /p response="Would you like to install TA-Lib for technical indicators? (y/n): "

if /i "%response%"=="y" (
    call :print_msg "Installing TA-Lib..."

    pip install -e ".[talib]" 2>nul
    if %ERRORLEVEL% equ 0 (
        call :print_success "OK: TA-Lib installed successfully"
    ) else (
        call :print_warning "WARNING: TA-Lib installation failed. This is optional."
        call :print_warning "  For Windows: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib"
    )
)
exit /b 0

REM Run verification tests
:run_verification
echo.
call :print_msg "Running verification tests..."

set VERIFICATION_SCRIPT=scripts\verify_installation.py

if not exist "%VERIFICATION_SCRIPT%" (
    call :print_warning "Warning: Verification script not found at %VERIFICATION_SCRIPT%"
    call :print_warning "Skipping verification..."
    exit /b 0
)

python %VERIFICATION_SCRIPT%

if %ERRORLEVEL% equ 0 (
    call :print_success "OK: Verification passed"
) else (
    call :print_warning "WARNING: Some verification tests failed. Please check the output above."
)
exit /b 0

REM Display success message and next steps
:display_next_steps
echo.
call :print_success "========================================"
call :print_success "Setup Complete!"
call :print_success "========================================"

echo.
call :print_msg "Quick Start Examples:"
echo.
echo   REM Get historical data
echo   python -c "from akshare_one import get_hist_data; df = get_hist_data('600000'); print(df.head())"
echo.
echo   REM Get real-time data
echo   python -c "from akshare_one import get_realtime_data; df = get_realtime_data('600000'); print(df.head())"
echo.
echo   REM Calculate technical indicators
echo   python -c "from akshare_one import get_hist_data; from akshare_one.indicators import get_sma; df = get_hist_data('600000'); sma = get_sma(df, window=20); print(sma.head())"
echo.

call :print_msg "Next Steps:"
echo   1. Read the documentation: docs\quickstart.md
echo   2. Explore examples: examples\
echo   3. Check API reference: https://zwldarren.github.io/akshare-one/
echo   4. Join discussions: https://github.com/zwldarren/akshare-one/discussions

echo.
call :print_warning "Need help?"
echo   - Documentation: https://zwldarren.github.io/akshare-one/
echo   - Issues: https://github.com/zwldarren/akshare-one/issues

REM If venv was created, remind to activate
if exist .venv (
    echo.
    call :print_warning "Note: Virtual environment created. To activate in future sessions:"
    echo   .venv\Scripts\activate.bat
)

echo.
call :print_success "Total time: ~2-3 minutes"
exit /b 0

REM Main execution
:main
call :print_msg "========================================"
call :print_msg "AKShare One Quick Start Script"
call :print_msg "========================================"

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Change to project root
cd /d "%PROJECT_ROOT%"

REM Run setup steps
call :check_python_version
if %ERRORLEVEL% neq 0 exit /b 1

call :create_venv
call :install_dependencies
if %ERRORLEVEL% neq 0 exit /b 1

call :run_verification
call :display_next_steps

exit /b 0