# V1.6.6.6 CORS Fixed Version

This folder contains the working version of the GPTTutor backend with CORS and response format fixes applied.

## V1.6.6.6 Core Files

The V1.6.6.6 version consists of **five core files**:

### 1. Core Application Files (Root Level)
- **`api_server.py`** - Flask API server with all endpoints and business logic
- **`query_engine.py`** - Core query processing engine with V1.6.6.6 implementation
- **`vector_index.faiss`** - FAISS vector index for semantic search

### 2. Course Configuration Files (courses/decision/)
- **`base_metadata.json`** - Course metadata and configuration
- **`glossary.json`** - Course glossary with terms and definitions

## Key Changes Made

### 1. CORS Headers Fixed
- **Before**: `Access-Control-Allow-Origin: *, *` (duplicate headers)
- **After**: `Access-Control-Allow-Origin: https://engentlabs.com` (single origin)
- **Location**: `lambda_handler.py` - Updated hardcoded CORS headers

### 2. Response Format Standardized to V1.6.6.6
- **Before**: Mixed response formats across endpoints
- **After**: Consistent V1.6.6.6 envelope format:
  ```json
  {
    "data": { ... },
    "status": "success",
    "version": "V1.6.6.6",
    "timestamp": "2025-08-22T00:00:00Z"
  }
  ```
- **Location**: `api_server.py` - Updated all endpoint responses

### 3. Working Structure Preserved
- Uses the exact same structure as the working `no_spacy` version
- `lambda_handler.py` imports `api_server` and uses Flask test client
- `api_server.py` contains all the business logic
- `query_engine.py` handles the core query processing

## File Organization

```
v1666_cors_fixed/
├── README.md                           # This documentation
├── lambda_handler.py                   # AWS Lambda entry point with CORS fixes
├── api_server.py                       # Flask app with V1.6.6.6 response format
├── query_engine.py                     # Core query processing engine
├── vector_index.faiss                  # FAISS vector index
├── Dockerfile                          # Container configuration
├── requirements_container.txt          # Python dependencies
├── base_metadata.json                  # Root level course metadata (for Lambda)
├── glossary.json                       # Root level course glossary (for Lambda)
└── courses/
    └── decision/
        ├── base_metadata.json          # Course metadata
        ├── glossary.json               # Course glossary
        ├── course_config.json          # Course configuration
        ├── sections.json               # Section definitions
        ├── prompts.json                # Prompt templates
        └── documents/                  # Course documents
```

## Deployment

This version was successfully deployed as Docker image:
- **Tag**: `engent-v1666-img:fix-cors-v1666`
- **ECR URI**: `771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-v1666-img:fix-cors-v1666`
- **Lambda Function**: `engent-v1666-img`

## Testing

The version passes all validation tests:
- ✅ Single CORS origin header
- ✅ V1.6.6.6 response envelope format
- ✅ All endpoints return correct structure
- ✅ Query endpoint includes all required sections

## Date Created

August 22, 2025 - Based on working `v1666_clean` version with CORS and response format fixes applied.

## Source

This version is based on the working `v1666_clean` folder which contains the original five core files:
- `api_server.py` (from v1666_clean root)
- `query_engine.py` (from v1666_clean root)  
- `vector_index.faiss` (from v1666_clean root)
- `base_metadata.json` (from v1666_clean/courses/decision/)
- `glossary.json` (from v1666_clean/courses/decision/)
