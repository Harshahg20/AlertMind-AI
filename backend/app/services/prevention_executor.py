import asyncio
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from app.models.alert import Alert, Client

logger = logging.getLogger(__name__)

class ActionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class PreventionAction:
    """Represents a prevention action that can be executed"""
    
    def __init__(self, action_id: str, action_type: str, target_system: str, 
                 parameters: Dict, priority: int = 5):
        self.action_id = action_id
        self.action_type = action_type
        self.target_system = target_system
        self.parameters = parameters
        self.priority = priority
        self.status = ActionStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.rollback_actions = []

class PreventionExecutor:
    """
    Executes prevention actions autonomously based on AI agent decisions
    This is where the agent actually takes action to prevent cascades
    """
    
    def __init__(self):
        self.active_actions = {}
        self.action_history = []
        self.success_rate = 0.0
        self.rollback_count = 0
        
        # Action templates for different prevention scenarios
        self.action_templates = {
            "database_optimization": {
                "restart_database": {
                    "description": "Restart database service to clear connections",
                    "estimated_time": 120,  # seconds
                    "success_rate": 0.85,
                    "rollback_available": True,
                    "risk_level": "medium"
                },
                "scale_database_resources": {
                    "description": "Scale up database CPU and memory",
                    "estimated_time": 300,
                    "success_rate": 0.92,
                    "rollback_available": True,
                    "risk_level": "low"
                },
                "clear_connection_pool": {
                    "description": "Clear and reset database connection pool",
                    "estimated_time": 30,
                    "success_rate": 0.88,
                    "rollback_available": True,
                    "risk_level": "low"
                }
            },
            "network_optimization": {
                "reroute_traffic": {
                    "description": "Reroute traffic to backup network path",
                    "estimated_time": 60,
                    "success_rate": 0.90,
                    "rollback_available": True,
                    "risk_level": "low"
                },
                "scale_bandwidth": {
                    "description": "Increase bandwidth allocation",
                    "estimated_time": 180,
                    "success_rate": 0.95,
                    "rollback_available": True,
                    "risk_level": "low"
                },
                "activate_failover": {
                    "description": "Activate network failover systems",
                    "estimated_time": 45,
                    "success_rate": 0.87,
                    "rollback_available": True,
                    "risk_level": "medium"
                }
            },
            "storage_optimization": {
                "cleanup_temp_files": {
                    "description": "Clean up temporary files to free space",
                    "estimated_time": 240,
                    "success_rate": 0.96,
                    "rollback_available": False,
                    "risk_level": "low"
                },
                "archive_old_logs": {
                    "description": "Archive old log files to free space",
                    "estimated_time": 300,
                    "success_rate": 0.94,
                    "rollback_available": False,
                    "risk_level": "low"
                },
                "expand_storage": {
                    "description": "Expand storage capacity",
                    "estimated_time": 600,
                    "success_rate": 0.98,
                    "rollback_available": True,
                    "risk_level": "low"
                }
            },
            "application_optimization": {
                "restart_application": {
                    "description": "Restart application services",
                    "estimated_time": 90,
                    "success_rate": 0.82,
                    "rollback_available": True,
                    "risk_level": "medium"
                },
                "scale_application_instances": {
                    "description": "Scale up application instances",
                    "estimated_time": 180,
                    "success_rate": 0.89,
                    "rollback_available": True,
                    "risk_level": "low"
                },
                "optimize_cache": {
                    "description": "Optimize application cache settings",
                    "estimated_time": 60,
                    "success_rate": 0.91,
                    "rollback_available": True,
                    "risk_level": "low"
                }
            }
        }
    
    async def execute_prevention_plan(self, prevention_plan: Dict, client: Client, 
                                    alerts: List[Alert]) -> Dict:
        """
        Execute a complete prevention plan for cascade prevention
        """
        execution_id = f"exec_{client.id}_{int(datetime.now().timestamp())}"
        
        logger.info(f"🚀 Executing prevention plan {execution_id} for {client.name}")
        
        execution_result = {
            "execution_id": execution_id,
            "client_id": client.id,
            "client_name": client.name,
            "started_at": datetime.now().isoformat(),
            "actions": [],
            "overall_status": ActionStatus.PENDING,
            "success_count": 0,
            "failure_count": 0,
            "total_actions": 0
        }
        
        try:
            # Parse prevention recommendations into executable actions
            actions = self._parse_prevention_plan(prevention_plan, client, alerts)
            execution_result["total_actions"] = len(actions)
            
            # Execute actions in priority order
            for action in sorted(actions, key=lambda x: x.priority, reverse=True):
                action_result = await self._execute_single_action(action, client)
                execution_result["actions"].append(action_result)
                
                if action_result["status"] == ActionStatus.SUCCESS:
                    execution_result["success_count"] += 1
                else:
                    execution_result["failure_count"] += 1
                
                # Store action in history
                self.action_history.append(action_result)
            
            # Determine overall execution status
            if execution_result["failure_count"] == 0:
                execution_result["overall_status"] = ActionStatus.SUCCESS
            elif execution_result["success_count"] > 0:
                execution_result["overall_status"] = ActionStatus.IN_PROGRESS
            else:
                execution_result["overall_status"] = ActionStatus.FAILED
            
            execution_result["completed_at"] = datetime.now().isoformat()
            
            # Update success rate
            self._update_success_rate()
            
            logger.info(f"✅ Prevention plan {execution_id} completed: {execution_result['success_count']}/{execution_result['total_actions']} actions successful")
            
        except Exception as e:
            logger.error(f"❌ Prevention plan {execution_id} failed: {e}")
            execution_result["overall_status"] = ActionStatus.FAILED
            execution_result["error"] = str(e)
            execution_result["completed_at"] = datetime.now().isoformat()
        
        return execution_result
    
    def _parse_prevention_plan(self, prevention_plan: Dict, client: Client, 
                             alerts: List[Alert]) -> List[PreventionAction]:
        """Parse prevention plan into executable actions"""
        
        actions = []
        action_counter = 0
        
        # Get primary prevention recommendations
        primary_actions = prevention_plan.get("primary_actions", [])
        
        for recommendation in primary_actions:
            action_counter += 1
            action = self._create_action_from_recommendation(
                f"{client.id}_action_{action_counter}",
                recommendation,
                client,
                alerts
            )
            if action:
                actions.append(action)
        
        # Add fallback actions if needed
        fallback_actions = prevention_plan.get("fallback_actions", [])
        for recommendation in fallback_actions:
            action_counter += 1
            action = self._create_action_from_recommendation(
                f"{client.id}_fallback_{action_counter}",
                recommendation,
                client,
                alerts,
                priority=3  # Lower priority for fallback actions
            )
            if action:
                actions.append(action)
        
        return actions
    
    def _create_action_from_recommendation(self, action_id: str, recommendation: str, 
                                         client: Client, alerts: List[Alert], 
                                         priority: int = 5) -> Optional[PreventionAction]:
        """Create a PreventionAction from a text recommendation"""
        
        recommendation_lower = recommendation.lower()
        
        # Map recommendations to action templates
        if "database" in recommendation_lower or "sql" in recommendation_lower:
            if "restart" in recommendation_lower:
                return PreventionAction(
                    action_id, "restart_database", "database", 
                    {"client_id": client.id, "service": "database"}, priority
                )
            elif "scale" in recommendation_lower:
                return PreventionAction(
                    action_id, "scale_database_resources", "database",
                    {"client_id": client.id, "cpu_scale": 1.5, "memory_scale": 1.5}, priority
                )
            elif "connection" in recommendation_lower or "pool" in recommendation_lower:
                return PreventionAction(
                    action_id, "clear_connection_pool", "database",
                    {"client_id": client.id, "pool_name": "default"}, priority
                )
        
        elif "network" in recommendation_lower or "traffic" in recommendation_lower:
            if "reroute" in recommendation_lower:
                return PreventionAction(
                    action_id, "reroute_traffic", "network",
                    {"client_id": client.id, "backup_path": "secondary"}, priority
                )
            elif "bandwidth" in recommendation_lower:
                return PreventionAction(
                    action_id, "scale_bandwidth", "network",
                    {"client_id": client.id, "bandwidth_increase": 2.0}, priority
                )
            elif "failover" in recommendation_lower:
                return PreventionAction(
                    action_id, "activate_failover", "network",
                    {"client_id": client.id, "failover_type": "automatic"}, priority
                )
        
        elif "storage" in recommendation_lower or "disk" in recommendation_lower:
            if "cleanup" in recommendation_lower or "temp" in recommendation_lower:
                return PreventionAction(
                    action_id, "cleanup_temp_files", "storage",
                    {"client_id": client.id, "temp_dirs": ["/tmp", "/var/tmp"]}, priority
                )
            elif "archive" in recommendation_lower or "logs" in recommendation_lower:
                return PreventionAction(
                    action_id, "archive_old_logs", "storage",
                    {"client_id": client.id, "log_age_days": 30}, priority
                )
            elif "expand" in recommendation_lower:
                return PreventionAction(
                    action_id, "expand_storage", "storage",
                    {"client_id": client.id, "size_increase_gb": 100}, priority
                )
        
        elif "application" in recommendation_lower or "app" in recommendation_lower:
            if "restart" in recommendation_lower:
                return PreventionAction(
                    action_id, "restart_application", "application",
                    {"client_id": client.id, "services": ["web", "api"]}, priority
                )
            elif "scale" in recommendation_lower:
                return PreventionAction(
                    action_id, "scale_application_instances", "application",
                    {"client_id": client.id, "instance_count": 3}, priority
                )
            elif "cache" in recommendation_lower:
                return PreventionAction(
                    action_id, "optimize_cache", "application",
                    {"client_id": client.id, "cache_type": "redis"}, priority
                )
        
        # Default action for unrecognized recommendations
        return PreventionAction(
            action_id, "manual_intervention", "system",
            {"client_id": client.id, "recommendation": recommendation}, priority
        )
    
    async def _execute_single_action(self, action: PreventionAction, client: Client) -> Dict:
        """Execute a single prevention action"""
        
        action.status = ActionStatus.IN_PROGRESS
        action.started_at = datetime.now()
        
        logger.info(f"🔧 Executing {action.action_type} for {client.name}")
        
        try:
            # Get action template
            action_template = self._get_action_template(action.action_type)
            
            if not action_template:
                raise ValueError(f"Unknown action type: {action.action_type}")
            
            # Simulate action execution
            await self._simulate_action_execution(action, action_template)
            
            # Mark as successful
            action.status = ActionStatus.SUCCESS
            action.completed_at = datetime.now()
            
            logger.info(f"✅ {action.action_type} completed successfully for {client.name}")
            
        except Exception as e:
            # Mark as failed
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            action.completed_at = datetime.now()
            
            logger.error(f"❌ {action.action_type} failed for {client.name}: {e}")
            
            # Attempt rollback if available
            if action_template and action_template.get("rollback_available", False):
                await self._attempt_rollback(action, client)
        
        # Return action result
        return {
            "action_id": action.action_id,
            "action_type": action.action_type,
            "target_system": action.target_system,
            "status": action.status.value,
            "started_at": action.started_at.isoformat() if action.started_at else None,
            "completed_at": action.completed_at.isoformat() if action.completed_at else None,
            "error_message": action.error_message,
            "execution_time": (action.completed_at - action.started_at).total_seconds() if action.completed_at and action.started_at else None
        }
    
    async def _simulate_action_execution(self, action: PreventionAction, template: Dict):
        """Simulate the execution of a prevention action"""
        
        # Simulate execution time
        execution_time = template.get("estimated_time", 60)
        await asyncio.sleep(min(execution_time / 10, 5))  # Scale down for demo
        
        # Simulate success/failure based on success rate
        success_rate = template.get("success_rate", 0.8)
        import random
        if random.random() > success_rate:
            raise Exception(f"Simulated failure for {action.action_type}")
        
        # Simulate different action types
        if action.action_type == "restart_database":
            logger.info(f"🔄 Restarting database service for {action.parameters['client_id']}")
        elif action.action_type == "scale_database_resources":
            logger.info(f"⚡ Scaling database resources for {action.parameters['client_id']}")
        elif action.action_type == "clear_connection_pool":
            logger.info(f"🧹 Clearing connection pool for {action.parameters['client_id']}")
        elif action.action_type == "reroute_traffic":
            logger.info(f"🛣️ Rerouting traffic for {action.parameters['client_id']}")
        elif action.action_type == "cleanup_temp_files":
            logger.info(f"🗑️ Cleaning up temp files for {action.parameters['client_id']}")
        elif action.action_type == "restart_application":
            logger.info(f"🔄 Restarting application for {action.parameters['client_id']}")
        else:
            logger.info(f"🔧 Executing {action.action_type} for {action.parameters['client_id']}")
    
    def _get_action_template(self, action_type: str) -> Optional[Dict]:
        """Get action template for a specific action type"""
        
        for category, actions in self.action_templates.items():
            if action_type in actions:
                return actions[action_type]
        
        return None
    
    async def _attempt_rollback(self, action: PreventionAction, client: Client):
        """Attempt to rollback a failed action"""
        
        logger.info(f"🔄 Attempting rollback for {action.action_type} on {client.name}")
        
        try:
            # Simulate rollback process
            await asyncio.sleep(2)
            
            action.status = ActionStatus.ROLLED_BACK
            self.rollback_count += 1
            
            logger.info(f"✅ Rollback successful for {action.action_type}")
            
        except Exception as e:
            logger.error(f"❌ Rollback failed for {action.action_type}: {e}")
    
    def _update_success_rate(self):
        """Update overall success rate based on recent actions"""
        
        if not self.action_history:
            return
        
        # Calculate success rate from last 50 actions
        recent_actions = self.action_history[-50:]
        successful_actions = len([a for a in recent_actions if a["status"] == ActionStatus.SUCCESS.value])
        
        if recent_actions:
            self.success_rate = successful_actions / len(recent_actions)
    
    def get_execution_metrics(self) -> Dict:
        """Get comprehensive execution metrics"""
        
        total_actions = len(self.action_history)
        successful_actions = len([a for a in self.action_history if a["status"] == ActionStatus.SUCCESS.value])
        failed_actions = len([a for a in self.action_history if a["status"] == ActionStatus.FAILED.value])
        rolled_back_actions = len([a for a in self.action_history if a["status"] == ActionStatus.ROLLED_BACK.value])
        
        return {
            "total_actions_executed": total_actions,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "rolled_back_actions": rolled_back_actions,
            "success_rate": self.success_rate,
            "active_actions": len(self.active_actions),
            "rollback_count": self.rollback_count,
            "available_action_types": len([action for category in self.action_templates.values() for action in category.keys()])
        }
    
    def get_action_templates(self) -> Dict:
        """Get all available action templates"""
        return self.action_templates
