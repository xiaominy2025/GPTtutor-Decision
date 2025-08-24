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
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    # Will handle gracefully with fallback

app = Flask(__name__)

# === CORS CONFIGURATION - V1.6.6.6 PRODUCTION ===
PROD_ALLOWED_ORIGINS = {
    "https://engentlabs.com",
    "https://www.engentlabs.com",
    "https://d1y6s1joavl0j7.cloudfront.net"
}
DEFAULT_ORIGIN = "https://engentlabs.com"
VERSION = "V1.6.6.6"

def pick_origin(event):
    try:
        origin = event.get("headers", {}).get("origin") or event.get("headers", {}).get("Origin")
        if origin in PROD_ALLOWED_ORIGINS:
            return origin
    except Exception:
        pass
    return DEFAULT_ORIGIN

def cors_headers(event):
    origin = pick_origin(event)
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }

def create_response(data, status="success", status_code=200, event=None):
    """Standardized response wrapper for all endpoints"""
    headers = cors_headers(event) if event else {
        "Access-Control-Allow-Origin": "https://engentlabs.com",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Max-Age": "86400",
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

def handle_options(event):
    headers = cors_headers(event)
    headers.pop("Content-Type", None)  # Remove Content-Type for OPTIONS response
    
    return {
        "statusCode": 200,
        "headers": headers,
        "body": ""
    }

# === V166 CORE COMPONENTS ===

# Course configuration
DEFAULT_COURSE = "decision"

# V166 System Prompt (Exact V166 Format)
SYSTEM_PROMPT_V166 = """You are a Decision Coach GPT. Your role is to help students make better decisions by thinking clearly, strategically, and—when appropriate—analytically.

CRITICAL: You must format your response with EXACTLY these section headers:

**Strategic Thinking Lens**

Provide a cohesive strategic narrative that flows naturally in paragraph form. Avoid bullet points or lists. Tell a story of how to approach this decision strategically. Identify the decision type and key challenge. When the decision involves uncertainty, trade-offs, optimization, or forecasting, weave relevant analytical tools naturally into the narrative (e.g., decision trees, Monte Carlo simulation, scenario analysis, SWOT analysis, sensitivity analysis, linear optimization, competitive advantage analysis).

**Follow-up Prompts**

Offer exactly 3 thoughtful questions to help the student apply the strategy. Format as numbered questions:
1. [Question about specific application]
2. [Question about implementation]  
3. [Question about monitoring/adaptation]

**Concepts/Tools**

List relevant decision-making concepts and tools mentioned, with brief definitions. Format as:
- **Concept Name**: Brief definition explaining how it helps with decision-making.

Focus on insight, structure, and practical application. Avoid generic motivational advice."""

def get_openai_key():
    """Get OpenAI API key from environment variable"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found in environment variables")
        raise ValueError("OpenAI API key not configured")
    return api_key

def compute_relevance_score(query: str) -> Tuple[float, str]:
    """Simple relevance scoring for decision-making queries"""
    query_lower = query.lower()
    
    # Decision-making keywords
    decision_keywords = [
        'decision', 'choose', 'select', 'evaluate', 'compare', 'analyze',
        'strategy', 'plan', 'optimize', 'risk', 'uncertainty', 'trade-off',
        'should i', 'how to', 'what factors', 'consider', 'assess'
    ]
    
    # Business/strategy keywords
    business_keywords = [
        'business', 'company', 'organization', 'market', 'competition',
        'investment', 'cost', 'benefit', 'profit', 'revenue', 'growth',
        'production', 'supply', 'demand', 'pricing', 'strategy',
        'salary', 'compensation', 'job', 'career', 'employment', 'negotiate'
    ]
    
    score = 0
    debug_info = []
    
    # Check for decision-making keywords
    for keyword in decision_keywords:
        if keyword in query_lower:
            score += 1
            debug_info.append(f"decision_keyword: {keyword}")
    
    # Check for business keywords
    for keyword in business_keywords:
        if keyword in query_lower:
            score += 0.5
            debug_info.append(f"business_keyword: {keyword}")
    
    return score, ", ".join(debug_info)

def detect_concepts_in_query(query: str) -> List[Tuple[str, str]]:
    """Detect relevant concepts in the query"""
    query_lower = query.lower()
    detected_concepts = []
    
    # Simple concept detection based on keywords
    concept_keywords = {
        "swot analysis": ["swot", "strengths", "weaknesses", "opportunities", "threats"],
        "decision tree": ["decision tree", "tree analysis", "branching"],
        "cost-benefit analysis": ["cost benefit", "cost-benefit", "compare costs"],
        "risk assessment": ["risk", "uncertainty", "threat", "assessment"],
        "scenario planning": ["scenario", "planning", "future", "what if"],
        "optimization": ["optimize", "optimization", "best", "efficient"],
        "supply chain": ["supply chain", "logistics", "procurement", "distribution"]
    }
    
    for concept, keywords in concept_keywords.items():
        for keyword in keywords:
            if keyword in query_lower:
                detected_concepts.append((concept, f"Relevant concept for {concept}"))
                break
    
    return detected_concepts

def extract_application_field(query: str) -> str:
    """Extract the application field from the query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["production", "manufacturing", "operations"]):
        return "Production and Operations Management"
    elif any(word in query_lower for word in ["investment", "finance", "financial"]):
        return "Financial Decision Making"
    elif any(word in query_lower for word in ["marketing", "market", "customer"]):
        return "Marketing Strategy"
    elif any(word in query_lower for word in ["job", "career", "employment", "salary"]):
        return "Career and Employment Decisions"
    elif any(word in query_lower for word in ["business", "strategy", "competitive"]):
        return "Business Strategy"
    else:
        return "General Decision Making"

