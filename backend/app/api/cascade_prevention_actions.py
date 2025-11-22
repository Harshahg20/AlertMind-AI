from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import datetime
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/execute-cascade-prevention")
async def execute_cascade_prevention(prediction_data: Dict) -> Dict:
    """
    Execute automated prevention actions for a cascade prediction
    
    This endpoint demonstrates:
    - Automated action execution
    - Real-time prevention
    - Operational efficiency
    - Time savings
    
    Args:
        prediction_data: Contains client_id, system, affected_systems, confidence, etc.
    
    Returns:
        Detailed action execution results with metrics
    """
    try:
        client_id = prediction_data.get("client_id")
        system = prediction_data.get("system")
        affected_systems = prediction_data.get("affected_systems", [])
        confidence = prediction_data.get("confidence", 0)
        time_to_cascade = prediction_data.get("time_to_cascade", 0)
        
        logger.info(f"Executing cascade prevention for {client_id} - {system}")
        
        # Generate prevention actions based on the prediction
        prevention_actions = _generate_prevention_actions(
            system, affected_systems, confidence, time_to_cascade
        )
        
        # Execute actions (simulated for demo, but shows real workflow)
        execution_results = await _execute_prevention_actions(
            prevention_actions, client_id, system
        )
        
        # Calculate efficiency metrics
        efficiency_metrics = _calculate_efficiency_metrics(
            prevention_actions, execution_results, time_to_cascade
        )
        
        return {
            "success": True,
            "client_id": client_id,
            "system": system,
            "prediction": {
                "confidence": confidence,
                "time_to_cascade_minutes": time_to_cascade,
                "affected_systems": affected_systems
            },
            "prevention_actions": prevention_actions,
            "execution_results": execution_results,
            "efficiency_metrics": efficiency_metrics,
            "summary": {
                "total_actions": len(prevention_actions),
                "successful_actions": len([r for r in execution_results if r["status"] == "success"]),
                "time_saved_minutes": efficiency_metrics["time_saved_minutes"],
                "downtime_prevented_minutes": efficiency_metrics["downtime_prevented_minutes"],
                "estimated_cost_savings_usd": efficiency_metrics["estimated_cost_savings_usd"]
            },
            "next_steps": _generate_next_steps(execution_results),
            "executed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to execute cascade prevention: {e}")
        raise HTTPException(status_code=500, detail=f"Prevention execution failed: {str(e)}")


def _generate_prevention_actions(system: str, affected_systems: List[str], 
                                 confidence: float, time_to_cascade: int) -> List[Dict]:
    """Generate appropriate prevention actions based on the prediction"""
    
    actions = []
    
    # Action 1: Scale resources for the primary system
    if system in ["database", "web-app", "api-gateway", "trading-platform"]:
        actions.append({
            "action_id": "action_001",
            "type": "resource_scaling",
            "priority": "IMMEDIATE",
            "target_system": system,
            "description": f"Scale {system} resources to handle increased load",
            "details": {
                "cpu_increase": "50%",
                "memory_increase": "40%",
                "estimated_time": "2 minutes"
            },
            "automation_level": "fully_automated",
            "risk_level": "low"
        })
    
    # Action 2: Enable failover for critical systems
    if confidence >= 0.7:
        actions.append({
            "action_id": "action_002",
            "type": "failover_activation",
            "priority": "HIGH",
            "target_system": system,
            "description": f"Activate standby failover for {system}",
            "details": {
                "failover_target": f"{system}-standby",
                "sync_status": "ready",
                "estimated_time": "1 minute"
            },
            "automation_level": "fully_automated",
            "risk_level": "low"
        })
    
    # Action 3: Implement rate limiting for affected systems
    for affected_system in affected_systems[:2]:  # Top 2 affected systems
        actions.append({
            "action_id": f"action_{len(actions) + 1:03d}",
            "type": "rate_limiting",
            "priority": "MEDIUM",
            "target_system": affected_system,
            "description": f"Apply rate limiting to {affected_system} to prevent overload",
            "details": {
                "current_limit": "1000 req/sec",
                "new_limit": "500 req/sec",
                "estimated_time": "30 seconds"
            },
            "automation_level": "fully_automated",
            "risk_level": "low"
        })
    
    # Action 4: Alert escalation
    if confidence >= 0.8:
        actions.append({
            "action_id": f"action_{len(actions) + 1:03d}",
            "type": "alert_escalation",
            "priority": "HIGH",
            "target_system": "monitoring",
            "description": "Escalate to senior technician for monitoring",
            "details": {
                "escalation_level": "senior_engineer",
                "notification_channels": ["email", "sms", "slack"],
                "estimated_time": "immediate"
            },
            "automation_level": "fully_automated",
            "risk_level": "none"
        })
    
    # Action 5: Increase monitoring frequency
    actions.append({
        "action_id": f"action_{len(actions) + 1:03d}",
        "type": "monitoring_enhancement",
        "priority": "MEDIUM",
        "target_system": system,
        "description": f"Increase monitoring frequency for {system} and dependencies",
        "details": {
            "current_interval": "5 minutes",
            "new_interval": "30 seconds",
            "duration": "60 minutes",
            "estimated_time": "10 seconds"
        },
        "automation_level": "fully_automated",
        "risk_level": "none"
    })
    
    return actions


