#!/usr/bin/env bash
# Build script for Render deployment

# Exit on any error
set -e

echo "Starting build process..."

# Upgrade pip first
pip install --upgrade pip

# Install setuptools and wheel first
pip install --no-cache-dir setuptools==68.0.0 wheel==0.41.2

# Install packages with specific flags to avoid compilation
pip install --no-cache-dir --only-binary=all Flask==2.3.2
pip install --no-cache-dir --only-binary=all sentence-transformers==2.2.2
pip install --no-cache-dir --only-binary=all torch==2.8.0
pip install --no-cache-dir --only-binary=all transformers==4.28.1
pip install --no-cache-dir --only-binary=all tokenizers==0.12.1
pip install --no-cache-dir --only-binary=all numpy==1.24.3
pip install --no-cache-dir --only-binary=all pytest==7.4.0
pip install --no-cache-dir --only-binary=all python-dotenv==1.0.0
pip install --no-cache-dir --only-binary=all openai==1.3.0
pip install --no-cache-dir --only-binary=all faiss-cpu==1.7.4
pip install --no-cache-dir --only-binary=all scikit-learn==1.3.0
pip install --no-cache-dir --only-binary=all Flask-CORS
pip install --no-cache-dir --only-binary=all huggingface_hub==0.15.1

echo "Build completed successfully!"
