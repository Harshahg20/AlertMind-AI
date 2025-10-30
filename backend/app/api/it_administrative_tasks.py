from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from app.api.alerts import MOCK_CLIENTS
from app.services.it_administrative_agent import ITAdministrativeAgent, AdministrativeTask, TaskType, TaskPriority

router = APIRouter()

# Initialize the IT administrative agent
admin_agent = ITAdministrativeAgent()

@router.get("/recommendations/{client_id}")
async def get_task_recommendations(client_id: str) -> Dict:
    """Get AI-powered task recommendations for a client"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        tasks = await admin_agent.generate_task_recommendations(client)
        
        return {
            "client_id": client_id,
            "client_name": client.name,
            "recommended_tasks": [
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type.value,
                    "priority": task.priority.value,
                    "description": task.description,
                    "estimated_duration": task.estimated_duration,
                    "required_resources": task.required_resources,
                    "success_criteria": task.success_criteria,
                    "risk_assessment": task.risk_assessment,
                    "ai_analysis": task.ai_analysis,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat()
                } for task in tasks
            ],
            "total_recommendations": len(tasks),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task recommendation failed: {str(e)}")

@router.post("/execute/{client_id}")
async def execute_administrative_task(
    client_id: str, 
    task_type: str, 
    priority: str = "medium",
    description: Optional[str] = None
) -> Dict:
    """Execute an administrative task for a client"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Create task
        task_id = f"{client_id}_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        task = AdministrativeTask(
            task_id=task_id,
            task_type=TaskType(task_type),
            client=client,
            priority=TaskPriority(priority),
            description=description or f"Execute {task_type} for {client.name}",
            ai_analysis={
                "reasoning": "Manual task execution",
                "estimated_impact": "medium",
                "automation_potential": "high",
                "scheduling_preference": "immediate"
            }
        )
        
        # Execute task
        result = await admin_agent.execute_task(task)
        
        return {
            "client_id": client_id,
            "task_execution": result,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

@router.get("/compliance-report/{client_id}")
async def generate_compliance_report(client_id: str) -> Dict:
    """Generate comprehensive compliance report for a client"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        compliance_report = await admin_agent.generate_compliance_report(client)
        
        return {
            "client_id": client_id,
            "client_name": client.name,
            "compliance_report": compliance_report,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance report generation failed: {str(e)}")

@router.get("/task-history/{client_id}")
async def get_task_history(client_id: str, limit: int = 10) -> Dict:
    """Get task execution history for a client"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Filter tasks for this client
        client_tasks = [task for task in admin_agent.task_history if task.client.id == client_id]
        recent_tasks = client_tasks[-limit:] if len(client_tasks) > limit else client_tasks
        
        return {
            "client_id": client_id,
            "client_name": client.name,
            "task_history": [
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type.value,
                    "priority": task.priority.value,
                    "description": task.description,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "estimated_duration": task.estimated_duration,
                    "risk_assessment": task.risk_assessment
                } for task in recent_tasks
            ],
            "total_tasks": len(client_tasks),
            "successful_tasks": len([task for task in client_tasks if task.status.value == "completed"]),
            "failed_tasks": len([task for task in client_tasks if task.status.value == "failed"]),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task history: {str(e)}")

@router.get("/available-tasks")
async def get_available_task_types() -> Dict:
    """Get list of available administrative task types"""
    try:
        task_types = [
            {
                "type": task_type.value,
                "name": task_type.value.replace("_", " ").title(),
                "description": _get_task_description(task_type),
                "typical_duration": _get_typical_duration(task_type),
                "automation_level": _get_automation_level(task_type)
            } for task_type in TaskType
        ]
        
        return {
            "available_task_types": task_types,
            "total_types": len(task_types),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task types: {str(e)}")

@router.get("/performance-metrics")
async def get_admin_agent_metrics() -> Dict:
    """Get IT administrative agent performance metrics"""
    try:
        metrics = admin_agent.get_performance_metrics()
        return {
            "metrics": metrics,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.post("/bulk-execute/{client_id}")
async def bulk_execute_tasks(
    client_id: str, 
    task_types: List[str],
    background_tasks: BackgroundTasks
) -> Dict:
    """Execute multiple administrative tasks in bulk"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        execution_results = []
        
        for task_type in task_types:
            try:
                task_id = f"{client_id}_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                
                task = AdministrativeTask(
                    task_id=task_id,
                    task_type=TaskType(task_type),
                    client=client,
                    priority=TaskPriority.MEDIUM,
                    description=f"Bulk execution of {task_type} for {client.name}",
                    ai_analysis={
                        "reasoning": "Bulk task execution",
                        "estimated_impact": "medium",
                        "automation_potential": "high",
                        "scheduling_preference": "immediate"
                    }
                )
                
                # Execute task
                result = await admin_agent.execute_task(task)
                execution_results.append({
                    "task_type": task_type,
                    "result": result
                })
                
            except Exception as e:
                execution_results.append({
                    "task_type": task_type,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "client_id": client_id,
            "bulk_execution": {
                "total_tasks": len(task_types),
                "successful_tasks": len([r for r in execution_results if "error" not in r]),
                "failed_tasks": len([r for r in execution_results if "error" in r]),
                "results": execution_results
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk execution failed: {str(e)}")

def _get_task_description(task_type: TaskType) -> str:
    """Get human-readable description for task type"""
    descriptions = {
        TaskType.SECURITY_AUDIT: "Comprehensive security assessment and vulnerability analysis",
        TaskType.COMPLIANCE_CHECK: "Verify compliance with regulatory requirements and policies",
        TaskType.BACKUP_VERIFICATION: "Verify backup integrity and test recovery procedures",
        TaskType.CAPACITY_PLANNING: "Analyze resource usage and plan for future capacity needs",
        TaskType.PERFORMANCE_OPTIMIZATION: "Identify and resolve performance bottlenecks",
        TaskType.USER_ACCESS_REVIEW: "Review and audit user access rights and permissions",
        TaskType.SYSTEM_HEALTH_CHECK: "Comprehensive system health and status verification",
        TaskType.DISASTER_RECOVERY_TEST: "Test disaster recovery procedures and backup systems",
        TaskType.SOFTWARE_INVENTORY: "Audit software installations and license compliance",
        TaskType.NETWORK_ANALYSIS: "Analyze network performance and security posture"
    }
    return descriptions.get(task_type, "Administrative task execution")

def _get_typical_duration(task_type: TaskType) -> str:
    """Get typical duration for task type"""
    durations = {
        TaskType.SECURITY_AUDIT: "2-4 hours",
        TaskType.COMPLIANCE_CHECK: "1-2 hours",
        TaskType.BACKUP_VERIFICATION: "30-60 minutes",
        TaskType.CAPACITY_PLANNING: "2-3 hours",
        TaskType.PERFORMANCE_OPTIMIZATION: "1-2 hours",
        TaskType.USER_ACCESS_REVIEW: "30-60 minutes",
        TaskType.SYSTEM_HEALTH_CHECK: "15-30 minutes",
        TaskType.DISASTER_RECOVERY_TEST: "4-6 hours",
        TaskType.SOFTWARE_INVENTORY: "30-60 minutes",
        TaskType.NETWORK_ANALYSIS: "1-2 hours"
    }
    return durations.get(task_type, "1 hour")

def _get_automation_level(task_type: TaskType) -> str:
    """Get automation level for task type"""
    automation_levels = {
        TaskType.SECURITY_AUDIT: "Medium",
        TaskType.COMPLIANCE_CHECK: "High",
        TaskType.BACKUP_VERIFICATION: "High",
        TaskType.CAPACITY_PLANNING: "Medium",
        TaskType.PERFORMANCE_OPTIMIZATION: "Medium",
        TaskType.USER_ACCESS_REVIEW: "High",
        TaskType.SYSTEM_HEALTH_CHECK: "High",
        TaskType.DISASTER_RECOVERY_TEST: "Low",
        TaskType.SOFTWARE_INVENTORY: "High",
        TaskType.NETWORK_ANALYSIS: "Medium"
    }
    return automation_levels.get(task_type, "Medium")
