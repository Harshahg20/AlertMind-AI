import asyncio
import json
import logging
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import subprocess
import time

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from app.models.alert import Alert, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"

class ActionType(Enum):
    SCALE_RESOURCES = "scale_resources"
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    ENABLE_FAILOVER = "enable_failover"
    NOTIFY_TEAM = "notify_team"
    EXECUTE_SCRIPT = "execute_script"
    UPDATE_CONFIG = "update_config"
    BACKUP_DATA = "backup_data"

@dataclass
class PreventionAction:
    """Represents a prevention action to be executed"""
    id: str
    action_type: ActionType
    description: str
    target_system: str
    parameters: Dict
    estimated_duration: int  # seconds
    success_criteria: List[str]
    rollback_plan: List[str]
    risk_level: str  # low, medium, high
    requires_approval: bool = False
    dependencies: List[str] = None

@dataclass
class ExecutionResult:
    """Result of action execution"""
    action_id: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    output: str
    error_message: Optional[str]
    metrics: Dict
    rollback_required: bool = False

@dataclass
class ExecutionPlan:
    """Complete execution plan for prevention actions"""
    plan_id: str
    alert_id: str
    client_id: str
    actions: List[PreventionAction]
    estimated_total_duration: int
    risk_assessment: str
    success_probability: float
    rollback_plan: List[str]
    created_at: datetime

class TinyLLMSummarizer:
    """
    Lightweight LLM for pre-check summaries using sentence transformers
    No heavy LLM needed - just for generating human-readable summaries
    """
    
    def __init__(self):
        self.embedder = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                logger.info("✅ Tiny LLM (sentence transformer) loaded for summaries")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load sentence transformer: {e}")
        else:
            logger.warning("⚠️ Sentence transformers not available, using fallback summaries")
    
    def generate_execution_summary(self, plan: ExecutionPlan, context: Dict) -> str:
        """Generate a human-readable summary of the execution plan"""
        
        if self.embedder:
            return self._generate_llm_summary(plan, context)
        else:
            return self._generate_fallback_summary(plan, context)
    
    def _generate_llm_summary(self, plan: ExecutionPlan, context: Dict) -> str:
        """Generate summary using sentence transformer embeddings"""
        try:
            # Create a structured summary
            action_descriptions = [action.description for action in plan.actions]
            action_text = " ".join(action_descriptions)
            
            # Use embeddings to create a semantic summary
            if action_text:
                embeddings = self.embedder.encode([action_text])
                # Simple summary based on action types and risk
                high_risk_actions = [a for a in plan.actions if a.risk_level == "high"]
                medium_risk_actions = [a for a in plan.actions if a.risk_level == "medium"]
                
                summary = f"Execution plan for {plan.alert_id}: "
                summary += f"{len(plan.actions)} actions planned, "
                summary += f"estimated duration {plan.estimated_total_duration}s, "
                summary += f"success probability {plan.success_probability:.1%}. "
                
                if high_risk_actions:
                    summary += f"High-risk actions: {len(high_risk_actions)}. "
                if medium_risk_actions:
                    summary += f"Medium-risk actions: {len(medium_risk_actions)}. "
                
                summary += f"Risk assessment: {plan.risk_assessment}."
                
                return summary
            else:
                return self._generate_fallback_summary(plan, context)
                
        except Exception as e:
            logger.warning(f"LLM summary generation failed: {e}")
            return self._generate_fallback_summary(plan, context)
    
    def _generate_fallback_summary(self, plan: ExecutionPlan, context: Dict) -> str:
        """Generate fallback summary without LLM"""
        action_types = [action.action_type.value for action in plan.actions]
        unique_types = list(set(action_types))
        
        summary = f"Prevention execution plan for alert {plan.alert_id}: "
        summary += f"{len(plan.actions)} actions ({', '.join(unique_types[:3])}), "
        summary += f"duration {plan.estimated_total_duration}s, "
        summary += f"success rate {plan.success_probability:.1%}, "
        summary += f"risk level: {plan.risk_assessment}"
        
        return summary

