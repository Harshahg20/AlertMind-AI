from fastapi import APIRouter, HTTPException
from typing import List, Dict
from datetime import datetime
import random

from app.models.alert import Alert, CascadePrediction, CorrelatedData
from app.services.cascade_prediction import CascadePredictionEngine
from app.services.cascade_prediction_agent import create_cascade_prediction_agent
from app.services.strands_agent import create_strands_agent
from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS

router = APIRouter()

# Initialize prediction engine and agents
prediction_engine = CascadePredictionEngine()
cascade_agent = create_cascade_prediction_agent()
strands_agent = create_strands_agent()

# Mock historical patterns for cross-client learning
HISTORICAL_PATTERNS = [
    {
        "client_id": "client_001",
        "alert_category": "performance",
        "severity": "warning",
        "cascade_time_minutes": 12,
        "affected_systems": ["web-app", "database", "api-gateway"],
        "resolution_time_minutes": 45,
        "pattern": "database_performance_cascade"
    },
    {
        "client_id": "client_002", 
        "alert_category": "performance",
        "severity": "critical",
        "cascade_time_minutes": 8,
        "affected_systems": ["trading-platform", "risk-engine"],
        "resolution_time_minutes": 23,
        "pattern": "database_performance_cascade"
    },
    {
        "client_id": "client_003",
        "alert_category": "storage",
        "severity": "warning", 
        "cascade_time_minutes": 25,
        "affected_systems": ["imaging-server", "database", "backup-system"],
        "resolution_time_minutes": 67,
        "pattern": "storage_system_cascade"
    },
    {
        "client_id": "client_001",
        "alert_category": "network",
        "severity": "warning",
        "cascade_time_minutes": 6,
        "affected_systems": ["firewall", "load-balancer", "web-app"],
        "resolution_time_minutes": 18,
        "pattern": "network_infrastructure_cascade"
    },
    {
        "client_id": "client_002",
        "alert_category": "system",
        "severity": "critical",
        "cascade_time_minutes": 15,
        "affected_systems": ["backup-system", "database"],
        "resolution_time_minutes": 89,
        "pattern": "storage_system_cascade"
    }
]

@router.get("/", response_model=List[CascadePrediction])
async def get_all_predictions():
    """Get cascade predictions for all current alerts"""
    try:
        # Get current alerts
        all_alerts = generate_mock_alerts()
        
        # Filter to high-risk alerts only
        high_risk_alerts = [a for a in all_alerts if a.cascade_risk > 0.6 and a.severity in ["warning", "critical"]]
        
        all_predictions = []
        
        # Generate predictions for each client
        for client in MOCK_CLIENTS:
            client_alerts = [a for a in high_risk_alerts if a.client_id == client.id]
            if client_alerts:
                predictions = prediction_engine.predict_cascade(client_alerts, client)
                all_predictions.extend(predictions)
        
        # Sort by confidence and time to cascade
        all_predictions.sort(key=lambda x: (x.prediction_confidence, -x.time_to_cascade_minutes), reverse=True)
        
        return all_predictions[:10]  # Return top 10 predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/client/{client_id}", response_model=List[CascadePrediction])
async def get_client_predictions(client_id: str):
    """Get cascade predictions for specific client - DYNAMIC with AI-generated data"""
    try:
        from app.services.data_generator import data_generator
        import uuid
        
        # Find client
        client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate dynamic predictions using the data generator
        # This will create different predictions on each refresh
        dynamic_predictions = data_generator.generate_client_predictions(client_id)
        
        # Convert to CascadePrediction objects
        predictions = []
        for pred_data in dynamic_predictions:
            prediction = CascadePrediction(
                alert_id=f"alert_{uuid.uuid4().hex[:8]}",  # Generate unique alert ID
                client_id=client_id,
                pattern_matched=pred_data["pattern"],
                affected_systems=pred_data.get("affected_systems", []),
                predicted_cascade_systems=pred_data["predicted_cascade_systems"],
                time_to_cascade_minutes=pred_data["time_to_cascade_minutes"],
                resolution_time_minutes=pred_data["resolution_time_minutes"],
                prediction_confidence=pred_data["prediction_confidence"],
                prevention_actions=[
                    f"Scale {pred_data['root_cause']} resources",
                    "Enable automated failover",
                    "Increase monitoring frequency",
                    "Prepare rollback plan"
                ]
            )
            predictions.append(prediction)
        
        return sorted(predictions, key=lambda x: x.prediction_confidence, reverse=True)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/high-risk")
