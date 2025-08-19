#!/usr/bin/env python3
"""
Deployment script for simple Lambda function
"""
import os
import subprocess
import zipfile
import shutil

def create_simple_deployment_package():
    """Create a deployment package for simple Lambda function"""
    print("📦 Creating simple Lambda deployment package...")
    
    # Create deployment directory
    deployment_dir = "lambda_simple"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Copy simple Lambda function
    shutil.copy("lambda_function_simple.py", f"{deployment_dir}/lambda_function.py")
    
    # Create ZIP file
    zip_filename = "lambda_simple.zip"
    print(f"🗜️ Creating {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Simple deployment package created: {zip_filename}")
    return zip_filename

def deploy_simple_to_aws(zip_filename):
    """Deploy the simple package to AWS Lambda"""
    print("🚀 Deploying simple Lambda function...")
    
    function_name = "gpttutor-api-v1666"
    
    try:
        # Update Lambda function code
        subprocess.run([
            "aws", "lambda", "update-function-code",
            "--function-name", function_name,
            "--zip-file", f"fileb://{zip_filename}",
            "--publish"
        ], check=True)
        
        print(f"✅ Successfully deployed simple function to: {function_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to deploy: {e}")
        return False

def test_simple_function():
    """Test the simple Lambda function"""
    print("🧪 Testing simple Lambda function...")
    
    function_url = "https://suu42zea6k74bqdogirjfhh2p40vflgq.lambda-url.us-east-2.on.aws"
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get(f"{function_url}/health")
        print(f"Health Status: {response.status_code}")
        print(f"Health Response: {response.text}")
        
        # Test OPTIONS preflight
        response = requests.options(f"{function_url}/query", headers={
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        print(f"OPTIONS Status: {response.status_code}")
        print(f"OPTIONS Headers: {dict(response.headers)}")
        
        # Test POST request
        response = requests.post(f"{function_url}/query", 
                               json={"query": "test query", "course_id": "decision"},
                               headers={'Content-Type': 'application/json'})
        print(f"POST Status: {response.status_code}")
        print(f"POST Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Simple function test PASSED!")
            return True
        else:
            print("❌ Simple function test FAILED!")
            return False
            
    except ImportError:
        print("📦 Install requests: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main deployment process"""
    print("🚀 Simple Lambda Deployment")
    print("=" * 40)
    
    # Create deployment package
    zip_filename = create_simple_deployment_package()
    
    # Deploy to AWS
    if deploy_simple_to_aws(zip_filename):
        print("\n🎉 Simple deployment successful!")
        print("\n📋 Testing function...")
        
        # Wait a moment for deployment to complete
        import time
        time.sleep(5)
        
        # Test the function
        if test_simple_function():
            print("\n✅ CORS fix is working! Your frontend should now work.")
        else:
            print("\n❌ Function test failed. Check AWS Lambda console for logs.")
        
        # Clean up
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            print(f"🧹 Cleaned up {zip_filename}")
    else:
        print("\n❌ Deployment failed. Check AWS CLI configuration.")

if __name__ == "__main__":
    main()
