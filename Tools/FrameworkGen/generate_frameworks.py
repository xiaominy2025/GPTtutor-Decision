
import json
from docx import Document
import re
from collections import defaultdict
import sys

def generate_frameworks(docx_path, output_path):
    """
    Extracts frameworks from a DOCX file, using headings as keys and the first 2+ sentences as summaries.
    Outputs a Python file with a FRAMEWORKS dictionary for use in other tools.
    """
    try:
        doc = Document(docx_path)
    except Exception as e:
        print(f"❌ Error opening DOCX file: {e}")
        return
    context_index = defaultdict(str)
    current_heading = ""
    buffer = []

    # Build context map
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

    # Extract definitions from heading-context mapping
    frameworks = {}
    for heading, content in context_index.items():
        sentences = re.split(r'(?<=[.!?]) +', content)
        # Always take at least two sentences
        summary = " ".join(sentences[:2]).strip()
        if len(sentences) > 2 and len(summary) < 60:
            summary = " ".join(sentences[:3]).strip()
        if 30 < len(summary) < 350:
            frameworks[heading] = summary

    # Write to output .py file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# This file is auto-generated. You can add custom frameworks below.\n")
            f.write("import json\n\n")
            f.write("FRAMEWORKS = ")
            json.dump(frameworks, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.write("# Add custom frameworks below, e.g.:\n# FRAMEWORKS['My Custom Model'] = 'Short description.'\n")
        print(f"✅ Framework dictionary saved to {output_path}")
    except Exception as e:
        print(f"❌ Error writing output file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_frameworks.py <input.docx> <output.py>")
    else:
        generate_frameworks(sys.argv[1], sys.argv[2])
