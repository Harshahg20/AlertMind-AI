import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.alert import Alert, Client, CascadePrediction
from app.services.cascade_prediction import CascadePredictionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cascade Prediction Agent Prompt
PREDICTION_PROMPT = """
You are the Cascade Prediction Agent.

Input: historical metrics + correlated alerts.
Task: predict whether a cascade failure will occur within the next 30 minutes.

Respond as JSON:
{ "predicted_in": <minutes>, "confidence": <0-1>, "root_causes": ["..."], "summary": "..." }

Base your judgment on patterns of CPU, memory, I/O spikes and temporal ordering.

Analyze the following data:
- Current alert patterns and severity levels
- System dependencies and infrastructure topology
- Historical cascade patterns and timing
- Cross-client learning insights
- Prevention rule effectiveness

Focus on:
1. Temporal correlation between alerts (time-based patterns)
2. System dependency chains and failure propagation
3. Resource exhaustion indicators (CPU, memory, I/O, network)
4. Service degradation patterns
5. Historical success rates of prevention actions

Provide actionable insights for immediate prevention.
"""

class Agent:
    """Base Agent class for all prediction agents"""
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
    
    async def run(self, *args, **kwargs):
        """Override in subclasses"""
        raise NotImplementedError

class CascadePredictionAgent(Agent):
    """
    Advanced Cascade Prediction Agent using LLM reasoning with numeric prediction engine
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("cascade_prediction_agent")
        
        # Initialize LLM (Gemini 1.5 Pro for reasoning)
        self.api_key = api_key or "demo_key"
        if self.api_key != "demo_key":
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash", 
                temperature=0.2,
                google_api_key=self.api_key
            )
        else:
            self.llm = None
            logger.warning("Using mock LLM responses - set GOOGLE_AI_API_KEY for real predictions")
        
        # Initialize numeric prediction engine
        self.prediction_engine = CascadePredictionEngine()
        
        # Agent memory for learning
        self.incident_memory = []
        self.pattern_effectiveness = {}
        
    async def run(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent execution method
        
        Args:
            correlated_data: Dictionary containing alerts, client info, and historical data
            
        Returns:
            Enhanced prediction with LLM reasoning
        """
        try:
            # Extract data from correlated_data
            alerts = correlated_data.get("alerts", [])
            client = correlated_data.get("client")
            historical_data = correlated_data.get("historical_data", [])
            
            if not alerts or not client:
                raise ValueError("Missing required data: alerts and client")
            
            # Step 1: Get numeric prediction from FastAPI backend
            engine_output = await self._get_numeric_prediction(correlated_data)
            
            # Step 2: Prepare context for LLM reasoning
            analysis_context = self._prepare_llm_context(alerts, client, historical_data, engine_output)
            
            # Step 3: Get LLM reasoning and insights
            if self.llm:
                llm_reasoning = await self._get_llm_reasoning(analysis_context)
            else:
                llm_reasoning = self._get_mock_llm_reasoning(analysis_context)
            
            # Step 4: Combine numeric prediction with LLM insights
            enhanced_prediction = self._combine_predictions(engine_output, llm_reasoning, alerts, client)
            
            # Step 5: Update agent memory for learning
            self._update_agent_memory(alerts, enhanced_prediction, client.id)
            
            return enhanced_prediction
            
        except Exception as e:
            logger.error(f"Cascade Prediction Agent failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._fallback_prediction(correlated_data)
    
    async def _get_numeric_prediction(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get numeric prediction from the existing FastAPI backend"""
        try:
            # Use the existing prediction engine
            alerts = correlated_data.get("alerts", [])
            client = correlated_data.get("client")
            
            if not alerts or not client:
                return {"error": "Missing alerts or client data"}
            
            # Convert dictionaries to Alert objects if needed
            if alerts and isinstance(alerts[0], dict):
                # Convert dict alerts to Alert objects for the prediction engine
                from app.models.alert import Alert, SeverityLevel, AlertCategory
                alert_objects = []
                for alert_dict in alerts:
                    alert_obj = Alert(
                        id=alert_dict.get("id", "unknown"),
                        client_id=alert_dict.get("client_id", client.id),
                        client_name=alert_dict.get("client_name", client.name),
                        system=alert_dict.get("system", "unknown"),
                        severity=SeverityLevel(alert_dict.get("severity", "info")),
                        message=alert_dict.get("message", "No message"),
                        category=AlertCategory(alert_dict.get("category", "system")),
                        timestamp=datetime.fromisoformat(alert_dict.get("timestamp", datetime.now().isoformat()).replace('Z', '+00:00')),
                        cascade_risk=alert_dict.get("cascade_risk", 0.0),
                        is_correlated=alert_dict.get("is_correlated", False)
                    )
                    alert_objects.append(alert_obj)
                predictions = self.prediction_engine.predict_cascade(alert_objects, client)
            else:
                # Use alerts as-is if they're already Alert objects
                predictions = self.prediction_engine.predict_cascade(alerts, client)
            
            if not predictions:
                return {
                    "cascade_predicted": False,
                    "confidence": 0.0,
                    "time_to_cascade": 0,
                    "affected_systems": [],
                    "prevention_actions": []
                }
            
            # Aggregate predictions
            primary_prediction = predictions[0]  # Highest confidence prediction
            
            return {
                "cascade_predicted": True,
                "confidence": primary_prediction.prediction_confidence,
                "time_to_cascade": primary_prediction.time_to_cascade_minutes,
                "affected_systems": primary_prediction.predicted_cascade_systems,
                "prevention_actions": primary_prediction.prevention_actions,
                "pattern_matched": primary_prediction.pattern_matched,
                "all_predictions": [
                    {
                        "alert_id": p.alert_id,
                        "confidence": p.prediction_confidence,
                        "time_to_cascade": p.time_to_cascade_minutes,
                        "affected_systems": p.predicted_cascade_systems
                    } for p in predictions
                ]
            }
            
        except Exception as e:
            logger.error(f"Numeric prediction failed: {e}")
            return {"error": str(e)}
    
    def _prepare_llm_context(self, alerts: List[Alert], client: Client, 
                           historical_data: List[Dict], engine_output: Dict) -> str:
        """Prepare comprehensive context for LLM analysis"""
        
        current_time = datetime.now()
        
        # Current alert analysis
        alert_analysis = []
        for alert in alerts:
            if isinstance(alert, dict):
                # Handle dictionary format
                timestamp = datetime.fromisoformat(alert.get("timestamp", current_time.isoformat()).replace('Z', '+00:00'))
                time_diff = (current_time - timestamp).total_seconds() / 60
                alert_analysis.append({
                    "system": alert.get("system", "unknown"),
                    "severity": alert.get("severity", "info"),
                    "category": alert.get("category", "system"),
                    "message": alert.get("message", "No message"),
                    "minutes_ago": int(time_diff),
                    "cascade_risk": alert.get("cascade_risk", 0.0),
                    "is_correlated": alert.get("is_correlated", False)
                })
            else:
                # Handle Alert object format
                time_diff = (current_time - alert.timestamp).total_seconds() / 60
                alert_analysis.append({
                    "system": alert.system,
                    "severity": alert.severity,
                    "category": alert.category,
                    "message": alert.message,
                    "minutes_ago": int(time_diff),
                    "cascade_risk": alert.cascade_risk,
                    "is_correlated": alert.is_correlated
                })
        
        # Client infrastructure context
        client_context = {
            "name": client.name,
            "tier": client.tier,
            "environment": client.environment,
            "critical_systems": client.critical_systems,
            "system_dependencies": client.system_dependencies
        }
        
        # Historical pattern context
        historical_context = []
        for incident in historical_data[-5:]:  # Last 5 incidents
            historical_context.append({
                "pattern": incident.get("pattern", "unknown"),
                "cascade_time": incident.get("cascade_time_minutes", 0),
                "affected_systems": incident.get("affected_systems", []),
                "resolution_time": incident.get("resolution_time_minutes", 0),
                "success": incident.get("prevention_successful", False)
            })
        
        # Cross-client insights
        cross_client_insights = self._get_cross_client_insights()
        
        context = f"""
{PREDICTION_PROMPT}

CURRENT SITUATION:
Client: {client.name} ({client.tier} tier, {client.environment} environment)
Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}

CURRENT ALERTS ({len(alerts)} total):
{json.dumps(alert_analysis, indent=2)}

CLIENT INFRASTRUCTURE:
{json.dumps(client_context, indent=2)}

NUMERIC ENGINE OUTPUT:
{json.dumps(engine_output, indent=2)}

HISTORICAL PATTERNS:
{json.dumps(historical_context, indent=2)}

CROSS-CLIENT INSIGHTS:
{json.dumps(cross_client_insights, indent=2)}

AGENT MEMORY PATTERNS:
{json.dumps(self._get_agent_patterns(), indent=2)}

TASK: Analyze this data and provide enhanced cascade prediction with reasoning.
Focus on temporal patterns, system dependencies, and prevention effectiveness.
"""
        
        return context
    
    async def _get_llm_reasoning(self, context: str) -> Dict[str, Any]:
        """Get LLM reasoning and insights"""
        # Check if LLM is available
        if not self.llm:
            logger.info("LLM not available, using mock reasoning")
            return self._get_mock_llm_reasoning(context)
        
        try:
            response = await self.llm.ainvoke(context)
            response_text = response.content.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Try to parse as JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If not valid JSON, extract key information
                return self._parse_text_response(response_text)
                
        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
            return self._get_mock_llm_reasoning(context)
    
    def _get_mock_llm_reasoning(self, context: str) -> Dict[str, Any]:
        """Generate mock LLM reasoning for demo purposes"""
        
        # Extract key metrics from context
        alert_count = context.count('"severity"')
        critical_count = context.count('"critical"')
        warning_count = context.count('"warning"')
        
        # Simulate intelligent analysis
        if critical_count > 0:
            predicted_in = 8 + (critical_count * 3)
            confidence = min(0.95, 0.7 + (critical_count * 0.1))
            urgency = "critical"
        elif warning_count > 2:
            predicted_in = 15 + (warning_count * 2)
            confidence = min(0.85, 0.6 + (warning_count * 0.05))
            urgency = "high"
        else:
            predicted_in = 25
            confidence = 0.4
            urgency = "medium"
        
        return {
            "predicted_in": predicted_in,
            "confidence": round(confidence, 2),
            "root_causes": [
                "Resource exhaustion detected in critical systems",
                "Temporal correlation between alerts indicates cascade pattern",
                "System dependencies show high failure propagation risk"
            ],
            "summary": f"LLM analysis indicates {urgency} cascade risk with {confidence*100:.0f}% confidence. Predicted cascade within {predicted_in} minutes based on current alert patterns and system dependencies. Immediate prevention actions recommended.",
            "reasoning": {
                "temporal_analysis": f"Detected {alert_count} alerts with temporal clustering pattern",
                "dependency_analysis": "Critical system dependencies show high cascade risk",
                "resource_analysis": "CPU, memory, and I/O patterns indicate resource exhaustion",
                "prevention_effectiveness": "Historical data shows 85% success rate for immediate actions"
            },
            "urgency_level": urgency,
            "recommended_immediate_actions": [
                "Scale critical system resources immediately",
                "Activate failover mechanisms for dependent systems",
                "Clear resource bottlenecks (connections, cache, etc.)"
            ]
        }
    
    def _parse_text_response(self, response_text: str) -> Dict[str, Any]:
        """Parse non-JSON LLM response into structured format"""
        
        # Extract key information from text response
        lines = response_text.split('\n')
        
        # Look for key patterns
        predicted_in = 15  # default
        confidence = 0.7   # default
        root_causes = []
        summary = response_text[:200] + "..." if len(response_text) > 200 else response_text
        
        for line in lines:
            if "predicted" in line.lower() and "minute" in line.lower():
                # Extract time
                import re
                time_match = re.search(r'(\d+)\s*minute', line.lower())
                if time_match:
                    predicted_in = int(time_match.group(1))
            
            if "confidence" in line.lower():
                # Extract confidence
                conf_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                if conf_match:
                    confidence = float(conf_match.group(1)) / 100
            
            if "cause" in line.lower() or "reason" in line.lower():
                root_causes.append(line.strip())
        
        return {
            "predicted_in": predicted_in,
            "confidence": confidence,
            "root_causes": root_causes[:3] if root_causes else ["Analysis indicates cascade risk"],
            "summary": summary,
            "reasoning": {"text_analysis": response_text},
            "urgency_level": "high" if confidence > 0.7 else "medium"
        }
    
    def _combine_predictions(self, engine_output: Dict, llm_reasoning: Dict, 
                           alerts: List[Alert], client: Client) -> Dict[str, Any]:
        """Combine numeric prediction with LLM reasoning"""
        
        # Extract key metrics
        numeric_confidence = engine_output.get("confidence", 0.0)
        llm_confidence = llm_reasoning.get("confidence", 0.0)
        
        # Weighted combination (70% numeric, 30% LLM for confidence)
        combined_confidence = (numeric_confidence * 0.7) + (llm_confidence * 0.3)
        
        # Use LLM time prediction if more recent/aligned with patterns
        predicted_time = llm_reasoning.get("predicted_in", engine_output.get("time_to_cascade", 15))
        
        # Combine affected systems
        numeric_systems = engine_output.get("affected_systems", [])
        llm_systems = llm_reasoning.get("reasoning", {}).get("dependency_analysis", "")
        
        # Enhanced prevention actions
        prevention_actions = engine_output.get("prevention_actions", [])
        llm_actions = llm_reasoning.get("recommended_immediate_actions", [])
        combined_actions = list(set(prevention_actions + llm_actions))
        
        # Determine urgency
        urgency = llm_reasoning.get("urgency_level", "medium")
        if combined_confidence > 0.8 and predicted_time < 10:
            urgency = "critical"
        elif combined_confidence > 0.6 and predicted_time < 20:
            urgency = "high"
        
        return {
            "predicted_in": predicted_time,
            "confidence": round(combined_confidence, 2),
            "root_causes": llm_reasoning.get("root_causes", ["System analysis indicates cascade risk"]),
            "summary": llm_reasoning.get("summary", "Cascade prediction analysis completed"),
            "explanation": llm_reasoning.get("reasoning", {}),
            "urgency_level": urgency,
            "affected_systems": numeric_systems,
            "prevention_actions": combined_actions,
            "pattern_matched": engine_output.get("pattern_matched"),
            "numeric_engine_output": engine_output,
            "llm_reasoning": llm_reasoning,
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "alerts_analyzed": len(alerts),
                "client_id": client.id,
                "combined_confidence": combined_confidence
            }
        }
    
    def _update_agent_memory(self, alerts: List[Alert], prediction: Dict, client_id: str):
        """Update agent memory for learning and pattern recognition"""
        
        # Store incident for learning
        incident_record = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "alerts": [{"system": a.get("system") if isinstance(a, dict) else a.system, 
                       "severity": a.get("severity") if isinstance(a, dict) else a.severity, 
                       "category": a.get("category") if isinstance(a, dict) else a.category} for a in alerts],
            "prediction": prediction,
            "confidence": prediction.get("confidence", 0.0),
            "urgency": prediction.get("urgency_level", "medium")
        }
        
        self.incident_memory.append(incident_record)
        
        # Keep memory size manageable
        if len(self.incident_memory) > 500:
            self.incident_memory = self.incident_memory[-400:]
        
        # Update pattern effectiveness
        pattern_key = f"{len(alerts)}_alerts_{prediction.get('urgency_level', 'unknown')}"
        if pattern_key not in self.pattern_effectiveness:
            self.pattern_effectiveness[pattern_key] = []
        
        self.pattern_effectiveness[pattern_key].append({
            "confidence": prediction.get("confidence", 0.0),
            "timestamp": datetime.now().isoformat(),
            "prevention_actions": prediction.get("prevention_actions", [])
        })
    
    def _get_cross_client_insights(self) -> Dict[str, Any]:
        """Get cross-client learning insights"""
        
        if not self.incident_memory:
            return {"patterns_learned": 0, "confidence_improvement": 0}
        
        # Analyze patterns across clients
        client_patterns = {}
        for incident in self.incident_memory[-50:]:
            client_id = incident["client_id"]
            if client_id not in client_patterns:
                client_patterns[client_id] = []
            client_patterns[client_id].append(incident)
        
        return {
            "patterns_learned": len(self.pattern_effectiveness),
            "clients_analyzed": len(client_patterns),
            "confidence_improvement": min(0.3, len(self.incident_memory) / 1000),
            "most_effective_patterns": list(self.pattern_effectiveness.keys())[:3],
            "average_confidence": sum(i["confidence"] for i in self.incident_memory[-20:]) / min(20, len(self.incident_memory))
        }
    
    def _get_agent_patterns(self) -> Dict[str, Any]:
        """Get learned patterns from agent memory"""
        
        if not self.pattern_effectiveness:
            return {"no_patterns": True}
        
        # Analyze pattern effectiveness
        pattern_analysis = {}
        for pattern, incidents in self.pattern_effectiveness.items():
            if incidents:
                avg_confidence = sum(i["confidence"] for i in incidents) / len(incidents)
                pattern_analysis[pattern] = {
                    "occurrences": len(incidents),
                    "average_confidence": round(avg_confidence, 2),
                    "last_seen": incidents[-1]["timestamp"]
                }
        
        return pattern_analysis
    
    def _fallback_prediction(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback prediction when agent fails"""
        
        alerts = correlated_data.get("alerts", [])
        client = correlated_data.get("client")
        
        # Handle both Alert objects and dictionaries
        if alerts and isinstance(alerts[0], dict):
            critical_count = len([a for a in alerts if a.get("severity") == "critical"])
            avg_cascade_risk = sum(a.get("cascade_risk", 0) for a in alerts) / len(alerts) if alerts else 0
        else:
            critical_count = len([a for a in alerts if a.severity == "critical"])
            avg_cascade_risk = sum(a.cascade_risk for a in alerts) / len(alerts) if alerts else 0
        
        return {
            "predicted_in": 20,
            "confidence": min(0.7, avg_cascade_risk),
            "root_causes": ["Fallback analysis: System monitoring indicates potential issues"],
            "summary": f"Fallback prediction: {critical_count} critical alerts detected. Manual investigation recommended.",
            "explanation": {"fallback_mode": True, "reason": "Agent processing failed"},
            "urgency_level": "high" if critical_count > 0 else "medium",
            "affected_systems": [],
            "prevention_actions": ["Manual investigation required", "Contact senior technician"],
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "fallback_mode": True
            }
        }

# Factory function to create agent instances
def create_cascade_prediction_agent(api_key: Optional[str] = None) -> CascadePredictionAgent:
    """Factory function to create CascadePredictionAgent instances"""
    return CascadePredictionAgent(api_key=api_key)
