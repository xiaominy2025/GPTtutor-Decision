#!/usr/bin/env python3
"""
Comprehensive Quality Testing Framework
Systematic evaluation across domains, fields, entities, and keywords
"""

import os
import sys
import json
import time
import traceback
import re
from typing import Dict, List, Any
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def log_message(message: str, level: str = "INFO"):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def generate_comprehensive_test_queries() -> List[Dict]:
    """Generate comprehensive test queries across all domains and scenarios"""
    
    test_queries = []
    
    # ============================================================================
    # DOMAIN 1: CAREER & PERSONAL DECISIONS
    # ============================================================================
    career_queries = [
        {
            "query": "I need to decide between two job offers with different salaries",
            "domain": "career",
            "entities": ["job offers", "salary", "career decision"],
            "keywords": ["job", "offer", "salary", "career", "decision"],
            "expected_concepts": ["decision tree", "weighted scoring", "career planning"]
        },
        {
            "query": "Should I accept a promotion that requires relocation?",
            "domain": "career",
            "entities": ["promotion", "relocation", "career advancement"],
            "keywords": ["promotion", "relocation", "career", "advancement"],
            "expected_concepts": ["decision tree", "risk assessment", "stakeholder alignment"]
        },
        {
            "query": "How do I choose between staying at my current company or joining a startup?",
            "domain": "career",
            "entities": ["current company", "startup", "career choice"],
            "keywords": ["company", "startup", "career", "choice"],
            "expected_concepts": ["swot analysis", "risk assessment", "career planning"]
        },
        {
            "query": "What factors should I consider when negotiating my salary?",
            "domain": "career",
            "entities": ["salary negotiation", "compensation", "bargaining"],
            "keywords": ["salary", "negotiation", "compensation", "bargaining"],
            "expected_concepts": ["batna", "zopa", "negotiation strategy"]
        }
    ]
    test_queries.extend(career_queries)
    
    # ============================================================================
    # DOMAIN 2: BUSINESS STRATEGY & COMPETITIVE ANALYSIS
    # ============================================================================
    strategy_queries = [
        {
            "query": "How should our company position itself against new competitors?",
            "domain": "strategy",
            "entities": ["company", "competitors", "market positioning"],
            "keywords": ["company", "competitors", "positioning", "strategy"],
            "expected_concepts": ["porter's five forces", "competitive analysis", "strategic positioning"]
        },
        {
            "query": "Should we expand into international markets?",
            "domain": "strategy",
            "entities": ["international expansion", "global markets", "business growth"],
            "keywords": ["expand", "international", "markets", "growth"],
            "expected_concepts": ["swot analysis", "risk assessment", "market analysis"]
        },
        {
            "query": "How do we evaluate different pricing strategies for our new product?",
            "domain": "strategy",
            "entities": ["pricing strategies", "new product", "market analysis"],
            "keywords": ["pricing", "strategies", "product", "market"],
            "expected_concepts": ["competitive analysis", "market analysis", "profitability analysis"]
        },
        {
            "query": "What are the risks and opportunities of entering a new market segment?",
            "domain": "strategy",
            "entities": ["market segment", "risks", "opportunities"],
            "keywords": ["market", "segment", "risks", "opportunities"],
            "expected_concepts": ["risk assessment", "swot analysis", "market analysis"]
        }
    ]
    test_queries.extend(strategy_queries)
    
    # ============================================================================
    # DOMAIN 3: OPERATIONS & SUPPLY CHAIN
    # ============================================================================
    operations_queries = [
        {
            "query": "How do I optimize our supply chain to reduce costs?",
            "domain": "operations",
            "entities": ["supply chain", "cost reduction", "optimization"],
            "keywords": ["supply chain", "costs", "optimize", "reduce"],
            "expected_concepts": ["linear optimization", "supply chain risk management", "cost analysis"]
        },
        {
            "query": "What's the best way to allocate resources across multiple projects?",
            "domain": "operations",
            "entities": ["resource allocation", "multiple projects", "optimization"],
            "keywords": ["resources", "allocation", "projects", "optimize"],
            "expected_concepts": ["linear optimization", "resource planning", "project management"]
        },
        {
            "query": "How can we improve our production capacity planning?",
            "domain": "operations",
            "entities": ["production capacity", "planning", "manufacturing"],
            "keywords": ["production", "capacity", "planning", "manufacturing"],
            "expected_concepts": ["aggregate planning", "capacity planning", "optimization"]
        },
        {
            "query": "What forecasting method should we use for seasonal demand?",
            "domain": "operations",
            "entities": ["forecasting", "seasonal demand", "demand planning"],
            "keywords": ["forecasting", "seasonal", "demand", "planning"],
            "expected_concepts": ["seasonal analysis", "moving average", "forecasting"]
        }
    ]
    test_queries.extend(operations_queries)
    
    # ============================================================================
    # DOMAIN 4: FINANCIAL & INVESTMENT DECISIONS
    # ============================================================================
    financial_queries = [
        {
            "query": "What are the risks of investing in emerging market stocks?",
            "domain": "financial",
            "entities": ["emerging markets", "stocks", "investment risks"],
            "keywords": ["investing", "emerging markets", "stocks", "risks"],
            "expected_concepts": ["risk assessment", "portfolio management", "investment analysis"]
        },
        {
            "query": "How should I evaluate different retirement investment options?",
            "domain": "financial",
            "entities": ["retirement investments", "investment options", "long-term planning"],
            "keywords": ["retirement", "investments", "options", "long-term"],
            "expected_concepts": ["decision tree", "risk tolerance assessment", "portfolio management"]
        },
        {
            "query": "What's the best way to assess the value of a potential acquisition?",
            "domain": "financial",
            "entities": ["acquisition", "valuation", "mergers and acquisitions"],
            "keywords": ["acquisition", "value", "assess", "mergers"],
            "expected_concepts": ["value chain analysis", "profitability analysis", "risk assessment"]
        },
        {
            "query": "How do I model the uncertainty in my investment portfolio?",
            "domain": "financial",
            "entities": ["investment portfolio", "uncertainty", "risk modeling"],
            "keywords": ["portfolio", "uncertainty", "model", "risk"],
            "expected_concepts": ["monte carlo simulation", "risk assessment", "portfolio management"]
        }
    ]
    test_queries.extend(financial_queries)
    
    # ============================================================================
    # DOMAIN 5: NEGOTIATION & CONFLICT RESOLUTION
    # ============================================================================
    negotiation_queries = [
        {
            "query": "How do I negotiate better terms with a dominant supplier?",
            "domain": "negotiation",
            "entities": ["supplier negotiation", "dominant supplier", "bargaining"],
            "keywords": ["negotiate", "supplier", "dominant", "terms"],
            "expected_concepts": ["batna", "zopa", "negotiation strategy"]
        },
        {
            "query": "What's my best alternative if this business deal falls through?",
            "domain": "negotiation",
            "entities": ["business deal", "alternative options", "fallback plan"],
            "keywords": ["deal", "alternative", "falls through", "business"],
            "expected_concepts": ["batna", "risk assessment"]
        },
        {
            "query": "How can I create value in a zero-sum negotiation?",
            "domain": "negotiation",
            "entities": ["value creation", "zero-sum negotiation", "win-win"],
            "keywords": ["value", "zero-sum", "negotiation", "win-win"],
            "expected_concepts": ["value creation", "integrative negotiation", "negotiation strategy"]
        },
        {
            "query": "What's my reservation point in this salary negotiation?",
            "domain": "negotiation",
            "entities": ["salary negotiation", "reservation point", "walk-away"],
            "keywords": ["salary", "negotiation", "reservation", "walk-away"],
            "expected_concepts": ["reservation point", "batna", "negotiation strategy"]
        }
    ]
    test_queries.extend(negotiation_queries)
    
    # ============================================================================
    # DOMAIN 6: RISK MANAGEMENT & UNCERTAINTY
    # ============================================================================
    risk_queries = [
        {
            "query": "How do I assess the risks of launching a new product?",
            "domain": "risk",
            "entities": ["new product launch", "product risks", "market uncertainty"],
            "keywords": ["assess", "risks", "launch", "product"],
            "expected_concepts": ["risk assessment", "scenario analysis", "market analysis"]
        },
        {
            "query": "What's the probability of success for this R&D project?",
            "domain": "risk",
            "entities": ["R&D project", "success probability", "research uncertainty"],
            "keywords": ["probability", "success", "R&D", "project"],
            "expected_concepts": ["monte carlo simulation", "risk assessment", "expected value"]
        },
        {
            "query": "How should we model the uncertainty in our demand forecasts?",
            "domain": "risk",
            "entities": ["demand forecasts", "uncertainty modeling", "forecasting"],
            "keywords": ["model", "uncertainty", "demand", "forecasts"],
            "expected_concepts": ["monte carlo simulation", "scenario analysis", "forecasting"]
        },
        {
            "query": "What are the worst-case scenarios for our business plan?",
            "domain": "risk",
            "entities": ["business plan", "worst-case scenarios", "risk planning"],
            "keywords": ["worst-case", "scenarios", "business plan", "risk"],
            "expected_concepts": ["scenario analysis", "risk assessment"]
        }
    ]
    test_queries.extend(risk_queries)
    
    # ============================================================================
    # DOMAIN 7: HUMAN BEHAVIOR & PSYCHOLOGY
    # ============================================================================
    behavioral_queries = [
        {
            "query": "How do cognitive biases affect our team's decision-making?",
            "domain": "behavioral",
            "entities": ["cognitive biases", "team decisions", "group dynamics"],
            "keywords": ["cognitive", "biases", "team", "decisions"],
            "expected_concepts": ["cognitive behaviors", "judgment intuitive bias", "group dynamics"]
        },
        {
            "query": "Why do people continue investing in failing projects?",
            "domain": "behavioral",
            "entities": ["failing projects", "continued investment", "sunk cost"],
            "keywords": ["failing", "projects", "investing", "continue"],
            "expected_concepts": ["escalation of commitment", "sunk cost fallacy", "cognitive bias"]
        },
        {
            "query": "How do anchoring effects influence our pricing decisions?",
            "domain": "behavioral",
            "entities": ["anchoring effects", "pricing decisions", "cognitive bias"],
            "keywords": ["anchoring", "effects", "pricing", "decisions"],
            "expected_concepts": ["anchoring bias", "cognitive behaviors", "pricing strategy"]
        },
        {
            "query": "What causes groupthink in high-pressure team decisions?",
            "domain": "behavioral",
            "entities": ["groupthink", "team decisions", "pressure"],
            "keywords": ["groupthink", "team", "decisions", "pressure"],
            "expected_concepts": ["cognitive behaviors", "group dynamics", "leadership assessment"]
        }
    ]
    test_queries.extend(behavioral_queries)
    
    # ============================================================================
    # DOMAIN 8: TECHNOLOGY & INNOVATION
    # ============================================================================
    technology_queries = [
        {
            "query": "Should we adopt AI technology for our customer service?",
            "domain": "technology",
            "entities": ["AI technology", "customer service", "technology adoption"],
            "keywords": ["AI", "technology", "customer service", "adopt"],
            "expected_concepts": ["technology assessment", "risk assessment", "cost-benefit analysis"]
        },
        {
            "query": "How do we evaluate competing technology platforms?",
            "domain": "technology",
            "entities": ["technology platforms", "competing technologies", "platform selection"],
            "keywords": ["technology", "platforms", "competing", "evaluate"],
            "expected_concepts": ["competitive analysis", "decision tree", "technology assessment"]
        },
        {
            "query": "What's the ROI of implementing automation in our processes?",
            "domain": "technology",
            "entities": ["automation", "ROI", "process improvement"],
            "keywords": ["automation", "ROI", "processes", "implement"],
            "expected_concepts": ["profitability analysis", "cost-benefit analysis", "risk assessment"]
        },
        {
            "query": "How should we prioritize our innovation projects?",
            "domain": "technology",
            "entities": ["innovation projects", "project prioritization", "R&D"],
            "keywords": ["innovation", "projects", "prioritize", "R&D"],
            "expected_concepts": ["portfolio management", "decision tree", "project prioritization"]
        }
    ]
    test_queries.extend(technology_queries)
    
    # ============================================================================
    # DOMAIN 9: SUSTAINABILITY & ESG
    # ============================================================================
    sustainability_queries = [
        {
            "query": "How do we balance profitability with environmental responsibility?",
            "domain": "sustainability",
            "entities": ["profitability", "environmental responsibility", "ESG"],
            "keywords": ["profitability", "environmental", "responsibility", "balance"],
            "expected_concepts": ["stakeholder alignment", "value creation", "sustainability assessment"]
        },
        {
            "query": "What are the risks of ignoring climate change in our strategy?",
            "domain": "sustainability",
            "entities": ["climate change", "strategic risks", "environmental impact"],
            "keywords": ["climate change", "risks", "strategy", "ignoring"],
            "expected_concepts": ["risk assessment", "scenario analysis", "strategic planning"]
        },
        {
            "query": "How should we evaluate suppliers based on ESG criteria?",
            "domain": "sustainability",
            "entities": ["supplier evaluation", "ESG criteria", "sustainable sourcing"],
            "keywords": ["suppliers", "ESG", "criteria", "evaluate"],
            "expected_concepts": ["supply chain risk management", "stakeholder alignment", "ESG assessment"]
        },
        {
            "query": "What's the business case for investing in renewable energy?",
            "domain": "sustainability",
            "entities": ["renewable energy", "business case", "investment"],
            "keywords": ["renewable", "energy", "business case", "invest"],
            "expected_concepts": ["profitability analysis", "risk assessment", "investment analysis"]
        }
    ]
    test_queries.extend(sustainability_queries)
    
    # ============================================================================
    # DOMAIN 10: GLOBALIZATION & INTERNATIONAL BUSINESS
    # ============================================================================
    global_queries = [
        {
            "query": "How do we manage currency risk in international operations?",
            "domain": "global",
            "entities": ["currency risk", "international operations", "foreign exchange"],
            "keywords": ["currency", "risk", "international", "operations"],
            "expected_concepts": ["risk assessment", "hedging strategies", "international finance"]
        },
        {
            "query": "What are the trade-offs of outsourcing vs. local production?",
            "domain": "global",
            "entities": ["outsourcing", "local production", "supply chain"],
            "keywords": ["outsourcing", "local", "production", "trade-offs"],
            "expected_concepts": ["cost-benefit analysis", "supply chain risk management", "decision tree"]
        },
        {
            "query": "How should we approach market entry in emerging economies?",
            "domain": "global",
            "entities": ["market entry", "emerging economies", "international expansion"],
            "keywords": ["market entry", "emerging", "economies", "approach"],
            "expected_concepts": ["market analysis", "risk assessment", "strategic planning"]
        },
        {
            "query": "What are the political risks of investing in foreign markets?",
            "domain": "global",
            "entities": ["political risks", "foreign markets", "international investment"],
            "keywords": ["political", "risks", "foreign", "markets"],
            "expected_concepts": ["risk assessment", "scenario analysis", "international finance"]
        }
    ]
    test_queries.extend(global_queries)
    
    return test_queries

