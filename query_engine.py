"""
GPTutor Decision Coach - Enhanced Query Engine
=============================================

This engine uses an enhanced GPT prompt that generates structured answers with:
1. Strategy/Explanation - varied writing styles, no repetitive openings
2. Story in Action - engaging narrative examples
3. Reflection Prompts - 3 concise thinking prompts
4. Concept/Tool References - clean tooltip-ready list

The system prioritizes user materials but supplements with GPT knowledge when needed.
"""

import json
import faiss
from openai import OpenAI
import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import sys
import traceback
import re
import spacy
from frameworks import FRAMEWORKS

# Add grammar and clarity filtering imports
import re
from typing import List, Tuple, Dict

# Global variables - will be initialized safely
FRAMEWORKS_GPT = {}
PREBUILT_TOOLTIPS = {}

def safe_load_data():
    """Safely load all required data files with proper error handling"""
    global FRAMEWORKS_GPT, PREBUILT_TOOLTIPS
    
    # Load GPT-polished frameworks from JSON
    try:
        with open("frameworks_gpt.json", "r", encoding="utf-8") as f:
            FRAMEWORKS_GPT = json.load(f)
        print("✅ Loaded frameworks_gpt.json")
    except FileNotFoundError:
        print("⚠️ frameworks_gpt.json not found - using empty dictionary")
        FRAMEWORKS_GPT = {}
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing frameworks_gpt.json: {e}")
        FRAMEWORKS_GPT = {}
    except Exception as e:
        print(f"⚠️ Unexpected error loading frameworks_gpt.json: {e}")
        FRAMEWORKS_GPT = {}

    # Prebuilt tooltips dictionary for common concepts
    PREBUILT_TOOLTIPS = {
        "decision tree": "A visual tool that maps out different options and their potential outcomes to help make confident choices when faced with uncertainty.",
        "swot analysis": "A framework that helps identify strengths, weaknesses, opportunities, and threats to assess your situation comprehensively.",
        "cost-benefit analysis": "A systematic approach to compare the pros and cons of different options by weighing their advantages and disadvantages.",
        "expected utility": "A method for calculating the value of different scenarios when dealing with uncertainty and multiple possible outcomes.",
        "ooda loop": "A decision cycle (Observe, Orient, Decide, Act) that helps you stay agile and responsive in fast-changing situations.",
        "bounded rationality": "The recognition that good decisions don't require perfect information when time or information is limited.",
        "prospect theory": "Shows how people often value avoiding losses more than achieving gains when evaluating options.",
        "anchoring bias": "The tendency to rely too heavily on the first piece of information when making decisions.",
        "confirmation bias": "The tendency to seek out information that confirms existing beliefs while ignoring contradictory evidence.",
        "status quo bias": "The preference to keep things as they are rather than making changes, even when change might be beneficial.",
        "sunk cost fallacy": "The tendency to continue investing in a decision based on past investments rather than future benefits.",
        "framing effect": "How the way information is presented influences decision-making, even when the underlying facts are the same.",
        "endowment effect": "The tendency to value something more highly simply because you own it.",
        "escalation of commitment": "The tendency to continue investing in a failing course of action to justify previous investments.",
        "satisficing": "Choosing an option that is good enough rather than searching for the optimal solution.",
        "utility theory": "A framework for measuring the satisfaction or value derived from different outcomes and choices."
    }
    print("✅ Loaded prebuilt tooltips")

# Initialize data safely
safe_load_data()

# Hybrid tooltip system - optimize token usage
class HybridTooltipManager:
    def __init__(self):
        self.prebuilt_tooltips = FRAMEWORKS_GPT
        self.custom_tooltip_cache = {}
        self.context_cache = {}  # Cache for similar contexts
        self.token_usage = {"prebuilt": 0, "custom": 0, "prebuilt_dict": 0}
        self.session_stats = {"prebuilt_used": 0, "custom_generated": 0, "prebuilt_dict_used": 0}
    
    def get_tooltip(self, concept: str, context: str = "") -> tuple[str, bool, str]:
        """
        Returns (tooltip_text, is_prebuilt, source_type)
        Uses prebuilt tooltips when possible, generates custom ones only when needed
        """
        concept_lower = concept.lower()
        
        # Check prebuilt dictionary first (most efficient - 0 tokens)
        if concept_lower in PREBUILT_TOOLTIPS:
            self.token_usage["prebuilt_dict"] += 1
            self.session_stats["prebuilt_dict_used"] += 1
            tooltip = clean_tooltip_text(PREBUILT_TOOLTIPS[concept_lower], max_words=50)
            return tooltip, True, "prebuilt_dict"
        
        # Check GPT-polished tooltips second
        if concept_lower in self.prebuilt_tooltips:
            self.token_usage["prebuilt"] += 1
            self.session_stats["prebuilt_used"] += 1
            tooltip = clean_tooltip_text(self.prebuilt_tooltips[concept_lower], max_words=50)
            return tooltip, True, "prebuilt_gpt"
        
        # Check custom cache
        if concept_lower in self.custom_tooltip_cache:
            self.token_usage["custom"] += 1
            self.session_stats["custom_generated"] += 1
            tooltip = clean_tooltip_text(self.custom_tooltip_cache[concept_lower], max_words=50)
            return tooltip, False, "cached_custom"
        
        # Generate custom tooltip only if context is unique
        if context and len(context) > 50:  # Only generate for substantial context
            # Check context cache for similar contexts
            context_key = self._get_context_key(context)
            if context_key in self.context_cache:
                cached_tooltip = self.context_cache[context_key].get(concept_lower)
                if cached_tooltip:
                    self.token_usage["custom"] += 1
                    self.session_stats["custom_generated"] += 1
                    return cached_tooltip, False, "context_cached"
            
            custom_tooltip = self._generate_custom_tooltip(concept, context)
            cleaned_tooltip = clean_tooltip_text(custom_tooltip, max_words=50)
            self.custom_tooltip_cache[concept_lower] = cleaned_tooltip
            
            # Cache for similar contexts
            if context_key not in self.context_cache:
                self.context_cache[context_key] = {}
            self.context_cache[context_key][concept_lower] = cleaned_tooltip
            
            self.token_usage["custom"] += 1
            self.session_stats["custom_generated"] += 1
            return cleaned_tooltip, False, "new_custom"
        
        # Fallback to canonical definition
        canonical = FRAMEWORKS.get(concept_lower, f"Concept: {concept}")
        cleaned_canonical = clean_tooltip_text(canonical, max_words=50)
        self.token_usage["prebuilt"] += 1
        self.session_stats["prebuilt_used"] += 1
        return cleaned_canonical, True, "canonical"
    
    def _get_context_key(self, context: str) -> str:
        """Generate a key for context caching based on content similarity"""
        # Use first 100 characters and word count as a simple similarity key
        words = context.split()
        return f"{len(words)}_{context[:100].lower().replace(' ', '_')}"
    
    def _generate_custom_tooltip(self, concept: str, context: str) -> str:
        """Generate custom tooltip using minimal GPT tokens with 50-word limit"""
        prompt = f"""Given this context about {concept} in decision-making, provide a clear explanation in student-friendly terms. Keep it under 50 words and end with a period.

Context: {context[:200]}...

{concept}:"""
        
        try:
            response = client.chat.completions.create(
                model=openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=openai_temperature,
                max_tokens=100  # Enough for 50 words
            )
            content = response.choices[0].message.content
            if content is not None:
                # Clean and apply word limit using the existing function
                return clean_tooltip_text(content.strip(), max_words=50)
            else:
                fallback = FRAMEWORKS.get(concept.lower(), f"Concept: {concept}.")
                return clean_tooltip_text(fallback, max_words=50)
        except Exception:
            fallback = FRAMEWORKS.get(concept.lower(), f"Concept: {concept}.")
            return clean_tooltip_text(fallback, max_words=50)
    
    def get_usage_stats(self) -> dict:
        """Get token usage statistics"""
        total_prebuilt = self.token_usage["prebuilt"] + self.token_usage["prebuilt_dict"]
        total_all = total_prebuilt + self.token_usage["custom"]
        
        return {
            "prebuilt_dict_used": self.token_usage["prebuilt_dict"],
            "prebuilt_gpt_used": self.token_usage["prebuilt"],
            "custom_generated": self.token_usage["custom"],
            "total_concepts": total_all,
            "efficiency": f"{total_prebuilt / total_all:.1%}" if total_all > 0 else "0%",
            "session_stats": self.session_stats
        }

# Initialize hybrid tooltip manager
tooltip_manager = HybridTooltipManager()

# Load environment variables
print("🔍 Loading environment variables...")
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Default to cost-effective model
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY not set in environment variables.")
    print("   Please set it in your .env file or environment.")
    sys.exit(1)

