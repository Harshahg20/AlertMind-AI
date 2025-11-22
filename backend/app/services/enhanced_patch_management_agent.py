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

class PatchSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class PatchStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class CVEAnalysis:
    def __init__(self, cve_id: str, severity: float, product: str, summary: str, 
                 client_impact: float, ai_analysis: Dict):
        self.cve_id = cve_id
        self.severity = severity
        self.product = product
        self.summary = summary
        self.client_impact = client_impact
        self.ai_analysis = ai_analysis
        self.patch_priority = self._calculate_priority()
        self.estimated_effort = self._estimate_effort()
        self.risk_assessment = self._assess_risk()

    def _calculate_priority(self) -> str:
        """Calculate patch priority based on severity and client impact"""
        if self.severity >= 9.0 and self.client_impact >= 0.8:
            return "IMMEDIATE"
        elif self.severity >= 7.0 and self.client_impact >= 0.6:
            return "HIGH"
        elif self.severity >= 5.0 and self.client_impact >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _estimate_effort(self) -> Dict[str, Any]:
        """Estimate patch implementation effort"""
        base_effort = {
            "hours": max(1, int(self.severity * 0.5)),
            "complexity": "high" if self.severity >= 8.0 else "medium" if self.severity >= 6.0 else "low",
            "downtime_minutes": max(5, int(self.severity * 2)),
            "rollback_risk": "high" if self.severity >= 8.0 else "medium" if self.severity >= 6.0 else "low"
        }
        return base_effort

    def _assess_risk(self) -> Dict[str, Any]:
        """Assess patch implementation risk"""
        return {
            "implementation_risk": min(0.95, self.severity / 10.0),
            "business_impact": self.client_impact,
            "rollback_complexity": "high" if self.severity >= 8.0 else "medium",
            "testing_required": self.severity >= 6.0
        }
    
    def calculate_business_impact(self, client: Client) -> Dict[str, Any]:
        """
        Calculate comprehensive business impact score
        KEY FEATURE: Shows ROI of patch management with business metrics
        
        Args:
            client: Client object with business context
            
        Returns:
            Dictionary with business impact metrics including:
            - business_impact_score: Composite score (0-1)
            - priority_level: CRITICAL/HIGH/MEDIUM/LOW
            - affected_users_estimate: Number of users affected
            - estimated_downtime_minutes: Potential downtime
            - revenue_at_risk_usd: Potential revenue loss
            - compliance_risk: Compliance impact assessment
            - recommended_action_timeline: When to patch
            - business_justification: Executive summary
        """
        # Base impact from CVE severity
        severity_impact = self.severity / 10.0
        
        # Client criticality multiplier
        critical_systems = getattr(client, 'critical_systems', [])
        is_critical_system = self.product in critical_systems
        criticality_multiplier = 2.0 if is_critical_system else 1.0
        
        # Exploitability factor from AI analysis
        exploitability_map = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
        exploitability = exploitability_map.get(
            self.ai_analysis.get("exploitability", "medium"), 0.5
        )
        
        # Calculate composite business impact score
        business_impact_score = (
            severity_impact * 0.4 +
            (1.0 if is_critical_system else 0.5) * 0.3 +
            exploitability * 0.3
        ) * min(criticality_multiplier, 1.5)  # Cap multiplier at 1.5
        
        # Estimate business metrics
        affected_users = self._estimate_affected_users(client, is_critical_system)
        estimated_downtime = self._estimate_downtime(self.severity)
        revenue_at_risk = self._calculate_revenue_at_risk(
            affected_users, estimated_downtime, client
        )
        
        # Assess compliance risk
        compliance_risk = self._assess_compliance_risk()
        
        # Get recommended action timeline
        action_timeline = self._get_action_timeline(business_impact_score)
        
        # Generate business justification
        business_justification = self._generate_business_justification(
            business_impact_score, revenue_at_risk, affected_users, estimated_downtime
        )
        
        return {
            "business_impact_score": round(business_impact_score, 2),
            "priority_level": self._get_priority_level(business_impact_score),
            "affected_users_estimate": affected_users,
            "estimated_downtime_minutes": estimated_downtime,
            "revenue_at_risk_usd": revenue_at_risk,
            "compliance_risk": compliance_risk,
            "recommended_action_timeline": action_timeline,
            "business_justification": business_justification,
            "is_critical_system": is_critical_system,
            "exploitability_level": self.ai_analysis.get("exploitability", "medium"),
            "cost_benefit_analysis": {
                "patch_cost_estimate_usd": estimated_downtime * 50,  # $50/min downtime cost
                "risk_cost_estimate_usd": revenue_at_risk,
                "roi_ratio": round(revenue_at_risk / max(estimated_downtime * 50, 1), 2)
            }
        }
    
    def _estimate_affected_users(self, client: Client, is_critical: bool) -> int:
        """Estimate number of users affected by vulnerability"""
        # Base user count (could be from client data in production)
        base_users = 1000  # Assume 1000 users per client
        
        # Adjust based on client tier
        tier_multipliers = {
            "Enterprise": 2.0,
            "Premium": 1.5,
            "Standard": 1.0
        }
        tier = getattr(client, 'tier', 'Standard')
        tier_multiplier = tier_multipliers.get(tier, 1.0)
        
        # Calculate affected users
        if is_critical:
            return int(base_users * tier_multiplier * 0.8)  # 80% of users
        return int(base_users * tier_multiplier * 0.2)  # 20% of users
    
    def _estimate_downtime(self, severity: float) -> int:
        """Estimate potential downtime in minutes based on severity"""
        if severity >= 9.0:
            return 240  # 4 hours for critical vulnerabilities
        elif severity >= 7.0:
            return 120  # 2 hours for high severity
        elif severity >= 5.0:
            return 60   # 1 hour for medium severity
        return 30  # 30 minutes for low severity
    
    def _calculate_revenue_at_risk(self, users: int, downtime_minutes: int, client: Client) -> float:
        """Calculate potential revenue at risk due to vulnerability"""
        # Revenue per user per hour (industry average)
        revenue_per_user_per_hour = 100
        
        # Adjust based on client tier
        tier_revenue_multipliers = {
            "Enterprise": 2.0,
            "Premium": 1.5,
            "Standard": 1.0
        }
        tier = getattr(client, 'tier', 'Standard')
        tier_multiplier = tier_revenue_multipliers.get(tier, 1.0)
        
        hours = downtime_minutes / 60
        revenue_at_risk = users * revenue_per_user_per_hour * hours * tier_multiplier
        
        return round(revenue_at_risk, 2)
    
    def _assess_compliance_risk(self) -> str:
        """Assess compliance risk level based on vulnerability type"""
        compliance_keywords = [
            "data", "privacy", "security", "encryption", "authentication",
            "authorization", "access", "credential", "password", "pii"
        ]
        summary_lower = self.summary.lower()
        
        keyword_matches = sum(1 for keyword in compliance_keywords if keyword in summary_lower)
        
        if keyword_matches >= 3:
            return "CRITICAL - High compliance impact (HIPAA/PCI-DSS/SOC2/GDPR)"
        elif keyword_matches >= 2:
            return "HIGH - Moderate compliance impact"
        elif keyword_matches >= 1:
            return "MEDIUM - Some compliance considerations"
        return "LOW - Minimal compliance impact"
    
    def _get_action_timeline(self, score: float) -> str:
        """Get recommended action timeline based on business impact score"""
        if score >= 0.8:
            return "IMMEDIATE - Patch within 24 hours (emergency maintenance)"
        elif score >= 0.6:
            return "URGENT - Patch within 72 hours (next maintenance window)"
        elif score >= 0.4:
            return "SCHEDULED - Patch within 1 week (regular maintenance)"
        return "ROUTINE - Patch in next monthly maintenance cycle"
    
    def _get_priority_level(self, score: float) -> str:
        """Get priority level from business impact score"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        return "LOW"
    
    def _generate_business_justification(self, score: float, revenue: float, 
                                        users: int, downtime: int) -> str:
        """Generate executive-friendly business justification"""
        return (
            f"Business Impact Score: {score:.2f}/1.0. "
            f"This vulnerability puts ${revenue:,.2f} in revenue at risk, "
            f"affecting approximately {users:,} users with an estimated {downtime} minutes of potential downtime. "
            f"Patching this vulnerability prevents significant business disruption, maintains SLA compliance, "
            f"and protects customer trust. The cost of patching is minimal compared to the potential business impact."
        )


class PatchPlan:
    def __init__(self, client: Client, cve_analyses: List[CVEAnalysis]):
        self.client = client
        self.cve_analyses = cve_analyses
        self.maintenance_windows = []
        self.rollback_plans = {}
        self.created_at = datetime.now()
        self.status = PatchStatus.PENDING

    def generate_maintenance_schedule(self) -> List[Dict]:
        """Generate optimal maintenance windows using AI"""
        # Group patches by priority and system
        immediate_patches = [cve for cve in self.cve_analyses if cve.patch_priority == "IMMEDIATE"]
        high_priority = [cve for cve in self.cve_analyses if cve.patch_priority == "HIGH"]
        medium_priority = [cve for cve in self.cve_analyses if cve.patch_priority == "MEDIUM"]
        low_priority = [cve for cve in self.cve_analyses if cve.patch_priority == "LOW"]

        schedule = []
        
        # Immediate patches - schedule within 24 hours
        if immediate_patches:
            schedule.append({
                "window_id": f"immediate_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "scheduled_time": datetime.now() + timedelta(hours=2),
                "patches": immediate_patches,
                "estimated_duration": sum(cve.estimated_effort["hours"] for cve in immediate_patches),
                "risk_level": "CRITICAL",
                "rollback_plan": self._generate_rollback_plan(immediate_patches)
            })

        # High priority - schedule within 48 hours
        if high_priority:
            schedule.append({
                "window_id": f"high_priority_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "scheduled_time": datetime.now() + timedelta(days=1),
                "patches": high_priority,
                "estimated_duration": sum(cve.estimated_effort["hours"] for cve in high_priority),
                "risk_level": "HIGH",
                "rollback_plan": self._generate_rollback_plan(high_priority)
            })

        # Medium and low priority - schedule in next maintenance window
        if medium_priority or low_priority:
            schedule.append({
                "window_id": f"routine_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "scheduled_time": datetime.now() + timedelta(days=7),
                "patches": medium_priority + low_priority,
                "estimated_duration": sum(cve.estimated_effort["hours"] for cve in medium_priority + low_priority),
                "risk_level": "MEDIUM",
                "rollback_plan": self._generate_rollback_plan(medium_priority + low_priority)
            })

        return schedule

    def _generate_rollback_plan(self, patches: List[CVEAnalysis]) -> Dict:
        """Generate rollback plan for patches"""
        return {
            "rollback_steps": [
                "Stop all services",
                "Restore from backup",
                "Verify system integrity",
                "Restart services",
                "Run health checks"
            ],
            "estimated_rollback_time": sum(p.estimated_effort["downtime_minutes"] for p in patches),
            "rollback_triggers": [
                "Error rate > 5%",
                "Response time > 2x baseline",
                "Critical service failure",
                "Data corruption detected"
            ]
        }

class EnhancedPatchManagementAgent:
    """
    Enhanced Patch Management Agent using Gemini for intelligent CVE analysis,
    patch prioritization, and maintenance window optimization
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.name = "enhanced_patch_management_agent"
        self.version = "2.0.0"
        self.created_at = datetime.now()
        
        # Initialize Gemini LLM with graceful fallback
        import os
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY") or "demo_key"
        self.model = None
        self.llm_available = False
        
        if self.api_key and self.api_key != "demo_key":
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    'gemini-1.5-pro',
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
                    logger.info("✅ Gemini 1.5 Pro loaded and API key validated for enhanced patch management")
                except Exception as validation_error:
                    logger.warning(f"⚠️ API key validation failed (will use fallback mode): {str(validation_error)}")
                    logger.info("ℹ️ Enhanced patch management will work with deterministic fallback algorithms")
                    self.model = None
                    self.llm_available = False
                    self.api_key = "demo_key"
            except Exception as e:
                logger.warning(f"⚠️ Gemini initialization failed (will use fallback mode): {str(e)}")
                logger.info("ℹ️ Enhanced patch management will work with deterministic fallback algorithms")
                self.model = None
                self.llm_available = False
                self.api_key = "demo_key"
        else:
            logger.info("ℹ️ No API key provided - using fallback mode for enhanced patch management")
            logger.info("ℹ️ Set GOOGLE_AI_API_KEY environment variable for AI-powered analysis")
        
        # Agent memory for learning
        self.patch_history = []
        self.success_rates = {}
        self.client_preferences = {}
        self.performance_metrics = {
            "total_patches_analyzed": 0,
            "successful_patches": 0,
            "failed_patches": 0,
            "average_patch_time": 0.0,
            "rollback_rate": 0.0
        }

    async def analyze_cve_with_ai(self, cve_data: Dict, client: Client) -> CVEAnalysis:
        """Analyze CVE using AI to determine client-specific impact and recommendations"""
        
        if not self.llm_available:
            logger.info(f"LLM not available, using fallback analysis for CVE {cve_data.get('cve', 'Unknown')}")
            return self._fallback_cve_analysis(cve_data, client)
        
        try:
            # Prepare context for AI analysis
            context = {
                "cve_id": cve_data.get("cve", "Unknown"),
                "severity": cve_data.get("severity", 0),
                "product": cve_data.get("product", "Unknown"),
                "summary": cve_data.get("summary", "No description available"),
                "client_critical_systems": client.critical_systems,
                "client_system_dependencies": client.system_dependencies,
                "client_business_hours": getattr(client, 'business_hours', '9-17 UTC'),
                "client_compliance_requirements": getattr(client, 'compliance_requirements', [])
            }
            
            prompt = f"""
            As an expert cybersecurity analyst, analyze this CVE for a specific client environment:
            
            CVE: {context['cve_id']}
            Severity: {context['severity']}/10
            Product: {context['product']}
            Description: {context['summary']}
            
            Client Environment:
            - Critical Systems: {context['client_critical_systems']}
            - System Dependencies: {context['client_system_dependencies']}
            - Business Hours: {context['client_business_hours']}
            - Compliance Requirements: {context['client_compliance_requirements']}
            
            Provide a detailed analysis in JSON format with these fields:
            {{
                "client_impact_score": 0.0-1.0,
                "business_impact": "low/medium/high/critical",
                "exploitability": "low/medium/high/critical",
                "patch_urgency": "immediate/high/medium/low",
                "affected_systems": ["list of affected systems"],
                "potential_blast_radius": "description of potential impact",
                "compliance_implications": ["list of compliance issues"],
                "recommended_actions": ["list of specific actions"],
                "testing_requirements": ["list of testing needed"],
                "rollback_complexity": "low/medium/high",
                "maintenance_window_preference": "immediate/off_hours/weekend",
                "risk_mitigation": ["list of risk mitigation strategies"]
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Try to parse JSON
            try:
                ai_analysis = json.loads(response_text)
            except json.JSONDecodeError as json_error:
                logger.warning(f"Failed to parse AI response as JSON: {json_error}. Response: {response_text[:200]}")
                # Use fallback analysis if JSON parsing fails
                logger.info(f"Using fallback CVE analysis for {context['cve_id']}")
                return self._fallback_cve_analysis(cve_data, client)
            
            # Validate required fields
            if not isinstance(ai_analysis, dict):
                logger.warning(f"AI response is not a dictionary, using fallback")
                return self._fallback_cve_analysis(cve_data, client)
            
            # Calculate client impact score
            client_impact = ai_analysis.get("client_impact_score", 0.5)
            if not isinstance(client_impact, (int, float)):
                client_impact = 0.5
            
            # Ensure patch_priority is set correctly
            patch_urgency = ai_analysis.get("patch_urgency", "medium")
            patch_priority_map = {
                "immediate": "IMMEDIATE",
                "high": "HIGH",
                "medium": "MEDIUM",
                "low": "LOW"
            }
            patch_priority = patch_priority_map.get(patch_urgency.lower(), "MEDIUM")
            
            analysis = CVEAnalysis(
                cve_id=context['cve_id'],
                severity=context['severity'],
                product=context['product'],
                summary=context['summary'],
                client_impact=float(client_impact),
                ai_analysis=ai_analysis
            )
            
            # Override patch_priority from AI analysis
            analysis.patch_priority = patch_priority
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI CVE analysis: {e}", exc_info=True)
            # Use fallback instead of raising
            logger.info(f"Falling back to deterministic analysis for {cve_data.get('cve', 'Unknown')}")
            return self._fallback_cve_analysis(cve_data, client)

    def _fallback_cve_analysis(self, cve_data: Dict, client: Client) -> CVEAnalysis:
        """Fallback deterministic CVE analysis when AI is not available"""
        cve_id = cve_data.get("cve_id") or cve_data.get("cve", "Unknown")
        severity = float(cve_data.get("severity", 0))
        product = cve_data.get("product", "Unknown")
        summary = cve_data.get("summary", "No description available")
        
        # Simple impact calculation
        is_critical_system = product in client.critical_systems if hasattr(client, 'critical_systems') else False
        client_impact = min(1.0, severity / 10.0 * (1.5 if is_critical_system else 1.0))
        
        ai_analysis = {
            "client_impact_score": float(client_impact),
            "business_impact": "critical" if client_impact > 0.8 else "high" if client_impact > 0.6 else "medium" if client_impact > 0.4 else "low",
            "exploitability": "high" if severity > 8.0 else "medium" if severity > 6.0 else "low",
            "patch_urgency": "immediate" if severity > 9.0 else "high" if severity > 7.0 else "medium" if severity > 5.0 else "low",
            "affected_systems": [product] if is_critical_system else [],
            "potential_blast_radius": f"May affect {product} and dependent systems",
            "compliance_implications": ["Security compliance risk"] if severity > 7.0 else [],
            "recommended_actions": [f"Patch {product} within 24-48 hours"] if severity > 7.0 else [f"Schedule patch for {product}"],
            "testing_requirements": ["Full system testing"] if severity > 7.0 else ["Basic functionality testing"],
            "rollback_complexity": "high" if severity > 8.0 else "medium" if severity > 6.0 else "low",
            "maintenance_window_preference": "immediate" if severity > 9.0 else "off_hours",
            "risk_mitigation": ["Backup before patching", "Test in staging environment"]
        }
        
        analysis = CVEAnalysis(
            cve_id=str(cve_id),
            severity=float(severity),
            product=str(product),
            summary=str(summary),
            client_impact=float(client_impact),
            ai_analysis=ai_analysis
        )
        
        return analysis

    async def generate_patch_plan(self, client: Client, cve_list: List[Dict]) -> PatchPlan:
        """Generate comprehensive patch plan using AI analysis"""
        
        # Analyze each CVE with AI
        cve_analyses = []
        for cve_data in cve_list:
            analysis = await self.analyze_cve_with_ai(cve_data, client)
            cve_analyses.append(analysis)
        
        # Create patch plan
        patch_plan = PatchPlan(client, cve_analyses)
        
        # Generate maintenance schedule
        patch_plan.maintenance_windows = patch_plan.generate_maintenance_schedule()
        
        # Update performance metrics
        self.performance_metrics["total_patches_analyzed"] += len(cve_analyses)
        
        return patch_plan

    async def optimize_maintenance_windows(self, patch_plan: PatchPlan) -> Dict:
        """Use AI to optimize maintenance windows based on client patterns"""
        
        if not self.llm_available:
            logger.info(f"LLM not available, using fallback optimization for {patch_plan.client.id}")
            return self._fallback_optimization(patch_plan)
        
        try:
            context = {
                "client_id": patch_plan.client.id,
                "client_name": patch_plan.client.name,
                "maintenance_windows": patch_plan.maintenance_windows,
                "patch_history": self.patch_history[-10:],  # Last 10 patches
                "success_rates": self.success_rates.get(patch_plan.client.id, {}),
                "business_hours": getattr(patch_plan.client, 'business_hours', '9-17 UTC')
            }
            
            prompt = f"""
            As an expert IT operations manager, optimize these maintenance windows for maximum success:
            
            Client: {context['client_name']} ({context['client_id']})
            Business Hours: {context['business_hours']}
            
            Current Maintenance Windows:
            {json.dumps(context['maintenance_windows'], indent=2, default=str)}
            
            Historical Performance:
            {json.dumps(context['success_rates'], indent=2)}
            
            Provide optimized maintenance windows in JSON format:
            {{
                "optimized_windows": [
                    {{
                        "window_id": "string",
                        "optimized_time": "ISO datetime",
                        "reasoning": "explanation for timing",
                        "success_probability": 0.0-1.0,
                        "risk_mitigation": ["list of additional mitigations"],
                        "rollback_plan": {{"steps": [], "triggers": []}}
                    }}
                ],
                "overall_risk_assessment": "low/medium/high",
                "recommended_approach": "aggressive/conservative/balanced",
                "success_prediction": 0.0-1.0
            }}
            """
            
            response = await self.model.generate_content_async(prompt)
            optimization = json.loads(response.text)
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error in maintenance window optimization: {e}")
            raise

    def _fallback_optimization(self, patch_plan: PatchPlan) -> Dict:
        """Fallback optimization when AI is not available"""
        optimized_windows = []
        
        for window in patch_plan.maintenance_windows:
            # Simple optimization: move to off-hours if possible
            scheduled_time = window["scheduled_time"]
            if scheduled_time.hour >= 9 and scheduled_time.hour <= 17:
                # Move to off-hours (2 AM)
                optimized_time = scheduled_time.replace(hour=2, minute=0)
            else:
                optimized_time = scheduled_time
            
            optimized_windows.append({
                "window_id": window["window_id"],
                "optimized_time": optimized_time.isoformat(),
                "reasoning": "Moved to off-hours to minimize business impact",
                "success_probability": 0.85,
                "risk_mitigation": ["Backup before patching", "Monitor during implementation"],
                "rollback_plan": window["rollback_plan"]
            })
        
        return {
            "optimized_windows": optimized_windows,
            "overall_risk_assessment": "medium",
            "recommended_approach": "balanced",
            "success_prediction": 0.85
        }

    async def monitor_patch_execution(self, window_id: str, client: Client) -> Dict:
        """Monitor patch execution and provide real-time insights"""
        
        # Simulate monitoring data
        monitoring_data = {
            "window_id": window_id,
            "client_id": client.id,
            "status": "in_progress",
            "progress_percentage": 65,
            "current_step": "Applying security patches",
            "metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_io": 23.1,
                "network_latency": 12.5,
                "error_rate": 0.1
            },
            "alerts": [],
            "estimated_completion": datetime.now() + timedelta(minutes=15),
            "rollback_triggered": False
        }
        
        # Use AI to analyze monitoring data
        if self.llm_available:
            try:
                prompt = f"""
                Analyze this patch execution monitoring data and provide insights:
                
                {json.dumps(monitoring_data, indent=2, default=str)}
                
                Provide analysis in JSON format:
                {{
                    "execution_health": "good/warning/critical",
                    "risk_level": "low/medium/high",
                    "recommendations": ["list of recommendations"],
                    "should_continue": true/false,
                    "rollback_advised": true/false,
                    "estimated_success_probability": 0.0-1.0
                }}
                """
                
                response = await self.model.generate_content_async(prompt)
                ai_analysis = json.loads(response.text)
                monitoring_data["ai_analysis"] = ai_analysis
                
            except Exception as e:
                logger.error(f"Error in patch execution monitoring: {e}")
                raise
        
        return monitoring_data

    def get_performance_metrics(self) -> Dict:
        """Get agent performance metrics"""
        return {
            "agent_name": self.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "llm_available": self.llm_available,
            "performance_metrics": self.performance_metrics,
            "total_clients_served": len(self.client_preferences),
            "patch_success_rate": (
                self.performance_metrics["successful_patches"] / 
                max(1, self.performance_metrics["total_patches_analyzed"])
            ) * 100
        }
