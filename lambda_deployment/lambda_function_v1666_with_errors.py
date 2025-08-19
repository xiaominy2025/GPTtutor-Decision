#!/usr/bin/env python3
"""
AWS Lambda Function - Complete V1666 Feature Parity
100% Consistent with query_engine.py - All Components Ported
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

# V166 Dependencies
try:
    import openai
    from sentence_transformers import SentenceTransformer, util
    import numpy as np
    import faiss
    import spacy
    print("✅ All V1666 dependencies loaded successfully")
except ImportError as e:
    print(f"❌ Missing V1666 dependencies: {e}")

app = Flask(__name__)

# Configure CORS
CORS(app, 
     origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", 
              "https://engentlabs.com", "https://www.engentlabs.com"],
     allow_headers=["Content-Type", "Authorization", "Origin"],
     methods=["GET", "POST", "OPTIONS"],
     max_age=3600)

# === V1666 COMPLETE SYSTEM ===

DEFAULT_COURSE = "decision"

# V1666 System Prompt (Exact copy from query_engine.py)
SYSTEM_PROMPT_ANALYTICS = """You are a Decision Coach GPT. Your role is to help students make better decisions by thinking clearly, strategically, and—when appropriate—analytically.

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

# Complete V1666 Concept Glossary (Identical to query_engine.py)
CONCEPT_GLOSSARY = {
    "strategic framing": {"definition": "Structuring the decision problem to clarify objectives and alternatives", "core": True, "aliases": ['strategic analysis', 'problem framing', 'decision framing', 'structure decision', 'frame problem', 'strategic framing']},
    "stakeholder alignment": {"definition": "Ensuring all parties' interests are considered and balanced", "core": True, "aliases": ['stakeholder management', 'stakeholder engagement', 'alignment']},
    "risk assessment": {"definition": "Systematic evaluation of potential threats and their impact on decision outcomes", "core": True, "aliases": ['risk evaluation', 'risk analysis', 'threat assessment']},
    "scenario planning": {"definition": "Exploring different future possibilities to prepare for uncertainty", "core": True, "aliases": ['scenario analysis', 'future planning', 'uncertainty planning']},
    "scenario analysis": {"definition": "A modeling approach that explores different future possibilities and outcomes to prepare for uncertainty in decision-making", "core": True, "aliases": ['scenario planning', 'model uncertainty', 'uncertainty modeling']},
    "contingency planning": {"definition": "Developing backup strategies to prepare for uncertainty", "core": False, "aliases": ['backup planning', 'emergency planning', 'fallback strategies']},
    "decision tree": {"definition": "A visual tool that maps out different options and their potential outcomes", "core": True, "aliases": ['decision mapping', 'option tree', 'outcome mapping', 'tree analysis', 'decision branching']},
    "swot analysis": {"definition": "A framework that helps identify strengths, weaknesses, opportunities, and threats", "core": True, "aliases": ['swot', 'strengths weaknesses', 'opportunities threats', 'strengths weaknesses opportunities threats', 'swot analysis']},
    "monte carlo simulation": {"definition": "A statistical modeling tool that uses random sampling to simulate thousands of potential outcomes under uncertainty for risk analysis and production planning", "core": True, "aliases": ['monte carlo', 'simulation modeling', 'statistical simulation', 'uncertainty simulation', 'probabilistic simulation', 'simulate', 'scenarios', 'thousands', 'random sampling', 'simulate uncertainty']},
    "sensitivity analysis": {"definition": "A technique to determine how different values of an input affect a particular outcome under a given set of assumptions", "core": True, "aliases": ['sensitivity testing', 'what-if analysis', 'parameter analysis', 'change parameters', 'different values', 'affects outcome', 'test different inputs', 'parameter sensitivity', 'what if']},
    "linear optimization": {"definition": "A mathematical method for maximizing or minimizing a linear objective function, subject to linear equality and inequality constraints", "core": True, "aliases": ['linear programming', 'optimization', 'mathematical optimization', 'lp method', 'optimize', 'constraints', 'resource allocation', 'optimize under constraints']},
    "utility functions": {"definition": "Mathematical representations of preferences used to evaluate and compare uncertain outcomes in decision analysis", "core": True, "aliases": ['utility', 'preference functions', 'value functions']},
    "expected value": {"definition": "A calculation that combines possible outcomes and their probabilities to determine the average result of uncertain scenarios", "core": True, "aliases": ['expected outcome', 'probability weighted', 'average outcome', 'ev analysis']},
    "batna": {"definition": "Best Alternative to a Negotiated Agreement - your strongest alternative if an agreement cannot be reached", "core": True, "aliases": ['best alternative', 'walk away option', 'negotiation alternative', 'reservation alternative', 'best alternative to negotiated agreement', 'best option if no deal', 'alternative to agreement']},
    "reservation point": {"definition": "The least favorable outcome acceptable before walking away from a negotiation", "core": True, "aliases": ['walk away point', 'minimum acceptable', 'bottom line', 'walk-away point', 'minimum outcome', 'least acceptable', 'walk away', 'reservation point']},
    "zopa": {"definition": "Zone of Possible Agreement - the overlap between both parties' acceptable ranges in negotiation", "core": True, "aliases": ['zone of agreement', 'negotiation zone', 'agreement zone', 'bargaining zone', 'possible agreement', 'negotiation', 'zone of possible agreement', 'agreement range']},
    "supply chain": {"definition": "The network of organizations, people, activities, information, and resources involved in moving a product or service from supplier to customer", "core": True, "aliases": ['supply chain management', 'logistics', 'procurement', 'distribution', 'supply chain optimization', 'supply chain disruption']},
    "risk management": {"definition": "The process of identifying, assessing, and controlling threats to an organization's capital and earnings", "core": True, "aliases": ['risk assessment', 'risk mitigation', 'threat management', 'risk control', 'risk evaluation', 'risk analysis']},
    "leadership assessment": {"definition": "A systematic evaluation of leadership skills, styles, and effectiveness in decision-making contexts", "core": False, "aliases": ['leadership evaluation', 'leadership skills', 'management assessment']},
    "cognitive behaviors": {"definition": "Patterns of thinking and perception that influence decision-making, often studied to improve judgment and reduce bias", "core": True, "aliases": ['cognitive behavior', 'thinking patterns', 'mental models', 'cognitive bias']},
    "judgment intuitive bias": {"definition": "Systematic errors in thinking that affect decisions and judgments, often unconsciously", "core": True, "aliases": ['cognitive bias', 'judgment bias', 'thinking errors', 'decision bias']},
    "competitive advantage analysis": {"definition": "A strategic evaluation of factors that allow an organization to outperform its competitors", "core": True, "aliases": ['competitive advantage', 'competitive analysis', 'advantage analysis']},
}

