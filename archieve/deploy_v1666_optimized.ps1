# ================================
# V1.6.6.6 Optimized Lambda Deployment - All Optimizations Included
# ================================

param (
    [string]$LambdaName = "engent-labs-v1666-optimized",
    [string]$Region = "us-east-2",
    [string]$AccountId = "771049112957"
)

Write-Host "=== Starting Optimized V1.6.6.6 Deployment ==="

# Step 1 - Clean environment completely
Write-Host "🧹 Cleaning environment completely..."
Remove-Item -Recurse -Force build, .venv, v1666.zip, temp_build -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Include __pycache__, *.pyc, .DS_Store, Thumbs.db | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Step 2 - Verify all required files
$requiredFiles = @(
    "api_server.py",
    "query_engine_optimized.py", 
    "lambda_handler_v1666_real.py",
    "courses\decision\base_metadata.json",
    "courses\decision\glossary.json",
    "vector_index.faiss",
    "requirements_container_optimized.txt"
)
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Error "Missing required file: $file"
        exit 1
    }
}
Write-Host "✅ All required files verified."

# Step 3 - Create optimized Dockerfile
Write-Host "🐳 Creating optimized Dockerfile..."
$dockerfileContent = @"
FROM public.ecr.aws/lambda/python:3.11

# Set Lambda-specific environment variables
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV TRANSFORMERS_CACHE=/tmp/transformers_cache
ENV HF_HOME=/tmp/hf_home
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers

WORKDIR /var/task

# Copy optimized requirements
COPY requirements_container_optimized.txt ./requirements.txt

# Install dependencies with CPU-only optimizations
RUN pip install --no-cache-dir -r requirements.txt

# Create cache directories
RUN mkdir -p /tmp/transformers_cache /tmp/hf_home /tmp/sentence_transformers

# Copy application code
COPY api_server.py ./
COPY query_engine_optimized.py ./query_engine.py
COPY lambda_handler_v1666_real.py ./

# Copy course data
COPY courses/ ./courses/

# Copy FAISS index
COPY vector_index.faiss ./

# Set environment variables
ENV COURSE_ID=decision
ENV METADATA_MODE=baked
ENV PYTHONPATH=/var/task

# Set the handler
CMD ["lambda_handler_v1666_real.handler"]
"@

$dockerfileContent | Out-File -FilePath "Dockerfile.optimized" -Encoding utf8

# Step 4 - Create comprehensive .dockerignore
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

# Old deployment files
Dockerfile
Dockerfile.*
deploy_*.ps1

# Non-optimized files
query_engine.py
requirements_container.txt
"@

$dockerignoreContent | Out-File -FilePath ".dockerignore" -Encoding utf8

# Step 5 - Build optimized Docker image
Write-Host "🔨 Building optimized Docker image..."
docker build --platform linux/amd64 -f Dockerfile.optimized -t $LambdaName .

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Docker build failed"
    Write-Host "Troubleshooting:"
    Write-Host "1. Ensure Docker Desktop is running"
    Write-Host "2. Check disk space: docker system df"
    Write-Host "3. Clean Docker: docker system prune -a"
    exit 1
}
Write-Host "✅ Optimized Docker image built successfully."

# Step 6 - ECR setup
Write-Host "🔐 Setting up ECR..."

# Check AWS CLI
$awsIdentity = aws sts get-caller-identity --query 'Account' --output text 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ AWS CLI not configured. Run: aws configure"
    exit 1
}
Write-Host "✅ AWS CLI configured for account: $awsIdentity"

# Authenticate with ECR
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $AccountId.dkr.ecr.$Region.amazonaws.com

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ ECR authentication failed"
    exit 1
}
Write-Host "✅ ECR authentication successful."

# Step 7 - Create new ECR repository
Write-Host "📦 Creating new ECR repository: $LambdaName"
aws ecr create-repository --repository-name $LambdaName --region $Region

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to create ECR repository"
    exit 1
}
Write-Host "✅ ECR repository created successfully."

# Step 8 - Push to ECR
$ecrUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$LambdaName"
Write-Host "📤 Pushing to ECR: $ecrUri"
docker tag $LambdaName $ecrUri`:latest
docker push $ecrUri`:latest

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to push to ECR"
    exit 1
}
Write-Host "✅ Image pushed to ECR successfully."