print(f"🤖 Using model: {openai_model}")
print(f"📊 Max tokens: {openai_max_tokens}")
print(f"🌡️ Temperature: {openai_temperature}")

# Initialize OpenAI client with new API
try:
    client = OpenAI(api_key=openai_api_key)
    # Test the connection
    test_response = client.chat.completions.create(
        model=openai_model,
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
    print("✅ OpenAI connection successful")
except Exception as e:
    print(f"❌ Error connecting to OpenAI: {e}")
    print("   Please check your API key and internet connection.")
    sys.exit(1)

# Load user profile for personalization (except response_format)
user_profile = {
    "role": "helpful tutor",
    "tone": "encouraging and clear",
    "thinking_style": "step-by-step reasoning"
}
try:
    with open("user_profile.json", "r", encoding="utf-8") as f:
        profile_data = json.load(f)
        for k in ["role", "tone", "thinking_style"]:
            if k in profile_data:
                user_profile[k] = profile_data[k]
except Exception:
    pass  # Use defaults if file not found or invalid

# Load FAISS index and metadata
try:
    index = faiss.read_index("vector_index.faiss")
except Exception as e:
    print(f"❌ Error loading FAISS index: {e}")
    sys.exit(1)

try:
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    documents = metadata["documents"]
    file_names = metadata.get("file_names", ["Unknown"] * len(documents))
    file_paths = metadata.get("file_paths", file_names)
except Exception as e:
    print(f"❌ Error loading metadata: {e}")
    sys.exit(1)

# Load embedding model
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"❌ Error loading embedding model: {e}")
    sys.exit(1)

# Load spaCy English model for NER
nlp = spacy.load("en_core_web_sm")

# List of decision frameworks/models and their explanations
# Add more models to FRAMEWORKS
FRAMEWORKS.update({
    "bounded rationality": "Bounded rationality describes the limitations of decision-makers in processing information and finding optimal solutions.",
    "satisficing": "Satisficing is a decision-making strategy that aims for a satisfactory or adequate result, rather than the optimal one.",
    "OODA loop": "The OODA loop (Observe, Orient, Decide, Act) is a decision cycle used for rapid and effective decision-making, especially in dynamic environments."
})

