#!/bin/bash
# Build script for V1.6.6.6 Lambda Function Container
# CORS and Response Format Fixes

set -e

echo "🚀 Building V1.6.6.6 Lambda Function Container"
echo "📍 Target: engent-v1666-img:fix-cors-v1666"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found in current directory"
    exit 1
fi

echo "✅ Dockerfile found"

# Build the container
echo "🔨 Building Docker container..."
echo "   Tag: engent-v1666-img:fix-cors-v1666"
echo ""

docker build -t engent-v1666-img:fix-cors-v1666 .

# Check build result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo "📦 Container: engent-v1666-img:fix-cors-v1666"
    echo ""
    echo "🔍 Container details:"
    docker images engent-v1666-img:fix-cors-v1666
    echo ""
    echo "📋 Next steps:"
    echo "1. Test the container locally if needed"
    echo "2. Push to ECR: docker push <ecr-repo>/engent-v1666-img:fix-cors-v1666"
    echo "3. Update Lambda function with new image"
    echo "4. Run validation tests: python test_v1666_final_validation.py"
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi
