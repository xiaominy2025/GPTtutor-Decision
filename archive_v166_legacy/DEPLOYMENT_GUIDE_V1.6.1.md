# ThinkPal Decision Coach V1.6.1 - Deployment Guide

## 🚀 Production Deployment Instructions

This guide provides step-by-step instructions for deploying ThinkPal Decision Coach V1.6.1 to production.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for OpenAI API

### Required Accounts
- **OpenAI API Key**: Active OpenAI account with API access
- **Environment**: Production server or cloud platform

## 🔧 Installation Steps

### 1. Environment Setup

```bash
# Clone or download the project
cd /path/to/ThinkPal-Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import openai, flask, faiss; print('Dependencies installed successfully')"
```

### 3. Configuration Setup

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Server Configuration
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0

# Optional: Custom settings
MAX_TOKENS=2000
TEMPERATURE=0.7
```

### 4. Verify Data Files

Ensure these files are present:
- ✅ `frameworks_gpt.json` (98KB decision frameworks database)
- ✅ `vector_index.faiss` (437KB vector search index)
- ✅ `metadata.json` (4.2MB document metadata)

## 🏃‍♂️ Running the Application

### Development Mode

```bash
# Start the API server
python api_server.py

# Server will be available at: http://localhost:5000
```

### Production Mode

```bash
# Using Gunicorn (recommended for production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app

# Using Waitress (Windows alternative)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 api_server:app
```

## 🧪 Testing the Deployment

### 1. Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "engine_ready": true
}
```

### 2. Test Query

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How to prioritize tasks when under tight deadlines?"}'
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "answer": "**Strategic Thinking Lens**\n...",
    "query": "How to prioritize tasks when under tight deadlines?",
    "timestamp": "2024-12-XX...",
    "model": "gpt-3.5-turbo",
    "processing_time": 2.3,
    "conceptsToolsPractice": [...]
  }
}
```

## 🔒 Security Considerations

### 1. API Key Security
- Store API keys in environment variables
- Never commit API keys to version control
- Use secret management services in production

### 2. Network Security
- Use HTTPS in production
- Configure firewall rules
- Implement rate limiting

### 3. Access Control
- Implement authentication if needed
- Use API keys for external access
- Monitor API usage

## 📊 Monitoring and Logging

### 1. Application Logs

The server provides detailed logging:
- Request/response logging
- Error tracking
- Performance metrics

### 2. Health Monitoring

Monitor these endpoints:
- `GET /health` - System health
- `GET /stats` - Usage statistics

### 3. Performance Metrics

Track these metrics:
- Response time
- Error rate
- API usage
- Memory consumption

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `OPENAI_MODEL` | gpt-3.5-turbo | AI model to use |
| `FLASK_ENV` | development | Flask environment |
| `PORT` | 5000 | Server port |
| `HOST` | 0.0.0.0 | Server host |

### Advanced Configuration

Edit `config.py` for additional settings:
- Model parameters
- Response formatting
- Error handling
- Logging levels

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: OpenAI API key not found
   Solution: Set OPENAI_API_KEY environment variable
   ```

2. **Port Already in Use**
   ```
   Error: Address already in use
   Solution: Change PORT in .env file or kill existing process
   ```

3. **Missing Dependencies**
   ```
   Error: Module not found
   Solution: Run pip install -r requirements.txt
   ```

4. **Memory Issues**
   ```
   Error: Out of memory
   Solution: Increase server RAM or optimize vector index
   ```

### Debug Mode

Enable debug mode for troubleshooting:
```bash
export FLASK_DEBUG=True
python api_server.py
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer for multiple instances
- Implement session management
- Use shared storage for data files

### Vertical Scaling
- Increase server resources
- Optimize vector search performance
- Implement caching strategies

### Database Considerations
- Consider moving to external database
- Implement connection pooling
- Add data backup strategies

## 🔄 Maintenance

### Regular Tasks
1. **Monitor API usage** - Track OpenAI API costs
2. **Update dependencies** - Keep packages current
3. **Backup data files** - Regular backups of JSON databases
4. **Review logs** - Monitor for errors and performance issues

### Updates
1. **Code updates** - Deploy new versions
2. **Model updates** - Update AI model configurations
3. **Framework updates** - Keep decision frameworks current

## 📞 Support

### Documentation
- `V1.6.1_RELEASE_SUMMARY.md` - Complete release documentation
- `BACKEND_V16_COMPLETE.md` - Backend implementation details
- `FRONTEND_V16_TESTING_CHECKLIST.md` - Frontend integration guide

### Testing
- Run `test_final.py` for comprehensive testing
- Use test cases in `test_cases.json`
- Validate response format compliance

## ✅ Deployment Checklist

- [ ] Environment setup complete
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] API key configured
- [ ] Data files verified
- [ ] Server started successfully
- [ ] Health check passed
- [ ] Test query successful
- [ ] Security measures implemented
- [ ] Monitoring configured
- [ ] Documentation updated

## 🎉 Success!

Your ThinkPal Decision Coach V1.6.1 is now deployed and ready for production use!

**Next Steps:**
1. Test with frontend integration
2. Monitor performance and usage
3. Implement additional security measures
4. Plan for future enhancements

---

**Status**: ✅ **V1.6.1 DEPLOYMENT READY**

*For additional support, refer to the comprehensive documentation in the project files.* 