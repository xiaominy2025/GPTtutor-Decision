#!/usr/bin/env python3
"""
Script to remove all debug print statements from query_engine.py
"""

import re

# Read the file
with open('query_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all debug print statements
lines = content.split('\n')
clean_lines = []

for line in lines:
    # Skip lines that start with debug print statements
    if line.strip().startswith('print(f"DEBUG:'):
        continue
    if line.strip().startswith('print(f"DEBUG: '):
        continue
    if 'DEBUG:' in line and 'print(' in line:
        continue
    clean_lines.append(line)

# Write back the cleaned content
with open('query_engine.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(clean_lines))

print("✅ Removed all debug print statements from query_engine.py") 