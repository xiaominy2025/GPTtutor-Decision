param(
  [string]$Region    = "us-east-2",
  [string]$AccountId = "771049112957",
  [string]$RepoName  = "engent-labs-v1666",
  [string]$ImageTag  = "latest",
  [string]$LambdaZipName = "gpttutor-api-v1666",      # existing Zip function (if present)
  [string]$LambdaImgName = "gpttutor-api-v1666-img",  # image-based function we manage
  [string]$ApiName   = "gpttutor-api-v1666",
  [string]$StageName = "prod",
  [switch]$SkipApiGateway = $true
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$ProgressPreference = "SilentlyContinue"

function Info($m){ Write-Host "== $m" }

# --- Resolve ECR URI ---
$EcrUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$RepoName"

# --- Print detected routes (no code changes) ---
try {
  Info "Route discovery from api_server.app"
  $py = @"
import importlib, json, sys
m = importlib.import_module('api_server')
app = getattr(m, 'app', None)
if not app:
    raise SystemExit('api_server.app not found')
routes = []
for r in app.url_map.iter_rules():
    routes.append(dict(rule=str(r), methods=sorted([mm for mm in r.methods if mm not in ('HEAD','OPTIONS')])))
print(json.dumps(sorted(routes, key=lambda x: x['rule']), indent=2))
"@
  $tmp = Join-Path $env:TEMP "route_$([guid]::NewGuid()).py"
  Set-Content -Path $tmp -Value $py -Encoding UTF8
  try { & python $tmp } finally { Remove-Item $tmp -ErrorAction SilentlyContinue }
} catch { Write-Warning $_.Exception.Message }

# --- ECR: ensure repo + login ---
Info "ECR: ensure repo and login"
try {
    aws ecr describe-repositories --repository-names $RepoName --region $Region 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Repository not found" }
} catch {
    aws ecr create-repository --repository-name $RepoName --image-scanning-configuration scanOnPush=true --region $Region | Out-Null
}
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com" | Out-Null

# --- Build & push image as linux/amd64, WITHOUT BuildKit (no attestation/index) ---
Info "Docker build (linux/amd64; BuildKit OFF)"
$env:DOCKER_BUILDKIT = "0"
$env:DOCKER_DEFAULT_PLATFORM = "linux/amd64"
docker build --platform linux/amd64 -t "$EcrUri`:$ImageTag" .
if ($LASTEXITCODE -ne 0) { throw "docker build failed: $LASTEXITCODE" }

Info "Docker push"
docker push "$EcrUri`:$ImageTag"
if ($LASTEXITCODE -ne 0) { throw "docker push failed: $LASTEXITCODE" }

Info "Verify manifest"
docker manifest inspect "$EcrUri`:$ImageTag" | Write-Host

# --- Ensure image-based Lambda exists/updated ---
Info "Ensure image-based Lambda function"
$imgExists = $false
try {
  $cfg = aws lambda get-function-configuration --function-name $LambdaImgName --region $Region | ConvertFrom-Json
  if ($cfg) { $imgExists = $true }
} catch { }

if (-not $imgExists) {
  # If a Zip function exists, reuse its role (and VPC if any)
  $roleArn = $null
  $vpcArgs = @()
  try {
    $old = aws lambda get-function-configuration --function-name $LambdaZipName --region $Region | ConvertFrom-Json
    if ($old) {
      $roleArn = $old.Role
      if ($old.VpcConfig -and $old.VpcConfig.SubnetIds -and $old.VpcConfig.SecurityGroupIds) {
        $subnets = ($old.VpcConfig.SubnetIds -join ',')
        $sgs     = ($old.VpcConfig.SecurityGroupIds -join ',')
        $vpcArgs = @("--vpc-config", "SubnetIds=$subnets,SecurityGroupIds=$sgs")
      }
    }
  } catch { }

  if (-not $roleArn) {
    throw "Cannot determine IAM role. Ensure $LambdaZipName exists, or provide a role to create $LambdaImgName."
  }

  Info "Create image-based function: $LambdaImgName"
  $args = @(
    "create-function",
    "--function-name", $LambdaImgName,
    "--package-type", "Image",
    "--code", "ImageUri=$EcrUri`:$ImageTag",
    "--role", $roleArn,
    "--architectures", "x86_64",
    "--timeout", "120",
    "--memory-size", "2048",
    "--region", $Region
  ) + $vpcArgs
  aws lambda @args | Out-Null
  aws lambda wait function-active --function-name $LambdaImgName --region $Region
}

# Always attach the fresh image + set sane limits
Info "Update image + config (timeout/memory)"
aws lambda update-function-code --function-name $LambdaImgName --image-uri "$EcrUri`:$ImageTag" --region $Region | Out-Null
aws lambda update-function-configuration --function-name $LambdaImgName --timeout 120 --memory-size 2048 --region $Region | Out-Null
aws lambda wait function-updated --function-name $LambdaImgName --region $Region

# --- Ensure runtime env vars (merge with existing) ---
Info "Set runtime environment variables"
$existing = aws lambda get-function-configuration --function-name $LambdaImgName --region $Region --query "Environment.Variables" --output json | ConvertFrom-Json
$desired = [ordered]@{
  OPENAI_API_KEY = $existing.OPENAI_API_KEY  # keep whatever is already set
  COURSE_DIR     = "/var/task/courses"
  DEFAULT_COURSE = "decision"
  LOG_LEVEL      = "INFO"
}
$kv = ($desired.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ','
$varsArg = "Variables={$kv}"

aws lambda update-function-configuration --function-name $LambdaImgName --region $Region --environment "$varsArg" | Out-Null
aws lambda wait function-updated --function-name $LambdaImgName --region $Region

# --- Function URL (for quick smoke test) ---
Info "Ensure Function URL (public) and test /health"
$furlObj = $null
try { $furlObj = aws lambda get-function-url-config --function-name $LambdaImgName --region $Region | ConvertFrom-Json } catch { }
if (-not $furlObj) {
  aws lambda create-function-url-config --function-name $LambdaImgName --auth-type NONE --region $Region | Out-Null
  aws lambda add-permission `
    --function-name $LambdaImgName `
    --statement-id "AllowPublicFunctionUrlInvoke" `
    --action lambda:InvokeFunctionUrl `
    --principal "*" `
    --function-url-auth-type NONE `
    --region $Region | Out-Null
  $furlObj = aws lambda get-function-url-config --function-name $LambdaImgName --region $Region | ConvertFrom-Json
}
$FunctionUrl = $furlObj.FunctionUrl
Write-Host "Function URL: $FunctionUrl"
try { Invoke-WebRequest "$FunctionUrl/health" -UseBasicParsing | Out-Null; Write-Host "FunctionURL /health OK" } catch { Write-Warning "FunctionURL /health failed: $($_.Exception.Message)" }

if (-not $SkipApiGateway) {
  # --- API Gateway v2 (HTTP API) creation/wiring ---
  Info "HTTP API v2: create or update and wire to Lambda"
  $api = $null
  try {
    $api = aws apigatewayv2 get-apis --region $Region | ConvertFrom-Json | Select-Object -ExpandProperty Items | Where-Object { $_.Name -eq $ApiName }
  } catch { }
  if (-not $api) {
    $api = aws apigatewayv2 create-api --name $ApiName --protocol-type HTTP --region $Region | ConvertFrom-Json
    Write-Host "Created HTTP API: $($api.ApiId)"
  }
  $ApiId = $api.ApiId

  # Integration (AWS_PROXY, payload v2.0)
  $fnArn = (aws lambda get-function --function-name $LambdaImgName --region $Region --query Configuration.FunctionArn --output text)
  $integration = $null
  try {
    $integration = aws apigatewayv2 get-integrations --api-id $ApiId --region $Region | ConvertFrom-Json | Select-Object -ExpandProperty Items | Where-Object { $_.IntegrationUri -like "*$fnArn*" }
  } catch { }
  if (-not $integration) {
    $integration = aws apigatewayv2 create-integration `
      --api-id $ApiId `
      --integration-type AWS_PROXY `
      --integration-uri "arn:aws:apigateway:$Region:lambda:path/2015-03-31/functions/$fnArn/invocations" `
      --payload-format-version "2.0" `
      --timeout-in-millis 30000 `
      --region $Region | ConvertFrom-Json
    Write-Host "Created integration: $($integration.IntegrationId)"
  }
  $IntegrationId = $integration.IntegrationId

  # Permission for API Gateway to invoke Lambda (idempotent try)
  try {
    aws lambda add-permission `
      --function-name $LambdaImgName `
      --statement-id "AllowApiGwInvoke-$ApiId" `
      --action lambda:InvokeFunction `
      --principal apigateway.amazonaws.com `
      --region $Region | Out-Null
  } catch { }

  # Routes: ANY / and ANY /{proxy+}
  function Ensure-Route {
    param([string]$RouteKey)
    $routes = aws apigatewayv2 get-routes --api-id $ApiId --region $Region | ConvertFrom-Json
    $existing = $routes.Items | Where-Object { $_.RouteKey -eq $RouteKey }
    if (-not $existing) {
      aws apigatewayv2 create-route --api-id $ApiId --route-key $RouteKey --target "integrations/$IntegrationId" --region $Region | Out-Null
      Write-Host "Created route: $RouteKey"
    }
  }
  Ensure-Route "ANY /"
  Ensure-Route "ANY /{proxy+}"

  # Stage: prod (auto-deploy ON)
  $stage = $null
  try { $stage = aws apigatewayv2 get-stage --api-id $ApiId --stage-name $StageName --region $Region | ConvertFrom-Json } catch { }
  if (-not $stage) {
    aws apigatewayv2 create-stage --api-id $ApiId --stage-name $StageName --auto-deploy --region $Region | Out-Null
    Write-Host "Created stage: $StageName"
  } else {
    aws apigatewayv2 update-stage --api-id $ApiId --stage-name $StageName --auto-deploy --region $Region | Out-Null
  }

  # Print final API URL and smoke test
  $ApiEndpoint = (aws apigatewayv2 get-api --api-id $ApiId --region $Region --query ApiEndpoint --output text)
  $BASE = "$ApiEndpoint/$StageName"
  Write-Host "HTTP API Invoke URL: $BASE"

  function Try-Get { param($Url) try { $r=Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing; Write-Host "OK $($r.StatusCode): $Url" } catch { Write-Warning "FAIL: $Url - $($_.Exception.Message)" } }
  function Try-PostJson { param($Url,$Body) try { $r=Invoke-WebRequest -Uri $Url -Method POST -Headers @{ "Content-Type"="application/json" } -Body $Body -UseBasicParsing; Write-Host "OK $($r.StatusCode): $Url" } catch { Write-Warning "FAIL: $Url - $($_.Exception.Message)" } }

  Try-Get "$BASE/health"
  Try-Get "$BASE/courses"
  Try-Get "$BASE/glossary?course_id=decision"
  Try-PostJson "$BASE/query" '{"query":"quick sanity"}'

  Write-Host "=== Deployment complete ==="
  Write-Host "Image: $EcrUri`:$ImageTag"
  Write-Host "Lambda: $LambdaImgName"
  Write-Host "Function URL: $FunctionUrl"
  Write-Host "HTTP API: $BASE"
  exit 0
} else {
  Write-Host "Skipping API Gateway setup. Backend is available via Function URL only." -ForegroundColor Yellow
  Write-Host "=== Deployment complete (Function URL only) ==="
  Write-Host "Image: $EcrUri`:$ImageTag"
  Write-Host "Lambda: $LambdaImgName"
  Write-Host "Function URL: $FunctionUrl"
  exit 0
}
