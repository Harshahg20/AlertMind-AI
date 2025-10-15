from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv

from app.models.alert import Alert, Client, AgentPrediction, CorrelatedData
from app.services.cascade_prediction_agent import create_cascade_prediction_agent
from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS

# Load environment variables
load_dotenv()

router = APIRouter()

# Initialize the Cascade Prediction Agent
def get_cascade_agent():
    """Get or create the cascade prediction agent with current environment variables"""
    if not hasattr(get_cascade_agent, '_agent'):
        AGENT_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
        get_cascade_agent._agent = create_cascade_prediction_agent(api_key=AGENT_API_KEY)
    return get_cascade_agent._agent

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
        return {
            "agent_name": get_cascade_agent().name,
            "agent_created": get_cascade_agent().created_at.isoformat(),
            "llm_available": get_cascade_agent().llm is not None,
            "memory_size": len(get_cascade_agent().incident_memory),
            "patterns_learned": len(get_cascade_agent().pattern_effectiveness),
            "cross_client_insights": get_cascade_agent()._get_cross_client_insights(),
            "agent_patterns": get_cascade_agent()._get_agent_patterns(),
            "status": "operational"
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
                "average_prediction_confidence": sum(i["confidence"] for i in get_cascade_agent().incident_memory[-20:]) / min(20, len(get_cascade_agent().incident_memory)) if get_cascade_agent().incident_memory else 0
            }
        }
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/learn")
async def update_agent_learning(incident_data: Dict):
    """
    Update agent learning with new incident data
    This would be called when prevention actions are taken and outcomes are known
    """
    try:
        # Extract learning data
        client_id = incident_data.get("client_id")
        alerts = incident_data.get("alerts", [])
        prevention_actions = incident_data.get("prevention_actions", [])
        outcome = incident_data.get("outcome", "unknown")  # "success", "failure", "partial"
        actual_cascade_time = incident_data.get("actual_cascade_time_minutes", 0)
        
        # Create learning record
        learning_record = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "alerts": alerts,
            "prevention_actions": prevention_actions,
            "outcome": outcome,
            "actual_cascade_time": actual_cascade_time,
            "learning_type": "outcome_feedback"
        }
        
        # Update agent memory
        get_cascade_agent().incident_memory.append(learning_record)
        
        # Update pattern effectiveness based on outcome
        if prevention_actions:
            pattern_key = f"{len(alerts)}_alerts_{outcome}"
            if pattern_key not in get_cascade_agent().pattern_effectiveness:
                get_cascade_agent().pattern_effectiveness[pattern_key] = []
            
            effectiveness_score = 1.0 if outcome == "success" else 0.5 if outcome == "partial" else 0.0
            get_cascade_agent().pattern_effectiveness[pattern_key].append({
                "effectiveness_score": effectiveness_score,
                "prevention_actions": prevention_actions,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "status": "learning_updated",
            "learning_record": learning_record,
            "total_incidents": len(get_cascade_agent().incident_memory),
            "patterns_learned": len(get_cascade_agent().pattern_effectiveness)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/predictions/history")
async def get_prediction_history(limit: int = 20):
    """Get history of agent predictions for analysis"""
    try:
        recent_predictions = get_cascade_agent().incident_memory[-limit:] if get_cascade_agent().incident_memory else []
        
        # Format for frontend consumption
        formatted_predictions = []
        for pred in recent_predictions:
            formatted_predictions.append({
                "timestamp": pred.get("timestamp"),
                "client_id": pred.get("client_id"),
                "confidence": pred.get("confidence", 0.0),
                "urgency": pred.get("urgency", "medium"),
                "alerts_count": len(pred.get("alerts", [])),
                "prediction_summary": pred.get("prediction", {}).get("summary", "No summary available")
            })
        
        return {
            "predictions": formatted_predictions,
            "total_count": len(get_cascade_agent().incident_memory),
            "retrieved_count": len(formatted_predictions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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