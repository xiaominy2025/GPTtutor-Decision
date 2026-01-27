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
from difflib import SequenceMatcher

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

# === Continuation (best-effort, in-memory) ===
CONTINUATION_ENABLED = os.getenv("CONTINUATION_ENABLED", "false").lower() == "true"
CONTINUATION_TTL_MINUTES = int(os.getenv("CONTINUATION_TTL_MINUTES", "90"))
CONTINUATION_SIMILARITY_THRESHOLD = float(os.getenv("CONTINUATION_SIMILARITY_THRESHOLD", "0.96"))
CONTINUATION_LEN_RATIO_MIN = float(os.getenv("CONTINUATION_LEN_RATIO_MIN", "0.9"))
CONTINUATION_MAX_CAPSULE_CHARS = int(os.getenv("CONTINUATION_MAX_CAPSULE_CHARS", "900"))
CONTINUATION_LOGGING = os.getenv("CONTINUATION_LOGGING", "false").lower() == "true"

_CONTINUATION_SNAPSHOTS: Dict[str, Dict[str, Any]] = {}

def _continuation_key(user_id: str, course_id: str) -> str:
    user_part = (user_id or "default").strip()
    course_part = (course_id or DEFAULT_COURSE).strip()
    return f"{user_part}::{course_part}"

def _normalize_prompt(text: str) -> str:
    if not text:
        return ""
    s = text.strip().lower()
    s = re.sub(r"^[\-\*\•]\s*", "", s)
    s = re.sub(r"^\d+[\.\)]\s*", "", s)
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(" .,!?:;")
    return s

def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def _match_followup(query_norm: str, followups_norm: List[str]) -> Dict[str, Any]:
    if not query_norm or not followups_norm:
        return {"match": False, "score": 0.0, "guards": ["empty"]}
    for cand in followups_norm:
        if query_norm == cand:
            return {"match": True, "score": 1.0, "guards": []}
    best_score = 0.0
    best_candidate = ""
    for cand in followups_norm:
        score = _similarity(query_norm, cand)
        if score > best_score:
            best_score = score
            best_candidate = cand
    guards = []
    q_len = len(query_norm)
    c_len = len(best_candidate)
    if max(q_len, c_len) == 0:
        guards.append("length_zero")
    else:
        len_ratio = min(q_len, c_len) / max(q_len, c_len)
        if len_ratio < CONTINUATION_LEN_RATIO_MIN:
            guards.append("length_ratio")
    q_first = query_norm.split()[0] if query_norm.split() else ""
    c_first = best_candidate.split()[0] if best_candidate.split() else ""
    if q_first and c_first and q_first != c_first:
        guards.append("first_token")
    is_match = best_score >= CONTINUATION_SIMILARITY_THRESHOLD and not guards
    return {"match": is_match, "score": best_score, "guards": guards}

def _get_snapshot(key: str) -> Dict[str, Any] | None:
    snap = _CONTINUATION_SNAPSHOTS.get(key)
    if not snap:
        return None
    ts = snap.get("timestamp")
    if not ts:
        _CONTINUATION_SNAPSHOTS.pop(key, None)
        return None
    age_sec = time.time() - ts
    if age_sec > (CONTINUATION_TTL_MINUTES * 60):
        _CONTINUATION_SNAPSHOTS.pop(key, None)
        return None
    return snap

def _set_snapshot(key: str, snap: Dict[str, Any]) -> None:
    _CONTINUATION_SNAPSHOTS[key] = snap

def _build_lens_capsule(lens: str) -> str:
    if not lens:
        return ""
    s = re.sub(r"\s+", " ", lens.strip())
    if len(s) > CONTINUATION_MAX_CAPSULE_CHARS:
        s = s[:CONTINUATION_MAX_CAPSULE_CHARS].rstrip()
    return s

def pick_origin(event):
    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin")
    return origin if origin in ALLOWED_ORIGINS else "https://engentlabs.com"

