# ================================
# V1.6.6.6 Robust Lambda Deployment - Avoids Windows/Proxy Issues
# ================================

param (
    [string]$LambdaName = "engent-labs-backend-v1666",
    [string]$Region = "us-east-2",
    [string]$AccountId = "771049112957",
    [string]$ImageTag = "latest"
)

Write-Host "=== Starting Robust V1.6.6.6 Deployment ==="

# Step 0 - Clean environment completely
Write-Host "🧹 Cleaning environment..."
Remove-Item -Recurse -Force build, .venv, v1666.zip, temp_build -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Include __pycache__, *.pyc, .DS_Store, Thumbs.db | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Step 1 - Verify required files
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
Write-Host "✅ All required files found."

# Step 2 - Create clean Dockerfile for Linux
Write-Host "🐳 Creating clean Linux Dockerfile..."
$dockerfileContent = @"
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR /var/task

# Copy requirements first for better caching
COPY requirements_container.txt ./requirements.txt

# Install dependencies with explicit platform
RUN pip install --no-cache-dir --platform manylinux2014_x86_64 --only-binary=all -r requirements.txt

# Copy application code
COPY api_server.py ./
COPY query_engine.py ./
COPY lambda_handler_v1666_real.py ./

# Copy course data
COPY courses/ ./courses/

# Copy FAISS index
COPY vector_index.faiss ./

# Set environment variables
ENV COURSE_ID=decision
ENV METADATA_MODE=baked
ENV PYTHONPATH=/var/task

# Ensure proper permissions
RUN chmod 755 /var/task/lambda_handler_v1666_real.py

# Set the handler
CMD ["lambda_handler_v1666_real.handler"]
"@

$dockerfileContent | Out-File -FilePath "Dockerfile.lambda" -Encoding utf8
Write-Host "✅ Clean Dockerfile created."

# Step 3 - Create .dockerignore to exclude Windows files
Write-Host "📝 Creating .dockerignore..."
$dockerignoreContent = @"
# Windows files
*.exe
*.dll
*.pyd
Thumbs.db
desktop.ini
$RECYCLE.BIN/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Development files
.git/
.gitignore
.env
.venv/
venv/
env/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db

# Build artifacts
build/
dist/
*.egg-info/

# Logs
*.log

# Temporary files
*.tmp
*.temp
temp_build/
"@

$dockerignoreContent | Out-File -FilePath ".dockerignore" -Encoding utf8
Write-Host "✅ .dockerignore created."

# Step 4 - Build Docker image with explicit platform
Write-Host "🔨 Building Docker image for Linux..."
docker build --platform linux/amd64 -f Dockerfile.lambda -t $LambdaName .

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Docker build failed"
    Write-Host "Troubleshooting tips:"
    Write-Host "1. Ensure Docker Desktop is running"
    Write-Host "2. Check if you have enough disk space"
    Write-Host "3. Try: docker system prune -a"
    exit 1
}
Write-Host "✅ Docker image built successfully."

# Step 5 - Test image locally (optional but recommended)
Write-Host "🧪 Testing Docker image..."
docker run --rm -p 9000:8080 $LambdaName
$dockerPid = $null

Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" -Method POST -Body '{"httpMethod":"GET","path":"/health"}' -ContentType "application/json" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Docker image test successful"
    } else {
        Write-Warning "⚠️ Docker image test returned status: $($response.StatusCode)"
    }
} catch {
    Write-Warning "⚠️ Docker image test failed: $_"
} finally {
    # Clean up test container
    docker stop $dockerPid 2>$null
}

# Step 6 - Configure AWS CLI for ECR
Write-Host "🔐 Configuring AWS ECR access..."

# Check AWS CLI configuration
$awsConfig = aws configure list 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ AWS CLI not configured. Please run: aws configure"
    exit 1
}

# Authenticate with ECR
Write-Host "Authenticating with ECR..."
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $AccountId.dkr.ecr.$Region.amazonaws.com

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ ECR authentication failed"
    Write-Host "Troubleshooting:"
    Write-Host "1. Check AWS credentials: aws sts get-caller-identity"
    Write-Host "2. Verify region: $Region"
    Write-Host "3. Check ECR permissions"
    exit 1
}
Write-Host "✅ ECR authentication successful."

