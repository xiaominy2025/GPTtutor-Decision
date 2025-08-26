# Comprehensive CORS Validation Test
Write-Host "🔍 CORS Validation Test Suite" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Test 1: GET health
Write-Host "`n📋 Test 1: GET /health" -ForegroundColor Yellow
$uri = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/health"
$headers = @{ "Origin" = "https://www.engentlabs.com" }

try {
    $response = Invoke-WebRequest -Uri $uri -Headers $headers
    Write-Host "✅ Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response Headers:" -ForegroundColor Cyan
    $response.Headers.GetEnumerator() | Where-Object { $_.Key -like "*cors*" -or $_.Key -like "*origin*" } | ForEach-Object {
        Write-Host "   $($_.Key): $($_.Value)" -ForegroundColor White
    }
    Write-Host "📝 Response Body Preview:" -ForegroundColor Cyan
    Write-Host "   $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: OPTIONS health
Write-Host "`n📋 Test 2: OPTIONS /health" -ForegroundColor Yellow
$optionsHeaders = @{
    "Origin" = "https://www.engentlabs.com"
    "Access-Control-Request-Method" = "GET"
}

try {
    $response = Invoke-WebRequest -Uri $uri -Method OPTIONS -Headers $optionsHeaders
    Write-Host "✅ Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 CORS Headers:" -ForegroundColor Cyan
    if ($response.Headers.ContainsKey("Access-Control-Allow-Origin")) {
        Write-Host "   ✅ Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Access-Control-Allow-Origin: MISSING" -ForegroundColor Red
    }
    if ($response.Headers.ContainsKey("Access-Control-Allow-Methods")) {
        Write-Host "   ✅ Access-Control-Allow-Methods: $($response.Headers['Access-Control-Allow-Methods'])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Access-Control-Allow-Methods: MISSING" -ForegroundColor Red
    }
    if ($response.Headers.ContainsKey("Access-Control-Allow-Headers")) {
        Write-Host "   ✅ Access-Control-Allow-Headers: $($response.Headers['Access-Control-Allow-Headers'])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Access-Control-Allow-Headers: MISSING" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: GET course metadata
Write-Host "`n📋 Test 3: GET /api/course/decision" -ForegroundColor Yellow
$uri = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/api/course/decision"

try {
    $response = Invoke-WebRequest -Uri $uri -Headers $headers
    Write-Host "✅ Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response Headers:" -ForegroundColor Cyan
    $response.Headers.GetEnumerator() | Where-Object { $_.Key -like "*cors*" -or $_.Key -like "*origin*" } | ForEach-Object {
        Write-Host "   $($_.Key): $($_.Value)" -ForegroundColor White
    }
    Write-Host "📝 Response Body Preview:" -ForegroundColor Cyan
    Write-Host "   $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor White
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: OPTIONS course metadata
Write-Host "`n📋 Test 4: OPTIONS /api/course/decision" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $uri -Method OPTIONS -Headers $optionsHeaders
    Write-Host "✅ Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 CORS Headers:" -ForegroundColor Cyan
    if ($response.Headers.ContainsKey("Access-Control-Allow-Origin")) {
        Write-Host "   ✅ Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Access-Control-Allow-Origin: MISSING" -ForegroundColor Red
    }
    if ($response.Headers.ContainsKey("Access-Control-Allow-Methods")) {
        Write-Host "   ✅ Access-Control-Allow-Methods: $($response.Headers['Access-Control-Allow-Methods'])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Access-Control-Allow-Methods: MISSING" -ForegroundColor Red
    }
    if ($response.Headers.ContainsKey("Access-Control-Allow-Headers")) {
        Write-Host "   ✅ Access-Control-Allow-Headers: $($response.Headers['Access-Control-Allow-Headers'])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Access-Control-Allow-Headers: MISSING" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🏁 CORS Validation Test Complete" -ForegroundColor Green
