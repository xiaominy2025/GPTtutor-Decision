#!/usr/bin/env python3
"""
AWS Lambda Function with Complete V166 Query Engine Integration
V1.6.6.6 Final Version - Complete Feature Parity with api_server.py
"""

import json
import time
import os
import sys
import re
import traceback
from typing import List, Tuple, Dict, Any
import boto3

# Flask for Lambda compatibility
from flask import Flask, request, jsonify
from flask_cors import CORS

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

# Configure CORS with specific settings for production
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", 
              "https://engentlabs.com", "https://www.engentlabs.com"],
     allow_headers=["Content-Type", "Authorization", "Origin"],
     methods=["GET", "POST", "OPTIONS"],
     max_age=3600)

# === V166 CORE COMPONENTS ===

# Course configuration
DEFAULT_COURSE = "decision"

# V166 Frameworks and Concept Glossary (Essential subset for Lambda)
FRAMEWORKS = {
    "strategic analysis": "Strategic frameworks for analyzing competitive positioning, industry structure, and business strategy decisions.",
    "analytical tools": "Mathematical and statistical tools for optimization, forecasting, simulation, and data-driven decision making.",
    "human behaviors": "Psychological frameworks for understanding cognitive biases, decision patterns, and behavioral economics in decision making.",
    "negotiation frameworks": "Structured approaches for bargaining, value creation, and reaching agreements in competitive situations.",
    "risk assessment": "Systematic frameworks for evaluating uncertainty, threats, and opportunities in decision contexts."
}

# Core concept glossary (subset of most important concepts)
CONCEPT_GLOSSARY = {
    "scenario analysis": {"definition": "A modeling approach that explores different future possibilities and outcomes to prepare for uncertainty in decision-making", "core": True, "aliases": ['scenario planning', 'model uncertainty', 'uncertainty modeling']},
    "monte carlo simulation": {"definition": "A statistical modeling tool that uses random sampling to simulate thousands of potential outcomes under uncertainty for risk analysis and production planning", "core": True, "aliases": ['monte carlo', 'simulation modeling', 'statistical simulation', 'uncertainty simulation', 'probabilistic simulation', 'simulate', 'scenarios', 'thousands', 'random sampling', 'simulate uncertainty']},
    "sensitivity analysis": {"definition": "A technique to determine how different values of an input affect a particular outcome under a given set of assumptions", "core": True, "aliases": ['sensitivity testing', 'what-if analysis', 'parameter analysis', 'change parameters', 'different values', 'affects outcome', 'test different inputs', 'parameter sensitivity', 'what if']},
    "decision tree": {"definition": "A visual tool that maps out different options and their potential outcomes", "core": True, "aliases": ['decision mapping', 'option tree', 'outcome mapping', 'tree analysis', 'decision branching']},
    "swot analysis": {"definition": "A framework that helps identify strengths, weaknesses, opportunities, and threats", "core": True, "aliases": ['swot', 'strengths weaknesses', 'opportunities threats', 'strengths weaknesses opportunities threats', 'swot analysis']},
    "linear optimization": {"definition": "A mathematical method for maximizing or minimizing a linear objective function, subject to linear equality and inequality constraints", "core": True, "aliases": ['linear programming', 'optimization', 'mathematical optimization', 'lp method', 'optimize', 'constraints', 'resource allocation', 'optimize under constraints']},
    "risk assessment": {"definition": "Systematic evaluation of potential threats and their impact on decision outcomes", "core": True, "aliases": ['risk evaluation', 'risk analysis', 'threat assessment']},
    "strategic framing": {"definition": "Structuring the decision problem to clarify objectives and alternatives", "core": True, "aliases": ['strategic analysis', 'problem framing', 'decision framing', 'structure decision', 'frame problem', 'strategic framing']},
    "supply chain": {"definition": "The network of organizations, people, activities, information, and resources involved in moving a product or service from supplier to customer", "core": True, "aliases": ['supply chain management', 'logistics', 'procurement', 'distribution', 'supply chain optimization', 'supply chain disruption']},
    "competitive advantage analysis": {"definition": "A strategic evaluation of factors that allow an organization to outperform its competitors", "core": True, "aliases": ['competitive advantage', 'competitive analysis', 'advantage analysis']},
}

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
    """Securely retrieve OpenAI API key from AWS Secrets Manager"""
    secret_name = "arn:aws:secretsmanager:us-east-2:771049112957:secret:engentlabs/openai_api_key-gTpV3u"
    region_name = "us-east-2"
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    print("🔐 Retrieving OpenAI API key from AWS Secrets Manager...")
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(get_secret_value_response['SecretString'])

    openai_api_key = secret.get('OPENAI_API_KEY')

    # If not found, check if the key is malformed (key contains the API key)
    if not openai_api_key:
        for key in secret.keys():
            if 'OPENAI_API_KEY' in key and 'sk-' in key:
                # Extract API key from malformed key name
                api_key_part = key.split(' : ')[-1] if ' : ' in key else key.split(':')[-1]
                if api_key_part.startswith('sk-'):
                    openai_api_key = api_key_part
                    print("🔧 Extracted API key from malformed secret structure")
                    break

    if not openai_api_key:
        raise Exception("OPENAI_API_KEY not found in secret")

    print("✅ Successfully retrieved OpenAI API key from Secrets Manager")
    return openai_api_key

