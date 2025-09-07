#!/usr/bin/env python3
"""
AWS Lambda Function with Complete V166 Query Engine Integration
V1.6.6.6 Final Version - Complete Feature Parity with api_server.py
FIXED VERSION - Proper Response Formatting
"""

import json
import time
import os
import sys
import re
import traceback
from typing import List, Tuple, Dict, Any
import boto3
from datetime import datetime

# Flask for Lambda compatibility
from flask import Flask, request, jsonify

# V166 Dependencies (must be included in Lambda deployment)
try:
    import openai
    import numpy as np
    import faiss
    import spacy
    # Import the authoritative query_engine module
    import query_engine
except ImportError as e:
    # Missing dependencies
    # Will handle gracefully with fallback
    pass

app = Flask(__name__)

# === CORS CONFIGURATION - V1.6.6.6 PRODUCTION ===
ALLOWED_ORIGINS = {
    "https://engentlabs.com",
    "https://www.engentlabs.com"
}

def pick_origin(event):
    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin")
    return origin if origin in ALLOWED_ORIGINS else "https://engentlabs.com"

def create_response(data, status="success", status_code=200, event=None):
    """Standardized response wrapper for all endpoints"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "data": data,
            "status": status,
            "version": "V1.6.6.6",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    }

def handle_options(event):
    """Handle OPTIONS preflight requests with robust CORS headers"""
    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin")
    
    # Always return CORS headers, even for invalid origins (browser will handle)
    cors_origin = origin if origin in ALLOWED_ORIGINS else "https://engentlabs.com"
    
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
            "Vary": "Origin"
        },
        "body": ""
    }

# === V166 CORE COMPONENTS ===

# Course configuration
DEFAULT_COURSE = "decision"

# Note: Using authoritative SYSTEM_PROMPT_ANALYTICS from query_engine.py

# Note: Removed duplicate functions - now using authoritative query_engine methods

def process_query_v166_fixed(query: str) -> dict:
    """
    V1.6.6: Fixed Query Processing - Uses authoritative query_engine.process_query_structured()
    Eliminates double work by using structured data instead of re-parsing GPT response.
    """
    try:
        # Check if query_engine is available
        if not hasattr(query_engine, 'process_query_structured'):
            raise Exception("query_engine.process_query_structured method not available")
        
        # V1.6.6: Use the authoritative query_engine.process_query_structured() method
        # This eliminates the need to re-parse GPT response and ensures 100% consistency
        start_time = time.time()
        try:
            structured_response = query_engine.process_query_structured(query)
        except Exception as qe:
            traceback.print_exc()
            raise qe
            
        processing_time = time.time() - start_time
        
        # Add processing time to the structured response
        structured_response["processing_time"] = processing_time
        
        # Check if query was rejected by relevance filter
        if isinstance(structured_response.get("answer", ""), str) and structured_response["answer"].startswith("⚠️ This question doesn't appear to be related to the course"):
            return {
                "answer": structured_response["answer"],
                "strategicThinkingLens": structured_response["answer"],
                "followUpPrompts": "",
                "conceptsToolsPractice": [],
                "model": "relevance_filter",
                "processing_time": processing_time
            }
        
        # V1.6.6: Return the authoritative structured response directly
        # No more re-parsing of GPT response - query-engine is the source of truth
        return structured_response
        
    except Exception as e:
        traceback.print_exc()
        
        # Fallback response
        fallback_answer = f"I understand you're asking about: {query}\n\nThis appears to be a decision-making question that would benefit from systematic analysis. Consider using frameworks like decision trees, SWOT analysis, or scenario planning to evaluate your options thoroughly."
        return {
            "answer": fallback_answer,
            "strategicThinkingLens": fallback_answer,
            "followUpPrompts": "",
            "conceptsToolsPractice": [],
            "model": "fallback",
            "processing_time": 0.0
        }

def lambda_handler(event, context):
    """
    Main Lambda handler for V1.6.6.6
    """
    try:
        # Handle different event types
        if isinstance(event, dict) and ('requestContext' in event):
            # Lambda Function URL event
            request_context = event.get('requestContext', {})
            http_info = request_context.get('http', {})
            http_method = http_info.get('method', 'GET')
            path = http_info.get('path', '/')
            body = event.get('body', '{}')
            
            # Parse body with better error handling
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                except json.JSONDecodeError as e:
                    body = {}
                except Exception as e:
                    body = {}
            elif body is None:
                body = {}
            
            # Handle different endpoints
            start_time = time.time()
            
            if http_method == 'OPTIONS':
                return handle_options(event)
            
            if http_method == 'GET' and path == '/health':
                return create_response({"status": "healthy"}, event=event)
                
            elif http_method == 'GET' and path == '/debug/files':
                    # Debug endpoint to check file access
                    
                    # Use the unified path system from query_engine
                    try:
                        import query_engine
                        base_dir = query_engine.get_base_dir()
                        course_dir = query_engine.get_course_dir()
                        idx_path = query_engine.get_idx_path()
                        
                        debug_info = {
                            "base_dir": base_dir,
                            "course_dir": course_dir,
                            "idx_path": idx_path,
                            "root_files": os.listdir(base_dir) if os.path.exists(base_dir) else "MISSING",
                            "course_files": os.listdir(course_dir) if os.path.exists(course_dir) else "MISSING",
                            "faiss_exists": os.path.exists(idx_path),
                            "query_engine_exists": os.path.exists(os.path.join(base_dir, "query_engine.py")),
                            "lambda_function_exists": os.path.exists(os.path.join(base_dir, "lambda_function.py")),
                            "file_check": query_engine.assert_required_files_exist()
                        }
                    except Exception as e:
                        debug_info = {
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "base_dir": os.getcwd(),
                            "root_files": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else "MISSING"
                        }
                    
                    return create_response(debug_info, event=event)
                
            elif http_method == 'GET' and path == '/courses':
                return create_response({"courses": ["decision","marketing","strategy"]}, event=event)
                
            elif http_method == 'GET' and path.startswith('/api/course/'):
                # Extract course ID from path
                course_id = path.split('/')[-1]
                try:
                    with open(f"courses/{course_id}/ui_metadata.json") as f:
                        ui_metadata = json.load(f)
                    return create_response(ui_metadata, event=event)
                except Exception as e:
                    return create_response(
                        {"error": f"Failed to load UI metadata: {str(e)}"}, 
                        status="error", 
                        status_code=500, 
                        event=event
                    )
                
            elif http_method == 'POST' and path == '/query':
                if not body or 'query' not in body:
                    return create_response(
                        {"error": "Query is required"}, 
                        status="error", 
                        status_code=400,
                        event=event
                    )
                
                query = body['query']
                course_id = body.get('course_id', DEFAULT_COURSE)
                
                try:
                    # Process query using fixed V166 implementation
                    response_data = process_query_v166_fixed(query)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return create_response(
                        {"error": f"Query processing failed: {str(e)}"}, 
                        status="error", 
                        status_code=500,
                        event=event
                    )
                
                return create_response(response_data, event=event)
                
            else:
                # Unknown endpoint
                return create_response(
                    {"error": f"Not found: {http_method} {path}"}, 
                    status="error", 
                    status_code=404,
                    event=event
                )
        
        else:
            # Direct Lambda invocation
            return create_response({
                "message": "V1.6.6.6 Lambda function is running",
                "event_type": "Direct Invocation"
            }, event=event)
            
    except Exception as e:
        traceback.print_exc()
        
        return create_response(
            {"error": "Internal server error", "message": str(e)}, 
            status="error", 
            status_code=500,
            event=event
        )

if __name__ == '__main__':
    # Local development server
    app.run(debug=True, host='0.0.0.0', port=5000)
