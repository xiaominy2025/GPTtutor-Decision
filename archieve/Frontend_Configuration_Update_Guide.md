# Frontend Configuration Update Guide
## Using the New Prod Alias URL

**Date**: September 3, 2025  
**Status**: ✅ Ready for Production  
**Purpose**: Update frontend configuration to use the new Lambda prod alias URL

---

## 🎯 Overview

Your frontend application needs to be updated to use the new **prod alias URL** instead of the previous endpoint. This change provides:

- **Stable versioning**: Always points to a tested, immutable version
- **Better performance**: Eliminates cold starts through version management
- **Production reliability**: Isolated from development changes

---

## 🔗 New API Endpoints

### Production Alias URL (Recommended)
```
https://ppoh5tatv4cnr7x7gzgha5k6wu0jrisc.lambda-url.us-east-2.on.aws/
```

### Legacy URL (Fallback)
```
https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/
```

---

## 📝 Required Configuration Changes

### 1. Environment Variables (.env)

**Update your `.env` file:**

```bash
# OLD (if exists)
# REACT_APP_API_BASE=https://old-endpoint.com

# NEW - Production Alias URL
REACT_APP_API_BASE=https://ppoh5tatv4cnr7x7gzgha5k6wu0jrisc.lambda-url.us-east-2.on.aws/
```

### 2. Environment Variables (.env.production)

**For production builds:**

```bash
REACT_APP_API_BASE=https://ppoh5tatv4cnr7x7gzgha5k6wu0jrisc.lambda-url.us-east-2.on.aws/
```

### 3. Environment Variables (.env.development)

**For development builds:**

```bash
REACT_APP_API_BASE=https://ppoh5tatv4cnr7x7gzgha5k6wu0jrisc.lambda-url.us-east-2.on.aws/
```

---

## 🚀 API Endpoints Available

### Health Check
```
GET ${REACT_APP_API_BASE}/health
```

### Course Information
```
GET ${REACT_APP_API_BASE}/courses
GET ${REACT_APP_API_BASE}/api/course/decision
```

### Query Processing
```
POST ${REACT_APP_API_BASE}/query
Content-Type: application/json

{
  "query": "Your question here",
  "courseId": "decision",
  "userId": "user123"
}
```

---

## ✅ Testing Your Configuration

### 1. Health Check Test
```javascript
// Test if the new endpoint is accessible
fetch(`${process.env.REACT_APP_API_BASE}/health`)
  .then(response => response.json())
  .then(data => console.log('Health check:', data))
  .catch(error => console.error('Error:', error));
```

**Expected Response:**
```json
{
  "data": {
    "status": "healthy"
  },
  "status": "success",
  "version": "V1.6.6.6",
  "timestamp": "2025-09-03T14:57:58.290602Z"
}
```

### 2. Query Test
```javascript
// Test the query endpoint
fetch(`${process.env.REACT_APP_API_BASE}/query`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: "How should I plan production under tariff uncertainty?",
    courseId: "decision",
    userId: "test-user"
  })
})
.then(response => response.json())
.then(data => console.log('Query response:', data))
.catch(error => console.error('Error:', error));
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. CORS Errors
**Problem**: `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Solution**: CORS is properly configured for:
- `https://www.engentlabs.com`
- `https://engentlabs.com`

Ensure your frontend is running on one of these domains.

#### 2. 403 Forbidden
**Problem**: `{"Message":"Forbidden"}`

**Solution**: The prod alias URL has been configured with proper permissions. If you still get this error, contact the backend team.

#### 3. Environment Variable Not Loading
**Problem**: `process.env.REACT_APP_API_BASE` is undefined

**Solution**: 
- Restart your development server after updating `.env`
- Ensure the variable name starts with `REACT_APP_`
- Check for typos in the variable name

---

## 📋 Implementation Checklist

- [ ] Update `.env` file with new `REACT_APP_API_BASE`
- [ ] Update `.env.production` if using production builds
- [ ] Update `.env.development` if using development builds
- [ ] Test health endpoint (`/health`)
- [ ] Test query endpoint (`/query`)
- [ ] Verify CORS is working in browser DevTools
- [ ] Update any hardcoded API URLs in your code
- [ ] Test in development environment
- [ ] Test in production environment (if applicable)

---

## 🔄 Rollback Plan

If you need to rollback to the previous endpoint:

```bash
# In .env files
REACT_APP_API_BASE=https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/
```

---

## 📞 Support

**Backend Team Contact**: Available for quota increase and PC configuration  
**Current Status**: Prod alias URL is fully functional and ready for production use  
**Next Steps**: Backend team will request quota increase to enable Provisioned Concurrency (PC=1)

---

## 🎉 Benefits of This Update

1. **Version Stability**: Always uses tested, immutable versions
2. **Performance**: Better response times through version management
3. **Reliability**: Isolated from development changes
4. **Scalability**: Ready for future performance optimizations
5. **Monitoring**: Better tracking of production vs development usage

---

*Last Updated: September 3, 2025*  
*Version: 1.0*  
*Status: Production Ready* ✅


