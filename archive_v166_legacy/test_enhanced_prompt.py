#!/usr/bin/env python3
"""
Test script for the enhanced GPT prompt in query_engine.py
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY not set in environment variables.")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

def test_enhanced_prompt():
    """Test the enhanced GPT prompt with a sample decision-making question"""
    
    # Enhanced GPT prompt (copied from query_engine.py)
    enhanced_prompt = (
        "You are an expert decision coach helping learners explore complex questions using practical tools, relatable stories, and behavioral insights.\n\n"
        "Your task is to generate thoughtful, engaging, and grammatically polished answers to user queries. Each answer should:\n\n"
        "1. Use **varied structure and style** to prevent repetition.\n"
        "2. Include **a strategic explanation**, **a relevant story or analogy**, **2-4 reflection prompts**, and **a reference list of key concepts**.\n"
        "3. Be **grammatically correct**, **clear**, and free of awkward phrasing (e.g., fix fragments like 'individual, a professional…').\n"
        "4. Use a **teaching tone** — warm, smart, and human — like a great professor-coach.\n\n"
        "🎨 Vary the way you present ideas. Avoid repetitive structures like 'When considering…' or 'It's essential to…' at the beginning of every response.\n\n"
        "Use different styles across answers:\n"
        "• Start with a question: 'What should you do when both options seem great?'\n"
        "• Use direct coaching: 'Let's map this out together.'\n"
        "• Offer metaphors: 'Think of this like steering a ship in fog...'\n"
        "• Try bullet-point logic or 'Do's and Don'ts' when useful.\n\n"
        "✍️ Always run a quick internal grammar and clarity check. If something sounds off or robotic, rewrite it.\n\n"
        "🎯 Final output = 4 sections:\n"
        "1. **Strategy/Explanation** (well-structured, not formulaic)\n"
        "2. **Story or Analogy** (1 paragraph or short narrative)\n"
        "3. **Reflection Prompts** (3 concise bullets)\n"
        "4. **Concept/Tool References** (clean tooltip-ready list)\n\n"
        "This will be used in a classroom-facing decision tutor, so make the response insightful, engaging, and correct — every time.\n\n"
        "Your role: helpful tutor. Tone: encouraging and clear. Thinking style: step-by-step reasoning."
    )
    
    # Test question
    test_question = "How should I decide between two job offers when both seem equally good?"
    
    # Create the full prompt
    full_prompt = f"{enhanced_prompt}\n\nQuestion: {test_question}\n\nSynthesized Answer (use the required structure):"
    
    print("🧪 Testing Enhanced GPT Prompt")
    print("=" * 50)
    print(f"Question: {test_question}")
    print("\nGenerating response...")
    
    try:
        response = client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        answer = content.strip() if content is not None else ""
        
        print("\n✅ Response Generated Successfully!")
        print("=" * 50)
        print(answer)
        
        # Validate the response structure
        print("\n🔍 Structure Validation:")
        print("-" * 30)
        
        required_sections = [
            "Strategy/Explanation",
            "Story or Analogy", 
            "Reflection Prompts",
            "Concept/Tool References"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in answer:
                missing_sections.append(section)
            else:
                print(f"✅ Found: {section}")
        
        if missing_sections:
            print(f"❌ Missing sections: {', '.join(missing_sections)}")
        else:
            print("✅ All required sections present!")
        
        # Check for varied writing style indicators
        style_indicators = [
            "What should you do",
            "Let's map this out",
            "Think of this like",
            "Do's and Don'ts"
        ]
        
        found_styles = []
        for indicator in style_indicators:
            if indicator.lower() in answer.lower():
                found_styles.append(indicator)
        
        if found_styles:
            print(f"✅ Varied writing styles detected: {', '.join(found_styles)}")
        else:
            print("⚠️ No varied writing style indicators found")
        
        # Word count check
        word_count = len(answer.split())
        print(f"📊 Word count: {word_count} words")
        
        if 100 <= word_count <= 800:
            print("✅ Word count is within reasonable range")
        else:
            print(f"⚠️ Word count ({word_count}) may be outside optimal range")
            
    except Exception as e:
        print(f"❌ Error generating response: {e}")

if __name__ == "__main__":
    test_enhanced_prompt() 