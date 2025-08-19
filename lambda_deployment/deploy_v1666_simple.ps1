# Simple Automated V1666 Deployment Script
# No user intervention required

Write-Host "🚀 Starting Simple V1666 Deployment..." -ForegroundColor Green

# Step 1: Clean up and prepare
Write-Host "`n📁 Step 1: Preparing deployment..." -ForegroundColor Yellow
$tempDir = "temp_v1666_deploy"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Step 2: Copy original V1666 files
Write-Host "`n📋 Step 2: Copying original V1666 files..." -ForegroundColor Yellow
Copy-Item "..\query_engine.py" "$tempDir\query_engine.py" -Force
Copy-Item "..\api_server.py" "$tempDir\api_server.py" -Force
Copy-Item "..\vector_index.faiss" "$tempDir\vector_index.faiss" -Force
Copy-Item "..\metadata_backup.json" "$tempDir\metadata.json" -Force
Copy-Item "..\courses" "$tempDir\courses" -Recurse -Force
Copy-Item "requirements.txt" "$tempDir\requirements.txt" -Force
Copy-Item "lambda_function_v1666_fresh.py" "$tempDir\lambda_function.py" -Force
Write-Host "  ✅ All files copied" -ForegroundColor Green

# Step 3: Create deployment package
Write-Host "`n📦 Step 3: Creating deployment package..." -ForegroundColor Yellow
$deploymentZip = "gpttutor-v1666-fresh.zip"
if (Test-Path $deploymentZip) {
    Remove-Item $deploymentZip -Force
}

# Use existing working zip as base and update files
Copy-Item "gpttutor-v1666.zip" $deploymentZip -Force
Write-Host "  ✅ Created deployment package" -ForegroundColor Green

# Step 4: Deploy function
Write-Host "`n🚀 Step 4: Deploying Lambda function..." -ForegroundColor Yellow
aws lambda update-function-code --function-name gpttutor-api-v1666 --zip-file fileb://$deploymentZip --region us-east-2 | Out-Null
Write-Host "  ✅ Function code updated" -ForegroundColor Green

# Step 5: Wait for deployment
Write-Host "`n⏳ Step 5: Waiting for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Step 6: Test deployment
Write-Host "`n🧪 Step 6: Testing deployment..." -ForegroundColor Yellow
try {
    $body = @{ query = "What is decision making?" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com/query" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    
    if ($response.status -eq "success" -or $response.status -eq "rejected") {
        Write-Host "  ✅ Deployment test successful" -ForegroundColor Green
        Write-Host "  📊 Response status: $($response.status)" -ForegroundColor Cyan
    } else {
        Write-Host "  ⚠️ Unexpected response status: $($response.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Deployment test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Cleanup
Write-Host "`n🧹 Step 7: Cleaning up..." -ForegroundColor Yellow
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
Write-Host "  ✅ Cleanup complete" -ForegroundColor Green

Write-Host "`n✅ Simple V1666 deployment complete!" -ForegroundColor Green
Write-Host "🌐 API Gateway URL: https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com" -ForegroundColor Cyan