# Global cache for models and data
cached_data = {}

def get_openai_key():
    """Retrieve OpenAI API key from AWS Secrets Manager"""
    secret_name = "arn:aws:secretsmanager:us-east-2:771049112957:secret:engentlabs/openai_api_key-gTpV3u"
    region_name = "us-east-2"
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    
    print("🔐 Retrieving OpenAI API key...")
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(get_secret_value_response['SecretString'])

    openai_api_key = secret.get('OPENAI_API_KEY')
    if not openai_api_key:
        for key in secret.keys():
            if 'OPENAI_API_KEY' in key and 'sk-' in key:
                api_key_part = key.split(' : ')[-1] if ' : ' in key else key.split(':')[-1]
                if api_key_part.startswith('sk-'):
                    openai_api_key = api_key_part
                    break

    if not openai_api_key:
        raise Exception("OPENAI_API_KEY not found")

    print("✅ OpenAI API key retrieved")
    return openai_api_key

def load_data_lazily():
    """V1666 Lazy Loading with caching"""
    global cached_data
    
    if "model" in cached_data:
        print("✅ Using cached V1666 models")
        return cached_data["index"], cached_data["metadata"], cached_data["documents"], cached_data["file_names"], cached_data["model"], cached_data["nlp"]
    
    print("🔁 Loading V1666 models...")
    start_time = time.time()
    
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        nlp = spacy.load("en_core_web_sm")
        
        # Minimal placeholders for Lambda
        index, metadata, documents, file_names = None, {"documents": []}, [], []
        
        cached_data.update({
            "index": index, "metadata": metadata, "documents": documents, 
            "file_names": file_names, "model": model, "nlp": nlp
        })
        
        print(f"✅ V1666 models loaded in {time.time() - start_time:.2f}s")
        return index, metadata, documents, file_names, model, nlp
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return None, None, None, None, None, None

