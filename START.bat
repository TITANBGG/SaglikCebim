@echo off
setlocal EnableDelayedExpansion
title SaglikCebim - Baslatici

echo.
echo =====================================================
echo   SaglikCebim - Sistem Baslatici
echo =====================================================
echo.

set ROOT=%~dp0
set BACKEND=%ROOT%backend (1)
set FRONTEND=%ROOT%frontend
set PYTHON=%BACKEND%\venv\Scripts\python.exe

REM ── 1. Python venv kontrolu ──────────────────────────
if not exist "%PYTHON%" (
    echo [HATA] Python venv bulunamadi:
    echo        %PYTHON%
    echo.
    echo Cozum: backend (1) klasorunde "python -m venv venv" calistirin
    pause
    exit /b 1
)

REM ── 2. Port temizligi (8000 ve 5173) ─────────────────
echo [1/4] Eski prosesler temizleniyor...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM ── 3. Ollama kontrolu ───────────────────────────────
echo [2/4] Ollama kontrol ediliyor...
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3 -UseBasicParsing; Write-Host '  Ollama: HAZIR' -ForegroundColor Green } catch { Write-Host '  UYARI: Ollama kapali - Chat/AI ozelligi calismaz' -ForegroundColor Yellow }"

REM ── 4. Backend ───────────────────────────────────────
echo [3/4] Backend baslatiliyor (port 8000)...
start "SaglikCebim BACKEND" cmd /k "cd /d "%BACKEND%" && echo Backend baslatiliyor... && "%PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

REM Backend ayaga kalkana kadar bekle
echo     Hazir olana kadar bekleniyor...
set /a ATTEMPTS=0
:WAIT_BACKEND
timeout /t 2 /nobreak >nul
set /a ATTEMPTS+=1
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 2 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 goto BACKEND_READY
if %ATTEMPTS% geq 20 (
    echo [HATA] Backend 40 saniyede hazir olmadi.
    echo Backend penceresini kontrol edin.
    pause
    exit /b 1
)
goto WAIT_BACKEND

:BACKEND_READY
echo     Backend HAZIR (http://127.0.0.1:8000)

REM ── 5. Frontend ──────────────────────────────────────
echo [4/4] Frontend baslatiliyor (port 5173)...
start "SaglikCebim FRONTEND" cmd /k "cd /d "%FRONTEND%" && echo Frontend baslatiliyor... && npm.cmd run dev -- --host 127.0.0.1 --port 5173"

REM Frontend ayaga kalkana kadar bekle
echo     Hazir olana kadar bekleniyor...
set /a ATTEMPTS=0
:WAIT_FRONTEND
timeout /t 2 /nobreak >nul
set /a ATTEMPTS+=1
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -TimeoutSec 2 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 goto FRONTEND_READY
if %ATTEMPTS% geq 25 (
    echo [UYARI] Frontend 50 saniyede hazir olmadi, yine de devam ediliyor.
    goto DONE
)
goto WAIT_FRONTEND

:FRONTEND_READY
echo     Frontend HAZIR (http://127.0.0.1:5173)

:DONE
echo.
echo =====================================================
echo   SISTEM HAZIR
echo =====================================================
echo   Frontend  : http://127.0.0.1:5173
echo   Backend   : http://127.0.0.1:8000
echo   API Docs  : http://127.0.0.1:8000/docs
echo =====================================================
echo.
echo Tarayici aciliyor...
start "" "http://127.0.0.1:5173"
echo.
echo Sistemi durdurmak icin: STOP.bat
echo Bu pencereyi kapatabilirsiniz.
echo.
pause