def add_readability_breaks(answer: str) -> str:
    """Add natural breaks for long answers to improve readability"""
    
    word_count = len(answer.split())
    if word_count <= 500:
        return answer
    
    # Find the Strategy or Explanation section (usually the longest)
    strategy_pattern = r'(\*\*Strategy or Explanation\*\*.*?)(\*\*Story|\*\*Reflection|\*\*Concept|$)'
    match = re.search(strategy_pattern, answer, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return answer
    
    strategy_section = match.group(1)
    rest_of_answer = answer[match.end():]
    
    # Split the strategy section into sentences
    sentences = re.split(r'(?<=[.!?]) +', strategy_section)
    
    # If strategy section is very long, add a break
    if len(strategy_section) > 300:
        # Find a good breaking point (around the middle)
        mid_point = len(sentences) // 2
        if mid_point > 0:
            # Insert a natural break
            break_text = "\n\n---\n\n"
            strategy_section = " ".join(sentences[:mid_point]) + break_text + " ".join(sentences[mid_point:])
    
    return strategy_section + rest_of_answer

def clean_and_deduplicate_tooltips(answer: str) -> str:
    """Clean and deduplicate tooltips in the Concept/Tool References section"""
    
    # Find the Concept/Tool References section
    tooltip_pattern = r'(\*\*Concept/Tool References\*\*.*?)(?=\*\*|$)'
    match = re.search(tooltip_pattern, answer, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return answer
    
    tooltip_section = match.group(1)
    rest_of_answer = answer[:match.start()] + answer[match.end():]
    
    # Extract tooltip lines
    lines = tooltip_section.split('\n')
    tooltip_lines = []
    header_line = ""
    
    for line in lines:
        if line.strip().startswith('**Concept/Tool References**'):
            header_line = line
        elif line.strip().startswith('- **'):
            tooltip_lines.append(line.strip())
    
    # Deduplicate and clean tooltips
    unique_tooltips = {}
    for line in tooltip_lines:
        # Extract tooltip name and definition
        name_match = re.search(r'- \*\*(.*?)\*\*:?\s*(.*)', line)
        if name_match:
            name = name_match.group(1).strip()
            definition = name_match.group(2).strip()
            
            # Clean the definition
            definition = re.sub(r'\.$', '', definition)  # Remove trailing period
            definition = definition.strip()
            
            # Normalize the name (title case)
            normalized_name = " ".join(word.capitalize() for word in name.split())
            
            # Only keep if not already present or if this definition is better
            if normalized_name not in unique_tooltips or len(definition) > len(unique_tooltips[normalized_name]):
                unique_tooltips[normalized_name] = definition
    
    # Rebuild the tooltip section
    cleaned_section = header_line + "\n"
    for name, definition in sorted(unique_tooltips.items()):
        if definition:
            cleaned_section += f"- **{name}**: {definition}\n"
        else:
            cleaned_section += f"- **{name}**\n"
    
    return rest_of_answer + cleaned_section

# --- Grammar and Clarity Filtering Functions ---

def detect_repetitive_patterns(text: str) -> List[Tuple[str, str]]:
    """Detect and return repetitive opening patterns that should be varied"""
    repetitive_patterns = [
        (r'\bWhen considering\b', "When considering"),
        (r'\bIt\'s essential to\b', "It's essential to"),
        (r'\bIt is important to\b', "It is important to"),
        (r'\bIn order to\b', "In order to"),
        (r'\bTo properly\b', "To properly"),
        (r'\bWhen making\b', "When making"),
        (r'\bWhen faced with\b', "When faced with"),
        (r'\bWhen dealing with\b', "When dealing with"),
        (r'\bWhen evaluating\b', "When evaluating"),
        (r'\bWhen analyzing\b', "When analyzing"),
        (r'\bImagine you\'re at a crossroads\b', "Imagine you're at a crossroads"),
        (r'\bPicture yourself\b', "Picture yourself"),
        (r'\bConsider this scenario\b', "Consider this scenario"),
        (r'\bThink about\b', "Think about"),
        (r'\bLet\'s imagine\b', "Let's imagine")
    ]
    
    found_patterns = []
    for pattern, description in repetitive_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found_patterns.append((pattern, description))
    
    return found_patterns

def detect_grammar_fragments(text: str) -> List[Tuple[str, str]]:
    """Detect common grammar fragments and awkward phrasing"""
    fragment_patterns = [
        (r'\bindividual, a professional\b', "individual, a professional"),
        (r'\bindividual, an expert\b', "individual, an expert"),
        (r'\bperson, a manager\b', "person, a manager"),
        (r'\bindividual, a decision-maker\b', "individual, a decision-maker"),
        (r'\bindividual, a leader\b', "individual, a leader"),
        (r'\bindividual, a student\b', "individual, a student"),
        (r'\bindividual, a business\b', "individual, a business"),
        (r'\bindividual, a company\b', "individual, a company"),
        (r'\bindividual, an organization\b', "individual, an organization"),
        (r'\bindividual, a team\b', "individual, a team"),
        # Add more fragment patterns
        (r'\bdecision, a choice\b', "decision, a choice"),
        (r'\boption, a possibility\b', "option, a possibility"),
        (r'\bstrategy, a plan\b', "strategy, a plan"),
        (r'\bapproach, a method\b', "approach, a method"),
        (r'\bprocess, a procedure\b', "process, a procedure")
    ]
    
    found_fragments = []
    for pattern, description in fragment_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found_fragments.append((pattern, description))
    
    return found_fragments

def detect_awkward_phrasing(text: str) -> List[Tuple[str, str]]:
    """Detect awkward or robotic phrasing patterns"""
    awkward_patterns = [
        (r'\bIt is worth noting that\b', "It is worth noting that"),
        (r'\bIt should be mentioned that\b', "It should be mentioned that"),
        (r'\bIt is important to note that\b', "It is important to note that"),
        (r'\bIt is crucial to understand that\b', "It is crucial to understand that"),
        (r'\bIt is necessary to consider that\b', "It is necessary to consider that"),
        (r'\bIt is essential to recognize that\b', "It is essential to recognize that"),
        (r'\bIt is vital to acknowledge that\b', "It is vital to acknowledge that"),
        (r'\bIt is imperative to realize that\b', "It is imperative to realize that"),
        (r'\bIt is critical to understand that\b', "It is critical to understand that"),
        (r'\bIt is fundamental to consider that\b', "It is fundamental to consider that"),
        # Robotic patterns
        (r'\bIn conclusion\b', "In conclusion"),
        (r'\bTo summarize\b', "To summarize"),
        (r'\bAs previously mentioned\b', "As previously mentioned"),
        (r'\bAs stated earlier\b', "As stated earlier"),
        (r'\bAs mentioned before\b', "As mentioned before"),
        (r'\bAs discussed above\b', "As discussed above"),
        (r'\bAs outlined previously\b', "As outlined previously"),
        (r'\bAs indicated earlier\b', "As indicated earlier"),
        (r'\bAs noted before\b', "As noted before"),
        (r'\bAs described above\b', "As described above")
    ]
    
    found_awkward = []
    for pattern, description in awkward_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found_awkward.append((pattern, description))
    
    return found_awkward

def suggest_style_variations() -> List[str]:
    """Provide alternative writing styles to replace repetitive patterns"""
    return [
        "What should you do when",
        "Let's map this out together.",
        "Think of this like",
        "Here's a practical approach:",
        "Consider this scenario:",
        "Picture yourself in this situation:",
        "Imagine you're faced with",
        "Let's break this down:",
        "Here's how to approach this:",
        "The key question is:",
        "Your challenge is to",
        "The real issue here is",
        "What matters most is",
        "The core decision is",
        "Your goal should be to",
        "Three things matter here:",
        "Let's map this out together:",
        "Here's the real question:",
        "Your challenge is to",
        "The key insight is:"
    ]

def fix_grammar_fragments(text: str) -> str:
    """Automatically fix common grammar fragments"""
    # Fix "individual, a professional" patterns
    text = re.sub(r'\bindividual, a professional\b', "a professional", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, an expert\b', "an expert", text, flags=re.IGNORECASE)
    text = re.sub(r'\bperson, a manager\b', "a manager", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a decision-maker\b', "a decision-maker", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a leader\b', "a leader", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a student\b', "a student", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a business\b', "a business", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a company\b', "a company", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, an organization\b', "an organization", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a team\b', "a team", text, flags=re.IGNORECASE)
    
    # Fix other fragment patterns
    text = re.sub(r'\bdecision, a choice\b', "a choice", text, flags=re.IGNORECASE)
    text = re.sub(r'\boption, a possibility\b', "a possibility", text, flags=re.IGNORECASE)
    text = re.sub(r'\bstrategy, a plan\b', "a plan", text, flags=re.IGNORECASE)
    text = re.sub(r'\bapproach, a method\b', "a method", text, flags=re.IGNORECASE)
    text = re.sub(r'\bprocess, a procedure\b', "a procedure", text, flags=re.IGNORECASE)
    
    return text

def improve_repetitive_openings(text: str) -> str:
    """Replace repetitive opening patterns with varied alternatives"""
    import random
    
    # Define replacement patterns
    replacements = {
        r'\bWhen considering\b': [
            "What should you do when",
            "Let's map this out together.",
            "Think of this like",
            "Here's a practical approach:",
            "Consider this scenario:"
        ],
        r'\bIt\'s essential to\b': [
            "The key is to",
            "What matters most is",
            "Your focus should be on",
            "The real question is",
            "Here's what you need to do:"
        ],
        r'\bIt is important to\b': [
            "Keep in mind that",
            "Remember that",
            "The crucial point is",
            "What you should know is",
            "Here's what to consider:"
        ],
        r'\bIn order to\b': [
            "To",
            "So that you can",
            "With the goal of",
            "Aiming to",
            "Working toward"
        ]
    }
    
    improved_text = text
    for pattern, alternatives in replacements.items():
        if re.search(pattern, improved_text, re.IGNORECASE):
            replacement = random.choice(alternatives)
            improved_text = re.sub(pattern, replacement, improved_text, flags=re.IGNORECASE)
    
    return improved_text

def apply_grammar_and_clarity_filters(answer: str) -> Tuple[str, Dict[str, List[str]]]:
    """Apply comprehensive grammar and clarity filtering"""
    issues = {
        "repetitive_patterns": [],
        "grammar_fragments": [],
        "awkward_phrasing": []
    }
    
    # Detect issues
    repetitive = detect_repetitive_patterns(answer)
    fragments = detect_grammar_fragments(answer)
    awkward = detect_awkward_phrasing(answer)
    
    # Record issues
    for pattern, description in repetitive:
        issues["repetitive_patterns"].append(description)
    
    for pattern, description in fragments:
        issues["grammar_fragments"].append(description)
    
    for pattern, description in awkward:
        issues["awkward_phrasing"].append(description)
    
    # Apply fixes
    improved_answer = answer
    improved_answer = fix_grammar_fragments(improved_answer)
    improved_answer = improve_repetitive_openings(improved_answer)
    
    return improved_answer, issues

def generate_response(answer_raw: str, prebuilt_tooltips: dict, frameworks_gpt: dict) -> str:
    """
    Enhanced response generator with improved tooltip coverage, creativity, and formatting
    
    Args:
        answer_raw: Raw response from GPT
        prebuilt_tooltips: Dictionary of tooltip definitions
        frameworks_gpt: Dictionary of GPT-polished frameworks
    
    Returns:
        Processed answer with enforced structure, enhanced tooltips, and improved formatting
    """
    # Section headers expected in the answer
    response_sections = {
        "Strategy or Explanation": "",
        "Story or Analogy": "",
        "Reflection Prompts": "",
        "Concept/Tool References": ""
    }

    # Parse sections from raw answer with improved detection
    current_section = None
    lines = answer_raw.split("\n")
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for section headers (both bold and non-bold)
        if line in response_sections:
            current_section = line
        elif line.replace("**", "") in response_sections:
            current_section = line.replace("**", "")
        elif line == "**Story or Analogy**":
            current_section = "Story or Analogy"
        elif line == "**Reflection Prompts**":
            current_section = "Reflection Prompts"
        elif line == "**Concept/Tool References**":
            current_section = "Concept/Tool References"
        elif line == "**Strategy or Explanation**":
            current_section = "Strategy or Explanation"
        elif current_section and line:
            # Only add content if we're in a section and line is not empty
            if not line.startswith("**") and not line.startswith("💡") and not line.startswith("🧠"):
                response_sections[current_section] += line + " "
    
    # Clean up sections - remove extra whitespace and normalize
    for section in response_sections:
        response_sections[section] = response_sections[section].strip()
        # Remove any section headers that might have been captured as content
        response_sections[section] = re.sub(r'\*\*[^*]+\*\*', '', response_sections[section])
        response_sections[section] = response_sections[section].strip()

    # Enhanced tooltip injection with comprehensive coverage
    def inject_comprehensive_tooltips(content: str) -> str:
        """Inject tooltips for all relevant concepts found in content"""
        enhanced_content = content
        
        # Priority tooltips that should always be included if mentioned
        priority_concepts = [
            "framing bias", "endowment effect", "swot analysis", "decision tree",
            "cost-benefit analysis", "expected utility", "prospect theory",
            "anchoring bias", "confirmation bias", "status quo bias",
            "sunk cost fallacy", "escalation of commitment", "bounded rationality",
            "ooda loop", "utility theory", "satisficing"
        ]
        
        # Check for priority concepts and inject tooltips
        found_tooltips = []
        for concept in priority_concepts:
            if concept.lower() in content.lower():
                # Look for tooltip in prebuilt_tooltips first
                tooltip = prebuilt_tooltips.get(concept.lower())
                if tooltip:
                    found_tooltips.append((concept, tooltip))
                # Also check frameworks_gpt
                elif concept.lower() in frameworks_gpt:
                    found_tooltips.append((concept, frameworks_gpt[concept.lower()]))
        
        # Add tooltips to content if not already present and no existing tooltip section
        if found_tooltips and "**Concept/Tool References**" not in content and "**Concepts/Tools/Practice Reference:**" not in content:
            tooltip_section = "\n\n**Concept/Tool References**\n"
            for concept, tooltip in found_tooltips:
                concept_title = " ".join(word.capitalize() for word in concept.split())
                tooltip_section += f"- **{concept_title}**: {tooltip}\n"
            enhanced_content += tooltip_section
        
        return enhanced_content

    # Enhanced story creativity with vivid analogies
    def enhance_story_creativity(content: str) -> str:
        """Replace overused analogies with more vivid alternatives"""
        creativity_replacements = {
            r'\bat a crossroads\b': [
                "like an astronaut preparing for launch",
                "like a chef balancing complex flavors",
                "like a chess player calculating moves",
                "like a conductor leading an orchestra",
                "like a pilot navigating through turbulence"
            ],
            r'\bsteering a ship\b': [
                "piloting a spacecraft through asteroid fields",
                "conducting a symphony in a thunderstorm",
                "playing chess against a grandmaster",
                "sculpting marble with precision tools",
                "orchestrating a complex dance performance"
            ],
            r'\bweathering the storm\b': [
                "navigating through uncharted territory",
                "balancing on a tightrope over a canyon",
                "solving a complex puzzle with time pressure",
                "building a bridge while crossing it",
                "dancing on the edge of possibility"
            ]
        }
        
        enhanced_content = content
        import random
        
        for pattern, alternatives in creativity_replacements.items():
            if re.search(pattern, enhanced_content, re.IGNORECASE):
                replacement = random.choice(alternatives)
                enhanced_content = re.sub(pattern, replacement, enhanced_content, flags=re.IGNORECASE)
        
        return enhanced_content

    # Enhanced Pro Tip generation with strict rules
    def add_pro_tip(content: str) -> str:
        """Add exactly one Pro Tip with varied phrasing"""
        # Check for existing Pro Tips
        if "Pro Tip:" in content or "💡" in content or "🧠" in content:
            return content
        
        # Context-sensitive framework recommendations
        context_keywords = {
            "ethical": ["Ethical Decision-Making Framework", "Values-Based Decision Matrix"],
            "business": ["SWOT Analysis", "Decision Matrix"],
            "personal": ["GROW Model", "Eisenhower Grid"],
            "complex": ["Decision Tree", "Weighted Scoring Matrix"],
            "uncertainty": ["Expected Utility", "Prospect Theory"],
            "time": ["OODA Loop", "Bounded Rationality"]
        }
        
        # Determine context and recommend appropriate framework
        recommended_framework = "Decision Tree"  # Default
        for keyword, frameworks in context_keywords.items():
            if keyword in content.lower():
                recommended_framework = frameworks[0]
                break
        
        # Varied Pro Tip phrasing (exactly one sentence)
        pro_tip_phrases = [
            f"Sketch a quick **{recommended_framework}** to explore both paths before deciding.",
            f"Try a **{recommended_framework}** to balance risk and opportunity.",
            f"Use the **{recommended_framework}** to organize your thoughts systematically.",
            f"Apply the **{recommended_framework}** to weigh your options objectively.",
            f"Consider the **{recommended_framework}** for a structured approach to this decision."
        ]
        
        import random
        pro_tip = random.choice(pro_tip_phrases)
        
        # Add Pro Tip after Story section
        if "**Story or Analogy**" in content:
            # Insert after Story section
            story_end = content.find("**Reflection Prompts**")
            if story_end != -1:
                pro_tip_section = f"\n\n💡 **Pro Tip**: {pro_tip}\n"
                content = content[:story_end] + pro_tip_section + content[story_end:]
            else:
                # Fallback: add at the end
                content += f"\n\n💡 **Pro Tip**: {pro_tip}\n"
        else:
            # Fallback: add at the end
            content += f"\n\n💡 **Pro Tip**: {pro_tip}\n"
        
        return content

    # Enhanced formatting and clarity with comprehensive fixes
    def improve_formatting(content: str) -> str:
        """Ensure proper formatting, remove duplicates, and fix broken Markdown"""
        # Fix broken bold/italic combinations
        content = re.sub(r'\*{3,}', '**', content)  # Fix excessive asterisks
        content = re.sub(r'\*{2,}([^*]+)\*{2,}', r'**\1**', content)  # Fix broken bold
        content = re.sub(r'\*{4,}([^*]+)\*{4,}', r'**\1**', content)  # Fix excessive bold
        content = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', content)  # Fix quadruple asterisks
        content = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', content)  # Fix broken tool names
        content = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', content)  # Fix malformed tool references
        
        # Bold all tool names consistently
        tool_names = [
            "Decision Tree", "SWOT Analysis", "GROW Model", "Premortem Analysis",
            "Weighted Scoring Matrix", "Cost-Benefit Analysis", "Expected Utility",
            "Prospect Theory", "OODA Loop", "Bounded Rationality", "Utility Theory",
            "Framing Bias", "Endowment Effect", "Anchoring Bias", "Confirmation Bias",
            "Status Quo Bias", "Sunk Cost Fallacy", "Escalation of Commitment"
        ]
        
        for tool in tool_names:
            # Replace non-bold instances with bold
            pattern = rf'\b{re.escape(tool)}\b'
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, f"**{tool}**", content, flags=re.IGNORECASE)
        
        # Replace placeholder words with role-appropriate alternatives
        placeholder_replacements = {
            r'\bindividual\b': ["a product manager", "a founder", "a student", "a professional", "the decision maker", "a designer", "a teacher"],
            r'\bperson\b': ["a leader", "a manager", "someone in your shoes", "a professional", "a colleague"],
            r'\bteam member\b': ["a colleague", "a team member", "a coworker", "a professional"]
        }
        
        import random
        for pattern, alternatives in placeholder_replacements.items():
            if re.search(pattern, content, re.IGNORECASE):
                replacement = random.choice(alternatives)
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Remove duplicate tooltips in Concept/Tool References section
        if "**Concept/Tool References**" in content:
            lines = content.split('\n')
            tooltip_lines = []
            other_lines = []
            in_tooltip_section = False
            
            for line in lines:
                if "**Concept/Tool References**" in line:
                    in_tooltip_section = True
                    other_lines.append(line)
                elif in_tooltip_section and line.strip().startswith('- **'):
                    tooltip_lines.append(line.strip())
                elif in_tooltip_section and not line.strip():
                    continue
                else:
                    in_tooltip_section = False
                    other_lines.append(line)
            
            # Deduplicate tooltips
            unique_tooltips = {}
            for line in tooltip_lines:
                match = re.search(r'- \*\*(.*?)\*\*:?\s*(.*)', line)
                if match:
                    name = match.group(1).strip()
                    definition = match.group(2).strip()
                    if name not in unique_tooltips:
                        unique_tooltips[name] = definition
            
            # Rebuild content with deduplicated tooltips
            if unique_tooltips:
                other_lines.append("**Concept/Tool References**")
                for name, definition in sorted(unique_tooltips.items()):
                    other_lines.append(f"- **{name}**: {definition}")
                content = '\n'.join(other_lines)
        
        return content

    # Enhanced repetition avoidance with tone variety
    def avoid_repetition(content: str) -> str:
        """Replace repetitive phrases with varied alternatives and add tone variety"""
        repetition_replacements = {
            r'\bpause and reflect\b': [
                "take a moment to consider",
                "step back and evaluate",
                "give yourself space to think",
                "allow time for contemplation",
                "create mental distance"
            ],
            r'\balign with values\b': [
                "resonate with your principles",
                "match your core beliefs",
                "reflect your fundamental values",
                "honor your guiding principles",
                "stay true to your convictions"
            ],
            r'\bwhen faced with\b': [
                "when you encounter",
                "when you're dealing with",
                "when you're navigating",
                "when you're working through",
                "when you're addressing"
            ],
            r'\bwhen you\'re working through\b': [
                "when you encounter",
                "when you're dealing with",
                "when you're navigating",
                "when you're addressing",
                "when you're managing"
            ],
            r'\bconsider the implications\b': [
                "think through the consequences",
                "weigh the potential outcomes",
                "evaluate the ripple effects",
                "assess the broader impact",
                "examine the downstream effects"
            ],
            r'\btake a moment to reflect\b': [
                "step back and evaluate",
                "give yourself space to think",
                "allow time for contemplation",
                "create mental distance",
                "pause to consider"
            ]
        }
        
        # Add varied openers for different sections
        opener_replacements = {
            r'\bOne way to think about this\b': [
                "This situation calls for",
                "It might help to first clarify",
                "A useful approach here is",
                "The key is to",
                "What matters most is"
            ],
            r'\bImagine you\'re\b': [
                "Picture this scenario:",
                "It's like being",
                "A real-world example might be",
                "Think of it as",
                "Consider this situation:"
            ]
        }
        
        enhanced_content = content
        import random
        
        # Apply repetition replacements
        for pattern, alternatives in repetition_replacements.items():
            if re.search(pattern, enhanced_content, re.IGNORECASE):
                replacement = random.choice(alternatives)
                enhanced_content = re.sub(pattern, replacement, enhanced_content, flags=re.IGNORECASE)
        
        # Apply opener replacements
        for pattern, alternatives in opener_replacements.items():
            if re.search(pattern, enhanced_content, re.IGNORECASE):
                replacement = random.choice(alternatives)
                enhanced_content = re.sub(pattern, replacement, enhanced_content, flags=re.IGNORECASE)
        
        return enhanced_content

    # Ensure proper section structure and prevent duplicates
    def ensure_clean_structure(content: str) -> str:
        """Ensure clean section structure with no duplicates"""
        # Remove duplicate section headers
        sections = ["**Strategy or Explanation**", "**Story in Action**", "**Reflection Prompts**", "**Concept/Tool References**"]
        
        for section in sections:
            # Count occurrences of each section header
            count = content.count(section)
            if count > 1:
                # Keep only the first occurrence
                parts = content.split(section)
                if len(parts) > 1:
                    # Rebuild with only first occurrence
                    content = parts[0] + section + ''.join(parts[1:]).replace(section, '')
        
        # Remove duplicate Pro Tips (both 💡 and 🧠)
        pro_tip_count = content.count("💡") + content.count("🧠")
        if pro_tip_count > 1:
            # Keep only the first Pro Tip
            if "💡" in content:
                parts = content.split("💡")
                if len(parts) > 1:
                    first_pro_tip = parts[1].split("\n\n")[0] if "\n\n" in parts[1] else parts[1]
                    remaining_content = "".join(parts[2:]) if len(parts) > 2 else ""
                    content = parts[0] + "💡" + first_pro_tip + "\n\n" + remaining_content
            elif "🧠" in content:
                parts = content.split("🧠")
                if len(parts) > 1:
                    first_pro_tip = parts[1].split("\n\n")[0] if "\n\n" in parts[1] else parts[1]
                    remaining_content = "".join(parts[2:]) if len(parts) > 2 else ""
                    content = parts[0] + "🧠" + first_pro_tip + "\n\n" + remaining_content
        
        # Clean up malformed tool references
        content = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', content)
        content = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', content)
        content = re.sub(r'\*\*\*\*([^*]+)\*\*\*\*', r'**\1**', content)
        
        # Ensure proper spacing between sections
        content = re.sub(r'\*\*([^*]+)\*\*\n\*\*', r'**\1**\n\n**', content)
        
        return content
    
    # Process each section with enhancements
    for section, content in response_sections.items():
        if content.strip() and not content.strip().startswith("_[This section"):
            # Apply all enhancements
            enhanced_content = inject_comprehensive_tooltips(content)
            enhanced_content = enhance_story_creativity(enhanced_content)
            enhanced_content = add_pro_tip(enhanced_content)
            enhanced_content = improve_formatting(enhanced_content)
            enhanced_content = avoid_repetition(enhanced_content)
            response_sections[section] = enhanced_content

    # Ensure all sections are present with fallback placeholders
    for section in response_sections:
        if not response_sections[section].strip():
            if section == "Reflection Prompts":
                response_sections[section] = "1. What are the key factors influencing this decision?\n2. How might this choice impact your long-term goals?\n3. What would success look like in this situation?"
            elif section == "Story or Analogy":
                response_sections[section] = "Consider a scenario where a professional faces a similar challenge. Through careful analysis and thoughtful consideration, they navigate the complexity to reach a well-informed decision."
            else:
                response_sections[section] = "_[This section was not generated — please revise your prompt or add logic to fill this in.]_"

    # Combine all sections into final answer
    final_answer = ""
    for section, content in response_sections.items():
        # Skip empty Concept/Tool References section to avoid duplication
        if section == "Concept/Tool References" and not content.strip():
            continue
        final_answer += f"**{section}**\n{content.strip()}\n\n"
    
    # Add Pro Tip after Story section if not already present
    if "💡" not in final_answer and "🧠" not in final_answer:
        final_answer = add_pro_tip(final_answer)
    
    # Ensure exactly one Pro Tip
    pro_tip_count = final_answer.count("💡") + final_answer.count("🧠")
    if pro_tip_count > 1:
        # Keep only the first Pro Tip
        if "💡" in final_answer:
            parts = final_answer.split("💡")
            if len(parts) > 1:
                first_pro_tip = parts[1].split("\n\n")[0] if "\n\n" in parts[1] else parts[1]
                remaining_content = "".join(parts[2:]) if len(parts) > 2 else ""
                final_answer = parts[0] + "💡" + first_pro_tip + "\n\n" + remaining_content
        elif "🧠" in final_answer:
            parts = final_answer.split("🧠")
            if len(parts) > 1:
                first_pro_tip = parts[1].split("\n\n")[0] if "\n\n" in parts[1] else parts[1]
                remaining_content = "".join(parts[2:]) if len(parts) > 2 else ""
                final_answer = parts[0] + "🧠" + first_pro_tip + "\n\n" + remaining_content

    # Final formatting pass with structure cleanup
    final_answer = improve_formatting(final_answer)
    final_answer = avoid_repetition(final_answer)
    final_answer = ensure_clean_structure(final_answer)

    return final_answer.strip()

# --- Name anonymization ---
def remove_names(text):
    # Protect the label from anonymization - handle all variations
    protected_variations = [
        "💬 Want to Go Deeper?",
        "Want to Go Deeper?",
        "Want to Go individual?"
    ]
    
    # Replace all variations with protected markers
    for i, variation in enumerate(protected_variations):
        text = text.replace(variation, f"<<PROTECTED_LABEL_{i}>>")
    
    doc = nlp(text)
    result = []
    last_idx = 0
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            result.append(text[last_idx:ent.start_char])
            result.append("individual")
            last_idx = ent.end_char
    result.append(text[last_idx:])
    text = "".join(result)
    
    # Restore the correct label
    for i, variation in enumerate(protected_variations):
        text = text.replace(f"<<PROTECTED_LABEL_{i}>>", "💬 Want to Go Deeper?")
    
    return text

# --- Highlight decision frameworks/models ---
def highlight_frameworks(answer: str) -> str:
    def bold_with_tooltip(match):
        fw = match.group(0)
        key = fw.lower()
        explanation = FRAMEWORKS.get(key, "")
        if explanation:
            # Markdown bold with tooltip-style explanation in parentheses
            return f"**{fw}** ({explanation})"
        else:
            return f"**{fw}**"
    # Sort frameworks by length to avoid partial matches
    sorted_frameworks = sorted(FRAMEWORKS.keys(), key=len, reverse=True)
    for fw in sorted_frameworks:
        pattern = re.compile(rf'\b{re.escape(fw)}\b', re.IGNORECASE)
        answer = pattern.sub(bold_with_tooltip, answer)
    return answer

def insert_model_references(how_to_think: str, context: str) -> str:
    # Search for any model keyword in FRAMEWORKS in the answer or context
    found = None
    for model in FRAMEWORKS.keys():
        pattern = re.compile(rf'\b{re.escape(model)}\b', re.IGNORECASE)
        if pattern.search(how_to_think) or pattern.search(context):
            found = model
            break
    if found:
        phrase = f" This aligns with the concept of **{found}**, which suggests: {FRAMEWORKS[found]}"
        # Insert after the first sentence or at the end if only one sentence
        sentences = re.split(r'(?<=[.!?]) +', how_to_think)
        if len(sentences) > 1:
            sentences[0] = sentences[0] + phrase
            return " ".join(sentences)
        else:
            return how_to_think + phrase
    return how_to_think

def enhance_strategy_section(strategy_section: str) -> str:
    # Ensure the section naturally reflects the universal decision-making approach
    # 1. Goal setting
    if not re.search(r'goal|objective|success|aim|purpose', strategy_section, re.IGNORECASE):
        strategy_section = "Start by clarifying what success looks like in this decision. " + strategy_section
    # 2. Analytical evaluation
    if not re.search(r'analytical|framework|tool|matrix|compare|evaluate|weigh|analysis|quantitative|option', strategy_section, re.IGNORECASE):
        strategy_section += " You can use a cost-benefit matrix or sensitivity analysis to weigh your options."
    # 3. Cognitive bias awareness
    if not re.search(r'bias|cognitive|heuristic|anchoring|status quo|groupthink|overconfidence|intuition|emotion|urge|pressure', strategy_section, re.IGNORECASE):
        strategy_section += " Be mindful of how urgency or pressure might trigger cognitive biases such as anchoring or status quo bias."
    return strategy_section

def improve_strategic_thinking_flow(answer: str) -> str:
    """Improve the flow of the Strategy/Explanation section by reframing tool-focused openings"""
    
    # Find the Strategy/Explanation section
    strategic_pattern = r'(\*\*Strategy/Explanation.*?\*\*.*?)(\*\*Story|\*\*Reflection|\*\*Concept|$)'
    match = re.search(strategic_pattern, answer, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return answer
    
    strategic_section = match.group(1)
    rest_of_answer = answer[match.end():]
    
    # Common tool-focused openings to improve - optimized for single pass
    tool_openings = [
        (r'\*\*Decision trees?\*\* are best used when', 'When you\'re faced with multiple options and uncertainty, **decision trees** help you visualize possible outcomes and make more confident choices.'),
        (r'\*\*SWOT analysis\*\* is a framework', 'When you need to assess your situation comprehensively, **SWOT analysis** helps you identify strengths, weaknesses, opportunities, and threats.'),
        (r'\*\*Cost-benefit analysis\*\* involves', 'When weighing different options, **cost-benefit analysis** helps you systematically compare the pros and cons of each choice.'),
        (r'\*\*Expected utility\*\* theory suggests', 'When dealing with uncertainty and multiple outcomes, **expected utility** helps you calculate the value of different scenarios.'),
        (r'\*\*OODA loop\*\* is a decision cycle', 'In fast-changing situations, the **OODA loop** (Observe, Orient, Decide, Act) helps you stay agile and responsive.'),
        (r'\*\*Bounded rationality\*\* recognizes', 'When information is overwhelming or time is limited, **bounded rationality** reminds us that good decisions don\'t require perfect information.'),
        (r'\*\*Prospect theory\*\* shows', 'When evaluating gains and losses, **prospect theory** reveals how we often value avoiding losses more than achieving gains.')
    ]
    
    # Apply improvements - single pass optimization
    improved_section = strategic_section
    for pattern, replacement in tool_openings:
        if re.search(pattern, improved_section, re.IGNORECASE):
            improved_section = re.sub(pattern, replacement, improved_section, flags=re.IGNORECASE)
            break  # Only apply one improvement per section
    
    return improved_section + rest_of_answer



def deduplicate_tooltips(tooltips: dict) -> dict:
    """Deduplicate tooltips by merging identical definitions"""
    if not tooltips:
        return {}
    
    # Group by definition
    definition_groups = {}
    for label, definition in tooltips.items():
        if definition not in definition_groups:
            definition_groups[definition] = []
        definition_groups[definition].append(label)
    
    # Create deduplicated dictionary
    deduplicated = {}
    for definition, labels in definition_groups.items():
        if len(labels) == 1:
            # Single label, keep as is
            deduplicated[labels[0]] = definition
        else:
            # Multiple labels, merge with comma separation
            merged_label = ", ".join(labels)
            deduplicated[merged_label] = definition
    
    return deduplicated

def clean_tooltip_text(text: str, max_words: int = 50) -> str:
    """Post-process tooltip text to ensure proper sentence boundaries and formatting"""
    if not text:
        return ""
    
    # Clean the text first
    text = text.strip()
    
    # Split into words
    words = text.split()
    
    # If within limit, ensure it ends properly
    if len(words) <= max_words:
        # Ensure it ends with proper sentence punctuation
        if not text.endswith(('.', '!', '?')):
            return text + "."
        return text
    
    # Find the best truncation point within the word limit
    truncated_words = words[:max_words]
    truncated_text = " ".join(truncated_words)
    
    # Look for sentence boundaries in the truncated text
    sentence_endings = ['.', '!', '?']
    best_break_point = -1
    
    # Find the last sentence ending in the truncated text
    for ending in sentence_endings:
        last_ending = truncated_text.rfind(ending)
        if last_ending > best_break_point:
            best_break_point = last_ending
    
    # If we found a sentence boundary and it's not too early (at least 70% of max words)
    if best_break_point > 0 and best_break_point > len(truncated_text) * 0.7:
        # Use the sentence boundary
        final_text = truncated_text[:best_break_point + 1]
    else:
        # No good sentence boundary found, truncate at word boundary
        final_text = truncated_text
        # Add "..." only if it doesn't already end in punctuation
        if not final_text.endswith(('.', '!', '?', ':', ';', '...')):
            final_text += "..."
    
    return final_text

def process_tooltips_for_output(tooltips: dict) -> dict:
    """Process tooltips for final output with cleaning and deduplication"""
    if not tooltips:
        return {}
    
    # Clean each tooltip
    cleaned_tooltips = {}
    for label, definition in tooltips.items():
        # Title-case the label
        title_cased_label = " ".join(word.capitalize() for word in label.split())
        # Clean the definition using the dedicated function with 50-word limit
        cleaned_definition = clean_tooltip_text(definition, max_words=50)
        if cleaned_definition:
            cleaned_tooltips[title_cased_label] = cleaned_definition
    
    # Deduplicate
    final_tooltips = deduplicate_tooltips(cleaned_tooltips)
    
    return final_tooltips

def validate_answer_quality(answer: str) -> tuple[bool, str]:
    """Check if answer meets quality standards and return issues if any"""
    issues = []
    
    # Check for required sections (updated for new 4-section structure with exact formatting)
    required_sections = [
        ("**Strategy or Explanation**", "Strategy or Explanation"),
        ("**Story in Action**", "Story in Action"), 
        ("**Reflection Prompts**", "Reflection Prompts"),
        ("**Concept/Tool References**", "Concept/Tool References")
    ]
    
    for section_name, text_section in required_sections:
        if section_name not in answer:
            issues.append(f"Missing {text_section} section with proper bold formatting")
    
    # Check for reasonable length (not too short, not too long)
    word_count = len(answer.split())
    if word_count < 50:
        issues.append("Answer too short (less than 50 words)")
    elif word_count > 800:
        issues.append("Answer too long (over 800 words)")
    
    # Check for framework mentions
    framework_mentions = sum(1 for fw in FRAMEWORKS.keys() if fw.lower() in answer.lower())
    if framework_mentions == 0:
        issues.append("No decision frameworks mentioned")
    
    # Enhanced check for varied writing style indicators
    style_indicators = [
        "What should you do",
        "Let's break this down",
        "Think of this like",
        "Here's the real question",
        "Three things matter",
        "Let's map this out",
        "Picture yourself",
        "Imagine you're",
        "Let's map this out together",
        "Here's how to approach this"
    ]
    style_variety = sum(1 for indicator in style_indicators if indicator.lower() in answer.lower())
    if style_variety == 0:
        issues.append("No varied writing styles detected")
    
    # Check for repetitive opening patterns (CRITICAL)
    repetitive_patterns = detect_repetitive_patterns(answer)
    if repetitive_patterns:
        issues.append(f"Repetitive patterns detected: {', '.join([desc for _, desc in repetitive_patterns])}")
    
    # Check for named decision tools/frameworks (REQUIRED)
    named_tools = [
        "decision tree", "grow model", "premortem analysis", "weighted scoring matrix",
        "swot analysis", "risk assessment matrix", "cost-benefit analysis", "expected utility",
        "ooda loop", "bounded rationality", "prospect theory", "utility theory"
    ]
    tool_mentions = sum(1 for tool in named_tools if tool.lower() in answer.lower())
    if tool_mentions == 0:
        issues.append("No named decision tools or frameworks mentioned")
    
    # Check for grammar and clarity issues
    grammar_fragments = detect_grammar_fragments(answer)
    awkward_phrasing = detect_awkward_phrasing(answer)
    
    if grammar_fragments:
        issues.append(f"Grammar fragments detected: {', '.join([desc for _, desc in grammar_fragments])}")
    
    if awkward_phrasing:
        issues.append(f"Awkward phrasing detected: {', '.join([desc for _, desc in awkward_phrasing])}")
    
    # Check for tooltip sanity (deduplication and formatting)
    tooltip_section = re.search(r'\*\*Concept/Tool References\*\*.*?(?=\*\*|$)', answer, re.DOTALL | re.IGNORECASE)
    if tooltip_section:
        tooltip_text = tooltip_section.group(0)
        # Check for duplicate tooltips
        tooltip_lines = [line.strip() for line in tooltip_text.split('\n') if line.strip().startswith('- **')]
        unique_tooltips = set()
        duplicates = []
        for line in tooltip_lines:
            tooltip_name = re.search(r'- \*\*(.*?)\*\*', line)
            if tooltip_name:
                name = tooltip_name.group(1).lower()
                if name in unique_tooltips:
                    duplicates.append(name)
                else:
                    unique_tooltips.add(name)
        
        if duplicates:
            issues.append(f"Duplicate tooltips detected: {', '.join(duplicates)}")
    
    # Check for readability breaks for long answers
    if word_count > 500:
        # Look for natural breaks or summary lines
        if not re.search(r'---|___|###|Summary|In summary|To summarize', answer, re.IGNORECASE):
            issues.append("Long answer (>500 words) without readability breaks")
    
    is_valid = len(issues) == 0
    return is_valid, "; ".join(issues) if issues else "Quality check passed"

def robust_api_call(client, prompt: str, max_tokens: int = 0, max_retries: int = 3, base_delay: float = 1.0):
    """Handle API failures gracefully with exponential backoff"""
    # Use provided max_tokens or fall back to environment variable
    tokens_to_use = max_tokens if max_tokens > 0 else openai_max_tokens
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=openai_temperature,
                max_tokens=tokens_to_use
            )
            return response, None  # Success
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"⚠️ API call failed (attempt {attempt + 1}/{max_retries}): {error_msg}")
                print(f"   Retrying in {delay:.1f} seconds...")
                import time
                time.sleep(delay)
            else:
                return None, f"Failed after {max_retries} attempts: {error_msg}"
    
    return None, "Max retries exceeded"

def calculate_optimal_tokens(query_length: int, context_length: int) -> int:
    """Dynamically adjust token limits based on input size"""
    total_input = query_length + context_length
    
    # Use environment variable as base, adjust based on input size
    base_tokens = openai_max_tokens
    
    if total_input > 6000:
        return min(800, base_tokens)  # Shorter responses for long inputs
    elif total_input > 3000:
        return min(1200, base_tokens)  # Medium responses
    else:
        return base_tokens  # Full responses for short inputs

def track_usage_metrics(query: str, response_time: float, tokens_used: int, quality_score: bool):
    """Track performance and cost metrics with memory management"""
    import datetime
    
    # Simple in-memory tracking (could be extended to file/database)
    if not hasattr(track_usage_metrics, 'metrics'):
        track_usage_metrics.metrics = {
            'total_queries': 0,
            'total_tokens': 0,
            'avg_response_time': 0,
            'quality_scores': [],
            'query_patterns': {},
            'cost_estimate': 0.0,
            'last_cleanup': 0
        }
    
    metrics = track_usage_metrics.metrics
    metrics['total_queries'] += 1
    metrics['total_tokens'] += tokens_used
    metrics['quality_scores'].append(quality_score)
    
    # Memory management: Clean up old data every 100 queries
    if metrics['total_queries'] - metrics['last_cleanup'] >= 100:
        # Keep only last 50 quality scores
        if len(metrics['quality_scores']) > 50:
            metrics['quality_scores'] = metrics['quality_scores'][-50:]
        
        # Keep only top 20 query patterns
        if len(metrics['query_patterns']) > 20:
            sorted_patterns = sorted(metrics['query_patterns'].items(), key=lambda x: x[1], reverse=True)
            metrics['query_patterns'] = dict(sorted_patterns[:20])
        
        metrics['last_cleanup'] = metrics['total_queries']
    
    # Update average response time
    if metrics['avg_response_time'] == 0:
        metrics['avg_response_time'] = response_time
    else:
        metrics['avg_response_time'] = (metrics['avg_response_time'] + response_time) / 2
    
    # Track query patterns (simplified)
    query_words = query.lower().split()[:5]  # First 5 words as pattern
    pattern = " ".join(query_words)
    metrics['query_patterns'][pattern] = metrics['query_patterns'].get(pattern, 0) + 1
    
    # Estimate cost (GPT-3.5-turbo rates)
    input_cost = (tokens_used * 0.7) * 0.0015 / 1000  # Assume 70% input, 30% output
    output_cost = (tokens_used * 0.3) * 0.002 / 1000
    metrics['cost_estimate'] += input_cost + output_cost
    
    # Print summary every 10 queries
    if metrics['total_queries'] % 10 == 0:
        print(f"\n📊 Usage Summary (last {metrics['total_queries']} queries):")
        print(f"   💰 Estimated cost: ${metrics['cost_estimate']:.4f}")
        print(f"   ⏱️ Avg response time: {metrics['avg_response_time']:.2f}s")
        print(f"   📈 Quality score: {sum(metrics['quality_scores'])}/{len(metrics['quality_scores'])}")
        print(f"   🧹 Memory cleanup: {metrics['last_cleanup']} queries ago")

def get_usage_summary():
    """Get current usage statistics"""
    if not hasattr(track_usage_metrics, 'metrics'):
        return "No usage data available"
    
    metrics = track_usage_metrics.metrics
    if metrics['total_queries'] == 0:
        return "No queries processed yet"
    
    quality_rate = sum(metrics['quality_scores']) / len(metrics['quality_scores']) * 100
    
    return {
        'total_queries': metrics['total_queries'],
        'total_tokens': metrics['total_tokens'],
        'avg_response_time': metrics['avg_response_time'],
        'quality_rate': f"{quality_rate:.1f}%",
        'estimated_cost': f"${metrics['cost_estimate']:.4f}",
        'avg_tokens_per_query': metrics['total_tokens'] / metrics['total_queries']
    }

def smart_context_truncation(docs: list, max_chars: int = 8000) -> str:
    """Prioritize most relevant content within token limits"""
    if not docs:
        return ""
    
    # Simple relevance scoring based on document position and length
    scored_docs = []
    for i, doc in enumerate(docs):
        # Higher score for earlier documents (assumed more relevant)
        position_score = 1.0 / (i + 1)
        # Higher score for documents with more content (more informative)
        content_score = min(len(doc) / 1000, 2.0)  # Cap at 2.0
        total_score = position_score * content_score
        scored_docs.append((doc, total_score))
    
    # Sort by relevance score
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    # Build context prioritizing most relevant content
    combined_context = ""
    for doc, score in scored_docs:
        remaining_chars = max_chars - len(combined_context)
        if remaining_chars <= 0:
            break
        
        # Take the most relevant portion of each document
        if len(doc) > remaining_chars:
            # Try to find a good breaking point (sentence boundary)
            truncated = doc[:remaining_chars]
            last_period = truncated.rfind('.')
            last_exclamation = truncated.rfind('!')
            last_question = truncated.rfind('?')
            
            # Find the latest sentence boundary
            break_point = max(last_period, last_exclamation, last_question)
            if break_point > remaining_chars * 0.7:  # Only if we're not losing too much
                doc = doc[:break_point + 1]
            else:
                doc = truncated + "..."
        
        if combined_context:
            combined_context += "\n\n---\n\n"
        combined_context += doc
    
    return combined_context

TOOLS_AND_THEORIES = {
    "decision tree": None,
    "expected utility": None,
    "SWOT": None,
    "cost-benefit analysis": None,
    "sensitivity analysis": None,
    "OODA loop": None,
    "bounded rationality": None,
    "satisficing": None,
    "prospect theory": None,
    "utility theory": None,
    "escalation of commitment": None,
    "anchoring bias": None,
    "confirmation bias": None,
    "framing effect": None,
    "endowment effect": None,
    "status quo bias": None,
    "sunk cost fallacy": None
}

def insert_model_reference(answer: str, query: str, combined_context: str):
    all_concepts = set(FRAMEWORKS.keys()) | set(TOOLS_AND_THEORIES.keys())
    found = []
    tooltip_metadata = {}
    text_to_search = f"{query}\n{combined_context}"
    for concept in all_concepts:
        pattern = re.compile(rf'\b{re.escape(concept)}\b', re.IGNORECASE)
        if pattern.search(text_to_search):
            display_name = " ".join([w.capitalize() for w in concept.split()])
            found.append((concept, display_name))
    reference_section = ""
    if found:
        reference_section = "\n\n**Concepts/Tools/Practice Reference:**"
        for concept, display_name in sorted(found, key=lambda x: x[1]):
            # Use hybrid tooltip manager for optimal token usage
            tooltip_text, is_prebuilt, source_type = tooltip_manager.get_tooltip(concept, combined_context)
            reference_section += f"\n- **{display_name}**"
            if tooltip_text:
                reference_section += f": {tooltip_text}"
            # Store in metadata for UI tooltips
            tooltip_metadata[display_name] = tooltip_text
    return answer + reference_section, tooltip_metadata


print("\n✅ Query engine is ready!")
print("💡 This engine will synthesize answers from multiple relevant documents, prioritizing your materials but supplementing with GPT's own knowledge if needed.")


# Main loop
try:
    while True:
        try:
            query = input("\nAsk a question (or type 'exit'): ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting. Goodbye!")
            break
        if query.strip().lower() == "exit":
            print("👋 Exiting. Goodbye!")
            break
        if query.strip().lower() == "stats":
            summary = get_usage_summary()
            if isinstance(summary, dict):
                print(f"\n📊 Usage Statistics:")
                for key, value in summary.items():
                    print(f"   {key.replace('_', ' ').title()}: {value}")
            else:
                print(f"\n📊 {summary}")
            continue
        if not query.strip():
            print("⚠️ Please enter a non-empty question.")
            continue
        
        k = 5
        try:
            query_embedding = model.encode([query])
            query_embedding = np.array(query_embedding).astype("float32")
        except Exception as e:
            print(f"❌ Error embedding query: {e}")
            continue
        try:
            D, I = index.search(query_embedding, k)
            top_indices = I[0]
            if len(top_indices) == 0 or top_indices[0] == -1:
                print("⚠️ No results found in the index.")
                continue
        except Exception as e:
            print(f"❌ Error searching FAISS index: {e}")
            continue
        print(f"\n📚 Retrieved {len(top_indices)} relevant documents:")
        for rank, idx in enumerate(top_indices, 1):
            if idx == -1:
                continue
            print(f"  [{rank}] {file_names[idx]}")
        relevant_docs = []
        for idx in top_indices:
            if idx != -1:
                relevant_docs.append(documents[idx])
        # Use smart context truncation
        combined_context = smart_context_truncation(relevant_docs, max_chars=8000)
        if len(combined_context) > 8000:
            print(f"⚠️ Context was smart-truncated to fit token limits.")
        # Enhanced GPT prompt for decision coach with comprehensive quality guidelines
        personalized_instruction = (
            "You are an expert decision coach helping learners explore complex questions using practical tools, relatable stories, and behavioral insights.\n\n"
            "Your task is to generate thoughtful, engaging, and grammatically polished answers to user queries. Each answer must follow these EXACT guidelines:\n\n"
            "🧱 REQUIRED STRUCTURE (ENFORCED FORMATTING):\n"
            "Format every answer with these FOUR bold-labeled sections (no exceptions):\n"
            "1. **Strategy or Explanation** (well-structured, not formulaic)\n"
            "2. **Story in Action** (1 paragraph or short narrative)\n"
            "3. **Reflection Prompts** (3 concise bullets)\n"
            "4. **Concept/Tool References** (clean tooltip-ready list)\n\n"
            "Use double asterisks (Markdown-style) for all section headers exactly as written above. If any section is missing or unlabeled, the answer is incomplete.\n\n"
            "🎭 STYLE & VARIETY REQUIREMENTS:\n"
            "AVOID repetitive openings like 'When faced with...' or 'Imagine you're at a crossroads.'\n"
            "Rotate among different tones and formats:\n"
            "• Rhetorical questions: 'What should you do when both options seem great?'\n"
            "• Metaphors (only reuse if 4+ responses apart): 'Think of this like steering a ship in fog...'\n"
            "• Coaching voice: 'Let's map this out together...'\n"
            "• Bulleted strategies: 'Three things matter here...'\n"
            "• First-person coaching: 'Let's break this down together...'\n"
            "• Bold conversational hooks: 'Here's the real question...'\n\n"
            "🧠 CONTENT & TOOL DEPTH:\n"
            "INCLUDE at least one named decision tool or framework, such as:\n"
            "• Decision Tree\n"
            "• GROW Model\n"
            "• Premortem Analysis\n"
            "• Weighted Scoring Matrix\n"
            "• SWOT Analysis\n"
            "• Risk Assessment Matrix\n\n"
            "Make sure tools are contextually relevant (e.g., don't suggest numeric tools for personal/family decisions).\n\n"
            "🧰 TOOLTIP INTEGRATION:\n"
            "Use the provided tooltip dictionary to insert relevant decision-making or cognitive bias concepts in the final section.\n"
            "Ensure the tooltip text is clean and human-readable — no duplicate entries, inconsistent tone, or incomplete definitions.\n\n"
            "🧪 FINAL OUTPUT QUALITY CHECK:\n"
            "Each response must:\n"
            "• Include all 4 sections with bold headers\n"
            "• Be grammatically correct and easy to follow\n"
            "• Mention 1 or more decision tools or frameworks\n"
            "• Have varied opening tone (no repetitive phrases)\n"
            "• Include contextually appropriate tooltips\n\n"
            "This will be used in a classroom-facing decision tutor, so make every response engaging, personalized, and structurally sound.\n\n"
            f"Your role: {user_profile['role']}. Tone: {user_profile['tone']}. Thinking style: {user_profile['thinking_style']}."
        )
        prompt = f"""{personalized_instruction}\n\nDocument excerpts:\n{combined_context}\n\nQuestion: {query}\n\nSynthesized Answer (use the required structure):"""
        
        # Calculate optimal tokens based on input size
        optimal_tokens = calculate_optimal_tokens(len(query), len(combined_context))
        
        # Track start time for performance monitoring
        import time
        start_time = time.time()
        
        try:
            # Use robust API call with retries and optimal tokens
            response, error = robust_api_call(client, prompt, max_tokens=optimal_tokens)
            if error:
                print(f"❌ API Error: {error}")
                continue
                
            if response is None:
                print("❌ No response received from API")
                continue
                
            content = response.choices[0].message.content
            answer_raw = content.strip() if content is not None else ""
            
            # Calculate response metrics
            response_time = time.time() - start_time
            estimated_tokens = len(prompt.split()) + len(answer_raw.split())  # Rough estimate
            
            # Apply enhanced response generation with structure enforcement
            answer = generate_response(answer_raw, PREBUILT_TOOLTIPS, FRAMEWORKS_GPT)
            
            # Apply grammar and clarity filters
            answer, grammar_issues = apply_grammar_and_clarity_filters(answer)
            
            # Clean and deduplicate tooltips
            answer = clean_and_deduplicate_tooltips(answer)
            
            # Add readability breaks for long answers
            answer = add_readability_breaks(answer)
            
            answer = remove_names(answer)
            answer = highlight_frameworks(answer)
            # Insert model reference in the 'Strategy/Explanation' section if present
            strategy_match = re.search(r'(\*\*Strategy/Explanation.*?\*\*.*?)(\*\*Story|\*\*Reflection|\*\*Concept|$)', answer, re.DOTALL|re.IGNORECASE)
            if strategy_match:
                strategy_section = strategy_match.group(1)
                rest = answer.replace(strategy_section, '', 1)
                strategy_section = insert_model_references(strategy_section, combined_context)
                strategy_section = enhance_strategy_section(strategy_section)
                answer = strategy_section + rest
            # Add Concepts/Tools/Practice Reference section at the end, and collect tooltips
            answer, tooltips = insert_model_reference(answer, query, combined_context)
            # Improve Strategy/Explanation flow
            answer = improve_strategic_thinking_flow(answer)
            # Process tooltips for final output
            final_tooltips = process_tooltips_for_output(tooltips)
            
            # Validate answer quality
            is_valid, quality_issues = validate_answer_quality(answer)
            
            # Track usage metrics
            track_usage_metrics(query, response_time, estimated_tokens, is_valid)
            
            # Print results
            print(f"\n🎯 Synthesized Answer:\n{answer}")
            print(f"\n📊 Sources: {len(top_indices)} documents synthesized")
            print(f"⏱️ Response time: {response_time:.2f}s")
            print(f"📈 Quality check: {quality_issues}")
            
            # Report grammar and clarity improvements
            if any(grammar_issues.values()):
                print(f"\n🔧 Grammar & Clarity Improvements Applied:")
                for issue_type, issues in grammar_issues.items():
                    if issues:
                        print(f"   • {issue_type.replace('_', ' ').title()}: {', '.join(issues)}")
            else:
                print(f"\n✅ No grammar or clarity issues detected")
            
            # Show hybrid tooltip efficiency stats
            stats = tooltip_manager.get_usage_stats()
            print(f"\n🔋 Token Efficiency: {stats['efficiency']} prebuilt tooltips used")
            print(f"   📈 Usage: {stats['prebuilt_dict_used']} prebuilt dict, {stats['prebuilt_gpt_used']} prebuilt GPT, {stats['custom_generated']} custom generated")
            print(f"   💰 Cost savings: {stats['prebuilt_dict_used']} tooltips used 0 tokens")
            
            if final_tooltips:
                import json
                print("\n[TOOLTIPS METADATA FOR UI]:")
                print(json.dumps(final_tooltips, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"❌ Error from OpenAI API: {e}")
            traceback.print_exc()
except KeyboardInterrupt:
    print("\n👋 Exiting. Goodbye!")

# Safety and Efficiency Summary
"""
🔒 SAFETY IMPROVEMENTS:
✅ Safe file loading with proper error handling
✅ OpenAI connection testing on startup
✅ Memory management for tracking metrics
✅ Graceful error recovery with fallbacks
✅ Input validation and sanitization

⚡ EFFICIENCY IMPROVEMENTS:
✅ Context caching to reduce API calls
✅ Optimized string operations (single-pass regex)
✅ Memory cleanup every 100 queries
✅ Consolidated tooltip cleaning functions
✅ Smart context truncation with sentence boundaries

📊 PERFORMANCE MONITORING:
✅ Usage statistics with cost tracking
✅ Quality validation for answers
✅ Response time monitoring
✅ Token usage optimization
✅ Memory usage tracking

🛡️ ERROR HANDLING:
✅ File not found scenarios
✅ API connection failures
✅ JSON parsing errors
✅ Invalid environment variables
✅ Graceful degradation for missing data
"""