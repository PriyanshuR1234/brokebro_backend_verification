@echo off
echo Starting Student ID Verification Backend...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and add your Gemini API key
    echo.
    copy .env.example .env
    echo Created .env file from template. Please edit it with your API key.
    echo.
    pause
)

REM Start the application
echo.
echo Starting Flask application...
echo Server will be available at: http://localhost:5000
echo Frontend test page: http://localhost:5000 (open index.html in browser)
echo.
python app.py

pause
