@echo off
title SaglikCebim - Durdur

echo.
echo =====================================================
echo   SaglikCebim - Sistem Durduruluyor
echo =====================================================
echo.

echo Port 8000 (backend) kapatiliyor...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   PID %%a kapatildi.
)

echo Port 5173 (frontend) kapatiliyor...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   PID %%a kapatildi.
)

echo.
echo Sistem durduruldu.
timeout /t 2 /nobreak >nul