async def get_high_risk_predictions():
    """Get only high-confidence cascade predictions requiring immediate attention"""
    try:
        all_alerts = generate_mock_alerts()
        critical_alerts = [a for a in all_alerts if a.severity == "critical" or a.cascade_risk > 0.8]
        
        urgent_predictions = []
        
        for client in MOCK_CLIENTS:
            client_alerts = [a for a in critical_alerts if a.client_id == client.id]
            if client_alerts:
                predictions = prediction_engine.predict_cascade(client_alerts, client)
                # Filter for high confidence and short time windows
                urgent = [p for p in predictions if p.prediction_confidence > 0.7 and p.time_to_cascade_minutes < 20]
                urgent_predictions.extend(urgent)
        
        # Sort by urgency (confidence * inverse time)
        urgent_predictions.sort(key=lambda x: x.prediction_confidence * (1 / max(x.time_to_cascade_minutes, 1)), reverse=True)
        
        return {
            "urgent_predictions": urgent_predictions[:5],
            "total_high_risk_alerts": len(critical_alerts),
            "immediate_action_required": len([p for p in urgent_predictions if p.time_to_cascade_minutes < 10]),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cross-client-insights")
async def get_cross_client_insights():
    """Analyze patterns across all clients for better predictions"""
    try:
        all_alerts = generate_mock_alerts()
        
        insights = {
            "total_clients_analyzed": len(MOCK_CLIENTS),
            "historical_patterns_count": len(HISTORICAL_PATTERNS),
            "client_insights": {},
            "pattern_analysis": {},
            "recommendations": []
        }
        
        # Analyze each client's current situation against historical patterns
        for client in MOCK_CLIENTS:
            client_alerts = [a for a in all_alerts if a.client_id == client.id and a.severity in ["warning", "critical"]]
            
            if client_alerts:
                # Get cross-client insights for each critical alert
                client_insight = {"alerts_analyzed": len(client_alerts), "similar_patterns": []}
                
                for alert in client_alerts[:3]:  # Analyze top 3 alerts
                    cross_insight = prediction_engine.get_cross_client_insights(alert, HISTORICAL_PATTERNS)
                    if cross_insight["similar_incidents_count"] > 0:
                        client_insight["similar_patterns"].append({
                            "alert_system": alert.system,
                            "alert_category": alert.category,
                            "similar_incidents": cross_insight["similar_incidents_count"],
                            "average_cascade_time": cross_insight["average_cascade_time"],
                            "confidence": cross_insight["confidence"]
                        })
                
                insights["client_insights"][client.name] = client_insight
        
        # Pattern analysis across all clients
        pattern_counts = {}
        for pattern in HISTORICAL_PATTERNS:
            pattern_type = pattern["pattern"]
            if pattern_type not in pattern_counts:
                pattern_counts[pattern_type] = {
                    "occurrences": 0,
                    "avg_cascade_time": 0,
                    "avg_resolution_time": 0,
                    "severity_distribution": {}
                }
            
            pattern_counts[pattern_type]["occurrences"] += 1
            pattern_counts[pattern_type]["avg_cascade_time"] += pattern["cascade_time_minutes"]
            pattern_counts[pattern_type]["avg_resolution_time"] += pattern["resolution_time_minutes"]
            
            severity = pattern["severity"]
            pattern_counts[pattern_type]["severity_distribution"][severity] = \
                pattern_counts[pattern_type]["severity_distribution"].get(severity, 0) + 1
        
        # Calculate averages
        for pattern_type, data in pattern_counts.items():
            count = data["occurrences"]
            data["avg_cascade_time"] = round(data["avg_cascade_time"] / count, 1)
            data["avg_resolution_time"] = round(data["avg_resolution_time"] / count, 1)
        
        insights["pattern_analysis"] = pattern_counts
        
        # Generate recommendations
        insights["recommendations"] = [
            "Database performance issues show highest cascade risk - monitor CPU and memory closely",
            "Network cascades happen fastest (avg 6-8 minutes) - implement automated failover",
            "Storage issues take longest to resolve - proactive disk space monitoring recommended",
            f"Cross-client pattern learning shows {len(HISTORICAL_PATTERNS)} similar incidents - confidence increasing"
        ]
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cascade-timeline/{alert_id}")
async def get_cascade_timeline(alert_id: str):
    """Get detailed cascade timeline prediction for specific alert"""
    try:
        all_alerts = generate_mock_alerts()
        target_alert = next((a for a in all_alerts if a.id == alert_id), None)
        
        if not target_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        client = next((c for c in MOCK_CLIENTS if c.id == target_alert.client_id), None)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate detailed cascade prediction
        predictions = prediction_engine.predict_cascade([target_alert], client)
        
        if not predictions:
            return {
                "alert_id": alert_id,
                "cascade_predicted": False,
                "reason": "Alert does not match known cascade patterns"
            }
        
        prediction = predictions[0]
        
        # Generate timeline events
        timeline_events = []
        current_time = datetime.now()
        
        # Current alert
        timeline_events.append({
            "time_offset_minutes": 0,
            "event": f"Alert triggered: {target_alert.message}",
            "system": target_alert.system,
            "severity": target_alert.severity,
            "status": "current"
        })
        
        # Predicted cascade events
        for i, system in enumerate(prediction.predicted_cascade_systems):
            time_offset = prediction.time_to_cascade_minutes + (i * 3)
            timeline_events.append({
                "time_offset_minutes": time_offset,
                "event": f"Predicted impact on {system}",
                "system": system,
                "severity": "warning" if i == 0 else "critical",
                "status": "predicted",
                "confidence": max(0.6, prediction.prediction_confidence - (i * 0.1))
            })
        
        return {
            "alert_id": alert_id,
            "cascade_predicted": True,
            "pattern_matched": prediction.pattern_matched,
            "overall_confidence": prediction.prediction_confidence,
            "timeline_events": timeline_events,
            "prevention_actions": prediction.prevention_actions,
            "estimated_total_impact_minutes": prediction.time_to_cascade_minutes + (len(prediction.predicted_cascade_systems) * 3),
            "cross_client_insight": prediction_engine.get_cross_client_insights(target_alert, HISTORICAL_PATTERNS)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-prevention")
async def simulate_prevention_impact(alert_id: str, prevention_action: str):
    """Simulate the impact of taking a prevention action"""
    try:
        # This would integrate with actual systems in production
        # For demo, we'll simulate the outcome
        
        prevention_outcomes = {
            "Restart database service": {
                "success_probability": 0.85,
                "time_to_execute_minutes": 2,
                "cascade_risk_reduction": 0.7,
                "potential_downtime_minutes": 1
            },
            "Scale database resources": {
                "success_probability": 0.92,
                "time_to_execute_minutes": 5,
                "cascade_risk_reduction": 0.8,
                "potential_downtime_minutes": 0
            },
            "Restart network services": {
                "success_probability": 0.78,
                "time_to_execute_minutes": 3,
                "cascade_risk_reduction": 0.6,
                "potential_downtime_minutes": 2
            },
            "Clear connection pool": {
                "success_probability": 0.90,
                "time_to_execute_minutes": 1,
                "cascade_risk_reduction": 0.5,
                "potential_downtime_minutes": 0
            }
        }
        
        outcome = prevention_outcomes.get(prevention_action, {
            "success_probability": 0.70,
            "time_to_execute_minutes": 5,
            "cascade_risk_reduction": 0.4,
            "potential_downtime_minutes": 1
        })
        
        # Add some randomization for realism
        actual_success = random.random() < outcome["success_probability"]
        
        return {
            "alert_id": alert_id,
            "prevention_action": prevention_action,
            "simulation_result": {
                "predicted_success": actual_success,
                "success_probability": outcome["success_probability"],
                "execution_time_minutes": outcome["time_to_execute_minutes"],
                "cascade_risk_reduction": outcome["cascade_risk_reduction"] if actual_success else 0.1,
                "estimated_downtime_minutes": outcome["potential_downtime_minutes"],
                "recommendation": "Execute immediately" if actual_success and outcome["cascade_risk_reduction"] > 0.6 else "Consider alternative action",
                "simulated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent-enhanced")
async def get_agent_enhanced_predictions(client_id: str = None):
    """Get cascade predictions enhanced with AI agent reasoning"""
    try:
        # Get current alerts
        all_alerts = generate_mock_alerts()
        
        if client_id:
            # Get predictions for specific client
            client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")
            
            client_alerts = [a for a in all_alerts if a.client_id == client_id and a.cascade_risk > 0.5]
            if not client_alerts:
                return {"client_id": client_id, "predictions": [], "message": "No high-risk alerts found"}
            
            # Prepare correlated data for agent
            correlated_data = CorrelatedData(
                alerts=client_alerts,
                client=client,
                historical_data=HISTORICAL_PATTERNS
            )
            
            # Run agent prediction
            agent_result = await cascade_agent.run(correlated_data.dict())
            
            return {
                "client_id": client_id,
                "client_name": client.name,
                "agent_prediction": agent_result,
                "alerts_analyzed": len(client_alerts),
                "generated_at": datetime.now().isoformat()
            }
        else:
            # Get predictions for all clients
            all_predictions = []
            
            for client in MOCK_CLIENTS:
                client_alerts = [a for a in all_alerts if a.client_id == client.id and a.cascade_risk > 0.6]
                if client_alerts:
                    correlated_data = CorrelatedData(
                        alerts=client_alerts,
                        client=client,
                        historical_data=HISTORICAL_PATTERNS
                    )
                    
                    agent_result = await cascade_agent.run(correlated_data.dict())
                    all_predictions.append({
                        "client_id": client.id,
                        "client_name": client.name,
                        "prediction": agent_result
                    })
            
            return {
                "total_clients_analyzed": len(all_predictions),
                "predictions": all_predictions,
                "generated_at": datetime.now().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strands-agent")
async def get_strands_agent_predictions(client_id: str = None):
    """Get cascade predictions using the advanced strands agent"""
    try:
        # Get current alerts
        all_alerts = generate_mock_alerts()
        
        if client_id:
            # Get predictions for specific client
            client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")
            
            client_alerts = [a for a in all_alerts if a.client_id == client_id and a.cascade_risk > 0.4]
            if not client_alerts:
                return {"client_id": client_id, "predictions": [], "message": "No alerts found for strands analysis"}
            
            # Prepare correlated data for strands agent
            correlated_data = {
                "alerts": [alert.dict() for alert in client_alerts],
                "client": client.dict(),
                "historical_data": HISTORICAL_PATTERNS
            }
            
            # Run strands agent prediction
            strands_result = await strands_agent.run(correlated_data)
            
            return {
                "client_id": client_id,
                "client_name": client.name,
                "strands_prediction": strands_result,
                "alerts_analyzed": len(client_alerts),
                "agent_status": strands_agent.get_status(),
                "generated_at": datetime.now().isoformat()
            }
        else:
            # Get predictions for all clients
            all_predictions = []
            
            for client in MOCK_CLIENTS:
                client_alerts = [a for a in all_alerts if a.client_id == client.id and a.cascade_risk > 0.3]
                if client_alerts:
                    correlated_data = {
                        "alerts": [alert.dict() for alert in client_alerts],
                        "client": client.dict(),
                        "historical_data": HISTORICAL_PATTERNS
                    }
                    
                    strands_result = await strands_agent.run(correlated_data)
                    all_predictions.append({
                        "client_id": client.id,
                        "client_name": client.name,
                        "prediction": strands_result
                    })
            
            return {
                "total_clients_analyzed": len(all_predictions),
                "predictions": all_predictions,
                "agent_status": strands_agent.get_status(),
                "generated_at": datetime.now().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strands-agent/status")
async def get_strands_agent_status():
    """Get strands agent status and performance metrics"""
    try:
        return strands_agent.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))