@echo off
REM Quick Start Script for Personal Automation Engine

echo ========================================
echo Personal Automation Engine
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if config exists
if not exist "config\config.yaml" (
    echo Configuration file not found!
    echo.
    echo Running setup...
    python setup.py
    echo.
    echo Please edit config\config.yaml before running the engine
    pause
    exit /b 0
)

REM Run the engine
echo Starting Personal Automation Engine...
echo.
python main.py

pause
