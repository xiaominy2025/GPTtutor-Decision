#!/usr/bin/env python3
"""
AWS Lambda Function with V166 Query Engine Integration
Based on working no_spacy version with CORS fixes
"""

import json
import time
import os
import sys
import re
import traceback
from typing import List, Tuple, Dict, Any
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

def pick_origin():
    """Get the appropriate origin for CORS headers"""
    try:
        origin = request.headers.get('origin') or request.headers.get('Origin')
        if origin in PROD_ALLOWED_ORIGINS:
            return origin
    except Exception:
        pass
    return DEFAULT_ORIGIN

def cors_headers():
    """Return standardized CORS headers for production"""
    origin = pick_origin()
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Max-Age": "86400"
    }

def create_response(data, status="success", status_code=200):
    """Create standardized V1.6.6.6 response format"""
    response = jsonify({
        "data": data,
        "status": status,
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })
    response.status_code = status_code
    
    # Add CORS headers
    for key, value in cors_headers().items():
        response.headers[key] = value
    
    return response

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
    """Get OpenAI API key from environment"""
    return os.environ.get('OPENAI_API_KEY')

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
    V166 Application Field Detection - Simplified version for Lambda
    """
    query_lower = query.lower()
    
    # Business/Strategic fields
    if any(word in query_lower for word in ['business', 'company', 'market', 'competition', 'strategy', 'revenue', 'profit']):
        return "Business Strategy"
    
    # Operations/Supply Chain
    if any(word in query_lower for word in ['production', 'supply', 'manufacturing', 'operations', 'logistics', 'inventory']):
        return "Operations Management"
    
    # Finance/Investment
    if any(word in query_lower for word in ['investment', 'financial', 'budget', 'cost', 'pricing', 'valuation']):
        return "Financial Decision-Making"
    
    # Technology/Innovation
    if any(word in query_lower for word in ['technology', 'innovation', 'digital', 'software', 'platform']):
        return "Technology Management"
    
    # Risk/Uncertainty
    if any(word in query_lower for word in ['risk', 'uncertainty', 'uncertain', 'volatile', 'unpredictable']):
        return "Risk Management"
    
    # Negotiation/Partnership
    if any(word in query_lower for word in ['negotiation', 'partnership', 'contract', 'agreement', 'deal']):
        return "Negotiation & Partnerships"
    
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

def extract_strategic_thinking_lens(answer: str) -> List[dict]:
    """
    Extract Strategic Thinking Lens section from the response
    Returns list of {"title": str, "content": str} objects
    """
    strategic_lens = []
    
    # Look for Strategic Thinking Lens section
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n+(.*?)(?=\n\n\*\*|\Z)', answer, re.DOTALL)
    if lens_match:
        lens_content = lens_match.group(1).strip()
        strategic_lens.append({
            "title": "Strategic Framework",
            "content": lens_content
        })
    
    return strategic_lens

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
    Returns structured response matching V1.6.6.6 format
    """
    try:
        print(f"🔄 V166 Processing Query: {query}")
        
        # Step 1: Relevance scoring (V166 abuse prevention)
        score, debug_info = compute_relevance_score(query)
        print(f"📊 Relevance Score: {score}, Debug: {debug_info}")
        
        if score < 2:
            print(f"⚠️ Query rejected due to low relevance. Debug: {debug_info}")
            return {
                "answer": "⚠️ This question doesn't appear to be related to decision-making. Try asking about decision-making tools, strategies, or business decisions.",
                "strategicThinkingLens": [],
                "followUpPrompts": [],
                "conceptsToolsPractice": [],
                "model": "gpt-3.5-turbo",
                "processing_time": 0.1
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
        strategic_thinking_lens = extract_strategic_thinking_lens(answer)
        concepts_tools_practice = extract_tools_from_section(answer)
        follow_up_prompts = extract_follow_up_prompts(answer)
        
        print(f"🧠 Extracted {len(strategic_thinking_lens)} strategic thinking lens")
        print(f"📋 Extracted {len(concepts_tools_practice)} concepts/tools")
        print(f"❓ Extracted {len(follow_up_prompts)} follow-up prompts")
        
        # Step 7: Return V1.6.6.6-compatible response
        return {
            "answer": answer,
            "strategicThinkingLens": strategic_thinking_lens,
            "followUpPrompts": follow_up_prompts,
            "conceptsToolsPractice": concepts_tools_practice,
            "model": "gpt-3.5-turbo",
            "processing_time": round(processing_time, 2)
        }
        
    except Exception as e:
        print(f"❌ Error in V166 processing: {e}")
        traceback.print_exc()
        
        # Fallback response
        return {
            "answer": f"I understand you're asking about: {query}\n\nThis appears to be a decision-making question that would benefit from systematic analysis. Consider using frameworks like decision trees, SWOT analysis, or scenario planning to evaluate your options thoroughly.",
            "strategicThinkingLens": [],
            "followUpPrompts": [],
            "conceptsToolsPractice": [],
            "model": "gpt-3.5-turbo",
            "processing_time": 0.1
        }

# === FLASK ROUTES ===

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return create_response({
        "status": "healthy",
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route('/courses', methods=['GET'])
def courses():
    """Get available courses"""
    return create_response({
        "courses": ["decision", "marketing", "strategy"]
    })

@app.route('/api/course/<course_id>', methods=['GET'])
def course_metadata(course_id):
    """Get course metadata"""
    return create_response({
        "course_id": course_id,
        "title": "Decision-Making Practice Lab",
        "mobile_title": "Decision Lab",
        "tagline": "A GPT-powered active learning platform for deeper understanding",
        "placeholder": "Ask a decision-making question...",
        "default_sections": 3,
        "sections_titles": [
            "Strategic Thinking Lens",
            "Follow-up Prompts", 
            "Concepts/Tools"
        ]
    })

@app.route('/query', methods=['POST'])
def query():
    """Process query endpoint"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return create_response(
                {"error": "Query is required"}, 
                status="error", 
                status_code=400
            )
        
        query = data['query']
        course_id = data.get('course_id', DEFAULT_COURSE)
        
        print(f"📚 Frontend requested course: {course_id}")
        print("🔄 Using Complete V166 Query Engine")
        
        # Process query using complete V166 implementation
        response_data = process_query_v166(query)
        
        print("✅ V166 Query processed successfully.")
        return create_response(response_data)
        
    except Exception as e:
        print(f"❌ Query endpoint error: {e}")
        traceback.print_exc()
        return create_response(
            {"error": "Internal server error", "message": str(e)}, 
            status="error", 
            status_code=500
        )

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Catch all other routes"""
    return create_response(
        {"error": f"Not found: {request.method} /{path}"}, 
        status="error", 
        status_code=404
    )

# === LAMBDA HANDLER ===

import json
from api_server import app as flask_app

def lambda_handler(event, context):
    # Handle Function URL events (different structure than direct Lambda invocations)
    if 'requestContext' in event and 'http' in event.get('requestContext', {}):
        # Function URL event format
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('rawPath', '/')
        body = event.get('body', '')
        headers = event.get('headers', {})
    else:
        # Direct Lambda invocation format
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body', '')
        headers = event.get('headers', {})
    
    # Parse body if it's a string
    if isinstance(body, str) and body:
        try:
            body_json = json.loads(body)
        except Exception:
            body_json = None
    else:
        body_json = body
    
    # Use Flask test client to handle the request
    with flask_app.test_client() as client:
        if method == 'GET':
            resp = client.get(path)
        elif method == 'POST':
            resp = client.post(path, json=body_json)
        elif method == 'PUT':
            resp = client.put(path, json=body_json)
        else:
            resp = client.get('/health')
        
        return {
            'statusCode': resp.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': '*'
            },
            'body': resp.get_data(as_text=True)
        }

if __name__ == '__main__':
    # Local development server
    print("🧪 Running V1.6.6.6 Lambda Function locally for testing")
    app.run(debug=True, host='0.0.0.0', port=5000)
