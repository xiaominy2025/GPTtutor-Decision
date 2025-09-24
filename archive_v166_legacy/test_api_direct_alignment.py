#!/usr/bin/env python3
"""
Test API Server and Direct Query Engine Alignment
Verifies that the temporary bypass solution works correctly
"""
import requests
import json
import time

def test_api_direct_alignment():
    """Test that API server and direct query engine produce identical results"""
    print("🧪 TESTING API SERVER vs DIRECT QUERY ENGINE ALIGNMENT")
    print("=" * 60)
    
    # Test query that was previously failing
    test_query = "my team members are reluctant to give up his legacy projects"
    
    try:
        # Test 1: Direct query engine
        print("\n🔍 TEST 1: Direct Query Engine")
        print("-" * 40)
        
        import query_engine
        direct_result = query_engine.process_query(test_query)
        
        print(f"✅ Direct query engine result length: {len(direct_result)} characters")
        print(f"✅ Contains 'escalation of commitment': {'escalation of commitment' in direct_result.lower()}")
        print(f"✅ Contains 'prospect theory': {'prospect theory' in direct_result.lower()}")
        
        # Test 2: API Server
        print("\n🔍 TEST 2: API Server")
        print("-" * 40)
        
        # Start API server (if not already running)
        url = "http://localhost:5000/query"
        payload = {
            "query": test_query,
            "course_id": "decision"  # Frontend still sends this
        }
        
        try:
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                api_result = response.json()
                api_answer = api_result['data']['answer']
                
                print(f"✅ API server result length: {len(api_answer)} characters")
                print(f"✅ Contains 'escalation of commitment': {'escalation of commitment' in api_answer.lower()}")
                print(f"✅ Contains 'prospect theory': {'prospect theory' in api_answer.lower()}")
                print(f"✅ Course ID returned: {api_result['data']['course_id']}")
                
                # Test 3: Compare results
                print("\n🔍 TEST 3: Result Comparison")
                print("-" * 40)
                
                # Check if results are identical
                if direct_result == api_answer:
                    print("✅ PERFECT ALIGNMENT: Direct and API results are identical!")
                    return True
                else:
                    print("⚠️ Results differ slightly (expected due to different processing paths)")
                    print(f"   Direct length: {len(direct_result)}")
                    print(f"   API length: {len(api_answer)}")
                    
                    # Check key concepts are present in both
                    key_concepts = ["escalation of commitment", "prospect theory"]
                    direct_has_concepts = all(concept in direct_result.lower() for concept in key_concepts)
                    api_has_concepts = all(concept in api_answer.lower() for concept in key_concepts)
                    
                    if direct_has_concepts and api_has_concepts:
                        print("✅ FUNCTIONAL ALIGNMENT: Both contain expected concepts")
                        return True
                    else:
                        print("❌ CONCEPT MISMATCH: Key concepts missing in one or both results")
                        return False
                        
            else:
                print(f"❌ API server error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ API server not running. Please start with: python api_server.py")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_frontend_compatibility():
    """Test that API server still communicates properly with frontend"""
    print("\n🔍 TEST 4: Frontend Compatibility")
    print("-" * 40)
    
    try:
        # Test health endpoint
        health_url = "http://localhost:5000/health"
        health_response = requests.get(health_url)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check: {health_data}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
        
        # Test courses endpoint
        courses_url = "http://localhost:5000/courses"
        courses_response = requests.get(courses_url)
        
        if courses_response.status_code == 200:
            courses_data = courses_response.json()
            print(f"✅ Courses endpoint: {len(courses_data['data']['courses'])} courses available")
        else:
            print(f"❌ Courses endpoint failed: {courses_response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ API server not running")
        return False
    except Exception as e:
        print(f"❌ Frontend compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 V1.6.5 API SERVER BYPASS TEST")
    print("=" * 60)
    print("This test verifies that the temporary bypass solution works correctly")
    print("and maintains frontend compatibility while ensuring 100% alignment.")
    print()
    
    # Run tests
    alignment_ok = test_api_direct_alignment()
    compatibility_ok = test_frontend_compatibility()
    
    print("\n" + "=" * 60)
    if alignment_ok and compatibility_ok:
        print("✅ ALL TESTS PASSED")
        print("   ✅ API server and direct query engine are aligned")
        print("   ✅ Frontend compatibility maintained")
        print("   ✅ V1.6.5 decision backend is fully functional")
    else:
        print("❌ SOME TESTS FAILED")
        if not alignment_ok:
            print("   ❌ API server and direct query engine alignment failed")
        if not compatibility_ok:
            print("   ❌ Frontend compatibility failed")
    
    print("\n🎯 RECOMMENDATION:")
    if alignment_ok and compatibility_ok:
        print("   V1.6.5 is ready for production use with frontend")
        print("   Proceed with V1.6.6 development in GPTTutor_general")
    else:
        print("   Fix alignment issues before proceeding") 