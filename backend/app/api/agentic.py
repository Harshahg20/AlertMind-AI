from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import logging

from app.models.alert import Alert, Client, CascadePrediction
from app.services.agentic_ai_services import AgenticAIService
from app.services.autonomous_agent import AutonomousAgent
from app.services.prevention_executor import PreventionExecutor
from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agentic AI components
ai_service = AgenticAIService()
autonomous_agent = AutonomousAgent(ai_service)
prevention_executor = PreventionExecutor()

# Global state for agent operation
agent_running = False
agent_task = None

@router.post("/start")
async def start_autonomous_agent(background_tasks: BackgroundTasks):
    """Start the autonomous cascade prevention agent"""
    global agent_running, agent_task
    
    if agent_running:
        return {"message": "Agent is already running", "status": "running"}
    
    try:
        # Start agent in background
        agent_task = asyncio.create_task(autonomous_agent.start_autonomous_operation(MOCK_CLIENTS))
        agent_running = True
        
        logger.info("🤖 Autonomous agent started successfully")
        
        return {
            "message": "Autonomous cascade prevention agent started",
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "agent_metrics": autonomous_agent.get_agent_metrics()
        }
        
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")

@router.post("/stop")
async def stop_autonomous_agent():
    """Stop the autonomous cascade prevention agent"""
    global agent_running, agent_task
    
    if not agent_running:
        return {"message": "Agent is not running", "status": "stopped"}
    
    try:
        if agent_task:
            agent_task.cancel()
            try:
                await agent_task
            except asyncio.CancelledError:
                pass
        
        agent_running = False
        agent_task = None
        
        logger.info("🤖 Autonomous agent stopped")
        
        return {
            "message": "Autonomous cascade prevention agent stopped",
            "status": "stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")

