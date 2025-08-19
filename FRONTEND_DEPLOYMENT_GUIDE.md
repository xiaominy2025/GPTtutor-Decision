# GPTTutor Frontend Deployment & Backend Communication Guide

## 🎯 Current Status
- ✅ Frontend UI is developed and working
- ✅ Clickable follow-up prompts functionality exists locally
- ❌ Clickable prompts functionality was lost during previous deployment
- 🔧 Need to restore and ensure proper backend communication

## 🔗 Backend Communication Requirements

### API Endpoints
The frontend expects these endpoints from the V1666 backend:

```javascript
// Health check
GET /health
Response: {"status": "healthy", "version": "V166-Lambda"}

// Query processing
POST /query
Request: {"query": "your question", "course_id": "decision"}
Response: {
  "status": "success",
  "data": {
    "answer": "**Strategic Thinking Lens**\n\n[content]...",
    "followUpPrompts": ["prompt1", "prompt2", "prompt3"],
    "processing_time": 2.5,
    "model": "gpt-3.5-turbo"
  }
}
```

### CORS Configuration
Ensure backend has proper CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

## 🔧 Restoring Clickable Follow-up Prompts

### The Issue
The clickable prompts functionality was working locally but lost during deployment. This typically happens due to:
1. JavaScript file not loading properly
2. API response format mismatch
3. CORS issues preventing API calls
4. File compression/minification issues

### Quick Fix Steps

#### 1. Verify JavaScript Loading
Check browser console for errors. Ensure `app.js` loads without errors:
```javascript
// Add this to your main JavaScript file
console.log('🚀 Frontend loaded successfully');
console.log('🔗 API URL:', getApiBaseUrl());
```

#### 2. Test API Communication
Add this test function to verify backend connectivity:
```javascript
async function testBackendConnection() {
    try {
        const response = await fetch(`${getApiBaseUrl()}/health`);
        const data = await response.json();
        console.log('✅ Backend health check:', data);
        return true;
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
        return false;
    }
}
```

#### 3. Verify Follow-up Prompts Processing
Add debugging to the follow-up prompts display:
```javascript
function displayFollowUpPrompts(prompts) {
    console.log('📋 Received follow-up prompts:', prompts);
    
    if (!prompts || prompts.length === 0) {
        console.warn('⚠️ No follow-up prompts received');
        return;
    }
    
    // Your existing display logic here
    prompts.forEach((prompt, index) => {
        console.log(`Prompt ${index + 1}:`, prompt);
    });
}
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Test locally with `python -m http.server 8000`
- [ ] Verify clickable prompts work locally
- [ ] Check browser console for errors
- [ ] Test API communication locally

### Deployment Steps
1. **Upload files to S3/CloudFront**
2. **Verify file integrity** - Check that `app.js` is not corrupted
3. **Test API connectivity** from deployed domain
4. **Check CORS** - Ensure backend allows requests from your domain
5. **Verify follow-up prompts** - Test the clickable functionality

### Post-Deployment Verification
```javascript
// Add this to your deployed site to test
async function verifyDeployment() {
    console.log('🔍 Verifying deployment...');
    
    // Test 1: API connectivity
    const healthOk = await testBackendConnection();
    
    // Test 2: Submit a test query
    if (healthOk) {
        const testQuery = "How do I make a decision under uncertainty?";
        const response = await fetch(`${getApiBaseUrl()}/query`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: testQuery, course_id: 'decision'})
        });
        
        const data = await response.json();
        console.log('📋 Test response:', data);
        
        if (data.data && data.data.followUpPrompts) {
            console.log('✅ Follow-up prompts received:', data.data.followUpPrompts.length);
        } else {
            console.warn('⚠️ No follow-up prompts in response');
        }
    }
}
```

## 🔍 Troubleshooting Common Issues

### Issue 1: Follow-up Prompts Not Clickable
**Symptoms**: Prompts appear but don't respond to clicks
**Solutions**:
1. Check browser console for JavaScript errors
2. Verify `onclick` handlers are properly attached
3. Ensure no CSS is blocking click events
4. Test with a simple alert to verify event binding

### Issue 2: API Calls Failing
**Symptoms**: Network errors in console
**Solutions**:
1. Check CORS configuration on backend
2. Verify API URL is correct for production
3. Test API endpoints directly with curl/Postman
4. Check if backend is accessible from deployment domain

### Issue 3: Response Format Mismatch
**Symptoms**: Follow-up prompts not displaying
**Solutions**:
1. Verify backend returns `followUpPrompts` array
2. Check response structure matches expected format
3. Add response logging to debug format issues

## 📋 Quick Recovery Script

If clickable prompts are lost, add this emergency fix:

```javascript
// Emergency follow-up prompts fix
function emergencyFollowUpFix() {
    // Override the display function if needed
    window.displayFollowUpPrompts = function(prompts) {
        console.log('🚨 Using emergency follow-up prompts fix');
        
        const container = document.getElementById('followUpPrompts');
        if (!container) {
            console.error('❌ Follow-up container not found');
            return;
        }
        
        const promptsHtml = prompts.map((prompt, index) => `
            <button 
                class="follow-up-prompt bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg p-4 text-left transition-all duration-200 cursor-pointer"
                onclick="handleFollowUpClick('${prompt.replace(/'/g, "\\'")}')"
            >
                <div class="flex items-start space-x-3">
                    <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                        <span class="text-blue-600 text-sm font-medium">${index + 1}</span>
                    </div>
                    <div class="flex-1">
                        <p class="text-gray-700 font-medium">${prompt}</p>
                        <p class="text-gray-500 text-sm mt-1">Click to ask this question</p>
                    </div>
                </div>
            </button>
        `).join('');
        
        container.innerHTML = promptsHtml;
        console.log('✅ Emergency fix applied');
    };
    
    // Override the click handler
    window.handleFollowUpClick = function(prompt) {
        console.log('🖱️ Follow-up prompt clicked:', prompt);
        const queryInput = document.getElementById('queryInput');
        if (queryInput) {
            queryInput.value = prompt;
            // Trigger form submission
            document.getElementById('queryForm').dispatchEvent(new Event('submit'));
        }
    };
}

// Run emergency fix
emergencyFollowUpFix();
```

## 🎯 Success Criteria

Your deployment is successful when:
- [ ] Frontend loads without console errors
- [ ] API health check returns success
- [ ] Query submission works
- [ ] Follow-up prompts appear as clickable buttons
- [ ] Clicking a prompt populates input and auto-submits
- [ ] Response sections display properly formatted

## 📞 Emergency Contacts

If issues persist:
1. Check browser console for specific error messages
2. Test API endpoints directly with curl/Postman
3. Verify backend is running and accessible
4. Check CORS configuration on backend
5. Review deployment logs for file upload issues

---

**Remember**: The clickable follow-up prompts are the key differentiator of your UI. Always test this functionality after any deployment!