async def _execute_prevention_actions(actions: List[Dict], client_id: str, 
                                      system: str) -> List[Dict]:
    """Execute prevention actions and return results"""
    
    results = []
    
    for action in actions:
        # Simulate execution time
        execution_time = _get_execution_time(action["type"])
        await asyncio.sleep(0.1)  # Small delay for demo realism
        
        # Simulate execution (in production, this would call actual APIs)
        result = {
            "action_id": action["action_id"],
            "action_type": action["type"],
            "target_system": action["target_system"],
            "status": "success",  # In production: could be success/failed/partial
            "execution_time_seconds": execution_time,
            "result_message": f"{action['description']} - Completed successfully",
            "metrics": _get_action_metrics(action["type"]),
            "timestamp": datetime.now().isoformat()
        }
        
        results.append(result)
        logger.info(f"Executed action {action['action_id']}: {action['type']}")
    
    return results


def _get_execution_time(action_type: str) -> int:
    """Get estimated execution time for action type"""
    execution_times = {
        "resource_scaling": 120,  # 2 minutes
        "failover_activation": 60,  # 1 minute
        "rate_limiting": 30,  # 30 seconds
        "alert_escalation": 5,  # 5 seconds
        "monitoring_enhancement": 10  # 10 seconds
    }
    return execution_times.get(action_type, 30)


def _get_action_metrics(action_type: str) -> Dict:
    """Get metrics for executed action"""
    metrics_map = {
        "resource_scaling": {
            "cpu_utilization_before": "87%",
            "cpu_utilization_after": "45%",
            "capacity_increase": "50%"
        },
        "failover_activation": {
            "failover_status": "active",
            "sync_lag": "0 seconds",
            "availability": "99.99%"
        },
        "rate_limiting": {
            "requests_blocked": 0,
            "requests_throttled": 150,
            "system_stability": "improved"
        },
        "alert_escalation": {
            "notification_sent": True,
            "acknowledgment_time": "2 minutes",
            "escalation_level": "senior_engineer"
        },
        "monitoring_enhancement": {
            "data_points_collected": 120,
            "anomalies_detected": 0,
            "monitoring_coverage": "100%"
        }
    }
    return metrics_map.get(action_type, {})


def _calculate_efficiency_metrics(actions: List[Dict], results: List[Dict], 
                                  time_to_cascade: int) -> Dict:
    """Calculate efficiency and cost savings metrics"""
    
    # Calculate time saved
    manual_execution_time = len(actions) * 15  # 15 min per manual action
    automated_execution_time = sum(r["execution_time_seconds"] for r in results) / 60
    time_saved = manual_execution_time - automated_execution_time
    
    # Calculate downtime prevented
    downtime_prevented = time_to_cascade + 30  # Cascade time + recovery time
    
    # Calculate cost savings
    # Assumptions: $200/hour for technician, $5000/hour for downtime
    labor_cost_saved = (time_saved / 60) * 200
    downtime_cost_saved = (downtime_prevented / 60) * 5000
    total_savings = labor_cost_saved + downtime_cost_saved
    
    return {
        "time_saved_minutes": round(time_saved, 1),
        "manual_execution_time_minutes": manual_execution_time,
        "automated_execution_time_minutes": round(automated_execution_time, 1),
        "automation_efficiency_percentage": round((time_saved / manual_execution_time) * 100, 1),
        "downtime_prevented_minutes": downtime_prevented,
        "labor_cost_saved_usd": round(labor_cost_saved, 2),
        "downtime_cost_saved_usd": round(downtime_cost_saved, 2),
        "estimated_cost_savings_usd": round(total_savings, 2),
        "roi_ratio": round(total_savings / 100, 1)  # Assuming $100 automation cost
    }


def _generate_next_steps(results: List[Dict]) -> List[str]:
    """Generate recommended next steps based on execution results"""
    
    next_steps = []
    
    # Check if all actions succeeded
    all_success = all(r["status"] == "success" for r in results)
    
    if all_success:
        next_steps.extend([
            "✅ All prevention actions executed successfully",
            "📊 Monitor system metrics for next 30 minutes",
            "🔍 Verify cascade risk has been mitigated",
            "📝 Document incident for future learning"
        ])
    else:
        next_steps.extend([
            "⚠️ Some actions require manual intervention",
            "🔧 Review failed actions and retry if needed",
            "📞 Contact on-call engineer for assistance"
        ])
    
    next_steps.append("🔄 Continue monitoring for new predictions")
    
    return next_steps


@router.get("/prevention-history/{client_id}")
async def get_prevention_history(client_id: str, limit: int = 10) -> Dict:
    """
    Get history of prevention actions for a client
    Shows track record of automated prevention
    """
    try:
        # In production, this would query a database
        # For demo, return mock history
        history = []
        
        for i in range(min(limit, 5)):
            history.append({
                "execution_id": f"exec_{client_id}_{i:03d}",
                "timestamp": datetime.now().isoformat(),
                "system": ["database", "web-app", "api-gateway"][i % 3],
                "actions_executed": 4 + i,
                "success_rate": 100.0,
                "time_saved_minutes": 45 + (i * 5),
                "cost_savings_usd": 2500 + (i * 500),
                "downtime_prevented_minutes": 60 + (i * 10)
            })
        
        total_savings = sum(h["cost_savings_usd"] for h in history)
        total_time_saved = sum(h["time_saved_minutes"] for h in history)
        
        return {
            "client_id": client_id,
            "history": history,
            "summary": {
                "total_preventions": len(history),
                "total_cost_savings_usd": total_savings,
                "total_time_saved_minutes": total_time_saved,
                "average_success_rate": 100.0,
                "total_downtime_prevented_hours": round(sum(h["downtime_prevented_minutes"] for h in history) / 60, 1)
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get prevention history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
