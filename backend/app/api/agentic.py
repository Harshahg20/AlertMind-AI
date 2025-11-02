from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from app.models.alert import Alert, Client, AgentPrediction, CorrelatedData
from app.services.cascade_prediction_agent import create_cascade_prediction_agent
from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS

# Load environment variables
load_dotenv()

router = APIRouter()

# Initialize the Cascade Prediction Agent
# Global agent instance to maintain state across requests
_cascade_agent = None
_training_active = False
_training_task = None

def get_cascade_agent():
    """Get or create the cascade prediction agent with current environment variables"""
    global _cascade_agent
    if _cascade_agent is None:
        AGENT_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
        _cascade_agent = create_cascade_prediction_agent(api_key=AGENT_API_KEY)
        # Initialize with some mock data to demonstrate functionality
        _cascade_agent.incident_memory = [
            {
                "timestamp": datetime.now().isoformat(),
                "client_id": "client_001",
                "alerts": [],
                "prevention_actions": ["Mock learning cycle triggered"],
                "outcome": "success",
                "actual_cascade_time": 0,
                "learning_type": "outcome_feedback",
                "confidence": 0.8
            }
        ]
        _cascade_agent.pattern_effectiveness = {
            "mock_pattern": [
                {
                    "effectiveness_score": 1.0,
                    "prevention_actions": ["Mock prevention action"],
                    "timestamp": datetime.now().isoformat(),
                    "confidence": 0.8
                }
            ]
        }
    return _cascade_agent

async def simulate_training_cycle():
    """Simulate a training cycle for the agent"""
    global _training_active, _cascade_agent
    
    while _training_active:
        try:
            # Simulate training work
            await asyncio.sleep(5)  # Training cycle every 5 seconds
            
            if _training_active and _cascade_agent:
                # Trigger learning during training
                await _cascade_agent.trigger_intelligent_learning()
                
                # Add some mock training data
                training_record = {
                    "timestamp": datetime.now().isoformat(),
                    "client_id": f"training_client_{len(_cascade_agent.incident_memory)}",
                    "alerts": [],
                    "prevention_actions": ["Training cycle completed"],
                    "outcome": "training_success",
                    "actual_cascade_time": 0,
                    "learning_type": "training_cycle",
                    "confidence": 0.7 + (len(_cascade_agent.incident_memory) * 0.01)  # Gradually improve
                }
                
                _cascade_agent.incident_memory.append(training_record)
                
                # Keep memory size manageable
                if len(_cascade_agent.incident_memory) > 100:
                    _cascade_agent.incident_memory = _cascade_agent.incident_memory[-50:]
                
                print(f"Training cycle completed. Total incidents: {len(_cascade_agent.incident_memory)}")
                
        except Exception as e:
            print(f"Training cycle error: {e}")
            await asyncio.sleep(10)  # Wait longer on error

cascade_agent = get_cascade_agent()

# Mock historical data for agent learning
HISTORICAL_INCIDENTS = [
    {
        "pattern": "database_performance_cascade",
        "cascade_time_minutes": 12,
        "affected_systems": ["database", "web-app", "api-gateway"],
        "resolution_time_minutes": 45,
        "prevention_successful": True,
        "client_tier": "enterprise"
    },
    {
        "pattern": "network_infrastructure_cascade", 
        "cascade_time_minutes": 8,
        "affected_systems": ["firewall", "load-balancer", "web-servers"],
        "resolution_time_minutes": 23,
        "prevention_successful": True,
        "client_tier": "premium"
    },
    {
        "pattern": "storage_system_cascade",
        "cascade_time_minutes": 25,
        "affected_systems": ["storage-server", "database", "backup-system"],
        "resolution_time_minutes": 67,
        "prevention_successful": False,
        "client_tier": "standard"
    }
]

@router.post("/predict/cascade", response_model=AgentPrediction)
async def predict_cascade_with_agent(correlated_data: CorrelatedData):
    """
    Enhanced cascade prediction using the Cascade Prediction Agent
    Combines numeric prediction engine with LLM reasoning
    """
    try:
        # Run the agent with correlated data
        agent = get_cascade_agent()
        agent_result = await agent.run(correlated_data.dict())
        
        # Convert to AgentPrediction model
        prediction = AgentPrediction(**agent_result)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent prediction failed: {str(e)}")

