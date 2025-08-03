#!/usr/bin/env python3
"""
Check metadata.json content
"""
import json

def check_metadata():
    """Check metadata.json content"""
    try:
        with open("metadata.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("📊 METADATA.JSON ANALYSIS")
        print("=" * 50)
        print(f"Documents: {len(data['documents'])}")
        print(f"File names: {len(data['file_names'])}")
        print(f"Concept names: {len(data.get('concept_names', []))}")
        
        if 'concept_names' in data:
            print(f"\nFirst 5 concept names:")
            for i, name in enumerate(data['concept_names'][:5]):
                print(f"  {i}: {name}")
        else:
            print("\n❌ No concept_names field found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking metadata: {e}")
        return False

if __name__ == "__main__":
    check_metadata() 