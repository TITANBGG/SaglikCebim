@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-presentation.ps1"
if errorlevel 1 (
  echo.
  echo Start failed.
  exit /b 1
)
