@echo off
echo ========================================
echo KIro Todo - Start Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

echo Checking Python environment...
python --version
echo.

echo Starting FastAPI backend on port 8001...
echo.
echo Backend will be available at: http://localhost:8001
echo API Documentation: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn src.main:app --reload --port 8001