@router.post("/predict/cascade/simple")
async def predict_cascade_simple(client_id: str, alert_ids: List[str]):
    """
    Simplified cascade prediction endpoint for specific client and alerts
    """
    try:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get alerts
        all_alerts = generate_mock_alerts()
        target_alerts = [a for a in all_alerts if a.id in alert_ids and a.client_id == client_id]
        
        if not target_alerts:
            raise HTTPException(status_code=404, detail="No matching alerts found")
        
        # Convert alerts to dictionaries for the agent
        alert_dicts = []
        for alert in target_alerts:
            alert_dict = {
                'id': alert.id,
                'client_id': alert.client_id,
                'client_name': alert.client_name,
                'system': alert.system,
                'severity': alert.severity,
                'message': alert.message,
                'category': alert.category,
                'timestamp': alert.timestamp.isoformat(),
                'cascade_risk': alert.cascade_risk,
                'is_correlated': alert.is_correlated
            }
            alert_dicts.append(alert_dict)
        
        # Prepare correlated data as dictionary
        correlated_data = {
            'alerts': alert_dicts,
            'client': client,
            'historical_data': HISTORICAL_INCIDENTS
        }
        
        # Run agent prediction
        agent_result = await get_cascade_agent().run(correlated_data)
        
        return {
            "client_id": client_id,
            "alert_ids": alert_ids,
            "prediction": agent_result,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/status")
async def get_agent_status():
    """Get current status and capabilities of the Cascade Prediction Agent"""
    try:
        agent = get_cascade_agent()
        return {
            "agent_name": agent.name,
            "agent_created": agent.created_at.isoformat(),
            "llm_available": agent.llm is not None,
            "memory_size": len(agent.incident_memory),
            "patterns_learned": len(agent.pattern_effectiveness),
            "cross_client_insights": agent._get_cross_client_insights(),
            "agent_patterns": agent._get_agent_patterns(),
            "status": "operational",
            "agent_running": _training_active,  # Real training status
            "training_active": _training_active,
            "agent_metrics": {
                "total_actions_taken": len(agent.incident_memory),
                "success_rate": 85,  # Mock success rate
                "learning_cycles": len(agent.incident_memory),
                "agent_state": "active" if _training_active else "stopped",
                "confidence_threshold": 0.7,
                "risk_tolerance": 0.6,
                "active_clients": len(set(incident.get("client_id", "unknown") for incident in agent.incident_memory)),
                "patterns_learned": len(agent.pattern_effectiveness),
                "recent_decisions": len(agent.incident_memory[-10:]) if agent.incident_memory else 0
            },
            "agent_insights": {
                "agent_personality": {
                    "risk_tolerance": "moderate",
                    "learning_speed": "fast",
                    "confidence_level": "high"
                },
                "performance_analysis": {
                    "success_rate": "85%",
                    "efficiency": "high",
                    "reliability": "excellent"
                },
                "recommendations": [
                    "Continue monitoring system performance",
                    "Consider expanding pattern recognition",
                    "Maintain current confidence thresholds"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/insights")
async def get_agent_insights():
    """Get insights and learning from the agent's memory"""
    try:
        insights = {
            "total_incidents_analyzed": len(get_cascade_agent().incident_memory),
            "patterns_learned": len(get_cascade_agent().pattern_effectiveness),
            "cross_client_insights": get_cascade_agent()._get_cross_client_insights(),
            "recent_incidents": get_cascade_agent().incident_memory[-5:] if get_cascade_agent().incident_memory else [],
            "pattern_effectiveness": get_cascade_agent().pattern_effectiveness,
            "agent_learning_summary": {
                "confidence_improvement": min(0.3, len(get_cascade_agent().incident_memory) / 1000),
                "most_common_patterns": list(get_cascade_agent().pattern_effectiveness.keys())[:3],
                "average_prediction_confidence": sum(i.get("confidence", 0.5) for i in get_cascade_agent().incident_memory[-20:]) / min(20, len(get_cascade_agent().incident_memory)) if get_cascade_agent().incident_memory else 0.5
            }
        }
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/learn")
async def update_agent_learning(incident_data: Dict = None):
    """
    Update agent learning with new incident data using Gemini AI
    This triggers intelligent learning analysis using the Gemini model
    """
    try:
        # Use the new intelligent learning method
        agent = get_cascade_agent()
        learning_result = await agent.trigger_intelligent_learning()
        
        return learning_result
        
    except Exception as e:
        logger.error(f"Learning endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _format_root_causes(root_causes):
    """Format root causes as string for frontend display"""
    if isinstance(root_causes, str):
        return root_causes
    elif isinstance(root_causes, list):
        if len(root_causes) == 0:
            return "Potential cascade detected based on current alerts"
        return ". ".join(str(cause) for cause in root_causes if cause)
    else:
        return str(root_causes) if root_causes else "Potential cascade detected based on current alerts"

@router.get("/agent/predictions/history")
async def get_prediction_history(limit: int = 20):
    """Get active cascade predictions for all clients"""
    try:
        # Get current alerts
        all_alerts = generate_mock_alerts()
        
        # Filter high-risk alerts that could lead to cascades
        high_risk_alerts = [
            a for a in all_alerts 
            if a.cascade_risk > 0.5 and a.severity in ["warning", "critical"]
        ]
        
        if not high_risk_alerts:
            return {
                "predictions": [],
                "total_count": 0,
                "retrieved_count": 0
            }
        
        # Group alerts by client
        client_alerts_map = {}
        for alert in high_risk_alerts:
            if alert.client_id not in client_alerts_map:
                client_alerts_map[alert.client_id] = []
            client_alerts_map[alert.client_id].append(alert)
        
        # Generate predictions for each client with high-risk alerts
        # Limit to top clients to avoid timeout
        agent = get_cascade_agent()
        formatted_predictions = []
        
        # Process up to 5 clients at a time to avoid timeout
        clients_to_process = list(client_alerts_map.items())[:min(limit, 5)]
        
        for client_id, client_alerts in clients_to_process:
            try:
                # Find client
                client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
                if not client:
                    continue
                
                # Prepare correlated data for agent
                alert_dicts = []
                for alert in client_alerts:
                    alert_dict = {
                        'id': alert.id,
                        'client_id': alert.client_id,
                        'client_name': alert.client_name,
                        'system': alert.system,
                        'severity': alert.severity,
                        'message': alert.message,
                        'category': alert.category,
                        'timestamp': alert.timestamp.isoformat(),
                        'cascade_risk': alert.cascade_risk,
                        'is_correlated': alert.is_correlated
                    }
                    alert_dicts.append(alert_dict)
                
                correlated_data = {
                    'alerts': alert_dicts,
                    'client': client,
                    'historical_data': HISTORICAL_INCIDENTS
                }
                
                # Run agent prediction
                agent_result = await agent.run(correlated_data)
                
                # Extract predicted systems from alerts
                predicted_systems = list(set([alert.system for alert in client_alerts]))
                
                # Format for frontend
                formatted_predictions.append({
                    "client_id": client_id,
                    "client_name": client.name,
                    "confidence": agent_result.get("prediction_confidence", agent_result.get("confidence", 0.0)),
                    "prediction_confidence": agent_result.get("prediction_confidence", agent_result.get("confidence", 0.0)),
                    "time_to_cascade_minutes": agent_result.get("time_to_cascade_minutes", agent_result.get("predicted_in", 0)),
                    "predicted_in": agent_result.get("predicted_in", agent_result.get("time_to_cascade_minutes", 0)),
                    "predicted_cascade_systems": predicted_systems,
                    "ai_analysis": {
                        "root_cause_analysis": _format_root_causes(
                            agent_result.get("ai_analysis", {}).get("root_cause_analysis") or 
                            agent_result.get("root_causes", []) or
                            agent_result.get("summary", "Potential cascade detected based on current alerts")
                        ),
                        "reasoning": (
                            agent_result.get("ai_analysis", {}).get("reasoning", "") or 
                            agent_result.get("summary", "") or
                            "AI analysis based on current alert patterns and system dependencies"
                        )
                    },
                    "recommended_actions": agent_result.get("recommended_actions", []) or 
                                         agent_result.get("prevention_actions", []) or [],
                    "timestamp": datetime.now().isoformat(),
                    "alerts_count": len(client_alerts),
                    "urgency": "high" if agent_result.get("prediction_confidence", 0) > 0.7 else "medium"
                })
                
            except Exception as e:
                logger.warning(f"Failed to generate prediction for {client_id}: {e}")
                continue
        
        # Sort by confidence and urgency
        formatted_predictions.sort(
            key=lambda x: (x.get("prediction_confidence", 0), -x.get("time_to_cascade_minutes", 0)), 
            reverse=True
        )
        
        return {
            "predictions": formatted_predictions[:limit],
            "total_count": len(formatted_predictions),
            "retrieved_count": len(formatted_predictions[:limit])
        }
        
    except Exception as e:
        logger.error(f"Failed to get prediction history: {e}", exc_info=True)
        # Return empty rather than fail completely
        return {
            "predictions": [],
            "total_count": 0,
            "retrieved_count": 0,
            "error": str(e)
        }

@router.post("/agent/simulate")
async def simulate_agent_prediction():
    """
    Simulate agent prediction with mock data for testing
    """
    try:
        # Get a random client and some alerts
        import random
        client = random.choice(MOCK_CLIENTS)
        all_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_alerts if a.client_id == client.id and a.severity in ["critical", "warning"]]
        
        if not client_alerts:
            # Create a mock alert if none exist
            from app.models.alert import Alert, SeverityLevel, AlertCategory
            mock_alert = Alert(
                id="sim_001",
                client_id=client.id,
                client_name=client.name,
                system="database",
                severity=SeverityLevel.CRITICAL,
                message="CPU usage critical - 95% utilization",
                category=AlertCategory.PERFORMANCE,
                timestamp=datetime.now(),
                cascade_risk=0.8
            )
            client_alerts = [mock_alert]
        
        # Select 2-3 random alerts
        if len(client_alerts) >= 3:
            selected_alerts = random.sample(client_alerts, 3)
        elif len(client_alerts) >= 2:
            selected_alerts = random.sample(client_alerts, 2)
        else:
            selected_alerts = client_alerts
        
        # Convert alerts to dictionaries for the agent
        alert_dicts = []
        for alert in selected_alerts:
            alert_dict = {
                'id': alert.id,
                'client_id': alert.client_id,
                'client_name': alert.client_name,
                'system': alert.system,
                'severity': alert.severity,
                'message': alert.message,
                'category': alert.category,
                'timestamp': alert.timestamp.isoformat(),
                'cascade_risk': alert.cascade_risk,
                'is_correlated': alert.is_correlated
            }
            alert_dicts.append(alert_dict)
        
        # Prepare correlated data as dictionary
        correlated_data = {
            'alerts': alert_dicts,
            'client': client,
            'historical_data': HISTORICAL_INCIDENTS
        }
        
        # Run agent prediction
        agent_result = await get_cascade_agent().run(correlated_data)
        
        return {
            "simulation": True,
            "client": {"id": client.id, "name": client.name},
            "alerts_analyzed": [{"id": a.id, "system": a.system, "severity": a.severity} for a in selected_alerts],
            "prediction": agent_result,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/patterns")
async def get_learned_patterns():
    """Get patterns learned by the agent"""
    try:
        return {
            "pattern_effectiveness": get_cascade_agent().pattern_effectiveness,
            "agent_patterns": get_cascade_agent()._get_agent_patterns(),
            "cross_client_insights": get_cascade_agent()._get_cross_client_insights(),
            "total_patterns": len(get_cascade_agent().pattern_effectiveness)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy Agent Control Endpoints
@router.post("/start")
async def start_agent():
    """Start the cascade prediction agent training"""
    global _training_active, _training_task
    
    try:
        if _training_active:
            return {
                "status": "already_running",
                "message": "Agent training is already active",
                "agent_running": True,
                "started_at": datetime.now().isoformat()
            }
        
        # Start training
        _training_active = True
        _training_task = asyncio.create_task(simulate_training_cycle())
        
        return {
            "status": "success",
            "message": "Agent training started successfully",
            "agent_running": True,
            "started_at": datetime.now().isoformat(),
            "training_active": True
        }
    except Exception as e:
        _training_active = False
        if _training_task:
            _training_task.cancel()
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

@router.post("/stop")
async def stop_agent():
    """Stop the cascade prediction agent training"""
    global _training_active, _training_task
    
    try:
        if not _training_active:
            return {
                "status": "already_stopped",
                "message": "Agent training is already stopped",
                "agent_running": False,
                "stopped_at": datetime.now().isoformat()
            }
        
        # Stop training
        _training_active = False
        
        if _training_task:
            _training_task.cancel()
            try:
                await _training_task
            except asyncio.CancelledError:
                pass
            _training_task = None
        
        return {
            "status": "success",
            "message": "Agent training stopped successfully",
            "agent_running": False,
            "stopped_at": datetime.now().isoformat(),
            "training_active": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")

@router.get("/training/status")
async def get_training_status():
    """Get detailed training status"""
    global _training_active, _training_task
    
    try:
        agent = get_cascade_agent()
        
        return {
            "training_active": _training_active,
            "training_task_running": _training_task is not None and not _training_task.done(),
            "total_training_cycles": len([inc for inc in agent.incident_memory if inc.get("learning_type") == "training_cycle"]),
            "last_training_cycle": agent.incident_memory[-1].get("timestamp") if agent.incident_memory else None,
            "training_progress": {
                "incidents_processed": len(agent.incident_memory),
                "patterns_learned": len(agent.pattern_effectiveness),
                "average_confidence": sum(inc.get("confidence", 0.5) for inc in agent.incident_memory[-10:]) / min(10, len(agent.incident_memory)) if agent.incident_memory else 0.5
            },
            "status": "training" if _training_active else "stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_cascade_risk(client_id: str):
    """Analyze cascade risk for a specific client"""
    try:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get alerts for the client
        all_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_alerts if a.client_id == client_id]
        
        # Run agent analysis
        agent = get_cascade_agent()
        correlated_data = {
            'alerts': [alert.dict() for alert in client_alerts],
            'client': client,
            'historical_data': HISTORICAL_INCIDENTS
        }
        
        analysis_result = await agent.run(correlated_data)
        
        return {
            "client_id": client_id,
            "client_name": client.name,
            "analysis": analysis_result,
            "alerts_analyzed": len(client_alerts),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/prevent")
async def execute_prevention(client_id: str, prevention_plan: Dict):
    """Execute prevention actions for a client"""
    try:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # In a real implementation, this would execute actual prevention actions
        # For now, we'll simulate the execution
        actions = prevention_plan.get("actions", [])
        
        return {
            "status": "success",
            "message": f"Prevention plan executed for {client.name}",
            "client_id": client_id,
            "actions_executed": len(actions),
            "execution_time": datetime.now().isoformat(),
            "prevention_plan": prevention_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prevention execution failed: {str(e)}")

@router.get("/decisions")
async def get_agent_decisions():
    """Get recent agent decisions"""
    try:
        agent = get_cascade_agent()
        recent_decisions = agent.incident_memory[-10:] if agent.incident_memory else []
        
        return {
            "decisions": recent_decisions,
            "total_decisions": len(agent.incident_memory),
            "retrieved_count": len(recent_decisions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get decisions: {str(e)}")

@router.post("/resolution-playbook")
async def get_resolution_playbook(client_id: str):
    """Get resolution playbook for a client"""
    try:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate a mock resolution playbook
        playbook = {
            "client_id": client_id,
            "client_name": client.name,
            "playbook": {
                "database_issues": [
                    "Check connection pool status",
                    "Restart database service if needed",
                    "Scale database resources",
                    "Check for blocking queries"
                ],
                "network_issues": [
                    "Check network connectivity",
                    "Restart network services",
                    "Check firewall rules",
                    "Monitor bandwidth usage"
                ],
                "application_issues": [
                    "Check application logs",
                    "Restart application services",
                    "Check resource usage",
                    "Verify configuration"
                ],
                "storage_issues": [
                    "Check disk space",
                    "Clean up temporary files",
                    "Scale storage if needed",
                    "Check I/O performance"
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return playbook
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get playbook: {str(e)}")

# Add missing endpoints that frontend expects
@router.get("/agent/agent/status")
async def get_agent_status_legacy():
    """Legacy endpoint for agent status - matches frontend expectations"""
    return await get_agent_status()

@router.get("/agent/agent/insights")
async def get_agent_insights_legacy():
    """Legacy endpoint for agent insights - matches frontend expectations"""
    return await get_agent_insights()

@router.get("/agent/agent/predictions/history")
async def get_agent_predictions_history_legacy():
    """Legacy endpoint for agent predictions history - matches frontend expectations"""
    return await get_prediction_history()

@router.post("/agent/agent/learn")
async def trigger_agent_learning_legacy():
    """Legacy endpoint for triggering agent learning - matches frontend expectations"""
    return await update_agent_learning(None)

@router.post("/agent/agent/simulate")
async def simulate_cascade_legacy(scenario: Dict[str, Any]):
    """Legacy endpoint for cascade simulation - matches frontend expectations"""
    return await simulate_agent_prediction()