def detect_concepts_in_query(query: str) -> List[Tuple[str, str]]:
    """
    V166 Concept Detection - Simplified version for Lambda
    Returns list of (concept_name, definition) tuples
    """
    query_lower = query.lower()
    detected_concepts = []
    
    for concept_name, concept_data in CONCEPT_GLOSSARY.items():
        definition = concept_data["definition"]
        aliases = concept_data.get("aliases", [])
        
        # Check if concept name or any alias appears in query
        if concept_name in query_lower:
            detected_concepts.append((concept_name, definition))
        else:
            for alias in aliases:
                if alias.lower() in query_lower:
                    detected_concepts.append((concept_name, definition))
                    break
    
    # Return top 3 most relevant concepts
    return detected_concepts[:3]

def extract_application_field(query: str) -> str:
    """
    V166 Application Field Detection - Updated with 12+1 standardized fields
    """
    query_lower = query.lower()
    
    # 4. Technology Management (check first - most specific)
    tech_keywords = ['technology', 'digital', 'software', 'platform', 'artificial intelligence', 'automation', 'cybersecurity', 'data science']
    # Special case for AI - check as whole word
    if any(word in query_lower for word in tech_keywords) or ' ai ' in f' {query_lower} ' or query_lower.startswith('ai ') or query_lower.endswith(' ai'):
        return "Technology Management"
    
    # 3. Financial Decision-Making (check early - specific terms)
    if any(word in query_lower for word in ['invest', 'investment', 'financial', 'budget', 'cost', 'pricing', 'valuation', 'capital', 'funding', 'expenses', 'profitability']):
        return "Financial Decision-Making"
    
    # 10. Education & Learning (check before product development)
    if any(word in query_lower for word in ['education', 'learning', 'school', 'teaching', 'curriculum', 'training', 'students']):
        return "Education & Learning"
    
    # 6. People, Talent & Career (check before general business terms)
    if any(word in query_lower for word in ['hire', 'hiring', 'recruitment', 'employee', 'staff', 'team', 'leadership', 'management', 'culture', 'retention', 'job', 'offer', 'employment', 'career', 'salary', 'compensation', 'benefits', 'talent']):
        return "People, Talent & Career"
    
    # 1. Business & Markets (check before product development)
    if any(word in query_lower for word in ['business', 'company', 'market', 'competition', 'growth', 'branding', 'marketing', 'customer', 'sales', 'revenue', 'profit']):
        return "Business & Markets"
    
    # 8. Product Development & Innovation (check after more specific terms)
    if any(word in query_lower for word in ['product', 'design', 'prototype', 'testing', 'features', 'roadmap', 'user feedback']):
        return "Product Development & Innovation"
    
    # 2. Operations Management
    if any(word in query_lower for word in ['production', 'operations', 'logistics', 'supply', 'manufacturing', 'inventory', 'process', 'workflow']):
        return "Operations Management"
    
    # 5. Risk, Crisis & Resilience
    if any(word in query_lower for word in ['risk', 'uncertainty', 'volatile', 'unpredictable', 'threat', 'mitigation', 'contingency', 'disaster', 'emergency', 'safety', 'resilience']):
        return "Risk, Crisis & Resilience"
    
    # 7. Policy & Regulatory
    if any(word in query_lower for word in ['policy', 'regulation', 'compliance', 'legal', 'government', 'legislation', 'standards', 'ethics']):
        return "Policy & Regulatory"
    
    # 9. Sustainability & Environment
    if any(word in query_lower for word in ['sustainability', 'environmental', 'climate', 'carbon', 'renewable', 'conservation', 'green']):
        return "Sustainability & Environment"
    
    # 11. Healthcare & Medical
    if any(word in query_lower for word in ['healthcare', 'medical', 'patient', 'treatment', 'diagnosis', 'clinical', 'hospital', 'therapy']):
        return "Healthcare & Medical"
    
    # 12. Military & Defense Decisions
    if any(word in query_lower for word in ['military', 'defense', 'army', 'navy', 'air force', 'marine', 'security', 'mission', 'tactical', 'combat', 'deployment', 'training exercise']):
        return "Military & Defense Decisions"
    
    # 13. General Decision-Making (default)
    return "General Decision-Making"

def compute_relevance_score(query: str) -> Tuple[int, dict]:
    """
    V166 Relevance Scoring - Simplified version for Lambda
    Returns (score, debug_info)
    """
    query_lower = query.lower()
    
    # Decision-making keywords
    decision_keywords = ['decision', 'choose', 'select', 'option', 'alternative', 'strategy', 'plan', 'approach']
    decision_score = sum(1 for keyword in decision_keywords if keyword in query_lower)
    
    # Business/analytical keywords
    business_keywords = ['business', 'market', 'competition', 'analysis', 'optimization', 'risk', 'uncertainty']
    business_score = sum(1 for keyword in business_keywords if keyword in query_lower)
    
    # Concept detection
    concepts = detect_concepts_in_query(query)
    concept_score = len(concepts)
    
    # Application field detection
    application_field = extract_application_field(query)
    field_score = 1 if application_field != "General Decision-Making" else 0
    
    total_score = decision_score + business_score + concept_score + field_score
    
    debug_info = {
        "decision_score": decision_score,
        "business_score": business_score,
        "concept_score": concept_score,
        "field_score": field_score,
        "concepts": [c[0] for c in concepts],
        "application_field": application_field,
        "total_score": total_score
    }
    
    return total_score, debug_info

def extract_tools_from_section(answer: str) -> List[dict]:
    """
    V166 Tool Extraction - Extract concepts and tools from the response
    Returns list of {"term": str, "definition": str} objects
    """
    tools = []
    
    # Look for Concepts/Tools section (exact V166 format with flexible spacing)
    concepts_match = re.search(r'\*\*Concepts/Tools\*\*\s*\n+(.*?)(?=\n\n\*\*|\Z)', answer, re.DOTALL)
    if not concepts_match:
        # Fallback: Look for alternative formats
        concepts_match = re.search(r'Concepts/Tools:\s*\n+(.*?)(?=\n\n|\Z)', answer, re.DOTALL)
    
    if concepts_match:
        concepts_section = concepts_match.group(1).strip()
        
        # Extract V166 format: "- **Tool Name**: Definition"
        tool_matches = re.findall(r'-\s*\*\*([^*]+)\*\*:\s*([^\n]+)', concepts_section)
        for tool_name, definition in tool_matches:
            tools.append({
                "term": tool_name.strip(),
                "definition": definition.strip()
            })
        
        # Fallback: Extract simple format "- Tool Name: Definition"
        if not tools:
            simple_matches = re.findall(r'-\s*([^:]+?):\s*([^\n]+)', concepts_section)
            for tool_name, definition in simple_matches:
                # Skip if it looks like a question or has numbers
                if not re.match(r'^\d+\.', tool_name.strip()) and '?' not in tool_name:
                    tools.append({
                        "term": tool_name.strip(),
                        "definition": definition.strip()
                    })
    
    return tools

