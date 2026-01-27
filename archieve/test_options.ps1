# Test OPTIONS request for health endpoint
Write-Host "=== Testing OPTIONS for /health ==="
$uri = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/health"
$headers = @{
    "Origin" = "https://www.engentlabs.com"
    "Access-Control-Request-Method" = "GET"
}

try {
    $response = Invoke-WebRequest -Uri $uri -Method OPTIONS -Headers $headers
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "CORS Headers Found:"
    if ($response.Headers.ContainsKey("Access-Control-Allow-Origin")) {
        Write-Host "✅ Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])"
    } else {
        Write-Host "❌ Access-Control-Allow-Origin: MISSING"
    }
    if ($response.Headers.ContainsKey("Access-Control-Allow-Methods")) {
        Write-Host "✅ Access-Control-Allow-Methods: $($response.Headers['Access-Control-Allow-Methods'])"
    } else {
        Write-Host "❌ Access-Control-Allow-Methods: MISSING"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host "`n=== Testing OPTIONS for /api/course/decision ==="
$uri = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/api/course/decision"
try {
    $response = Invoke-WebRequest -Uri $uri -Method OPTIONS -Headers $headers
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "CORS Headers Found:"
    if ($response.Headers.ContainsKey("Access-Control-Allow-Origin")) {
        Write-Host "✅ Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])"
    } else {
        Write-Host "❌ Access-Control-Allow-Origin: MISSING"
    }
    if ($response.Headers.ContainsKey("Access-Control-Allow-Methods")) {
        Write-Host "✅ Access-Control-Allow-Methods: $($response.Headers['Access-Control-Allow-Methods'])"
    } else {
        Write-Host "❌ Access-Control-Allow-Methods: MISSING"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
