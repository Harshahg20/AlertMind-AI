import vertexai
from vertexai.preview.generative_models import GenerativeModel
import json
import logging
import os

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, project_id: str = "alert-mind", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.model = None
        self._initialize()

    def _initialize(self):
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel("gemini-1.5-flash-001")
            logger.info(f"✅ GeminiService initialized with project {self.project_id}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GeminiService: {e}")
            self.model = None

    async def generate_patch_analysis(self, cve_details: dict, client_context: dict) -> dict:
        if not self.model:
            logger.warning("Gemini model not initialized, returning empty dict")
            return {}

        prompt = self._build_prompt(cve_details, client_context)
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Parse JSON response
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback if strict JSON mode fails or returns markdown
                text = response.text
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                return json.loads(text)
                
        except Exception as e:
            logger.error(f"Error generating patch analysis: {e}")
            return {}

    def _build_prompt(self, cve: dict, client: dict) -> str:
        return f"""
        You are an expert Cybersecurity Analyst. Analyze this CVE for the specific client environment.
        
        CVE Details:
        ID: {cve.get('cve_id', 'Unknown')}
        Severity: {cve.get('severity', 'Unknown')}
        Product: {cve.get('product', 'Unknown')}
        Description: {cve.get('summary', '')}
        
        Client Context:
        Industry: {client.get('industry', 'Technology')}
        Critical Systems: {client.get('critical_systems', [])}
        
        Provide a detailed analysis in JSON format with the following structure:
        {{
            "client_impact_score": 0.0-1.0,
            "business_impact": "low/medium/high/critical",
            "exploitability": "low/medium/high/critical",
            "patch_urgency": "immediate/high/medium/low",
            "executive_summary": "2-3 sentences for the C-suite",
            "strategic_analysis": "Strategic implications paragraph",
            "compliance_badges": ["list", "of", "regulations"],
            "probability_of_exploitation_percentage": 0-100,
            "blast_radius_details": {{
                "direct_affected_systems": [],
                "indirect_affected_systems": [],
                "estimated_outage_impact": "description"
            }},
            "affected_systems": [],
            "potential_blast_radius": "summary description",
            "compliance_implications": [],
            "recommended_actions": [],
            "detailed_recommendation_steps": [
                {{"step": "Step Name", "description": "Details", "estimated_time": "Duration", "role": "Role"}}
            ],
            "testing_requirements": [],
            "rollback_complexity": "low/medium/high",
            "maintenance_window_preference": "immediate/off_hours/weekend",
            "risk_mitigation": [],
            "realistic_implementation_time_hours": 0.0,
            "financial_impact_analysis": {{
                "estimated_cost_of_exploitation": "$Amount",
                "cost_of_inaction": "Description",
                "patching_roi": "Description",
                "operational_risk_score": 0-100
            }},
            "what_if_scenario": "Scenario description"
        }}
        """

    async def optimize_maintenance_schedule(self, context: dict) -> dict:
        if not self.model:
            return {}
            
        prompt = f"""
        As an expert DevSecOps Architect, optimize these maintenance windows.
        
        Client: {context.get('client_name')}
        Current Windows: {json.dumps(context.get('maintenance_windows', []), default=str)}
        History: {json.dumps(context.get('patch_history', []), default=str)}
        
        Provide an optimized schedule in JSON format:
        {{
            "optimized_windows": [
                {{
                    "window_id": "id",
                    "optimized_time": "ISO datetime",
                    "reasoning": "explanation",
                    "success_probability": 0.0-1.0,
                    "risk_mitigation": [],
                    "rollback_plan": {{"steps": [], "triggers": []}},
                    "resource_requirements": [],
                    "security_checks": {{"pre_patch": [], "post_patch": []}}
                }}
            ],
            "overall_risk_assessment": "low/medium/high",
            "recommended_approach": "aggressive/conservative/balanced",
            "success_prediction": 0.0-1.0,
            "optimization_summary": "summary",
            "threat_window_analysis": {{
                "risk_of_delay": "High/Medium/Low",
                "exploitation_probability_next_24h": "15%",
                "description": "analysis"
            }},
            "security_dependency_check": {{
                "conflicts_detected": false,
                "dependencies": [],
                "notes": "notes"
            }},
            "resource_impact_forecast": {{
                "cpu_spike_estimate": "85%",
                "memory_usage_estimate": "4GB",
                "network_bandwidth_impact": "High"
            }},
            "risk_trajectory": [
                {{"time": "Current", "risk_score": 85, "label": "Pre-Patch"}},
                {{"time": "Window Start", "risk_score": 85, "label": "Maintenance Begins"}},
                {{"time": "Patch Applied", "risk_score": 45, "label": "Vulnerability Mitigated"}},
                {{"time": "Verified", "risk_score": 10, "label": "Post-Verification"}}
            ],
            "conflicts_avoided": [
                {{"conflict": "Weekly Backup", "resolution": "Shifted window by 2 hours"}},
                {{"conflict": "High Traffic Period", "resolution": "Scheduled for off-peak"}}
            ],
            "detailed_resource_allocation": [
                {{"role": "DevOps Lead", "hours": 2, "status": "Available"}},
                {{"role": "DBA", "hours": 1, "status": "On-Call"}}
            ]
        }}
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return {}
