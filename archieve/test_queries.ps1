# Test Query 1: Tariff Uncertainty
Write-Host "Testing Query 1: Under tariff uncertainty, how do I plan my production?"
$response1 = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body '{"query":"Under tariff uncertainty, how do I plan my production?"}' -TimeoutSec 120

# Test Query 2: Job Offers
Write-Host "Testing Query 2: I have two job offers, how to choose?"
$response2 = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body '{"query":"I have two job offers, how to choose?"}' -TimeoutSec 120

# Test Query 3: Salary Negotiation
Write-Host "Testing Query 3: How do I negotiate a better salary package with my boss?"
$response3 = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body '{"query":"How do I negotiate a better salary package with my boss?"}' -TimeoutSec 120

# Create results object
$results = @{
    "test_timestamp" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "query_1" = @{
        "question" = "Under tariff uncertainty, how do I plan my production?"
        "status_code" = $response1.StatusCode
        "response" = $response1.Content
        "content_length" = $response1.RawContentLength
    }
    "query_2" = @{
        "question" = "I have two job offers, how to choose?"
        "status_code" = $response2.StatusCode
        "response" = $response2.Content
        "content_length" = $response2.RawContentLength
    }
    "query_3" = @{
        "question" = "How do I negotiate a better salary package with my boss?"
        "status_code" = $response3.StatusCode
        "response" = $response3.Content
        "content_length" = $response3.RawContentLength
    }
}

# Save to JSON file
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath "query_test_results.json" -Encoding UTF8

Write-Host "Results saved to query_test_results.json"
Write-Host "Query 1 Status: $($response1.StatusCode), Length: $($response1.RawContentLength)"
Write-Host "Query 2 Status: $($response2.StatusCode), Length: $($response2.RawContentLength)"
Write-Host "Query 3 Status: $($response3.StatusCode), Length: $($response3.RawContentLength)"
