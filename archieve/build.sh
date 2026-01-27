#!/usr/bin/env bash
# Build script for Render deployment

# Exit on any error
set -e

echo "Starting build process..."

# Upgrade pip first
pip install --upgrade pip

# Install only essential packages
pip install --no-cache-dir Flask==2.3.2
pip install --no-cache-dir Flask-CORS
pip install --no-cache-dir openai==1.3.0
pip install --no-cache-dir python-dotenv==1.0.0

echo "Build completed successfully!"
