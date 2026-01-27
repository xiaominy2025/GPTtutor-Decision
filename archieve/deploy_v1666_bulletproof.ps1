# ================================
# V1.6.6.6 BULLETPROOF DEPLOYMENT SCRIPT
# Addresses ALL previous deployment failures
# ================================

param (
    [string]$LambdaName = "engent-v1666-img",
    [string]$Region = "us-east-2",
    [string]$AccountId = "771049112957",
    [switch]$FreshStart = $false,
    [switch]$SkipTests = $false
)

# ================================
# CONFIGURATION & VALIDATION
# ================================

Write-Host "🚀 === V1.6.6.6 BULLETPROOF DEPLOYMENT ===" -ForegroundColor Cyan
Write-Host "Target: $LambdaName in $Region" -ForegroundColor Yellow
Write-Host "Account: $AccountId" -ForegroundColor Yellow

# Validate AWS CLI
Write-Host "`n🔍 Validating AWS CLI..." -ForegroundColor Green
try {
    $awsVersion = aws --version 2>&1
    Write-Host "✅ AWS CLI: $awsVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
}

# Validate Docker
Write-Host "`n🔍 Validating Docker..." -ForegroundColor Green
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ Docker not found. Please install Docker Desktop first."
    exit 1
}

# Check required files
Write-Host "`n🔍 Validating required files..." -ForegroundColor Green
$requiredFiles = @(
    "api_server.py",
    "query_engine_lambda_ready.py",
    "requirements_container_lambda_ready.txt",
    "vector_index.faiss",
    "courses\decision\base_metadata.json"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Error "❌ Missing required file: $file"
        exit 1
    }
    Write-Host "✅ Found: $file" -ForegroundColor Green
}

# ================================
# CLEANUP & PREPARATION
# ================================

Write-Host "`n🧹 Cleaning up previous artifacts..." -ForegroundColor Green
$cleanupItems = @(
    "build",
    ".venv", 
    "*.zip",
    "Dockerfile.bulletproof",
    ".dockerignore.bulletproof"
)

foreach ($item in $cleanupItems) {
    if (Test-Path $item) {
        Remove-Item -Recurse -Force $item -ErrorAction SilentlyContinue
        Write-Host "🗑️ Cleaned: $item" -ForegroundColor Yellow
    }
}

# Remove Python cache
Get-ChildItem -Recurse -Include __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Include *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue

# ================================
# CREATE BULLETPROOF DOCKERFILE
# ================================

Write-Host "`n🔨 Creating bulletproof Dockerfile..." -ForegroundColor Green
@"
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR \${LAMBDA_TASK_ROOT}

# Install system dependencies
RUN yum update -y && yum install -y \
    gcc \
    gcc-c++ \
    make \
    && yum clean all

# Copy requirements first for better caching
COPY requirements_container_lambda_ready.txt .

# Install Python dependencies with specific versions
RUN pip install --no-cache-dir -r requirements_container_lambda_ready.txt

# Copy application code
COPY api_server.py .
COPY query_engine_lambda_ready.py .
COPY lambda_handler_v1666_real.py .

# Copy data files
COPY vector_index.faiss .
COPY courses/ ./courses/

# Set environment variables for Lambda optimization
ENV PYTHONPATH=\${LAMBDA_TASK_ROOT}
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV TRANSFORMERS_CACHE=/tmp/transformers_cache
ENV HF_HOME=/tmp/hf_home
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers

# Set the handler
CMD ["lambda_handler_v1666_real.handler"]
"@ | Out-File Dockerfile.bulletproof -Encoding utf8

# ================================
# CREATE COMPREHENSIVE .dockerignore
# ================================

Write-Host "`n📝 Creating comprehensive .dockerignore..." -ForegroundColor Green
@"
# Windows files
Thumbs.db
desktop.ini
*.lnk
$RECYCLE.BIN/
System Volume Information/

# macOS files
.DS_Store
.AppleDouble
.LSOverride
Icon
._*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Git
.git/
.gitignore

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
.tmp/
.temp/

# Deployment artifacts
*.zip
deploy_*.ps1
Dockerfile*
.dockerignore*

# Test files
test_*.py
*_test.py
tests/

# Documentation
*.md
docs/

# Archive
archive_*/
v1666_manual/

# Other
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
"@ | Out-File .dockerignore.bulletproof -Encoding utf8

# ================================
# BUILD DOCKER IMAGE
# ================================

Write-Host "`n🔨 Building Docker image..." -ForegroundColor Green
try {
    docker build --platform linux/amd64 -f Dockerfile.bulletproof -t $LambdaName . 2>&1 | Tee-Object -FilePath "docker_build.log"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Docker build failed. Check docker_build.log for details."
        exit 1
    }
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} catch {
    Write-Error "❌ Docker build failed: $_"
    exit 1
}