@router.get("/status")
async def get_agent_status():
    """Get current agent status and metrics"""
    
    return {
        "agent_running": agent_running,
        "agent_metrics": autonomous_agent.get_agent_metrics(),
        "agent_insights": autonomous_agent.get_agent_insights(),
        "execution_metrics": prevention_executor.get_execution_metrics(),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/analyze")
async def analyze_cascade_risk(client_id: str, background_tasks: BackgroundTasks):
    """Trigger immediate cascade risk analysis for a specific client"""
    
    try:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get current alerts for client
        all_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_alerts if a.client_id == client_id]
        
        if not client_alerts:
            return {
                "message": "No alerts found for client",
                "client_id": client_id,
                "analysis": None
            }
        
        # Perform AI analysis
        historical_data = []  # Would be populated from actual historical data
        analysis = await ai_service.analyze_cascade_risk(client_alerts, client, historical_data)
        
        # Make autonomous decision
        decision = await autonomous_agent._make_autonomous_decision(analysis, client, client_alerts)
        
        # Execute action if required
        if decision["action_required"]:
            background_tasks.add_task(
                autonomous_agent._execute_autonomous_action, 
                decision, client, client_alerts
            )
        
        return {
            "message": "Cascade risk analysis completed",
            "client_id": client_id,
            "client_name": client.name,
            "alerts_analyzed": len(client_alerts),
            "analysis": analysis,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/prevent")
async def execute_prevention_actions(client_id: str, prevention_plan: Dict):
    """Execute prevention actions for a specific client"""
    
    try:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get current alerts
        all_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_alerts if a.client_id == client_id]
        
        # Execute prevention plan
        execution_result = await prevention_executor.execute_prevention_plan(
            prevention_plan, client, client_alerts
        )
        
        return {
            "message": "Prevention actions executed",
            "execution_result": execution_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Prevention execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prevention execution failed: {str(e)}")

@router.get("/insights")
async def get_agent_insights():
    """Get comprehensive AI agent insights and learning data"""
    
    try:
        insights = {
            "agent_insights": autonomous_agent.get_agent_insights(),
            "execution_metrics": prevention_executor.get_execution_metrics(),
            "action_templates": prevention_executor.get_action_templates(),
            "learning_data": {
                "incident_memory_size": len(ai_service.incident_memory),
                "pattern_memory_size": len(ai_service.pattern_memory),
                "client_behavior_profiles": len(ai_service.client_behavior_profiles)
            },
            "cross_client_patterns": ai_service._get_cross_client_patterns(),
            "timestamp": datetime.now().isoformat()
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@router.get("/predictions")
async def get_agent_predictions():
    """Get current cascade predictions from the AI agent"""
    
    try:
        all_alerts = generate_mock_alerts()
        all_predictions = []
        
        # Analyze each client
        for client in MOCK_CLIENTS:
            client_alerts = [a for a in all_alerts if a.client_id == client.id and a.cascade_risk > 0.5]
            
            if client_alerts:
                historical_data = []
                analysis = await ai_service.analyze_cascade_risk(client_alerts, client, historical_data)
                
                # Extract predictions
                for prediction in analysis.get("cascade_predictions", []):
                    all_predictions.append({
                        "alert_id": prediction.alert_id,
                        "client_id": prediction.client_id,
                        "client_name": client.name,
                        "prediction_confidence": prediction.prediction_confidence,
                        "predicted_cascade_systems": prediction.predicted_cascade_systems,
                        "time_to_cascade_minutes": prediction.time_to_cascade_minutes,
                        "prevention_actions": prediction.prevention_actions,
                        "pattern_matched": prediction.pattern_matched,
                        "ai_analysis": analysis.get("ai_analysis", {}),
                        "business_impact": analysis.get("business_impact", {}),
                        "recommended_actions": analysis.get("recommended_actions", [])
                    })
        
        # Sort by confidence and urgency
        all_predictions.sort(key=lambda x: x["prediction_confidence"], reverse=True)
        
        return {
            "predictions": all_predictions,
            "total_predictions": len(all_predictions),
            "high_risk_predictions": len([p for p in all_predictions if p["prediction_confidence"] > 0.7]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get predictions: {str(e)}")

@router.post("/learn")
async def trigger_agent_learning():
    """Trigger agent learning cycle to update patterns and improve performance"""
    
    try:
        # Trigger learning update
        await autonomous_agent._update_agent_learning()
        
        return {
            "message": "Agent learning cycle completed",
            "learning_cycles": autonomous_agent.learning_cycles,
            "success_rate": autonomous_agent.success_rate,
            "confidence_threshold": autonomous_agent.confidence_threshold,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Learning cycle failed: {e}")
        raise HTTPException(status_code=500, detail=f"Learning cycle failed: {str(e)}")

@router.get("/decisions")
async def get_agent_decision_history():
    """Get history of agent decisions and their outcomes"""
    
    try:
        decisions = autonomous_agent.decision_history[-50:]  # Last 50 decisions
        
        return {
            "decisions": decisions,
            "total_decisions": len(autonomous_agent.decision_history),
            "recent_decisions": len(decisions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get decision history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get decision history: {str(e)}")

@router.get("/patterns")
async def get_learned_patterns():
    """Get patterns learned by the AI agent"""
    
    try:
        patterns = autonomous_agent.pattern_recognition
        
        return {
            "patterns": patterns,
            "pattern_count": len(patterns),
            "most_common_patterns": list(patterns.keys())[:10],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

@router.post("/resolution-playbook")
async def generate_resolution_playbook(client_id: str):
    """Generate AI resolution playbook with suggestions and evidence from similar incidents"""
    try:
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        all_alerts = generate_mock_alerts()
        client_alerts = [a for a in all_alerts if a.client_id == client_id and a.severity in ["warning", "critical"]]
        if not client_alerts:
            client_alerts = [a for a in all_alerts if a.client_id == client_id]

        playbook = ai_service.generate_resolution_playbook(client_alerts[:10], client)

        return {
            "message": "Resolution playbook generated",
            "client_id": client_id,
            "client_name": client.name,
            "playbook": playbook,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate playbook: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate playbook: {str(e)}")

@router.post("/simulate-cascade")
async def simulate_cascade_scenario(scenario: Dict):
    """Simulate a cascade scenario for testing agent response"""
    
    try:
        # Create simulated alerts based on scenario
        simulated_alerts = []
        client_id = scenario.get("client_id", "client_001")
        
        # Generate alerts based on scenario type
        scenario_type = scenario.get("type", "database_cascade")
        
        if scenario_type == "database_cascade":
            simulated_alerts = [
                Alert(
                    id=f"sim_{client_id}_001",
                    client_id=client_id,
                    client_name="Simulated Client",
                    system="database",
                    severity="warning",
                    message="Database CPU usage 85%",
                    category="performance",
                    timestamp=datetime.now(),
                    cascade_risk=0.8
                ),
                Alert(
                    id=f"sim_{client_id}_002",
                    client_id=client_id,
                    client_name="Simulated Client",
                    system="web-app",
                    severity="warning",
                    message="Application response time > 10 seconds",
                    category="performance",
                    timestamp=datetime.now(),
                    cascade_risk=0.7
                )
            ]
        elif scenario_type == "network_cascade":
            simulated_alerts = [
                Alert(
                    id=f"sim_{client_id}_001",
                    client_id=client_id,
                    client_name="Simulated Client",
                    system="network-gateway",
                    severity="critical",
                    message="Packet loss 15% on WAN interface",
                    category="network",
                    timestamp=datetime.now(),
                    cascade_risk=0.9
                )
            ]
        
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Analyze with AI
        historical_data = []
        analysis = await ai_service.analyze_cascade_risk(simulated_alerts, client, historical_data)
        
        # Make decision
        decision = await autonomous_agent._make_autonomous_decision(analysis, client, simulated_alerts)
        
        return {
            "message": "Cascade scenario simulated",
            "scenario_type": scenario_type,
            "simulated_alerts": len(simulated_alerts),
            "analysis": analysis,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
