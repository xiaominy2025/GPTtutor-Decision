#!/usr/bin/env python3
"""
Recreate metadata.json to match current glossary
"""
import json
import os

def recreate_metadata():
    """Recreate metadata.json to match current glossary"""
    print("🔧 RECREATING METADATA.JSON")
    print("=" * 50)
    
    try:
        # Load current glossary
        with open("courses/decision/glossary.json", 'r', encoding='utf-8') as f:
            glossary = json.load(f)
        
        print(f"✅ Current glossary has {len(glossary)} concepts")
        
        # Create concept texts
        concept_texts = []
        concept_names = []
        
        for name, concept_data in glossary.items():
            if isinstance(concept_data, dict):
                definition = concept_data["definition"]
            else:
                definition = concept_data
            
            concept_text = f"{definition} {name.replace('-', ' ')}"
            concept_texts.append(concept_text)
            concept_names.append(name)
        
        # Create new metadata
        metadata = {
            "documents": concept_texts,
            "file_names": [f"concept_{i}" for i in range(len(concept_texts))],
            "concept_names": concept_names
        }
        
        # Create backup
        if os.path.exists("metadata.json"):
            os.rename("metadata.json", "metadata_backup.json")
            print("✅ Created backup: metadata_backup.json")
        
        # Save new metadata
        with open("metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ New metadata created with {len(concept_texts)} concepts")
        print(f"   Documents: {len(metadata['documents'])}")
        print(f"   File names: {len(metadata['file_names'])}")
        print(f"   Concept names: {len(metadata['concept_names'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreating metadata: {e}")
        return False

if __name__ == "__main__":
    if recreate_metadata():
        print("\n✅ Metadata recreated successfully")
        print("   V1.6.5 alignment verification can now proceed")
    else:
        print("\n❌ Failed to recreate metadata") 