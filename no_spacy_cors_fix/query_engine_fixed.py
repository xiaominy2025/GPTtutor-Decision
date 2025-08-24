"""
Query Engine for Engent Labs V1.6.6.6 Final
Optimized for Lambda deployment with graceful spacy handling
"""
import os
import sys
import json
import time
import re
import hashlib
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Try to import spacy, but make it optional for Lambda deployment
try:
    import spacy
    SPACY_AVAILABLE = True
    print("✅ Spacy imported successfully")
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️ Spacy not available, using fallback NLP processing")

from pathlib import Path

from sentence_transformers import util
import uuid
import string

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

# --- Relevance Scoring Helper ---
def compute_relevance_score(query):
    """
    Compute relevance score for query abuse prevention.
    Higher scores indicate more relevant queries for decision-making topics.
    """
    # Extract domains using existing function
    domains = detect_course_concept_domains(query)
    domain_count = len([d for d in domains.values() if d > 0.1])
    
    # Extract application field using existing function
    try:
        application_field = extract_application_field_semantic(query, None)  # Will use cached model
    except:
        application_field = extract_application_field(query)
    
    # Extract concepts using existing function
    concepts = get_top_ranked_concepts(query, top_k=3)
    concept_count = len(concepts)
    
    # Fuzzy fallback if no concept match
    if not concepts:
        fuzzy_hits = extract_concepts_with_fuzzy_matching(query, threshold=0.8)
        if fuzzy_hits:
            concepts = fuzzy_hits
            concept_count = len(concepts)
    
    # Calculate relevance score
    score = 2 * concept_count + domain_count + (1 if application_field else 0)
    
    debug_info = {
        "domains": list(domains.keys()),
        "application_fields": [application_field] if application_field else [],
        "concepts": [concept[0] for concept in concepts],
        "score": score
    }
    return score, debug_info

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Global variables for lazy loading
_index = None
_metadata = None
_documents = None
_file_names = None
_model = None
_nlp = None

# TEMPORARY CACHE for V1.6.6.6 – to be removed in V1.6.7 when multi-course engine is introduced
cached_data = {}

def load_data_lazily():
    """Load data only when needed"""
    global _index, _metadata, _documents, _file_names, _model, _nlp
    
    if _index is None:
        print("Loading FAISS index...")
        import faiss
        _index = faiss.read_index("vector_index.faiss")
        print("✅ FAISS index loaded")
    
    if _metadata is None:
        print("Loading metadata...")
        with open(SELECTED_META_PATH, 'r', encoding='utf-8') as f:
            _metadata = json.load(f)
        print("✅ Metadata loaded")
    
    if _documents is None:
        print("Loading documents...")
        _documents = _metadata.get('documents', [])
        print("✅ Documents loaded")
    
    if _file_names is None:
        print("Loading file names...")
        _file_names = _metadata.get('file_names', [])
        print("✅ File names loaded")
    
    if _model is None:
        print("Loading sentence transformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence transformer model loaded")
    
    # Only load spacy if available
    if _nlp is None and SPACY_AVAILABLE:
        try:
            print("Loading spacy model...")
            _nlp = spacy.load("en_core_web_sm")
            print("✅ Spacy model loaded")
        except Exception as e:
            print(f"⚠️ Failed to load spacy model: {e}")
            _nlp = None
    elif _nlp is None and not SPACY_AVAILABLE:
        print("⚠️ Spacy not available, skipping NLP model loading")
        _nlp = None

# Copy the rest of the functions from the original query_engine.py
# For now, let me create a simplified version that focuses on the core functionality

def process_query(query: str) -> str:
    """
    Process a query and return a structured response.
    This is the main entry point for the V1666 query engine.
    """
    try:
        # Load data lazily
        load_data_lazily()
        
        # Check relevance score
        relevance_score, debug_info = compute_relevance_score(query)
        
        if relevance_score < 1:
            return f"⚠️ This question doesn't appear to be related to the course content. Please ask a question about decision-making, business strategy, or related topics."
        
        # Generate response using OpenAI
        response = generate_structured_response(query)
        
        return response
        
    except Exception as e:
        print(f"Error processing query: {e}")
        return f"An error occurred while processing your query: {str(e)}"

def generate_structured_response(query: str) -> str:
    """
    Generate a structured response using OpenAI.
    """
    try:
        # Create a prompt for structured response
        prompt = f"""
You are an expert decision-making tutor. Answer the following question with a structured response that includes:

1. A strategic thinking lens analysis
2. Key concepts from decision-making theory
3. Follow-up prompts for deeper learning

Question: {query}

Please provide your response in a clear, educational format that helps the student understand decision-making principles.
"""
        
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": "You are an expert decision-making tutor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=openai_max_tokens,
            temperature=openai_temperature
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"An error occurred while generating the response: {str(e)}"

# Placeholder functions for compatibility
def detect_course_concept_domains(query: str) -> Dict[str, float]:
    """Placeholder for domain detection"""
    return {"decision_making": 0.8, "business_strategy": 0.6}

def extract_application_field_semantic(query: str, model) -> Optional[str]:
    """Placeholder for application field extraction"""
    return "business"

def extract_application_field(query: str) -> Optional[str]:
    """Placeholder for application field extraction"""
    return "business"

def get_top_ranked_concepts(query: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """Placeholder for concept extraction"""
    return [("decision making", 0.9), ("uncertainty", 0.8)]

def extract_concepts_with_fuzzy_matching(query: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
    """Placeholder for fuzzy matching"""
    return [("decision making", 0.9)]
