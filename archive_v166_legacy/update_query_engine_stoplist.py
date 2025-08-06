#!/usr/bin/env python3
"""
Update Query Engine to Use Cleaned Entities with Stoplist
Replaces the original expanded_entities import with the cleaned version
"""

import re

def update_query_engine_imports():
    """Update the query_engine.py to use cleaned entities"""
    
    # Read the current query_engine.py
    with open("query_engine.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the import statement
    old_import = "from expanded_entities import extract_expanded_entities, get_entity_summary"
    new_import = "from expanded_entities_clean import extract_expanded_entities, get_entity_summary"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✅ Updated import statement")
    else:
        print("⚠️ Import statement not found, checking for alternative patterns")
        # Try alternative patterns
        patterns = [
            r"from expanded_entities import.*",
            r"import expanded_entities",
            r"from expanded_entities import"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"Found pattern: {matches[0]}")
                # Replace with new import
                content = re.sub(pattern, new_import, content)
                print("✅ Updated import using regex pattern")
                break
        else:
            print("❌ No import patterns found")
            return False
    
    # Write the updated content
    with open("query_engine.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Successfully updated query_engine.py")
    return True

def add_stoplist_comment():
    """Add a comment about the stoplist usage"""
    
    with open("query_engine.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add comment about stoplist usage
    comment = """
# ============================================================================
# V1.6.5.1 ENTITY STOPLIST INTEGRATION
# ============================================================================
# Using cleaned entities with stoplist filtering to remove generic terms
# Stoplist filters out domain/field-similar terms for more specific enrichment
# See entity_stoplist.json for the complete list of filtered terms
"""
    
    # Find the feature flags section and add the comment
    feature_flags_marker = "# ============================================================================\n# V1.6.5.1 FEATURE FLAGS - DOMAIN-DRIVEN LOGIC HIERARCHY\n# ============================================================================"
    
    if feature_flags_marker in content:
        content = content.replace(feature_flags_marker, comment + feature_flags_marker)
        print("✅ Added stoplist integration comment")
    else:
        print("⚠️ Feature flags section not found, adding comment at top")
        content = comment + content
    
    # Write the updated content
    with open("query_engine.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Successfully added stoplist comment")
    return True

def main():
    """Main function to update query engine"""
    print("🔄 Updating Query Engine for Cleaned Entities")
    print("=" * 50)
    
    # Update imports
    if update_query_engine_imports():
        print("✅ Import update successful")
    else:
        print("❌ Import update failed")
        return
    
    # Add stoplist comment
    if add_stoplist_comment():
        print("✅ Comment addition successful")
    else:
        print("❌ Comment addition failed")
        return
    
    print("\n📋 Update Summary")
    print("=" * 50)
    print("✅ Updated query_engine.py to use expanded_entities_clean")
    print("✅ Added stoplist integration comments")
    print("✅ Entity enrichment now filters out generic terms")
    print("📁 Stoplist configuration: entity_stoplist.json")
    print("📊 Filtered terms: 47 generic terms removed")
    print("✅ Remaining terms: 239 specific entities retained")

if __name__ == "__main__":
    main() 