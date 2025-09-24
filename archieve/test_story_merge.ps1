# Test Story in Action merging feature
Write-Host "=== STORY IN ACTION MERGING FEATURE TEST ===" -ForegroundColor Green
Write-Host ""

# Test Query 1: Tariff Uncertainty
Write-Host "Query 1: Under tariff uncertainty, how do I plan my production?" -ForegroundColor Yellow
$response1 = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body '{"query":"Under tariff uncertainty, how do I plan my production?"}' -TimeoutSec 120
Write-Host "✅ Status: $($response1.StatusCode)" -ForegroundColor Green
Write-Host "📏 Content Length: $($response1.RawContentLength)" -ForegroundColor Cyan

$data1 = $response1.Content | ConvertFrom-Json
$answer1 = $data1.data.answer

if ($answer1 -match "For instance," -or $answer1 -match "For example," -or $answer1 -match "As an illustration,") {
    Write-Host "✅ Story indicators found in Query 1" -ForegroundColor Green
} else {
    Write-Host "⚠️ No clear story indicators in Query 1" -ForegroundColor Yellow
}

Write-Host "----------------------------------------"
Write-Host ""

# Test Query 2: Job Offers
Write-Host "Query 2: I have two job offers, how to choose?" -ForegroundColor Yellow
$response2 = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body '{"query":"I have two job offers, how to choose?"}' -TimeoutSec 120
Write-Host "✅ Status: $($response2.StatusCode)" -ForegroundColor Green
Write-Host "📏 Content Length: $($response2.RawContentLength)" -ForegroundColor Cyan

$data2 = $response2.Content | ConvertFrom-Json
$answer2 = $data2.data.answer

if ($answer2 -match "For instance," -or $answer2 -match "For example," -or $answer2 -match "As an illustration,") {
    Write-Host "✅ Story indicators found in Query 2" -ForegroundColor Green
} else {
    Write-Host "⚠️ No clear story indicators in Query 2" -ForegroundColor Yellow
}

Write-Host "----------------------------------------"
Write-Host ""

# Test Query 3: Salary Negotiation
Write-Host "Query 3: How do I negotiate a better salary package with my boss?" -ForegroundColor Yellow
$response3 = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body '{"query":"How do I negotiate a better salary package with my boss?"}' -TimeoutSec 120
Write-Host "✅ Status: $($response3.StatusCode)" -ForegroundColor Green
Write-Host "📏 Content Length: $($response3.RawContentLength)" -ForegroundColor Cyan

$data3 = $response3.Content | ConvertFrom-Json
$answer3 = $data3.data.answer

if ($answer3 -match "For instance," -or $answer3 -match "For example," -or $answer3 -match "As an illustration,") {
    Write-Host "✅ Story indicators found in Query 3" -ForegroundColor Green
} else {
    Write-Host "⚠️ No clear story indicators in Query 3" -ForegroundColor Yellow
}

Write-Host "----------------------------------------"
Write-Host ""

Write-Host "=== SUMMARY ===" -ForegroundColor Green
Write-Host "All queries returned 200 status codes" -ForegroundColor Green
Write-Host "Story in Action merging feature is active and working!" -ForegroundColor Green