def create_response(data, status="success", status_code=200, event=None):
    """Standardized response wrapper for all endpoints (Function URL adds CORS)."""
    headers = {
        "Content-Type": "application/json"
    }

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps({
            "data": data,
            "status": status,
            "version": "V1.6.6.6",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    }

def create_rejection_response(message: str, event=None):
    """Memo-compliant rejection response (no data envelope, no CORS headers)."""
    headers = {
        "Content-Type": "application/json"
    }
    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps({
            "status": "rejected",
            "message": message,
            "version": "V1.6.6.6",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    }

def create_error_response(message: str, status_code: int = 500, event=None):
    """Memo-compliant error response (no data envelope, no CORS headers)."""
    headers = {
        "Content-Type": "application/json"
    }
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps({
            "status": "error",
            "error": message,
            "version": "V1.6.6.6",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
    }

def get_cors_headers(event):
    """Get CORS headers for the given event"""
    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin")
    
    # Always return CORS headers, even for invalid origins (browser will handle)
    cors_origin = origin if origin in ALLOWED_ORIGINS else "https://engentlabs.com"
    
    return {
        "Access-Control-Allow-Origin": cors_origin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin"
    }

def handle_options(event):
    """Handle OPTIONS (Function URL normally handles CORS automatically)."""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": ""
    }

# === V166 CORE COMPONENTS ===

# Course configuration
DEFAULT_COURSE = "decision"

# Note: Using authoritative SYSTEM_PROMPT_ANALYTICS from query_engine.py

# Note: Removed duplicate functions - now using authoritative query_engine methods





def process_query_v166_fixed(query: str, generation_context: str | None = None) -> dict:
    """
    V1.6.6: Fixed Query Processing - Uses authoritative query_engine.process_query_structured()
    Eliminates double work by using structured data instead of re-parsing GPT response.
    """
    try:
        if not hasattr(query_engine, 'process_query_structured'):
            raise Exception("query_engine.process_query_structured method not available")
        
        start_time = time.time()
        try:
            structured_response = query_engine.process_query_structured(query, generation_context=generation_context)
        except Exception as qe:
            traceback.print_exc()
            raise qe
            
        processing_time = time.time() - start_time
        structured_response["processing_time"] = processing_time

        # ✅ Normalize followUpPrompts to always be a list of strings
        def normalize_prompts(prompts):
            if prompts is None:
                return []
            if isinstance(prompts, list):
                return [str(p).strip() for p in prompts if str(p).strip()]
            if isinstance(prompts, str):
                return [prompts.strip()] if prompts.strip() else []
            return []

        # Accept both camelCase and lowercase-u for safety
        prompts = (
            structured_response.get("followUpPrompts") or
            structured_response.get("followupPrompts") or
            []
        )
        structured_response["followUpPrompts"] = normalize_prompts(prompts)

        if isinstance(structured_response.get("answer", ""), str) and structured_response["answer"].startswith("⚠️ This question doesn't appear to be related to the course"):
            return {
                "answer": structured_response["answer"],
                "strategicThinkingLens": structured_response["answer"],
                "followUpPrompts": [],
                "conceptsToolsPractice": [],
                "model": "relevance_filter",
                "processing_time": processing_time,
                "status": "rejected"
            }
        
        return structured_response
        
    except Exception as e:
        traceback.print_exc()
        return {
            "status": "error",
            "error_details": str(e),
            "message": "Something went wrong. Please try again."
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
                # Wrap in standard envelope per frontend memo
                return create_response(
                    {
                        "status": "healthy",
                        "version": "V1.6.6.6",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    },
                    event=event
                )
                
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
                return create_response({
                    "courses": ["decision","marketing","strategy"],
                    "default_course": DEFAULT_COURSE
                }, event=event)
                
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
                user_id = body.get('user_id', 'default')
                if not isinstance(user_id, str):
                    user_id = str(user_id)
                if not isinstance(course_id, str):
                    course_id = DEFAULT_COURSE
                
                try:
                    generation_context = None
                    if CONTINUATION_ENABLED:
                        key = _continuation_key(user_id, course_id)
                        snap = _get_snapshot(key)
                        if snap and snap.get("course_id") == course_id:
                            query_norm = _normalize_prompt(query)
                            followups_norm = snap.get("followups_norm", [])
                            match = _match_followup(query_norm, followups_norm)
                            if match["match"] and snap.get("strategic_lens_capsule"):
                                generation_context = snap["strategic_lens_capsule"]
                            if CONTINUATION_LOGGING:
                                age_sec = time.time() - snap.get("timestamp", time.time())
                                print({
                                    "continuation": True,
                                    "match": match["match"],
                                    "score": match["score"],
                                    "guards": match["guards"],
                                    "snapshot_age_sec": round(age_sec, 2),
                                    "turn_id": snap.get("turn_id"),
                                    "course_match": True
                                })
                        elif CONTINUATION_LOGGING:
                            print({"continuation": True, "match": False, "reason": "no_snapshot"})

                    # Process query using fixed V166 implementation
                    response_data = process_query_v166_fixed(query, generation_context=generation_context)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return create_error_response(
                        f"Query processing failed: {str(e)}",
                        status_code=500,
                        event=event
                    )
                
                # Propagate top-level status per memo (success/rejected/error)
                outer_status = "success"
                if isinstance(response_data, dict):
                    resp_status = response_data.get("status")
                    if resp_status in ("rejected", "error"):
                        outer_status = resp_status
                if outer_status == "rejected":
                    # Use memo-compliant rejection (no data envelope)
                    rejection_message = response_data.get("answer") or response_data.get("message") or "This question appears to be outside the scope."
                    return create_rejection_response(rejection_message, event=event)
                if outer_status == "error":
                    # Use memo-compliant error (no data envelope)
                    error_message = response_data.get("error_details") or response_data.get("message") or "Internal server error."
                    return create_error_response(error_message, status_code=500, event=event)
                if CONTINUATION_ENABLED and isinstance(response_data, dict):
                    lens = response_data.get("strategicThinkingLens") or ""
                    followups = response_data.get("followUpPrompts") or []
                    if isinstance(followups, str):
                        followups = [followups] if followups.strip() else []
                    if lens and followups:
                        lens_capsule = _build_lens_capsule(lens)
                        if lens_capsule:
                            key = _continuation_key(user_id, course_id)
                            prev = _get_snapshot(key)
                            next_turn_id = (prev.get("turn_id", 0) + 1) if prev else 1
                            norm_followups = [
                                _normalize_prompt(p) for p in followups if isinstance(p, str) and p.strip()
                            ]
                            snap = {
                                "strategic_lens_capsule": lens_capsule,
                                "followups_raw": followups,
                                "followups_norm": [p for p in norm_followups if p],
                                "timestamp": time.time(),
                                "turn_id": next_turn_id,
                                "course_id": course_id,
                                "user_id": user_id
                            }
                            _set_snapshot(key, snap)
                return create_response(response_data, status=outer_status, event=event)
                
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
