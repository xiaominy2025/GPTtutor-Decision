# Test deduplication feature with a query that should generate multiple concepts
Write-Host "Testing deduplication feature..."

$response = Invoke-WebRequest -Method POST -Uri "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query" -Headers @{"Content-Type"="application/json"} -Body '{"query":"What are the key decision-making biases and how do they affect strategic thinking?"}' -TimeoutSec 120

Write-Host "Status Code: $($response.StatusCode)"
Write-Host "Content Length: $($response.RawContentLength)"

# Parse the response
$data = $response.Content | ConvertFrom-Json

# Check if concepts were extracted
$concepts = $data.data.conceptsToolsPractice
Write-Host "Number of concepts extracted: $($concepts.Count)"

if ($concepts.Count -gt 0) {
    Write-Host "Concepts found:"
    for ($i = 0; $i -lt $concepts.Count; $i++) {
        Write-Host "  $($i+1). $($concepts[$i].term): $($concepts[$i].definition)"
    }
    
    # Check for duplicates
    $terms = $concepts | ForEach-Object { $_.term.ToLower() }
    $uniqueTerms = $terms | Sort-Object -Unique
    Write-Host "Total terms: $($terms.Count)"
    Write-Host "Unique terms: $($uniqueTerms.Count)"
    
    if ($terms.Count -eq $uniqueTerms.Count) {
        Write-Host "✅ No duplicates found - deduplication working correctly"
    } else {
        Write-Host "⚠️ Duplicates found - deduplication may not be working"
    }
} else {
    Write-Host "⚠️ No concepts extracted - checking answer text"
    
    # Extract concepts from answer text
    $answer = $data.data.answer
    if ($answer -match '\*\*Concepts/Tools\*\*\s*\n\n(.*?)(?=\n\n|$)') {
        $conceptsText = $matches[1]
        Write-Host "Concepts section in answer:"
        Write-Host $conceptsText
    }
}
