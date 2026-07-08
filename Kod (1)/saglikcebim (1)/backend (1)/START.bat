@echo off
chcp 65001 > nul
cls
title SaglikCebim Backend

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   🏥 SaglikCebim Backend                       ║
echo ║                   Starting...                                  ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

if exist venv (
    echo ✅ Virtual environment found
) else (
    echo Creating venv...
    py -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

echo.
echo ✅ Starting API Server...
echo.
echo 🌐 Access points:
echo    - API:    http://127.0.0.1:8000
echo    - Docs:   http://127.0.0.1:8000/docs
echo    - ReDoc:  http://127.0.0.1:8000/redoc
echo.
echo Press CTRL+C to stop the server
echo.

call venv\Scripts\activate.bat
"%~dp0venv\Scripts\python.exe" "%~dp0run.py"

pause

