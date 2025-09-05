from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from app.models.alert import Alert, AlertCorrelation

class AlertCorrelationEngine:
    def __init__(self):
        self.noise_patterns = [
            "disk cleanup completed",
            "scheduled backup started",
            "automatic update installed",
            "service restarted successfully",
            "connection established",
            "user logged in",
            "cache cleared"
        ]
        
        self.duplicate_keywords = [
            ["cpu", "processor", "high usage"],
            ["memory", "ram", "out of memory"],
            ["disk", "storage", "space"],
            ["network", "connection", "timeout"],
            ["database", "sql", "query"]
        ]
    
    def filter_noise_alerts(self, alerts: List[Alert]) -> Tuple[List[Alert], List[Alert]]:
        """Separate critical alerts from noise"""
        critical_alerts = []
        noise_alerts = []
        
        for alert in alerts:
            if self._is_noise_alert(alert):
                alert.is_noise = True
                noise_alerts.append(alert)
            else:
                critical_alerts.append(alert)
        
        return critical_alerts, noise_alerts
    
    def correlate_alerts(self, alerts: List[Alert]) -> List[AlertCorrelation]:
        """Find related alerts and group them"""
        correlations = []
        processed_alerts = set()
        
        for i, primary_alert in enumerate(alerts):
            if primary_alert.id in processed_alerts:
                continue
                
            related_alerts = []
            
            for j, candidate_alert in enumerate(alerts):
                if i != j and candidate_alert.id not in processed_alerts:
                    correlation_score = self._calculate_correlation_score(primary_alert, candidate_alert)
                    
                    if correlation_score > 0.6:
                        related_alerts.append(candidate_alert.id)
                        processed_alerts.add(candidate_alert.id)
            
            if related_alerts:
                correlation_type = self._determine_correlation_type(primary_alert, [a for a in alerts if a.id in related_alerts])
                
                correlations.append(AlertCorrelation(
                    primary_alert_id=primary_alert.id,
                    related_alert_ids=related_alerts,
                    correlation_confidence=min(0.9, len(related_alerts) * 0.3),
                    correlation_type=correlation_type
                ))
                
                processed_alerts.add(primary_alert.id)
        
        return correlations
    
    def _is_noise_alert(self, alert: Alert) -> bool:
        message_lower = alert.message.lower()
        
        # Check against known noise patterns
        for pattern in self.noise_patterns:
            if pattern in message_lower:
                return True
        
        # Check severity and category
        if alert.severity == "info" and alert.category not in ["security", "performance"]:
            return True
        
        # Check for successful operations (usually not critical)
        success_indicators = ["completed", "successful", "ok", "normal", "restored"]
        if any(indicator in message_lower for indicator in success_indicators):
            return True
        
        return False
    
    def _calculate_correlation_score(self, alert1: Alert, alert2: Alert) -> float:
        score = 0.0
        
        # Time proximity (alerts within 10 minutes get higher score)
        time_diff = abs((alert1.timestamp - alert2.timestamp).total_seconds())
        if time_diff <= 600:  # 10 minutes
            score += 0.4 * (1 - time_diff / 600)
        
        # Same client
        if alert1.client_id == alert2.client_id:
            score += 0.3
        
        # Same or related systems
        if alert1.system == alert2.system:
            score += 0.4
        elif self._are_related_systems(alert1.system, alert2.system):
            score += 0.2
        
        # Same category
        if alert1.category == alert2.category:
            score += 0.2
        
        # Similar message content
        similarity = self._calculate_message_similarity(alert1.message, alert2.message)
        score += similarity * 0.3
        
        return min(score, 1.0)
    
    def _are_related_systems(self, system1: str, system2: str) -> bool:
        """Check if two systems are typically related"""
        related_groups = [
            ["database", "web-app", "api-gateway"],
            ["email-server", "file-server", "backup-system"],
            ["network-gateway", "firewall", "load-balancer"],
            ["storage-server", "backup-system", "file-server"]
        ]
        
        for group in related_groups:
            if system1 in group and system2 in group:
                return True
        
        return False
    
    def _calculate_message_similarity(self, message1: str, message2: str) -> float:
        """Simple keyword-based similarity calculation"""
        words1 = set(message1.lower().split())
        words2 = set(message2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _determine_correlation_type(self, primary_alert: Alert, related_alerts: List[Alert]) -> str:
        """Determine the type of correlation between alerts"""
        
        # Check for cascade pattern (escalating severity)
        severities = [primary_alert.severity] + [a.severity for a in related_alerts]
        if "warning" in severities and "critical" in severities:
            return "cascade"
        
        # Check for duplicates (very similar messages)
        for related_alert in related_alerts:
            similarity = self._calculate_message_similarity(primary_alert.message, related_alert.message)
            if similarity > 0.8:
                return "duplicate"
        
        # Check for same system/category
        same_system = all(a.system == primary_alert.system for a in related_alerts)
        same_category = all(a.category == primary_alert.category for a in related_alerts)
        
        if same_system and same_category:
            return "related"
        
        return "related"
    
    def generate_alert_summary(self, alerts: List[Alert], correlations: List[AlertCorrelation]) -> Dict:
        """Generate a summary of alert filtering and correlation results"""
        critical_alerts, noise_alerts = self.filter_noise_alerts(alerts)
        
        total_alerts = len(alerts)
        noise_filtered = len(noise_alerts)
        correlated_groups = len(correlations)
        
        # Calculate reduction in alert noise
        noise_reduction_percent = (noise_filtered / total_alerts) * 100 if total_alerts > 0 else 0
        
        # Get top alert categories
        category_counts = {}
        for alert in critical_alerts:
            category_counts[alert.category] = category_counts.get(alert.category, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "noise_filtered": noise_filtered,
            "critical_alerts": len(critical_alerts),
            "noise_reduction_percent": round(noise_reduction_percent, 1),
            "correlated_groups": correlated_groups,
            "top_categories": dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]),
            "efficiency_improvement": f"{noise_reduction_percent:.1f}% noise reduction, {correlated_groups} alert groups identified"
        }