def extract_follow_up_prompts(answer: str) -> List[str]:
    """
    V166 Follow-up Prompts Extraction - Extract clickable questions
    """
    prompts = []
    
    # Look for Follow-up Prompts section (exact V166 format with flexible spacing)
    prompts_match = re.search(r'\*\*Follow-up Prompts\*\*\s*\n+(.*?)(?=\n\n\*\*|\Z)', answer, re.DOTALL)
    if not prompts_match:
        # Fallback: Look for alternative question sections
        prompts_match = re.search(r'To apply this strategy to your context:\s*\n+(.*?)(?=\n\n|\Z)', answer, re.DOTALL)
    
    if prompts_match:
        prompts_section = prompts_match.group(1).strip()
        
        # Extract numbered questions (V166 format: "1. Question?")
        question_matches = re.findall(r'\d+\.\s*([^?\n]+\?)', prompts_section)
        for q in question_matches:
            clean_q = q.strip()
            if clean_q not in prompts:
                prompts.append(clean_q)
        
        # If no numbered questions, look for bullet points
        if not prompts:
            bullet_matches = re.findall(r'-\s*([^?\n]+\?)', prompts_section)
            for q in bullet_matches:
                clean_q = q.strip()
                if clean_q not in prompts:
                    prompts.append(clean_q)
        
        # Final fallback: any question in the section
        if not prompts:
            all_questions = re.findall(r'([^.!?\n]*\?)', prompts_section)
            for q in all_questions:
                clean_q = re.sub(r'^\d+\.\s*|-\s*', '', q.strip())
                if len(clean_q) > 10 and clean_q not in prompts:  # Filter out short fragments
                    prompts.append(clean_q)
    
    # Return exactly 3 prompts
    return prompts[:3]

def process_query_v166(query: str) -> dict:
    """
    Complete V166 Query Processing - Main processing function
    Returns structured response matching api_server.py format
    """
    try:
        print(f"🔄 V166 Processing Query: {query}")
        
        # Step 1: Relevance scoring (V166 abuse prevention)
        score, debug_info = compute_relevance_score(query)
        print(f"📊 Relevance Score: {score}, Debug: {debug_info}")
        
        if score < 2:
            print(f"⚠️ Query rejected due to low relevance. Debug: {debug_info}")
            return {
                "status": "rejected",
                "message": "⚠️ This question doesn't appear to be related to decision-making. Try asking about decision-making tools, strategies, or business decisions.",
                "data": {
                    "query": query,
                    "course_id": DEFAULT_COURSE,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "model": "gpt-3.5-turbo",
                    "processing_time": 0.1,
                    "conceptsToolsPractice": [],
                    "followUpPrompts": []
                }
            }
        
        # Step 2: Concept detection
        concepts = detect_concepts_in_query(query)
        print(f"🔍 Detected Concepts: {[c[0] for c in concepts]}")
        
        # Step 3: Application field detection
        application_field = extract_application_field(query)
        print(f"🎯 Application Field: {application_field}")
        
        # Step 4: Build context-aware user message
        user_message = f"Query: {query}\n\n"
        
        # Add relevant concepts as context
        if concepts:
            concept_context = "Relevant concepts to consider:\n"
            for concept_name, definition in concepts:
                concept_context += f"- {concept_name}: {definition}\n"
            user_message += concept_context + "\n"
        
        # Add application field context
        user_message += f"Application field: {application_field}\n\n"
        
        # Step 5: OpenAI API call with V166 system prompt
        openai_api_key = get_openai_key()
        openai.api_key = openai_api_key
        
        start_time = time.time()
        
        print("🤖 Making OpenAI API call...")
        response_obj = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_V166},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        processing_time = time.time() - start_time
        answer = response_obj.choices[0].message.content.strip()
        
        print(f"✅ OpenAI Response received in {processing_time:.2f}s")
        
        # Step 6: Extract structured components
        concepts_tools_practice = extract_tools_from_section(answer)
        follow_up_prompts = extract_follow_up_prompts(answer)
        
        print(f"📋 Extracted {len(concepts_tools_practice)} concepts/tools")
        print(f"❓ Extracted {len(follow_up_prompts)} follow-up prompts")
        
        # Step 7: Return V166-compatible response
        return {
            "status": "success",
            "data": {
                "answer": answer,
                "query": query,
                "course_id": DEFAULT_COURSE,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": "gpt-3.5-turbo",
                "processing_time": round(processing_time, 2),
                "conceptsToolsPractice": concepts_tools_practice,
                "followUpPrompts": follow_up_prompts
            }
        }
        
    except Exception as e:
        print(f"❌ Error in V166 processing: {e}")
        traceback.print_exc()
        
        # Fallback response
        return {
            "status": "error",
            "message": f"Processing error: {str(e)}",
            "data": {
                "answer": f"I understand you're asking about: {query}\n\nThis appears to be a decision-making question that would benefit from systematic analysis. Consider using frameworks like decision trees, SWOT analysis, or scenario planning to evaluate your options thoroughly.",
                "query": query,
                "course_id": DEFAULT_COURSE,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": "lambda-fallback",
                "processing_time": 0.1,
                "conceptsToolsPractice": [],
                "followUpPrompts": []
            }
        }

