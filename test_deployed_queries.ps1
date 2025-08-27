# Test script for deployed Lambda function v1666
Write-Host "Testing deployed Lambda function v1666 with specified queries..."

$queries = @(
    "Under tariff uncertainty, how do I plan my production?",
    "I have two job offers, how to choose?",
    "How to convey bad news to my boss?",
    "How do I negotiate a better salary package with my boss?",
    "How to negotiate with a dealership?"
)

$results = @()

foreach ($query in $queries) {
    Write-Host "`nTesting query: $query"
    
    try {
        $body = @{
            query = $query
            course_id = "decision"
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
        
        $responseData = $response.Content | ConvertFrom-Json
        
        $result = @{
            Query = $query
            Answer = $responseData.data.answer
            StrategicThinkingLens = $responseData.data.strategicThinkingLens
            FollowUpPrompts = $responseData.data.followUpPrompts
            ConceptsToolsPractice = $responseData.data.conceptsToolsPractice
            Model = $responseData.data.model
            ProcessingTime = $responseData.data.processing_time
            Status = "Success"
        }
        
        $results += $result
        Write-Host "✅ Success"
        
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)"
        $result = @{
            Query = $query
            Answer = "Error occurred during processing"
            StrategicThinkingLens = ""
            FollowUpPrompts = ""
            ConceptsToolsPractice = @()
            Model = "error"
            ProcessingTime = 0
            Status = "Failed"
            Error = $_.Exception.Message
        }
        $results += $result
    }
}

# Save results to JSON for later processing
$results | ConvertTo-Json -Depth 10 | Out-File -FilePath "deployed_test_results.json" -Encoding UTF8

Write-Host "`nTest completed. Results saved to deployed_test_results.json"