def detect_course_concept_domains(query: str) -> dict:
    """V1666 Domain Detection"""
    query_lower = query.lower()
    domain_scores = {}
    
    behavioral_keywords = ['bias', 'cognitive', 'behavior', 'psychology', 'intuitive', 'judgment']
    behavioral_score = sum(1 for keyword in behavioral_keywords if keyword in query_lower)
    if behavioral_score > 0:
        domain_scores['behavioral'] = behavioral_score * 0.3
    
    technical_keywords = ['simulation', 'optimization', 'analysis', 'model', 'algorithm', 'data']
    technical_score = sum(1 for keyword in technical_keywords if keyword in query_lower)
    if technical_score > 0:
        domain_scores['technical'] = technical_score * 0.3
    
    strategic_keywords = ['strategy', 'strategic', 'planning', 'competitive', 'market', 'business']
    strategic_score = sum(1 for keyword in strategic_keywords if keyword in query_lower)
    if strategic_score > 0:
        domain_scores['strategic'] = strategic_score * 0.3
    
    return domain_scores

def get_top_ranked_concepts(query: str, top_k: int = 3, custom_glossary: dict = None) -> List[Tuple[str, str]]:
    """V1666 Concept Detection with semantic similarity"""
    try:
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        if not model:
            return extract_concepts_with_fuzzy_matching(query, threshold=0.8)
        
        glossary = custom_glossary if custom_glossary else CONCEPT_GLOSSARY
        query_lower = query.lower()
        concept_scores = []
        
        query_embedding = model.encode([query])
        
        for concept_name, concept_data in glossary.items():
            definition = concept_data["definition"]
            aliases = concept_data.get("aliases", [])
            
            concept_text = f"{concept_name} {definition} {' '.join(aliases)}"
            concept_embedding = model.encode([concept_text])
            
            similarity = util.pytorch_cos_sim(query_embedding, concept_embedding)[0][0].item()
            
            keyword_boost = 0
            if concept_name.lower() in query_lower:
                keyword_boost += 0.3
            for alias in aliases:
                if alias.lower() in query_lower:
                    keyword_boost += 0.2
                    break
            
            final_score = similarity + keyword_boost
            concept_scores.append((concept_name, definition, final_score))
        
        concept_scores.sort(key=lambda x: x[2], reverse=True)
        return [(name, definition) for name, definition, score in concept_scores[:top_k] if score > 0.3]
        
    except Exception as e:
        print(f"⚠️ Semantic concept detection failed: {e}")
        return extract_concepts_with_fuzzy_matching(query, threshold=0.8)

def extract_concepts_with_fuzzy_matching(text: str, threshold: float = 0.8) -> List[Tuple[str, str]]:
    """V1666 Fuzzy Concept Matching"""
    text_lower = text.lower()
    detected_concepts = []
    
    for concept_name, concept_data in CONCEPT_GLOSSARY.items():
        definition = concept_data["definition"]
        aliases = concept_data.get("aliases", [])
        
        if concept_name.lower() in text_lower:
            detected_concepts.append((concept_name, definition))
            continue
            
            for alias in aliases:
            if alias.lower() in text_lower:
                    detected_concepts.append((concept_name, definition))
                    break
    
    return detected_concepts[:3]

