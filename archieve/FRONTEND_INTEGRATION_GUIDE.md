# Frontend Integration Guide for AWS Lambda Backend

## 🎯 Overview

Your AWS Lambda backend is now deployed and ready! This guide will help you integrate your React frontend with the new serverless backend.

## 🔗 Backend Information

### Function URL
```
https://your-lambda-function-url.lambda-url.us-east-1.on.aws/
```

### API Endpoints Available
- `GET /health` - Health check
- `POST /query` - Process queries
- `GET /courses` - List available courses
- `GET /api/course/{course_id}` - Get course metadata
- `GET /stats` - Get usage statistics
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `GET /test` - Test endpoint

## 🚀 Integration Steps

### Step 1: Update Environment Variables

In your frontend project, update the `.env` file:

```bash
# .env
VITE_API_BASE_URL=https://your-lambda-function-url.lambda-url.us-east-1.on.aws
VITE_API_VERSION=v1.6.6.6
VITE_DEPLOYMENT=aws-lambda
```

### Step 2: Update API Configuration

If you have an API configuration file, update it:

```javascript
// src/config/api.js or similar
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000, // 30 seconds for Lambda
  headers: {
    'Content-Type': 'application/json',
  }
};
```

### Step 3: Test Backend Connectivity

Create a simple test component to verify the connection:

```javascript
// src/components/BackendTest.jsx
import { useState, useEffect } from 'react';

export default function BackendTest() {
  const [status, setStatus] = useState('Testing...');
  const [data, setData] = useState(null);

  useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/health`);
        const result = await response.json();
        
        if (response.ok) {
          setStatus('✅ Backend Connected!');
          setData(result);
        } else {
          setStatus('❌ Backend Error');
          setData(result);
        }
      } catch (error) {
        setStatus('❌ Connection Failed');
        setData({ error: error.message });
      }
    };

    testBackend();
  }, []);

  return (
    <div className="p-4 border rounded">
      <h3>Backend Connection Test</h3>
      <p><strong>Status:</strong> {status}</p>
      {data && (
        <pre className="text-sm bg-gray-100 p-2 rounded">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}
```

### Step 4: Update API Service Functions

Update your existing API service functions to use the new backend:

```javascript
// src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE_URL;

export const apiService = {
  // Health check
  async checkHealth() {
    const response = await fetch(`${API_BASE}/health`);
    return response.json();
  },

  // Process query
  async processQuery(query, courseId = 'decision') {
    const response = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        course_id: courseId,
        user_id: 'default'
      })
    });
    return response.json();
  },

  // Get course metadata
  async getCourseMetadata(courseId) {
    const response = await fetch(`${API_BASE}/api/course/${courseId}`);
    return response.json();
  },

  // Get available courses
  async getCourses() {
    const response = await fetch(`${API_BASE}/courses`);
    return response.json();
  },

  // Get user profile
  async getUserProfile() {
    const response = await fetch(`${API_BASE}/profile`);
    return response.json();
  },

  // Update user profile
  async updateUserProfile(profileData) {
    const response = await fetch(`${API_BASE}/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData)
    });
    return response.json();
  },

  // Get statistics
  async getStats() {
    const response = await fetch(`${API_BASE}/stats`);
    return response.json();
  }
};
```

### Step 5: Update Your Main Components

Update your existing components to use the new API service:

```javascript
// Example: Update your query processing component
import { apiService } from '../services/api';

export default function QueryProcessor() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await apiService.processQuery(query);
      setResponse(result);
    } catch (error) {
      console.error('Query processing error:', error);
      setResponse({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>
      
      {response && (
        <div className="mt-4">
          <h3>Response:</h3>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

## 🧪 Testing Checklist

### ✅ Backend Connectivity
- [ ] Health check endpoint responds
- [ ] CORS is working (no browser errors)
- [ ] All endpoints return expected JSON

### ✅ Frontend Integration
- [ ] Environment variables loaded correctly
- [ ] API service functions work
- [ ] Error handling works
- [ ] Loading states display correctly

### ✅ User Experience
- [ ] Query processing works
- [ ] Course metadata loads
- [ ] Profile management works
- [ ] Error messages are user-friendly

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**
   ```
   Access to fetch at '...' from origin '...' has been blocked by CORS policy
   ```
   **Solution:** The Lambda function already has CORS configured. Check that your frontend origin is included.

2. **Network Errors**
   ```
   Failed to fetch
   ```
   **Solution:** Verify the Function URL is correct and accessible.

3. **Timeout Errors**
   ```
   Request timeout
   ```
   **Solution:** Lambda timeout is set to 30 seconds. For longer operations, consider optimizing the backend.

4. **Environment Variables Not Loading**
   ```
   VITE_API_BASE_URL is undefined
   ```
   **Solution:** Restart your development server after updating `.env` file.

### Debug Commands

```bash
# Test backend directly
curl -X GET "https://your-function-url.lambda-url.us-east-1.on.aws/health"

# Test with CORS headers
curl -X GET "https://your-function-url.lambda-url.us-east-1.on.aws/health" \
  -H "Origin: http://localhost:5173"

# Test query endpoint
curl -X POST "https://your-function-url.lambda-url.us-east-1.on.aws/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"test query","course_id":"decision"}'
```

## 🚀 Production Deployment

### Environment Variables for Production
```bash
# Production .env
VITE_API_BASE_URL=https://your-lambda-function-url.lambda-url.us-east-1.on.aws
VITE_API_VERSION=v1.6.6.6
VITE_DEPLOYMENT=aws-lambda
```

### Build and Deploy
```bash
# Build for production
npm run build

# Deploy to your hosting platform
# (Vercel, Netlify, AWS S3, etc.)
```

## 📊 Monitoring

### Frontend Monitoring
- Add error tracking (Sentry, LogRocket)
- Monitor API response times
- Track user interactions

### Backend Monitoring
- CloudWatch logs for Lambda
- API Gateway metrics (if using)
- Custom metrics for business logic

## 🎉 Success Indicators

You'll know the integration is successful when:

1. ✅ Health check returns 200 OK
2. ✅ Query processing works end-to-end
3. ✅ Course metadata loads correctly
4. ✅ No CORS errors in browser console
5. ✅ All existing functionality works with new backend
6. ✅ Error handling works gracefully

---

## 🚀 Ready to Deploy!

Your frontend is now ready to connect to your AWS Lambda backend. The serverless architecture will automatically scale with your traffic and provide excellent performance.

**Next Steps:**
1. Test the integration locally
2. Deploy to production
3. Monitor performance
4. Set up custom domain (optional)

**Happy coding! 🎉**
