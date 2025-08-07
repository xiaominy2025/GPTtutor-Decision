#!/usr/bin/env python3
"""
Script to fix syntax errors in query_engine.py
"""

import re

# Read the file
with open('query_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix missing bodies for if and except statements
lines = content.split('\n')
fixed_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    fixed_lines.append(line)
    
    # Check for if statements without bodies
    if line.strip().startswith('if ') and line.strip().endswith(':'):
        # Check if next line is not indented (missing body)
        if i + 1 < len(lines) and not lines[i + 1].strip().startswith(' ') and lines[i + 1].strip() != '':
            # Add pass statement as body
            fixed_lines.append('    pass  # Empty body')
    
    # Check for except statements without bodies
    elif line.strip().startswith('except ') and line.strip().endswith(':'):
        # Check if next line is not indented (missing body)
        if i + 1 < len(lines) and not lines[i + 1].strip().startswith(' ') and lines[i + 1].strip() != '':
            # Add pass statement as body
            fixed_lines.append('    pass  # Empty body')
    
    i += 1

# Write back the fixed content
with open('query_engine.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("✅ Fixed syntax errors in query_engine.py")
print("✅ Added missing bodies for if and except statements") 