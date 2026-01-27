#!/usr/bin/env python3
"""
V1.6.5 Alignment Verification Script
Ensures all components are fully aligned before V1.6.6 development
"""
import json
import os
import sys
from typing import Dict, Any

def verify_glossary_alignment():
    """Verify glossary alignment between query_engine.py and course files"""
    print("🔍 VERIFYING GLOSSARY ALIGNMENT")
    print("=" * 50)
    
    try:
        # Load course glossary
        with open("courses/decision/glossary.json", 'r', encoding='utf-8') as f:
            course_glossary = json.load(f)
        
        print(f"✅ Course glossary loaded: {len(course_glossary)} concepts")
        
        # Check for key concepts that were missing before
        key_concepts = ["escalation of commitment", "prospect theory", "confirmation bias"]
        missing_concepts = []
        
        for concept in key_concepts:
            if concept not in course_glossary:
                missing_concepts.append(concept)
        
        if missing_concepts:
            print(f"❌ Missing concepts: {missing_concepts}")
            return False
        else:
            print("✅ All key concepts present in course glossary")
            return True
            
    except Exception as e:
        print(f"❌ Glossary alignment error: {e}")
        return False

def verify_course_config():
    """Verify course configuration is complete"""
    print("\n🔍 VERIFYING COURSE CONFIGURATION")
    print("=" * 50)
    
    try:
        with open("courses/decision/course_config.json", 'r', encoding='utf-8') as f:
            course_config = json.load(f)
        
        required_fields = ["course_id", "name", "version", "domains", "application_fields", "entity_types"]
        missing_fields = []
        
        for field in required_fields:
            if field not in course_config:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields in course config: {missing_fields}")
            return False
        
        print(f"✅ Course config complete:")
        print(f"   Course ID: {course_config['course_id']}")
        print(f"   Name: {course_config['name']}")
        print(f"   Version: {course_config['version']}")
        print(f"   Domains: {list(course_config['domains'].keys())}")
        print(f"   Application Fields: {len(course_config['application_fields'])}")
        print(f"   Entity Types: {len(course_config['entity_types'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Course config error: {e}")
        return False

def verify_api_server_alignment():
    """Verify API server can load course configuration correctly"""
    print("\n🔍 VERIFYING API SERVER ALIGNMENT")
    print("=" * 50)
    
    try:
        # Import and test API server course loading
        import api_server
        
        # Test course config loading
        test_course_id = "decision"
        config = api_server.load_course_config(test_course_id)
        
        if config and config.get('course_id') == test_course_id:
            print("✅ API server course config loading works")
            print(f"   Loaded course: {config['course_id']}")
            print(f"   Glossary concepts: {len(config.get('glossary', {}))}")
            return True
        else:
            print("❌ API server course config loading failed")
            return False
            
    except Exception as e:
        print(f"❌ API server alignment error: {e}")
        return False

def test_query_consistency():
    """Test that same query produces consistent results"""
    print("\n🔍 TESTING QUERY CONSISTENCY")
    print("=" * 50)
    
    test_query = "my team members are reluctant to give up his legacy projects"
    
    try:
        # Test direct query engine
        import query_engine
        direct_result = query_engine.process_query(test_query)
        
        # Test API server (simulated)
        import api_server
        api_config = api_server.load_course_config("decision")
        api_result = query_engine.process_query(test_query, course_config=api_config)
        
        # Check if results are similar (should be identical with aligned glossary)
        if "escalation of commitment" in direct_result.lower() and "escalation of commitment" in api_result.lower():
            print("✅ Query consistency verified")
            print("   Both direct and API results contain expected concepts")
            return True
        else:
            print("❌ Query consistency failed")
            print("   Direct and API results differ")
            return False
            
    except Exception as e:
        print(f"❌ Query consistency error: {e}")
        return False

def verify_v165_alignment():
    """Main verification function"""
    print("🚀 V1.6.5 ALIGNMENT VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Glossary Alignment", verify_glossary_alignment),
        ("Course Configuration", verify_course_config),
        ("API Server Alignment", verify_api_server_alignment),
        ("Query Consistency", test_query_consistency)
    ]
    
    all_passed = True
    
    for check_name, check_function in checks:
        try:
            result = check_function()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ V1.6.5 ALIGNMENT VERIFICATION PASSED")
        print("   All components are aligned and ready for V1.6.6 development")
        return True
    else:
        print("❌ V1.6.5 ALIGNMENT VERIFICATION FAILED")
        print("   Please fix alignment issues before proceeding")
        return False

def disable_multi_course_functionality():
    """Temporarily disable multi-course functionality for V1.6.5 stability"""
    print("\n🔧 DISABLING MULTI-COURSE FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Read current api_server.py
        with open("api_server.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already disabled
        if "course_id = \"decision\"" in content:
            print("✅ Multi-course functionality already disabled")
            return True
        
        # Create backup
        with open("api_server_v165_backup.py", 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Created backup: api_server_v165_backup.py")
        
        # Modify load_course_config function
        # This is a simplified version - in practice, you'd want to be more careful
        modified_content = content.replace(
            "def load_course_config(course_id: str) -> dict:",
            "def load_course_config(course_id: str) -> dict:\n    # TEMPORARY: Force decision course for V1.6.5 stability\n    course_id = \"decision\""
        )
        
        with open("api_server.py", 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("✅ Multi-course functionality disabled")
        print("   All requests will use decision course")
        return True
        
    except Exception as e:
        print(f"❌ Error disabling multi-course functionality: {e}")
        return False

if __name__ == "__main__":
    # Run alignment verification
    alignment_ok = verify_v165_alignment()
    
    if alignment_ok:
        print("\n🎯 V1.6.5 is ready for V1.6.6 development")
        print("   Proceed with creating GPTTutor_general")
    else:
        print("\n⚠️ V1.6.5 alignment issues found")
        print("   Please fix issues before proceeding")
        sys.exit(1) 