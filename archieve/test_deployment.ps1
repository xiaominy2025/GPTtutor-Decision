# Test script for deployed Lambda function
Write-Host "Testing deployed Lambda function..."

# Test health endpoint
Write-Host "`n1. Testing /health endpoint..."
try {
    $response = Invoke-WebRequest -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/health" -TimeoutSec 10
    Write-Host "✅ Health endpoint response:"
    Write-Host $response.Content
} catch {
    Write-Host "❌ Health endpoint error: $($_.Exception.Message)"
}

# Test query endpoint
Write-Host "`n2. Testing /query endpoint..."
try {
    $body = @{
        query = "How should I plan production under tariff uncertainty?"
        course_id = "decision"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Query endpoint response:"
    Write-Host $response.Content
} catch {
    Write-Host "❌ Query endpoint error: $($_.Exception.Message)"
}

Write-Host "`nTest completed."
