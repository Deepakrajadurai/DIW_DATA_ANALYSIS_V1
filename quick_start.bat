@echo off
setlocal enabledelayedexpansion

:: German Economic Insights Dashboard - Quick Start Script for Windows
:: This script automates the setup and launch process

title German Economic Insights Dashboard - Setup

echo.
echo 🏛️  German Economic Insights Dashboard
echo =======================================
echo.

:: Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

:: Check if pip is installed
echo Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed
    echo Please install pip or reinstall Python with pip included
    pause
    exit /b 1
)
echo ✅ pip found

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip upgraded

:: Install requirements
echo Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
) else (
    echo ❌ requirements.txt not found!
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found
    
    :: Create .env file
    (
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo DATABASE_URL=sqlite:///./dashboard.db
        echo DEBUG=True
        echo HOST=0.0.0.0
        echo PORT=8000
    ) > .env
    
    echo ℹ️  Created .env file with default settings
    echo ⚠️  Please edit .env file and add your Gemini API key:
    echo    1. Get API key from: https://makersuite.google.com/app/apikey
    echo    2. Replace 'your_gemini_api_key_here' with your actual API key
    echo.
    
    :: Ask if user wants to continue without API key
    set /p "continue=Continue without API key? (AI features will be disabled) [y/N]: "
    if /i not "!continue!"=="y" (
        echo ℹ️  Please configure your API key and run this script again.
        pause
        exit /b 0
    )
) else (
    echo ✅ .env file found
)

:: Create necessary directories
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "static" mkdir static
if not exist "templates" mkdir templates
if not exist "services" mkdir services
if not exist "data" mkdir data
echo ✅ Directories created

:: Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found! Please ensure all project files are present.
    pause
    exit /b 1
)

:: Final setup complete
echo ✅ Setup complete!
echo.
echo ℹ️  🚀 Starting the dashboard...
echo    URL: http://localhost:8000
echo    Press Ctrl+C to stop
echo.

:: Start the application
python main.py

:: Pause before closing if there was an error
if %errorlevel% neq 0 (
    echo.
    echo ❌ Application exited with an error
    pause
)