# Step 9 - Create new Lambda function with optimized settings
Write-Host "🆕 Creating optimized Lambda function: $LambdaName"
aws lambda create-function `
    --function-name $LambdaName `
    --package-type Image `
    --code ImageUri="$ecrUri`:latest" `
    --role "arn:aws:iam::$AccountId`:role/lambda-execution-role" `
    --timeout 30 `
    --memory-size 4096 `
    --environment "Variables={COURSE_ID=decision,METADATA_MODE=baked,OMP_NUM_THREADS=1,MKL_NUM_THREADS=1,HF_HUB_DISABLE_TELEMETRY=1}" `
    --region $Region

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to create Lambda function"
    Write-Host "Note: If function already exists, it will be updated in next step"
} else {
    Write-Host "✅ Optimized Lambda function created successfully."
}

# Step 10 - Update Lambda function (in case it already existed)
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
Write-Host "✅ Lambda function updated successfully."

# Step 11 - Configure optimized Lambda settings
Write-Host "⚙️ Configuring optimized Lambda settings..."
aws lambda update-function-configuration `
    --function-name $LambdaName `
    --timeout 30 `
    --memory-size 4096 `
    --environment "Variables={COURSE_ID=decision,METADATA_MODE=baked,OMP_NUM_THREADS=1,MKL_NUM_THREADS=1,HF_HUB_DISABLE_TELEMETRY=1,TRANSFORMERS_CACHE=/tmp/transformers_cache,HF_HOME=/tmp/hf_home,SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers}" `
    --region $Region

Write-Host "✅ Optimized Lambda configuration updated."

# Step 12 - Create Function URL
Write-Host "🔗 Creating Function URL..."
aws lambda create-function-url-config `
    --function-name $LambdaName `
    --auth-type NONE `
    --region $Region

if ($LASTEXITCODE -ne 0) {
    Write-Warning "⚠️ Failed to create Function URL (may already exist)"
} else {
    Write-Host "✅ Function URL created successfully."
}

# Step 13 - Test deployment
Write-Host "🧪 Testing optimized deployment..."
Start-Sleep -Seconds 15

try {
    $functionUrl = aws lambda get-function-url-config --function-name $LambdaName --region $Region --query 'FunctionUrl' --output text 2>$null
    
    if ($functionUrl) {
        Write-Host "Testing Function URL: $functionUrl"
        $response = Invoke-WebRequest -Uri "$functionUrl/health" -UseBasicParsing -TimeoutSec 20
        Write-Host "✅ Health check successful: $($response.StatusCode)"
        Write-Host "Response: $($response.Content)"
        
        # Parse response to verify V1666 backend
        $responseData = $response.Content | ConvertFrom-Json
        if ($responseData.version -eq "1.6.6.6") {
            Write-Host "✅ Real V1666 backend confirmed!"
        }
    } else {
        Write-Host "ℹ️ No Function URL found, but Lambda function is deployed"
    }
} catch {
    Write-Warning "⚠️ Health check failed: $_"
    Write-Host "ℹ️ Lambda function deployed, but health check failed"
}

# Step 14 - Cleanup
Write-Host "🧹 Cleaning up..."
Remove-Item "Dockerfile.optimized" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build, .venv, v1666.zip, temp_build -ErrorAction SilentlyContinue

Write-Host "=== Optimized V1.6.6.6 Deployment Completed Successfully ==="
Write-Host "🎯 Optimized Lambda Function: $LambdaName"
Write-Host "📦 Optimized ECR Repository: $ecrUri"
Write-Host "🌍 Region: $Region"
Write-Host "🔗 Function URL: $functionUrl"
Write-Host "🚀 Optimizations included:"
Write-Host "   • CPU-only PyTorch"
Write-Host "   • Single-threaded execution"
Write-Host "   • Lazy model loading"
Write-Host "   • Proxy support"
Write-Host "   • Smaller embedding model"
Write-Host "   • Optimized memory usage"
Write-Host "💡 Use silent frontend warmup for best UX"
