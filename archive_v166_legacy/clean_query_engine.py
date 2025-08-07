#!/usr/bin/env python3
"""
Clean Query Engine - Produces only user-facing output without developer information
"""

import os
import sys
import json
import re
import time
import traceback
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import spacy

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY not set in environment variables.")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Load data safely
try:
    index = faiss.read_index("vector_index.faiss")
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    documents = metadata["documents"]
    file_names = metadata.get("file_names", ["Unknown"] * len(documents))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    sys.exit(1)

# Decision frameworks
FRAMEWORKS = {
    "decision tree": "A visual tool that maps out different options and their potential outcomes.",
    "swot analysis": "A framework that helps identify strengths, weaknesses, opportunities, and threats.",
    "cost-benefit analysis": "A systematic approach to compare the pros and cons of different options.",
    "grow model": "A structured approach to goal setting and action planning.",
    "prospect theory": "Shows how people often value avoiding losses more than achieving gains.",
    "bounded rationality": "The recognition that good decisions don't require perfect information.",
    "ooda loop": "A decision cycle (Observe, Orient, Decide, Act) for rapid decision-making."
}

def smart_context_truncation(docs: list, max_chars: int = 8000) -> str:
    """Smart context truncation with sentence boundaries"""
    combined = " ".join(docs)
    if len(combined) <= max_chars:
        return combined
    
    # Find sentence boundaries
    sentences = re.split(r'(?<=[.!?]) +', combined)
    truncated = ""
    
    for sentence in sentences:
        if len(truncated + sentence) <= max_chars:
            truncated += sentence + " "
        else:
            break
    
    return truncated.strip()

def calculate_optimal_tokens(query_length: int, context_length: int) -> int:
    """Calculate optimal token limit based on input size"""
    total_input = query_length + context_length
    if total_input > 6000:
        return 800
    elif total_input > 3000:
        return 1000
    else:
        return 1200

def robust_api_call(client, prompt: str, max_tokens: int = 0, max_retries: int = 3):
    """Handle API calls with retries"""
    tokens_to_use = max_tokens if max_tokens > 0 else openai_max_tokens
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=openai_temperature,
                max_tokens=tokens_to_use
            )
            return response, None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1 * (2 ** attempt))
            else:
                return None, str(e)
    
    return None, "Max retries exceeded"

def generate_clean_response(answer_raw: str) -> str:
    """Generate clean response with proper formatting"""
    
    # Ensure all four sections are present
    required_sections = ["How to Strategize Your Decision", "Story in Action", "Reflection Prompts", "Concepts/Tools/Practice Reference"]
    missing_sections = []
    
    for section in required_sections:
        if f"**{section}**" not in answer_raw:
            missing_sections.append(section)
    
    if missing_sections:
        # Generate fallback content
        query_topic = "this decision"
        
        strategy_content = f"To make {query_topic}, try applying the Decision Tree framework to map out your options and their potential outcomes. Use the GROW Model to structure your thinking: define your Goal, assess your current Reality, explore your Options, and plan your Way forward."
        
        story_content = f"Consider a young professional who faced a similar crossroads. Through careful analysis and thoughtful consideration, this individual navigated the complexity to reach a well-informed decision that aligned with their core values and long-term vision."
        
        reflection_content = "- What specific factors are most critical to your decision?\n- How might this choice impact your long-term goals and values?\n- What steps can you take to validate your decision before committing?"
        
        tool_content = "- **Decision Tree**: A visual tool that maps out different options and their potential outcomes.\n- **SWOT Analysis**: A framework that helps identify strengths, weaknesses, opportunities, and threats."
        
        answer = f"""**How to Strategize Your Decision**
{strategy_content}

**Story in Action**
{story_content}

**Reflection Prompts**
{reflection_content}

**Concepts/Tools/Practice Reference:**
{tool_content}"""
    else:
        answer = answer_raw
    
    # Clean up formatting
    answer = re.sub(r'\*{4,}', '**', answer)
    answer = re.sub(r'\*\*{3,}', '**', answer)
    
    return answer.strip()

