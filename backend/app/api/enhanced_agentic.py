"""
Enhanced Agentic API endpoints with comprehensive data integration
Maximizes LLM effectiveness with rich data sources and optimized analysis
"""

import os
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

from app.models.alert import Alert, Client, CorrelatedData, AgentPrediction, SeverityLevel, AlertCategory
from app.services.enhanced_cascade_prediction_agent import create_enhanced_cascade_prediction_agent
from app.services.strands_agent import create_strands_agent
from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Initialize the Enhanced Cascade Prediction Agent
def get_enhanced_cascade_agent():
    """Get or create the enhanced cascade prediction agent with current environment variables"""
    if not hasattr(get_enhanced_cascade_agent, '_agent'):
        AGENT_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
        get_enhanced_cascade_agent._agent = create_enhanced_cascade_prediction_agent(api_key=AGENT_API_KEY)
    return get_enhanced_cascade_agent._agent

# Initialize the Strands Agent
def get_strands_agent():
    """Get or create the strands agent"""
    if not hasattr(get_strands_agent, '_agent'):
        get_strands_agent._agent = create_strands_agent()
    return get_strands_agent._agent

# Mock historical data for agent learning
HISTORICAL_INCIDENTS = [
    {
        "pattern": "database_performance_cascade",
        "cascade_time_minutes": 12,
        "affected_systems": ["database", "web-app", "api-gateway"],
        "resolution_time_minutes": 45,
        "prevention_successful": True,
        "timestamp": (datetime.now() - timedelta(days=7)).isoformat()
    },
    {
        "pattern": "network_infrastructure_cascade",
        "cascade_time_minutes": 8,
        "affected_systems": ["network-gateway", "firewall"],
        "resolution_time_minutes": 20,
        "prevention_successful": False,
        "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
    },
    {
        "pattern": "storage_system_cascade",
        "cascade_time_minutes": 25,
        "affected_systems": ["storage-server", "database"],
        "resolution_time_minutes": 60,
        "prevention_successful": True,
        "timestamp": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "pattern": "memory_exhaustion_cascade",
        "cascade_time_minutes": 15,
        "affected_systems": ["web-app", "cache-server", "api-gateway"],
        "resolution_time_minutes": 30,
        "prevention_successful": True,
        "timestamp": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "pattern": "cpu_overload_cascade",
        "cascade_time_minutes": 6,
        "affected_systems": ["database", "web-app"],
        "resolution_time_minutes": 15,
        "prevention_successful": True,
        "timestamp": (datetime.now() - timedelta(days=2)).isoformat()
    }
]

