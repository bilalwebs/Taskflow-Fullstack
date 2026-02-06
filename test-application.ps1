# KIro Todo Application Test Script
# Tests both backend and frontend connectivity

Write-Host "=== KIro Todo Application Test ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend Health Check
Write-Host "1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -Method GET -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Backend is running and healthy" -ForegroundColor Green
        $content = $response.Content | ConvertFrom-Json
        Write-Host "   Environment: $($content.environment)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure backend is running: uvicorn src.main:app --reload --port 8001" -ForegroundColor Yellow
}

Write-Host ""

# Test 2: Backend API Docs
Write-Host "2. Testing Backend API Documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/docs" -Method GET -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ API docs accessible at http://localhost:8001/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ API docs not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Frontend Accessibility
Write-Host "3. Testing Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Frontend is running at http://localhost:3000" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Frontend not accessible: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure frontend is running: npm run dev" -ForegroundColor Yellow
}

Write-Host ""

# Test 4: Test Signup Endpoint
Write-Host "4. Testing Signup Endpoint..." -ForegroundColor Yellow
$testEmail = "test_$(Get-Random)@example.com"
$signupBody = @{
    email = $testEmail
    password = "TestPass123"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/api/auth/signup" -Method POST -Body $signupBody -ContentType "application/json" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ Signup endpoint working" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host "   Created user: $($data.user.email)" -ForegroundColor Gray
        Write-Host "   Token received: $($data.access_token.Substring(0, 20))..." -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Signup failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application URLs:" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8001" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
