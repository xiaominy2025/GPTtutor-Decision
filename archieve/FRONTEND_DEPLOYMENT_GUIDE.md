# 🚀 Engent Labs API Deployment Guide - Phased Approach

## 📋 **Mission**
Implement a phased approach to solve CORS issues: **Phase 1** (immediate Lambda CORS fix) followed by **Phase 3** (future API Gateway implementation).

## 🎯 **Phased Strategy**

### **Phase 1: Lambda CORS Fix (IMMEDIATE - Highest Priority)**
- **Goal**: Unblock frontend immediately with minimal risk
- **Approach**: Fix CORS headers in Lambda function
- **Timeline**: 30-45 minutes
- **Risk**: Low

### **Phase 2: Frontend Validation (After Phase 1)**
- **Goal**: Validate CORS fix works in browser
- **Approach**: Test frontend integration
- **Timeline**: 15 minutes
- **Risk**: None (frontend unchanged)

### **Phase 3: API Gateway (Later This Week - Nice to Have)**
- **Goal**: Professional API with custom domain
- **Approach**: HTTP API + custom domain
- **Timeline**: 1-2 hours
- **Risk**: Medium (infrastructure change)

---

## 🔧 **Phase 1: Lambda CORS Fix Implementation**

### **Step 1: Patch Lambda Function**

#### **Current Problem:**
```python
# Current problematic code in lambda_function_v166.py
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", 
              "https://engentlabs.com", "https://www.engentlabs.com"],
     allow_headers=["Content-Type", "Authorization", "Origin"],
     methods=["GET", "POST", "OPTIONS"],
     max_age=3600)
```

#### **Solution: Remove Flask-CORS, Add Centralized CORS Headers**
```python
# Remove this line completely:
# CORS(app, ...)

# Add centralized CORS function:
def add_cors_headers(response, origin=None):
    # Handle dual origins: www.engentlabs.com and engentlabs.com
    if origin in ['https://www.engentlabs.com', 'https://engentlabs.com']:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        # Default to primary origin
        response.headers['Access-Control-Allow-Origin'] = 'https://www.engentlabs.com'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

# Add OPTIONS handler for preflight:
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    # Get origin from request headers for dynamic CORS response
    origin = request.headers.get('Origin')
    return add_cors_headers(response, origin)

# Modify existing endpoints to add CORS headers:
@app.route('/health', methods=['GET'])
def health():
    response = jsonify({"status": "healthy", "version": "V1.6.6.6", "engine_ready": True})
    # Get origin from request headers for dynamic CORS response
    origin = request.headers.get('Origin')
    return add_cors_headers(response, origin)
```

### **Step 2: Rebuild and Deploy**
1. **Update Lambda code** with CORS fix
2. **Rebuild Docker container** with updated code
3. **Deploy to ECR** and update Lambda function
4. **Test CORS headers** are present

### **Step 3: Test CORS Fix**

#### **Test 1: Health Endpoint**
```bash
curl -s https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/health
```
**Expected**: JSON response with CORS headers

#### **Test 2: CORS Preflight**
```bash
curl -X OPTIONS https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query \
  -H "Origin: https://www.engentlabs.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```
**Expected**: 200 OK with proper CORS headers

#### **Test 3: Browser Simulation**
```bash
curl -X POST https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query \
  -H "Origin: https://www.engentlabs.com" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","course_id":"decision"}' \
  -v
```
**Expected**: 200 OK with `Access-Control-Allow-Origin: https://www.engentlabs.com`

---

## 📱 **Phase 2: Frontend Validation**

### **Frontend Team Responsibilities:**
- **No code changes needed** - current integration works
- **Test browser requests** from `https://www.engentlabs.com`
- **Verify no CORS errors** in browser console
- **Test all functionality**: queries, course config, follow-up prompts

### **Validation Checklist:**
- [ ] Browser console: No CORS errors
- [ ] Query submission: Works from `www.engentlabs.com`
- [ ] Course config: Loads from `/courses/decision/config`
- [ ] All UI functionality: Follow-up prompts, etc.

---

## 🚀 **Phase 3: API Gateway (Future - Nice to Have)**

### **Benefits:**
- Clean custom domain (`api.engentlabs.com`)
- Built-in monitoring and scaling
- Professional API appearance
- Enhanced security features

### **Implementation (When Ready):**
1. **Create HTTP API** in us-east-2
2. **Configure Lambda integration** (`engent-v1666-img`)
3. **Set up CORS** with dual origins
4. **Create custom domain** with ACM certificate
5. **Update frontend**: `VITE_API_URL=https://api.engentlabs.com`

### **Frontend Changes for Phase 3:**
```bash
# Only environment variable change needed
VITE_API_URL=https://api.engentlabs.com
```

---

## ✅ **Success Criteria**

### **Phase 1 Success:**
- [ ] Lambda returns proper CORS headers
- [ ] OPTIONS preflight requests work
- [ ] Browser requests from `www.engentlabs.com` succeed
- [ ] No CORS errors in browser console

### **Phase 2 Success:**
- [ ] Frontend loads without CORS errors
- [ ] Course selection works
- [ ] Query submission works
- [ ] Follow-up prompts work

### **Phase 3 Success (Future):**
- [ ] Custom domain works (`api.engentlabs.com`)
- [ ] All functionality preserved
- [ ] Professional API appearance

---

## ⏱️ **Timeline**

### **Phase 1: Backend Fix**
- **Time**: 30-45 minutes
- **Risk**: Low
- **Impact**: Immediate frontend unblocking

### **Phase 2: Frontend Validation**
- **Time**: 15 minutes
- **Risk**: None
- **Impact**: Confirmation of CORS fix

### **Phase 3: API Gateway (Future)**
- **Time**: 1-2 hours
- **Risk**: Medium
- **Impact**: Production polish

**Total Phase 1+2**: ~1 hour  
**Phase 3**: Later this week (optional)

---

## 🎯 **Recommendation**

**Proceed with Phase 1 immediately!** This approach:
- ✅ **Unblocks frontend** in hours, not days
- ✅ **Minimal risk** with small Lambda patch
- ✅ **Immediate validation** of CORS fix
- ✅ **Flexible timeline** for API Gateway later

**Ready to execute Phase 1!** 🚀


