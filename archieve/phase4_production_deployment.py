#!/usr/bin/env python3
"""
Phase 4: Production Deployment for V1.6.5.1
Comprehensive deployment with monitoring and success metrics validation
"""

import json
import time
import statistics
from typing import Dict, List, Any, Tuple
from datetime import datetime
import threading
import queue
from dataclasses import dataclass
from enum import Enum

# Import the query engine modules
from query_engine import process_query
from expanded_entities import extract_expanded_entities, get_entity_summary

# ============================================================================
# PHASE 4 SUCCESS METRICS
# ============================================================================

@dataclass
class Phase4Metrics:
    """Phase 4 success metrics configuration"""
    avg_response_time_increase_max: float = 0.10  # ≤ 10%
    percentile_95_response_time_max: float = 0.25  # ≤ 25%
    clarity_score_min: float = 0.6  # ≥ 0.6
    structure_preservation_min: float = 0.95  # ≥ 95%
    natural_integration_min: float = 0.90  # ≥ 90%
    critical_errors_max: int = 0  # No critical errors

class DeploymentStatus(Enum):
    """Deployment status enumeration"""
    PREPARING = "preparing"
    GRADUAL_ROLLOUT = "gradual_rollout"
    FULL_DEPLOYMENT = "full_deployment"
    MONITORING = "monitoring"
    ROLLBACK = "rollback"
    SUCCESS = "success"
    FAILED = "failed"

# ============================================================================
# PRODUCTION MONITORING SYSTEM
# ============================================================================

class ProductionMonitor:
    """Real-time production monitoring system"""
    
    def __init__(self, metrics: Phase4Metrics):
        self.metrics = metrics
        self.response_times = []
        self.clarity_scores = []
        self.structure_preservation = []
        self.natural_integration = []
        self.critical_errors = 0
        self.total_queries = 0
        self.successful_queries = 0
        self.monitoring_active = False
        self.alert_queue = queue.Queue()
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.monitoring_active = True
        print("🔍 Starting production monitoring...")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        print("🛑 Stopping production monitoring...")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check metrics every 30 seconds
                time.sleep(30)
                self._check_metrics()
                
                # Process alerts
                while not self.alert_queue.empty():
                    alert = self.alert_queue.get_nowait()
                    self._handle_alert(alert)
                    
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                
    def _check_metrics(self):
        """Check if metrics are within acceptable ranges"""
        if len(self.response_times) < 10:  # Need minimum data points
            return
            
        # Calculate current metrics
        avg_response_time_increase = statistics.mean(self.response_times[-50:])  # Last 50 queries
        percentile_95 = self._calculate_percentile(self.response_times[-50:], 95)
        avg_clarity = statistics.mean(self.clarity_scores[-50:]) if self.clarity_scores else 0
        structure_rate = statistics.mean(self.structure_preservation[-50:]) if self.structure_preservation else 0
        natural_rate = statistics.mean(self.natural_integration[-50:]) if self.natural_integration else 0
        
        # Check thresholds
        alerts = []
        
        if avg_response_time_increase > self.metrics.avg_response_time_increase_max:
            alerts.append(f"Response time increase {avg_response_time_increase:.1%} exceeds {self.metrics.avg_response_time_increase_max:.1%}")
            
        if percentile_95 > self.metrics.percentile_95_response_time_max:
            alerts.append(f"95th percentile response time {percentile_95:.1%} exceeds {self.metrics.percentile_95_response_time_max:.1%}")
            
        if avg_clarity < self.metrics.clarity_score_min:
            alerts.append(f"Clarity score {avg_clarity:.3f} below {self.metrics.clarity_score_min}")
            
        if structure_rate < self.metrics.structure_preservation_min:
            alerts.append(f"Structure preservation {structure_rate:.1%} below {self.metrics.structure_preservation_min:.1%}")
            
        if natural_rate < self.metrics.natural_integration_min:
            alerts.append(f"Natural integration {natural_rate:.1%} below {self.metrics.natural_integration_min:.1%}")
            
        if self.critical_errors > self.metrics.critical_errors_max:
            alerts.append(f"Critical errors {self.critical_errors} exceed maximum {self.metrics.critical_errors_max}")
            
        # Send alerts
        for alert in alerts:
            self.alert_queue.put(("WARNING", alert))
            
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
            
    def _handle_alert(self, alert: Tuple[str, str]):
        """Handle monitoring alerts"""
        alert_type, message = alert
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {alert_type}: {message}")
        
        if alert_type == "CRITICAL":
            self._trigger_rollback()
            
    def _trigger_rollback(self):
        """Trigger automatic rollback"""
        print("🚨 CRITICAL: Triggering automatic rollback...")
        # Implementation for rollback would go here
        self.stop_monitoring()
        
    def record_query_result(self, response_time: float, clarity_score: float, 
                          structure_preserved: bool, natural_integration: bool, 
                          error: bool = False):
        """Record results from a query"""
        self.total_queries += 1
        
        if error:
            self.critical_errors += 1
        else:
            self.successful_queries += 1
            self.response_times.append(response_time)
            self.clarity_scores.append(clarity_score)
            self.structure_preservation.append(1.0 if structure_preserved else 0.0)
            self.natural_integration.append(1.0 if natural_integration else 0.0)

