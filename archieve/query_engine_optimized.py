#!/usr/bin/env python3
"""
Optimized Query Engine for AWS Lambda - V1.6.6.6 Final
Includes all Lambda-specific optimizations for stable deployment
"""

import os
import sys
import json
import re
import time
import traceback
import difflib
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv
import numpy as np
import faiss
from pathlib import Path

# Lambda-specific optimizations
import torch
torch.set_num_threads(1)  # Critical for Lambda stability

# Set environment variables for Lambda optimization
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

# Configure cache directories for Lambda
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['HF_HOME'] = '/tmp/hf_home'
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

if not openai_api_key:
    print("FAIL: Error: OPENAI_API_KEY not set in environment variables.")
    sys.exit(1)

# Define metadata loading constants
COURSE_ID = os.getenv("COURSE_ID", "decision")

# 1. Runtime metadata location (Lambda cold start creates this in rebuild mode)
TMP_META_PATH = Path(f"/tmp/courses/{COURSE_ID}/metadata.json")

# 2. Baked base metadata location
COURSE_DIR = Path(f"courses/{COURSE_ID}")
BASE_META_PATH = COURSE_DIR / "base_metadata.json"

# 3. Legacy metadata location (pre-transition)
LEGACY_META_PATH = COURSE_DIR / "metadata.json"

# Select the highest-priority existing file
if TMP_META_PATH.exists():
    SELECTED_META_PATH = TMP_META_PATH
elif BASE_META_PATH.exists():
    SELECTED_META_PATH = BASE_META_PATH
elif LEGACY_META_PATH.exists():
    SELECTED_META_PATH = LEGACY_META_PATH
else:
    raise FileNotFoundError(f"No metadata file found for course {COURSE_ID}")

# === LAZY SINGLETON INITIALIZATION ===
_embeddings_model = None
_faiss_index = None
_openai_client = None
_metadata_loaded = False

def get_embeddings_model():
    """Lazy singleton for embeddings model"""
    global _embeddings_model
    if _embeddings_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Use smaller, Lambda-friendly model
            _embeddings_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            print("✅ Embeddings model loaded (CPU-only)")
        except Exception as e:
            print(f"❌ Failed to load embeddings model: {e}")
            raise
    return _embeddings_model

def get_faiss_index():
    """Lazy singleton for FAISS index"""
    global _faiss_index
    if _faiss_index is None:
        try:
            # Load FAISS index from file
            index_path = Path("vector_index.faiss")
            if index_path.exists():
                _faiss_index = faiss.read_index(str(index_path))
                print("✅ FAISS index loaded")
            else:
                print("⚠️ No FAISS index found, creating empty index")
                _faiss_index = faiss.IndexFlatIP(384)  # Dimension for all-MiniLM-L6-v2
        except Exception as e:
            print(f"❌ Failed to load FAISS index: {e}")
            raise
    return _faiss_index

