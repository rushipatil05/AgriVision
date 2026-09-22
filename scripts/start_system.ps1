<#
.SYNOPSIS
  AgriPulse Full-Stack Unified Development Startup Script
.DESCRIPTION
  Launches the FastAPI backend and Angular frontend concurrently.
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AGRIPULSE -- PRECISION AGRICULTURE DL PLATFORM" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
$BackendProcess = Start-Process -FilePath "$BackendDir\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $BackendDir -PassThru

Start-Sleep -Seconds 3

Write-Host "[2/2] Starting Angular Frontend on http://localhost:4200..." -ForegroundColor Yellow
$FrontendProcess = Start-Process -FilePath "npm.cmd" -ArgumentList "start" -WorkingDirectory $FrontendDir -PassThru

Write-Host "`nAgriPulse System is Live!" -ForegroundColor Green
Write-Host " - Frontend UI:   http://localhost:4200" -ForegroundColor White
Write-Host " - Backend Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host " - Health Status: http://localhost:8000/api/health" -ForegroundColor White
Write-Host "`nPress Ctrl+C or close the terminal windows to exit." -ForegroundColor Gray
