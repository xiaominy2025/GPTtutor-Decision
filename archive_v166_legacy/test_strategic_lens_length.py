#!/usr/bin/env python3
"""
Test script to validate Strategic Thinking Lens length requirements for V1.6.5
"""

import re
import query_engine

def test_strategic_lens_length():
    """Test that Strategic Thinking Lens sections meet length requirements"""
    
    # Test queries that should trigger different domains
    test_queries = [
        "How do I choose between two job offers?",
        "Should I start a business or take a corporate job?",
        "How do I negotiate a better salary?",
        "What should I consider when choosing a college?",
        "How do I optimize my supply chain under uncertainty?"
    ]
    
    print("🧪 Testing Strategic Thinking Lens Length Requirements (V1.6.5)")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        
        try:
            # Process the query
            answer = query_engine.process_query(query)
            
            # Extract Strategic Thinking Lens section
            lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', answer, re.DOTALL | re.IGNORECASE)
            
            if lens_match:
                lens_content = lens_match.group(1).strip()
                word_count = len(lens_content.split())
                
                print(f"   📊 Word count: {word_count}")
                print(f"   ✅ Target range: 120-160 words")
                
                if 120 <= word_count <= 160:
                    print(f"   ✅ PASS: Length within target range")
                elif word_count < 100:
                    print(f"   ❌ FAIL: Too short (< 100 words)")
                elif word_count < 120:
                    print(f"   ⚠️  WARNING: Below minimum (120 words)")
                elif word_count > 160:
                    print(f"   ⚠️  WARNING: Above maximum (160 words)")
                
                # Check for domain coverage (should have tradeoffs and multiple domains)
                has_tradeoffs = any(word in lens_content.lower() for word in ['trade', 'balance', 'weigh', 'versus', 'against'])
                has_multiple_domains = len(re.findall(r'\b(strategic|analytical|behavioral|technical|negotiation|operations|startup|admission|job)\b', lens_content.lower())) >= 2
                
                print(f"   🔍 Tradeoffs mentioned: {'✅' if has_tradeoffs else '❌'}")
                print(f"   🔍 Multiple domains: {'✅' if has_multiple_domains else '❌'}")
                
            else:
                print(f"   ❌ FAIL: No Strategic Thinking Lens section found")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Strategic Thinking Lens Length Test Complete")

def test_fallback_enhancement():
    """Test the enhance_strategic_lens_fallback function"""
    
    print("\n🧪 Testing Fallback Enhancement Function")
    print("=" * 60)
    
    test_cases = [
        ("How do I choose a college?", "admission"),
        ("Should I take this job offer?", "job"),
        ("How do I start my own business?", "startup"),
        ("How do I negotiate a better deal?", "negotiation"),
        ("How do I optimize my operations?", "operations"),
        ("What should I do about this decision?", "general")
    ]
    
    for query, expected_domain in test_cases:
        print(f"\n📝 Testing: {query}")
        
        # Get base fallback
        fallbacks = query_engine.context_aware_fallbacks(query)
        base_lens = fallbacks.get('Strategic Thinking Lens', '')
        base_word_count = len(base_lens.split())
        
        print(f"   📊 Base fallback: {base_word_count} words")
        
        # Test enhancement
        enhanced_lens = query_engine.enhance_strategic_lens_fallback(query, base_lens)
        enhanced_word_count = len(enhanced_lens.split())
        
        print(f"   📊 Enhanced fallback: {enhanced_word_count} words")
        
        if 120 <= enhanced_word_count <= 160:
            print(f"   ✅ PASS: Enhanced length within target range")
        else:
            print(f"   ❌ FAIL: Enhanced length outside target range")
        
        # Check domain detection
        detected_domain = query_engine.extract_application_field(query)
        print(f"   🔍 Expected domain: {expected_domain}")
        print(f"   🔍 Detected domain: {detected_domain}")
        
        if detected_domain == expected_domain:
            print(f"   ✅ PASS: Domain detection correct")
        else:
            print(f"   ⚠️  WARNING: Domain detection mismatch")

if __name__ == "__main__":
    test_strategic_lens_length()
    test_fallback_enhancement() 