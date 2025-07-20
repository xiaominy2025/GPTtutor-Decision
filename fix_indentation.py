#!/usr/bin/env python3
"""
Script to fix indentation issues in query_engine.py
"""

import re

# Read the file
with open('query_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix indentation issues
lines = content.split('\n')
fixed_lines = []

for line in lines:
    # Fix lines that have "pass  # Empty body" without proper indentation
    if line.strip() == 'pass  # Empty body':
        # Find the previous line to determine proper indentation
        if len(fixed_lines) > 0:
            prev_line = fixed_lines[-1]
            if prev_line.strip().endswith(':'):
                # Get the indentation from the previous line
                indent = len(prev_line) - len(prev_line.lstrip())
                fixed_lines.append(' ' * (indent + 4) + 'pass  # Empty body')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write back the fixed content
with open('query_engine.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("✅ Fixed indentation issues in query_engine.py") 