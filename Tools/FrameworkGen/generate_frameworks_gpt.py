
from docx import Document
import re
from collections import defaultdict
import openai
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Import canonical frameworks from the generated frameworks.py in the project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))  # Add project root to sys.path
try:
    from frameworks import FRAMEWORKS as CANONICAL_FRAMEWORKS
except ImportError:
    CANONICAL_FRAMEWORKS = {}

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Default to cost-effective model
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "150"))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.5"))

# Initialize OpenAI client (new API)
client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None

def extract_context_from_docx(docx_path):
    doc = Document(docx_path)
    context_index = defaultdict(str)
    current_heading = ""
    buffer = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if para.style.name.startswith("Heading"):
            if current_heading and buffer:
                context_index[current_heading] = " ".join(buffer)
            current_heading = text
            buffer = []
        else:
            buffer.append(text)

    if current_heading and buffer:
        context_index[current_heading] = " ".join(buffer)

    return context_index

def generate_gpt_definition(term, base_definition, context=None):
    prompt = f"""You're an AI coach assistant. Rewrite the following draft explanation of a decision-making concept into a clear, student-friendly definition that fits a course on strategic decision-making.

Term: {term}
Draft definition: {base_definition}
"""
    if context:
        prompt += f"\nAdditional context: {context}\n"
    prompt += "\nDefinition:"
    try:
        response = client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=openai_temperature,
            max_tokens=openai_max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT error: {e}"

def generate_frameworks_with_gpt(docx_path, output_path):
    context_map = extract_context_from_docx(docx_path)
    all_terms = set(context_map.keys()) | set(CANONICAL_FRAMEWORKS.keys())
    frameworks_dict = {}
    for heading in sorted(all_terms):
        if 3 < len(heading) < 80:
            base_definition = CANONICAL_FRAMEWORKS.get(heading, "")
            context = context_map.get(heading, "")
            gpt_definition = generate_gpt_definition(heading, base_definition, context)
            frameworks_dict[heading] = gpt_definition
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(frameworks_dict, f, ensure_ascii=False, indent=2)
    print(f"✅ GPT-enhanced framework dictionary saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_frameworks_gpt.py <input.docx> <output.json>")
    else:
        if not openai_api_key:
            print("❌ OPENAI_API_KEY not found in .env file.")
        else:
            generate_frameworks_with_gpt(sys.argv[1], sys.argv[2])
