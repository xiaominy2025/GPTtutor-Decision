# AWS Lambda Deployment for V1.6.6.6 API

## 🚀 Overview

This is a complete AWS Lambda deployment solution for your V1.6.6.6 API. It provides all the functionality of your Flask API but runs serverlessly on AWS Lambda.

## ✅ Features

- **All V1.6.6.6 endpoints** - Health check, query processing, course metadata
- **Serverless** - Pay only for requests
- **Auto-scaling** - Handles traffic spikes automatically
- **Cost-effective** - Free tier available
- **Easy deployment** - Simple ZIP and upload process

## 📁 Files

- `lambda_function.py` - Main Lambda function with all endpoints
- `lambda_requirements.txt` - Minimal dependencies for Lambda
- `deploy_lambda.py` - Automated deployment script
- `LAMBDA_DEPLOYMENT_README.md` - This file

## 🛠️ Prerequisites

1. **AWS Account** - Sign up at aws.amazon.com
2. **AWS CLI** - Install and configure with your credentials
3. **Python 3.11** - For local development and packaging

## 📦 Deployment Steps

### Step 1: Install AWS CLI
```bash
# Windows
pip install awscli

# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### Step 2: Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
```

### Step 3: Create Lambda Function
```bash
# Create the Lambda function (run once)
aws lambda create-function \
  --function-name gpttutor-api-v1666 \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_deployment.zip
```

### Step 4: Deploy
```bash
# Run the deployment script
python deploy_lambda.py
```

## 🔧 Configuration

### Environment Variables
Set these in the Lambda console:
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.3
FLASK_DEBUG=False
```

### IAM Role Permissions
Your Lambda execution role needs:
- Basic Lambda execution permissions
- CloudWatch Logs permissions
- Any additional permissions for your specific needs

## 🌐 API Endpoints

Once deployed, your Lambda function will have these endpoints:

- `GET /health` - Health check
- `POST /query` - Process queries
- `GET /courses` - List available courses
- `GET /courses/{course_id}/config` - Get course configuration
- `GET /api/course/{course_id}` - Get course metadata
- `GET /stats` - Get usage statistics
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `GET /test` - Test endpoint

## 💰 Cost Estimation

**Free Tier (first 1M requests/month):**
- 1M requests: $0
- 400,000 GB-seconds: $0

**After free tier:**
- $0.20 per 1M requests
- $0.0000166667 per GB-second

**Typical usage (1000 requests/day):**
- ~$0.60/month

## 🔄 Updating the Function

To update your Lambda function:

```bash
# Just run the deployment script again
python deploy_lambda.py
```

## 🧪 Testing

### Local Testing
```bash
# Test locally
python lambda_function.py
```

### Lambda Testing
```bash
# Test the deployed function
aws lambda invoke \
  --function-name gpttutor-api-v1666 \
  --payload '{"path": "/health", "httpMethod": "GET"}' \
  response.json
```

## 🚨 Troubleshooting

### Common Issues

1. **Function not found**
   - Make sure the function name exists
   - Check your AWS region

2. **Permission denied**
   - Verify your AWS credentials
   - Check IAM role permissions

3. **Package too large**
   - Remove unnecessary files
   - Use Lambda layers for large dependencies

4. **Timeout errors**
   - Increase Lambda timeout (max 15 minutes)
   - Optimize your code

### Logs
```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/gpttutor-api-v1666
```

## 🔗 Function URL

After deployment, you can create a function URL for direct HTTP access:

```bash
aws lambda create-function-url-config \
  --function-name gpttutor-api-v1666 \
  --auth-type NONE \
  --cors '{"AllowCredentials":false,"AllowHeaders":["*"],"AllowMethods":["*"],"AllowOriginUrls":["*"],"ExposeHeaders":["*"],"MaxAge":0}'
```

## 📈 Scaling

Lambda automatically scales based on demand:
- **Concurrent executions**: Up to 1000 by default
- **Request rate**: Unlimited
- **Memory**: 128MB to 10GB
- **Timeout**: Up to 15 minutes

## 🔐 Security

- **Function URL**: Public access (no authentication)
- **API Gateway**: Can add authentication
- **VPC**: Can run in private VPC if needed
- **Environment variables**: Encrypted at rest

## 🎯 Next Steps

1. **Deploy the function** using the deployment script
2. **Set environment variables** in Lambda console
3. **Test the endpoints** to ensure everything works
4. **Update your frontend** to use the new API URL
5. **Monitor usage** in CloudWatch
6. **Add authentication** if needed (API Gateway)

## 📞 Support

If you encounter issues:
1. Check CloudWatch logs for errors
2. Verify AWS credentials and permissions
3. Test locally first
4. Check Lambda function configuration

---

**Happy deploying! 🚀**
