"""
Strands Agent for Advanced Alert Prediction and Analysis
Implements multi-threaded analysis with pattern recognition and predictive modeling
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

class StrandType(Enum):
    """Types of analysis strands"""
    TEMPORAL = "temporal"
    DEPENDENCY = "dependency"
    RESOURCE = "resource"
    PATTERN = "pattern"
    CROSS_CLIENT = "cross_client"
    PREDICTIVE = "predictive"

@dataclass
class StrandResult:
    """Result from a single analysis strand"""
    strand_type: StrandType
    confidence: float
    prediction: Dict[str, Any]
    reasoning: str
    metadata: Dict[str, Any]
    execution_time_ms: float

class StrandsAgent:
    """
    Advanced Strands Agent for comprehensive alert prediction analysis
    Uses multiple parallel analysis strands to provide robust predictions
    """
    
    def __init__(self, max_workers: int = 6):
        self.name = "strands_agent"
        self.created_at = datetime.now()
        self.max_workers = max_workers
        
        # Initialize prediction engine
        self.prediction_engine = CascadePredictionEngine()
        
        # Agent memory and learning
        self.incident_memory = []
        self.pattern_effectiveness = {}
        self.strand_performance = {}
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance metrics
        self.performance_metrics = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "average_execution_time_ms": 0.0,
            "strand_success_rates": {},
            "prediction_accuracy": 0.0
        }
    
    async def run(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for strands agent
        Runs multiple analysis strands in parallel and combines results
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
            
            # Define analysis strands
            strands = [
                (StrandType.TEMPORAL, self._temporal_analysis_strand),
                (StrandType.DEPENDENCY, self._dependency_analysis_strand),
                (StrandType.RESOURCE, self._resource_analysis_strand),
                (StrandType.PATTERN, self._pattern_analysis_strand),
                (StrandType.CROSS_CLIENT, self._cross_client_analysis_strand),
                (StrandType.PREDICTIVE, self._predictive_analysis_strand)
            ]
            
            # Execute strands in parallel
            strand_results = await self._execute_strands_parallel(
                strands, alert_objects, client, historical_data
            )
            
            # Combine strand results
            combined_prediction = self._combine_strand_results(
                strand_results, alert_objects, client
            )
            
            # Update agent memory and performance
            self._update_agent_memory(alert_objects, combined_prediction, client.id)
            self._update_performance_metrics(strand_results, start_time)
            
            return combined_prediction
            
        except Exception as e:
            logger.error(f"Strands Agent failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._fallback_prediction(correlated_data)
    
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
    
    async def _execute_strands_parallel(
        self, 
        strands: List[Tuple[StrandType, callable]], 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> List[StrandResult]:
        """Execute analysis strands in parallel"""
        
        # Create tasks for each strand
        tasks = []
        for strand_type, strand_func in strands:
            task = asyncio.create_task(
                self._execute_single_strand(strand_type, strand_func, alerts, client, historical_data)
            )
            tasks.append(task)
        
        # Wait for all strands to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Strand {strands[i][0].value} failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _execute_single_strand(
        self, 
        strand_type: StrandType, 
        strand_func: callable, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> StrandResult:
        """Execute a single analysis strand"""
        start_time = datetime.now()
        
        try:
            # Run strand function in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                strand_func, 
                alerts, 
                client, 
                historical_data
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return StrandResult(
                strand_type=strand_type,
                confidence=result.get("confidence", 0.0),
                prediction=result.get("prediction", {}),
                reasoning=result.get("reasoning", ""),
                metadata=result.get("metadata", {}),
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Strand {strand_type.value} execution failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return StrandResult(
                strand_type=strand_type,
                confidence=0.0,
                prediction={},
                reasoning=f"Strand failed: {str(e)}",
                metadata={"error": str(e)},
                execution_time_ms=execution_time
            )
    
    def _temporal_analysis_strand(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze temporal patterns in alerts"""
        try:
            current_time = datetime.now()
            
            # Analyze alert timing patterns
            alert_times = [alert.timestamp for alert in alerts]
            time_diffs = [(current_time - t).total_seconds() / 60 for t in alert_times]
            
            # Calculate temporal clustering
            if len(time_diffs) > 1:
                time_variance = np.var(time_diffs)
                temporal_clustering = 1.0 / (1.0 + time_variance / 60)  # Normalize to 0-1
            else:
                temporal_clustering = 0.5
            
            # Analyze severity progression
            severity_weights = {"critical": 4, "warning": 2, "info": 1, "low": 0.5}
            severity_scores = [severity_weights.get(alert.severity.value, 1) for alert in alerts]
            severity_progression = np.mean(severity_scores) / 4.0
            
            # Calculate temporal risk
            temporal_risk = (temporal_clustering * 0.6) + (severity_progression * 0.4)
            
            # Predict cascade timing based on temporal patterns
            if temporal_risk > 0.7:
                predicted_time = 8 + (temporal_clustering * 10)
                confidence = min(0.9, temporal_risk)
            elif temporal_risk > 0.5:
                predicted_time = 15 + (temporal_clustering * 15)
                confidence = temporal_risk
            else:
                predicted_time = 25
                confidence = temporal_risk * 0.8
            
            return {
                "confidence": confidence,
                "prediction": {
                    "predicted_in": int(predicted_time),
                    "temporal_risk": temporal_risk,
                    "clustering_factor": temporal_clustering,
                    "severity_progression": severity_progression
                },
                "reasoning": f"Temporal analysis shows {temporal_clustering:.2f} clustering factor and {severity_progression:.2f} severity progression",
                "metadata": {
                    "alert_count": len(alerts),
                    "time_span_minutes": max(time_diffs) - min(time_diffs) if time_diffs else 0,
                    "analysis_type": "temporal_patterns"
                }
            }
            
        except Exception as e:
            logger.error(f"Temporal analysis failed: {e}")
            return {
                "confidence": 0.0,
                "prediction": {},
                "reasoning": f"Temporal analysis failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _dependency_analysis_strand(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze system dependencies and cascade paths"""
        try:
            # Get affected systems from alerts
            affected_systems = list(set([alert.system for alert in alerts]))
            
            # Analyze dependency chains
            dependency_risk = 0.0
            cascade_paths = []
            
            for system in affected_systems:
                # Get systems that depend on this system
                dependent_systems = []
                for sys, deps in client.system_dependencies.items():
                    if system in deps:
                        dependent_systems.append(sys)
                
                # Calculate dependency risk
                if dependent_systems:
                    dependency_risk += len(dependent_systems) * 0.2
                    cascade_paths.extend(dependent_systems)
            
            # Normalize dependency risk
            dependency_risk = min(1.0, dependency_risk)
            
            # Predict cascade based on dependencies
            if dependency_risk > 0.6:
                predicted_time = 10 + (dependency_risk * 8)
                confidence = min(0.9, dependency_risk)
            elif dependency_risk > 0.3:
                predicted_time = 18 + (dependency_risk * 12)
                confidence = dependency_risk
            else:
                predicted_time = 30
                confidence = dependency_risk * 0.6
            
            return {
                "confidence": confidence,
                "prediction": {
                    "predicted_in": int(predicted_time),
                    "dependency_risk": dependency_risk,
                    "cascade_paths": list(set(cascade_paths)),
                    "affected_systems": affected_systems
                },
                "reasoning": f"Dependency analysis shows {dependency_risk:.2f} risk with {len(set(cascade_paths))} potential cascade paths",
                "metadata": {
                    "systems_analyzed": len(affected_systems),
                    "dependency_chains": len(cascade_paths),
                    "analysis_type": "dependency_analysis"
                }
            }
            
        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            return {
                "confidence": 0.0,
                "prediction": {},
                "reasoning": f"Dependency analysis failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _resource_analysis_strand(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze resource exhaustion patterns"""
        try:
            # Analyze alert categories for resource indicators
            resource_categories = {
                "performance": 0.8,
                "system": 0.6,
                "storage": 0.7,
                "network": 0.5,
                "application": 0.4
            }
            
            resource_risk = 0.0
            resource_indicators = []
            
            for alert in alerts:
                category_risk = resource_categories.get(alert.category.value, 0.3)
                severity_multiplier = {"critical": 1.0, "warning": 0.7, "info": 0.4, "low": 0.2}
                severity_factor = severity_multiplier.get(alert.severity.value, 0.3)
                
                alert_risk = category_risk * severity_factor
                resource_risk += alert_risk
                
                if alert_risk > 0.5:
                    resource_indicators.append({
                        "system": alert.system,
                        "category": alert.category.value,
                        "risk": alert_risk
                    })
            
            # Normalize resource risk
            resource_risk = min(1.0, resource_risk / len(alerts)) if alerts else 0.0
            
            # Predict cascade based on resource exhaustion
            if resource_risk > 0.7:
                predicted_time = 6 + (resource_risk * 6)
                confidence = min(0.95, resource_risk)
            elif resource_risk > 0.4:
                predicted_time = 12 + (resource_risk * 10)
                confidence = resource_risk
            else:
                predicted_time = 25
                confidence = resource_risk * 0.7
            
            return {
                "confidence": confidence,
                "prediction": {
                    "predicted_in": int(predicted_time),
                    "resource_risk": resource_risk,
                    "resource_indicators": resource_indicators,
                    "exhaustion_likelihood": resource_risk
                },
                "reasoning": f"Resource analysis shows {resource_risk:.2f} exhaustion risk with {len(resource_indicators)} critical indicators",
                "metadata": {
                    "indicators_count": len(resource_indicators),
                    "avg_risk_per_alert": resource_risk,
                    "analysis_type": "resource_exhaustion"
                }
            }
            
        except Exception as e:
            logger.error(f"Resource analysis failed: {e}")
            return {
                "confidence": 0.0,
                "prediction": {},
                "reasoning": f"Resource analysis failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _pattern_analysis_strand(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze historical patterns and match current situation"""
        try:
            # Use existing prediction engine for pattern matching
            predictions = self.prediction_engine.predict_cascade(alerts, client)
            
            if predictions:
                # Get the highest confidence prediction
                best_prediction = max(predictions, key=lambda p: p.prediction_confidence)
                
                return {
                    "confidence": best_prediction.prediction_confidence,
                    "prediction": {
                        "predicted_in": best_prediction.time_to_cascade_minutes,
                        "pattern_matched": best_prediction.pattern_matched,
                        "affected_systems": best_prediction.predicted_cascade_systems,
                        "prevention_actions": best_prediction.prevention_actions
                    },
                    "reasoning": f"Pattern analysis matched '{best_prediction.pattern_matched}' with {best_prediction.prediction_confidence:.2f} confidence",
                    "metadata": {
                        "patterns_available": len(self.prediction_engine.cascade_patterns),
                        "matched_pattern": best_prediction.pattern_matched,
                        "analysis_type": "pattern_matching"
                    }
                }
            else:
                # No pattern match found
                return {
                    "confidence": 0.3,
                    "prediction": {
                        "predicted_in": 30,
                        "pattern_matched": "no_pattern_match",
                        "affected_systems": [],
                        "prevention_actions": ["Monitor closely", "Manual investigation"]
                    },
                    "reasoning": "Pattern analysis found no matching historical patterns",
                    "metadata": {
                        "patterns_available": len(self.prediction_engine.cascade_patterns),
                        "matched_pattern": None,
                        "analysis_type": "pattern_matching"
                    }
                }
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
            return {
                "confidence": 0.0,
                "prediction": {},
                "reasoning": f"Pattern analysis failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _cross_client_analysis_strand(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze cross-client patterns and insights"""
        try:
            # Analyze historical data for similar patterns
            similar_incidents = []
            
            for incident in historical_data:
                # Check for similar alert categories and severities
                incident_categories = incident.get("alert_category", "")
                incident_severity = incident.get("severity", "")
                
                current_categories = [alert.category.value for alert in alerts]
                current_severities = [alert.severity.value for alert in alerts]
                
                # Calculate similarity
                category_match = any(cat in incident_categories for cat in current_categories)
                severity_match = any(sev in incident_severity for sev in current_severities)
                
                if category_match and severity_match:
                    similar_incidents.append(incident)
            
            # Calculate cross-client insights
            if similar_incidents:
                avg_cascade_time = np.mean([inc.get("cascade_time_minutes", 15) for inc in similar_incidents])
                avg_resolution_time = np.mean([inc.get("resolution_time_minutes", 30) for inc in similar_incidents])
                success_rate = len([inc for inc in similar_incidents if inc.get("prevention_successful", False)]) / len(similar_incidents)
                
                # Predict based on cross-client data
                predicted_time = int(avg_cascade_time)
                confidence = min(0.9, 0.5 + (len(similar_incidents) * 0.1) + (success_rate * 0.3))
                
                return {
                    "confidence": confidence,
                    "prediction": {
                        "predicted_in": predicted_time,
                        "similar_incidents": len(similar_incidents),
                        "avg_cascade_time": avg_cascade_time,
                        "success_rate": success_rate
                    },
                    "reasoning": f"Cross-client analysis found {len(similar_incidents)} similar incidents with {success_rate:.2f} success rate",
                    "metadata": {
                        "historical_incidents_analyzed": len(historical_data),
                        "similar_incidents_found": len(similar_incidents),
                        "analysis_type": "cross_client_learning"
                    }
                }
            else:
                # No similar incidents found
                return {
                    "confidence": 0.2,
                    "prediction": {
                        "predicted_in": 25,
                        "similar_incidents": 0,
                        "avg_cascade_time": 25,
                        "success_rate": 0.5
                    },
                    "reasoning": "Cross-client analysis found no similar historical incidents",
                    "metadata": {
                        "historical_incidents_analyzed": len(historical_data),
                        "similar_incidents_found": 0,
                        "analysis_type": "cross_client_learning"
                    }
                }
            
        except Exception as e:
            logger.error(f"Cross-client analysis failed: {e}")
            return {
                "confidence": 0.0,
                "prediction": {},
                "reasoning": f"Cross-client analysis failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _predictive_analysis_strand(
        self, 
        alerts: List[Alert], 
        client: Client, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Advanced predictive modeling strand"""
        try:
            # Combine multiple factors for predictive analysis
            factors = {
                "alert_density": len(alerts) / 10.0,  # Normalize to 0-1
                "severity_weight": sum({"critical": 4, "warning": 2, "info": 1, "low": 0.5}.get(a.severity.value, 1) for a in alerts) / (len(alerts) * 4),
                "system_diversity": len(set(a.system for a in alerts)) / 5.0,  # Normalize to 0-1
                "category_risk": sum({"performance": 0.8, "system": 0.6, "storage": 0.7, "network": 0.5, "application": 0.4}.get(a.category.value, 0.3) for a in alerts) / len(alerts),
                "temporal_clustering": self._calculate_temporal_clustering(alerts)
            }
            
            # Weighted prediction model
            weights = {
                "alert_density": 0.25,
                "severity_weight": 0.30,
                "system_diversity": 0.15,
                "category_risk": 0.20,
                "temporal_clustering": 0.10
            }
            
            # Calculate overall risk score
            risk_score = sum(factors[factor] * weights[factor] for factor in factors)
            risk_score = min(1.0, risk_score)
            
            # Predict cascade timing
            if risk_score > 0.8:
                predicted_time = 5 + (risk_score * 8)
                confidence = min(0.95, risk_score)
            elif risk_score > 0.6:
                predicted_time = 10 + (risk_score * 12)
                confidence = risk_score
            elif risk_score > 0.4:
                predicted_time = 18 + (risk_score * 15)
                confidence = risk_score * 0.9
            else:
                predicted_time = 30
                confidence = risk_score * 0.7
            
            return {
                "confidence": confidence,
                "prediction": {
                    "predicted_in": int(predicted_time),
                    "risk_score": risk_score,
                    "factor_analysis": factors,
                    "model_weights": weights
                },
                "reasoning": f"Predictive model shows {risk_score:.2f} risk score based on {len(factors)} factors",
                "metadata": {
                    "model_type": "multi_factor_predictive",
                    "factors_analyzed": len(factors),
                    "analysis_type": "predictive_modeling"
                }
            }
            
        except Exception as e:
            logger.error(f"Predictive analysis failed: {e}")
            return {
                "confidence": 0.0,
                "prediction": {},
                "reasoning": f"Predictive analysis failed: {str(e)}",
                "metadata": {"error": str(e)}
            }
    
    def _calculate_temporal_clustering(self, alerts: List[Alert]) -> float:
        """Calculate temporal clustering factor"""
        if len(alerts) < 2:
            return 0.5
        
        current_time = datetime.now()
        time_diffs = [(current_time - alert.timestamp).total_seconds() / 60 for alert in alerts]
        
        if len(time_diffs) > 1:
            time_variance = np.var(time_diffs)
            clustering = 1.0 / (1.0 + time_variance / 60)
            return min(1.0, clustering)
        
        return 0.5
    
    def _combine_strand_results(
        self, 
        strand_results: List[StrandResult], 
        alerts: List[Alert], 
        client: Client
    ) -> Dict[str, Any]:
        """Combine results from all analysis strands"""
        
        if not strand_results:
            return self._fallback_prediction({"alerts": alerts, "client": client})
        
        # Weight strands by their confidence and performance
        strand_weights = {
            StrandType.PATTERN: 0.25,
            StrandType.PREDICTIVE: 0.20,
            StrandType.DEPENDENCY: 0.20,
            StrandType.RESOURCE: 0.15,
            StrandType.TEMPORAL: 0.10,
            StrandType.CROSS_CLIENT: 0.10
        }
        
        # Calculate weighted predictions
        weighted_confidence = 0.0
        weighted_time = 0.0
        total_weight = 0.0
        
        strand_insights = []
        all_affected_systems = set()
        all_prevention_actions = set()
        
        for result in strand_results:
            weight = strand_weights.get(result.strand_type, 0.1)
            confidence = result.confidence
            prediction = result.prediction
            
            if confidence > 0:
                weighted_confidence += confidence * weight
                predicted_time = prediction.get("predicted_in", 20)
                weighted_time += predicted_time * weight * confidence
                total_weight += weight * confidence
                
                # Collect insights
                strand_insights.append({
                    "strand_type": result.strand_type.value,
                    "confidence": confidence,
                    "reasoning": result.reasoning,
                    "execution_time_ms": result.execution_time_ms,
                    "prediction": prediction
                })
                
                # Collect affected systems and prevention actions
                if "affected_systems" in prediction:
                    all_affected_systems.update(prediction["affected_systems"])
                if "prevention_actions" in prediction:
                    all_prevention_actions.update(prediction["prevention_actions"])
        
        # Calculate final predictions
        if total_weight > 0:
            final_confidence = weighted_confidence / total_weight
            final_time = int(weighted_time / total_weight) if total_weight > 0 else 20
        else:
            final_confidence = 0.3
            final_time = 25
        
        # Determine urgency level
        if final_confidence > 0.8 and final_time < 10:
            urgency = "critical"
        elif final_confidence > 0.6 and final_time < 20:
            urgency = "high"
        elif final_confidence > 0.4:
            urgency = "medium"
        else:
            urgency = "low"
        
        # Generate root causes from strand insights
        root_causes = []
        for insight in strand_insights:
            if insight["confidence"] > 0.6:
                root_causes.append(f"{insight['strand_type'].title()} analysis: {insight['reasoning']}")
        
        if not root_causes:
            root_causes = ["Multi-strand analysis indicates potential cascade risk"]
        
        return {
            "predicted_in": final_time,
            "confidence": round(final_confidence, 2),
            "root_causes": root_causes[:3],  # Top 3 causes
            "summary": f"Strands agent analysis predicts cascade within {final_time} minutes with {final_confidence:.1%} confidence based on {len(strand_results)} analysis strands",
            "urgency_level": urgency,
            "affected_systems": list(all_affected_systems),
            "prevention_actions": list(all_prevention_actions),
            "pattern": "strands_agent_analysis",
            "strand_analysis": {
                "strands_executed": len(strand_results),
                "strands_successful": len([r for r in strand_results if r.confidence > 0]),
                "strand_insights": strand_insights,
                "execution_time_ms": sum(r.execution_time_ms for r in strand_results),
                "average_confidence": np.mean([r.confidence for r in strand_results if r.confidence > 0]) if strand_results else 0
            },
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "strands_used": [r.strand_type.value for r in strand_results],
                "total_execution_time_ms": sum(r.execution_time_ms for r in strand_results),
                "parallel_execution": True
            }
        }
    
    def _update_agent_memory(self, alerts: List[Alert], prediction: Dict, client_id: str):
        """Update agent memory for learning"""
        incident_record = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "alerts": [{"system": a.system, "severity": a.severity.value, "category": a.category.value} for a in alerts],
            "prediction": prediction,
            "confidence": prediction.get("confidence", 0.0),
            "urgency": prediction.get("urgency_level", "medium"),
            "strands_used": prediction.get("strand_analysis", {}).get("strands_executed", 0)
        }
        
        self.incident_memory.append(incident_record)
        
        # Keep memory size manageable
        if len(self.incident_memory) > 1000:
            self.incident_memory = self.incident_memory[-800:]
    
    def _update_performance_metrics(self, strand_results: List[StrandResult], start_time: datetime):
        """Update performance metrics"""
        self.performance_metrics["total_analyses"] += 1
        
        # Update strand success rates
        for result in strand_results:
            strand_type = result.strand_type.value
            if strand_type not in self.strand_performance:
                self.strand_performance[strand_type] = {"total": 0, "successful": 0}
            
            self.strand_performance[strand_type]["total"] += 1
            if result.confidence > 0:
                self.strand_performance[strand_type]["successful"] += 1
        
        # Update average execution time
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        current_avg = self.performance_metrics["average_execution_time_ms"]
        total_analyses = self.performance_metrics["total_analyses"]
        
        self.performance_metrics["average_execution_time_ms"] = (
            (current_avg * (total_analyses - 1) + total_time) / total_analyses
        )
        
        # Update success rate
        successful_analyses = len([r for r in strand_results if r.confidence > 0])
        if successful_analyses > 0:
            self.performance_metrics["successful_analyses"] += 1
    
    def _fallback_prediction(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction when agent fails"""
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
            "predicted_in": 20,
            "confidence": min(0.7, avg_cascade_risk),
            "root_causes": ["Fallback analysis: Strands agent processing failed"],
            "summary": f"Fallback prediction: {critical_count} critical alerts detected. Manual investigation recommended.",
            "explanation": {"fallback_mode": True, "reason": "Strands agent processing failed"},
            "urgency_level": "high" if critical_count > 0 else "medium",
            "affected_systems": [],
            "prevention_actions": ["Manual investigation required", "Contact senior technician"],
            "pattern": "strands_agent_fallback",
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "fallback_mode": True
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get strands agent status"""
        return {
            "agent_name": self.name,
            "agent_created": self.created_at.isoformat(),
            "max_workers": self.max_workers,
            "memory_size": len(self.incident_memory),
            "performance_metrics": self.performance_metrics,
            "strand_performance": self.strand_performance,
            "strands_available": [strand_type.value for strand_type in StrandType],
            "status": "operational"
        }
    
    def __del__(self):
        """Cleanup thread pool"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

def create_strands_agent(max_workers: int = 6) -> StrandsAgent:
    """Factory function to create StrandsAgent instances"""
    return StrandsAgent(max_workers=max_workers)