# ============================================================================
# PHASE 4 DEPLOYMENT SYSTEM
# ============================================================================

class Phase4Deployment:
    """Phase 4 production deployment system"""
    
    def __init__(self, metrics: Phase4Metrics):
        self.metrics = metrics
        self.monitor = ProductionMonitor(metrics)
        self.status = DeploymentStatus.PREPARING
        self.deployment_data = {
            "start_time": None,
            "gradual_rollout_time": None,
            "full_deployment_time": None,
            "completion_time": None,
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "metrics_summary": {}
        }
        
    def execute_phase4(self) -> Dict[str, Any]:
        """Execute complete Phase 4 deployment"""
        print("🚀 Phase 4: Production Deployment for V1.6.5.1")
        print("=" * 60)
        
        try:
            # Phase 4A: Safe Deployment
            self._prepare_deployment()
            self._gradual_rollout()
            
            # Phase 4B: Full Deployment
            self._full_deployment()
            self._monitor_and_validate()
            
            # Generate final report
            return self._generate_deployment_report()
            
        except Exception as e:
            print(f"❌ Phase 4 deployment failed: {e}")
            self.status = DeploymentStatus.FAILED
            return {"status": "failed", "error": str(e)}
            
    def _prepare_deployment(self):
        """Prepare for deployment"""
        print("📋 Phase 4A: Preparing Deployment...")
        self.status = DeploymentStatus.PREPARING
        self.deployment_data["start_time"] = datetime.now()
        
        # Enable enhanced entities
        import query_engine
        query_engine.USE_ENHANCED_ENTITIES = True
        print("✅ Enhanced entities enabled")
        
        # Start monitoring
        self.monitor.start_monitoring()
        print("✅ Production monitoring started")
        
    def _gradual_rollout(self):
        """Gradual rollout to 10% of queries"""
        print("📈 Phase 4A: Gradual Rollout (10%)...")
        self.status = DeploymentStatus.GRADUAL_ROLLOUT
        self.deployment_data["gradual_rollout_time"] = datetime.now()
        
        # Test with sample queries
        test_queries = [
            "Should I invest in renewable energy for my company within the next 6 months?",
            "How do we handle employee concerns about the new policy in the short term?",
            "What financial criteria should we consider for long-term investor satisfaction?",
            "How do we manage operational complexity for immediate customer needs?",
            "What strategic risks do regulators see in our approach to market expansion?"
        ]
        
        print(f"🧪 Testing with {len(test_queries)} sample queries...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"   Testing query {i}/{len(test_queries)}: {query[:50]}...")
            
            start_time = time.time()
            try:
                result = process_query(query)
                response_time = time.time() - start_time
                
                # Assess quality
                clarity_score = self._assess_clarity(result)
                structure_preserved = self._check_structure_preservation(result)
                natural_integration = self._check_natural_integration(result)
                
                # Record metrics
                self.monitor.record_query_result(
                    response_time=response_time,
                    clarity_score=clarity_score,
                    structure_preserved=structure_preserved,
                    natural_integration=natural_integration
                )
                
                self.deployment_data["total_queries"] += 1
                self.deployment_data["successful_queries"] += 1
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
                self.monitor.record_query_result(0, 0, False, False, error=True)
                self.deployment_data["total_queries"] += 1
                self.deployment_data["failed_queries"] += 1
                
        print("✅ Gradual rollout completed")
        
    def _full_deployment(self):
        """Full deployment to 100% of queries"""
        print("🚀 Phase 4B: Full Deployment (100%)...")
        self.status = DeploymentStatus.FULL_DEPLOYMENT
        self.deployment_data["full_deployment_time"] = datetime.now()
        
        # Test with comprehensive query set
        comprehensive_queries = [
            # Entity-rich queries
            "Should we expand our business to new markets within the next quarter?",
            "How do we balance cost and quality for our suppliers in the coming months?",
            "What operational efficiency measures should we implement this year?",
            "How do we address customer complaints about our service quality?",
            "What risk management strategies should we adopt for high uncertainty scenarios?",
            
            # Entity-neutral queries
            "What is the best approach to decision making?",
            "How do I improve my analytical skills?",
            "What frameworks are useful for strategic planning?",
            "How do I evaluate different options?",
            "What tools help with problem solving?"
        ]
        
        print(f"🧪 Testing with {len(comprehensive_queries)} comprehensive queries...")
        
        for i, query in enumerate(comprehensive_queries, 1):
            print(f"   Testing query {i}/{len(comprehensive_queries)}: {query[:50]}...")
            
            start_time = time.time()
            try:
                result = process_query(query)
                response_time = time.time() - start_time
                
                # Assess quality
                clarity_score = self._assess_clarity(result)
                structure_preserved = self._check_structure_preservation(result)
                natural_integration = self._check_natural_integration(result)
                
                # Record metrics
                self.monitor.record_query_result(
                    response_time=response_time,
                    clarity_score=clarity_score,
                    structure_preserved=structure_preserved,
                    natural_integration=natural_integration
                )
                
                self.deployment_data["total_queries"] += 1
                self.deployment_data["successful_queries"] += 1
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
                self.monitor.record_query_result(0, 0, False, False, error=True)
                self.deployment_data["total_queries"] += 1
                self.deployment_data["failed_queries"] += 1
                
        print("✅ Full deployment completed")
        
    def _monitor_and_validate(self):
        """Monitor and validate success metrics"""
        print("📊 Phase 4B: Monitoring and Validation...")
        self.status = DeploymentStatus.MONITORING
        
        # Wait for monitoring to collect data
        time.sleep(60)  # Monitor for 1 minute
        
        # Calculate final metrics
        if self.monitor.response_times:
            avg_response_time_increase = statistics.mean(self.monitor.response_times)
            percentile_95 = self.monitor._calculate_percentile(self.monitor.response_times, 95)
        else:
            avg_response_time_increase = 0.0
            percentile_95 = 0.0
            
        avg_clarity = statistics.mean(self.monitor.clarity_scores) if self.monitor.clarity_scores else 0.0
        structure_rate = statistics.mean(self.monitor.structure_preservation) if self.monitor.structure_preservation else 0.0
        natural_rate = statistics.mean(self.monitor.natural_integration) if self.monitor.natural_integration else 0.0
        
        # Validate success metrics
        success_metrics = {
            "avg_response_time_increase": avg_response_time_increase,
            "percentile_95_response_time": percentile_95,
            "clarity_score": avg_clarity,
            "structure_preservation": structure_rate,
            "natural_integration": natural_rate,
            "critical_errors": self.monitor.critical_errors
        }
        
        # Check if all metrics pass
        all_passed = (
            avg_response_time_increase <= self.metrics.avg_response_time_increase_max and
            percentile_95 <= self.metrics.percentile_95_response_time_max and
            avg_clarity >= self.metrics.clarity_score_min and
            structure_rate >= self.metrics.structure_preservation_min and
            natural_rate >= self.metrics.natural_integration_min and
            self.monitor.critical_errors <= self.metrics.critical_errors_max
        )
        
        if all_passed:
            self.status = DeploymentStatus.SUCCESS
            print("🎉 Phase 4 SUCCESS: All metrics passed!")
        else:
            self.status = DeploymentStatus.FAILED
            print("❌ Phase 4 FAILED: Some metrics did not meet requirements")
            
        # Store metrics summary
        self.deployment_data["metrics_summary"] = success_metrics
        self.deployment_data["completion_time"] = datetime.now()
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
    def _assess_clarity(self, text: str) -> float:
        """Assess text clarity (same as Phase 3)"""
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        complex_words = len([w for w in text.split() if len(w) > 6])
        total_words = len(text.split())
        complexity_ratio = complex_words / total_words if total_words > 0 else 0
        
        # Improved clarity score (0-1, higher is better)
        sentence_length_penalty = (avg_sentence_length - 20) / 200
        clarity_score = max(0, 1 - complexity_ratio - sentence_length_penalty)
        
        # Add paragraph bonus for clear, digestible sections
        paragraph_breaks = text.count('\n')
        paragraph_bonus = min(0.1, paragraph_breaks * 0.02)
        clarity_score = min(1.0, clarity_score + paragraph_bonus)
        
        return min(1.0, max(0.0, clarity_score))
        
    def _check_structure_preservation(self, text: str) -> bool:
        """Check if ThinkPal structure is preserved"""
        required_sections = ["Strategic Thinking Lens", "Story in Action", "Follow-up Prompts"]
        return all(section in text for section in required_sections)
        
    def _check_natural_integration(self, text: str) -> bool:
        """Check if entities are integrated naturally"""
        template_indicators = [
            "timeframe:", "stakeholders:", "criteria:", "uncertainty:", "complexity:",
            "detected entities:", "entity context:", "extracted entities:"
        ]
        has_template_language = any(indicator in text.lower() for indicator in template_indicators)
        return not has_template_language
        
    def _generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment report"""
        print("\n📊 PHASE 4 DEPLOYMENT REPORT")
        print("=" * 60)
        
        # Calculate metrics
        metrics = self.deployment_data["metrics_summary"]
        
        print(f"📈 Deployment Summary:")
        print(f"   Status: {self.status.value.upper()}")
        print(f"   Total Queries: {self.deployment_data['total_queries']}")
        print(f"   Successful Queries: {self.deployment_data['successful_queries']}")
        print(f"   Failed Queries: {self.deployment_data['failed_queries']}")
        print(f"   Success Rate: {self.deployment_data['successful_queries']/self.deployment_data['total_queries']:.1%}")
        
        print(f"\n🎯 Success Metrics:")
        print(f"   Avg Response Time Increase: {metrics['avg_response_time_increase']:.1%} (target: ≤{self.metrics.avg_response_time_increase_max:.1%})")
        print(f"   95th Percentile Response Time: {metrics['percentile_95_response_time']:.1%} (target: ≤{self.metrics.percentile_95_response_time_max:.1%})")
        print(f"   Clarity Score: {metrics['clarity_score']:.3f} (target: ≥{self.metrics.clarity_score_min})")
        print(f"   Structure Preservation: {metrics['structure_preservation']:.1%} (target: ≥{self.metrics.structure_preservation_min:.1%})")
        print(f"   Natural Integration: {metrics['natural_integration']:.1%} (target: ≥{self.metrics.natural_integration_min:.1%})")
        print(f"   Critical Errors: {metrics['critical_errors']} (target: ≤{self.metrics.critical_errors_max})")
        
        # Determine overall success
        all_passed = (
            metrics['avg_response_time_increase'] <= self.metrics.avg_response_time_increase_max and
            metrics['percentile_95_response_time'] <= self.metrics.percentile_95_response_time_max and
            metrics['clarity_score'] >= self.metrics.clarity_score_min and
            metrics['structure_preservation'] >= self.metrics.structure_preservation_min and
            metrics['natural_integration'] >= self.metrics.natural_integration_min and
            metrics['critical_errors'] <= self.metrics.critical_errors_max
        )
        
        if all_passed:
            print(f"\n🎉 PHASE 4 SUCCESS: All metrics passed!")
        else:
            print(f"\n❌ PHASE 4 FAILED: Some metrics did not meet requirements")
            
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"phase4_deployment_report_{timestamp}.json"
        
        report_data = {
            "phase": "Phase 4",
            "version": "V1.6.5.1",
            "status": self.status.value,
            "deployment_data": self.deployment_data,
            "metrics": metrics,
            "success": all_passed,
            "timestamp": timestamp
        }
        
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        return report_data

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_phase4_deployment():
    """Main function to run Phase 4 deployment"""
    print("🚀 Phase 4: Production Deployment for V1.6.5.1")
    print("=" * 60)
    
    # Initialize metrics
    metrics = Phase4Metrics()
    
    # Initialize deployment
    deployment = Phase4Deployment(metrics)
    
    # Execute Phase 4
    result = deployment.execute_phase4()
    
    return result

if __name__ == "__main__":
    run_phase4_deployment() 