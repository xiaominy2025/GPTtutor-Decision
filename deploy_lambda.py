#!/usr/bin/env python3
"""
AWS Lambda deployment script for V1.6.6.6 API
"""
import os
import subprocess
import zipfile
import shutil

def create_lambda_package():
    """Create a deployment package for AWS Lambda"""
    print("📦 Creating Lambda deployment package...")
    
    # Create deployment directory
    deploy_dir = "lambda_deployment"
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Copy essential files
    essential_files = [
        "lambda_function.py",
        "lambda_requirements.txt",
        "courses/",
        "config.py"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            if os.path.isdir(file):
                shutil.copytree(file, os.path.join(deploy_dir, file))
            else:
                shutil.copy2(file, deploy_dir)
    
    # Install dependencies
    print("📥 Installing dependencies...")
    subprocess.run([
        "pip", "install", "-r", "lambda_requirements.txt", 
        "-t", deploy_dir, "--no-deps"
    ], check=True)
    
    # Create ZIP file
    zip_name = "lambda_deployment.zip"
    print(f"🗜️ Creating {zip_name}...")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Lambda package created: {zip_name}")
    print(f"📊 Package size: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB")
    
    return zip_name

def deploy_to_aws_lambda(zip_name, function_name="gpttutor-api-v1666"):
    """Deploy to AWS Lambda using AWS CLI"""
    print(f"🚀 Deploying to AWS Lambda function: {function_name}")
    
    try:
        # Update function code
        subprocess.run([
            "aws", "lambda", "update-function-code",
            "--function-name", function_name,
            "--zip-file", f"fileb://{zip_name}"
        ], check=True)
        
        print("✅ Lambda function updated successfully!")
        
        # Get function URL
        result = subprocess.run([
            "aws", "lambda", "get-function-url-config",
            "--function-name", function_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🌐 Function URL available")
        else:
            print("⚠️ Function URL not configured - you may need to create one")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print("💡 Make sure you have AWS CLI configured and the function exists")
        return False
    
    return True

def create_function_url(function_name="gpttutor-api-v1666"):
    """Create function URL for HTTP access"""
    print(f"🔗 Creating function URL for {function_name}...")
    
    try:
        subprocess.run([
            "aws", "lambda", "create-function-url-config",
            "--function-name", function_name,
            "--auth-type", "NONE",
            "--cors", '{"AllowCredentials":false,"AllowHeaders":["*"],"AllowMethods":["*"],"AllowOriginUrls":["*"],"ExposeHeaders":["*"],"MaxAge":0}'
        ], check=True)
        
        print("✅ Function URL created successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Function URL creation failed: {e}")
        print("💡 URL might already exist or function doesn't exist")

def main():
    """Main deployment process"""
    print("🚀 AWS Lambda Deployment for V1.6.6.6 API")
    print("=" * 50)
    
    # Create deployment package
    zip_name = create_lambda_package()
    
    # Deploy to AWS Lambda
    function_name = "gpttutor-api-v1666"
    if deploy_to_aws_lambda(zip_name, function_name):
        print("\n🎉 Deployment completed successfully!")
        print(f"📋 Next steps:")
        print(f"   1. Configure API Gateway (if needed)")
        print(f"   2. Set environment variables in Lambda console")
        print(f"   3. Test the endpoints")
        print(f"   4. Update your frontend to use the new API URL")
    else:
        print("\n❌ Deployment failed!")
        print("💡 Check your AWS credentials and function configuration")

if __name__ == "__main__":
    main()