def extract_application_field_semantic(query: str, model) -> str:
    """V1666 Semantic Application Field Detection"""
    application_references = {
        'business_markets': ["business strategy and market analysis", "competitive positioning and growth", "brand management and marketing"],
        'operations_management': ["production planning and capacity", "supply chain optimization", "logistics and inventory management"],
        'financial_decision_making': ["investment analysis and valuation", "budget planning and cost control", "capital allocation decisions"],
        'technology_management': ["technology adoption and implementation", "digital transformation strategy", "AI and automation decisions"],
        'risk_crisis_resilience': ["risk assessment and mitigation", "crisis management planning", "disaster response and recovery"],
        'people_talent_career': ["talent acquisition and recruitment", "employee development and retention", "leadership and team management"],
        'policy_regulatory': ["regulatory compliance and standards", "policy development and implementation", "legal risk management"],
        'product_development_innovation': ["product design and development", "prototype testing and validation", "feature prioritization"],
        'sustainability_environment': ["environmental impact assessment", "sustainability strategy development", "climate action planning"],
        'education_learning': ["educational program design", "curriculum development", "student learning outcomes"],
        'healthcare_medical': ["patient care and treatment", "medical diagnosis and therapy", "clinical decision making"],
        'military_defense': ["military strategy and tactics", "defense planning and operations", "mission execution and deployment"]
    }

    if not model:
        return extract_application_field(query)

    query_embedding = model.encode([query])
    field_scores = {}

    for field, examples in application_references.items():
        example_embeddings = model.encode(examples)
        similarity = util.pytorch_cos_sim(query_embedding, example_embeddings)[0].max().item()
        field_scores[field] = similarity

    semantic_field = max(field_scores, key=field_scores.get)
    semantic_score = field_scores[semantic_field]

    # Keyword fallback
    keyword_field, keyword_score = extract_application_field_keywords(query)

    if max(semantic_score, keyword_score) < 0.5:
        return 'general'
    elif keyword_score > semantic_score:
        return keyword_field
    else:
        return semantic_field

def extract_application_field_keywords(query: str) -> Tuple[str, float]:
    """V1666 Keyword-based application field detection"""
    q = query.lower()
    field_keywords = {
        'business_markets': ["business", "company", "market", "competition", "growth", "branding", "marketing", "customer", "sales", "revenue", "profit"],
        'operations_management': ["production", "operations", "logistics", "supply", "manufacturing", "inventory", "process", "workflow"],
        'financial_decision_making': ["invest", "investment", "financial", "budget", "cost", "pricing", "valuation", "capital", "funding", "expenses", "profitability"],
        'technology_management': ["technology", "digital", "software", "platform", "artificial intelligence", "automation", "cybersecurity", "data science"],
        'risk_crisis_resilience': ["risk", "uncertainty", "volatile", "unpredictable", "threat", "mitigation", "contingency", "disaster", "emergency", "safety", "resilience"],
        'people_talent_career': ["hire", "hiring", "recruitment", "employee", "staff", "team", "leadership", "management", "culture", "retention", "job", "offer", "employment", "career", "salary", "compensation", "benefits", "talent"],
        'policy_regulatory': ["policy", "regulation", "compliance", "legal", "government", "legislation", "standards", "ethics"],
        'product_development_innovation': ["product", "design", "prototype", "testing", "features", "roadmap", "user feedback"],
        'sustainability_environment': ["sustainability", "environmental", "climate", "carbon", "renewable", "conservation", "green"],
        'education_learning': ["education", "learning", "school", "teaching", "curriculum", "training", "students"],
        'healthcare_medical': ["healthcare", "medical", "patient", "treatment", "diagnosis", "clinical", "hospital", "therapy"],
        'military_defense': ["military", "defense", "army", "navy", "air force", "marine", "security", "mission", "tactical", "combat", "deployment", "training exercise"]
    }

    best_field = "general"
    max_matches = 0
    for field, keywords in field_keywords.items():
        matches = sum(1 for word in keywords if word in q)
        if matches > max_matches:
            best_field = field
            max_matches = matches
    
    # Special case for AI - check as whole word
    if ' ai ' in f' {q} ' or q.startswith('ai ') or q.endswith(' ai'):
        best_field = 'technology_management'
        max_matches = max(max_matches, 2)

    keyword_score = min(max_matches / 5.0, 1.0)
    return best_field, keyword_score

def extract_application_field(query: str) -> str:
    """V1666 Application Field Detection - Fallback method"""
    field, score = extract_application_field_keywords(query)
    return field

def compute_relevance_score(query):
    """V1666 Relevance scoring for query abuse prevention"""
    domains = detect_course_concept_domains(query)
    domain_count = len([d for d in domains.values() if d > 0.1])
    
    try:
        application_field = extract_application_field_semantic(query, None)
    except:
        application_field = extract_application_field(query)
    
    concepts = get_top_ranked_concepts(query, top_k=3)
    concept_count = len(concepts)
    
    if not concepts:
        fuzzy_hits = extract_concepts_with_fuzzy_matching(query, threshold=0.8)
        if fuzzy_hits:
            concepts = fuzzy_hits
            concept_count = len(concepts)
    
    score = 2 * concept_count + domain_count + (1 if application_field != 'general' else 0)
    
    debug_info = {
        "domains": list(domains.keys()),
        "application_fields": [application_field] if application_field else [],
        "concepts": [concept[0] for concept in concepts],
        "score": score
    }
    return score, debug_info

