#!/usr/bin/env python3
"""
Simple test script to verify course configuration
"""
import json
import os

def test_decision_course_config():
    """Test the decision course configuration"""
    print("🔍 TESTING DECISION COURSE CONFIGURATION")
    print("=" * 50)
    
    config_path = "courses/decision/course_config.json"
    
    if not os.path.exists(config_path):
        print(f"❌ Course config not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✅ Course config loaded successfully")
        print(f"   Course ID: {config['course_id']}")
        print(f"   Name: {config['name']}")
        print(f"   Version: {config['version']}")
        print(f"   Domains: {list(config['domains'].keys())}")
        print(f"   Application Fields: {len(config['application_fields'])}")
        print(f"   Entity Types: {len(config['entity_types'])}")
        
        # Test domain detection
        test_query = "my team members are reluctant to give up his legacy projects"
        query_lower = test_query.lower()
        
        print(f"\n🔍 TESTING DOMAIN DETECTION")
        print(f"   Query: {test_query}")
        
        for domain_name, domain_config in config['domains'].items():
            score = 0
            for keyword in domain_config['keywords']:
                if keyword in query_lower:
                    score += 1
            print(f"   {domain_name}: {score} matches")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing course config: {e}")
        return False

if __name__ == "__main__":
    test_decision_course_config() 