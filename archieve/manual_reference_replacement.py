import json

def manual_reference_replacement():
    """Manually replace the domain_references section in detect_domain_semantic function"""
    
    # Read the updated reference queries
    with open('reference_queries_updated.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Organize queries by domain
    domain_mapping = {'S': 'strategic', 'T': 'technical', 'H': 'behavioral', 'N': 'negotiation'}
    new_domain_references = {}
    
    for item in data:
        query = item['query']
        domains = item['domains']
        for domain_code in domains:
            domain_name = domain_mapping.get(domain_code)
            if domain_name:
                if domain_name not in new_domain_references:
                    new_domain_references[domain_name] = []
                new_domain_references[domain_name].append(query)
    
    # Create the new content
    new_content = """        # 79 updated domain-specific reference queries (hardcoded for performance)
        domain_references = {
"""
    
    for domain_name, queries in new_domain_references.items():
        new_content += f"            '{domain_name}': [\n"
        for query in queries:
            new_content += f'                "{query}",\n'
        new_content += "            ],\n"
    
    new_content += "        }\n"
    
    # Read the file
    with open('Repeatability/query_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the domain_references section
    old_pattern = """        # Domain reference texts (representative examples for each domain)
        domain_references = {
            'behavioral': [
                "human judgment and cognitive biases in professional settings",
                "psychological factors affecting workplace behavior",
                "intuitive judgment versus analytical thinking",
                "cognitive psychology and human reasoning",
                "emotional intelligence and interpersonal dynamics",
                "psychological activities and mental frameworks",
                "human cognition and behavioral patterns",
                "intuitive decision patterns and cognitive shortcuts"
            ],
            'technical': [
                "optimizing production capacity using mathematical models",
                "forecasting demand with statistical analysis",
                "simulation modeling for risk assessment",
                "linear programming for resource allocation",
                "data analysis and statistical modeling",
                "mathematical optimization and algorithms"
            ],
            'strategic': [
                "developing long-term business strategy",
                "competitive positioning and market analysis",
                "strategic planning and corporate decisions",
                "business expansion and growth strategy",
                "competitive advantage and market positioning",
                "strategic decision making for organizations"
            ],
            'negotiation': [
                "negotiating deals and agreements",
                "bargaining strategies and tactics",
                "contract negotiations and settlements",
                "negotiation techniques and approaches",
                "deal-making and agreement methods",
                "negotiation frameworks and approaches",
                "negotiating salary packages and compensation",
                "bargaining for better terms and conditions"
            ],
            'general': [
                "what tools can help me make better decisions",
                "general decision making tools and frameworks",
                "basic decision making approaches and methods",
                "decision making tools and techniques",
                "how to make better decisions",
                "decision making frameworks and processes"
            ]
        }"""
    
    if old_pattern in content:
        new_content_full = content.replace(old_pattern, new_content)
        
        with open('Repeatability/query_engine.py', 'w', encoding='utf-8') as f:
            f.write(new_content_full)
        
        print("✅ Successfully replaced domain_references section")
        print(f"📊 Domain distribution:")
        for domain, queries in new_domain_references.items():
            print(f"  {domain}: {len(queries)} queries")
    else:
        print("❌ Could not find the old domain_references section")

if __name__ == "__main__":
    manual_reference_replacement()