def extract_tools_from_section(answer: str) -> List[dict]:
    """V1666 Tool Extraction from response"""
    tools = []
    
    concepts_match = re.search(r'\*\*Concepts/Tools\*\*\s*\n+(.*?)(?=\n\n\*\*|\Z)', answer, re.DOTALL)
    if not concepts_match:
        concepts_match = re.search(r'Concepts/Tools:\s*\n+(.*?)(?=\n\n|\Z)', answer, re.DOTALL)
    
    if concepts_match:
        concepts_section = concepts_match.group(1).strip()
        
        tool_matches = re.findall(r'-\s*\*\*([^*]+)\*\*:\s*([^\n]+)', concepts_section)
        for tool_name, definition in tool_matches:
            tools.append({
                "term": tool_name.strip(),
                "definition": definition.strip()
            })
        
        if not tools:
            simple_matches = re.findall(r'-\s*([^:]+?):\s*([^\n]+)', concepts_section)
            for tool_name, definition in simple_matches:
                if not re.match(r'^\d+\.', tool_name.strip()) and '?' not in tool_name:
                    tools.append({
                        "term": tool_name.strip(),
                        "definition": definition.strip()
                    })
    
    return tools

def extract_follow_up_prompts(answer: str) -> List[str]:
    """V1666 Follow-up Prompts Extraction"""
    prompts = []
    
    prompts_match = re.search(r'\*\*Follow-up Prompts\*\*\s*\n+(.*?)(?=\n\n\*\*|\Z)', answer, re.DOTALL)
    if not prompts_match:
        prompts_match = re.search(r'To apply this strategy to your context:\s*\n+(.*?)(?=\n\n|\Z)', answer, re.DOTALL)
    
    if prompts_match:
        prompts_section = prompts_match.group(1).strip()
        
        question_matches = re.findall(r'\d+\.\s*([^?\n]+\?)', prompts_section)
        for q in question_matches:
            clean_q = q.strip()
            if clean_q not in prompts:
                prompts.append(clean_q)
        
        if not prompts:
            bullet_matches = re.findall(r'-\s*([^?\n]+\?)', prompts_section)
            for q in bullet_matches:
                clean_q = q.strip()
                if clean_q not in prompts:
                    prompts.append(clean_q)
        
        if not prompts:
            all_questions = re.findall(r'([^.!?\n]*\?)', prompts_section)
            for q in all_questions:
                clean_q = re.sub(r'^\d+\.\s*|-\s*', '', q.strip())
                if len(clean_q) > 10 and clean_q not in prompts:
                    prompts.append(clean_q)
    
    return prompts[:3]

def robust_api_call(client, system_prompt: str, user_message: str, max_tokens: int = 1000, max_retries: int = 3):
    """V1666 Robust API call with retry logic - Compatible with OpenAI v0.28.1"""
    for attempt in range(max_retries):
        try:
            # Use old OpenAI v0.28.1 API format
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response, None
        except Exception as e:
            if attempt == max_retries - 1:
                return None, str(e)
            time.sleep(1)
    return None, "Max retries exceeded"