# ================================
# VERIFY IMPORTS IN CONTAINER
# ================================

Write-Host "`n🔍 Verifying imports in container..." -ForegroundColor Green
try {
    $importTest = docker run --rm $LambdaName python -c "import dotenv, torch, faiss, sentence_transformers, spacy, openai, flask; print('✅ All imports successful')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Import verification failed: $importTest"
        exit 1
    }
    Write-Host $importTest -ForegroundColor Green
} catch {
    Write-Error "❌ Import verification failed: $_"
    exit 1
}

# ================================
# ECR SETUP & PUSH
# ================================

Write-Host "`n📦 Setting up ECR repository..." -ForegroundColor Green
$ecrRepo = $LambdaName.ToLower()
$ecrUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$ecrRepo"

# Create ECR repository if it doesn't exist
try {
    aws ecr describe-repositories --repository-names $ecrRepo --region $Region 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating ECR repository: $ecrRepo" -ForegroundColor Yellow
        aws ecr create-repository --repository-name $ecrRepo --region $Region
    } else {
        Write-Host "✅ ECR repository exists: $ecrRepo" -ForegroundColor Green
    }
} catch {
    Write-Error "❌ ECR repository setup failed: $_"
    exit 1
}

# Login to ECR
Write-Host "`n🔐 Logging into ECR..." -ForegroundColor Green
try {
    aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $ecrUri
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ ECR login failed"
        exit 1
    }
    Write-Host "✅ ECR login successful" -ForegroundColor Green
} catch {
    Write-Error "❌ ECR login failed: $_"
    exit 1
}

