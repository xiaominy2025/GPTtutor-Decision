import json
import os
import re

def comprehensive_reference_replacement():
    """
    Comprehensive replacement of all reference queries in query_engine.py:
    1. Completely remove all old reference queries from semantic detection function
    2. Insert the new 79 queries from reference_queries_updated.json
    3. Verify no legacy content remains
    4. Ensure consistency with the updated list
    """
    
    print("🔍 COMPREHENSIVE REFERENCE QUERY REPLACEMENT")
    print("=" * 60)
    
    # Read the updated reference queries
    json_path = 'reference_queries_updated.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Found {len(data)} updated reference queries")
    
    # Organize queries by domain
    domain_mapping = {
        'S': 'strategic',
        'T': 'technical', 
        'H': 'behavioral',
        'N': 'negotiation'
    }
    
    new_domain_references = {}
    for item in data:
        query = item['query']
        domains = item['domains']
        
        # Map domain codes to full names
        for domain_code in domains:
            domain_name = domain_mapping.get(domain_code)
            if domain_name:
                if domain_name not in new_domain_references:
                    new_domain_references[domain_name] = []
                new_domain_references[domain_name].append(query)
    
    print("\n📊 Domain distribution:")
    for domain, queries in new_domain_references.items():
        print(f"  {domain}: {len(queries)} queries")
    
    # Create the new domain_references content
    new_domain_references_content = """        # 79 updated domain-specific reference queries (hardcoded for performance)
        domain_references = {
"""
    
    for domain_name, queries in new_domain_references.items():
        new_domain_references_content += f"            '{domain_name}': [\n"
        for query in queries:
            new_domain_references_content += f'                "{query}",\n'
        new_domain_references_content += "            ],\n"
    
    new_domain_references_content += "        }\n"
    
    # Read the current query_engine.py
    query_engine_path = 'Repeatability/query_engine.py'
    with open(query_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n🔍 Searching for semantic detection function...")
    
    # Find the detect_domain_semantic function
    function_start = re.search(r'def detect_domain_semantic\(query: str\) -> dict:', content)
    if not function_start:
        print("❌ Could not find detect_domain_semantic function")
        return
    
    print("✅ Found detect_domain_semantic function")
    
    # Find the domain_references section within this function
    # Look for the pattern: domain_references = { ... }
    start_pattern = r'(\s+)domain_references = \{'
    end_pattern = r'(\s+)\}'
    
    start_match = re.search(start_pattern, content)
    if not start_match:
        print("❌ Could not find domain_references section")
        return
    
    start_pos = start_match.start()
    
    # Find the matching closing brace by counting braces
    brace_count = 1
    pos = start_match.end()
    
    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count != 0:
        print("❌ Could not properly parse domain_references section structure")
        return
    
    end_pos = pos
    
    print(f"✅ Found domain_references section (lines {content[:start_pos].count(chr(10)) + 1}-{content[:end_pos].count(chr(10)) + 1})")
    
    # Extract the current content for verification
    current_section = content[start_pos:end_pos]
    print(f"\n🔍 Current section contains {len(current_section)} characters")
    
    # Check for legacy content
    legacy_indicators = [
        "Placeholder query",
        "bargaining positions",
        "joint venture",
        "merger negotiation",
        "supplier negotiations",
        "contract negotiation",
        "BATNA",
        "anchoring offers"
    ]
    
    legacy_found = []
    for indicator in legacy_indicators:
        if indicator in current_section:
            legacy_found.append(indicator)
    
    if legacy_found:
        print(f"⚠️  Found legacy content: {', '.join(legacy_found)}")
    else:
        print("✅ No obvious legacy content found")
    
    # Replace the entire section
    before_section = content[:start_pos]
    after_section = content[end_pos:]
    
    new_content = before_section + new_domain_references_content + after_section
    
    # Write the updated content
    with open(query_engine_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ Successfully updated {query_engine_path}")
    
    # Verify the replacement
    print("\n🔍 Verifying replacement...")
    with open(query_engine_path, 'r', encoding='utf-8') as f:
        new_file_content = f.read()
    
    # Check if new queries are present
    verification_queries = [
        "How do I decide whether to expand capacity now or wait until demand is clearer?",
        "My forecasting model fits historical data but fails during shocks. How should I improve it?",
        "Why do managers keep funding projects even when the numbers show it's a loss?"
    ]
    
    all_present = True
    for query in verification_queries:
        if query not in new_file_content:
            print(f"❌ Verification failed: '{query}' not found")
            all_present = False
    
    if all_present:
        print("✅ Verification successful: New queries are present")
    
    # Check if legacy content was removed
    legacy_removed = True
    for indicator in legacy_indicators:
        if indicator in new_file_content:
            print(f"⚠️  Legacy content still present: '{indicator}'")
            legacy_removed = False
    
    if legacy_removed:
        print("✅ Legacy content successfully removed")
    
    print("\n" + "=" * 60)
    print("🎯 REPLACEMENT COMPLETE")
    print(f"📊 Final domain distribution:")
    for domain, queries in new_domain_references.items():
        print(f"  {domain}: {len(queries)} queries")
    
    return True

if __name__ == "__main__":
    comprehensive_reference_replacement()
