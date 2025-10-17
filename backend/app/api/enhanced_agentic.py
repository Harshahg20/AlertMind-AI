"""
Enhanced Agentic API endpoints with comprehensive data integration
Maximizes LLM effectiveness with rich data sources and optimized analysis
"""

import os
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from app.models.alert import Alert, Client, CorrelatedData, AgentPrediction, SeverityLevel, AlertCategory
from app.services.enhanced_cascade_prediction_agent import create_enhanced_cascade_prediction_agent
from app.services.strands_agent import create_strands_agent
from app.services.cascade_failure_agent import create_cascade_failure_agent
from app.services.learning_service import get_learning_service
from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

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

# Initialize the Cascade Failure Agent
def get_cascade_failure_agent():
    """Get or create the cascade failure agent"""
    if not hasattr(get_cascade_failure_agent, '_agent'):
        get_cascade_failure_agent._agent = create_cascade_failure_agent()
    return get_cascade_failure_agent._agent

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
        
        # Automatically trigger learning with prediction data
        try:
            learning_data = {
                "client_id": correlated_data.client.id,
                "alerts": [alert.dict() for alert in correlated_data.alerts],
                "enhanced_prediction": agent_result,
                "comprehensive_data": agent_result.get("explanation", {}).get("comprehensive_data_summary", {})
            }
            # Note: This would be called in a real system when outcomes are known
            # For now, we just prepare the learning data structure
            agent_result["learning_data_prepared"] = learning_data
        except Exception as learning_error:
            logger.warning(f"Failed to prepare learning data: {learning_error}")
        
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
        
        # Automatically trigger learning with prediction data
        try:
            learning_data = {
                "client_id": correlated_data.client.id,
                "alerts": [alert.dict() for alert in correlated_data.alerts],
                "strands_prediction": agent_result
            }
            # Note: This would be called in a real system when outcomes are known
            # For now, we just prepare the learning data structure
            agent_result["learning_data_prepared"] = learning_data
        except Exception as learning_error:
            logger.warning(f"Failed to prepare learning data: {learning_error}")
        
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

