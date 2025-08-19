# GPTTutor Frontend Deployment Script
# Deploys the frontend to S3 and CloudFront

param(
    [string]$BucketName = "engentlab.com",
    [string]$DistributionId = "",
    [string]$Region = "us-east-1",
    [switch]$CreateResources = $false,
    [switch]$UpdateDNS = $false
)

Write-Host "🚀 GPTTutor Frontend Deployment" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if AWS CLI is installed
try {
    aws --version | Out-Null
    Write-Host "✅ AWS CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Check if required files exist
$requiredFiles = @("index.html", "app.js")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Required file not found: $file" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ All required files found" -ForegroundColor Green

# Function to create S3 bucket
function Create-S3Bucket {
    param([string]$BucketName, [string]$Region)
    
    Write-Host "📦 Creating S3 bucket: $BucketName" -ForegroundColor Yellow
    
    try {
        # Create bucket
        aws s3 mb "s3://$BucketName" --region $Region
        
        # Configure bucket for static website hosting
        $websiteConfig = @{
            IndexDocument = @{Suffix = "index.html"}
            ErrorDocument = @{Key = "index.html"}
        } | ConvertTo-Json
        
        aws s3api put-bucket-website --bucket $BucketName --website-configuration $websiteConfig
        
        # Set bucket policy for public read access
        $bucketPolicy = @{
            Version = "2012-10-17"
            Statement = @(
                @{
                    Sid = "PublicReadGetObject"
                    Effect = "Allow"
                    Principal = "*"
                    Action = "s3:GetObject"
                    Resource = "arn:aws:s3:::$BucketName/*"
                }
            )
        } | ConvertTo-Json
        
        aws s3api put-bucket-policy --bucket $BucketName --policy $bucketPolicy
        
        Write-Host "✅ S3 bucket created and configured" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to create S3 bucket: $_" -ForegroundColor Red
        return $false
    }
}

# Function to create CloudFront distribution
function Create-CloudFrontDistribution {
    param([string]$BucketName, [string]$Region)
    
    Write-Host "☁️ Creating CloudFront distribution" -ForegroundColor Yellow
    
    try {
        # Create distribution configuration
        $distributionConfig = @{
            CallerReference = (Get-Date).ToString("yyyyMMddHHmmss")
            Comment = "GPTTutor Frontend Distribution"
            Origins = @{
                Quantity = 1
                Items = @(
                    @{
                        Id = "S3-$BucketName"
                        DomainName = "$BucketName.s3.$Region.amazonaws.com"
                        S3OriginConfig = @{
                            OriginAccessIdentity = ""
                        }
                    }
                )
            }
            DefaultCacheBehavior = @{
                TargetOriginId = "S3-$BucketName"
                ViewerProtocolPolicy = "redirect-to-https"
                AllowedMethods = @{
                    Quantity = 2
                    Items = @("GET", "HEAD")
                    CachedMethods = @{
                        Quantity = 2
                        Items = @("GET", "HEAD")
                    }
                }
                ForwardedValues = @{
                    QueryString = $false
                    Cookies = @{
                        Forward = "none"
                    }
                }
                MinTTL = 0
                DefaultTTL = 86400
                MaxTTL = 31536000
            }
            Enabled = $true
            PriceClass = "PriceClass_100"
        } | ConvertTo-Json -Depth 10
        
        # Create distribution
        $result = aws cloudfront create-distribution --distribution-config $distributionConfig | ConvertFrom-Json
        
        $distributionId = $result.Distribution.Id
        $domainName = $result.Distribution.DomainName
        
        Write-Host "✅ CloudFront distribution created" -ForegroundColor Green
        Write-Host "   Distribution ID: $distributionId" -ForegroundColor Cyan
        Write-Host "   Domain: $domainName" -ForegroundColor Cyan
        
        return @{
            DistributionId = $distributionId
            DomainName = $domainName
        }
    } catch {
        Write-Host "❌ Failed to create CloudFront distribution: $_" -ForegroundColor Red
        return $null
    }
}

# Function to request ACM certificate
function Request-ACMCertificate {
    param([string]$DomainName, [string]$Region)
    
    Write-Host "🔒 Requesting ACM certificate for: $DomainName" -ForegroundColor Yellow
    
    try {
        $certificateArn = aws acm request-certificate `
            --domain-name $DomainName `
            --subject-alternative-names "*.$DomainName" `
            --region $Region `
            --query 'CertificateArn' `
            --output text
        
        Write-Host "✅ Certificate requested: $certificateArn" -ForegroundColor Green
        Write-Host "   Note: Certificate validation may take 5-30 minutes" -ForegroundColor Yellow
        
        return $certificateArn
    } catch {
        Write-Host "❌ Failed to request certificate: $_" -ForegroundColor Red
        return $null
    }
}

# Function to upload files to S3
function Upload-ToS3 {
    param([string]$BucketName)
    
    Write-Host "📤 Uploading files to S3" -ForegroundColor Yellow
    
    try {
        # Upload files with cache headers
        aws s3 cp index.html "s3://$BucketName/" --cache-control "max-age=300" --content-type "text/html"
        aws s3 cp app.js "s3://$BucketName/" --cache-control "max-age=3600" --content-type "application/javascript"
        
        Write-Host "✅ Files uploaded successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to upload files: $_" -ForegroundColor Red
        return $false
    }
}

# Function to invalidate CloudFront cache
function Invalidate-CloudFrontCache {
    param([string]$DistributionId)
    
    Write-Host "🔄 Invalidating CloudFront cache" -ForegroundColor Yellow
    
    try {
        $invalidation = aws cloudfront create-invalidation `
            --distribution-id $DistributionId `
            --paths "/*" `
            --query 'Invalidation.Id' `
            --output text
        
        Write-Host "✅ Cache invalidation created: $invalidation" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to invalidate cache: $_" -ForegroundColor Red
        return $false
    }
}

# Main deployment logic
if ($CreateResources) {
    Write-Host "🔧 Creating AWS resources..." -ForegroundColor Yellow
    
    # Create S3 bucket
    if (-not (Create-S3Bucket -BucketName $BucketName -Region $Region)) {
        exit 1
    }
    
    # Request ACM certificate
    $certificateArn = Request-ACMCertificate -DomainName $BucketName -Region $Region
    if (-not $certificateArn) {
        Write-Host "⚠️ Certificate request failed, but continuing..." -ForegroundColor Yellow
    }
    
    # Create CloudFront distribution
    $distribution = Create-CloudFrontDistribution -BucketName $BucketName -Region $Region
    if (-not $distribution) {
        exit 1
    }
    
    $DistributionId = $distribution.DistributionId
    
    Write-Host "🎉 AWS resources created successfully!" -ForegroundColor Green
    Write-Host "   Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Wait for ACM certificate validation (5-30 minutes)" -ForegroundColor White
    Write-Host "   2. Update CloudFront distribution with certificate" -ForegroundColor White
    Write-Host "   3. Configure DNS records" -ForegroundColor White
    Write-Host "   4. Run this script again without -CreateResources" -ForegroundColor White
}

# Upload files to S3
if (-not (Upload-ToS3 -BucketName $BucketName)) {
    exit 1
}

# Invalidate CloudFront cache if distribution ID is provided
if ($DistributionId) {
    if (-not (Invalidate-CloudFrontCache -DistributionId $DistributionId)) {
        Write-Host "⚠️ Cache invalidation failed, but files are uploaded" -ForegroundColor Yellow
    }
}

# Display results
Write-Host ""
Write-Host "🎯 Deployment Summary" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "S3 Bucket: $BucketName" -ForegroundColor White
Write-Host "S3 Website URL: http://$BucketName.s3-website-$Region.amazonaws.com" -ForegroundColor White

if ($DistributionId) {
    Write-Host "CloudFront Distribution ID: $DistributionId" -ForegroundColor White
    Write-Host "CloudFront Domain: https://$DistributionId.cloudfront.net" -ForegroundColor White
}

Write-Host ""
Write-Host "✅ Frontend deployment completed!" -ForegroundColor Green

if ($UpdateDNS) {
    Write-Host ""
    Write-Host "📝 DNS Configuration Required:" -ForegroundColor Yellow
    Write-Host "   Add CNAME record: $BucketName -> $DistributionId.cloudfront.net" -ForegroundColor White
    Write-Host "   Or A record with CloudFront alias" -ForegroundColor White
}

Write-Host ""
Write-Host "🔗 Test URLs:" -ForegroundColor Cyan
Write-Host "   S3: http://$BucketName.s3-website-$Region.amazonaws.com" -ForegroundColor White
if ($DistributionId) {
    Write-Host "   CloudFront: https://$DistributionId.cloudfront.net" -ForegroundColor White
}