def analyze_response_quality(response: str, query_info: Dict) -> Dict:
    """Analyze the quality of a response across multiple dimensions"""
    
    analysis = {
        "query": query_info["query"],
        "domain": query_info["domain"],
        "structure_quality": {"score": 0, "issues": []},
        "content_quality": {"score": 0, "issues": []},
        "concept_relevance": {"score": 0, "issues": []},
        "story_overlap": {"score": 0, "issues": []},
        "domain_alignment": {"score": 0, "issues": []},
        "overall_score": 0
    }
    
    # ============================================================================
    # 1. STRUCTURE QUALITY ANALYSIS
    # ============================================================================
    required_sections = [
        "**Strategic Thinking Lens**",
        "**Story in Action**", 
        "**Follow-up Prompts**",
        "**Concepts/Tools**"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in response:
            missing_sections.append(section)
    
    if missing_sections:
        analysis["structure_quality"]["issues"].append(f"Missing sections: {missing_sections}")
        analysis["structure_quality"]["score"] = max(0, 4 - len(missing_sections)) / 4
    else:
        analysis["structure_quality"]["score"] = 1.0
    
    # ============================================================================
    # 2. CONTENT QUALITY ANALYSIS
    # ============================================================================
    content_issues = []
    
    # Check for generic placeholders
    generic_placeholders = [
        "Relevant framework for this decision context",
        "Relevant framework",
        "Decision Frameworks",
        "Value Assessment",
        "Risk Evaluation",
        "Systematic Analysis"
    ]
    
    for placeholder in generic_placeholders:
        if placeholder in response:
            content_issues.append(f"Generic placeholder: '{placeholder}'")
    
    # Check for proper concept format
    concepts_match = re.search(r'\*\*Concepts/Tools\*\*(.*?)(?=\*\*|$)', response, re.DOTALL)
    if concepts_match:
        concepts_content = concepts_match.group(1).strip()
        concept_lines = concepts_content.split('\n')
        for line in concept_lines:
            if line.strip() and ':' not in line and '-' not in line:
                content_issues.append(f"Invalid concept format: '{line.strip()}'")
    
    analysis["content_quality"]["issues"] = content_issues
    analysis["content_quality"]["score"] = max(0, 1 - len(content_issues) * 0.2)
    
    # ============================================================================
    # 3. CONCEPT RELEVANCE ANALYSIS
    # ============================================================================
    expected_concepts = query_info.get("expected_concepts", [])
    concept_relevance_issues = []
    
    if concepts_match and expected_concepts:
        concepts_content = concepts_match.group(1).strip()
        found_concepts = []
        
        for concept in expected_concepts:
            if concept.lower() in concepts_content.lower():
                found_concepts.append(concept)
        
        missing_concepts = [c for c in expected_concepts if c not in found_concepts]
        if missing_concepts:
            concept_relevance_issues.append(f"Missing expected concepts: {missing_concepts}")
        
        analysis["concept_relevance"]["score"] = len(found_concepts) / len(expected_concepts) if expected_concepts else 0.5
    else:
        analysis["concept_relevance"]["score"] = 0.5
    
    analysis["concept_relevance"]["issues"] = concept_relevance_issues
    
    # ============================================================================
    # 4. STORY OVERLAP ANALYSIS
    # ============================================================================
    strategic_lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*(.*?)\*\*Story in Action\*\*', response, re.DOTALL)
    story_match = re.search(r'\*\*Story in Action\*\*(.*?)\*\*Follow-up Prompts\*\*', response, re.DOTALL)
    
    overlap_issues = []
    if strategic_lens_match and story_match:
        strategic_content = strategic_lens_match.group(1).strip()
        story_content = story_match.group(1).strip()
        
        # Check for repeated phrases
        common_phrases = [
            "mentor", "career trajectory", "five-year", "skills you'll develop",
            "dream role", "write down your thoughts", "clarify your priorities",
            "trusted mentor", "consider how this role fits", "long-term",
            "growth potential", "personal values", "strategic choice"
        ]
        
        overlap_count = 0
        for phrase in common_phrases:
            if phrase in strategic_content.lower() and phrase in story_content.lower():
                overlap_issues.append(f"Repeated phrase: '{phrase}'")
                overlap_count += 1
        
        # Calculate overlap score (lower is better)
        analysis["story_overlap"]["score"] = max(0, 1 - overlap_count * 0.1)
    else:
        analysis["story_overlap"]["score"] = 0.5
    
    analysis["story_overlap"]["issues"] = overlap_issues
    
    # ============================================================================
    # 5. DOMAIN ALIGNMENT ANALYSIS
    # ============================================================================
    domain_keywords = {
        "career": ["career", "job", "professional", "work", "employment"],
        "strategy": ["strategy", "competitive", "market", "positioning", "business"],
        "operations": ["operations", "supply chain", "production", "optimization"],
        "financial": ["financial", "investment", "money", "cost", "revenue"],
        "negotiation": ["negotiation", "bargaining", "deal", "agreement", "batna"],
        "risk": ["risk", "uncertainty", "probability", "scenario", "threat"],
        "behavioral": ["behavior", "cognitive", "bias", "psychology", "human"],
        "technology": ["technology", "AI", "digital", "automation", "innovation"],
        "sustainability": ["sustainability", "environmental", "ESG", "green", "climate"],
        "global": ["global", "international", "foreign", "currency", "trade"]
    }
    
    domain_keywords_list = domain_keywords.get(query_info["domain"], [])
    response_lower = response.lower()
    
    domain_alignment_score = 0
    if domain_keywords_list:
        keyword_matches = sum(1 for keyword in domain_keywords_list if keyword in response_lower)
        domain_alignment_score = min(1.0, keyword_matches / len(domain_keywords_list))
    
    analysis["domain_alignment"]["score"] = domain_alignment_score
    
    # ============================================================================
    # 6. OVERALL SCORE CALCULATION
    # ============================================================================
    weights = {
        "structure_quality": 0.25,
        "content_quality": 0.25,
        "concept_relevance": 0.20,
        "story_overlap": 0.15,
        "domain_alignment": 0.15
    }
    
    overall_score = sum(
        analysis[metric]["score"] * weight 
        for metric, weight in weights.items()
    )
    
    analysis["overall_score"] = overall_score
    
    return analysis

def run_comprehensive_quality_testing():
    """Run comprehensive quality testing across all domains"""
    log_message("Starting comprehensive quality testing...")
    
    # Generate test queries
    test_queries = generate_comprehensive_test_queries()
    log_message(f"Generated {len(test_queries)} test queries across 10 domains")
    
    # Test each query
    results = []
    try:
        from query_engine import process_query
        
        for i, query_info in enumerate(test_queries):
            try:
                log_message(f"Testing query {i+1}/{len(test_queries)}: {query_info['domain']} - {query_info['query'][:50]}...")
                
                start_time = time.time()
                response = process_query(query_info["query"])
                processing_time = time.time() - start_time
                
                # Analyze response quality
                analysis = analyze_response_quality(response, query_info)
                analysis["processing_time"] = processing_time
                analysis["response_length"] = len(response)
                
                results.append(analysis)
                
                # Log progress
                if (i + 1) % 10 == 0:
                    log_message(f"Completed {i+1}/{len(test_queries)} queries")
                
            except Exception as e:
                log_message(f"Error testing query {i+1}: {e}", "ERROR")
                results.append({
                    "query": query_info["query"],
                    "domain": query_info["domain"],
                    "error": str(e),
                    "overall_score": 0
                })
    
    except Exception as e:
        log_message(f"Comprehensive testing failed: {e}", "ERROR")
        return {"error": str(e)}
    
    # Analyze overall results
    log_message("Analyzing comprehensive results...")
    
    # Calculate domain-specific statistics
    domain_stats = {}
    for result in results:
        domain = result.get("domain", "unknown")
        if domain not in domain_stats:
            domain_stats[domain] = {
                "count": 0,
                "scores": [],
                "avg_score": 0,
                "issues": []
            }
        
        domain_stats[domain]["count"] += 1
        domain_stats[domain]["scores"].append(result.get("overall_score", 0))
        
        # Collect issues
        for metric in ["structure_quality", "content_quality", "concept_relevance", "story_overlap", "domain_alignment"]:
            if metric in result and "issues" in result[metric]:
                domain_stats[domain]["issues"].extend(result[metric]["issues"])
    
    # Calculate averages
    for domain in domain_stats:
        scores = domain_stats[domain]["scores"]
        domain_stats[domain]["avg_score"] = sum(scores) / len(scores) if scores else 0
    
    # Generate comprehensive report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"comprehensive_quality_report_{timestamp}.md"
    
    # Calculate queries with issues
    metrics_to_check = ['structure_quality', 'content_quality', 'concept_relevance', 'story_overlap', 'domain_alignment']
    queries_with_issues = 0
    for r in results:
        for metric in metrics_to_check:
            if r.get(metric, {}).get('issues', []):
                queries_with_issues += 1
                break
    
    report = f"""
# Comprehensive Quality Testing Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Test Summary
- Total Queries Tested: {len(test_queries)}
- Domains Covered: {len(domain_stats)}
- Average Processing Time: {sum(r.get('processing_time', 0) for r in results) / len(results):.2f}s

## Overall Quality Metrics
- Average Overall Score: {sum(r.get('overall_score', 0) for r in results) / len(results):.2%}
- Queries with Issues: {queries_with_issues}

## Domain-Specific Results
"""
    
    # Sort domains by average score
    sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1]["avg_score"], reverse=True)
    
    for domain, stats in sorted_domains:
        report += f"""
### {domain.title()} Domain
- Queries Tested: {stats['count']}
- Average Score: {stats['avg_score']:.2%}
- Common Issues: {len(set(stats['issues']))} unique issues
"""
    
    report += f"""
## Detailed Results by Query
"""
    
    for i, result in enumerate(results):
        report += f"""
### Query {i+1}: {result.get('query', 'Unknown')}
- Domain: {result.get('domain', 'Unknown')}
- Overall Score: {result.get('overall_score', 0):.2%}
- Processing Time: {result.get('processing_time', 0):.2f}s
- Response Length: {result.get('response_length', 0)} characters

#### Quality Breakdown:
- Structure Quality: {result.get('structure_quality', {}).get('score', 0):.2%}
- Content Quality: {result.get('content_quality', {}).get('score', 0):.2%}
- Concept Relevance: {result.get('concept_relevance', {}).get('score', 0):.2%}
- Story Overlap: {result.get('story_overlap', {}).get('score', 0):.2%}
- Domain Alignment: {result.get('domain_alignment', {}).get('score', 0):.2%}

#### Issues Found:
"""
        
        for metric in ["structure_quality", "content_quality", "concept_relevance", "story_overlap", "domain_alignment"]:
            if metric in result and result[metric].get("issues"):
                report += f"- {metric.replace('_', ' ').title()}: {', '.join(result[metric]['issues'])}\n"
    
    try:
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)
        log_message(f"Comprehensive report saved to {report_filename}")
    except Exception as e:
        log_message(f"Failed to save comprehensive report: {e}", "ERROR")
    
    # Save detailed results as JSON
    results_filename = f"comprehensive_results_{timestamp}.json"
    try:
        with open(results_filename, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "total_queries": len(test_queries),
                "domain_stats": domain_stats,
                "detailed_results": results
            }, f, indent=2, ensure_ascii=False)
        log_message(f"Detailed results saved to {results_filename}")
    except Exception as e:
        log_message(f"Failed to save detailed results: {e}", "ERROR")
    
    # Final summary
    log_message("Comprehensive quality testing completed!")
    log_message(f"Total queries tested: {len(test_queries)}")
    log_message(f"Domains covered: {len(domain_stats)}")
    log_message(f"Average overall score: {sum(r.get('overall_score', 0) for r in results) / len(results):.2%}")
    
    return {
        "total_queries": len(test_queries),
        "domain_stats": domain_stats,
        "results": results
    }

if __name__ == "__main__":
    results = run_comprehensive_quality_testing()
    if "error" in results:
        sys.exit(1)
    else:
        sys.exit(0) 