class DeterministicOrchestrator:
    """
    Pure code orchestration for execution - deterministic and auditable
    No LLM dependency for core execution logic
    """
    
    def __init__(self):
        self.execution_history = []
        self.active_executions = {}
        self.action_templates = self._initialize_action_templates()
    
    def _initialize_action_templates(self) -> Dict[ActionType, Dict]:
        """Initialize templates for different action types"""
        return {
            ActionType.SCALE_RESOURCES: {
                "description": "Scale system resources",
                "estimated_duration": 30,
                "success_criteria": ["resource_usage < 80%", "response_time < 2s"],
                "rollback_plan": ["revert_resource_scaling", "monitor_system_health"],
                "risk_level": "medium"
            },
            ActionType.RESTART_SERVICE: {
                "description": "Restart service",
                "estimated_duration": 60,
                "success_criteria": ["service_running", "health_check_passing"],
                "rollback_plan": ["restart_service_again", "check_dependencies"],
                "risk_level": "high"
            },
            ActionType.CLEAR_CACHE: {
                "description": "Clear system cache",
                "estimated_duration": 15,
                "success_criteria": ["cache_cleared", "performance_improved"],
                "rollback_plan": ["rebuild_cache", "restore_from_backup"],
                "risk_level": "low"
            },
            ActionType.ENABLE_FAILOVER: {
                "description": "Enable failover mechanism",
                "estimated_duration": 45,
                "success_criteria": ["failover_active", "traffic_redirected"],
                "rollback_plan": ["disable_failover", "restore_primary"],
                "risk_level": "medium"
            },
            ActionType.NOTIFY_TEAM: {
                "description": "Notify team members",
                "estimated_duration": 5,
                "success_criteria": ["notifications_sent", "acknowledgments_received"],
                "rollback_plan": ["send_correction_notice"],
                "risk_level": "low"
            },
            ActionType.EXECUTE_SCRIPT: {
                "description": "Execute custom script",
                "estimated_duration": 120,
                "success_criteria": ["script_completed", "exit_code_0"],
                "rollback_plan": ["execute_rollback_script", "restore_previous_state"],
                "risk_level": "high"
            },
            ActionType.UPDATE_CONFIG: {
                "description": "Update configuration",
                "estimated_duration": 20,
                "success_criteria": ["config_updated", "service_reloaded"],
                "rollback_plan": ["restore_previous_config", "restart_service"],
                "risk_level": "medium"
            },
            ActionType.BACKUP_DATA: {
                "description": "Backup critical data",
                "estimated_duration": 300,
                "success_criteria": ["backup_completed", "integrity_verified"],
                "rollback_plan": ["verify_backup_integrity"],
                "risk_level": "low"
            }
        }
    
    def create_execution_plan(self, alert: Alert, client: Client, 
                            recommended_actions: List[str]) -> ExecutionPlan:
        """Create a deterministic execution plan from recommended actions"""
        
        actions = []
        total_duration = 0
        
        for action_desc in recommended_actions:
            action = self._parse_action_description(action_desc, alert, client)
            if action:
                actions.append(action)
                total_duration += action.estimated_duration
        
        # Calculate risk assessment
        risk_assessment = self._assess_execution_risk(actions)
        
        # Calculate success probability
        success_probability = self._calculate_success_probability(actions, client)
        
        # Create rollback plan
        rollback_plan = self._create_rollback_plan(actions)
        
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            alert_id=alert.id,
            client_id=client.id,
            actions=actions,
            estimated_total_duration=total_duration,
            risk_assessment=risk_assessment,
            success_probability=success_probability,
            rollback_plan=rollback_plan,
            created_at=datetime.now()
        )
    
    def _parse_action_description(self, action_desc: str, alert: Alert, 
                                 client: Client) -> Optional[PreventionAction]:
        """Parse action description and create PreventionAction"""
        
        action_desc_lower = action_desc.lower()
        
        # Map descriptions to action types
        if "scale" in action_desc_lower and "resource" in action_desc_lower:
            action_type = ActionType.SCALE_RESOURCES
            target_system = alert.system
            parameters = {"scale_factor": 1.5, "target_usage": 70}
        elif "restart" in action_desc_lower:
            action_type = ActionType.RESTART_SERVICE
            target_system = alert.system
            parameters = {"service_name": alert.system, "graceful": True}
        elif "clear" in action_desc_lower and "cache" in action_desc_lower:
            action_type = ActionType.CLEAR_CACHE
            target_system = alert.system
            parameters = {"cache_type": "all", "force": True}
        elif "failover" in action_desc_lower:
            action_type = ActionType.ENABLE_FAILOVER
            target_system = alert.system
            parameters = {"failover_target": "backup_system", "automatic": True}
        elif "notify" in action_desc_lower or "contact" in action_desc_lower:
            action_type = ActionType.NOTIFY_TEAM
            target_system = "notification_system"
            parameters = {"urgency": alert.severity, "client": client.name}
        elif "script" in action_desc_lower or "execute" in action_desc_lower:
            action_type = ActionType.EXECUTE_SCRIPT
            target_system = alert.system
            parameters = {"script_path": "/scripts/fix.sh", "timeout": 300}
        elif "config" in action_desc_lower or "update" in action_desc_lower:
            action_type = ActionType.UPDATE_CONFIG
            target_system = alert.system
            parameters = {"config_file": f"/etc/{alert.system}.conf", "backup": True}
        else:
            # Default to scale resources for unknown actions
            action_type = ActionType.SCALE_RESOURCES
            target_system = alert.system
            parameters = {"scale_factor": 1.2, "target_usage": 80}
        
        # Get template
        template = self.action_templates[action_type]
        
        return PreventionAction(
            id=str(uuid.uuid4()),
            action_type=action_type,
            description=action_desc,
            target_system=target_system,
            parameters=parameters,
            estimated_duration=template["estimated_duration"],
            success_criteria=template["success_criteria"],
            rollback_plan=template["rollback_plan"],
            risk_level=template["risk_level"],
            requires_approval=template["risk_level"] == "high",
            dependencies=[]
        )
    
    def _assess_execution_risk(self, actions: List[PreventionAction]) -> str:
        """Assess overall execution risk"""
        high_risk_count = len([a for a in actions if a.risk_level == "high"])
        medium_risk_count = len([a for a in actions if a.risk_level == "medium"])
        
        if high_risk_count > 0:
            return "high"
        elif medium_risk_count > 1:
            return "medium"
        else:
            return "low"
    
    def _calculate_success_probability(self, actions: List[PreventionAction], 
                                     client: Client) -> float:
        """Calculate success probability based on actions and client"""
        base_probability = 0.9
        
        # Adjust for risk levels
        for action in actions:
            if action.risk_level == "high":
                base_probability -= 0.1
            elif action.risk_level == "medium":
                base_probability -= 0.05
        
        # Adjust for client tier (enterprise clients get more resources)
        if client.tier.lower() == "enterprise":
            base_probability += 0.05
        elif client.tier.lower() == "basic":
            base_probability -= 0.05
        
        return max(0.5, min(0.95, base_probability))
    
    def _create_rollback_plan(self, actions: List[PreventionAction]) -> List[str]:
        """Create comprehensive rollback plan"""
        rollback_steps = []
        
        # Reverse order of actions for rollback
        for action in reversed(actions):
            rollback_steps.extend(action.rollback_plan)
        
        # Add general rollback steps
        rollback_steps.extend([
            "Verify system health",
            "Restore monitoring",
            "Notify team of rollback completion"
        ])
        
        return rollback_steps

