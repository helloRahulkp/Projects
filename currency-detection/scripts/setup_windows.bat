@echo off
REM =============================================================================
REM Windows Setup Script — AI Currency Detection System v2.0
REM Requires: Docker Desktop for Windows
REM =============================================================================

echo ============================================================
echo  AI Currency Detection System v2.0 — Windows Setup
echo ============================================================
echo.

REM Check Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not running.
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo [OK] Docker detected.
echo.

REM Check docker compose
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose not found. Please update Docker Desktop.
    pause
    exit /b 1
)

echo [OK] Docker Compose detected.
echo.

REM Copy env example if .env doesn't exist
if not exist ".env" (
    copy ".env.example" ".env"
    echo [OK] Created .env from .env.example
)

echo.
echo [INFO] Building and starting all services...
echo [INFO] First build may take 5-10 minutes (downloading packages)...
echo.

docker compose up --build

pause
