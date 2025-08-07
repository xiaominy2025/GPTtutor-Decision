#!/usr/bin/env bash
# Build script for Render deployment

# Exit on any error
set -e

echo "Starting build process..."

# Upgrade pip first
pip install --upgrade pip

# Install system dependencies if needed
# apt-get update && apt-get install -y build-essential

# Install Python packages with specific flags for better compatibility
pip install --no-cache-dir --upgrade setuptools wheel

# Install packages one by one to better handle errors
pip install --no-cache-dir Flask==2.3.2
pip install --no-cache-dir sentence-transformers==2.2.2
pip install --no-cache-dir torch>=1.9.0
pip install --no-cache-dir transformers>=4.21.0
pip install --no-cache-dir "tokenizers>=0.13.0,<0.15.0"
pip install --no-cache-dir numpy>=1.21.0
pip install --no-cache-dir pytest>=7.0.0
pip install --no-cache-dir python-dotenv>=0.19.0
pip install --no-cache-dir openai>=1.0.0
pip install --no-cache-dir faiss-cpu>=1.7.0
pip install --no-cache-dir spacy>=3.0.0
pip install --no-cache-dir scikit-learn>=1.0.0
pip install --no-cache-dir Flask-CORS
pip install --no-cache-dir huggingface-hub==0.15.1

echo "Build completed successfully!"
