# ================================
# V1.6.6.6 Backend One-Click Deploy Script (With Health Check)
# ================================

param (
    [string]$LambdaName = "<YourLambdaName>",
    [string]$Region = "us-east-2",
    [string]$OpenAIKey = "<YourOpenAIKey>",
    [string]$HealthURL = "<YourLambdaOrApiGatewayURL>/health"
)

Write-Host "=== Starting V1.6.6.6 Deployment ==="

# Step 0 - Clean up old artifacts
Write-Host "Cleaning old build artifacts..."
Remove-Item -Recurse -Force build, .venv, v1666.zip -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Include __pycache__ | Remove-Item -Recurse -Force

# Step 1 - Check required baked metadata files
$requiredFiles = @(
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
Write-Host "All required baked metadata files found."

# Step 2 - Create lambda_requirements.txt
Write-Host "Creating lambda_requirements.txt..."
@"
flask
flask-cors
openai
faiss-cpu
numpy
scikit-learn
"@ | Out-File lambda_requirements.txt -Encoding utf8

# Step 3 - Create virtual env and install dependencies
Write-Host "Installing dependencies into build folder..."
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r lambda_requirements.txt --target build

# Step 4 - Copy backend code + baked metadata + FAISS index
Write-Host "Copying backend code and baked metadata..."
Copy-Item api_server.py build\
Copy-Item query_engine.py build\
Copy-Item vector_index.faiss build\
New-Item -ItemType Directory -Path build\courses\decision -Force | Out-Null
Copy-Item courses\decision\base_metadata.json build\courses\decision\
Copy-Item courses\decision\glossary.json build\courses\decision\

# Step 5 - Create Lambda entrypoint
Write-Host "Creating lambda_function.py entrypoint..."
@"
from api_server import app as flask_app

def handler(event, context):
    return flask_app(event, context)
"@ | Out-File build\lambda_function.py -Encoding utf8

# Step 6 - Create ZIP package
Write-Host "Creating deployment package v1666.zip..."
if (Test-Path v1666.zip) { Remove-Item v1666.zip }
Compress-Archive -Path build\* -DestinationPath v1666.zip

# Step 7 - Upload to AWS Lambda
Write-Host "Uploading v1666.zip to AWS Lambda function: $LambdaName..."
aws lambda update-function-code --function-name $LambdaName --zip-file fileb://v1666.zip --region $Region

# Step 8 - Update Lambda environment variables
Write-Host "Updating Lambda environment variables..."
aws lambda update-function-configuration --function-name $LambdaName `
  --environment "Variables={COURSE_ID=decision,METADATA_MODE=baked,OPENAI_API_KEY=$OpenAIKey}" `
  --region $Region

# Step 9 - Health check after deployment
if ($HealthURL -ne "<YourLambdaOrApiGatewayURL>/health") {
    Write-Host "Waiting 10 seconds for Lambda to warm up..."
    Start-Sleep -Seconds 10
    Write-Host "Checking /health endpoint at $HealthURL..."
    try {
        $response = Invoke-WebRequest -Uri $HealthURL -UseBasicParsing -TimeoutSec 10
        Write-Host "Health Check Status Code: $($response.StatusCode)"
        Write-Host "Health Check Response: $($response.Content)"
    } catch {
        Write-Warning "Health check failed: $_"
    }
} else {
    Write-Warning "No health check URL provided. Skipping automatic test."
}

Write-Host "=== Deployment Completed Successfully ==="
