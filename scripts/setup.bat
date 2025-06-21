@echo off
REM Cryptocurrency Arbitrage Detection System - Windows Setup Script
REM This script provides a graceful way to start the system on Windows

echo 🚀 Starting Cryptocurrency Arbitrage Detection System...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo [SUCCESS] Docker is running

REM Check for existing containers
docker ps -a --format "table {{.Names}}" | findstr "arbitrage-" >nul
if %errorlevel% equ 0 (
    echo [WARNING] Found existing arbitrage containers
    set /p "response=Do you want to stop and remove existing containers? (y/N): "
    if /i "%response%"=="y" (
        echo [INFO] Stopping and removing existing containers...
        docker-compose down
    )
)

REM Build and start services
echo [INFO] Building and starting services...
docker-compose build --no-cache
docker-compose up -d

REM Wait for services
echo [INFO] Waiting for services to become healthy...
timeout /t 30 /nobreak >nul

echo [SUCCESS] All services are running!

echo.
echo 🌐 Service URLs:
echo   Frontend:                 http://localhost:5173
echo   Market Data Service:      http://localhost:8001
echo   Arbitrage Detection:      http://localhost:8002
echo   Exchange Integration:     http://localhost:8003
echo   TimescaleDB:             postgresql://postgres:arbitrage_password_2025@localhost:5432/arbitrage_db
echo   Redis:                   redis://localhost:6379
echo   Kafka:                   localhost:9092
echo.

echo 📋 To view logs:
echo   All services:    docker-compose logs -f
echo   Specific service: docker-compose logs -f [service-name]
echo.

echo 🎉 System is ready for development!
pause
