#!/usr/bin/env bash

# Build script for Render deployment
# This script handles the build process and avoids Rust compilation issues

echo "Starting build process..."

# Install system dependencies
echo "Installing system dependencies..."
apt-get update -qq
apt-get install -y build-essential

# Install Python dependencies with pre-compiled wheels
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Build completed successfully!"