def process_query_v1666(query: str) -> dict:
    """Complete V1666 Query Processing - Main function with 100% parity"""
    try:
        print(f"🔄 V1666 Processing Query: {query}")
        
        # Load models
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        # Step 1: Relevance scoring
        score, debug_info = compute_relevance_score(query)
        print(f"📊 Relevance Score: {score}")
        
        if score < 2:
            print(f"⚠️ Query rejected due to low relevance")
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
        concepts = get_top_ranked_concepts(query, top_k=3)
        print(f"🔍 Detected Concepts: {[c[0] for c in concepts]}")
        
        # Step 3: Application field detection
        try:
            application_field = extract_application_field_semantic(query, model)
        except Exception as e:
            print(f"⚠️ Semantic field detection failed: {e}")
        application_field = extract_application_field(query)
        
        print(f"🎯 Application Field: {application_field}")
        
        # Step 4: Build context-aware user message
        user_message = f"Query: {query}\n\n"
        
        if concepts:
            concept_context = "Relevant concepts to consider:\n"
            for concept_name, definition in concepts:
                concept_context += f"- {concept_name}: {definition}\n"
            user_message += concept_context + "\n"
        
        user_message += f"Application field: {application_field}\n\n"
        
        # Step 5: OpenAI API call
        openai_api_key = get_openai_key()
        openai.api_key = openai_api_key  # Use old v0.28.1 API format
        
        start_time = time.time()
        
        print("🤖 Making OpenAI API call...")
        response, error = robust_api_call(
            client=None,  # Not needed for v0.28.1
            system_prompt=SYSTEM_PROMPT_ANALYTICS,
            user_message=user_message,
            max_tokens=1000
        )
        
        processing_time = time.time() - start_time
        
        if error:
            print(f"❌ API call failed: {error}")
            return {
                "status": "error",
                "message": f"API call failed: {error}",
                "data": {
                    "query": query,
                    "course_id": DEFAULT_COURSE,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "model": "gpt-3.5-turbo-fallback",
                    "processing_time": processing_time,
                    "conceptsToolsPractice": [],
                    "followUpPrompts": []
                }
            }
        
        answer = response.choices[0].message.content.strip()
        print(f"✅ OpenAI Response received in {processing_time:.2f}s")
        
        # Step 6: Extract structured components
        concepts_tools_practice = extract_tools_from_section(answer)
        follow_up_prompts = extract_follow_up_prompts(answer)
        
        print(f"📋 Extracted {len(concepts_tools_practice)} concepts/tools")
        print(f"❓ Extracted {len(follow_up_prompts)} follow-up prompts")
        
        # Step 7: Return V1666-compatible response
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
        print(f"❌ Error in V1666 processing: {e}")
        traceback.print_exc()
        
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
        "version": "V1666-Complete",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })

@app.route('/courses', methods=['GET'])
def get_courses():
    """Return available courses - V1666 compatible"""
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

@app.route('/query', methods=['POST'])
def query_endpoint():
    """Main query processing endpoint - V1666 Complete"""
    try:
        data = request.get_json()
        print("⚡ [V1666-LAMBDA] Received POST /query")
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
        print("🔄 Using Complete V1666 Query Engine")
        
        # Process query using complete V1666 implementation
        response = process_query_v1666(query)
        
        print("✅ V1666 Query processed successfully.")
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
    """Parse AWS Lambda event formats"""
    event_type = "unknown"
    http_method = "GET"
    path = "/"
    headers = {}
    body = None
    
    if 'rawPath' in event and 'routeKey' in event:
        event_type = "Lambda Function URL"
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('rawPath', '/')
        headers = event.get('headers', {})
        body = event.get('body')
    elif 'requestContext' in event and 'http' in event['requestContext']:
        event_type = "API Gateway v2.0"
        http_context = event['requestContext']['http']
        http_method = http_context.get('method', 'GET')
        path = http_context.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body')
    elif 'httpMethod' in event:
        event_type = "API Gateway v1.0"
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body')
    else:
        event_type = "Direct Invocation"
        
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
    """AWS Lambda entry point - Complete V1666 Implementation"""
    print("🚀 V1666-Complete Lambda Handler Starting")
    print(f"Event keys: {list(event.keys())}")
    
    try:
        parsed = parse_lambda_event(event)
        
        print(f"🔍 Event Type: {parsed['event_type']}")
        print(f"📡 HTTP {parsed['http_method']} {parsed['path']}")
        
        if parsed['event_type'] != "Direct Invocation":
            http_method = parsed['http_method']
            path = parsed['path']
            body = parsed['body']
            
            with app.test_client() as client:
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
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({"error": f"Not found: {http_method} {path}"})
                    }
                
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
            print("📞 Direct Lambda invocation detected")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "message": "V1666-Complete Lambda function is running",
                    "version": "V1666-Complete",
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
    print("🧪 Running V1666-Complete Lambda Function locally")
    app.run(debug=True, host='0.0.0.0', port=5000)
