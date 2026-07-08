@echo off
REM SaglikCebim - One-Click Backend Starter
REM Double-click this file to start the backend!

cd /d "%~dp0"
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0quick-start.py"
) else (
    py -3 "%~dp0quick-start.py"
)
pause
