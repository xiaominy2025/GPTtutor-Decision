#!/usr/bin/env python3
"""
Focused quality test for ThinkPal V1.6.3 answers
Tests the specific query mentioned in the requirements
"""

import sys
from test_suite import analyze_thinkpal_answer

def test_answer_quality_v163():
    """Test the quality of ThinkPal V1.6.3 answers"""
    print("🧪 ThinkPal V1.6.3 Answer Quality Test")
    print("=" * 50)
    
    # The specific test query from requirements
    test_query = "Should the company outsource its software development to reduce costs?"
    
    print(f"📝 Test Query: {test_query}")
    print("-" * 50)
    
    try:
        # Import and use query engine directly
        import query_engine
        
        print("🔄 Generating ThinkPal response...")
        response = query_engine.process_query(test_query)
        
        print("📊 Analyzing response quality...")
        warnings = analyze_thinkpal_answer(response)
        
        print("\n=== RESPONSE ===")
        print(response)
        print("\n=== ANALYSIS ===")
        for w in warnings:
            print(w)
        
        # Fail test on critical issues
        critical_issues = [w for w in warnings if "❌" in w]
        warning_issues = [w for w in warnings if "⚠️" in w]
        
        if critical_issues:
            print(f"\n❌ TEST FAILED: {len(critical_issues)} critical issues detected")
            assert False, "❌ Critical structure issue detected."
        
        if warning_issues:
            print(f"\n⚠️ TEST FAILED: {len(warning_issues)} formatting issues detected")
            assert False, "⚠️ Strategic Thinking section formatting issue."
        
        print("\n✅ TEST PASSED: Response meets V1.6.3 quality standards")
        return True
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_queries():
    """
    Test multiple queries to ensure consistent quality
    """
    print("\n🧪 Multiple Query Quality Test")
    print("=" * 50)
    
    test_queries = [
        "Should the company outsource its software development to reduce costs?",
        "Is it better to hire full-time employees or contractors for this project?",
        "Should we invest in automation tools or keep manual processes?",
        "Is it worth expanding to international markets right now?"
    ]
    
    all_passed = True
    total_warnings = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query[:60]}...")
        
        try:
            import query_engine
            response = query_engine.process_query(query)
            warnings = analyze_thinkpal_answer(response)
            
            # Check for critical and warning issues
            critical_issues = [w for w in warnings if "❌" in w]
            warning_issues = [w for w in warnings if "⚠️" in w]
            
            if critical_issues or warning_issues:
                print(f"❌ {len(critical_issues)} critical, {len(warning_issues)} warning issues:")
                for warning in warnings:
                    print(f"   {warning}")
                all_passed = False
                total_warnings += len(warnings)
            else:
                print("✅ No quality issues")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            all_passed = False
    
    print(f"\n📊 Multiple Query Summary:")
    print(f"   Queries tested: {len(test_queries)}")
    print(f"   Total warnings: {total_warnings}")
    print(f"   Overall result: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    
    return all_passed

def main():
    """Run the quality tests"""
    print("🚀 ThinkPal V1.6.3 Quality Validation Suite")
    print("=" * 60)
    
    # Test 1: V1.6.3 specific quality test
    test1_passed = test_answer_quality_v163()
    
    # Test 2: Multiple queries for consistency
    test2_passed = test_multiple_queries()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL QUALITY TEST SUMMARY")
    print("=" * 60)
    
    print(f"V1.6.3 Quality Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Multiple Query Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    overall_passed = test1_passed and test2_passed
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_passed else '❌ SOME TESTS FAILED'}")
    
    if overall_passed:
        print("🎉 ThinkPal V1.6.3 quality validation successful!")
    else:
        print("⚠️ Quality issues detected. Please review and fix the problems above.")
    
    return overall_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 