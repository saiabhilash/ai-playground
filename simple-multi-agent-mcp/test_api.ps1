# PowerShell test script for the Multi-Agent System API

$BASE_URL = "http://localhost:8000"

Write-Host "🧪 Testing Multi-Agent System API..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n📊 Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Root endpoint
Write-Host "`n🏠 Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Status endpoint
Write-Host "`n📈 Testing status endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/status" -Method Get
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Status check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Math query
Write-Host "`n🔢 Testing math calculation..." -ForegroundColor Yellow
try {
    $body = @{
        message = "Calculate 15 + 27"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$BASE_URL/chat" -Method Post -Body $body -ContentType "application/json"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Math test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Text analysis
Write-Host "`n📝 Testing text analysis..." -ForegroundColor Yellow
try {
    $body = @{
        message = "Analyze the sentiment of: I love sunny days!"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$BASE_URL/chat" -Method Post -Body $body -ContentType "application/json"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Text test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Complex task
Write-Host "`n🎯 Testing task coordination..." -ForegroundColor Yellow
try {
    $body = @{
        message = "Help me solve 2x + 5 = 15 and then count the words in the solution"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$BASE_URL/chat" -Method Post -Body $body -ContentType "application/json"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Task test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ API testing complete!" -ForegroundColor Green
