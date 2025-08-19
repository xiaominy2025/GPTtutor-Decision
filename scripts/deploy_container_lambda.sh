#!/bin/bash
# Bash script to build, tag, push, and deploy Engent Labs V1.6.6.6 Backend
# 100% Feature Parity Container Lambda Deployment

set -e

# Configuration
REGION=${1:-"us-east-2"}
ACCOUNT_ID=${2:-"771049112957"}
IMAGE_TAG=${3:-"latest"}
REPO_NAME="engent-labs-backend-v1666"
IMAGE_NAME="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME"

echo "🚀 Deploying Engent Labs V1.6.6.6 Backend Container Lambda"
echo "   Region: $REGION"
echo "   Account: $ACCOUNT_ID" 
echo "   Image Tag: $IMAGE_TAG"

# Step 1: Prepare container requirements
echo "📦 Preparing container requirements..."
if [ -f "requirements_container.txt" ]; then
    cp requirements_container.txt requirements.txt
    echo "✅ Using container-specific requirements.txt"
else
    echo "⚠️  requirements_container.txt not found, using existing requirements.txt"
fi

# Step 2: Build Docker image
echo "🔨 Building Docker image..."
docker build -t $REPO_NAME .
echo "✅ Docker image built successfully"

# Step 3: Authenticate with ECR
echo "🔐 Authenticating with ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
echo "✅ ECR authentication successful"

# Step 4: Create ECR repository if it doesn't exist
echo "📦 Ensuring ECR repository exists..."
if ! aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION >/dev/null 2>&1; then
    echo "📦 Creating ECR repository..."
    aws ecr create-repository --repository-name $REPO_NAME --region $REGION --image-scanning-configuration scanOnPush=true
    echo "✅ ECR repository created"
else
    echo "✅ ECR repository exists"
fi

# Step 5: Tag and push image
echo "🏷️  Tagging image..."
docker tag $REPO_NAME $IMAGE_NAME:$IMAGE_TAG

echo "⬆️  Pushing image to ECR..."
docker push $IMAGE_NAME:$IMAGE_TAG
echo "✅ Image pushed successfully"

# Step 6: Deploy CDK infrastructure
echo "🏗️  Deploying CDK infrastructure..."
cd infra

# Install CDK dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing CDK dependencies..."
    npm install -g aws-cdk
    pip install -r requirements.txt
fi

# Bootstrap CDK if needed
echo "🔧 Bootstrapping CDK..."
cdk bootstrap aws://$ACCOUNT_ID/$REGION

# Deploy stack
echo "🚀 Deploying CDK stack..."
cdk deploy --require-approval never
echo "✅ CDK stack deployed successfully"

cd ..

# Step 7: Update Lambda function with new image
echo "🔄 Updating Lambda function..."
aws lambda update-function-code \
    --function-name "engent-labs-backend-v1666" \
    --image-uri "$IMAGE_NAME:$IMAGE_TAG" \
    --region $REGION
echo "✅ Lambda function updated"

# Step 8: Wait for function to be ready
echo "⏳ Waiting for Lambda function to be ready..."
aws lambda wait function-updated --function-name "engent-labs-backend-v1666" --region $REGION
echo "✅ Lambda function is ready"

# Step 9: Get API Gateway URL
echo "🔗 Getting API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "EngentLabsBackendStack" \
    --region $REGION \
    --query "Stacks[0].Outputs[?OutputKey=='APIGatewayURL'].OutputValue" \
    --output text)

echo ""
echo "🎉 Deployment Complete!"
echo "   API Gateway URL: $API_URL"
echo "   Lambda Function: engent-labs-backend-v1666"
echo "   ECR Image: $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "🧪 Test endpoints:"
echo "   Health: GET $API_URL/health"
echo "   Query:  POST $API_URL/query"
echo "   Courses: GET $API_URL/courses"
echo "   Glossary: GET $API_URL/glossary"

echo $API_URL
