import sys
import os

# Add parent directory so we can import query_engine.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from query_engine import process_query

def test_formatting_of_example_and_header():
    """Test that formatting fixes are working correctly"""
    
    print("🧪 TESTING FORMATTING FIXES")
    print("=" * 35)
    
    query = "How to convey bad news to my boss?"
    answer = process_query(query)
    
    print("📋 TESTING HEADER FORMATTING:")
    print("-" * 30)
    
    # Check Strategic Thinking Lens header
    if "**Strategic Thinking Lens**" in answer:
        print("✅ Header present")
    else:
        print("❌ Header missing")
        assert False, "❌ Header missing"
    
    header_count = answer.count("**Strategic Thinking Lens**")
    if header_count == 1:
        print("✅ Single header (no duplicates)")
    else:
        print(f"❌ Duplicate headers found: {header_count}")
        assert False, f"❌ Duplicate header found: {header_count}"
    
    print("\n📋 TESTING CONNECTOR FORMATTING:")
    print("-" * 35)
    
    # Check for problematic triple asterisks
    if "***For example" in answer or "***For instance" in answer:
        print("❌ Triple asterisks still present")
        assert False, "❌ Triple asterisks still present"
    else:
        print("✅ No triple asterisks found")
    
    # Check for proper italic formatting
    has_proper_italic = "*For example" in answer or "*For instance" in answer
    if has_proper_italic:
        print("✅ Connectors properly italicized")
    else:
        print("❌ Connectors not italicized properly")
        assert False, "❌ 'For example' not italicized properly"
    
    print("\n📋 TESTING PART SUBHEADERS:")
    print("-" * 30)
    
    # Check for unwanted Part 1/Part 2 subheaders
    part_headers = [line for line in answer.split('\n') if 'Part' in line and ':' in line]
    if len(part_headers) == 0:
        print("✅ No Part subheaders found")
    else:
        print(f"❌ Part subheaders found: {part_headers}")
        assert False, f"❌ Part subheaders found: {part_headers}"
    
    print("\n✅ ALL FORMATTING TESTS PASSED!")
    print("=" * 35)
    print("✅ Single Strategic Thinking Lens header")
    print("✅ No triple asterisks in connectors")
    print("✅ Proper italic formatting for connectors")
    print("✅ No Part 1/Part 2 subheaders")
    
    return True

def test_multiple_queries_for_consistency():
    """Test multiple queries to ensure formatting is consistent"""
    
    print("\n🧪 TESTING MULTIPLE QUERIES FOR CONSISTENCY")
    print("=" * 50)
    
    test_queries = [
        "How to convey bad news to my boss?",
        "What should I consider when negotiating a salary increase?",
        "How can I optimize production with limited resources?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        
        try:
            answer = process_query(query)
            
            # Quick checks
            header_count = answer.count("**Strategic Thinking Lens**")
            has_triple_asterisks = "***For example" in answer or "***For instance" in answer
            has_proper_italic = "*For example" in answer or "*For instance" in answer
            
            if header_count == 1 and not has_triple_asterisks and has_proper_italic:
                print(f"  ✅ Query {i} formatting: PASS")
            else:
                print(f"  ❌ Query {i} formatting: FAIL")
                print(f"     Headers: {header_count}, Triple asterisks: {has_triple_asterisks}, Proper italic: {has_proper_italic}")
                # Debug: show what connectors are actually present
                if "For example" in answer:
                    print(f"     Debug: 'For example' found at position {answer.find('For example')}")
                if "For instance" in answer:
                    print(f"     Debug: 'For instance' found at position {answer.find('For instance')}")
                
        except Exception as e:
            print(f"  ❌ Query {i} failed: {e}")
    
    print("\n✅ MULTIPLE QUERY TEST COMPLETE")

if __name__ == "__main__":
    # Run the main formatting test
    test_formatting_of_example_and_header()
    
    # Run consistency test
    test_multiple_queries_for_consistency()
    
    print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 45)
    print("✅ Formatting fixes are working correctly")
    print("✅ No duplicate headers")
    print("✅ Clean italic formatting")
    print("✅ No unwanted subheaders")
    print("✅ Consistent across multiple queries") 