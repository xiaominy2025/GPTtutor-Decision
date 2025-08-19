# Optimized Lambda Deployment Script
# Uses Lambda Layers for dependencies and minimal function code

param(
    [string]$FunctionName = "gpttutor-api-v1666",
    [string]$Region = "us-east-2",
    [string]$LayerName = "gpttutor-v1666-dependencies"
)

Write-Host "🚀 Starting Optimized Lambda Deployment..." -ForegroundColor Green

# Step 1: Create optimized function package (excluding unnecessary files)
Write-Host "📦 Creating optimized function package..." -ForegroundColor Yellow

# Create temporary directory for clean deployment
$tempDir = "temp-deploy"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy only essential files
$essentialFiles = @(
    "lambda_function.py",
    "api_server.py", 
    "query_engine.py",
    "courses",
    "requirements.txt"
)

foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        if ((Get-Item $file).PSIsContainer) {
            Copy-Item $file -Destination $tempDir -Recurse -Force
        } else {
            Copy-Item $file -Destination $tempDir -Force
        }
        Write-Host "  ✅ Copied: $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $file" -ForegroundColor Red
    }
}

# Step 2: Create optimized function zip
$functionZip = "gpttutor-v1666-optimized.zip"
if (Test-Path $functionZip) {
    Remove-Item $functionZip -Force
}

Set-Location $tempDir
Compress-Archive -Path * -DestinationPath "../$functionZip" -Force
Set-Location ..

Write-Host "  ✅ Created: $functionZip" -ForegroundColor Green

# Step 3: Get layer ARN
Write-Host "🔍 Getting layer ARN..." -ForegroundColor Yellow
try {
    $layerArn = aws lambda list-layer-versions --layer-name $LayerName --region $Region --query "LayerVersions[0].LayerVersionArn" --output text
    if ($layerArn -eq "None") {
        Write-Host "  ❌ Layer not found: $LayerName" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✅ Found layer: $layerArn" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Error getting layer ARN: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Update function code
Write-Host "📤 Updating function code..." -ForegroundColor Yellow
try {
    aws lambda update-function-code --function-name $FunctionName --zip-file fileb://$functionZip --region $Region | Out-Null
    Write-Host "  ✅ Function code updated" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Error updating function code: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Attach layer
Write-Host "🔗 Attaching layer..." -ForegroundColor Yellow
try {
    aws lambda update-function-configuration --function-name $FunctionName --layers $layerArn --region $Region | Out-Null
    Write-Host "  ✅ Layer attached" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Error attaching layer: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Wait for update to complete
Write-Host "⏳ Waiting for function to update..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Step 7: Test deployment
Write-Host "🧪 Testing deployment..." -ForegroundColor Yellow
try {
    $body = @{ query = "Test query for optimization" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com/query" -Method POST -Body $body -ContentType "application/json"
    Write-Host "  ✅ Deployment test successful" -ForegroundColor Green
    Write-Host "  📊 Response status: $($response.status)" -ForegroundColor Cyan
} catch {
    Write-Host "  ❌ Deployment test failed: $_" -ForegroundColor Red
}

# Step 8: Cleanup
Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
Write-Host "  ✅ Cleanup complete" -ForegroundColor Green

# Step 9: Show optimization results
Write-Host "📊 Optimization Results:" -ForegroundColor Cyan
$originalSize = (Get-Item "gpttutor-v1666.zip").Length
$optimizedSize = (Get-Item $functionZip).Length
$reduction = [math]::Round((($originalSize - $optimizedSize) / $originalSize) * 100, 2)

Write-Host "  📦 Original size: $([math]::Round($originalSize / 1MB, 2)) MB" -ForegroundColor White
Write-Host "  📦 Optimized size: $([math]::Round($optimizedSize / 1MB, 2)) MB" -ForegroundColor White
Write-Host "  📉 Size reduction: $reduction%" -ForegroundColor Green

Write-Host "Optimized deployment complete!" -ForegroundColor Green
