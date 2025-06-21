@echo off
REM Cryptocurrency Arbitrage Detection System - Windows Clean Reset Script

echo 🧹 Cryptocurrency Arbitrage Detection System - Clean Reset
echo.

echo [WARNING] This will completely reset your development environment:
echo [WARNING] - Stop and remove all containers
echo [WARNING] - Remove all project volumes (including database data)
echo [WARNING] - Remove all project images
echo [WARNING] - Clean up networks
echo.

set /p "response=Are you sure you want to continue? (y/N): "
if /i not "%response%"=="y" (
    echo [INFO] Reset cancelled
    exit /b 0
)

REM Stop and remove containers
echo [INFO] Stopping and removing containers...
docker-compose down --remove-orphans

REM Remove volumes
echo [INFO] Removing project volumes...
for /f "tokens=*" %%i in ('docker volume ls -q ^| findstr "cryptocurrency-tracker"') do docker volume rm %%i

REM Remove images
echo [INFO] Removing project images...
for /f "tokens=*" %%i in ('docker images --format "table {{.Repository}}" ^| findstr "cryptocurrency-tracker"') do docker rmi -f %%i

REM Clean up dangling resources
echo [INFO] Cleaning up dangling resources...
docker system prune -f

echo [SUCCESS] Environment reset complete!
echo [INFO] You can now run 'scripts\setup.bat' to start fresh
pause
