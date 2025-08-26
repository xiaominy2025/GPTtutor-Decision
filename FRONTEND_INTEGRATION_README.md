# 🚀 Engent Labs Frontend Integration (v1666) - Phased Approach

## 📋 **Current Phase: Lambda CORS Fix (Phase 1)**

**Base API URL**: `https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws`

**Region**: us-east-2  
**API Type**: Lambda Function URL (Direct)  
**CORS**: Handled by Lambda with proper headers  
**Status**: Immediate CORS fix for frontend unblocking

## 🔗 **Endpoints**

### **Health Check**
- **Method**: `GET /health`
- **Response**: `{ status: "healthy", version: "V1.6.6.6", engine_ready: true }`

### **Query Processing**
- **Method**: `POST /query`
- **Body**: `{ query: string, course_id: "decision" }`
- **Response**: Structured JSON with `answer`, `conceptsToolsPractice`, `strategicThinkingLens`, `followUpPrompts`

### **Course Configuration**
- **Method**: `GET /courses/{courseId}/config`
- **Purpose**: Serves UI config by returning `ui_metadata.json` for the course
- **Path Parameter**: `courseId` (e.g., "decision")

## 🌐 **CORS Configuration (Phase 1)**

**Handled by Lambda** with centralized CORS headers:

- **Allowed Origins**: `https://www.engentlabs.com` (primary), `https://engentlabs.com` (fallback)
- **Allowed Methods**: `GET, POST, OPTIONS`
- **Allowed Headers**: `Content-Type, Authorization`
- **Max-Age**: `86400` (24 hours)
- **Preflight**: Explicit OPTIONS handling

## ⚙️ **Frontend Environment (Phase 1)**

```bash
# Current Lambda Function URL (no changes needed)
VITE_API_URL=https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws
```

## 🧪 **Example Requests (Phase 1)**

### **Health Check**
```bash
curl -s https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/health
```

### **Query Processing**
```bash
curl -s -X POST https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I negotiate a better salary?","course_id":"decision"}'
```

### **Course Configuration**
```bash
curl -s https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/courses/decision/config
```

### **CORS Preflight Test**
```bash
curl -X OPTIONS https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query \
  -H "Origin: https://www.engentlabs.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

## 📊 **Response Structure**

### **Health Response**
```json
{
  "status": "healthy",
  "version": "V1.6.6.6",
  "engine_ready": true
}
```

### **Query Response**
```json
{
  "status": "success",
  "data": {
    "answer": "**Strategic Thinking Lens**\n\n[Content here]\n\n**Follow-up Prompts**\n\n1. [Question 1]\n2. [Question 2]\n\n**Concepts/Tools**\n\n[Concepts here]",
    "conceptsToolsPractice": [
      {
        "term": "Decision Matrix",
        "definition": "A systematic approach to evaluate options..."
      }
    ],
    "model": "gpt-3.5-turbo",
    "processing_time": 2.5,
    "timestamp": "2024-12-19T10:30:00Z"
  }
}
```

### **Course Config Response**
```json
{
  "success": true,
  "data": {
    "title": "Decision-Making Practice Lab",
    "mobile_title": "Decision Lab", 
    "tagline": "A GPT-powered active learning platform",
    "placeholder": "Ask a decision-making question...",
    "default_sections": 3,
    "sections_titles": [
      "Strategic Thinking Lens",
      "Follow-up Prompts",
      "Concepts/Tools"
    ]
  }
}
```

## 📁 **Content Sources**

- **Course UI**: Pulls from `ui_metadata.json`, not a separate `config.json`
- **Lambda Function**: `engent-v1666-img` in us-east-2
- **Path Parameters**: Handled as `event.pathParameters.courseId` in Lambda

## ✅ **Phase 1 Success Criteria**

- [ ] Health endpoint returns `{ status: "healthy" }`
- [ ] Query endpoint returns structured JSON with all sections
- [ ] Course config loads successfully from `/courses/decision/config`
- [ ] **No CORS errors from `https://www.engentlabs.com`**
- [ ] All required response fields are present
- [ ] Browser requests work without CORS blocking

## 🚀 **Future Phase: API Gateway (Phase 3)**

**Planned Base URL**: `https://api.engentlabs.com`

**Benefits**:
- Clean custom domain
- Built-in monitoring and scaling
- Professional API appearance
- Enhanced security features

**Timeline**: Later this week (nice to have, not blocking)

**Frontend Changes**: Only environment variable update needed