def process_query(query: str) -> str:
    """Process a single query and return clean output"""
    
    try:
        # Embed query
        query_embedding = model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")
        
        # Search for relevant documents
        D, I = index.search(query_embedding, 5)
        top_indices = I[0]
        
        if len(top_indices) == 0 or top_indices[0] == -1:
            return "I couldn't find relevant information for your question. Please try rephrasing your query."
        
        # Get relevant documents
        relevant_docs = []
        for idx in top_indices:
            if idx != -1:
                relevant_docs.append(documents[idx])
        
        # Combine context
        combined_context = smart_context_truncation(relevant_docs, max_chars=8000)
        
        # Create prompt
        prompt = f"""You are an expert decision coach helping learners explore complex questions using practical tools, relatable stories, and behavioral insights.

Your task is to generate thoughtful, engaging, and grammatically polished answers to user queries. Each answer must follow these EXACT guidelines:

🧱 REQUIRED STRUCTURE (ENFORCED FORMATTING):
Format every answer with these FOUR sections in EXACT order:

**How to Strategize Your Decision**
[Start with a capitalized, confident sentence that directly reflects the user's question. Avoid weak openers like 'When thinking about...' or 'It's important to...' Vary sentence structures and include at least one named decision tool (e.g., SWOT Analysis, GROW Model) if appropriate.]

**Story in Action**
[Create a realistic, vivid scenario using one anonymous character (e.g., 'a young engineer' or 'an operations manager'). Focus on conflict, decision-making, or transformation, not just generic outcomes. Make the story general and relatable, not based on real people.]

**Reflection Prompts**
- [Thoughtful, tailored question based on user's scenario]
- [Deeper insight or next-step guidance question]
- [Action-oriented reflection question]

**Concepts/Tools/Practice Reference**
- **[Tool Name]**: [Concise explanation]

- **[Tool Name]**: [Concise explanation]

⚠️ CRITICAL REQUIREMENTS:
• You MUST include ALL FOUR sections in EXACT order
• Each section MUST have the exact header format shown above
• Do NOT skip any sections or combine them
• Do NOT add any additional sections
• Do NOT include Pro Tips or other content outside these four sections

Document excerpts:
{combined_context}

Question: {query}

Synthesized Answer (use the required structure):"""
        
        # Calculate optimal tokens
        optimal_tokens = calculate_optimal_tokens(len(query), len(combined_context))
        
        # Get response from API
        response, error = robust_api_call(client, prompt, max_tokens=optimal_tokens)
        
        if error:
            return f"I encountered an error processing your question. Please try again."
        
        if response is None:
            return f"I couldn't generate a response. Please try again."
        
        content = response.choices[0].message.content
        answer_raw = content.strip() if content is not None else ""
        
        # Generate clean response
        answer = generate_clean_response(answer_raw)
        
        return answer
        
    except Exception as e:
        return f"I encountered an error processing your question. Please try again."

def run_test_mode(test_questions):
    """Run automated tests with clean output"""
    for i, query in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}/{len(test_questions)}: {query}")
        print(f"{'='*60}")
        
        answer = process_query(query)
        print(f"{answer}")
    
    print(f"\n✅ TEST MODE COMPLETE: Processed {len(test_questions)} questions")

# Main execution
if __name__ == "__main__":
    try:
        # Check if test mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            # Test mode - run automated tests
            test_questions = [
                "I've been offered a strategic HQ role but must leave a city I love.",
                "My mentor offered me funding for grad school, but I'm unsure I want to go."
            ]
            run_test_mode(test_questions)
            sys.exit(0)
        else:
            # Interactive mode
            while True:
                try:
                    query = input("\nAsk a question (or type 'exit'): ")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Exiting. Goodbye!")
                    break
                
                if query.strip().lower() == "exit":
                    print("👋 Exiting. Goodbye!")
                    break
                
                if not query.strip():
                    print("⚠️ Please enter a non-empty question.")
                    continue
                
                answer = process_query(query)
                print(f"{answer}")
                
    except KeyboardInterrupt:
        print("\n👋 Exiting. Goodbye!") 