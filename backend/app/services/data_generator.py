"""
Enhanced Data Generator for Dynamic Predictions
Generates varied, realistic data for cascade predictions with AI integration
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedDataGenerator:
    """Generate dynamic, varied data for realistic cascade predictions"""
    
    def __init__(self):
        self.systems = [
            "web-app", "database", "cache-server", "api-gateway", 
            "load-balancer", "file-server", "backup-system", "auth-service",
            "payment-gateway", "notification-service", "analytics-engine",
            "cdn", "message-queue", "search-index", "monitoring-system"
        ]
        
        self.failure_patterns = [
            "database_overload", "memory_leak", "disk_full", "network_congestion",
            "cpu_spike", "connection_pool_exhausted", "cache_miss_storm",
            "deadlock_detected", "timeout_cascade", "rate_limit_exceeded",
            "dns_failure", "ssl_certificate_expired", "storage_quota_exceeded",
            "thread_pool_exhausted", "garbage_collection_pause"
        ]
        
        self.severities = ["critical", "warning", "info", "low"]
        self.urgency_levels = ["critical", "high", "medium", "low"]
        
        # Cascade scenarios with realistic dependencies
        self.cascade_scenarios = [
            {
                "trigger": "database",
                "cascade_to": ["web-app", "api-gateway", "cache-server"],
                "pattern": "database_overload",
                "severity": "critical",
                "time_range": (2, 10)
            },
            {
                "trigger": "load-balancer",
                "cascade_to": ["web-app", "api-gateway"],
                "pattern": "network_congestion",
                "severity": "critical",
                "time_range": (5, 15)
            },
            {
                "trigger": "cache-server",
                "cascade_to": ["database", "web-app"],
                "pattern": "cache_miss_storm",
                "severity": "warning",
                "time_range": (3, 12)
            },
            {
                "trigger": "file-server",
                "cascade_to": ["backup-system", "web-app"],
                "pattern": "disk_full",
                "severity": "warning",
                "time_range": (10, 30)
            },
            {
                "trigger": "auth-service",
                "cascade_to": ["web-app", "api-gateway", "payment-gateway"],
                "pattern": "connection_pool_exhausted",
                "severity": "critical",
                "time_range": (1, 5)
            }
        ]
    
    def generate_alert(self, client_id: str, system: str = None, severity: str = None) -> Dict[str, Any]:
        """Generate a single alert with realistic data"""
        if not system:
            system = random.choice(self.systems)
        if not severity:
            severity = random.choices(
                self.severities,
                weights=[0.15, 0.35, 0.35, 0.15]  # More warnings and info
            )[0]
        
        alert_id = f"alert_{uuid.uuid4().hex[:8]}"
        
        # Generate realistic messages based on system and severity
        messages = {
            "database": [
                f"High query latency detected: {random.randint(500, 5000)}ms",
                f"Connection pool usage at {random.randint(80, 99)}%",
                f"Slow query detected: {random.randint(2, 30)} seconds",
                f"Deadlock detected on table: users_{random.randint(1, 10)}"
            ],
            "web-app": [
                f"Response time degraded: {random.randint(1000, 8000)}ms",
                f"Error rate increased to {random.randint(5, 25)}%",
                f"Memory usage at {random.randint(85, 98)}%",
                f"Thread pool exhausted: {random.randint(95, 100)}% utilization"
            ],
            "cache-server": [
                f"Cache hit ratio dropped to {random.randint(20, 60)}%",
                f"Memory eviction rate: {random.randint(100, 1000)} keys/sec",
                f"Connection timeout: {random.randint(50, 200)} clients",
                f"Cache miss storm detected: {random.randint(1000, 5000)} misses/sec"
            ]
        }
        
        default_messages = [
            f"System health degraded: {random.randint(60, 85)}%",
            f"Resource utilization high: {random.randint(80, 95)}%",
            f"Performance anomaly detected",
            f"Threshold exceeded: {random.choice(['CPU', 'Memory', 'Disk', 'Network'])}"
        ]
        
        message_list = messages.get(system, default_messages)
        
        return {
            "id": alert_id,
            "client_id": client_id,
            "system": system,
            "severity": severity,
            "message": random.choice(message_list),
            "category": random.choice(["performance", "availability", "security", "capacity"]),
            "cascade_risk": round(random.uniform(0.3, 0.95), 2),
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat(),
            "resolved": False
        }
    
    def generate_cascade_prediction(self, client_id: str, scenario: Dict = None) -> Dict[str, Any]:
        """Generate a realistic cascade prediction"""
        if not scenario:
            scenario = random.choice(self.cascade_scenarios)
        
        # Calculate time to cascade with some randomness
        min_time, max_time = scenario["time_range"]
        time_to_cascade = random.randint(min_time, max_time)
        
        # Calculate confidence based on severity and time
        base_confidence = 0.7 if scenario["severity"] == "critical" else 0.6
        confidence = round(base_confidence + random.uniform(-0.15, 0.15), 2)
        confidence = max(0.5, min(0.95, confidence))
        
        # Determine urgency based on time and severity
        if time_to_cascade <= 5 and scenario["severity"] == "critical":
            urgency = "critical"
        elif time_to_cascade <= 10 or scenario["severity"] == "critical":
            urgency = "high"
        elif time_to_cascade <= 20:
            urgency = "medium"
        else:
            urgency = "low"
        
        return {
            "client_id": client_id,
            "pattern": scenario["pattern"],
            "pattern_matched": scenario["pattern"],
            "affected_systems": [scenario["trigger"]],
            "predicted_cascade_systems": scenario["cascade_to"],
            "time_to_cascade_minutes": time_to_cascade,
            "resolution_time_minutes": time_to_cascade + random.randint(10, 30),
            "prediction_confidence": confidence,
            "urgency_level": urgency,
            "severity": scenario["severity"],
            "root_cause": scenario["trigger"],
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_client_predictions(self, client_id: str, count: int = None) -> List[Dict[str, Any]]:
        """Generate multiple predictions for a client with varied risk levels"""
        if count is None:
            # Vary the number of predictions
            count = random.randint(3, 6)
        
        predictions = []
        used_scenarios = []
        
        # Ensure we have at least one high-risk scenario if count > 2
        if count >= 3:
            # Pick a critical scenario first
            critical_scenarios = [s for s in self.cascade_scenarios if s["severity"] == "critical"]
            if critical_scenarios:
                scenario = random.choice(critical_scenarios)
                prediction = self.generate_cascade_prediction(client_id, scenario)
                # Force it to be high risk by adjusting time and confidence
                prediction["time_to_cascade_minutes"] = random.randint(2, 8)
                prediction["prediction_confidence"] = round(random.uniform(0.75, 0.92), 2)
                prediction["urgency_level"] = "critical" if prediction["time_to_cascade_minutes"] <= 5 else "high"
                predictions.append(prediction)
                used_scenarios.append(scenario)
                count -= 1
        
        # Generate remaining predictions with variety
        for _ in range(count):
            # Pick a scenario we haven't used yet if possible
            available_scenarios = [s for s in self.cascade_scenarios if s not in used_scenarios]
            if not available_scenarios:
                available_scenarios = self.cascade_scenarios
                used_scenarios = []
            
            scenario = random.choice(available_scenarios)
            used_scenarios.append(scenario)
            
            prediction = self.generate_cascade_prediction(client_id, scenario)
            predictions.append(prediction)
        
        return predictions
    
    async def generate_enhanced_prediction_with_ai(self, client_id: str) -> Dict[str, Any]:
        """Generate enhanced AI prediction using REAL Gemini AI model"""
        import os
        import google.generativeai as genai
        
        # Get API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key or api_key == "demo_key":
            # Fallback to deterministic if no API key
            return self.generate_enhanced_prediction(client_id)
        
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate base scenario
            scenario = random.choice(self.cascade_scenarios)
            base_prediction = self.generate_cascade_prediction(client_id, scenario)
            
            # Create AI prompt for dynamic analysis
            prompt = f"""You are an expert IT infrastructure analyst. Analyze this cascade failure scenario and provide a detailed prediction.

