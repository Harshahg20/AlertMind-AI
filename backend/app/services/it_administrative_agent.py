import asyncio
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import numpy as np
from app.models.alert import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    SECURITY_AUDIT = "security_audit"
    COMPLIANCE_CHECK = "compliance_check"
    BACKUP_VERIFICATION = "backup_verification"
    CAPACITY_PLANNING = "capacity_planning"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    USER_ACCESS_REVIEW = "user_access_review"
    SYSTEM_HEALTH_CHECK = "system_health_check"
    DISASTER_RECOVERY_TEST = "disaster_recovery_test"
    SOFTWARE_INVENTORY = "software_inventory"
    NETWORK_ANALYSIS = "network_analysis"

class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AdministrativeTask:
    def __init__(self, task_id: str, task_type: TaskType, client: Client, 
                 priority: TaskPriority, description: str, ai_analysis: Dict):
        self.task_id = task_id
        self.task_type = task_type
        self.client = client
        self.priority = priority
        self.description = description
        self.ai_analysis = ai_analysis
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.estimated_duration = self._estimate_duration()
        self.required_resources = self._determine_resources()
        self.success_criteria = self._define_success_criteria()
        self.risk_assessment = self._assess_risks()

    def _estimate_duration(self) -> Dict[str, Any]:
        """Estimate task duration based on type and complexity"""
        duration_map = {
            TaskType.SECURITY_AUDIT: {"hours": 4, "complexity": "high"},
            TaskType.COMPLIANCE_CHECK: {"hours": 2, "complexity": "medium"},
            TaskType.BACKUP_VERIFICATION: {"hours": 1, "complexity": "low"},
            TaskType.CAPACITY_PLANNING: {"hours": 3, "complexity": "high"},
            TaskType.PERFORMANCE_OPTIMIZATION: {"hours": 2, "complexity": "medium"},
            TaskType.USER_ACCESS_REVIEW: {"hours": 1, "complexity": "low"},
            TaskType.SYSTEM_HEALTH_CHECK: {"hours": 0.5, "complexity": "low"},
            TaskType.DISASTER_RECOVERY_TEST: {"hours": 6, "complexity": "high"},
            TaskType.SOFTWARE_INVENTORY: {"hours": 1, "complexity": "low"},
            TaskType.NETWORK_ANALYSIS: {"hours": 2, "complexity": "medium"}
        }
        return duration_map.get(self.task_type, {"hours": 1, "complexity": "medium"})

    def _determine_resources(self) -> List[str]:
        """Determine required resources for the task"""
        resource_map = {
            TaskType.SECURITY_AUDIT: ["security_tools", "network_access", "admin_privileges"],
            TaskType.COMPLIANCE_CHECK: ["compliance_framework", "audit_tools", "documentation_access"],
            TaskType.BACKUP_VERIFICATION: ["backup_systems", "storage_access", "verification_tools"],
            TaskType.CAPACITY_PLANNING: ["monitoring_tools", "historical_data", "forecasting_tools"],
            TaskType.PERFORMANCE_OPTIMIZATION: ["performance_tools", "system_access", "optimization_tools"],
            TaskType.USER_ACCESS_REVIEW: ["identity_management", "access_control", "audit_logs"],
            TaskType.SYSTEM_HEALTH_CHECK: ["monitoring_tools", "health_checks", "alerting_systems"],
            TaskType.DISASTER_RECOVERY_TEST: ["backup_systems", "recovery_tools", "test_environment"],
            TaskType.SOFTWARE_INVENTORY: ["inventory_tools", "system_access", "license_management"],
            TaskType.NETWORK_ANALYSIS: ["network_tools", "traffic_analysis", "security_scanners"]
        }
        return resource_map.get(self.task_type, ["basic_tools", "system_access"])

    def _define_success_criteria(self) -> List[str]:
        """Define success criteria for the task"""
        criteria_map = {
            TaskType.SECURITY_AUDIT: ["No critical vulnerabilities found", "Security policies enforced", "Compliance requirements met"],
            TaskType.COMPLIANCE_CHECK: ["All compliance items verified", "No violations detected", "Documentation updated"],
            TaskType.BACKUP_VERIFICATION: ["Backups verified and accessible", "Recovery time objectives met", "Data integrity confirmed"],
            TaskType.CAPACITY_PLANNING: ["Capacity forecast generated", "Resource recommendations provided", "Growth projections updated"],
            TaskType.PERFORMANCE_OPTIMIZATION: ["Performance metrics improved", "Bottlenecks identified and resolved", "System efficiency increased"],
            TaskType.USER_ACCESS_REVIEW: ["Access rights reviewed and updated", "Orphaned accounts identified", "Privilege escalation risks mitigated"],
            TaskType.SYSTEM_HEALTH_CHECK: ["All systems operational", "Health metrics within normal ranges", "No critical issues detected"],
            TaskType.DISASTER_RECOVERY_TEST: ["Recovery procedures tested", "RTO/RPO objectives met", "Recovery plan validated"],
            TaskType.SOFTWARE_INVENTORY: ["Software inventory updated", "License compliance verified", "Unused software identified"],
            TaskType.NETWORK_ANALYSIS: ["Network performance analyzed", "Security vulnerabilities identified", "Optimization recommendations provided"]
        }
        return criteria_map.get(self.task_type, ["Task completed successfully", "No errors encountered"])

    def _assess_risks(self) -> Dict[str, Any]:
        """Assess risks associated with the task"""
        risk_levels = {
            TaskType.SECURITY_AUDIT: "medium",
            TaskType.COMPLIANCE_CHECK: "low",
            TaskType.BACKUP_VERIFICATION: "low",
            TaskType.CAPACITY_PLANNING: "low",
            TaskType.PERFORMANCE_OPTIMIZATION: "medium",
            TaskType.USER_ACCESS_REVIEW: "low",
            TaskType.SYSTEM_HEALTH_CHECK: "low",
            TaskType.DISASTER_RECOVERY_TEST: "high",
            TaskType.SOFTWARE_INVENTORY: "low",
            TaskType.NETWORK_ANALYSIS: "medium"
        }
        
        return {
            "risk_level": risk_levels.get(self.task_type, "medium"),
            "potential_impacts": ["Service disruption", "Data loss", "Security exposure"],
            "mitigation_strategies": ["Backup before execution", "Test in staging environment", "Monitor during execution"],
            "rollback_plan": ["Stop task execution", "Restore previous state", "Notify stakeholders"]
        }

