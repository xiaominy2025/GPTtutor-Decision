#!/usr/bin/env python3
"""
Deployment script for AWS Lambda function with CORS fix
"""
import os
import subprocess
import zipfile
import shutil
from pathlib import Path

def create_deployment_package():
    """Create a deployment package for AWS Lambda"""
    print("📦 Creating Lambda deployment package...")
    
    # Create deployment directory
    deployment_dir = "lambda_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Copy Lambda function from root directory
    shutil.copy("lambda_function.py", f"{deployment_dir}/lambda_function.py")
    
    # Copy courses directory
    if os.path.exists("courses"):
        shutil.copytree("courses", f"{deployment_dir}/courses")
    
    # Copy requirements from root directory
    if os.path.exists("lambda_requirements.txt"):
        shutil.copy("lambda_requirements.txt", f"{deployment_dir}/requirements.txt")
    
    # Install dependencies using Docker for Linux platform compatibility
    print("📥 Installing dependencies with Docker for Linux platform...")
    docker_success = False
    
    try:
        # Check if Docker is available
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        
        # Install dependencies inside Docker container with Linux environment
        print("🐳 Using Docker to install Linux-compatible dependencies...")
        subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{os.getcwd()}:/var/task",
            "-w", "/var/task",
            "python:3.10",
            "pip", "install", "-r", "lambda_requirements.txt", "-t", deployment_dir
        ], check=True)
        
        print("✅ Dependencies installed successfully using Docker")
        docker_success = True
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Docker installation failed: {e}")
        print("💡 Fallback: Trying local pip installation...")
    
    # Fallback to local installation if Docker failed or is not available
    if not docker_success:
        try:
            print("📦 Installing dependencies locally...")
            subprocess.run([
                "pip", "install", "-r", "lambda_requirements.txt", 
                "-t", deployment_dir, "--upgrade"
            ], check=True)
            
            print("✅ Dependencies installed successfully using local pip")
            
        except subprocess.CalledProcessError as fallback_error:
            print(f"❌ Local pip installation failed: {fallback_error}")
            print("💡 Make sure you have pip and the requirements file is valid")
            return None
    
    # Create ZIP file
    zip_filename = "lambda_deployment.zip"
    print(f"🗜️ Creating {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Deployment package created: {zip_filename}")
    print(f"📊 Package size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    return zip_filename

def deploy_to_aws(zip_filename):
    """Deploy the package to AWS Lambda"""
    print("🚀 Deploying to AWS Lambda...")
    
    # Get function name from environment or use default
    function_name = os.environ.get('LAMBDA_FUNCTION_NAME', 'gpttutor-api-v1666')
    
    try:
        # Update Lambda function code
        subprocess.run([
            "aws", "lambda", "update-function-code",
            "--function-name", function_name,
            "--zip-file", f"fileb://{zip_filename}",
            "--publish"
        ], check=True)
        
        print(f"✅ Successfully deployed to Lambda function: {function_name}")
        
        # Get function URL for testing
        result = subprocess.run([
            "aws", "lambda", "get-function-url-config",
            "--function-name", function_name
        ], capture_output=True, text=True, check=True)
        
        print("🔗 Function URL (if configured):")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to deploy: {e}")
        print("💡 Make sure you have AWS CLI configured and the function exists")
        return False
    
    return True

def test_cors():
    """Test CORS functionality"""
    print("🧪 Testing CORS functionality...")
    
    # Get function URL from environment or prompt
    function_url = os.environ.get('LAMBDA_FUNCTION_URL')
    if not function_url:
        function_url = input("Enter your Lambda function URL: ").strip()
    
    if not function_url:
        print("❌ No function URL provided")
        return
    
    # Test OPTIONS request
    try:
        import requests
        
        # Test OPTIONS preflight
        response = requests.options(f"{function_url}/query", headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        print(f"OPTIONS Response Status: {response.status_code}")
        print(f"OPTIONS Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS preflight test passed!")
        else:
            print("❌ CORS preflight test failed!")
            
    except ImportError:
        print("📦 Install requests: pip install requests")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main deployment process"""
    print("🚀 Lambda Deployment Script with CORS Fix")
    print("=" * 50)
    
    # Create deployment package
    zip_filename = create_deployment_package()
    
    if not zip_filename:
        print("❌ Failed to create deployment package")
        return
    
    # Deploy to AWS
    if deploy_to_aws(zip_filename):
        print("\n🎉 Deployment successful!")
        print("\n📋 Next steps:")
        print("1. Test your frontend application")
        print("2. If CORS issues persist, run: python deploy_lambda.py --test")
        print("3. Check AWS Lambda console for function logs")
        
        # Clean up
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            print(f"🧹 Cleaned up {zip_filename}")
    else:
        print("\n❌ Deployment failed. Check AWS CLI configuration.")

if __name__ == "__main__":
    import sys
    
    if "--test" in sys.argv:
        test_cors()
    else:
        main()
