@echo off
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║        PROMETHEUS AI  v12.0  Setup Script (Win)     ║
echo ╚══════════════════════════════════════════════════════╝
echo.

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Get it from python.org
    pause
    exit /b 1
)
echo [OK] Python found

:: Copy .env if missing
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env - EDIT IT and add your GROQ_KEY!
        echo.
        echo  Get your FREE key at: https://console.groq.com/keys
        echo.
    )
)

:: Create virtual environment
if not exist ".venv" (
    echo [...] Creating virtual environment...
    python -m venv .venv
    echo [OK] Virtual environment created
)

:: Activate and install
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated

echo [...] Installing dependencies...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo [OK] Dependencies installed

:: Create directories
if not exist "outputs"           mkdir outputs
if not exist "built_agents"      mkdir built_agents
if not exist "prometheus_memory" mkdir prometheus_memory
if not exist "core_versions"     mkdir core_versions

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║  Setup complete! To start the app:                   ║
echo ║                                                      ║
echo ║    .venv\Scripts\activate                            ║
echo ║    python app.py                                     ║
echo ║                                                      ║
echo ║  Then open: http://localhost:5000                    ║
echo ╚══════════════════════════════════════════════════════╝
echo.
pause