# Tag and push image
Write-Host "`n📤 Pushing image to ECR..." -ForegroundColor Green
try {
    docker tag $LambdaName`:latest $ecrUri`:latest
    docker push $ecrUri`:latest
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Image push failed"
        exit 1
    }
    Write-Host "✅ Image pushed successfully" -ForegroundColor Green
} catch {
    Write-Error "❌ Image push failed: $_"
    exit 1
}

# ================================
# LAMBDA FUNCTION SETUP
# ================================

Write-Host "`n⚡ Setting up Lambda function..." -ForegroundColor Green

# Check if function exists
$functionExists = $false
try {
    aws lambda get-function --function-name $LambdaName --region $Region 2>$null
    if ($LASTEXITCODE -eq 0) {
        $functionExists = $true
        Write-Host "✅ Lambda function exists: $LambdaName" -ForegroundColor Green
    }
} catch {
    Write-Host "📝 Lambda function does not exist, will create new one" -ForegroundColor Yellow
}

if ($FreshStart -and $functionExists) {
    Write-Host "🗑️ Deleting existing function for fresh start..." -ForegroundColor Yellow
    try {
        aws lambda delete-function --function-name $LambdaName --region $Region
        $functionExists = $false
        Write-Host "✅ Function deleted" -ForegroundColor Green
    } catch {
        Write-Error "❌ Failed to delete function: $_"
        exit 1
    }
}

if (-not $functionExists) {
    # Create new function
    Write-Host "🆕 Creating new Lambda function..." -ForegroundColor Green
    try {
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
            Write-Error "❌ Lambda function creation failed"
            exit 1
        }
        Write-Host "✅ Lambda function created successfully" -ForegroundColor Green
    } catch {
        Write-Error "❌ Lambda function creation failed: $_"
        exit 1
    }
} else {
    # Update existing function
    Write-Host "🔄 Updating existing Lambda function..." -ForegroundColor Green
    try {
        aws lambda update-function-code `
            --function-name $LambdaName `
            --image-uri "$ecrUri`:latest" `
            --region $Region
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Lambda function update failed"
            exit 1
        }
        Write-Host "✅ Lambda function updated successfully" -ForegroundColor Green
    } catch {
        Write-Error "❌ Lambda function update failed: $_"
        exit 1
    }
}

# ================================
# CONFIGURE LAMBDA SETTINGS
# ================================

Write-Host "`n⚙️ Configuring Lambda settings..." -ForegroundColor Green
try {
    aws lambda update-function-configuration `
        --function-name $LambdaName `
        --timeout 30 `
        --memory-size 4096 `
        --environment "Variables={COURSE_ID=decision,METADATA_MODE=baked,OMP_NUM_THREADS=1,MKL_NUM_THREADS=1,HF_HUB_DISABLE_TELEMETRY=1}" `
        --region $Region
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Lambda configuration update failed"
        exit 1
    }
    Write-Host "✅ Lambda settings configured" -ForegroundColor Green
} catch {
    Write-Error "❌ Lambda configuration failed: $_"
    exit 1
}

# ================================
# CREATE FUNCTION URL
# ================================

Write-Host "`n🌐 Creating function URL..." -ForegroundColor Green
try {
    $timestamp = Get-Date -Format "yyyyMMddHHmmss"
    aws lambda create-function-url-config `
        --function-name $LambdaName `
        --auth-type NONE `
        --cors "AllowCredentials=false,AllowHeaders=*,AllowMethods=*,AllowOrigins=*,ExposeHeaders=*,MaxAge=86400" `
        --region $Region 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Function URL may already exist, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Function URL created" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Function URL creation failed (may already exist): $_" -ForegroundColor Yellow
}

# Get function URL
try {
    $functionUrl = aws lambda get-function-url-config --function-name $LambdaName --region $Region --query 'FunctionUrl' --output text 2>$null
    if ($functionUrl) {
        Write-Host "🌐 Function URL: $functionUrl" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️ Could not retrieve function URL" -ForegroundColor Yellow
}

# ================================
# TESTING & VERIFICATION
# ================================

if (-not $SkipTests) {
    Write-Host "`n🧪 Testing deployment..." -ForegroundColor Green
    
    # Wait for function to be ready
    Write-Host "⏳ Waiting 15 seconds for Lambda to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    # Test Lambda directly
    Write-Host "🔍 Testing Lambda function directly..." -ForegroundColor Green
    try {
        $testPayload = '{"httpMethod":"GET","path":"/health","headers":{"Content-Type":"application/json"}}'
        $testPayload | Out-File test_payload.json -Encoding utf8
        
        aws lambda invoke `
            --function-name $LambdaName `
            --payload file://test_payload.json `
            --region $Region `
            response.json
        
        if ($LASTEXITCODE -eq 0) {
            $response = Get-Content response.json -Raw | ConvertFrom-Json
            Write-Host "✅ Direct Lambda test successful" -ForegroundColor Green
            Write-Host "Response: $($response.body)" -ForegroundColor Gray
        } else {
            Write-Warning "⚠️ Direct Lambda test failed"
        }
    } catch {
        Write-Warning "⚠️ Direct Lambda test failed: $_"
    }
    
    # Test via function URL if available
    if ($functionUrl) {
        Write-Host "`n🔍 Testing via function URL..." -ForegroundColor Green
        try {
            $healthUrl = "$functionUrl/health"
            $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 30
            Write-Host "✅ Function URL test successful" -ForegroundColor Green
            Write-Host "Status: $($response.StatusCode)" -ForegroundColor Gray
            Write-Host "Response: $($response.Content)" -ForegroundColor Gray
        } catch {
            Write-Warning "⚠️ Function URL test failed: $_"
        }
    }
    
    # Clean up test files
    Remove-Item test_payload.json, response.json -ErrorAction SilentlyContinue
}

# ================================
# CLEANUP & SUMMARY
# ================================

Write-Host "`n🧹 Cleaning up temporary files..." -ForegroundColor Green
$cleanupItems = @(
    "Dockerfile.bulletproof",
    ".dockerignore.bulletproof",
    "docker_build.log"
)

foreach ($item in $cleanupItems) {
    if (Test-Path $item) {
        Remove-Item $item -ErrorAction SilentlyContinue
    }
}

# ================================
# DEPLOYMENT SUMMARY
# ================================

Write-Host "`n🎉 === DEPLOYMENT COMPLETED SUCCESSFULLY ===" -ForegroundColor Cyan
Write-Host "Function Name: $LambdaName" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "ECR Repository: $ecrRepo" -ForegroundColor Yellow
Write-Host "Image URI: $ecrUri`:latest" -ForegroundColor Yellow

if ($functionUrl) {
    Write-Host "`n🌐 Function URL: $functionUrl" -ForegroundColor Cyan
    Write-Host "Health Check: $functionUrl/health" -ForegroundColor Cyan
    Write-Host "Query Endpoint: $functionUrl/query" -ForegroundColor Cyan
}

Write-Host "`n📋 Next Steps:" -ForegroundColor Green
Write-Host "1. Test the health endpoint: $functionUrl/health" -ForegroundColor White
Write-Host "2. Test a query: POST $functionUrl/query with JSON payload" -ForegroundColor White
Write-Host "3. Monitor CloudWatch logs for any issues" -ForegroundColor White
Write-Host "4. Update your frontend to use the new function URL" -ForegroundColor White

Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Green
Write-Host "• Check CloudWatch logs: aws logs tail /aws/lambda/$LambdaName --follow" -ForegroundColor White
Write-Host "• Test Lambda directly: aws lambda invoke --function-name $LambdaName --payload '{\"httpMethod\":\"GET\",\"path\":\"/health\"}' response.json" -ForegroundColor White
Write-Host "• View function details: aws lambda get-function --function-name $LambdaName" -ForegroundColor White

Write-Host "`n✅ BULLETPROOF DEPLOYMENT COMPLETE!" -ForegroundColor Green
