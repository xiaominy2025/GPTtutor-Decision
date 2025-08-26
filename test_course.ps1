Write-Host "Testing Course Endpoint..."

$uri = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/api/course/decision"
$headers = @{ "Origin" = "https://www.engentlabs.com" }

try {
    $response = Invoke-WebRequest -Uri $uri -Headers $headers
    Write-Host "GET /api/course/decision - Status: $($response.StatusCode)"
    Write-Host "CORS Origin: $($response.Headers['access-control-allow-origin'])"
    Write-Host "Response Preview: $($response.Content.Substring(0, 100))..."
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}

try {
    $response = Invoke-WebRequest -Uri $uri -Method OPTIONS -Headers @{ "Origin" = "https://www.engentlabs.com"; "Access-Control-Request-Method" = "GET" }
    Write-Host "OPTIONS /api/course/decision - Status: $($response.StatusCode)"
    Write-Host "CORS Origin: $($response.Headers['access-control-allow-origin'])"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