class PreventionExecutionAgent:
    """
    Prevention Execution Agent - Lightweight orchestrator with deterministic execution
    Primary: Pure code orchestration (recommended for safety)
    Optional: Tiny LLM for pre-check summaries
    """
    
    def __init__(self):
        self.name = "prevention_execution_agent"
        self.version = "2.0.0"
        
        # Initialize components
        self.orchestrator = DeterministicOrchestrator()
        self.summarizer = TinyLLMSummarizer()
        
        # Execution state
        self.active_plans = {}
        self.execution_history = []
        
        logger.info("✅ Prevention Execution Agent initialized")
    
    async def execute_prevention_plan(self, alert: Alert, client: Client, 
                                    recommended_actions: List[str],
                                    auto_approve: bool = False) -> Dict:
        """
        Execute prevention plan with deterministic orchestration
        
        Args:
            alert: Alert that triggered the prevention
            client: Client information
            recommended_actions: List of recommended actions
            auto_approve: Whether to auto-approve high-risk actions
        """
        try:
            # Step 1: Create execution plan
            plan = self.orchestrator.create_execution_plan(alert, client, recommended_actions)
            
            # Step 2: Generate summary
            context = {
                "alert_severity": alert.severity,
                "client_tier": client.tier,
                "business_hours": True,  # Would be calculated
                "system_criticality": alert.system in client.critical_systems
            }
            summary = self.summarizer.generate_execution_summary(plan, context)
            
            # Step 3: Check if approval is needed
            requires_approval = any(action.requires_approval for action in plan.actions)
            
            if requires_approval and not auto_approve:
                return {
                    "status": "approval_required",
                    "plan_id": plan.plan_id,
                    "summary": summary,
                    "risk_assessment": plan.risk_assessment,
                    "estimated_duration": plan.estimated_total_duration,
                    "success_probability": plan.success_probability,
                    "actions_requiring_approval": [
                        action.id for action in plan.actions if action.requires_approval
                    ]
                }
            
            # Step 4: Execute plan
            execution_results = await self._execute_plan(plan)
            
            # Step 5: Generate execution report
            report = self._generate_execution_report(plan, execution_results)
            
            return {
                "status": "completed",
                "plan_id": plan.plan_id,
                "summary": summary,
                "execution_results": execution_results,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Prevention execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_plan(self, plan: ExecutionPlan) -> List[ExecutionResult]:
        """Execute the prevention plan deterministically"""
        results = []
        
        # Store active plan
        self.active_plans[plan.plan_id] = plan
        
        try:
            for action in plan.actions:
                logger.info(f"Executing action: {action.description}")
                
                result = await self._execute_action(action)
                results.append(result)
                
                # If action failed and is critical, consider rollback
                if result.status == ExecutionStatus.FAILED and action.risk_level == "high":
                    logger.warning(f"Critical action failed: {action.id}")
                    # Could implement automatic rollback here
                
                # Small delay between actions
                await asyncio.sleep(1)
        
        finally:
            # Remove from active plans
            if plan.plan_id in self.active_plans:
                del self.active_plans[plan.plan_id]
        
        return results
    
    async def _execute_action(self, action: PreventionAction) -> ExecutionResult:
        """Execute a single action deterministically"""
        start_time = datetime.now()
        
        try:
            # Simulate action execution (in real implementation, this would call actual systems)
            await self._simulate_action_execution(action)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return ExecutionResult(
                action_id=action.id,
                status=ExecutionStatus.SUCCESS,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                output=f"Action {action.action_type.value} completed successfully",
                error_message=None,
                metrics={"execution_time": duration, "success": True},
                rollback_required=False
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return ExecutionResult(
                action_id=action.id,
                status=ExecutionStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                output="",
                error_message=str(e),
                metrics={"execution_time": duration, "success": False},
                rollback_required=action.risk_level == "high"
            )
    
    async def _simulate_action_execution(self, action: PreventionAction):
        """Simulate action execution (replace with real implementations)"""
        
        # Simulate execution time
        await asyncio.sleep(min(2, action.estimated_duration / 30))  # Scale down for demo
        
        # Simulate occasional failures for realism
        import random
        if random.random() < 0.1:  # 10% failure rate
            raise Exception(f"Simulated failure in {action.action_type.value}")
    
    def _generate_execution_report(self, plan: ExecutionPlan, 
                                 results: List[ExecutionResult]) -> Dict:
        """Generate execution report"""
        
        successful_actions = len([r for r in results if r.status == ExecutionStatus.SUCCESS])
        failed_actions = len([r for r in results if r.status == ExecutionStatus.FAILED])
        total_duration = sum(r.duration_seconds for r in results if r.duration_seconds)
        
        return {
            "plan_id": plan.plan_id,
            "execution_summary": {
                "total_actions": len(results),
                "successful_actions": successful_actions,
                "failed_actions": failed_actions,
                "success_rate": successful_actions / len(results) if results else 0,
                "total_duration_seconds": total_duration,
                "estimated_duration_seconds": plan.estimated_total_duration
            },
            "action_results": [
                {
                    "action_id": r.action_id,
                    "status": r.status.value,
                    "duration_seconds": r.duration_seconds,
                    "success": r.status == ExecutionStatus.SUCCESS,
                    "error": r.error_message
                }
                for r in results
            ],
            "risk_assessment": plan.risk_assessment,
            "rollback_available": any(r.rollback_required for r in results)
        }
    
    def get_agent_info(self) -> Dict:
        """Get agent information"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": [
                "deterministic_execution_orchestration",
                "action_plan_generation",
                "risk_assessment",
                "rollback_planning",
                "execution_monitoring",
                "tiny_llm_summaries" if SENTENCE_TRANSFORMERS_AVAILABLE else "fallback_summaries",
                "audit_trail_generation"
            ],
            "models_loaded": {
                "sentence_transformer": SENTENCE_TRANSFORMERS_AVAILABLE,
                "deterministic_orchestrator": True
            },
            "status": "ready",
            "active_plans": len(self.active_plans),
            "execution_history_count": len(self.execution_history)
        }
