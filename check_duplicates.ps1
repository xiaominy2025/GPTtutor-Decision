Write-Host "Checking for Duplicate CORS Headers..."

$uri = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/health"
$headers = @{ "Origin" = "https://www.engentlabs.com" }

try {
    $response = Invoke-WebRequest -Uri $uri -Headers $headers
    Write-Host "GET /health - Status: $($response.StatusCode)"
    Write-Host "All Headers:"
    $response.Headers.GetEnumerator() | ForEach-Object {
        Write-Host "  $($_.Key): $($_.Value)"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host "`nChecking Course Endpoint..."

$uri = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/api/course/decision"

try {
    $response = Invoke-WebRequest -Uri $uri -Headers $headers
    Write-Host "GET /api/course/decision - Status: $($response.StatusCode)"
    Write-Host "All Headers:"
    $response.Headers.GetEnumerator() | ForEach-Object {
        Write-Host "  $($_.Key): $($_.Value)"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