@router.post("/predict/cascade/enhanced", response_model=AgentPrediction)
async def predict_cascade_enhanced(correlated_data: CorrelatedData):
    """
    Enhanced cascade prediction using comprehensive data integration
    Combines numeric prediction engine with optimized LLM reasoning
    """
    try:
        # Add mock historical data to the correlated_data for agent learning
        correlated_data.historical_data.extend(HISTORICAL_INCIDENTS)
        
        # Get enhanced agent
        agent = get_enhanced_cascade_agent()
        
        # Run enhanced prediction
        agent_result = await agent.run(correlated_data.dict())
        
        return AgentPrediction(**agent_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced agent prediction failed: {e}")

@router.post("/predict/cascade/enhanced/simple", response_model=AgentPrediction)
async def predict_cascade_enhanced_simple(
    client_id: str = Query(..., description="ID of the client"),
    alerts_data: List[Dict[str, Any]] = Body(..., description="List of alert dictionaries")
):
    """
    Enhanced cascade prediction endpoint for specific client and alerts
    """
    try:
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Convert alerts to dictionaries for the agent
        alert_dicts = []
        for alert_data in alerts_data:
            if isinstance(alert_data, dict):
                alert_dicts.append(alert_data)
            else:
                alert_dicts.append(alert_data.dict())
        
        # Prepare correlated data as dictionary
        correlated_data = {
            'alerts': alert_dicts,
            'client': client,
            'historical_data': HISTORICAL_INCIDENTS
        }
        
        # Get enhanced agent
        agent = get_enhanced_cascade_agent()
        
        # Run enhanced prediction
        agent_result = await agent.run(correlated_data)
        
        return AgentPrediction(**agent_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced agent simple prediction failed: {e}")

@router.get("/agent/enhanced/status")
async def get_enhanced_agent_status():
    """Get current status and capabilities of the Enhanced Cascade Prediction Agent"""
    try:
        agent = get_enhanced_cascade_agent()
        return agent.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced agent status: {e}")

@router.get("/agent/enhanced/insights")
async def get_enhanced_agent_insights():
    """Get insights and learning from the enhanced agent's memory"""
    try:
        agent = get_enhanced_cascade_agent()
        return {
            "total_incidents_analyzed": len(agent.incident_memory),
            "patterns_learned": len(agent.pattern_effectiveness),
            "performance_metrics": agent.performance_metrics,
            "cross_client_insights": agent._get_cross_client_insights(),
            "recent_incidents": agent.incident_memory[-5:] if agent.incident_memory else [],
            "pattern_effectiveness": agent._get_cross_client_insights().get("most_common_patterns", []),
            "enhanced_features": {
                "comprehensive_data_collection": True,
                "optimized_prompts": True,
                "rich_context_analysis": True,
                "performance_tracking": True,
                "cross_client_learning": True
            },
            "agent_learning_summary": {
                "confidence_improvement": agent._get_cross_client_insights().get("confidence_improvement", 0),
                "average_prediction_confidence": agent.performance_metrics.get("average_confidence", 0),
                "total_predictions": agent.performance_metrics.get("total_predictions", 0),
                "accuracy_rate": agent.performance_metrics.get("accurate_predictions", 0) / max(1, agent.performance_metrics.get("total_predictions", 1))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced agent insights: {e}")

@router.post("/agent/enhanced/simulate")
async def simulate_enhanced_agent_prediction(
    client_id: str = Query("client_001", description="Client ID for simulation")
):
    """Simulate enhanced agent prediction with comprehensive data analysis"""
    try:
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate mock alerts for simulation
        all_mock_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_mock_alerts if a.client_id == client_id and a.cascade_risk > 0.5]
        
        # If no high-risk alerts, create a mock critical alert
        if not client_alerts:
            mock_alert = Alert(
                id=f"enhanced_alert_{client_id}_001",
                client_id=client_id,
                client_name=client.name,
                system="database",
                severity=SeverityLevel.CRITICAL,
                message="Enhanced simulation: High CPU usage on primary database server with memory pressure.",
                category=AlertCategory.PERFORMANCE,
                timestamp=datetime.now(),
                cascade_risk=0.8
            )
            client_alerts = [mock_alert]
        
        # Select 2-3 random alerts
        import random
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
        
        # Prepare correlated data
        correlated_data = {
            'alerts': alert_dicts,
            'client': client,
            'historical_data': HISTORICAL_INCIDENTS
        }
        
        # Get enhanced agent
        agent = get_enhanced_cascade_agent()
        
        # Run enhanced prediction
        prediction = await agent.run(correlated_data)
        
        return {
            "simulation": True,
            "enhanced_analysis": True,
            "client": {"id": client.id, "name": client.name},
            "alerts_analyzed": [{"id": a.id, "system": a.system, "severity": a.severity} for a in selected_alerts],
            "prediction": prediction,
            "comprehensive_data_used": prediction.get("enhanced_analysis", {}).get("comprehensive_data_used", False),
            "system_health_score": prediction.get("enhanced_analysis", {}).get("system_health_score", 0),
            "data_sources_count": prediction.get("enhanced_analysis", {}).get("data_sources_count", 0),
            "llm_analysis_quality": prediction.get("enhanced_analysis", {}).get("llm_analysis_quality", "unknown"),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced simulation failed: {e}")

@router.get("/agent/enhanced/performance")
async def get_enhanced_agent_performance():
    """Get performance metrics for the enhanced agent"""
    try:
        agent = get_enhanced_cascade_agent()
        return {
            "performance_metrics": agent.performance_metrics,
            "memory_usage": {
                "incident_memory_size": len(agent.incident_memory),
                "pattern_effectiveness_size": len(agent.pattern_effectiveness),
                "memory_efficiency": "good" if len(agent.incident_memory) < 800 else "high"
            },
            "learning_progress": {
                "patterns_learned": len(agent.pattern_effectiveness),
                "clients_analyzed": len(set(incident["client_id"] for incident in agent.incident_memory)),
                "learning_rate": len(agent.incident_memory) / max(1, (datetime.now() - agent.created_at).days)
            },
            "enhanced_features_status": {
                "comprehensive_data_collection": True,
                "optimized_prompts": True,
                "rich_context_analysis": True,
                "performance_tracking": True,
                "cross_client_learning": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced agent performance: {e}")

@router.post("/agent/enhanced/learn")
async def update_enhanced_agent_learning(incident_data: Dict[str, Any]):
    """
    Update enhanced agent learning with new incident data
    This would be called when prevention actions are taken and outcomes are known
    """
    try:
        agent = get_enhanced_cascade_agent()
        
        # For demo, we'll just append to memory. In real-world, this would involve more complex processing
        client_id = incident_data.get("client_id", "unknown")
        alerts = incident_data.get("alerts", [])
        prediction = incident_data.get("prediction", {})
        comprehensive_data = incident_data.get("comprehensive_data", {})
        
        # Ensure alerts are in the expected format (list of dicts)
        formatted_alerts = []
        for alert_data in alerts:
            if isinstance(alert_data, dict):
                formatted_alerts.append(alert_data)
            else:
                formatted_alerts.append(alert_data.dict())
        
        # Update enhanced agent memory
        agent._update_enhanced_agent_memory(formatted_alerts, prediction, client_id, comprehensive_data)
        
        return {
            "status": "success", 
            "message": "Enhanced agent memory updated",
            "memory_size": len(agent.incident_memory),
            "patterns_learned": len(agent.pattern_effectiveness)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update enhanced agent learning: {e}")

@router.get("/agent/enhanced/predictions/history")
async def get_enhanced_prediction_history(limit: int = 10):
    """Get history of enhanced agent predictions for analysis"""
    try:
        agent = get_enhanced_cascade_agent()
        return {
            "prediction_history": agent.incident_memory[-limit:] if agent.incident_memory else [],
            "total_predictions": len(agent.incident_memory),
            "performance_summary": {
                "average_confidence": agent.performance_metrics.get("average_confidence", 0),
                "total_predictions": agent.performance_metrics.get("total_predictions", 0),
                "accuracy_rate": agent.performance_metrics.get("accurate_predictions", 0) / max(1, agent.performance_metrics.get("total_predictions", 1))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced prediction history: {e}")

@router.get("/agent/enhanced/patterns")
async def get_enhanced_learned_patterns():
    """Get patterns learned by the enhanced agent"""
    try:
        agent = get_enhanced_cascade_agent()
        return {
            "learned_patterns": agent._get_cross_client_insights().get("most_common_patterns", []),
            "pattern_effectiveness": agent.pattern_effectiveness,
            "learning_insights": {
                "total_patterns": len(agent.pattern_effectiveness),
                "most_effective_pattern": max(agent.pattern_effectiveness.items(), key=lambda x: x[1]["successful"] / max(1, x[1]["total"])) if agent.pattern_effectiveness else None,
                "learning_confidence": agent._get_cross_client_insights().get("confidence_improvement", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced learned patterns: {e}")

# Strands Agent Endpoints
@router.post("/predict/cascade/strands", response_model=AgentPrediction)
async def predict_cascade_strands(correlated_data: CorrelatedData):
    """
    Advanced cascade prediction using the strands agent
    Uses multiple parallel analysis strands for comprehensive prediction
    """
    try:
        # Add mock historical data to the correlated_data for agent learning
        correlated_data.historical_data.extend(HISTORICAL_INCIDENTS)
        
        # Get strands agent
        agent = get_strands_agent()
        
        # Run strands prediction
        agent_result = await agent.run(correlated_data.dict())
        
        return AgentPrediction(**agent_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strands agent prediction failed: {e}")

@router.post("/predict/cascade/strands/simple", response_model=AgentPrediction)
async def predict_cascade_strands_simple(
    client_id: str = Query(..., description="ID of the client"),
    alerts_data: List[Dict[str, Any]] = Body(..., description="List of alert dictionaries")
):
    """
    Strands cascade prediction endpoint for specific client and alerts
    """
    try:
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Convert alerts to dictionaries for the agent
        alert_dicts = []
        for alert_data in alerts_data:
            if isinstance(alert_data, dict):
                alert_dicts.append(alert_data)
            else:
                alert_dicts.append(alert_data.dict())
        
        # Prepare correlated data as dictionary
        correlated_data = {
            'alerts': alert_dicts,
            'client': client,
            'historical_data': HISTORICAL_INCIDENTS
        }
        
        # Get strands agent
        agent = get_strands_agent()
        
        # Run strands prediction
        agent_result = await agent.run(correlated_data)
        
        return AgentPrediction(**agent_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strands agent simple prediction failed: {e}")

@router.get("/agent/strands/status")
async def get_strands_agent_status():
    """Get current status and capabilities of the Strands Agent"""
    try:
        agent = get_strands_agent()
        return agent.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strands agent status: {e}")

@router.post("/agent/strands/simulate")
async def simulate_strands_agent_prediction(
    client_id: str = Query("client_001", description="Client ID for simulation")
):
    """Simulate strands agent prediction with multi-strand analysis"""
    try:
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate mock alerts for simulation
        all_mock_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_mock_alerts if a.client_id == client_id and a.cascade_risk > 0.4]
        
        # If no alerts, create mock alerts for demonstration
        if not client_alerts:
            mock_alerts = [
                Alert(
                    id=f"strands_alert_{client_id}_001",
                    client_id=client_id,
                    client_name=client.name,
                    system="database",
                    severity=SeverityLevel.CRITICAL,
                    message="Strands simulation: Database performance degradation detected",
                    category=AlertCategory.PERFORMANCE,
                    timestamp=datetime.now(),
                    cascade_risk=0.8
                ),
                Alert(
                    id=f"strands_alert_{client_id}_002",
                    client_id=client_id,
                    client_name=client.name,
                    system="web-app",
                    severity=SeverityLevel.WARNING,
                    message="Strands simulation: High memory usage on web application servers",
                    category=AlertCategory.SYSTEM,
                    timestamp=datetime.now() - timedelta(minutes=5),
                    cascade_risk=0.6
                )
            ]
            client_alerts = mock_alerts
        
        # Select 2-3 random alerts
        import random
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
        
        # Prepare correlated data
        correlated_data = {
            'alerts': alert_dicts,
            'client': client,
            'historical_data': HISTORICAL_INCIDENTS
        }
        
        # Get strands agent
        agent = get_strands_agent()
        
        # Run strands prediction
        prediction = await agent.run(correlated_data)
        
        return {
            "simulation": True,
            "strands_analysis": True,
            "client": {"id": client.id, "name": client.name},
            "alerts_analyzed": [{"id": a.id, "system": a.system, "severity": a.severity} for a in selected_alerts],
            "prediction": prediction,
            "strands_executed": prediction.get("strand_analysis", {}).get("strands_executed", 0),
            "strands_successful": prediction.get("strand_analysis", {}).get("strands_successful", 0),
            "execution_time_ms": prediction.get("strand_analysis", {}).get("execution_time_ms", 0),
            "average_confidence": prediction.get("strand_analysis", {}).get("average_confidence", 0),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strands simulation failed: {e}")

@router.get("/agent/strands/performance")
async def get_strands_agent_performance():
    """Get performance metrics for the strands agent"""
    try:
        agent = get_strands_agent()
        return {
            "performance_metrics": agent.performance_metrics,
            "strand_performance": agent.strand_performance,
            "memory_usage": {
                "incident_memory_size": len(agent.incident_memory),
                "pattern_effectiveness_size": len(agent.pattern_effectiveness),
                "memory_efficiency": "good" if len(agent.incident_memory) < 800 else "high"
            },
            "strands_capabilities": {
                "max_workers": agent.max_workers,
                "strands_available": [strand_type.value for strand_type in agent.strand_performance.keys()],
                "parallel_execution": True,
                "multi_factor_analysis": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strands agent performance: {e}")

@router.get("/agent/strands/insights")
async def get_strands_agent_insights():
    """Get insights and learning from the strands agent's memory"""
    try:
        agent = get_strands_agent()
        return {
            "total_analyses": agent.performance_metrics.get("total_analyses", 0),
            "successful_analyses": agent.performance_metrics.get("successful_analyses", 0),
            "average_execution_time_ms": agent.performance_metrics.get("average_execution_time_ms", 0),
            "strand_success_rates": agent.strand_performance,
            "recent_incidents": agent.incident_memory[-5:] if agent.incident_memory else [],
            "strands_effectiveness": {
                "most_reliable_strand": max(agent.strand_performance.items(), key=lambda x: x[1]["successful"] / max(1, x[1]["total"])) if agent.strand_performance else None,
                "strands_used": len(agent.strand_performance),
                "parallel_execution_benefit": True
            },
            "agent_learning_summary": {
                "total_analyses": agent.performance_metrics.get("total_analyses", 0),
                "success_rate": agent.performance_metrics.get("successful_analyses", 0) / max(1, agent.performance_metrics.get("total_analyses", 1)),
                "average_confidence": agent.performance_metrics.get("average_confidence", 0),
                "execution_efficiency": agent.performance_metrics.get("average_execution_time_ms", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strands agent insights: {e}")