# === FLASK ROUTES ===

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "V166-Lambda",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })

@app.route('/courses', methods=['GET'])
def get_courses():
    """Return available courses"""
    return jsonify({
        "success": True,
        "data": {
            "courses": [
                {
                    "course_id": "decision",
                    "name": "Decision Making",
                    "has_glossary": True,
                    "has_prompt_template": True,
                    "has_sections_config": True
                },
                {
                    "course_id": "negotiation",
                    "name": "Negotiation",
                    "has_glossary": True,
                    "has_prompt_template": True,
                    "has_sections_config": True
                },
                {
                    "course_id": "analytics",
                    "name": "Analytics for Decisions",
                    "has_glossary": True,
                    "has_prompt_template": True,
                    "has_sections_config": True
                }
            ],
            "default_course": "decision"
        }
    })

@app.route('/glossary', methods=['GET'])
def get_glossary():
    """Return the glossary for the default course (decision)"""
    try:
        # Return the concept glossary that's already loaded
        return jsonify({
            "success": True,
            "data": {
                "glossary": CONCEPT_GLOSSARY,
                "course_id": "decision",
                "total_concepts": len(CONCEPT_GLOSSARY)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load glossary: {str(e)}"
        }), 500

@app.route('/glossary', methods=['GET', 'POST'])
def get_glossary():
    """
    V1.6.6.6 Glossary endpoint with comprehensive support
    Handles both GET with query params and POST with JSON body
    """
    try:
        course_id = 'decision'  # Default course
        
        if request.method == 'GET':
            # Handle GET /glossary?course_id=decision
            course_id = request.args.get('course_id', 'decision')
        elif request.method == 'POST':
            # Handle POST /glossary with {"course_id": "decision"}
            data = request.get_json() or {}
            course_id = data.get('course_id', 'decision')
        
        # Load course configuration to get glossary
        courses_dir = os.path.join(os.path.dirname(__file__), 'courses')
        course_path = os.path.join(courses_dir, course_id)
        glossary_path = os.path.join(course_path, 'glossary.json')
        
        glossary_data = {}
        if os.path.exists(glossary_path):
            try:
                with open(glossary_path, 'r', encoding='utf-8') as f:
                    glossary_data = json.load(f)
            except Exception as e:
                print(f"❌ Failed to load glossary from {glossary_path}: {e}")
        
        # If no glossary file found, use the built-in concept glossary
        if not glossary_data:
            glossary_data = CONCEPT_GLOSSARY
        
        return jsonify({
            "success": True,
            "data": {
                "glossary": glossary_data,
                "course_id": course_id,
                "total_terms": len(glossary_data)
            }
        })
        
    except Exception as e:
        print(f"❌ Error in glossary endpoint: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to load glossary: {str(e)}"
        }), 500

@app.route('/query', methods=['POST'])
def query_endpoint():
    """
    Main query processing endpoint - V166 Compatible
    """
    try:
        data = request.get_json()
        print("⚡ [V166-LAMBDA] Received POST /query")
        print("    Payload received:", data)

        if not data or 'query' not in data:
            print("❌ Missing 'query' field in request data.")
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400

        query = data['query']
        course_id = data.get('course_id', DEFAULT_COURSE)
        
        print(f"📚 Frontend requested course: {course_id}")
        print("🔄 Using Complete V166 Query Engine")
        
        # Process query using complete V166 implementation
        response = process_query_v166(query)
        
        print("✅ V166 Query processed successfully.")
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error in query endpoint: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

