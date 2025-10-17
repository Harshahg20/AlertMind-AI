"""
Cascade Failure Agent for Advanced Failure Detection and Analysis
Implements real-time failure monitoring with multi-dimensional analysis and automated response
"""

import asyncio
import json
import logging
import threading
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from dataclasses import dataclass
from enum import Enum

from app.models.alert import Alert, Client, CascadePrediction, SeverityLevel, AlertCategory
from app.services.cascade_prediction import CascadePredictionEngine

logger = logging.getLogger(__name__)

class FailureType(Enum):
    """Types of failure analysis"""
    SYSTEM_DEGRADATION = "system_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_FAILURE = "network_failure"
    DATABASE_FAILURE = "database_failure"
    APPLICATION_FAILURE = "application_failure"
    CASCADE_PROPAGATION = "cascade_propagation"
    DEPENDENCY_FAILURE = "dependency_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"

class FailureSeverity(Enum):
    """Failure severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    WARNING = "warning"

@dataclass
class FailureAnalysis:
    """Result from a single failure analysis"""
    failure_type: FailureType
    severity: FailureSeverity
    confidence: float
    analysis: Dict[str, Any]
    reasoning: str
    metadata: Dict[str, Any]
    execution_time_ms: float
    affected_systems: List[str]
    recovery_actions: List[str]

class CascadeFailureAgent:
    """
    Advanced Cascade Failure Agent for comprehensive failure detection and analysis
    Uses multiple parallel analysis modules to provide robust failure detection
    """
    
    def __init__(self, max_workers: int = 8):
        self.name = "cascade_failure_agent"
        self.created_at = datetime.now()
        self.max_workers = max_workers
        
        # Initialize prediction engine
        self.prediction_engine = CascadePredictionEngine()
        
        # Agent memory and learning
        self.failure_memory = []
        self.failure_patterns = {}
        self.recovery_effectiveness = {}
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance metrics
        self.performance_metrics = {
            "total_analyses": 0,
            "failures_detected": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "average_detection_time_ms": 0.0,
            "recovery_success_rate": 0.0
        }
        
        # Failure detection thresholds
        self.thresholds = {
            "critical_failure_confidence": 0.8,
            "high_failure_confidence": 0.6,
            "medium_failure_confidence": 0.4,
            "cascade_propagation_threshold": 0.7,
            "resource_exhaustion_threshold": 0.85
        }
    
    async def run(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for cascade failure agent
        Runs multiple failure analysis modules in parallel and combines results
        """
        start_time = datetime.now()
        
        try:
            # Extract data
            alerts = correlated_data.get("alerts", [])
            client = correlated_data.get("client")
            historical_data = correlated_data.get("historical_data", [])
            
            if not alerts or not client:
                raise ValueError("Missing required data: alerts and client")
            
            # Convert alerts to consistent format
            alert_objects = self._normalize_alerts(alerts, client)
            
            # Define failure analysis modules
            failure_analyzers = [
                (FailureType.SYSTEM_DEGRADATION, self._system_degradation_analysis),
                (FailureType.RESOURCE_EXHAUSTION, self._resource_exhaustion_analysis),
                (FailureType.NETWORK_FAILURE, self._network_failure_analysis),
                (FailureType.DATABASE_FAILURE, self._database_failure_analysis),
                (FailureType.APPLICATION_FAILURE, self._application_failure_analysis),
                (FailureType.CASCADE_PROPAGATION, self._cascade_propagation_analysis),
                (FailureType.DEPENDENCY_FAILURE, self._dependency_failure_analysis),
                (FailureType.PERFORMANCE_DEGRADATION, self._performance_degradation_analysis)
            ]
            
            # Execute failure analyzers in parallel
            failure_results = await self._execute_failure_analyzers_parallel(
                failure_analyzers, alert_objects, client, historical_data
            )
            
            # Combine failure analysis results
            combined_analysis = self._combine_failure_results(
                failure_results, alert_objects, client
            )
            
            # Update agent memory and performance
            self._update_agent_memory(alert_objects, combined_analysis, client.id)
            self._update_performance_metrics(failure_results, start_time)
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Cascade Failure Agent failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._fallback_analysis(correlated_data)
    
    def _normalize_alerts(self, alerts: List[Any], client: Client) -> List[Alert]:
        """Convert alerts to consistent Alert objects"""
        normalized_alerts = []
        
        for alert in alerts:
            if isinstance(alert, dict):
                # Convert dict to Alert object
                alert_obj = Alert(
                    id=alert.get("id", f"alert_{len(normalized_alerts)}"),
                    client_id=alert.get("client_id", client.id),
                    client_name=alert.get("client_name", client.name),
                    system=alert.get("system", "unknown"),
                    severity=SeverityLevel(alert.get("severity", "info")),
                    message=alert.get("message", "No message"),
                    category=AlertCategory(alert.get("category", "system")),
                    timestamp=datetime.fromisoformat(
                        alert.get("timestamp", datetime.now().isoformat()).replace('Z', '+00:00')
                    ),
                    cascade_risk=alert.get("cascade_risk", 0.0),
                    is_correlated=alert.get("is_correlated", False)
                )
                normalized_alerts.append(alert_obj)
            else:
                # Already an Alert object
                normalized_alerts.append(alert)
        
        return normalized_alerts
    
    async def _execute_failure_analyzers_parallel(
        self, 
        analyzers: List[Tuple[FailureType, callable]], 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> List[FailureAnalysis]:
        """Execute failure analyzers in parallel"""
        
        # Create tasks for each analyzer
        tasks = []
        for failure_type, analyzer_func in analyzers:
            task = asyncio.create_task(
                self._execute_single_failure_analyzer(failure_type, analyzer_func, alerts, client, historical_data)
            )
            tasks.append(task)
        
        # Wait for all analyzers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failure analyzer {analyzers[i][0].value} failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _execute_single_failure_analyzer(
        self, 
        failure_type: FailureType, 
        analyzer_func: callable, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> FailureAnalysis:
        """Execute a single failure analyzer"""
        start_time = datetime.now()
        
        try:
            # Run analyzer function in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                analyzer_func, 
                alerts, 
                client, 
                historical_data
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return FailureAnalysis(
                failure_type=failure_type,
                severity=result.get("severity", FailureSeverity.MEDIUM),
                confidence=result.get("confidence", 0.0),
                analysis=result.get("analysis", {}),
                reasoning=result.get("reasoning", ""),
                metadata=result.get("metadata", {}),
                execution_time_ms=execution_time,
                affected_systems=result.get("affected_systems", []),
                recovery_actions=result.get("recovery_actions", [])
            )
            
        except Exception as e:
            logger.error(f"Failure analyzer {failure_type.value} execution failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return FailureAnalysis(
                failure_type=failure_type,
                severity=FailureSeverity.LOW,
                confidence=0.0,
                analysis={},
                reasoning=f"Analyzer failed: {str(e)}",
                metadata={"error": str(e)},
                execution_time_ms=execution_time,
                affected_systems=[],
                recovery_actions=[]
            )
    
    def _system_degradation_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze system degradation patterns"""
        try:
            # Analyze alert severity progression
            severity_counts = {"critical": 0, "warning": 0, "info": 0, "low": 0}
            for alert in alerts:
                severity_counts[alert.severity.value] += 1
            
            # Calculate degradation score
            degradation_score = (
                severity_counts["critical"] * 4 +
                severity_counts["warning"] * 2 +
                severity_counts["info"] * 1 +
                severity_counts["low"] * 0.5
            ) / len(alerts) if alerts else 0
            
            # Analyze temporal degradation
            current_time = datetime.now()
            recent_alerts = [a for a in alerts if (current_time - a.timestamp).total_seconds() < 1800]  # Last 30 minutes
            temporal_degradation = len(recent_alerts) / max(1, len(alerts))
            
            # Calculate overall degradation confidence
            degradation_confidence = min(1.0, (degradation_score / 4.0) * temporal_degradation)
            
            # Determine severity
            if degradation_confidence > 0.8:
                severity = FailureSeverity.CRITICAL
            elif degradation_confidence > 0.6:
                severity = FailureSeverity.HIGH
            elif degradation_confidence > 0.4:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            # Get affected systems
            affected_systems = list(set([alert.system for alert in alerts]))
            
            return {
                "severity": severity,
                "confidence": degradation_confidence,
                "analysis": {
                    "degradation_score": degradation_score,
                    "temporal_degradation": temporal_degradation,
                    "severity_distribution": severity_counts,
                    "recent_alerts_count": len(recent_alerts)
                },
                "reasoning": f"System degradation analysis shows {degradation_confidence:.2f} confidence with {len(affected_systems)} affected systems",
                "metadata": {
                    "total_alerts": len(alerts),
                    "analysis_type": "system_degradation",
                    "time_window_minutes": 30
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Restart degraded services",
                    "Scale system resources",
                    "Check system health metrics",
                    "Review recent configuration changes"
                ]
            }
            
        except Exception as e:
            logger.error(f"System degradation analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"System degradation analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _resource_exhaustion_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze resource exhaustion patterns"""
        try:
            # Analyze resource-related alerts
            resource_keywords = {
                "cpu": ["cpu", "processor", "load", "utilization"],
                "memory": ["memory", "ram", "heap", "out of memory"],
                "disk": ["disk", "storage", "space", "full"],
                "network": ["bandwidth", "connection", "timeout", "latency"]
            }
            
            resource_alerts = {"cpu": [], "memory": [], "disk": [], "network": []}
            
            for alert in alerts:
                alert_text = alert.message.lower()
                for resource_type, keywords in resource_keywords.items():
                    if any(keyword in alert_text for keyword in keywords):
                        resource_alerts[resource_type].append(alert)
            
            # Calculate resource exhaustion scores
            resource_scores = {}
            for resource_type, resource_alert_list in resource_alerts.items():
                if resource_alert_list:
                    severity_weights = {"critical": 4, "warning": 2, "info": 1, "low": 0.5}
                    total_weight = sum(severity_weights.get(alert.severity.value, 1) for alert in resource_alert_list)
                    resource_scores[resource_type] = min(1.0, total_weight / (len(resource_alert_list) * 4))
                else:
                    resource_scores[resource_type] = 0.0
            
            # Calculate overall resource exhaustion confidence
            max_resource_score = max(resource_scores.values()) if resource_scores else 0.0
            resource_count = len([score for score in resource_scores.values() if score > 0.3])
            exhaustion_confidence = min(1.0, max_resource_score * (1 + resource_count * 0.2))
            
            # Determine severity
            if exhaustion_confidence > 0.8:
                severity = FailureSeverity.CRITICAL
            elif exhaustion_confidence > 0.6:
                severity = FailureSeverity.HIGH
            elif exhaustion_confidence > 0.4:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            # Get affected systems
            affected_systems = list(set([alert.system for alert in alerts if any(
                keyword in alert.message.lower() for keywords in resource_keywords.values() for keyword in keywords
            )]))
            
            return {
                "severity": severity,
                "confidence": exhaustion_confidence,
                "analysis": {
                    "resource_scores": resource_scores,
                    "resource_alerts_count": {k: len(v) for k, v in resource_alerts.items()},
                    "max_resource_score": max_resource_score,
                    "exhausted_resources": [k for k, v in resource_scores.items() if v > 0.5]
                },
                "reasoning": f"Resource exhaustion analysis shows {exhaustion_confidence:.2f} confidence with {len([k for k, v in resource_scores.items() if v > 0.3])} resource types affected",
                "metadata": {
                    "analysis_type": "resource_exhaustion",
                    "resource_types_analyzed": len(resource_keywords)
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Scale system resources immediately",
                    "Clear resource bottlenecks",
                    "Restart resource-intensive services",
                    "Optimize resource allocation"
                ]
            }
            
        except Exception as e:
            logger.error(f"Resource exhaustion analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"Resource exhaustion analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _network_failure_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze network failure patterns"""
        try:
            # Analyze network-related alerts
            network_keywords = [
                "network", "connection", "timeout", "latency", "packet", "bandwidth",
                "firewall", "gateway", "router", "switch", "dns", "tcp", "udp"
            ]
            
            network_alerts = [alert for alert in alerts if any(
                keyword in alert.message.lower() for keyword in network_keywords
            )]
            
            if not network_alerts:
                return {
                    "severity": FailureSeverity.LOW,
                    "confidence": 0.0,
                    "analysis": {"network_alerts": 0},
                    "reasoning": "No network-related alerts detected",
                    "metadata": {"analysis_type": "network_failure"},
                    "affected_systems": [],
                    "recovery_actions": []
                }
            
            # Analyze network failure patterns
            critical_network_alerts = [a for a in network_alerts if a.severity.value == "critical"]
            warning_network_alerts = [a for a in network_alerts if a.severity.value == "warning"]
            
            # Calculate network failure confidence
            network_failure_confidence = (
                len(critical_network_alerts) * 0.4 +
                len(warning_network_alerts) * 0.2 +
                len(network_alerts) * 0.1
            ) / max(1, len(alerts))
            
            network_failure_confidence = min(1.0, network_failure_confidence)
            
            # Determine severity
            if network_failure_confidence > 0.7:
                severity = FailureSeverity.CRITICAL
            elif network_failure_confidence > 0.5:
                severity = FailureSeverity.HIGH
            elif network_failure_confidence > 0.3:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            # Get affected systems
            affected_systems = list(set([alert.system for alert in network_alerts]))
            
            return {
                "severity": severity,
                "confidence": network_failure_confidence,
                "analysis": {
                    "network_alerts": len(network_alerts),
                    "critical_network_alerts": len(critical_network_alerts),
                    "warning_network_alerts": len(warning_network_alerts),
                    "network_failure_indicators": [alert.message for alert in critical_network_alerts[:3]]
                },
                "reasoning": f"Network failure analysis shows {network_failure_confidence:.2f} confidence with {len(network_alerts)} network-related alerts",
                "metadata": {
                    "analysis_type": "network_failure",
                    "network_keywords_checked": len(network_keywords)
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Check network connectivity",
                    "Restart network services",
                    "Verify firewall rules",
                    "Test network latency and bandwidth"
                ]
            }
            
        except Exception as e:
            logger.error(f"Network failure analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"Network failure analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _database_failure_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze database failure patterns"""
        try:
            # Analyze database-related alerts
            database_keywords = [
                "database", "db", "sql", "query", "connection", "timeout",
                "deadlock", "lock", "transaction", "replication", "backup"
            ]
            
            database_alerts = [alert for alert in alerts if any(
                keyword in alert.message.lower() for keyword in database_keywords
            )]
            
            if not database_alerts:
                return {
                    "severity": FailureSeverity.LOW,
                    "confidence": 0.0,
                    "analysis": {"database_alerts": 0},
                    "reasoning": "No database-related alerts detected",
                    "metadata": {"analysis_type": "database_failure"},
                    "affected_systems": [],
                    "recovery_actions": []
                }
            
            # Analyze database failure patterns
            critical_db_alerts = [a for a in database_alerts if a.severity.value == "critical"]
            warning_db_alerts = [a for a in database_alerts if a.severity.value == "warning"]
            
            # Calculate database failure confidence
            db_failure_confidence = (
                len(critical_db_alerts) * 0.5 +
                len(warning_db_alerts) * 0.3 +
                len(database_alerts) * 0.1
            ) / max(1, len(alerts))
            
            db_failure_confidence = min(1.0, db_failure_confidence)
            
            # Determine severity
            if db_failure_confidence > 0.7:
                severity = FailureSeverity.CRITICAL
            elif db_failure_confidence > 0.5:
                severity = FailureSeverity.HIGH
            elif db_failure_confidence > 0.3:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            # Get affected systems
            affected_systems = list(set([alert.system for alert in database_alerts]))
            
            return {
                "severity": severity,
                "confidence": db_failure_confidence,
                "analysis": {
                    "database_alerts": len(database_alerts),
                    "critical_database_alerts": len(critical_db_alerts),
                    "warning_database_alerts": len(warning_db_alerts),
                    "database_failure_indicators": [alert.message for alert in critical_db_alerts[:3]]
                },
                "reasoning": f"Database failure analysis shows {db_failure_confidence:.2f} confidence with {len(database_alerts)} database-related alerts",
                "metadata": {
                    "analysis_type": "database_failure",
                    "database_keywords_checked": len(database_keywords)
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Check database connectivity",
                    "Restart database services",
                    "Verify database replication",
                    "Check for deadlocks and long-running queries"
                ]
            }
            
        except Exception as e:
            logger.error(f"Database failure analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"Database failure analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _application_failure_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze application failure patterns"""
        try:
            # Analyze application-related alerts
            app_keywords = [
                "application", "app", "service", "api", "endpoint", "response",
                "error", "exception", "crash", "restart", "deployment"
            ]
            
            app_alerts = [alert for alert in alerts if any(
                keyword in alert.message.lower() for keyword in app_keywords
            )]
            
            if not app_alerts:
                return {
                    "severity": FailureSeverity.LOW,
                    "confidence": 0.0,
                    "analysis": {"application_alerts": 0},
                    "reasoning": "No application-related alerts detected",
                    "metadata": {"analysis_type": "application_failure"},
                    "affected_systems": [],
                    "recovery_actions": []
                }
            
            # Analyze application failure patterns
            critical_app_alerts = [a for a in app_alerts if a.severity.value == "critical"]
            warning_app_alerts = [a for a in app_alerts if a.severity.value == "warning"]
            
            # Calculate application failure confidence
            app_failure_confidence = (
                len(critical_app_alerts) * 0.4 +
                len(warning_app_alerts) * 0.2 +
                len(app_alerts) * 0.1
            ) / max(1, len(alerts))
            
            app_failure_confidence = min(1.0, app_failure_confidence)
            
            # Determine severity
            if app_failure_confidence > 0.6:
                severity = FailureSeverity.CRITICAL
            elif app_failure_confidence > 0.4:
                severity = FailureSeverity.HIGH
            elif app_failure_confidence > 0.2:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            # Get affected systems
            affected_systems = list(set([alert.system for alert in app_alerts]))
            
            return {
                "severity": severity,
                "confidence": app_failure_confidence,
                "analysis": {
                    "application_alerts": len(app_alerts),
                    "critical_application_alerts": len(critical_app_alerts),
                    "warning_application_alerts": len(warning_app_alerts),
                    "application_failure_indicators": [alert.message for alert in critical_app_alerts[:3]]
                },
                "reasoning": f"Application failure analysis shows {app_failure_confidence:.2f} confidence with {len(app_alerts)} application-related alerts",
                "metadata": {
                    "analysis_type": "application_failure",
                    "application_keywords_checked": len(app_keywords)
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Restart application services",
                    "Check application logs",
                    "Verify service dependencies",
                    "Test application endpoints"
                ]
            }
            
        except Exception as e:
            logger.error(f"Application failure analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"Application failure analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _cascade_propagation_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze cascade propagation patterns"""
        try:
            # Use existing prediction engine for cascade analysis
            predictions = self.prediction_engine.predict_cascade(alerts, client)
            
            if not predictions:
                return {
                    "severity": FailureSeverity.LOW,
                    "confidence": 0.0,
                    "analysis": {"cascade_predictions": 0},
                    "reasoning": "No cascade propagation patterns detected",
                    "metadata": {"analysis_type": "cascade_propagation"},
                    "affected_systems": [],
                    "recovery_actions": []
                }
            
            # Analyze cascade propagation
            high_confidence_predictions = [p for p in predictions if p.prediction_confidence > 0.7]
            medium_confidence_predictions = [p for p in predictions if 0.4 <= p.prediction_confidence <= 0.7]
            
            # Calculate cascade propagation confidence
            cascade_confidence = max([p.prediction_confidence for p in predictions]) if predictions else 0.0
            
            # Determine severity
            if cascade_confidence > 0.8:
                severity = FailureSeverity.CRITICAL
            elif cascade_confidence > 0.6:
                severity = FailureSeverity.HIGH
            elif cascade_confidence > 0.4:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            # Get affected systems from predictions
            all_affected_systems = []
            for prediction in predictions:
                all_affected_systems.extend(prediction.predicted_cascade_systems)
            affected_systems = list(set(all_affected_systems))
            
            return {
                "severity": severity,
                "confidence": cascade_confidence,
                "analysis": {
                    "cascade_predictions": len(predictions),
                    "high_confidence_predictions": len(high_confidence_predictions),
                    "medium_confidence_predictions": len(medium_confidence_predictions),
                    "predicted_cascade_systems": affected_systems,
                    "average_cascade_time": np.mean([p.time_to_cascade_minutes for p in predictions]) if predictions else 0
                },
                "reasoning": f"Cascade propagation analysis shows {cascade_confidence:.2f} confidence with {len(predictions)} cascade predictions",
                "metadata": {
                    "analysis_type": "cascade_propagation",
                    "prediction_engine_used": True
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Implement immediate isolation measures",
                    "Activate failover systems",
                    "Scale resources for affected systems",
                    "Monitor cascade propagation closely"
                ]
            }
            
        except Exception as e:
            logger.error(f"Cascade propagation analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"Cascade propagation analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _dependency_failure_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze dependency failure patterns"""
        try:
            # Analyze system dependencies
            affected_systems = list(set([alert.system for alert in alerts]))
            
            # Calculate dependency failure risk
            dependency_risks = {}
            for system in affected_systems:
                # Get systems that depend on this system
                dependent_systems = []
                for sys, deps in client.system_dependencies.items():
                    if system in deps:
                        dependent_systems.append(sys)
                
                # Calculate risk based on number of dependents
                dependency_risks[system] = min(1.0, len(dependent_systems) * 0.2)
            
            # Calculate overall dependency failure confidence
            if dependency_risks:
                max_dependency_risk = max(dependency_risks.values())
                avg_dependency_risk = np.mean(list(dependency_risks.values()))
                dependency_confidence = (max_dependency_risk * 0.7) + (avg_dependency_risk * 0.3)
            else:
                dependency_confidence = 0.0
            
            # Determine severity
            if dependency_confidence > 0.7:
                severity = FailureSeverity.CRITICAL
            elif dependency_confidence > 0.5:
                severity = FailureSeverity.HIGH
            elif dependency_confidence > 0.3:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            return {
                "severity": severity,
                "confidence": dependency_confidence,
                "analysis": {
                    "dependency_risks": dependency_risks,
                    "affected_systems": affected_systems,
                    "max_dependency_risk": max(dependency_risks.values()) if dependency_risks else 0.0,
                    "high_risk_systems": [k for k, v in dependency_risks.items() if v > 0.5]
                },
                "reasoning": f"Dependency failure analysis shows {dependency_confidence:.2f} confidence with {len(affected_systems)} systems at risk",
                "metadata": {
                    "analysis_type": "dependency_failure",
                    "systems_analyzed": len(affected_systems)
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Check system dependencies",
                    "Verify service connectivity",
                    "Test dependent system health",
                    "Implement dependency isolation"
                ]
            }
            
        except Exception as e:
            logger.error(f"Dependency failure analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"Dependency failure analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _performance_degradation_analysis(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze performance degradation patterns"""
        try:
            # Analyze performance-related alerts
            performance_keywords = [
                "performance", "slow", "latency", "response time", "throughput",
                "bottleneck", "queue", "backlog", "timeout", "delay"
            ]
            
            performance_alerts = [alert for alert in alerts if any(
                keyword in alert.message.lower() for keyword in performance_keywords
            )]
            
            if not performance_alerts:
                return {
                    "severity": FailureSeverity.LOW,
                    "confidence": 0.0,
                    "analysis": {"performance_alerts": 0},
                    "reasoning": "No performance-related alerts detected",
                    "metadata": {"analysis_type": "performance_degradation"},
                    "affected_systems": [],
                    "recovery_actions": []
                }
            
            # Analyze performance degradation patterns
            critical_perf_alerts = [a for a in performance_alerts if a.severity.value == "critical"]
            warning_perf_alerts = [a for a in performance_alerts if a.severity.value == "warning"]
            
            # Calculate performance degradation confidence
            perf_degradation_confidence = (
                len(critical_perf_alerts) * 0.4 +
                len(warning_perf_alerts) * 0.2 +
                len(performance_alerts) * 0.1
            ) / max(1, len(alerts))
            
            perf_degradation_confidence = min(1.0, perf_degradation_confidence)
            
            # Determine severity
            if perf_degradation_confidence > 0.6:
                severity = FailureSeverity.CRITICAL
            elif perf_degradation_confidence > 0.4:
                severity = FailureSeverity.HIGH
            elif perf_degradation_confidence > 0.2:
                severity = FailureSeverity.MEDIUM
            else:
                severity = FailureSeverity.LOW
            
            # Get affected systems
            affected_systems = list(set([alert.system for alert in performance_alerts]))
            
            return {
                "severity": severity,
                "confidence": perf_degradation_confidence,
                "analysis": {
                    "performance_alerts": len(performance_alerts),
                    "critical_performance_alerts": len(critical_perf_alerts),
                    "warning_performance_alerts": len(warning_perf_alerts),
                    "performance_indicators": [alert.message for alert in critical_perf_alerts[:3]]
                },
                "reasoning": f"Performance degradation analysis shows {perf_degradation_confidence:.2f} confidence with {len(performance_alerts)} performance-related alerts",
                "metadata": {
                    "analysis_type": "performance_degradation",
                    "performance_keywords_checked": len(performance_keywords)
                },
                "affected_systems": affected_systems,
                "recovery_actions": [
                    "Optimize system performance",
                    "Scale system resources",
                    "Check for bottlenecks",
                    "Review system configuration"
                ]
            }
            
        except Exception as e:
            logger.error(f"Performance degradation analysis failed: {e}")
            return {
                "severity": FailureSeverity.LOW,
                "confidence": 0.0,
                "analysis": {},
                "reasoning": f"Performance degradation analysis failed: {str(e)}",
                "metadata": {"error": str(e)},
                "affected_systems": [],
                "recovery_actions": []
            }
    
    def _combine_failure_results(
        self, 
        failure_results: List[FailureAnalysis], 
        alerts: List[Alert], 
        client: Client
    ) -> Dict[str, Any]:
        """Combine results from all failure analyzers"""
        
        if not failure_results:
            return self._fallback_analysis({"alerts": alerts, "client": client})
        
        # Weight analyzers by their confidence and severity
        analyzer_weights = {
            FailureType.CRITICAL: 0.25,
            FailureType.CASCADE_PROPAGATION: 0.20,
            FailureType.SYSTEM_DEGRADATION: 0.15,
            FailureType.RESOURCE_EXHAUSTION: 0.15,
            FailureType.DATABASE_FAILURE: 0.10,
            FailureType.NETWORK_FAILURE: 0.10,
            FailureType.APPLICATION_FAILURE: 0.10,
            FailureType.DEPENDENCY_FAILURE: 0.10,
            FailureType.PERFORMANCE_DEGRADATION: 0.10
        }
        
        # Calculate weighted failure analysis
        weighted_confidence = 0.0
        total_weight = 0.0
        
        failure_insights = []
        all_affected_systems = set()
        all_recovery_actions = set()
        severity_scores = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for result in failure_results:
            weight = analyzer_weights.get(result.failure_type, 0.1)
            confidence = result.confidence
            
            if confidence > 0:
                weighted_confidence += confidence * weight
                total_weight += weight
                
                # Collect insights
                failure_insights.append({
                    "failure_type": result.failure_type.value,
                    "severity": result.severity.value,
                    "confidence": confidence,
                    "reasoning": result.reasoning,
                    "execution_time_ms": result.execution_time_ms,
                    "analysis": result.analysis
                })
                
                # Collect affected systems and recovery actions
                all_affected_systems.update(result.affected_systems)
                all_recovery_actions.update(result.recovery_actions)
                
                # Count severity levels
                severity_scores[result.severity.value] += 1
        
        # Calculate final failure assessment
        if total_weight > 0:
            final_confidence = weighted_confidence / total_weight
        else:
            final_confidence = 0.0
        
        # Determine overall failure severity
        if final_confidence > 0.8 or severity_scores["critical"] > 0:
            overall_severity = "critical"
        elif final_confidence > 0.6 or severity_scores["high"] > 0:
            overall_severity = "high"
        elif final_confidence > 0.4 or severity_scores["medium"] > 0:
            overall_severity = "medium"
        else:
            overall_severity = "low"
        
        # Generate failure summary
        failure_summary = f"Cascade failure analysis detected {overall_severity} level failures with {final_confidence:.1%} confidence based on {len(failure_results)} analysis modules"
        
        return {
            "failure_detected": final_confidence > 0.3,
            "failure_confidence": round(final_confidence, 2),
            "failure_severity": overall_severity,
            "failure_summary": failure_summary,
            "affected_systems": list(all_affected_systems),
            "recovery_actions": list(all_recovery_actions),
            "failure_analysis": {
                "analyzers_executed": len(failure_results),
                "analyzers_successful": len([r for r in failure_results if r.confidence > 0]),
                "failure_insights": failure_insights,
                "execution_time_ms": sum(r.execution_time_ms for r in failure_results),
                "severity_distribution": severity_scores
            },
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzers_used": [r.failure_type.value for r in failure_results],
                "total_execution_time_ms": sum(r.execution_time_ms for r in failure_results),
                "parallel_execution": True
            }
        }
    
    def _update_agent_memory(self, alerts: List[Alert], analysis: Dict, client_id: str):
        """Update agent memory for learning"""
        failure_record = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "alerts": [{"system": a.system, "severity": a.severity.value, "category": a.category.value} for a in alerts],
            "analysis": analysis,
            "failure_detected": analysis.get("failure_detected", False),
            "failure_severity": analysis.get("failure_severity", "low"),
            "confidence": analysis.get("failure_confidence", 0.0)
        }
        
        self.failure_memory.append(failure_record)
        
        # Keep memory size manageable
        if len(self.failure_memory) > 1000:
            self.failure_memory = self.failure_memory[-800:]
    
    def _update_performance_metrics(self, failure_results: List[FailureAnalysis], start_time: datetime):
        """Update performance metrics"""
        self.performance_metrics["total_analyses"] += 1
        
        # Update failure detection metrics
        failures_detected = len([r for r in failure_results if r.confidence > 0.3])
        if failures_detected > 0:
            self.performance_metrics["failures_detected"] += 1
        
        # Update average detection time
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        current_avg = self.performance_metrics["average_detection_time_ms"]
        total_analyses = self.performance_metrics["total_analyses"]
        
        self.performance_metrics["average_detection_time_ms"] = (
            (current_avg * (total_analyses - 1) + total_time) / total_analyses
        )
    
    def _fallback_analysis(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when agent fails"""
        alerts = correlated_data.get("alerts", [])
        client = correlated_data.get("client")
        
        # Handle both Alert objects and dictionaries
        if alerts and isinstance(alerts[0], dict):
            critical_count = len([a for a in alerts if a.get("severity") == "critical"])
            avg_cascade_risk = sum(a.get("cascade_risk", 0) for a in alerts) / len(alerts) if alerts else 0
        else:
            critical_count = len([a for a in alerts if a.severity == "critical"])
            avg_cascade_risk = sum(a.cascade_risk for a in alerts) / len(alerts) if alerts else 0
        
        return {
            "failure_detected": critical_count > 0,
            "failure_confidence": min(0.7, avg_cascade_risk),
            "failure_severity": "high" if critical_count > 0 else "medium",
            "failure_summary": f"Fallback analysis: {critical_count} critical alerts detected. Manual investigation recommended.",
            "affected_systems": [],
            "recovery_actions": ["Manual investigation required", "Contact senior technician"],
            "failure_analysis": {
                "analyzers_executed": 0,
                "analyzers_successful": 0,
                "failure_insights": [],
                "execution_time_ms": 0,
                "severity_distribution": {"critical": critical_count, "high": 0, "medium": 0, "low": 0}
            },
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "fallback_mode": True
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get cascade failure agent status"""
        return {
            "agent_name": self.name,
            "agent_created": self.created_at.isoformat(),
            "max_workers": self.max_workers,
            "memory_size": len(self.failure_memory),
            "performance_metrics": self.performance_metrics,
            "failure_patterns": len(self.failure_patterns),
            "analyzers_available": [failure_type.value for failure_type in FailureType],
            "thresholds": self.thresholds,
            "status": "operational"
        }
    
    def __del__(self):
        """Cleanup thread pool"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

def create_cascade_failure_agent(max_workers: int = 8) -> CascadeFailureAgent:
    """Factory function to create CascadeFailureAgent instances"""
    return CascadeFailureAgent(max_workers=max_workers)
