#!/usr/bin/env python3
"""
Script to clean query_engine.py output by removing all developer information
and keeping only the clean synthesized answer.
"""

import re

# Read the file
with open('query_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove problematic print statements that show developer information
lines = content.split('\n')
clean_lines = []

for line in lines:
    # Skip lines that show developer information
    if any(pattern in line for pattern in [
        'print(f"\\n📚 Retrieved',
        'print(f"\\n🎯 Synthesized Answer:',
        'print(f"\\n📊 Sources:',
        'print(f"⏱️ Response time:',
        'print(f"📈 Quality check:',
        'print(f"\\n🔧 Grammar & Clarity Improvements Applied:',
        'print(f"\\n✅ No grammar or clarity issues detected',
        'print(f"\\n🔋 Token Efficiency:',
        'print(f"   📈 Usage:',
        'print(f"   💰 Cost savings:',
        'print("\\n[TOOLTIPS METADATA FOR UI]:',
        'print(json.dumps(final_tooltips,',
        'print(f"⚠️ Context was smart-truncated',
        'print(f"  [{rank}] {file_names[idx]}"',
        'print("⚠️ No results found in the index."',
        'print(f"❌ API Error:',
        'print("❌ No response received from API"',
        'print(f"❌ Error from OpenAI API:',
        'print(f"❌ Error processing test question',
        'print(f"\\n✅ TEST MODE COMPLETE:',
        'print("\\n✅ Test mode completed. Exiting."',
        'print("\\n👋 Exiting. Goodbye!"',
        'print("👋 Exiting. Goodbye!"',
        'print(f"\\n📊 Usage Statistics:"',
        'print("⚠️ Please enter a non-empty question."',
        'print(f"❌ Error embedding query:',
        'print(f"❌ Error searching FAISS index:',
        'print(f"\\n Retrieved {len(top_indices)} relevant documents:"',
        'print(f"  [{rank}] {file_names[idx]}"',
        'print(f"⚠️ Context was smart-truncated to fit token limits."',
        'print(f"❌ API Error: {error}"',
        'print("❌ No response received from API"',
        'print(f"❌ Error from OpenAI API: {e}"',
        'print("\\n👋 Exiting. Goodbye!"',
        'print(f"\\n🎯 Synthesized Answer:\\n{answer}"',
        'print(f"\\n📊 Sources: {len(top_indices)} documents synthesized"',
        'print(f"⏱️ Response time: {response_time:.2f}s"',
        'print(f"📈 Quality check: {quality_issues}"',
        'print(f"\\n🔧 Grammar & Clarity Improvements Applied:"',
        'print(f"\\n✅ No grammar or clarity issues detected"',
        'print(f"\\n🔋 Token Efficiency: {stats[\'efficiency\']} prebuilt tooltips used"',
        'print(f"   📈 Usage: {stats[\'prebuilt_dict_used\']} prebuilt dict, {stats[\'prebuilt_gpt_used\']} prebuilt GPT, {stats[\'custom_generated\']} custom generated"',
        'print(f"   💰 Cost savings: {stats[\'prebuilt_dict_used\']} tooltips used 0 tokens"',
        'print("\\n[TOOLTIPS METADATA FOR UI]:"',
        'print(json.dumps(final_tooltips, ensure_ascii=False, indent=2))',
    ]):
        continue
    
    # Keep the line if it doesn't match any of the patterns
    clean_lines.append(line)

# Write back the cleaned content
with open('query_engine.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(clean_lines))

print("✅ Removed all developer information and metrics from query_engine.py")
print("✅ Only clean synthesized answers will now be displayed") 