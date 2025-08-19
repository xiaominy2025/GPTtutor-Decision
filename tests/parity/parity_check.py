#!/usr/bin/env python3
"""
Parity Check for Engent Labs V1.6.6.6 Backend
Tests local vs remote endpoints for 100% feature parity
Structural comparison allowing minor text differences
"""

import requests
import json
import argparse
import sys
import time
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class TestCase:
    """Test case for parity checking"""
    name: str
    method: str
    endpoint: str
    payload: Dict[str, Any] = None
    description: str = ""

class ParityChecker:
    """Compares local and remote API responses for structural parity"""
    
    def __init__(self, local_base: str, remote_base: str, timeout: int = 30):
        self.local_base = local_base.rstrip('/')
        self.remote_base = remote_base.rstrip('/')
        self.timeout = timeout
        self.results = []
    
    def make_request(self, base_url: str, method: str, endpoint: str, payload: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any], str]:
        """Make HTTP request and return success, response data, error message"""
        url = f"{base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=payload or {}, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=payload or {}, timeout=self.timeout)
            else:
                return False, {}, f"Unsupported method: {method}"
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data, ""
                except json.JSONDecodeError:
                    return False, {}, f"Invalid JSON response: {response.text[:200]}"
            else:
                return False, {}, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            return False, {}, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, {}, "Connection error"
        except Exception as e:
            return False, {}, f"Request error: {str(e)}"
    
    def compare_structures(self, local_data: Dict[str, Any], remote_data: Dict[str, Any], path: str = "root") -> List[str]:
        """Compare data structures, allowing text content differences"""
        differences = []
        
        # Check keys
        local_keys = set(local_data.keys()) if isinstance(local_data, dict) else set()
        remote_keys = set(remote_data.keys()) if isinstance(remote_data, dict) else set()
        
        missing_in_remote = local_keys - remote_keys
        missing_in_local = remote_keys - local_keys
        
        for key in missing_in_remote:
            differences.append(f"{path}.{key}: Missing in remote")
        
        for key in missing_in_local:
            differences.append(f"{path}.{key}: Missing in local")
        
        # Check common keys
        common_keys = local_keys & remote_keys
        for key in common_keys:
            local_val = local_data[key]
            remote_val = remote_data[key]
            new_path = f"{path}.{key}"
            
            # Type comparison
            if type(local_val) != type(remote_val):
                differences.append(f"{new_path}: Type mismatch - local: {type(local_val).__name__}, remote: {type(remote_val).__name__}")
                continue
            
            # Recursive comparison for nested structures
            if isinstance(local_val, dict):
                differences.extend(self.compare_structures(local_val, remote_val, new_path))
            elif isinstance(local_val, list):
                if len(local_val) != len(remote_val):
                    differences.append(f"{new_path}: Length mismatch - local: {len(local_val)}, remote: {len(remote_val)}")
                else:
                    for i, (local_item, remote_item) in enumerate(zip(local_val, remote_val)):
                        if isinstance(local_item, dict) and isinstance(remote_item, dict):
                            differences.extend(self.compare_structures(local_item, remote_item, f"{new_path}[{i}]"))
                        elif type(local_item) != type(remote_item):
                            differences.append(f"{new_path}[{i}]: Type mismatch - local: {type(local_item).__name__}, remote: {type(remote_item).__name__}")
            # For strings and other primitives, we only check type (allowing content differences)
            # This allows for minor text variations while ensuring structural parity
        
        return differences
    
    def run_test(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a single parity test"""
        print(f"🧪 Testing {test_case.name}...")
        
        # Make requests to both endpoints
        local_success, local_data, local_error = self.make_request(
            self.local_base, test_case.method, test_case.endpoint, test_case.payload
        )
        
        remote_success, remote_data, remote_error = self.make_request(
            self.remote_base, test_case.method, test_case.endpoint, test_case.payload
        )
        
        result = {
            "test_name": test_case.name,
            "endpoint": test_case.endpoint,
            "method": test_case.method,
            "local_success": local_success,
            "remote_success": remote_success,
            "local_error": local_error,
            "remote_error": remote_error,
            "structural_differences": [],
            "passed": False
        }
        
        # Check if both requests succeeded
        if not local_success:
            result["error"] = f"Local request failed: {local_error}"
            return result
        
        if not remote_success:
            result["error"] = f"Remote request failed: {remote_error}"
            return result
        
        # Compare structures
        differences = self.compare_structures(local_data, remote_data)
        result["structural_differences"] = differences
        result["passed"] = len(differences) == 0
        
        if result["passed"]:
            print(f"   ✅ PASSED")
        else:
            print(f"   ❌ FAILED - {len(differences)} structural differences")
            for diff in differences[:3]:  # Show first 3 differences
                print(f"      • {diff}")
            if len(differences) > 3:
                print(f"      • ... and {len(differences) - 3} more")
        
        return result
    
    def run_all_tests(self, test_cases: List[TestCase]) -> bool:
        """Run all parity tests and return overall success"""
        print(f"🚀 Running {len(test_cases)} parity tests")
        print(f"   Local:  {self.local_base}")
        print(f"   Remote: {self.remote_base}")
        print()
        
        all_passed = True
        
        for test_case in test_cases:
            result = self.run_test(test_case)
            self.results.append(result)
            
            if not result["passed"]:
                all_passed = False
        
        # Summary
        print()
        passed_count = sum(1 for r in self.results if r["passed"])
        total_count = len(self.results)
        
        print(f"📊 Results: {passed_count}/{total_count} tests passed")
        
        if all_passed:
            print("🎉 All parity tests PASSED - 100% feature parity confirmed!")
        else:
            print("❌ Some parity tests FAILED - structural differences detected")
            
            # Show failed tests
            failed_tests = [r for r in self.results if not r["passed"]]
            for result in failed_tests:
                print(f"   • {result['test_name']}: {len(result['structural_differences'])} differences")
        
        return all_passed

def create_test_cases() -> List[TestCase]:
    """Create comprehensive test cases for V1.6.6.6 backend"""
    
    return [
        # Health check
        TestCase(
            name="Health Check",
            method="GET",
            endpoint="/health",
            description="Basic health check endpoint"
        ),
        
        # Glossary endpoint
        TestCase(
            name="Glossary",
            method="GET", 
            endpoint="/glossary",
            description="Glossary endpoint with course concepts"
        ),
        
        # Courses endpoint
        TestCase(
            name="Courses List",
            method="GET",
            endpoint="/courses",
            description="Available courses listing"
        ),
        
        # Query tests - 5 comprehensive cases
        TestCase(
            name="Query - Short Strategic",
            method="POST",
            endpoint="/query",
            payload={"query": "How should I make a strategic business decision?"},
            description="Short strategic business query"
        ),
        
        TestCase(
            name="Query - Long Analytical",
            method="POST", 
            endpoint="/query",
            payload={
                "query": "I need to decide whether to expand our manufacturing operations to a new facility in Southeast Asia. The investment would be $50M and we expect to break even in 3 years. What analytical tools should I use to evaluate this decision, and how should I account for political risk, currency fluctuations, and supply chain disruptions?"
            },
            description="Long analytical query with multiple domains"
        ),
        
        TestCase(
            name="Query - Noisy Input",
            method="POST",
            endpoint="/query", 
            payload={
                "query": "umm... so like, I'm trying to figure out if I should hire more people for my startup? We're growing fast but cash flow is tight. What do you think???"
            },
            description="Noisy query with informal language"
        ),
        
        TestCase(
            name="Query - Multi-Domain",
            method="POST",
            endpoint="/query",
            payload={
                "query": "Our company needs to implement AI automation while managing the risk of employee layoffs and ensuring regulatory compliance. How do we balance technology adoption with human capital management and legal requirements?"
            },
            description="Multi-domain query spanning technology, HR, and regulatory"
        ),
        
        TestCase(
            name="Query - Glossary Heavy",
            method="POST",
            endpoint="/query",
            payload={
                "query": "I'm in a negotiation where I need to determine my BATNA and reservation point. The other party seems to be using anchoring bias and I want to find the ZOPA. Should I use integrative or distributive negotiation strategies?"
            },
            description="Query heavy with glossary concepts and technical terms"
        )
    ]

def main():
    """Main parity checker entry point"""
    parser = argparse.ArgumentParser(description="Engent Labs V1.6.6.6 Parity Checker")
    parser.add_argument("--local", required=True, help="Local API base URL (e.g., http://localhost:8000)")
    parser.add_argument("--remote", required=True, help="Remote API base URL (e.g., https://api.example.com)")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--output", help="Output file for detailed results (JSON)")
    
    args = parser.parse_args()
    
    # Create test cases
    test_cases = create_test_cases()
    
    # Run parity checks
    checker = ParityChecker(args.local, args.remote, args.timeout)
    success = checker.run_all_tests(test_cases)
    
    # Save detailed results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "local_base": args.local,
                "remote_base": args.remote,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "results": checker.results
            }, f, indent=2)
        print(f"📄 Detailed results saved to {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