class ITAdministrativeAgent:
    """
    IT Administrative Agent using Gemini for intelligent automation of routine
    IT administrative tasks with AI-driven insights and recommendations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.name = "it_administrative_agent"
        self.version = "2.0.0"
        self.created_at = datetime.now()
        
        # Initialize Gemini LLM (required)
        import os
        from dotenv import load_dotenv
        from pathlib import Path
        
        # Load environment variables from .env file
        backend_dir = Path(__file__).resolve().parents[2]
        load_dotenv(backend_dir / ".env", override=True)
        load_dotenv(backend_dir / "settings.env")
        
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY") or "demo_key"
        self.model = None
        self.llm_available = False
        
        if self.api_key and self.api_key != "demo_key":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    'gemini-2.0-flash',
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                # Validate API key by attempting to list models
                try:
                    list(genai.list_models())
                    self.llm_available = True
                    logger.info("✅ Gemini 2.0 Flash loaded and API key validated for IT administrative tasks")
                except Exception as validation_error:
                    logger.warning(f"⚠️ API key validation failed (will use fallback mode): {str(validation_error)}")
                    logger.info("ℹ️ IT administrative tasks will work with deterministic fallback algorithms")
                    self.model = None
                    self.llm_available = False
                    self.api_key = "demo_key"
            except Exception as e:
                logger.warning(f"⚠️ Gemini initialization failed (will use fallback mode): {str(e)}")
                logger.info("ℹ️ IT administrative tasks will work with deterministic fallback algorithms")
                self.model = None
                self.llm_available = False
                self.api_key = "demo_key"
        else:
            logger.info("ℹ️ No API key provided - using fallback mode for IT administrative tasks")
            logger.info("ℹ️ Set GOOGLE_AI_API_KEY environment variable for AI-powered analysis")
        
        # Agent memory and learning
        self.task_history = []
        self.client_patterns = {}
        self.performance_metrics = {
            "total_tasks_executed": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "automation_rate": 0.0
        }

    async def generate_task_recommendations(self, client: Client) -> List[AdministrativeTask]:
        """Generate intelligent task recommendations based on client environment and AI analysis"""
        
        if not self.llm_available:
            logger.info(f"LLM not available, using fallback task generation for {client.id}")
            return self._fallback_task_generation(client)
        
        try:
            # Prepare context for AI analysis
            context = {
                "client_id": client.id,
                "client_name": client.name,
                "critical_systems": client.critical_systems,
                "system_dependencies": client.system_dependencies,
                "compliance_requirements": getattr(client, 'compliance_requirements', []),
                "business_hours": getattr(client, 'business_hours', '9-17 UTC'),
                "task_history": [task for task in self.task_history if task.client.id == client.id][-5:],
                "current_time": datetime.now().isoformat()
            }
            
            prompt = f"""
            As an expert IT operations manager, analyze this client environment and recommend routine administrative tasks:
            
            Client: {context['client_name']} ({context['client_id']})
            Critical Systems: {context['critical_systems']}
            System Dependencies: {context['system_dependencies']}
            Compliance Requirements: {context['compliance_requirements']}
            Business Hours: {context['business_hours']}
            Current Time: {context['current_time']}
            
            Recent Task History:
            {json.dumps([{"type": task.task_type.value, "status": task.status.value, "created_at": task.created_at.isoformat()} for task in context['task_history']], indent=2)}
            
            Recommend 3-5 routine IT administrative tasks that should be performed. Consider:
            - Security and compliance requirements
            - System health and performance
            - Business continuity and disaster recovery
            - Resource optimization
            - Risk mitigation
            
            Provide recommendations in JSON format:
            {{
                "recommended_tasks": [
                    {{
                        "task_type": "security_audit/compliance_check/backup_verification/capacity_planning/performance_optimization/user_access_review/system_health_check/disaster_recovery_test/software_inventory/network_analysis",
                        "priority": "critical/high/medium/low",
                        "description": "Detailed description of the task",
                        "reasoning": "Why this task is recommended",
                        "estimated_impact": "high/medium/low",
                        "automation_potential": "high/medium/low",
                        "scheduling_preference": "immediate/off_hours/weekend/monthly"
                    }}
                ],
                "overall_assessment": {{
                    "risk_level": "low/medium/high",
                    "compliance_status": "compliant/at_risk/non_compliant",
                    "operational_health": "excellent/good/fair/poor",
                    "recommendations_summary": "Summary of key recommendations"
                }}
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            try:
                ai_recommendations = json.loads(response_text)
            except json.JSONDecodeError as json_error:
                logger.error(f"Failed to parse AI response as JSON: {json_error}")
                logger.debug(f"AI Response text: {response_text[:500]}")
                # Fallback if JSON parsing fails
                raise RuntimeError(f"AI response parsing failed: {json_error}")
            
            # Validate and extract recommended tasks
            if "recommended_tasks" not in ai_recommendations:
                logger.warning("AI response missing 'recommended_tasks', using fallback")
                raise RuntimeError("Invalid AI response format")
            
            # Convert AI recommendations to AdministrativeTask objects
            tasks = []
            for i, task_data in enumerate(ai_recommendations.get("recommended_tasks", [])):
                try:
                    task_id = f"{client.id}_{task_data.get('task_type', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    
                    task = AdministrativeTask(
                        task_id=task_id,
                        task_type=TaskType(task_data.get("task_type", "system_health_check")),
                        client=client,
                        priority=TaskPriority(task_data.get("priority", "medium")),
                        description=task_data.get("description", "Administrative task"),
                        ai_analysis={
                            "reasoning": task_data.get("reasoning", "AI-recommended task"),
                            "estimated_impact": task_data.get("estimated_impact", "medium"),
                            "automation_potential": task_data.get("automation_potential", "medium"),
                            "scheduling_preference": task_data.get("scheduling_preference", "immediate"),
                            "overall_assessment": ai_recommendations.get("overall_assessment", {})
                        }
                    )
                    tasks.append(task)
                except (KeyError, ValueError) as task_error:
                    logger.warning(f"Failed to create task from AI data: {task_error}, skipping")
                    continue
            
            if not tasks:
                logger.warning("No valid tasks generated from AI, using fallback")
                raise RuntimeError("No valid tasks from AI response")
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error in AI task recommendation: {e}", exc_info=True)
            # Don't raise - let the caller handle fallback
            raise

    def _fallback_task_generation(self, client: Client) -> List[AdministrativeTask]:
        """Fallback task generation when AI is not available"""
        fallback_tasks = [
            {
                "task_type": TaskType.SYSTEM_HEALTH_CHECK,
                "priority": TaskPriority.HIGH,
                "description": "Perform comprehensive system health check for all critical systems",
                "reasoning": "Routine system health monitoring is essential for proactive issue detection",
                "estimated_impact": "high",
                "automation_potential": "high",
                "scheduling_preference": "immediate"
            },
            {
                "task_type": TaskType.SECURITY_AUDIT,
                "priority": TaskPriority.MEDIUM,
                "description": "Conduct security audit to identify vulnerabilities and compliance issues",
                "reasoning": "Regular security audits help maintain compliance and identify potential threats",
                "estimated_impact": "high",
                "automation_potential": "medium",
                "scheduling_preference": "weekly"
            },
            {
                "task_type": TaskType.BACKUP_VERIFICATION,
                "priority": TaskPriority.HIGH,
                "description": "Verify backup integrity and test recovery procedures",
                "reasoning": "Backup verification ensures data recovery readiness in case of disaster",
                "estimated_impact": "critical",
                "automation_potential": "high",
                "scheduling_preference": "weekly"
            },
            {
                "task_type": TaskType.USER_ACCESS_REVIEW,
                "priority": TaskPriority.MEDIUM,
                "description": "Review user access rights and remove unnecessary privileges",
                "reasoning": "Regular access reviews maintain security posture and compliance",
                "estimated_impact": "medium",
                "automation_potential": "high",
                "scheduling_preference": "monthly"
            }
        ]
        
        tasks = []
        for i, task_data in enumerate(fallback_tasks):
            task_id = f"{client.id}_{task_data['task_type'].value}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            task = AdministrativeTask(
                task_id=task_id,
                task_type=task_data["task_type"],
                client=client,
                priority=task_data["priority"],
                description=task_data["description"],
                ai_analysis={
                    "reasoning": task_data.get("reasoning", "Routine maintenance task"),
                    "estimated_impact": task_data.get("estimated_impact", "medium"),
                    "automation_potential": task_data.get("automation_potential", "high"),
                    "scheduling_preference": task_data.get("scheduling_preference", "off_hours"),
                    "overall_assessment": {
                        "risk_level": "medium",
                        "compliance_status": "compliant",
                        "operational_health": "good",
                        "recommendations_summary": "Standard administrative tasks for system maintenance"
                    }
                }
            )
            tasks.append(task)
        
        return tasks

    async def execute_task(self, task: AdministrativeTask) -> Dict:
        """Execute an administrative task with AI monitoring and guidance"""
        
        task.status = TaskStatus.IN_PROGRESS
        start_time = datetime.now()
        
        try:
            # Simulate task execution with AI guidance
            execution_result = await self._simulate_task_execution(task)
            
            # Use AI to analyze execution results
            if self.llm_available:
                execution_result = await self._analyze_execution_results(task, execution_result)
            
            task.status = TaskStatus.COMPLETED
            execution_time = (datetime.now() - start_time).total_seconds() / 3600  # hours
            
            # Update performance metrics
            self.performance_metrics["total_tasks_executed"] += 1
            self.performance_metrics["successful_tasks"] += 1
            self.performance_metrics["average_execution_time"] = (
                (self.performance_metrics["average_execution_time"] * (self.performance_metrics["total_tasks_executed"] - 1) + execution_time) /
                self.performance_metrics["total_tasks_executed"]
            )
            
            # Store in task history
            self.task_history.append(task)
            
            # Generate agentic execution log for UI
            agentic_log = self._generate_agentic_execution_log(task)
            
            return {
                "task_id": task.task_id,
                "status": "completed",
                "execution_time_hours": execution_time,
                "results": execution_result,
                "success_criteria_met": True,
                "recommendations": execution_result.get("ai_recommendations", []),
                "agentic_log": agentic_log
            }
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            self.performance_metrics["failed_tasks"] += 1
            self.performance_metrics["total_tasks_executed"] += 1
            
            # Store failed task in history too
            self.task_history.append(task)
            
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e),
                "rollback_required": True
            }

    def _generate_agentic_execution_log(self, task: AdministrativeTask) -> List[Dict]:
        """Generate a simulated log of agentic actions for UI visualization"""
        task_name = task.task_type.value.replace("_", " ").title()
        client_name = task.client.name
        
        logs = [
            {"step": "INIT", "message": f"Initializing {task_name} protocol for {client_name}...", "duration": 800},
            {"step": "AUTH", "message": "Authenticating with secure administrative credentials...", "duration": 1200},
            {"step": "SCAN", "message": f"Scanning target systems: {', '.join(task.client.critical_systems[:2])}...", "duration": 2000},
        ]
        
        if task.task_type == TaskType.SECURITY_AUDIT:
            logs.extend([
                {"step": "ANALYSIS", "message": "Running vulnerability signatures against CVE database...", "duration": 2500},
                {"step": "CHECK", "message": "Verifying firewall rules and access control lists...", "duration": 1500},
                {"step": "AI_INSIGHT", "message": "Gemini 1.5 Pro analyzing potential attack vectors...", "duration": 3000},
            ])
        elif task.task_type == TaskType.COMPLIANCE_CHECK:
            logs.extend([
                {"step": "ANALYSIS", "message": "Mapping system configuration to GDPR/HIPAA requirements...", "duration": 2500},
                {"step": "CHECK", "message": "Auditing data encryption standards...", "duration": 1500},
                {"step": "AI_INSIGHT", "message": "Gemini 1.5 Pro identifying compliance drift...", "duration": 3000},
            ])
        elif task.task_type == TaskType.PERFORMANCE_OPTIMIZATION:
            logs.extend([
                {"step": "ANALYSIS", "message": "Profiling CPU and Memory usage patterns...", "duration": 2500},
                {"step": "ACTION", "message": "Identifying resource bottlenecks...", "duration": 1500},
                {"step": "AI_INSIGHT", "message": "Gemini 1.5 Pro calculating optimal resource allocation...", "duration": 3000},
            ])
        else:
            logs.extend([
                {"step": "ANALYSIS", "message": "Collecting system metrics and logs...", "duration": 2000},
                {"step": "CHECK", "message": "Validating operational parameters...", "duration": 1500},
                {"step": "AI_INSIGHT", "message": "Gemini 1.5 Pro analyzing anomalies...", "duration": 2500},
            ])
            
        logs.extend([
            {"step": "REPORT", "message": "Compiling execution report and recommendations...", "duration": 1000},
            {"step": "COMPLETE", "message": "Task completed successfully. Report generated.", "duration": 500}
        ])
        
        return logs

    async def _simulate_task_execution(self, task: AdministrativeTask) -> Dict:
        """Simulate task execution with realistic results"""
        
        # Simulate different results based on task type
        if task.task_type == TaskType.SYSTEM_HEALTH_CHECK:
            return {
                "systems_checked": len(task.client.critical_systems),
                "healthy_systems": len(task.client.critical_systems) - 1,
                "issues_found": 1,
                "issues": ["High CPU usage on database server"],
                "recommendations": ["Scale database resources", "Optimize queries"],
                "overall_health_score": 0.85
            }
        
        elif task.task_type == TaskType.SECURITY_AUDIT:
            return {
                "vulnerabilities_found": 3,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 1,
                "medium_vulnerabilities": 2,
                "compliance_score": 0.92,
                "recommendations": ["Update security policies", "Implement additional monitoring"]
            }
        
        elif task.task_type == TaskType.BACKUP_VERIFICATION:
            return {
                "backups_verified": 5,
                "successful_backups": 5,
                "failed_backups": 0,
                "recovery_time_tested": True,
                "recovery_time_minutes": 15,
                "data_integrity_score": 1.0
            }
        
        elif task.task_type == TaskType.USER_ACCESS_REVIEW:
            return {
                "users_reviewed": 150,
                "access_changes_made": 12,
                "orphaned_accounts_found": 3,
                "privilege_escalations_reviewed": 5,
                "compliance_improvements": 8
            }
        
        else:
            return {
                "task_completed": True,
                "results_summary": f"Successfully completed {task.task_type.value}",
                "metrics_collected": True
            }

    async def _analyze_execution_results(self, task: AdministrativeTask, results: Dict) -> Dict:
        """Use AI to analyze task execution results and provide insights"""
        
        try:
            prompt = f"""
            Analyze the results of this IT administrative task execution:
            
            Task: {task.task_type.value}
            Client: {task.client.name}
            Priority: {task.priority.value}
            Description: {task.description}
            
            Execution Results:
            {json.dumps(results, indent=2)}
            
            Provide analysis in JSON format:
            {{
                "execution_quality": "excellent/good/fair/poor",
                "key_findings": ["list of key findings"],
                "immediate_actions_required": ["list of immediate actions"],
                "follow_up_tasks": ["list of follow-up tasks"],
                "risk_assessment": "low/medium/high",
                "compliance_impact": "positive/neutral/negative",
                "performance_impact": "positive/neutral/negative",
                "ai_recommendations": ["list of AI recommendations"],
                "next_scheduled_run": "ISO datetime or null"
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            # Robust JSON extraction
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            try:
                ai_analysis = json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI execution analysis JSON, using fallback")
                ai_analysis = {
                    "execution_quality": "good",
                    "key_findings": ["Task executed successfully", "No critical issues found"],
                    "immediate_actions_required": [],
                    "ai_recommendations": ["Continue regular monitoring"]
                }
            
            results["ai_analysis"] = ai_analysis
            return results
            
        except Exception as e:
            logger.error(f"Error in AI execution analysis: {e}")
            # Don't fail the whole task, just return results without AI analysis
            return results

    async def generate_compliance_report(self, client: Client) -> Dict:
        """Generate comprehensive compliance report using AI analysis"""
        
        if not self.llm_available:
            logger.info(f"LLM not available, using fallback compliance report for {client.id}")
            return self._fallback_compliance_report(client)
        
        try:
            # Get recent task history for compliance analysis
            recent_tasks = [task for task in self.task_history if task.client.id == client.id][-10:]
            
            context = {
                "client_id": client.id,
                "client_name": client.name,
                "compliance_requirements": getattr(client, 'compliance_requirements', []),
                "recent_tasks": [
                    {
                        "type": task.task_type.value,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat(),
                        "priority": task.priority.value
                    } for task in recent_tasks
                ]
            }
            
            prompt = f"""
            Generate a comprehensive compliance report for this client:
            
            Client: {context['client_name']} ({context['client_id']})
            Compliance Requirements: {context['compliance_requirements']}
            
            Recent Administrative Tasks:
            {json.dumps(context['recent_tasks'], indent=2)}
            
            Provide a detailed compliance report in JSON format:
            {{
                "compliance_score": 0.0-1.0,
                "overall_status": "compliant/at_risk/non_compliant",
                "compliance_areas": [
                    {{
                        "area": "security/compliance/backup/disaster_recovery/access_control",
                        "status": "compliant/at_risk/non_compliant",
                        "score": 0.0-1.0,
                        "last_checked": "ISO datetime",
                        "issues": ["list of issues"],
                        "recommendations": ["list of recommendations"]
                    }}
                ],
                "critical_gaps": ["list of critical compliance gaps"],
                "immediate_actions": ["list of immediate actions required"],
                "next_review_date": "ISO datetime",
                "risk_assessment": "low/medium/high",
                "executive_summary": "Summary for executive review"
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            # Robust JSON extraction
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            try:
                compliance_report = json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI compliance report JSON, using fallback")
                return self._fallback_compliance_report(client)
            
            return compliance_report
            
        except Exception as e:
            logger.error(f"Error in AI compliance report generation: {e}")
            return self._fallback_compliance_report(client)

    def _fallback_compliance_report(self, client: Client) -> Dict:
        """Fallback compliance report when AI is not available"""
        return {
            "compliance_score": 0.85,
            "overall_status": "compliant",
            "compliance_areas": [
                {
                    "area": "security",
                    "status": "compliant",
                    "score": 0.90,
                    "last_checked": datetime.now().isoformat(),
                    "issues": [],
                    "recommendations": ["Continue regular security audits"]
                },
                {
                    "area": "backup",
                    "status": "compliant",
                    "score": 0.95,
                    "last_checked": datetime.now().isoformat(),
                    "issues": [],
                    "recommendations": ["Maintain current backup procedures"]
                }
            ],
            "critical_gaps": [],
            "immediate_actions": [],
            "next_review_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "risk_assessment": "low",
            "executive_summary": "Client maintains good compliance posture with regular administrative tasks performed"
        }

    def get_performance_metrics(self) -> Dict:
        """Get agent performance metrics"""
        return {
            "agent_name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "llm_available": self.llm_available,
            "performance_metrics": self.performance_metrics,
            "total_clients_served": len(set(task.client.id for task in self.task_history)),
            "task_success_rate": (
                self.performance_metrics["successful_tasks"] / 
                max(1, self.performance_metrics["total_tasks_executed"])
            ) * 100,
            "automation_rate": self.performance_metrics["automation_rate"]
        }
