# ================================
# API Gateway Setup for api.engentlabs.com
# ================================

param (
    [string]$Region = "us-east-2",
    [string]$AccountId = "771049112957",
    [string]$LambdaFunctionName = "engent-v1666-img",
    [string]$DomainName = "api.engentlabs.com",
    [string]$CertificateArn = "arn:aws:acm:us-east-2:771049112957:certificate/ddf85db3-53d6-4e85-b17a-e3973946899e"
)

Write-Host "🚀 === API Gateway Setup for $DomainName ===" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "Account: $AccountId" -ForegroundColor Yellow
Write-Host "Lambda: $LambdaFunctionName" -ForegroundColor Yellow

# ================================
# STEP 1: Check Certificate Status
# ================================

Write-Host "`n🔍 Checking certificate status..." -ForegroundColor Green
try {
    $certStatus = aws acm describe-certificate --certificate-arn $CertificateArn --region $Region --query 'Certificate.Status' --output text
    Write-Host "Certificate Status: $certStatus" -ForegroundColor Yellow
    
    if ($certStatus -eq "PENDING_VALIDATION") {
        Write-Host "⚠️ Certificate is still pending validation" -ForegroundColor Yellow
        Write-Host "You need to add this DNS record to your domain:" -ForegroundColor Cyan
        Write-Host "Name: _a46244dcf4e0fbc10716e3c807aac617.api.engentlabs.com." -ForegroundColor White
        Write-Host "Type: CNAME" -ForegroundColor White
        Write-Host "Value: _5fd66680e94a17caf620f779fc0e5778.xlfgrmvvlj.acm-validations.aws." -ForegroundColor White
        Write-Host "`n⏳ Please add this DNS record and wait for validation to complete..." -ForegroundColor Yellow
        Write-Host "You can check status with: aws acm describe-certificate --certificate-arn $CertificateArn --region $Region" -ForegroundColor Gray
        exit 1
    } elseif ($certStatus -eq "ISSUED") {
        Write-Host "✅ Certificate is issued and ready!" -ForegroundColor Green
    } else {
        Write-Host "❌ Certificate status: $certStatus" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Error "❌ Failed to check certificate status: $_"
    exit 1
}

# ================================
# STEP 2: Create API Gateway
# ================================

Write-Host "`n🌐 Creating API Gateway..." -ForegroundColor Green
try {
    $apiId = aws apigateway create-rest-api --name "engent-v1666-api" --description "API Gateway for engentlabs.com backend" --region $Region --query 'id' --output text
    Write-Host "✅ API Gateway created with ID: $apiId" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to create API Gateway: $_"
    exit 1
}

# ================================
# STEP 3: Get Root Resource ID
# ================================

Write-Host "`n🔍 Getting root resource..." -ForegroundColor Green
try {
    $rootResourceId = aws apigateway get-resources --rest-api-id $apiId --region $Region --query 'items[?path==`/`].id' --output text
    Write-Host "✅ Root resource ID: $rootResourceId" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to get root resource: $_"
    exit 1
}

# ================================
# STEP 4: Create Proxy Resource
# ================================

Write-Host "`n🔧 Creating proxy resource..." -ForegroundColor Green
try {
    $proxyResourceId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rootResourceId --path-part "{proxy+}" --region $Region --query 'id' --output text
    Write-Host "✅ Proxy resource created with ID: $proxyResourceId" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to create proxy resource: $_"
    exit 1
}

# ================================
# STEP 5: Create ANY Method
# ================================

Write-Host "`n🔧 Creating ANY method..." -ForegroundColor Green
try {
    aws apigateway put-method --rest-api-id $apiId --resource-id $proxyResourceId --http-method ANY --authorization-type NONE --region $Region
    Write-Host "✅ ANY method created" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to create ANY method: $_"
    exit 1
}

# ================================
# STEP 6: Create Integration
# ================================

Write-Host "`n🔗 Creating Lambda integration..." -ForegroundColor Green
try {
    $lambdaUri = "arn:aws:apigateway:$Region`:lambda:path/2015-03-31/functions/arn:aws:lambda:$Region`:$AccountId`:function:$LambdaFunctionName/invocations"
    
    aws apigateway put-integration --rest-api-id $apiId --resource-id $proxyResourceId --http-method ANY --type AWS_PROXY --integration-http-method POST --uri $lambdaUri --region $Region
    Write-Host "✅ Lambda integration created" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to create Lambda integration: $_"
    exit 1
}

# ================================
# STEP 7: Add Lambda Permission
# ================================

Write-Host "`n🔐 Adding Lambda permission..." -ForegroundColor Green
try {
    $sourceArn = "arn:aws:execute-api:$Region`:$AccountId`:$apiId/*/*/{proxy+}"
    aws lambda add-permission --function-name $LambdaFunctionName --statement-id apigateway-proxy --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn $sourceArn --region $Region 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Lambda permission added" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Lambda permission may already exist" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Lambda permission setup failed (may already exist): $_" -ForegroundColor Yellow
}

# ================================
# STEP 8: Deploy API
# ================================

Write-Host "`n🚀 Deploying API..." -ForegroundColor Green
try {
    aws apigateway create-deployment --rest-api-id $apiId --stage-name prod --region $Region
    Write-Host "✅ API deployed to prod stage" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to deploy API: $_"
    exit 1
}

# ================================
# STEP 9: Create Custom Domain
# ================================

Write-Host "`n🌐 Creating custom domain..." -ForegroundColor Green
try {
    aws apigateway create-domain-name --domain-name $DomainName --certificate-arn $CertificateArn --endpoint-configuration "types=REGIONAL" --region $Region
    Write-Host "✅ Custom domain created" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to create custom domain: $_"
    exit 1
}

# ================================
# STEP 10: Create Base Path Mapping
# ================================

Write-Host "`n🔗 Creating base path mapping..." -ForegroundColor Green
try {
    aws apigateway create-base-path-mapping --domain-name $DomainName --rest-api-id $apiId --stage prod --region $Region
    Write-Host "✅ Base path mapping created" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to create base path mapping: $_"
    exit 1
}

# ================================
# SUMMARY
# ================================

Write-Host "`n🎉 === API Gateway Setup Complete ===" -ForegroundColor Cyan
Write-Host "API Gateway ID: $apiId" -ForegroundColor Yellow
Write-Host "Custom Domain: $DomainName" -ForegroundColor Yellow
Write-Host "Lambda Function: $LambdaFunctionName" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow

Write-Host "`n📋 Next Steps:" -ForegroundColor Green
Write-Host "1. Add DNS record: $DomainName → API Gateway endpoint" -ForegroundColor White
Write-Host "2. Test the API: https://$DomainName/health" -ForegroundColor White
Write-Host "3. Update frontend to use: https://$DomainName" -ForegroundColor White

Write-Host "`nTo get the API Gateway endpoint:" -ForegroundColor Cyan
