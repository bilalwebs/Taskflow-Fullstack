@echo off
echo ========================================
echo KIro Todo - Start Frontend Server
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Checking Node.js environment...
node --version
npm --version
echo.

echo Starting Next.js frontend on port 3000...
echo.
echo Frontend will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev
