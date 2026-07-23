@echo off
title davici-resolve — Setup & Launch
setlocal enabledelayedexpansion

echo ==========================================
echo   davici-resolve — Color Grading Panel
echo   Professional DaVinci Resolve-style tool
echo   Powered by Blender GPL color science
echo ==========================================
echo.

:: Detect Python
set PYTHON=python
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check Python version
"%PYTHON%" -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10+ required. You have:
    "%PYTHON%" --version
    pause
    exit /b 1
)

set VENV_DIR=%~dp0venv
set REQUIREMENTS=%~dp0requirements.txt

:: Create or use virtual environment
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [1/4] Creating virtual environment...
    "%PYTHON%" -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ERROR: Could not create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Using existing virtual environment...
)

:: Activate
call "%VENV_DIR%\Scripts\activate.bat"

:: Install dependencies
echo [2/4] Installing dependencies (this may take a few minutes)...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip -q
if exist "%REQUIREMENTS%" (
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REQUIREMENTS%" --default-timeout=120 -q
) else (
    "%VENV_DIR%\Scripts\python.exe" -m pip install PySide6 numpy opencv-python Pillow --default-timeout=120 -q
)
if errorlevel 1 (
    echo.
    echo WARNING: Some packages failed to install. Trying mirrors...
    "%VENV_DIR%\Scripts\python.exe" -m pip install PySide6 numpy opencv-python Pillow --default-timeout=300 -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -q
    if errorlevel 1 (
        echo.
        echo ERROR: Could not install dependencies. Check your internet connection.
        pause
        exit /b 1
    )
)

:: Run tests
echo [3/4] Running tests...
"%VENV_DIR%\Scripts\python.exe" -m pytest software\tests\ -v --tb=short 2>&1 | findstr /C:"passed" /C:"failed"
echo Tests complete.

:: Launch application
echo [4/4] Launching davici-resolve...
echo.
start /B "" "%VENV_DIR%\Scripts\python.exe" "%~dp0software\main.py"
echo Application started. Close the window to exit.
echo.
pause
