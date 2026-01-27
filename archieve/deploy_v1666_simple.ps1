# ================================
# V1.6.6.6 Simple Lambda Deployment - Minimal Issues
# ================================

param (
    [string]$LambdaName = "engent-labs-backend-v1666",
    [string]$Region = "us-east-2",
    [string]$AccountId = "771049112957"
)

Write-Host "=== Starting Simple V1.6.6.6 Deployment ==="

# Step 1 - Clean environment
Write-Host "🧹 Cleaning environment..."
Remove-Item -Recurse -Force build, .venv, v1666.zip -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Include __pycache__, *.pyc | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Step 2 - Create minimal Dockerfile
Write-Host "🐳 Creating minimal Dockerfile..."
$dockerfileContent = @"
FROM public.ecr.aws/lambda/python:3.11
WORKDIR /var/task
COPY requirements_container.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api_server.py ./
COPY query_engine.py ./
COPY lambda_handler_v1666_real.py ./
COPY courses/ ./courses/
COPY vector_index.faiss ./
ENV COURSE_ID=decision
CMD ["lambda_handler_v1666_real.handler"]
"@

$dockerfileContent | Out-File -FilePath "Dockerfile.minimal" -Encoding utf8

# Step 3 - Create .dockerignore
Write-Host "📝 Creating .dockerignore..."
$dockerignoreContent = @"
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.venv/
venv/
*.log
build/
dist/
"@

$dockerignoreContent | Out-File -FilePath ".dockerignore" -Encoding utf8

# Step 4 - Build image
Write-Host "🔨 Building Docker image..."
docker build --platform linux/amd64 -f Dockerfile.minimal -t $LambdaName .

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Docker build failed"
    exit 1
}
Write-Host "✅ Docker image built successfully."

# Step 5 - ECR setup
Write-Host "🔐 Setting up ECR..."
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $AccountId.dkr.ecr.$Region.amazonaws.com

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ ECR authentication failed"
    exit 1
}

# Create repository if needed
aws ecr create-repository --repository-name $LambdaName --region $Region 2>$null

# Step 6 - Push to ECR
$ecrUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$LambdaName"
Write-Host "📤 Pushing to ECR..."
docker tag $LambdaName $ecrUri`:latest
docker push $ecrUri`:latest

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to push to ECR"
    exit 1
}
Write-Host "✅ Image pushed to ECR successfully."

# Step 7 - Update Lambda
Write-Host "🔄 Updating Lambda function..."
aws lambda update-function-code `
    --function-name $LambdaName `
    --image-uri "$ecrUri`:latest" `
    --region $Region

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to update Lambda function"
    exit 1
}

# Wait for update
aws lambda wait function-updated --function-name $LambdaName --region $Region

# Step 8 - Configure Lambda
Write-Host "⚙️ Configuring Lambda..."
aws lambda update-function-configuration `
    --function-name $LambdaName `
    --timeout 30 `
    --memory-size 4096 `
    --environment "Variables={COURSE_ID=decision}" `
    --region $Region

# Step 9 - Cleanup
Remove-Item "Dockerfile.minimal" -ErrorAction SilentlyContinue

Write-Host "=== Simple V1.6.6.6 Deployment Completed ==="
Write-Host "🎯 Lambda Function: $LambdaName"
Write-Host "📦 Image: $ecrUri`:latest"
Write-Host "🌍 Region: $Region"
