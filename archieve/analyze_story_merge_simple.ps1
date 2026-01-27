# Analyze Story in Action merging results
Write-Host "=== STORY IN ACTION MERGING FEATURE ANALYSIS ===" -ForegroundColor Green
Write-Host ""

# Test each query individually
$queries = @(
    "Under tariff uncertainty, how do I plan my production?",
    "I have two job offers, how to choose?",
    "How do I negotiate a better salary package with my boss?"
)

for ($i = 0; $i -lt $queries.Count; $i++) {
    $query = $queries[$i]
    $queryNum = $i + 1
    
    Write-Host "Query $queryNum : $query" -ForegroundColor Yellow
    Write-Host "Testing..."
    
    try {
        $response = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body "{\"query\":\"$query\"}" -TimeoutSec 120
        
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            $answer = $data.data.answer
            
            Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "📏 Content Length: $($response.RawContentLength)" -ForegroundColor Cyan
            
            # Check for story indicators
            $storyIndicators = @("For instance,", "For example,", "As an illustration,", "Picture", "Imagine", "Envision", "Consider this scenario:")
            $foundIndicators = @()
            
            foreach ($indicator in $storyIndicators) {
                if ($answer -match [regex]::Escape($indicator)) {
                    $foundIndicators += $indicator
                }
            }
            
            if ($foundIndicators.Count -gt 0) {
                Write-Host "✅ Story indicators found: $($foundIndicators -join ', ')" -ForegroundColor Green
                Write-Host "✅ Story in Action merging is working!" -ForegroundColor Green
            } else {
                Write-Host "⚠️ No clear story indicators found" -ForegroundColor Yellow
            }
            
            # Check for italics formatting
            if ($answer -match "\*.*\*") {
                Write-Host "✅ Italics formatting preserved" -ForegroundColor Green
            }
            
            # Show preview of Strategic Thinking Lens
            if ($answer -match "\*\*Strategic Thinking Lens\*\*") {
                $lensMatch = [regex]::Match($answer, "\*\*Strategic Thinking Lens\*\*\s*\n\n(.*?)(?=\n\n\*\*|\Z)", [System.Text.RegularExpressions.RegexOptions]::Singleline)
                if ($lensMatch.Success) {
                    $lensContent = $lensMatch.Groups[1].Value.Trim()
                    $preview = if ($lensContent.Length -gt 150) { $lensContent.Substring(0, 150) + "..." } else { $lensContent }
                    Write-Host "📝 Lens Preview: $preview" -ForegroundColor White
                }
            }
        } else {
            Write-Host "❌ Status: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host "----------------------------------------"
    Write-Host ""
}
