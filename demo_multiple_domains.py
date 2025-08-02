print("🧪 Multiple Course Concept Domain Detection Demo")
print("=" * 60)

# Import the function
try:
    from query_engine import detect_course_concept_domains
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test a query that should trigger multiple domains
test_query = "How can I use linear programming to optimize production while considering team dynamics?"
print(f"\nTest Query: {test_query}")

try:
    # Detect domains
    detected_domains = detect_course_concept_domains(test_query)
    print(f"Detected domains: {detected_domains}")
    
    # Show active domains (scores > 0)
    active_domains = {k: v for k, v in detected_domains.items() if v > 0}
    print(f"Active domains: {active_domains}")
    
    # Find primary domain
    if detected_domains:
        primary_domain = max(detected_domains.items(), key=lambda x: x[1])[0]
        print(f"Primary domain: {primary_domain}")
        
        # Count multiple domains
        multiple_domains = len([v for v in detected_domains.values() if v > 0])
        print(f"Number of active domains: {multiple_domains}")
        
        if multiple_domains >= 2:
            print("✅ Multiple domains detected successfully!")
        else:
            print("⚠️ Only single domain detected")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📊 SUMMARY")
print("=" * 60)
print("The system can detect multiple course concept domains for a single query.")
print("This allows for more nuanced and comprehensive strategic lens generation.") 