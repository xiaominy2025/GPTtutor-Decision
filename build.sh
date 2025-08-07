#!/usr/bin/env bash
# Build script for Render deployment

# Exit on any error
set -e

echo "Starting build process..."

# Upgrade pip first
pip install --upgrade pip

# Install setuptools and wheel first
pip install --no-cache-dir setuptools>=69.0.0 wheel>=0.42.0

# Install packages normally
pip install --no-cache-dir Flask==2.3.2
pip install --no-cache-dir Flask-CORS
pip install --no-cache-dir sentence-transformers==2.2.2
pip install --no-cache-dir transformers==4.28.1
pip install --no-cache-dir torch==2.8.0
pip install --no-cache-dir huggingface_hub==0.15.1
pip install --no-cache-dir openai==1.3.0
pip install --no-cache-dir pytest==7.4.0
pip install --no-cache-dir numpy==1.24.3
pip install --no-cache-dir scikit-learn==1.3.0
pip install --no-cache-dir faiss-cpu==1.7.4
pip install --no-cache-dir python-dotenv==1.0.0

echo "Build completed successfully!"