def process_query_v166_fixed(query: str) -> dict:
    """
    Fixed V166 Query Processing - Returns formatted text response
    """
    try:
        print(f"🔄 V166 Processing Query: {query}")
        
        # Step 1: Relevance scoring
        score, debug_info = compute_relevance_score(query)
        print(f"📊 Relevance Score: {score}, Debug: {debug_info}")
        
        if score < 0.5:  # Much lower threshold for testing
            print(f"⚠️ Query rejected due to low relevance. Debug: {debug_info}")
            return {
                "answer": "⚠️ This question doesn't appear to be related to decision-making. Try asking about decision-making tools, strategies, or business decisions.",
                "strategicThinkingLens": "⚠️ This question doesn't appear to be related to decision-making. Try asking about decision-making tools, strategies, or business decisions.",
                "followUpPrompts": "",
                "conceptsToolsPractice": "",
                "model": "relevance_filter",
                "processing_time": 0.0
            }
        
        # Step 2: Build context-aware user message
        user_message = f"Query: {query}\n\n"
        
        # Add application field context
        application_field = extract_application_field(query)
        user_message += f"Application field: {application_field}\n\n"
        
        # Step 3: OpenAI API call with V166 system prompt
        try:
            openai_api_key = get_openai_key()
            print(f"🔑 OpenAI API key retrieved: {openai_api_key[:10]}...")
            openai.api_key = openai_api_key
            
            start_time = time.time()
            
            print("🤖 Making OpenAI API call...")
            print(f"📝 User message: {user_message}")
            
            response_obj = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_V166},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            processing_time = time.time() - start_time
            answer = response_obj.choices[0].message.content.strip()
            
            print(f"✅ OpenAI Response received in {processing_time:.2f}s")
            print(f"📝 Answer length: {len(answer)} characters")
            print(f"📄 Answer preview: {answer[:200]}...")
            
        except Exception as openai_error:
            print(f"❌ OpenAI API call failed: {openai_error}")
            print(f"❌ Error type: {type(openai_error)}")
            traceback.print_exc()
            raise openai_error
        
        # Step 4: Parse the answer into structured format
        strategic_thinking_lens = ""
        follow_up_prompts = ""
        concepts_tools_practice = ""
        
        # Simple parsing of the answer sections
        sections = answer.split("**")
        for i, section in enumerate(sections):
            if "Strategic Thinking Lens" in section:
                if i + 1 < len(sections):
                    strategic_thinking_lens = sections[i + 1].strip()
            elif "Follow-up Prompts" in section:
                if i + 1 < len(sections):
                    follow_up_prompts = sections[i + 1].strip()
            elif "Concepts/Tools" in section:
                if i + 1 < len(sections):
                    concepts_tools_practice = sections[i + 1].strip()
        
        # Return structured response with required keys
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
            "conceptsToolsPractice": "",
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
