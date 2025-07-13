@echo off
echo ===== Building Docker Image for Partner Dashboard =====
echo.

cd ..

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed. Please install Docker first.
    goto end
)

echo Building Docker image...
docker build -t partner-dashboard:latest -f "Deployment Approaches\Dockerfile" .

echo.
echo Docker image built successfully!
echo.
echo To run the dashboard:
echo   docker run -p 8501:8501 partner-dashboard:latest
echo.
echo Then open http://localhost:8501 in your browser.
echo.
echo To share with others, export the image:
echo   docker save partner-dashboard:latest -o partner-dashboard.tar
echo.

:end
pause