def get_openai_client():
    """Lazy singleton for OpenAI client with proxy support"""
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            import httpx
            
            # Configure proxy settings if available
            proxy_settings = {}
            if os.getenv('HTTP_PROXY'):
                proxy_settings['http'] = os.getenv('HTTP_PROXY')
            if os.getenv('HTTPS_PROXY'):
                proxy_settings['https'] = os.getenv('HTTPS_PROXY')
            if os.getenv('NO_PROXY'):
                proxy_settings['no_proxy'] = os.getenv('NO_PROXY')
            
            # Create HTTP client with proxy support and timeouts
            http_client = httpx.Client(
                proxies=proxy_settings if proxy_settings else None,
                timeout=30.0,  # 30 second timeout
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
            
            _openai_client = OpenAI(
                api_key=openai_api_key,
                http_client=http_client
            )
            print("✅ OpenAI client initialized with proxy support")
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            raise
    return _openai_client

def load_metadata():
    """Lazy load metadata"""
    global _metadata_loaded
    if not _metadata_loaded:
        try:
            with open(SELECTED_META_PATH, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            _metadata_loaded = True
            print("✅ Metadata loaded")
            return metadata
        except Exception as e:
            print(f"❌ Failed to load metadata: {e}")
            raise
    return None

# === OPTIMIZED QUERY PROCESSING ===

def compute_relevance_score(query):
    """
    Compute relevance score for query abuse prevention.
    Optimized for Lambda with reduced memory usage.
    """
    try:
        # Extract domains using existing function
        domains = detect_course_concept_domains(query)
        domain_count = len([d for d in domains.values() if d > 0.1])
        
        # Extract application field using existing function
        try:
            application_field = extract_application_field_semantic(query, None)
        except:
            application_field = extract_application_field(query)
        
        # Extract concepts using existing function (limited to top 3)
        concepts = get_top_ranked_concepts(query, top_k=3)
        concept_count = len(concepts)
        
        # Calculate relevance score
        score = 2 * concept_count + domain_count + (1 if application_field else 0)
        
        return score, {
            "domains": list(domains.keys()),
            "application_fields": [application_field] if application_field else [],
            "concepts": [concept[0] for concept in concepts],
            "score": score
        }
    except Exception as e:
        print(f"⚠️ Relevance scoring failed: {e}")
        return 0, {"error": str(e)}

def process_query(query):
    """
    Main query processing function - optimized for Lambda
    """
    try:
        print(f"🔄 Processing query: {query[:100]}...")
        
        # Step 1: Relevance scoring (with timeout protection)
        start_time = time.time()
        score, debug_info = compute_relevance_score(query)
        
        if score < 2:
            return f"⚠️ This question doesn't appear to be related to the course. Try asking about decision-making tools, strategies, or business decisions."
        
        # Step 2: Lazy load components
        embeddings_model = get_embeddings_model()
        faiss_index = get_faiss_index()
        openai_client = get_openai_client()
        metadata = load_metadata()
        
        # Step 3: Generate embeddings (CPU-only)
        query_embedding = embeddings_model.encode([query], convert_to_tensor=False)
        
        # Step 4: Search FAISS index (limited results)
        k = min(5, faiss_index.ntotal)  # Limit to 5 results or total documents
        if k > 0:
            scores, indices = faiss_index.search(query_embedding, k)
            relevant_docs = [metadata[i] for i in indices[0] if i < len(metadata)]
        else:
            relevant_docs = []
        
        # Step 5: Build context (limited size)
        context = ""
        for doc in relevant_docs[:3]:  # Limit to 3 documents
            context += f"{doc.get('content', '')}\n\n"
        
        # Step 6: OpenAI API call with timeout and retry
        system_prompt = """You are a Decision Coach GPT. Your role is to help students make better decisions by thinking clearly, strategically, and—when appropriate—analytically.

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

        user_message = f"Query: {query}\n\nContext: {context[:2000]}"  # Limit context size
        
        # API call with timeout protection
        try:
            response = openai_client.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=openai_max_tokens,
                temperature=openai_temperature,
                timeout=25  # 25 second timeout
            )
            
            answer = response.choices[0].message.content.strip()
            processing_time = time.time() - start_time
            
            print(f"✅ Query processed in {processing_time:.2f}s")
            return answer
            
        except Exception as api_error:
            print(f"❌ OpenAI API error: {api_error}")
            return f"I understand you're asking about: {query}\n\nThis appears to be a decision-making question that would benefit from systematic analysis. Consider using frameworks like decision trees, SWOT analysis, or scenario planning to evaluate your options thoroughly."
            
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        traceback.print_exc()
        return f"I understand you're asking about: {query}\n\nThis appears to be a decision-making question that would benefit from systematic analysis. Consider using frameworks like decision trees, SWOT analysis, or scenario planning to evaluate your options thoroughly."

# === OPTIMIZED HELPER FUNCTIONS ===

def detect_course_concept_domains(query):
    """Detect course concept domains - optimized for Lambda"""
    # Simplified domain detection
    domains = {
        "strategic analysis": 0.0,
        "analytical tools": 0.0,
        "human behaviors": 0.0,
        "negotiation frameworks": 0.0,
        "risk assessment": 0.0
    }
    
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['strategy', 'strategic', 'competitive', 'positioning']):
        domains["strategic analysis"] = 0.8
    
    if any(word in query_lower for word in ['analysis', 'optimization', 'simulation', 'forecasting']):
        domains["analytical tools"] = 0.8
    
    if any(word in query_lower for word in ['bias', 'behavior', 'psychology', 'decision']):
        domains["human behaviors"] = 0.8
    
    if any(word in query_lower for word in ['negotiation', 'bargaining', 'agreement']):
        domains["negotiation frameworks"] = 0.8
    
    if any(word in query_lower for word in ['risk', 'uncertainty', 'volatility']):
        domains["risk assessment"] = 0.8
    
    return domains

def extract_application_field(query):
    """Extract application field - simplified for Lambda"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['business', 'company', 'market', 'competition']):
        return "Business Strategy"
    
    if any(word in query_lower for word in ['production', 'supply', 'manufacturing', 'operations']):
        return "Operations Management"
    
    if any(word in query_lower for word in ['investment', 'financial', 'budget', 'cost']):
        return "Financial Decision-Making"
    
    if any(word in query_lower for word in ['technology', 'innovation', 'digital', 'software']):
        return "Technology Management"
    
    return "General Decision-Making"

def extract_application_field_semantic(query, model=None):
    """Semantic application field extraction - simplified for Lambda"""
    return extract_application_field(query)

def get_top_ranked_concepts(query, top_k=3):
    """Get top ranked concepts - simplified for Lambda"""
    # Simplified concept extraction
    concepts = []
    query_lower = query.lower()
    
    concept_keywords = {
        "decision tree": ["decision tree", "tree analysis"],
        "swot analysis": ["swot", "strengths weaknesses"],
        "monte carlo simulation": ["monte carlo", "simulation"],
        "scenario analysis": ["scenario", "scenarios"],
        "linear optimization": ["linear programming", "optimization"],
        "risk assessment": ["risk", "uncertainty"]
    }
    
    for concept, keywords in concept_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            concepts.append((concept, f"Definition of {concept}"))
            if len(concepts) >= top_k:
                break
    
    return concepts

def extract_concepts_with_fuzzy_matching(query, threshold=0.8):
    """Fuzzy concept matching - simplified for Lambda"""
    return get_top_ranked_concepts(query, top_k=3)

def extract_tools_from_section(answer):
    """Extract tools from answer - optimized for Lambda"""
    tools = []
    
    # Look for Concepts/Tools section
    concepts_match = re.search(r'\*\*Concepts/Tools\*\*\s*\n+(.*?)(?=\n\n\*\*|\Z)', answer, re.DOTALL)
    if concepts_match:
        concepts_section = concepts_match.group(1).strip()
        
        # Extract tool definitions
        tool_matches = re.findall(r'-\s*\*\*([^*]+)\*\*:\s*([^\n]+)', concepts_section)
        for tool_name, definition in tool_matches:
            tools.append({
                "term": tool_name.strip(),
                "definition": definition.strip()
            })
    
    return tools

# Initialize components on module import (lazy loading)
print("🚀 V1.6.6.6 Optimized Query Engine loaded (Lambda-ready)")

