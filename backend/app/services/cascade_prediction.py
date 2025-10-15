import json
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.models.alert import Alert, CascadePrediction, Client

class CascadePredictionEngine:
    def __init__(self):
        self.cascade_patterns = {
            "database_performance_cascade": {
                "triggers": ["cpu_high", "memory_warning", "slow_query"],
                "cascade_sequence": ["database", "web-app", "api-gateway", "user-interface"],
                "time_windows": [5, 10, 15, 20],  # minutes
                "confidence": 0.85,
                "prevention_actions": [
                    "Restart database service",
                    "Scale database resources",
                    "Clear connection pool",
                    "Enable query caching"
                ]
            },
            "network_infrastructure_cascade": {
                "triggers": ["packet_loss", "latency_spike", "bandwidth_limit"],
                "cascade_sequence": ["network-gateway", "firewall", "load-balancer", "web-servers"],
                "time_windows": [3, 8, 12, 18],
                "confidence": 0.78,
                "prevention_actions": [
                    "Restart network services",
                    "Failover to backup gateway",
                    "Increase bandwidth allocation",
                    "Update routing tables"
                ]
            },
            "storage_system_cascade": {
                "triggers": ["disk_space", "io_wait", "backup_failure"],
                "cascade_sequence": ["storage-server", "database", "file-server", "backup-system"],
                "time_windows": [10, 20, 30, 45],
                "confidence": 0.72,
                "prevention_actions": [
                    "Clear temporary files",
                    "Archive old logs",
                    "Add storage capacity",
                    "Optimize disk I/O"
                ]
            }
        }
        
    def predict_cascade(self, alerts: List[Alert], client: Client) -> List[CascadePrediction]:
        predictions = []
        
        for alert in alerts:
            if alert.severity in ["critical", "warning"]:
                prediction = self._analyze_single_alert(alert, client, alerts)
                if prediction and prediction.prediction_confidence > 0.5:
                    predictions.append(prediction)
        
        return predictions
    
    def _analyze_single_alert(self, alert: Alert, client: Client, all_alerts: List[Alert]) -> Optional[CascadePrediction]:
        # Check for pattern matching
        matched_pattern = self._match_cascade_pattern(alert, all_alerts)
        
        if matched_pattern:
            pattern_data = self.cascade_patterns[matched_pattern]
            
            # Calculate cascade risk based on system dependencies
            affected_systems = self._get_dependent_systems(alert.system, client)
            
            # Estimate time to cascade
            time_to_cascade = pattern_data["time_windows"][0] + random.randint(-2, 5)
            
            return CascadePrediction(
                alert_id=alert.id,
                client_id=alert.client_id,
                prediction_confidence=pattern_data["confidence"],
                predicted_cascade_systems=affected_systems[:3],  # Top 3 systems at risk
                time_to_cascade_minutes=time_to_cascade,
                prevention_actions=pattern_data["prevention_actions"][:2],
                pattern_matched=matched_pattern
            )
        
        # Fallback: Basic dependency-based prediction
        if alert.severity == "critical":
            affected_systems = self._get_dependent_systems(alert.system, client)
            if affected_systems:
                return CascadePrediction(
                    alert_id=alert.id,
                    client_id=alert.client_id,
                    prediction_confidence=0.6,
                    predicted_cascade_systems=affected_systems[:2],
                    time_to_cascade_minutes=random.randint(8, 25),
                    prevention_actions=["Check system dependencies", "Monitor related services"],
                    pattern_matched="dependency_based_fallback"
                )
        
        return None
    
    def _match_cascade_pattern(self, alert: Alert, all_alerts: List[Alert]) -> Optional[str]:
        alert_keywords = alert.message.lower().split()
        
        for pattern_name, pattern_data in self.cascade_patterns.items():
            trigger_matches = 0
            for trigger in pattern_data["triggers"]:
                if any(keyword in trigger for keyword in alert_keywords) or any(trigger in keyword for keyword in alert_keywords):
                    trigger_matches += 1
            
            # Check if we have related alerts that match this pattern
            recent_alerts = [a for a in all_alerts if (datetime.now() - a.timestamp).seconds < 1800]  # Last 30 minutes
            for recent_alert in recent_alerts:
                recent_keywords = recent_alert.message.lower().split()
                for trigger in pattern_data["triggers"]:
                    if any(keyword in trigger for keyword in recent_keywords):
                        trigger_matches += 1
            
            if trigger_matches >= 2:
                return pattern_name
        
        return None
    
    def _get_dependent_systems(self, system: str, client: Client) -> List[str]:
        dependencies = client.system_dependencies.get(system, [])
        
        # Add some intelligence - systems that depend on this system
        dependent_systems = []
        for sys, deps in client.system_dependencies.items():
            if system in deps:
                dependent_systems.append(sys)
        
        return dependencies + dependent_systems
    
    def get_cross_client_insights(self, current_alert: Alert, historical_patterns: List[Dict]) -> Dict:
        """Analyze patterns across multiple clients"""
        similar_patterns = []
        
        for pattern in historical_patterns:
            if (pattern.get("alert_category") == current_alert.category and 
                pattern.get("severity") == current_alert.severity):
                similar_patterns.append(pattern)
        
        if similar_patterns:
            avg_cascade_time = sum(p.get("cascade_time_minutes", 15) for p in similar_patterns) / len(similar_patterns)
            common_affected_systems = []
            
            for pattern in similar_patterns[:3]:  # Top 3 similar cases
                common_affected_systems.extend(pattern.get("affected_systems", []))
            
            return {
                "similar_incidents_count": len(similar_patterns),
                "average_cascade_time": int(avg_cascade_time),
                "commonly_affected_systems": list(set(common_affected_systems)),
                "confidence": min(0.9, len(similar_patterns) / 10)  # Higher confidence with more historical data
            }
        
        return {"similar_incidents_count": 0, "average_cascade_time": 15, "commonly_affected_systems": [], "confidence": 0.3}