# === LAMBDA HANDLER ===

def parse_lambda_event(event):
    """
    Parse different AWS Lambda event formats and extract HTTP details
    
    Supports:
    - AWS Lambda Function URL
    - API Gateway v1.0 (REST API)
    - API Gateway v2.0 (HTTP API)
    """
    event_type = "unknown"
    http_method = "GET"
    path = "/"
    headers = {}
    body = None
    
    # Detect event format and extract data
    if 'rawPath' in event and 'routeKey' in event:
        # AWS Lambda Function URL format
        event_type = "Lambda Function URL"
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('rawPath', '/')
        headers = event.get('headers', {})
        body = event.get('body')
        
    elif 'requestContext' in event and 'http' in event['requestContext']:
        # API Gateway v2.0 (HTTP API) format
        event_type = "API Gateway v2.0"
        http_context = event['requestContext']['http']
        http_method = http_context.get('method', 'GET')
        path = http_context.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body')
        
    elif 'requestContext' in event and 'resourcePath' in event['requestContext']:
        # API Gateway v1.0 (REST API) format
        event_type = "API Gateway v1.0"
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body')
        
    elif 'httpMethod' in event:
        # Legacy API Gateway format
        event_type = "API Gateway (Legacy)"
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body')
        
    else:
        # Direct Lambda invocation or unknown format
        event_type = "Direct Invocation"
        
    # Parse JSON body if it's a string
    parsed_body = None
    if body:
        if isinstance(body, str):
            try:
                parsed_body = json.loads(body)
            except json.JSONDecodeError:
                print(f"⚠️ Failed to parse JSON body: {body}")
                parsed_body = {}
        else:
            parsed_body = body
    
    return {
        'event_type': event_type,
        'http_method': http_method,
        'path': path,
        'headers': headers,
        'body': parsed_body
    }

def lambda_handler(event, context):
    """
    AWS Lambda entry point - Complete V166 Implementation with Universal Event Parsing
    """
    print("🚀 V166 Lambda Handler Starting")
    print(f"Event keys: {list(event.keys())}")
    
    try:
        # Parse the event using universal parser
        parsed = parse_lambda_event(event)
        
        print(f"🔍 Event Type Detected: {parsed['event_type']}")
        print(f"📡 HTTP {parsed['http_method']} {parsed['path']}")
        
        # Handle HTTP requests
        if parsed['event_type'] != "Direct Invocation":
            http_method = parsed['http_method']
            path = parsed['path']
            body = parsed['body']
            
            # Create Flask test client for processing
            with app.test_client() as client:
                # Handle different HTTP methods and paths
                if http_method == 'GET' and path == '/health':
                    response = client.get('/health')
                elif http_method == 'GET' and path == '/courses':
                    response = client.get('/courses')
                elif http_method == 'POST' and path == '/query':
                    print(f"📦 Parsed body: {body}")
                    
                    response = client.post('/query', 
                                         json=body or {},
                                         headers={'Content-Type': 'application/json'})
                elif http_method == 'OPTIONS':
                    # Handle CORS preflight
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Headers': 'Content-Type,Authorization,Origin',
                            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                            'Access-Control-Max-Age': '3600'
                        },
                        'body': ''
                    }
                else:
                    # Unknown endpoint
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({"error": f"Not found: {http_method} {path}"})
                    }
                
                # Return Flask response as Lambda response
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization,Origin',
                        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                    },
                    'body': response.get_data(as_text=True)
                }
        
        else:
            # Direct Lambda invocation
            print("📞 Direct Lambda invocation detected")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "message": "V166 Lambda function is running",
                    "version": "V166-Complete",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "event_type": "Direct Invocation"
                })
            }
            
    except Exception as e:
        print(f"❌ Lambda handler error: {e}")
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }

if __name__ == '__main__':
    # Local development server
    print("🧪 Running V166 Lambda Function locally for testing")
    app.run(debug=True, host='0.0.0.0', port=5000)
