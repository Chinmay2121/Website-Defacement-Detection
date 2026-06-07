@echo off
REM Setup script for Website Defacement Detection System
REM For Windows

echo ==========================================
echo Website Defacement Detection System Setup
echo ==========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Found: %PYTHON_VERSION%

REM Create project structure
echo.
echo Creating project directories...
if not exist "src" mkdir src
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo [OK] Directories created

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Remove and recreate? (y/n): "
    if /i "%RECREATE%"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Virtual environment recreated
    ) else (
        echo Using existing virtual environment
    )
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded

REM Install dependencies
echo.
echo Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    echo [OK] Dependencies installed from requirements.txt
) else (
    echo requirements.txt not found, installing core packages...
    pip install flask requests watchdog colorama --quiet
    echo [OK] Core packages installed
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import flask, requests, watchdog, colorama" 2>nul
if %errorlevel% equ 0 (
    echo [OK] All packages verified
) else (
    echo [ERROR] Some packages failed to install
)

REM Create .gitignore
echo.
echo Creating .gitignore...
(
echo # Virtual Environment
echo venv/
echo env/
echo.
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo.
echo # Data and Logs
echo data/*.json
echo logs/*.json
echo logs/*.txt
echo !data/.gitkeep
echo !logs/.gitkeep
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
) > .gitignore
echo [OK] .gitignore created

REM Summary
echo.
echo ==========================================
echo Setup Complete! [OK]
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Start the vulnerable server (Terminal 1):
echo    python src\vulnerable_server.py
echo.
echo 3. Start the detection monitor (Terminal 2):
echo    python src\detection_monitor.py
echo.
echo 4. Run attack simulator (Terminal 3):
echo    python src\attack_simulator.py
echo.
echo For more information, see README.md
echo ==========================================
echo.
pause