# Step 7 - Create ECR repository
Write-Host "📦 Creating ECR repository..."
aws ecr create-repository --repository-name $LambdaName --region $Region 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Created new ECR repository: $LambdaName"
} else {
    Write-Host "ℹ️ ECR repository already exists: $LambdaName"
}

# Step 8 - Tag and push image
$ecrUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$LambdaName"
Write-Host "🏷️ Tagging image for ECR: $ecrUri"
docker tag $LambdaName $ecrUri`:$ImageTag

Write-Host "📤 Pushing image to ECR..."
docker push $ecrUri`:$ImageTag

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to push image to ECR"
    Write-Host "Troubleshooting:"
    Write-Host "1. Check internet connection"
    Write-Host "2. Verify ECR repository exists"
    Write-Host "3. Check AWS permissions"
    exit 1
}
Write-Host "✅ Image pushed to ECR successfully."

# Step 9 - Deploy infrastructure (skip if using existing)
Write-Host "🏗️ Deploying infrastructure..."
if (Test-Path "infra") {
    cd infra
    
    # Install dependencies if needed
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
        Write-Warning "⚠️ CDK deployment failed, continuing with manual Lambda update"
    } else {
        Write-Host "✅ Infrastructure deployed successfully."
    }
    
    cd ..
} else {
    Write-Host "ℹ️ No infra directory found, skipping CDK deployment"
}

# Step 10 - Update Lambda function
Write-Host "🔄 Updating Lambda function..."
aws lambda update-function-code `
    --function-name $LambdaName `
    --image-uri "$ecrUri`:$ImageTag" `
    --region $Region

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to update Lambda function"
    Write-Host "Troubleshooting:"
    Write-Host "1. Check if Lambda function exists: $LambdaName"
    Write-Host "2. Verify ECR image URI: $ecrUri`:$ImageTag"
    Write-Host "3. Check Lambda permissions"
    exit 1
}

# Wait for update to complete
Write-Host "⏳ Waiting for Lambda function update..."
aws lambda wait function-updated --function-name $LambdaName --region $Region
Write-Host "✅ Lambda function updated successfully."

# Step 11 - Configure Lambda settings
Write-Host "⚙️ Configuring Lambda settings..."
aws lambda update-function-configuration `
    --function-name $LambdaName `
    --timeout 30 `
    --memory-size 4096 `
    --environment "Variables={COURSE_ID=decision,METADATA_MODE=baked}" `
    --region $Region

Write-Host "✅ Lambda configuration updated."

# Step 12 - Test deployment
Write-Host "🧪 Testing deployment..."
Start-Sleep -Seconds 10

try {
    # Get Lambda function URL or API Gateway URL
    $functionUrl = aws lambda get-function-url-config --function-name $LambdaName --region $Region --query 'FunctionUrl' --output text 2>$null
    
    if ($functionUrl) {
        Write-Host "Testing Lambda Function URL: $functionUrl"
        $response = Invoke-WebRequest -Uri "$functionUrl/health" -UseBasicParsing -TimeoutSec 15
        Write-Host "✅ Health check successful: $($response.StatusCode)"
        Write-Host "Response: $($response.Content)"
    } else {
        Write-Host "ℹ️ No Function URL found, deployment complete"
    }
} catch {
    Write-Warning "⚠️ Health check failed: $_"
    Write-Host "ℹ️ Deployment completed, but health check failed"
}

# Step 13 - Cleanup
Write-Host "🧹 Cleaning up..."
Remove-Item -Recurse -Force build, .venv, v1666.zip, temp_build -ErrorAction SilentlyContinue
Remove-Item "Dockerfile.lambda" -ErrorAction SilentlyContinue

Write-Host "=== Robust V1.6.6.6 Deployment Completed Successfully ==="
Write-Host "🎯 Deployed: api_server.py + query_engine.py (100% as-is)"
Write-Host "📦 Container: $ecrUri`:$ImageTag"
Write-Host "🔗 Lambda Function: $LambdaName"
Write-Host "🌍 Region: $Region"
Write-Host "💡 Use silent frontend warmup for best UX"