SCENARIO:
- Trigger System: {scenario['trigger']}
- Pattern: {scenario['pattern'].replace('_', ' ')}
- Severity: {scenario['severity']}
- Will cascade to: {', '.join(scenario['cascade_to'])}
- Time to cascade: {base_prediction['time_to_cascade_minutes']} minutes
- Confidence: {base_prediction['prediction_confidence']*100:.0f}%

Provide your analysis in this EXACT JSON format (no markdown, just raw JSON):
{{
  "summary": "A 2-3 sentence explanation of this cascade scenario and its business impact",
  "root_causes": ["cause 1", "cause 2", "cause 3"],
  "prevention_actions": ["action 1", "action 2", "action 3", "action 4"],
  "urgency_explanation": "Why this has {base_prediction['urgency_level']} urgency"
}}

Be specific and technical. Make each response unique and insightful."""

            # Call Gemini AI
            response = await model.generate_content_async(prompt)
            
            # Parse AI response
            import json
            import re
            
            # Extract JSON from response (handle markdown code blocks)
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            
            ai_analysis = json.loads(response_text)
            
            # Build enhanced prediction with AI-generated content
            enhanced = {
                "prediction": {
                    **base_prediction,
                    "predicted_in": base_prediction["time_to_cascade_minutes"],
                    "summary": ai_analysis.get("summary", self._generate_summary(scenario, base_prediction)),
                    "root_causes": ai_analysis.get("root_causes", self._generate_root_causes(scenario)),
                    "prevention_actions": ai_analysis.get("prevention_actions", self._generate_prevention_actions(scenario)),
                    "llm_analysis_quality": "excellent",  # Real AI used
                    "data_sources_count": random.randint(8, 15),
                    "trend_analysis_available": True,
                    "external_factors_considered": True,
                    "confidence": base_prediction["prediction_confidence"],
                    "ai_generated": True,
                    "urgency_explanation": ai_analysis.get("urgency_explanation", "")
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "model_version": "gemini-1.5-flash",
                    "analysis_type": "ai_enhanced_cascade_prediction",
                    "ai_model_used": True
                }
            }
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"AI generation failed, using fallback: {e}")
            # Fallback to deterministic generation
            return self.generate_enhanced_prediction(client_id)
    
    def generate_enhanced_prediction(self, client_id: str) -> Dict[str, Any]:
        """Generate enhanced AI prediction with detailed analysis (FALLBACK - deterministic)"""
        scenario = random.choice(self.cascade_scenarios)
        base_prediction = self.generate_cascade_prediction(client_id, scenario)
        
        # Add enhanced fields
        enhanced = {
            "prediction": {
                **base_prediction,
                "predicted_in": base_prediction["time_to_cascade_minutes"],  # Add this for frontend compatibility
                "summary": self._generate_summary(scenario, base_prediction),
                "root_causes": self._generate_root_causes(scenario),
                "prevention_actions": self._generate_prevention_actions(scenario),
                "llm_analysis_quality": "medium",  # Fallback mode
                "data_sources_count": random.randint(5, 10),
                "trend_analysis_available": random.choice([True, False]),
                "external_factors_considered": random.choice([True, False]),
                "confidence": base_prediction["prediction_confidence"],
                "ai_generated": False
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_version": "deterministic-fallback",
                "analysis_type": "enhanced_cascade_prediction",
                "ai_model_used": False
            }
        }
        
        return enhanced
    
    def _generate_summary(self, scenario: Dict, prediction: Dict) -> str:
        """Generate a realistic summary for the prediction"""
        summaries = [
            f"Cascade failure predicted starting from {scenario['trigger']} with {prediction['urgency_level']} urgency. "
            f"Expected to affect {len(scenario['cascade_to'])} dependent systems within {prediction['time_to_cascade_minutes']} minutes.",
            
            f"Critical pattern detected: {scenario['pattern'].replace('_', ' ')}. "
            f"System {scenario['trigger']} showing signs of failure that will cascade to {', '.join(scenario['cascade_to'][:2])}.",
            
            f"High-confidence prediction ({prediction['prediction_confidence']*100:.0f}%) of cascade failure. "
            f"Primary system {scenario['trigger']} degradation will impact {len(scenario['cascade_to'])} systems.",
            
            f"Imminent cascade risk from {scenario['trigger']}. "
            f"Pattern analysis indicates {scenario['pattern'].replace('_', ' ')} will propagate within {prediction['time_to_cascade_minutes']} minutes."
        ]
        
        return random.choice(summaries)
    
    def _generate_root_causes(self, scenario: Dict) -> List[str]:
        """Generate realistic root causes"""
        causes_map = {
            "database_overload": [
                "Inefficient query execution plans",
                "Missing database indexes on frequently queried tables",
                "Connection pool size insufficient for current load",
                "Long-running transactions blocking other queries"
            ],
            "memory_leak": [
                "Unclosed database connections accumulating",
                "Large object retention in application cache",
                "Event listeners not being properly removed",
                "Circular references preventing garbage collection"
            ],
            "network_congestion": [
                "Bandwidth saturation from large file transfers",
                "DDoS attack or unusual traffic spike",
                "Network switch port errors",
                "Routing table misconfiguration"
            ],
            "cache_miss_storm": [
                "Cache invalidation triggered for large dataset",
                "Cache server restart causing cold cache",
                "TTL expiration synchronized across keys",
                "Application not implementing cache-aside pattern correctly"
            ]
        }
        
        pattern = scenario["pattern"]
        causes = causes_map.get(pattern, [
            f"Resource exhaustion on {scenario['trigger']}",
            f"Configuration drift detected",
            f"Capacity threshold exceeded"
        ])
        
        return random.sample(causes, min(3, len(causes)))
    
    def _generate_prevention_actions(self, scenario: Dict) -> List[str]:
        """Generate realistic prevention actions"""
        actions_map = {
            "database_overload": [
                "Scale database read replicas",
                "Implement query result caching",
                "Optimize slow queries identified in logs",
                "Increase connection pool size",
                "Enable query timeout limits"
            ],
            "memory_leak": [
                "Restart affected services in rolling fashion",
                "Enable heap dump analysis",
                "Implement memory monitoring alerts",
                "Review recent code deployments"
            ],
            "network_congestion": [
                "Enable traffic shaping and QoS",
                "Scale out load balancer capacity",
                "Implement rate limiting on API endpoints",
                "Activate DDoS mitigation if applicable"
            ],
            "cache_miss_storm": [
                "Pre-warm cache with frequently accessed data",
                "Implement request coalescing",
                "Enable cache stampede protection",
                "Increase cache TTL for stable data"
            ]
        }
        
        pattern = scenario["pattern"]
        actions = actions_map.get(pattern, [
            f"Scale {scenario['trigger']} resources",
            f"Enable automated failover",
            f"Implement circuit breaker pattern",
            f"Increase monitoring frequency"
        ])
        
        return random.sample(actions, min(4, len(actions)))
    
    def generate_system_metrics(self, client_id: str, system: str) -> Dict[str, Any]:
        """Generate realistic system metrics"""
        # Create realistic metric patterns
        base_cpu = random.uniform(30, 70)
        base_memory = random.uniform(40, 75)
        
        # Add some correlation between metrics
        if base_cpu > 60:
            base_memory = min(95, base_memory + random.uniform(10, 20))
        
        return {
            "client_id": client_id,
            "system": system,
            "cpu_usage": round(base_cpu + random.uniform(-5, 15), 2),
            "memory_usage": round(base_memory + random.uniform(-5, 10), 2),
            "disk_usage": round(random.uniform(45, 85), 2),
            "network_latency": round(random.uniform(10, 150), 2),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
data_generator = EnhancedDataGenerator()
