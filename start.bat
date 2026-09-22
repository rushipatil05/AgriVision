@echo off
title AgriPulse Platform Launcher
echo ==========================================================
echo    AGRIPULSE -- PRECISION AGRICULTURE DL PLATFORM
echo ==========================================================
echo.

set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend
set FRONTEND_DIR=%PROJECT_ROOT%frontend

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "AgriPulse Backend" cmd /k "cd /d "%BACKEND_DIR%" && "%BACKEND_DIR%\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Angular Frontend on http://localhost:4200 ...
start "AgriPulse Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm start"

echo.
echo ==========================================================
echo AgriPulse is running!
echo  - Frontend Web UI:  http://localhost:4200
echo  - Backend API Docs: http://localhost:8000/docs
echo  - Health Endpoint:  http://localhost:8000/api/health
echo ==========================================================
echo Close the separate backend and frontend command windows to stop the servers.
pause
