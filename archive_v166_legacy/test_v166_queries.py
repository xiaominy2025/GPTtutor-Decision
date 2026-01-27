#!/usr/bin/env python3
"""
V1.6.6 Query Testing Script
Tests the current query engine with specific queries and generates a comprehensive report
"""

import os
import sys
import json
import time
from datetime import datetime
from query_engine import process_query

def test_v166_queries():
    """Test the current query engine with specific queries for V1.6.6 merge functionality"""
    
    # Test queries specifically designed to test the merge functionality
    queries = [
        "Under tariff uncertainty, how do I plan my production?",
        "I have two job offers, how to choose?",
        "How to convey bad news to my boss?",
        "How do I negotiate a better salary package with my boss?",
        "How to negotiate with a dealership?",
        "How shall I deal with unfair critiques from my manager?",
        "My team members are reluctant to give up his legacy projects, how shall I convince him to think differently?"
    ]
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"🧪 V1.6.6 Merge Functionality Testing - {timestamp}")
    print("=" * 60)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            response = process_query(query)
            end_time = time.time()
            
            # Analyze the response structure
            has_strategic_lens = "**Strategic Thinking Lens**" in response
            has_story_section = "**Story in Action**" in response
            has_followup = "**Follow-up Prompts**" in response
            has_concepts = "**Concepts/Tools**" in response
            
            # Check if merge was applied (Story section should be removed)
            merge_applied = has_strategic_lens and not has_story_section
            
            result = {
                "query_number": i,
                "query": query,
                "response": response,
                "processing_time": round(end_time - start_time, 2),
                "timestamp": datetime.now().isoformat(),
                "analysis": {
                    "has_strategic_lens": has_strategic_lens,
                    "has_story_section": has_story_section,
                    "has_followup": has_followup,
                    "has_concepts": has_concepts,
                    "merge_applied": merge_applied,
                    "response_length": len(response)
                }
            }
            
            results.append(result)
            
            print(f"✅ Query {i} completed in {result['processing_time']}s")
            print(f"📊 Response length: {len(response)} characters")
            print(f"🔍 Merge applied: {merge_applied}")
            print(f"📋 Sections: Lens={has_strategic_lens}, Story={has_story_section}, Followup={has_followup}, Concepts={has_concepts}")
            
        except Exception as e:
            print(f"❌ Error processing query {i}: {str(e)}")
            result = {
                "query_number": i,
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            results.append(result)
    
    # Generate comprehensive report
    generate_report(results, timestamp)
    
    return results

def generate_report(results, timestamp):
    """Generate a comprehensive report of the test results"""
    
    successful_results = [r for r in results if "error" not in r]
    failed_results = [r for r in results if "error" in r]
    
    # Calculate merge statistics
    merge_applied_count = sum(1 for r in successful_results if r.get('analysis', {}).get('merge_applied', False))
    merge_success_rate = (merge_applied_count / len(successful_results) * 100) if successful_results else 0
    
    report = {
        "test_info": {
            "version": "V1.6.6",
            "timestamp": timestamp,
            "total_queries": len(results),
            "successful_queries": len(successful_results),
            "failed_queries": len(failed_results),
            "merge_applied_count": merge_applied_count,
            "merge_success_rate": round(merge_success_rate, 2)
        },
        "results": results,
        "summary": {
            "average_processing_time": 0,
            "total_response_length": 0,
            "response_lengths": []
        }
    }
    
    # Calculate summary statistics
    if successful_results:
        report["summary"]["average_processing_time"] = round(
            sum(r["processing_time"] for r in successful_results) / len(successful_results), 2
        )
        report["summary"]["total_response_length"] = sum(len(r["response"]) for r in successful_results)
        report["summary"]["response_lengths"] = [len(r["response"]) for r in successful_results]
    
    # Save JSON report
    json_filename = f"v166_merge_test_report_{timestamp}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Generate markdown report
    md_filename = f"v166_merge_test_report_{timestamp}.md"
    generate_markdown_report(report, md_filename)
    
    print(f"\n📊 Report generated:")
    print(f"   📄 JSON: {json_filename}")
    print(f"   📄 Markdown: {md_filename}")
    print(f"   📈 Merge Success Rate: {merge_success_rate:.1f}%")

def generate_markdown_report(report, filename):
    """Generate a markdown report for easy reading"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# V1.6.6 Merge Functionality Test Report\n\n")
        f.write(f"**Test Date:** {report['test_info']['timestamp']}\n")
        f.write(f"**Version:** {report['test_info']['version']}\n")
        f.write(f"**Total Queries:** {report['test_info']['total_queries']}\n")
        f.write(f"**Successful:** {report['test_info']['successful_queries']}\n")
        f.write(f"**Failed:** {report['test_info']['failed_queries']}\n")
        f.write(f"**Merge Applied:** {report['test_info']['merge_applied_count']}\n")
        f.write(f"**Merge Success Rate:** {report['test_info']['merge_success_rate']}%\n\n")
        
        if report['summary']['average_processing_time'] > 0:
            f.write(f"**Average Processing Time:** {report['summary']['average_processing_time']}s\n")
            f.write(f"**Total Response Length:** {report['summary']['total_response_length']:,} characters\n\n")
        
        f.write("## Query Results\n\n")
        
        for result in report['results']:
            f.write(f"### Query {result['query_number']}: {result['query']}\n\n")
            
            if "error" in result:
                f.write(f"❌ **Error:** {result['error']}\n\n")
            else:
                f.write(f"✅ **Processing Time:** {result['processing_time']}s\n")
                f.write(f"📊 **Response Length:** {len(result['response'])} characters\n")
                f.write(f"🔍 **Merge Applied:** {result['analysis']['merge_applied']}\n")
                f.write(f"📋 **Sections:** Lens={result['analysis']['has_strategic_lens']}, Story={result['analysis']['has_story_section']}, Followup={result['analysis']['has_followup']}, Concepts={result['analysis']['has_concepts']}\n\n")
                f.write("**Response:**\n\n")
                f.write("```\n")
                f.write(result['response'])
                f.write("\n```\n\n")
                f.write("---\n\n")

if __name__ == "__main__":
    test_v166_queries() 