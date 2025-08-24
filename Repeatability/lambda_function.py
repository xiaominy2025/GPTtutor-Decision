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
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    import spacy
    # Import the authoritative query_engine module
    import query_engine
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    # Will handle gracefully with fallback

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
    ao = pick_origin(event or {})
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": ao,
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Max-Age": "86400",
            "Content-Type": "application/json",
            "Vary": "Origin"
        },
        "body": json.dumps({
            "data": data,
            "status": status,
            "version": "V1.6.6.6",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    }

def handle_options(event):
    ao = pick_origin(event)
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": ao,
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
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
    Fixed V166 Query Processing - Uses authoritative query_engine.process_query()
    """
    try:
        print(f"🔄 V166 Processing Query: {query}")
        
        # Test file access first
        print("🔍 Testing file access...")
        import os
        print(f"Current directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir('.')}")
        
        if os.path.exists('query_engine.py'):
            print("✅ query_engine.py exists")
        else:
            print("❌ query_engine.py not found")
            
        if os.path.exists('vector_index.faiss'):
            print("✅ vector_index.faiss exists")
        else:
            print("❌ vector_index.faiss not found")
            
        if os.path.exists('courses'):
            print("✅ courses directory exists")
        else:
            print("❌ courses directory not found")
        
        # Check if query_engine is available
        if not hasattr(query_engine, 'process_query'):
            print("❌ query_engine.process_query method not found")
            raise Exception("query_engine.process_query method not available")
        
        print("✅ query_engine.process_query method found")
        
        # Test if we can access basic query_engine functions
        print("🔍 Testing query_engine basic functionality...")
        try:
            # Test if we can access the compute_relevance_score function
            if hasattr(query_engine, 'compute_relevance_score'):
                score, debug = query_engine.compute_relevance_score(query)
                print(f"✅ Relevance score test: {score}, debug: {debug}")
            else:
                print("⚠️ compute_relevance_score not available")
        except Exception as e:
            print(f"⚠️ Relevance score test failed: {e}")
        
        # Use the authoritative query_engine.process_query() method
        # This ensures 100% consistency with api_server.py
        start_time = time.time()
        try:
            answer = query_engine.process_query(query)
            print(f"✅ Query engine processing completed successfully")
        except Exception as qe:
            print(f"❌ Query engine processing failed: {qe}")
            print(f"❌ Error type: {type(qe)}")
            traceback.print_exc()
            raise qe
            
        processing_time = time.time() - start_time
        
        print(f"✅ Query engine processing completed in {processing_time:.2f}s")
        print(f"📝 Answer length: {len(answer)} characters")
        print(f"📄 Answer preview: {answer[:200]}...")
        
        # Check if query was rejected by relevance filter
        if isinstance(answer, str) and answer.startswith("⚠️ This question doesn't appear to be related to the course"):
            print("⚠️ Query rejected by relevance filter")
            return {
                "answer": answer,
                "strategicThinkingLens": answer,
                "followUpPrompts": "",
                "conceptsToolsPractice": [],
                "model": "relevance_filter",
                "processing_time": processing_time
            }
        
        # Extract concepts/tools as objects for frontend (EXACT same logic as api_server.py)
        concepts_tools_practice = []
        if hasattr(query_engine, 'extract_tools_from_section'):
            import re
            # V1.6.3: Only look for Concepts/Tools section
            concepts_match = re.search(r'\*\*Concepts/Tools\*\*\s*\n(.*?)(?=\n\n|$)', answer, re.DOTALL)
            if concepts_match:
                concepts_section = concepts_match.group(0)
                concepts_tools_practice = query_engine.extract_tools_from_section(concepts_section)
        
        # --- VALIDATION BLOCK: Ensure conceptsToolsPractice is always a list of {term, definition} objects ---
        def is_valid_concept(obj):
            return (
                isinstance(obj, dict)
                and 'term' in obj and isinstance(obj['term'], str) and obj['term'].strip() != ''
                and 'definition' in obj and isinstance(obj['definition'], str) and obj['definition'].strip() != ''
            )
        if not isinstance(concepts_tools_practice, list):
            print("🚨 Invalid conceptsToolsPractice format (not a list):", concepts_tools_practice)
            concepts_tools_practice = []
        else:
            fixed = []
            for item in concepts_tools_practice:
                if is_valid_concept(item):
                    fixed.append(item)
                else:
                    print(f"🚨 Invalid concept entry in conceptsToolsPractice: {item}")
            concepts_tools_practice = fixed
        # --- END VALIDATION BLOCK ---
        
        # Parse sections from the answer (same as api_server.py logic)
        strategic_thinking_lens = ""
        follow_up_prompts = ""
        
        # Simple parsing of the answer sections
        sections = answer.split("**")
        for i, section in enumerate(sections):
            if "Strategic Thinking Lens" in section:
                if i + 1 < len(sections):
                    strategic_thinking_lens = sections[i + 1].strip()
            elif "Follow-up Prompts" in section:
                if i + 1 < len(sections):
                    follow_up_prompts = sections[i + 1].strip()
        
        # Return structured response with required keys (same format as api_server.py)
        return {
            "answer": answer,
            "strategicThinkingLens": strategic_thinking_lens,
            "followUpPrompts": follow_up_prompts,
            "conceptsToolsPractice": concepts_tools_practice,
            "model": "gpt-3.5-turbo",
            "processing_time": processing_time
        }
        
    except Exception as e:
        print(f"❌ Error in V166 processing: {e}")
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
        print(f"🚀 V1.6.6.6 Lambda Function invoked")
        print(f"Event type: {type(event)}")
        print(f"Event keys: {list(event.keys()) if isinstance(event, dict) else 'Not a dict'}")
        print(f"Event preview: {str(event)[:200]}...")
        
        # Handle different event types
        if isinstance(event, dict) and ('requestContext' in event):
            # Lambda Function URL event
            request_context = event.get('requestContext', {})
            http_info = request_context.get('http', {})
            http_method = http_info.get('method', 'GET')
            path = http_info.get('path', '/')
            body = event.get('body', '{}')
            
            print(f"🔍 Function URL Event Structure:")
            print(f"  requestContext: {request_context}")
            print(f"  http_info: {http_info}")
            print(f"  http_method: {http_method}")
            print(f"  path: {path}")
            print(f"  body: {body}")
            
            # Parse body
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                except:
                    body = {}
            
            print(f"🌐 API Gateway request: {http_method} {path}")
            
            # Handle different endpoints
            start_time = time.time()
            
            if http_method == 'OPTIONS':
                return handle_options(event)
            
            if http_method == 'GET' and path == '/health':
                elapsed = time.time() - start_time
                print(f"[LOG] Health check completed in {elapsed:.3f}s")
                return create_response({"status": "healthy"}, event=event)
                
            elif http_method == 'GET' and path == '/debug/files':
                    # Debug endpoint to check file access
                    print("🔍 Debug files endpoint called")
                    
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
                    
                    elapsed = time.time() - start_time
                    print(f"[LOG] Debug files endpoint completed in {elapsed:.3f}s")
                    return create_response(debug_info, event=event)
                
            elif http_method == 'GET' and path == '/courses':
                elapsed = time.time() - start_time
                print(f"[LOG] Courses endpoint completed in {elapsed:.3f}s")
                return create_response({"courses": ["decision","marketing","strategy"]}, event=event)
                
            elif http_method == 'GET' and path.startswith('/api/course/'):
                # Extract course ID from path
                course_id = path.split('/')[-1]
                try:
                    with open(f"courses/{course_id}/ui_metadata.json") as f:
                        ui_metadata = json.load(f)
                    elapsed = time.time() - start_time
                    print(f"[LOG] UI metadata endpoint completed in {elapsed:.3f}s")
                    return create_response(ui_metadata, event=event)
                except Exception as e:
                    elapsed = time.time() - start_time
                    print(f"[LOG] UI metadata endpoint failed in {elapsed:.3f}s: {str(e)}")
                    return create_response(
                        {"error": f"Failed to load UI metadata: {str(e)}"}, 
                        status="error", 
                        status_code=500, 
                        event=event
                    )
                
            elif http_method == 'POST' and path == '/query':
                print(f"📦 Parsed body: {body}")
                
                if not body or 'query' not in body:
                    return create_response(
                        {"error": "Query is required"}, 
                        status="error", 
                        status_code=400,
                        event=event
                    )
                
                query = body['query']
                course_id = body.get('course_id', DEFAULT_COURSE)
                
                print(f"📚 Frontend requested course: {course_id}")
                print("🔄 Using Fixed V166 Query Engine")
                
                # Process query using fixed V166 implementation
                response_data = process_query_v166_fixed(query)
                
                elapsed = time.time() - start_time
                print(f"[LOG] Query processing completed in {elapsed:.3f}s")
                print("✅ Fixed V166 Query processed successfully.")
                return create_response(response_data, event=event)
                
            else:
                # Unknown endpoint
                elapsed = time.time() - start_time
                print(f"[LOG] Unknown endpoint {http_method} {path} completed in {elapsed:.3f}s")
                return create_response(
                    {"error": f"Not found: {http_method} {path}"}, 
                    status="error", 
                    status_code=404,
                    event=event
                )
        
        else:
            # Direct Lambda invocation





            start_time = time.time()
            elapsed = time.time() - start_time
            print(f"[LOG] Direct Lambda invocation completed in {elapsed:.3f}s")
            print("📞 Direct Lambda invocation detected")
            return create_response({
             
                "message": "V1.6.6.6 Lambda function is running",
                "event_type": "Direct Invocation"
            }, event=event)
            
    except Exception as e:
        print(f"❌ Lambda handler error: {e}")
        traceback.print_exc()
        
        return create_response(
            {"error": "Internal server error", "message": str(e)}, 
            status="error", 
            status_code=500,
            event=event
        )

if __name__ == '__main__':
    # Local development server
    print("🧪 Running V1.6.6.6 Lambda Function locally for testing")
    app.run(debug=True, host='0.0.0.0', port=5000)