# Cascade Failure Agent Endpoints
@router.post("/analyze/cascade-failure", response_model=AgentPrediction)
async def analyze_cascade_failure(correlated_data: CorrelatedData):
    """
    Advanced cascade failure analysis using the cascade failure agent
    Uses multiple parallel failure analyzers for comprehensive failure detection
    """
    try:
        # Add mock historical data to the correlated_data for agent learning
        correlated_data.historical_data.extend(HISTORICAL_INCIDENTS)
        
        # Get cascade failure agent
        agent = get_cascade_failure_agent()
        
        # Run cascade failure analysis
        agent_result = await agent.run(correlated_data.dict())
        
        # Automatically trigger learning with analysis data
        try:
            learning_data = {
                "client_id": correlated_data.client.id,
                "alerts": [alert.dict() for alert in correlated_data.alerts],
                "failure_analysis": agent_result
            }
            # Note: This would be called in a real system when outcomes are known
            # For now, we just prepare the learning data structure
            agent_result["learning_data_prepared"] = learning_data
        except Exception as learning_error:
            logger.warning(f"Failed to prepare learning data: {learning_error}")
        
        return AgentPrediction(**agent_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cascade failure agent analysis failed: {e}")

@router.post("/analyze/cascade-failure/simple", response_model=AgentPrediction)
async def analyze_cascade_failure_simple(
    client_id: str = Query(..., description="ID of the client"),
    alerts_data: List[Dict[str, Any]] = Body(..., description="List of alert dictionaries")
):
    """
    Cascade failure analysis endpoint for specific client and alerts
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
        
        # Get cascade failure agent
        agent = get_cascade_failure_agent()
        
        # Run cascade failure analysis
        agent_result = await agent.run(correlated_data)
        
        return AgentPrediction(**agent_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cascade failure agent simple analysis failed: {e}")

@router.get("/agent/cascade-failure/status")
async def get_cascade_failure_agent_status():
    """Get current status and capabilities of the Cascade Failure Agent"""
    try:
        agent = get_cascade_failure_agent()
        return agent.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cascade failure agent status: {e}")

@router.post("/agent/cascade-failure/simulate")
async def simulate_cascade_failure_analysis(
    client_id: str = Query("client_001", description="Client ID for simulation")
):
    """Simulate cascade failure analysis with multi-analyzer detection"""
    try:
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate mock alerts for simulation
        all_mock_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_mock_alerts if a.client_id == client_id and a.cascade_risk > 0.3]
        
        # If no alerts, create mock alerts for demonstration
        if not client_alerts:
            mock_alerts = [
                Alert(
                    id=f"failure_alert_{client_id}_001",
                    client_id=client_id,
                    client_name=client.name,
                    system="database",
                    severity=SeverityLevel.CRITICAL,
                    message="Cascade failure simulation: Database connection pool exhausted",
                    category=AlertCategory.PERFORMANCE,
                    timestamp=datetime.now(),
                    cascade_risk=0.9
                ),
                Alert(
                    id=f"failure_alert_{client_id}_002",
                    client_id=client_id,
                    client_name=client.name,
                    system="web-app",
                    severity=SeverityLevel.WARNING,
                    message="Cascade failure simulation: High memory usage detected",
                    category=AlertCategory.SYSTEM,
                    timestamp=datetime.now() - timedelta(minutes=3),
                    cascade_risk=0.7
                ),
                Alert(
                    id=f"failure_alert_{client_id}_003",
                    client_id=client_id,
                    client_name=client.name,
                    system="api-gateway",
                    severity=SeverityLevel.CRITICAL,
                    message="Cascade failure simulation: API response time exceeded threshold",
                    category=AlertCategory.PERFORMANCE,
                    timestamp=datetime.now() - timedelta(minutes=1),
                    cascade_risk=0.8
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
        
        # Get cascade failure agent
        agent = get_cascade_failure_agent()
        
        # Run cascade failure analysis
        analysis = await agent.run(correlated_data)
        
        return {
            "simulation": True,
            "cascade_failure_analysis": True,
            "client": {"id": client.id, "name": client.name},
            "alerts_analyzed": [{"id": a.id, "system": a.system, "severity": a.severity} for a in selected_alerts],
            "analysis": analysis,
            "failure_detected": analysis.get("failure_detected", False),
            "failure_severity": analysis.get("failure_severity", "low"),
            "failure_confidence": analysis.get("failure_confidence", 0.0),
            "analyzers_executed": analysis.get("failure_analysis", {}).get("analyzers_executed", 0),
            "analyzers_successful": analysis.get("failure_analysis", {}).get("analyzers_successful", 0),
            "execution_time_ms": analysis.get("failure_analysis", {}).get("execution_time_ms", 0),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cascade failure simulation failed: {e}")

@router.get("/agent/cascade-failure/performance")
async def get_cascade_failure_agent_performance():
    """Get performance metrics for the cascade failure agent"""
    try:
        agent = get_cascade_failure_agent()
        return {
            "performance_metrics": agent.performance_metrics,
            "failure_patterns": len(agent.failure_patterns),
            "memory_usage": {
                "failure_memory_size": len(agent.failure_memory),
                "recovery_effectiveness_size": len(agent.recovery_effectiveness),
                "memory_efficiency": "good" if len(agent.failure_memory) < 800 else "high"
            },
            "failure_analyzers": {
                "max_workers": agent.max_workers,
                "analyzers_available": len(agent.thresholds),
                "parallel_execution": True,
                "multi_dimensional_analysis": True
            },
            "thresholds": agent.thresholds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cascade failure agent performance: {e}")

@router.get("/agent/cascade-failure/insights")
async def get_cascade_failure_agent_insights():
    """Get insights and learning from the cascade failure agent's memory"""
    try:
        agent = get_cascade_failure_agent()
        return {
            "total_analyses": agent.performance_metrics.get("total_analyses", 0),
            "failures_detected": agent.performance_metrics.get("failures_detected", 0),
            "false_positives": agent.performance_metrics.get("false_positives", 0),
            "false_negatives": agent.performance_metrics.get("false_negatives", 0),
            "average_detection_time_ms": agent.performance_metrics.get("average_detection_time_ms", 0),
            "recovery_success_rate": agent.performance_metrics.get("recovery_success_rate", 0),
            "recent_failures": agent.failure_memory[-5:] if agent.failure_memory else [],
            "failure_patterns": {
                "patterns_learned": len(agent.failure_patterns),
                "recovery_effectiveness": len(agent.recovery_effectiveness),
                "multi_analyzer_benefit": True
            },
            "agent_learning_summary": {
                "total_analyses": agent.performance_metrics.get("total_analyses", 0),
                "detection_accuracy": agent.performance_metrics.get("failures_detected", 0) / max(1, agent.performance_metrics.get("total_analyses", 1)),
                "average_detection_time": agent.performance_metrics.get("average_detection_time_ms", 0),
                "recovery_effectiveness": agent.performance_metrics.get("recovery_success_rate", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cascade failure agent insights: {e}")

# Learning Endpoints for All Agents
@router.post("/agent/strands/learn")
async def update_strands_agent_learning(incident_data: Dict[str, Any]):
    """
    Update strands agent learning with new incident data
    This would be called when prevention actions are taken and outcomes are known
    """
    try:
        agent = get_strands_agent()
        
        # Extract learning data
        client_id = incident_data.get("client_id", "unknown")
        alerts = incident_data.get("alerts", [])
        prediction = incident_data.get("prediction", {})
        outcome = incident_data.get("outcome", "unknown")  # "success", "failure", "partial"
        actual_cascade_time = incident_data.get("actual_cascade_time_minutes", 0)
        
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
        agent.incident_memory.append(learning_record)
        
        # Update strand effectiveness based on outcome
        if prediction.get("strand_analysis", {}).get("strands_executed", 0) > 0:
            effectiveness_score = 1.0 if outcome == "success" else 0.5 if outcome == "partial" else 0.0
            
            # Update each strand's effectiveness
            for strand_insight in prediction.get("strand_analysis", {}).get("strand_insights", []):
                strand_type = strand_insight.get("strand_type", "unknown")
                if strand_type not in agent.strand_performance:
                    agent.strand_performance[strand_type] = {"total": 0, "successful": 0}
                
                agent.strand_performance[strand_type]["total"] += 1
                if effectiveness_score > 0.5:
                    agent.strand_performance[strand_type]["successful"] += 1
        
        return {
            "status": "success",
            "message": "Strands agent learning updated",
            "memory_size": len(agent.incident_memory),
            "strand_performance": agent.strand_performance,
            "learning_record": learning_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update strands agent learning: {e}")

@router.post("/agent/cascade-failure/learn")
async def update_cascade_failure_agent_learning(incident_data: Dict[str, Any]):
    """
    Update cascade failure agent learning with new incident data
    This would be called when prevention actions are taken and outcomes are known
    """
    try:
        agent = get_cascade_failure_agent()
        
        # Extract learning data
        client_id = incident_data.get("client_id", "unknown")
        alerts = incident_data.get("alerts", [])
        analysis = incident_data.get("analysis", {})
        outcome = incident_data.get("outcome", "unknown")  # "success", "failure", "partial"
        recovery_actions_taken = incident_data.get("recovery_actions_taken", [])
        
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
        agent.failure_memory.append(learning_record)
        
        # Update failure pattern effectiveness based on outcome
        if analysis.get("failure_analysis", {}).get("analyzers_executed", 0) > 0:
            effectiveness_score = 1.0 if outcome == "success" else 0.5 if outcome == "partial" else 0.0
            
            # Update failure pattern effectiveness
            failure_severity = analysis.get("failure_severity", "unknown")
            pattern_key = f"{failure_severity}_failure_{outcome}"
            
            if pattern_key not in agent.failure_patterns:
                agent.failure_patterns[pattern_key] = {"total": 0, "successful": 0}
            
            agent.failure_patterns[pattern_key]["total"] += 1
            if effectiveness_score > 0.5:
                agent.failure_patterns[pattern_key]["successful"] += 1
            
            # Update recovery action effectiveness
            for action in recovery_actions_taken:
                if action not in agent.recovery_effectiveness:
                    agent.recovery_effectiveness[action] = {"total": 0, "successful": 0}
                
                agent.recovery_effectiveness[action]["total"] += 1
                if effectiveness_score > 0.5:
                    agent.recovery_effectiveness[action]["successful"] += 1
        
        return {
            "status": "success",
            "message": "Cascade failure agent learning updated",
            "memory_size": len(agent.failure_memory),
            "failure_patterns": len(agent.failure_patterns),
            "recovery_effectiveness": len(agent.recovery_effectiveness),
            "learning_record": learning_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update cascade failure agent learning: {e}")

@router.post("/agent/trigger-learning")
async def trigger_learning_for_all_agents(learning_data: Dict[str, Any]):
    """
    Trigger learning for all agents with comprehensive incident data
    This is the main learning endpoint that updates all agents
    """
    try:
        results = {}
        
        # Extract common learning data
        client_id = learning_data.get("client_id")
        alerts = learning_data.get("alerts", [])
        outcome = learning_data.get("outcome", "unknown")
        actual_cascade_time = learning_data.get("actual_cascade_time_minutes", 0)
        recovery_actions_taken = learning_data.get("recovery_actions_taken", [])
        
        if not client_id:
            raise HTTPException(status_code=400, detail="client_id is required for learning")
        
        # Update Enhanced Cascade Agent
        try:
            enhanced_agent = get_enhanced_cascade_agent()
            enhanced_learning_data = {
                "client_id": client_id,
                "alerts": alerts,
                "prediction": learning_data.get("enhanced_prediction", {}),
                "comprehensive_data": learning_data.get("comprehensive_data", {})
            }
            enhanced_result = await update_enhanced_agent_learning(enhanced_learning_data)
            results["enhanced_agent"] = enhanced_result
        except Exception as e:
            results["enhanced_agent"] = {"error": str(e)}
        
        # Update Strands Agent
        try:
            strands_learning_data = {
                "client_id": client_id,
                "alerts": alerts,
                "prediction": learning_data.get("strands_prediction", {}),
                "outcome": outcome,
                "actual_cascade_time": actual_cascade_time
            }
            strands_result = await update_strands_agent_learning(strands_learning_data)
            results["strands_agent"] = strands_result
        except Exception as e:
            results["strands_agent"] = {"error": str(e)}
        
        # Update Cascade Failure Agent
        try:
            failure_learning_data = {
                "client_id": client_id,
                "alerts": alerts,
                "analysis": learning_data.get("failure_analysis", {}),
                "outcome": outcome,
                "recovery_actions_taken": recovery_actions_taken
            }
            failure_result = await update_cascade_failure_agent_learning(failure_learning_data)
            results["cascade_failure_agent"] = failure_result
        except Exception as e:
            results["cascade_failure_agent"] = {"error": str(e)}
        
        return {
            "status": "learning_triggered",
            "message": "Learning triggered for all agents",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger learning for all agents: {e}")

@router.get("/agent/learning/status")
async def get_all_agents_learning_status():
    """Get learning status for all agents"""
    try:
        enhanced_agent = get_enhanced_cascade_agent()
        strands_agent = get_strands_agent()
        failure_agent = get_cascade_failure_agent()
        
        return {
            "enhanced_agent": {
                "memory_size": len(enhanced_agent.incident_memory),
                "patterns_learned": len(enhanced_agent.pattern_effectiveness),
                "performance_metrics": enhanced_agent.performance_metrics
            },
            "strands_agent": {
                "memory_size": len(strands_agent.incident_memory),
                "strand_performance": strands_agent.strand_performance,
                "performance_metrics": strands_agent.performance_metrics
            },
            "cascade_failure_agent": {
                "memory_size": len(failure_agent.failure_memory),
                "failure_patterns": len(failure_agent.failure_patterns),
                "recovery_effectiveness": len(failure_agent.recovery_effectiveness),
                "performance_metrics": failure_agent.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning status: {e}")

# Learning Service Endpoints
@router.post("/learning/trigger")
async def trigger_comprehensive_learning(learning_data: Dict[str, Any]):
    """
    Trigger comprehensive learning across all agents using the learning service
    This is the main endpoint for triggering learning
    """
    try:
        learning_service = get_learning_service()
        result = await learning_service.trigger_learning(learning_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger learning: {e}")

@router.get("/learning/status")
async def get_learning_service_status():
    """Get comprehensive learning service status"""
    try:
        learning_service = get_learning_service()
        return learning_service.get_learning_status()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning service status: {e}")

@router.get("/learning/analytics")
async def get_learning_analytics():
    """Get learning analytics and insights"""
    try:
        learning_service = get_learning_service()
        return learning_service.get_learning_analytics()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning analytics: {e}")

@router.post("/learning/simulate")
async def simulate_learning_scenario(
    client_id: str = Query("client_001", description="Client ID for simulation"),
    outcome: str = Query("success", description="Simulated outcome: success, failure, partial")
):
    """Simulate a learning scenario with mock data"""
    try:
        # Generate mock learning data
        mock_alerts = [
            {
                "id": f"learning_alert_{client_id}_001",
                "client_id": client_id,
                "system": "database",
                "severity": "critical",
                "message": "Learning simulation: Database performance issue",
                "category": "performance",
                "timestamp": datetime.now().isoformat(),
                "cascade_risk": 0.8
            },
            {
                "id": f"learning_alert_{client_id}_002",
                "client_id": client_id,
                "system": "web-app",
                "severity": "warning",
                "message": "Learning simulation: High memory usage",
                "category": "system",
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "cascade_risk": 0.6
            }
        ]
        
        # Create mock prediction data
        mock_enhanced_prediction = {
            "predicted_in": 15,
            "confidence": 0.8,
            "root_causes": ["Database performance degradation", "Memory pressure"],
            "summary": "Learning simulation: Cascade predicted within 15 minutes",
            "urgency_level": "high",
            "affected_systems": ["database", "web-app"],
            "prevention_actions": ["Restart database service", "Scale memory resources"]
        }
        
        mock_strands_prediction = {
            "predicted_in": 12,
            "confidence": 0.85,
            "root_causes": ["Temporal correlation detected", "Resource exhaustion pattern"],
            "summary": "Learning simulation: Strands analysis predicts cascade in 12 minutes",
            "urgency_level": "high",
            "affected_systems": ["database", "web-app", "api-gateway"],
            "prevention_actions": ["Scale database resources", "Clear memory cache"],
            "strand_analysis": {
                "strands_executed": 6,
                "strands_successful": 5,
                "strand_insights": [
                    {"strand_type": "temporal", "confidence": 0.8},
                    {"strand_type": "resource", "confidence": 0.9},
                    {"strand_type": "dependency", "confidence": 0.7}
                ]
            }
        }
        
        mock_failure_analysis = {
            "failure_detected": True,
            "failure_confidence": 0.9,
            "failure_severity": "high",
            "failure_summary": "Learning simulation: Multiple failure types detected",
            "affected_systems": ["database", "web-app"],
            "recovery_actions": ["Restart services", "Scale resources", "Check dependencies"],
            "failure_analysis": {
                "analyzers_executed": 8,
                "analyzers_successful": 7,
                "failure_insights": [
                    {"failure_type": "system_degradation", "confidence": 0.8},
                    {"failure_type": "resource_exhaustion", "confidence": 0.9},
                    {"failure_type": "database_failure", "confidence": 0.7}
                ]
            }
        }
        
        # Create comprehensive learning data
        learning_data = {
            "client_id": client_id,
            "alerts": mock_alerts,
            "enhanced_prediction": mock_enhanced_prediction,
            "strands_prediction": mock_strands_prediction,
            "failure_analysis": mock_failure_analysis,
            "outcome": outcome,
            "actual_cascade_time_minutes": 10 if outcome == "success" else 20,
            "recovery_actions_taken": ["Restart database service", "Scale memory resources"],
            "feedback_data": {
                "prevention_effective": outcome == "success",
                "response_time_minutes": 5,
                "escalation_required": outcome == "failure"
            }
        }
        
        # Trigger learning
        learning_service = get_learning_service()
        result = await learning_service.trigger_learning(learning_data)
        
        return {
            "simulation": True,
            "learning_triggered": True,
            "client_id": client_id,
            "outcome": outcome,
            "learning_result": result,
            "mock_data_used": {
                "alerts_count": len(mock_alerts),
                "enhanced_prediction": bool(mock_enhanced_prediction),
                "strands_prediction": bool(mock_strands_prediction),
                "failure_analysis": bool(mock_failure_analysis)
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning simulation failed: {e}")
