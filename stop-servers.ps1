# Stop Running Servers Script
# Run ye commands PowerShell mein

# 1. Port 8000 ko free karein (Backend)
Write-Host "Checking port 8000..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $pid = $port8000.OwningProcess
    Write-Host "Killing process $pid on port 8000..." -ForegroundColor Red
    Stop-Process -Id $pid -Force
    Write-Host "Port 8000 freed!" -ForegroundColor Green
} else {
    Write-Host "Port 8000 is already free" -ForegroundColor Green
}

# 2. Port 3000 ko free karein (Frontend)
Write-Host "`nChecking port 3000..." -ForegroundColor Yellow
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    $pid = $port3000.OwningProcess
    Write-Host "Killing process $pid on port 3000..." -ForegroundColor Red
    Stop-Process -Id $pid -Force
    Write-Host "Port 3000 freed!" -ForegroundColor Green
} else {
    Write-Host "Port 3000 is already free" -ForegroundColor Green
}

# 3. Next.js lock file ko delete karein
Write-Host "`nCleaning Next.js lock file..." -ForegroundColor Yellow
$lockFile = "D:\Hackthon_GIAIC\Hacthon_ALL_phase\KIro_Todo\frontend\.next\dev\lock"
if (Test-Path $lockFile) {
    Remove-Item $lockFile -Force
    Write-Host "Lock file removed!" -ForegroundColor Green
} else {
    Write-Host "No lock file found" -ForegroundColor Green
}

Write-Host "`n✅ All ports freed! Ready to start servers." -ForegroundColor Green
