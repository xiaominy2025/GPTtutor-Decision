# ================================
# V1.6.6.6 Real Backend Container Lambda Deployment
# Deploys api_server.py + query_engine.py as-is to AWS Lambda via ECR
# ================================

param (
    [string]$LambdaName = "engent-labs-backend-v1666-real",
    [string]$Region = "us-east-2",
    [string]$AccountId = "771049112957",
    [string]$ImageTag = "latest",
    [string]$HealthURL = "<YourLambdaOrApiGatewayURL>/health"
)

Write-Host "=== Starting V1.6.6.6 Real Backend Container Deployment ==="

# Step 0 - Clean up old artifacts
Write-Host "Cleaning old build artifacts..."
Remove-Item -Recurse -Force build, .venv, v1666_real.zip -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Include __pycache__ | Remove-Item -Recurse -Force

# Step 1 - Check required files for real V1666 backend
$requiredFiles = @(
    "api_server.py",
    "query_engine.py", 
    "lambda_handler_v1666_real.py",
    "courses\decision\base_metadata.json",
    "courses\decision\glossary.json",
    "vector_index.faiss"
)
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Error "Missing required file: $file"
        exit 1
    }
}
Write-Host "✅ All required V1666 real backend files found."

# Step 2 - Verify Dockerfile is configured for real backend
$dockerfileContent = Get-Content Dockerfile -Raw
if ($dockerfileContent -notmatch "lambda_handler_v1666_real\.handler") {
    Write-Error "Dockerfile not configured for real V1666 backend. Expected: lambda_handler_v1666_real.handler"
    exit 1
}
Write-Host "✅ Dockerfile configured for real V1666 backend."

# Step 3 - Build Docker image
Write-Host "Building Docker image for real V1666 backend..."
docker build -t $LambdaName .

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker build failed"
    exit 1
}
Write-Host "✅ Docker image built successfully."

# Step 4 - Authenticate with ECR
Write-Host "Authenticating with ECR..."
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $AccountId.dkr.ecr.$Region.amazonaws.com

if ($LASTEXITCODE -ne 0) {
    Write-Error "ECR authentication failed"
    exit 1
}
Write-Host "✅ ECR authentication successful."

# Step 5 - Create ECR repository if it doesn't exist
Write-Host "Creating ECR repository if needed..."
aws ecr create-repository --repository-name $LambdaName --region $Region 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Created new ECR repository: $LambdaName"
} else {
    Write-Host "ℹ️ ECR repository already exists: $LambdaName"
}

# Step 6 - Tag and push Docker image
$ecrUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$LambdaName"
Write-Host "Tagging image for ECR: $ecrUri"
docker tag $LambdaName $ecrUri`:$ImageTag

Write-Host "Pushing image to ECR..."
docker push $ecrUri`:$ImageTag

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to push image to ECR"
    exit 1
}
Write-Host "✅ Image pushed to ECR successfully."

# Step 7 - Deploy infrastructure using CDK
Write-Host "Deploying infrastructure using CDK..."
cd infra

# Install CDK dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing CDK dependencies..."
    npm install
}

# Bootstrap CDK if needed
Write-Host "Bootstrapping CDK..."
aws cdk bootstrap aws://$AccountId/$Region 2>$null

# Deploy stack
Write-Host "Deploying CDK stack..."
aws cdk deploy --require-approval never

if ($LASTEXITCODE -ne 0) {
    Write-Error "CDK deployment failed"
    exit 1
}

cd ..
Write-Host "✅ Infrastructure deployed successfully."

# Step 8 - Update Lambda function with new image
Write-Host "Updating Lambda function with new container image..."
aws lambda update-function-code `
    --function-name $LambdaName `
    --image-uri "$ecrUri`:$ImageTag" `
    --region $Region

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to update Lambda function"
    exit 1
}

# Wait for update to complete
Write-Host "Waiting for Lambda function update to complete..."
aws lambda wait function-updated --function-name $LambdaName --region $Region

Write-Host "✅ Lambda function updated successfully."

# Step 9 - Configure Lambda environment variables
Write-Host "Configuring Lambda environment variables..."
aws lambda update-function-configuration `
    --function-name $LambdaName `
    --environment "Variables={COURSE_ID=decision,METADATA_MODE=baked}" `
    --region $Region

Write-Host "✅ Lambda environment variables configured."

# Step 10 - Health check after deployment
if ($HealthURL -ne "<YourLambdaOrApiGatewayURL>/health") {
    Write-Host "Waiting 15 seconds for Lambda to warm up..."
    Start-Sleep -Seconds 15
    Write-Host "Checking /health endpoint at $HealthURL..."
    try {
        $response = Invoke-WebRequest -Uri $HealthURL -UseBasicParsing -TimeoutSec 15
        Write-Host "Health Check Status Code: $($response.StatusCode)"
        Write-Host "Health Check Response: $($response.Content)"
        
        # Parse response to check if it's the real V1666 backend
        $responseData = $response.Content | ConvertFrom-Json
        if ($responseData.version -eq "1.6.6.6") {
            Write-Host "✅ Real V1666 backend is running successfully!"
        } else {
            Write-Warning "⚠️ Backend version mismatch. Expected: 1.6.6.6, Got: $($responseData.version)"
        }
    } catch {
        Write-Warning "Health check failed: $_"
    }
} else {
    Write-Warning "No health check URL provided. Skipping automatic test."
}

Write-Host "=== Real V1666 Backend Deployment Completed Successfully ==="
Write-Host "🎯 Deployed: api_server.py + query_engine.py (100% as-is)"
Write-Host "📦 Container: $ecrUri`:$ImageTag"
Write-Host "🔗 Lambda Function: $LambdaName"
Write-Host "🌍 Region: $Region"
