#!/usr/bin/env python3
"""
Update Query Engine to Use Static Clean Entities
Replaces runtime stoplist filtering with static clean_entities.json
"""

import re

def update_query_engine_imports():
    """Update the query_engine.py to use static clean entities"""
    
    # Read the current query_engine.py
    with open("query_engine.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the import statement
    old_import = "from expanded_entities_clean import extract_expanded_entities, get_entity_summary"
    new_import = "from clean_entities_static import extract_expanded_entities, get_entity_summary"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✅ Updated import statement to use static entities")
    else:
        print("⚠️ Import statement not found, checking for alternative patterns")
        # Try alternative patterns
        patterns = [
            r"from expanded_entities_clean import.*",
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

def update_stoplist_comment():
    """Update the stoplist integration comment to reflect static usage"""
    
    with open("query_engine.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update comment about static entities usage
    new_comment = """
# ============================================================================
# V1.6.5.1 STATIC ENTITIES INTEGRATION
# ============================================================================
# Using static clean_entities.json for production entity enrichment
# No runtime filtering - all entities are pre-approved and optimized
# See clean_entities.json for the complete list of 255 approved entities
"""
    
    # Find and replace the old stoplist comment
    old_comment_pattern = r"# ============================================================================\n# V1\.6\.5\.1 ENTITY STOPLIST INTEGRATION\n# ============================================================================\n# Using cleaned entities with stoplist filtering to remove generic terms\n# Stoplist filters out domain/field-similar terms for more specific enrichment\n# See entity_stoplist\.json for the complete list of filtered terms"
    
    if re.search(old_comment_pattern, content):
        content = re.sub(old_comment_pattern, new_comment.strip(), content)
        print("✅ Updated stoplist comment to static entities")
    else:
        print("⚠️ Old stoplist comment not found, adding new comment")
        # Find the feature flags section and add the comment
        feature_flags_marker = "# ============================================================================\n# V1.6.5.1 FEATURE FLAGS - DOMAIN-DRIVEN LOGIC HIERARCHY\n# ============================================================================"
        
        if feature_flags_marker in content:
            content = content.replace(feature_flags_marker, new_comment + feature_flags_marker)
        else:
            content = new_comment + content
    
    # Write the updated content
    with open("query_engine.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Successfully updated comment")
    return True

def main():
    """Main function to update query engine"""
    print("🔄 Updating Query Engine for Static Clean Entities")
    print("=" * 50)
    
    # Update imports
    if update_query_engine_imports():
        print("✅ Import update successful")
    else:
        print("❌ Import update failed")
        return
    
    # Update comment
    if update_stoplist_comment():
        print("✅ Comment update successful")
    else:
        print("❌ Comment update failed")
        return
    
    print("\n📋 Update Summary")
    print("=" * 50)
    print("✅ Updated query_engine.py to use clean_entities_static")
    print("✅ Updated comments to reflect static entity usage")
    print("✅ Entity enrichment now uses pre-approved static entities")
    print("📁 Static entities: clean_entities.json")
    print("📊 Total entities: 255 pre-approved entities")
    print("✅ No runtime filtering - improved performance")

if __name__ == "__main__":
    main() 