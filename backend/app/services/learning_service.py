"""
Learning Service for Agent Learning Management
Handles learning triggers, data persistence, and learning analytics across all agents
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.models.alert import Alert, Client
from app.services.enhanced_cascade_prediction_agent import create_enhanced_cascade_prediction_agent
from app.services.strands_agent import create_strands_agent
from app.services.cascade_failure_agent import create_cascade_failure_agent

logger = logging.getLogger(__name__)

@dataclass
class LearningEvent:
    """Learning event data structure"""
    event_id: str
    timestamp: datetime
    client_id: str
    event_type: str  # "prediction", "failure_detection", "prevention_outcome"
    agent_type: str  # "enhanced", "strands", "cascade_failure"
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    outcome: Optional[str] = None  # "success", "failure", "partial"
    feedback_data: Optional[Dict[str, Any]] = None

class LearningService:
    """
    Centralized learning service for managing agent learning across the system
    """
    
    def __init__(self):
        self.name = "learning_service"
        self.created_at = datetime.now()
        
        # Initialize agents
        self.enhanced_agent = create_enhanced_cascade_prediction_agent()
        self.strands_agent = create_strands_agent()
        self.cascade_failure_agent = create_cascade_failure_agent()
        
        # Learning event storage
        self.learning_events = []
        self.learning_metrics = {
            "total_events": 0,
            "successful_learnings": 0,
            "failed_learnings": 0,
            "agents_updated": 0,
            "last_learning_time": None
        }
        
        # Learning triggers
        self.learning_triggers = {
            "prediction_made": True,
            "failure_detected": True,
            "prevention_executed": True,
            "outcome_known": True
        }
    
    async def trigger_learning(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main learning trigger that updates all agents with new data
        """
        try:
            start_time = datetime.now()
            
            # Validate learning data
            if not self._validate_learning_data(learning_data):
                raise ValueError("Invalid learning data provided")
            
            # Create learning event
            learning_event = self._create_learning_event(learning_data)
            self.learning_events.append(learning_event)
            
            # Update learning metrics
            self.learning_metrics["total_events"] += 1
            self.learning_metrics["last_learning_time"] = start_time.isoformat()
            
            # Trigger learning for each agent
            results = {}
            
            # Enhanced Agent Learning
            if learning_data.get("enhanced_prediction"):
                try:
                    enhanced_result = await self._update_enhanced_agent_learning(learning_data)
                    results["enhanced_agent"] = enhanced_result
                    self.learning_metrics["agents_updated"] += 1
                except Exception as e:
                    logger.error(f"Enhanced agent learning failed: {e}")
                    results["enhanced_agent"] = {"error": str(e)}
            
            # Strands Agent Learning
            if learning_data.get("strands_prediction"):
                try:
                    strands_result = await self._update_strands_agent_learning(learning_data)
                    results["strands_agent"] = strands_result
                    self.learning_metrics["agents_updated"] += 1
                except Exception as e:
                    logger.error(f"Strands agent learning failed: {e}")
                    results["strands_agent"] = {"error": str(e)}
            
            # Cascade Failure Agent Learning
            if learning_data.get("failure_analysis"):
                try:
                    failure_result = await self._update_cascade_failure_agent_learning(learning_data)
                    results["cascade_failure_agent"] = failure_result
                    self.learning_metrics["agents_updated"] += 1
                except Exception as e:
                    logger.error(f"Cascade failure agent learning failed: {e}")
                    results["cascade_failure_agent"] = {"error": str(e)}
            
            # Update success metrics
            if all("error" not in result for result in results.values()):
                self.learning_metrics["successful_learnings"] += 1
            else:
                self.learning_metrics["failed_learnings"] += 1
            
            return {
                "status": "learning_completed",
                "learning_event_id": learning_event.event_id,
                "results": results,
                "metrics": self.learning_metrics,
                "execution_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Learning service failed: {e}")
            self.learning_metrics["failed_learnings"] += 1
            return {
                "status": "learning_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_learning_data(self, learning_data: Dict[str, Any]) -> bool:
        """Validate learning data structure"""
        required_fields = ["client_id", "alerts"]
        
        for field in required_fields:
            if field not in learning_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Check if at least one agent data is provided
        agent_data_fields = ["enhanced_prediction", "strands_prediction", "failure_analysis"]
        if not any(field in learning_data for field in agent_data_fields):
            logger.error("No agent data provided for learning")
            return False
        
        return True
    
    def _create_learning_event(self, learning_data: Dict[str, Any]) -> LearningEvent:
        """Create a learning event record"""
        event_id = f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.learning_events)}"
        
        # Determine event type
        if learning_data.get("outcome"):
            event_type = "prevention_outcome"
        elif learning_data.get("failure_analysis"):
            event_type = "failure_detection"
        else:
            event_type = "prediction"
        
        # Determine agent type
        if learning_data.get("enhanced_prediction"):
            agent_type = "enhanced"
        elif learning_data.get("strands_prediction"):
            agent_type = "strands"
        elif learning_data.get("failure_analysis"):
            agent_type = "cascade_failure"
        else:
            agent_type = "unknown"
        
        return LearningEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            client_id=learning_data.get("client_id", "unknown"),
            event_type=event_type,
            agent_type=agent_type,
            input_data=learning_data,
            output_data={},  # Will be populated after learning
            outcome=learning_data.get("outcome"),
            feedback_data=learning_data.get("feedback_data")
        )
    
    async def _update_enhanced_agent_learning(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update enhanced agent learning"""
        try:
            client_id = learning_data.get("client_id")
            alerts = learning_data.get("alerts", [])
            prediction = learning_data.get("enhanced_prediction", {})
            comprehensive_data = learning_data.get("comprehensive_data", {})
            
            # Ensure alerts are in the expected format
            formatted_alerts = []
            for alert_data in alerts:
                if isinstance(alert_data, dict):
                    formatted_alerts.append(alert_data)
                else:
                    formatted_alerts.append(alert_data.dict())
            
            # Update enhanced agent memory
            self.enhanced_agent._update_enhanced_agent_memory(
                formatted_alerts, prediction, client_id, comprehensive_data
            )
            
            return {
                "status": "success",
                "message": "Enhanced agent learning updated",
                "memory_size": len(self.enhanced_agent.incident_memory),
                "patterns_learned": len(self.enhanced_agent.pattern_effectiveness)
            }
            
        except Exception as e:
            logger.error(f"Enhanced agent learning update failed: {e}")
            raise
    
    async def _update_strands_agent_learning(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update strands agent learning"""
        try:
            client_id = learning_data.get("client_id")
            alerts = learning_data.get("alerts", [])
            prediction = learning_data.get("strands_prediction", {})
            outcome = learning_data.get("outcome", "unknown")
            actual_cascade_time = learning_data.get("actual_cascade_time_minutes", 0)
            
            # Ensure alerts are in the expected format
            formatted_alerts = []
            for alert_data in alerts:
                if isinstance(alert_data, dict):
                    formatted_alerts.append(alert_data)
                else:
                    formatted_alerts.append(alert_data.dict())
            
            # Create learning record
            learning_record = {
                "timestamp": datetime.now().isoformat(),
                "client_id": client_id,
                "alerts": formatted_alerts,
                "prediction": prediction,
                "outcome": outcome,
                "actual_cascade_time": actual_cascade_time,
                "learning_type": "outcome_feedback",
                "strands_used": prediction.get("strand_analysis", {}).get("strands_executed", 0)
            }
            
            # Update agent memory
            self.strands_agent.incident_memory.append(learning_record)
            
            # Update strand effectiveness based on outcome
            if prediction.get("strand_analysis", {}).get("strands_executed", 0) > 0:
                effectiveness_score = 1.0 if outcome == "success" else 0.5 if outcome == "partial" else 0.0
                
                # Update each strand's effectiveness
                for strand_insight in prediction.get("strand_analysis", {}).get("strand_insights", []):
                    strand_type = strand_insight.get("strand_type", "unknown")
                    if strand_type not in self.strands_agent.strand_performance:
                        self.strands_agent.strand_performance[strand_type] = {"total": 0, "successful": 0}
                    
                    self.strands_agent.strand_performance[strand_type]["total"] += 1
                    if effectiveness_score > 0.5:
                        self.strands_agent.strand_performance[strand_type]["successful"] += 1
            
            return {
                "status": "success",
                "message": "Strands agent learning updated",
                "memory_size": len(self.strands_agent.incident_memory),
                "strand_performance": self.strands_agent.strand_performance
            }
            
        except Exception as e:
            logger.error(f"Strands agent learning update failed: {e}")
            raise
    
    async def _update_cascade_failure_agent_learning(self, learning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update cascade failure agent learning"""
        try:
            client_id = learning_data.get("client_id")
            alerts = learning_data.get("alerts", [])
            analysis = learning_data.get("failure_analysis", {})
            outcome = learning_data.get("outcome", "unknown")
            recovery_actions_taken = learning_data.get("recovery_actions_taken", [])
            
            # Ensure alerts are in the expected format
            formatted_alerts = []
            for alert_data in alerts:
                if isinstance(alert_data, dict):
                    formatted_alerts.append(alert_data)
                else:
                    formatted_alerts.append(alert_data.dict())
            
            # Create learning record
            learning_record = {
                "timestamp": datetime.now().isoformat(),
                "client_id": client_id,
                "alerts": formatted_alerts,
                "analysis": analysis,
                "outcome": outcome,
                "recovery_actions_taken": recovery_actions_taken,
                "learning_type": "failure_recovery_feedback",
                "analyzers_used": analysis.get("failure_analysis", {}).get("analyzers_executed", 0)
            }
            
            # Update agent memory
            self.cascade_failure_agent.failure_memory.append(learning_record)
            
            # Update failure pattern effectiveness based on outcome
            if analysis.get("failure_analysis", {}).get("analyzers_executed", 0) > 0:
                effectiveness_score = 1.0 if outcome == "success" else 0.5 if outcome == "partial" else 0.0
                
                # Update failure pattern effectiveness
                failure_severity = analysis.get("failure_severity", "unknown")
                pattern_key = f"{failure_severity}_failure_{outcome}"
                
                if pattern_key not in self.cascade_failure_agent.failure_patterns:
                    self.cascade_failure_agent.failure_patterns[pattern_key] = {"total": 0, "successful": 0}
                
                self.cascade_failure_agent.failure_patterns[pattern_key]["total"] += 1
                if effectiveness_score > 0.5:
                    self.cascade_failure_agent.failure_patterns[pattern_key]["successful"] += 1
                
                # Update recovery action effectiveness
                for action in recovery_actions_taken:
                    if action not in self.cascade_failure_agent.recovery_effectiveness:
                        self.cascade_failure_agent.recovery_effectiveness[action] = {"total": 0, "successful": 0}
                    
                    self.cascade_failure_agent.recovery_effectiveness[action]["total"] += 1
                    if effectiveness_score > 0.5:
                        self.cascade_failure_agent.recovery_effectiveness[action]["successful"] += 1
            
            return {
                "status": "success",
                "message": "Cascade failure agent learning updated",
                "memory_size": len(self.cascade_failure_agent.failure_memory),
                "failure_patterns": len(self.cascade_failure_agent.failure_patterns),
                "recovery_effectiveness": len(self.cascade_failure_agent.recovery_effectiveness)
            }
            
        except Exception as e:
            logger.error(f"Cascade failure agent learning update failed: {e}")
            raise
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get comprehensive learning status for all agents"""
        return {
            "learning_service": {
                "name": self.name,
                "created_at": self.created_at.isoformat(),
                "learning_metrics": self.learning_metrics,
                "learning_triggers": self.learning_triggers,
                "total_events": len(self.learning_events)
            },
            "enhanced_agent": {
                "memory_size": len(self.enhanced_agent.incident_memory),
                "patterns_learned": len(self.enhanced_agent.pattern_effectiveness),
                "performance_metrics": self.enhanced_agent.performance_metrics
            },
            "strands_agent": {
                "memory_size": len(self.strands_agent.incident_memory),
                "strand_performance": self.strands_agent.strand_performance,
                "performance_metrics": self.strands_agent.performance_metrics
            },
            "cascade_failure_agent": {
                "memory_size": len(self.cascade_failure_agent.failure_memory),
                "failure_patterns": len(self.cascade_failure_agent.failure_patterns),
                "recovery_effectiveness": len(self.cascade_failure_agent.recovery_effectiveness),
                "performance_metrics": self.cascade_failure_agent.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """Get learning analytics and insights"""
        try:
            # Analyze learning events
            recent_events = [e for e in self.learning_events if 
                           (datetime.now() - e.timestamp).total_seconds() < 86400]  # Last 24 hours
            
            # Calculate learning trends
            learning_trends = {
                "events_last_24h": len(recent_events),
                "success_rate": self.learning_metrics["successful_learnings"] / max(1, self.learning_metrics["total_events"]),
                "agents_updated": self.learning_metrics["agents_updated"],
                "last_learning": self.learning_metrics["last_learning_time"]
            }
            
            # Analyze agent performance
            agent_performance = {
                "enhanced_agent": {
                    "memory_utilization": len(self.enhanced_agent.incident_memory) / 1000,
                    "pattern_learning_rate": len(self.enhanced_agent.pattern_effectiveness),
                    "average_confidence": self.enhanced_agent.performance_metrics.get("average_confidence", 0)
                },
                "strands_agent": {
                    "memory_utilization": len(self.strands_agent.incident_memory) / 1000,
                    "strand_effectiveness": len(self.strands_agent.strand_performance),
                    "total_analyses": self.strands_agent.performance_metrics.get("total_analyses", 0)
                },
                "cascade_failure_agent": {
                    "memory_utilization": len(self.cascade_failure_agent.failure_memory) / 1000,
                    "failure_patterns_learned": len(self.cascade_failure_agent.failure_patterns),
                    "recovery_actions_learned": len(self.cascade_failure_agent.recovery_effectiveness)
                }
            }
            
            return {
                "learning_trends": learning_trends,
                "agent_performance": agent_performance,
                "learning_effectiveness": {
                    "total_learning_events": len(self.learning_events),
                    "successful_learnings": self.learning_metrics["successful_learnings"],
                    "failed_learnings": self.learning_metrics["failed_learnings"],
                    "learning_success_rate": learning_trends["success_rate"]
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate learning analytics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global learning service instance
learning_service = LearningService()

def get_learning_service() -> LearningService:
    """Get the global learning service instance"""
    return learning_service
