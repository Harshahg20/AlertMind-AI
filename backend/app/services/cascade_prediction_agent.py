import asyncio
import json
import logging
import traceback
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import httpx
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
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
        import os
        from dotenv import load_dotenv
        from pathlib import Path
        
        # Load environment variables from .env file
        backend_dir = Path(__file__).resolve().parents[2]
        load_dotenv(backend_dir / ".env")
        load_dotenv(backend_dir / "settings.env")
        
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        print("=" * 60)
        print("GOOGLE_AI_API_KEY:", self.api_key)
        if self.api_key:
            print(f"API Key length: {len(self.api_key)} characters")
            print(f"API Key preview: {self.api_key[:10]}...{self.api_key[-4:]}")
        print("=" * 60)
        if not self.api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY not set. Configure a valid Google AI API key.")
        genai.configure(api_key=self.api_key)
        self.llm = genai.GenerativeModel('gemini-1.5-flash')
        
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
            
            # Step 3: Get LLM reasoning and insights (no mock fallback)
            llm_reasoning = await self._get_llm_reasoning(analysis_context)
            
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
    
    async def _get_llm_reasoning(self, context: str, max_retries: int = 3) -> Dict[str, Any]:
        """Get LLM reasoning and insights with retry logic for quota errors"""
        for attempt in range(max_retries):
            try:
                response = await self.llm.generate_content_async(context)
                response_text = response.text.strip()
                
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
                    
            except google_exceptions.ResourceExhausted as e:
                # Extract retry delay from error message if available
                retry_delay = 20  # Default 20 seconds
                
                # Try to extract retry delay from error message
                error_str = str(e)
                if "retry_delay" in error_str or "Please retry in" in error_str:
                    try:
                        # Extract seconds from error message (format: "Please retry in X.XXs")
                        import re
                        match = re.search(r'retry in ([\d.]+)s', error_str)
                        if match:
                            retry_delay = float(match.group(1)) + 2  # Add 2 seconds buffer
                    except:
                        pass
                
                if attempt < max_retries - 1:
                    wait_time = min(retry_delay * (2 ** attempt), 60)  # Exponential backoff, max 60s
                    logger.warning(
                        f"API quota exceeded (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {wait_time:.1f} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"LLM reasoning failed after {max_retries} attempts: {e}")
                    # Return fallback response when quota is exhausted
                    return {
                        "reasoning": "API quota limit reached. Using fallback prediction.",
                        "confidence_impact": -0.1,
                        "quota_exceeded": True
                    }
            except Exception as e:
                logger.error(f"LLM reasoning failed: {e}")
                raise
    
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
            "average_confidence": sum(i.get("confidence", 0.5) for i in self.incident_memory[-20:]) / min(20, len(self.incident_memory)) if self.incident_memory else 0.5
        }
    
    def _get_agent_patterns(self) -> Dict[str, Any]:
        """Get learned patterns from agent memory"""
        
        if not self.pattern_effectiveness:
            return {"no_patterns": True}
        
        # Analyze pattern effectiveness
        pattern_analysis = {}
        for pattern, incidents in self.pattern_effectiveness.items():
            if incidents:
                avg_confidence = sum(i.get("confidence", 0.5) for i in incidents) / len(incidents)
                pattern_analysis[pattern] = {
                    "occurrences": len(incidents),
                    "average_confidence": round(avg_confidence, 2),
                    "last_seen": incidents[-1].get("timestamp", datetime.now().isoformat())
                }
        
        return pattern_analysis
    
    async def trigger_intelligent_learning(self) -> Dict[str, Any]:
        """
        Trigger intelligent learning using Gemini model to analyze patterns and improve predictions
        """
        try:
            logger.info(f"Starting intelligent learning - LLM available: {self.llm is not None}")
            if not self.llm:
                logger.warning("LLM not available, falling back to mock learning")
                # Fallback to mock learning if LLM not available
                return await self._mock_learning_cycle()
            
            # Prepare learning context from recent incidents
            recent_incidents = self.incident_memory[-10:] if self.incident_memory else []
            
            # Create learning prompt for Gemini
            learning_prompt = f"""
You are an AI learning system for cascade failure prediction. Analyze the following incident data and provide insights to improve future predictions.

Recent Incidents ({len(recent_incidents)}):
{json.dumps(recent_incidents, indent=2)}

Current Pattern Effectiveness:
{json.dumps(self.pattern_effectiveness, indent=2)}

Please provide:
1. Key patterns you've identified from the incident data
2. Confidence improvements based on historical success rates
3. New prevention strategies that should be learned
4. Risk factors that are becoming more prominent
5. A confidence score (0-1) for how well the system is learning

Respond in JSON format:
{{
    "patterns_identified": ["pattern1", "pattern2"],
    "confidence_improvement": 0.15,
    "new_prevention_strategies": ["strategy1", "strategy2"],
    "emerging_risk_factors": ["risk1", "risk2"],
    "learning_confidence": 0.85,
    "insights": "Summary of key learning insights",
    "recommendations": ["recommendation1", "recommendation2"]
}}
"""
            
            # Get Gemini's learning analysis with retry logic
            max_retries = 3
            response = None
            for attempt in range(max_retries):
                try:
                    response = await self.llm.generate_content_async(learning_prompt)
                    break
                except google_exceptions.ResourceExhausted as e:
                    if attempt < max_retries - 1:
                        wait_time = min(20 * (2 ** attempt), 60)  # Exponential backoff
                        logger.warning(
                            f"Learning API quota exceeded (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {wait_time:.1f} seconds..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Learning failed after {max_retries} attempts: {e}")
                        return await self._mock_learning_cycle()
                except Exception as e:
                    logger.error(f"Learning failed: {e}")
                    return await self._mock_learning_cycle()
            
            if not response:
                return await self._mock_learning_cycle()
                
            response_text = response.text.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            try:
                learning_analysis = json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Gemini learning response, using fallback")
                return await self._mock_learning_cycle()
            
            # Create learning record with Gemini insights
            learning_record = {
                "timestamp": datetime.now().isoformat(),
                "client_id": "learning_cycle",
                "alerts": [],
                "prevention_actions": learning_analysis.get("new_prevention_strategies", []),
                "outcome": "learning_success",
                "actual_cascade_time": 0,
                "learning_type": "gemini_analysis",
                "confidence": learning_analysis.get("learning_confidence", 0.8),
                "gemini_insights": learning_analysis
            }
            
            # Update agent memory
            self.incident_memory.append(learning_record)
            
            # Update pattern effectiveness with new insights
            for pattern in learning_analysis.get("patterns_identified", []):
                if pattern not in self.pattern_effectiveness:
                    self.pattern_effectiveness[pattern] = []
                
                self.pattern_effectiveness[pattern].append({
                    "effectiveness_score": learning_analysis.get("learning_confidence", 0.8),
                    "prevention_actions": learning_analysis.get("new_prevention_strategies", []),
                    "timestamp": datetime.now().isoformat(),
                    "confidence": learning_analysis.get("learning_confidence", 0.8),
                    "source": "gemini_analysis"
                })
            
            return {
                "status": "intelligent_learning_completed",
                "learning_record": learning_record,
                "total_incidents": len(self.incident_memory),
                "patterns_learned": len(self.pattern_effectiveness),
                "confidence_improvement": learning_analysis.get("confidence_improvement", 0.1),
                "gemini_insights": learning_analysis
            }
            
        except Exception as e:
            logger.error(f"Intelligent learning failed: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return await self._mock_learning_cycle()
    
    async def _mock_learning_cycle(self) -> Dict[str, Any]:
        """Fallback mock learning cycle when Gemini is not available"""
        learning_record = {
            "timestamp": datetime.now().isoformat(),
            "client_id": "client_001",
            "alerts": [],
            "prevention_actions": ["Mock learning cycle triggered"],
            "outcome": "success",
            "actual_cascade_time": 0,
            "learning_type": "mock_fallback",
            "confidence": 0.6
        }
        
        self.incident_memory.append(learning_record)
        
        # Update pattern effectiveness
        pattern_key = f"mock_pattern_{len(self.incident_memory)}"
        if pattern_key not in self.pattern_effectiveness:
            self.pattern_effectiveness[pattern_key] = []
        
        self.pattern_effectiveness[pattern_key].append({
            "effectiveness_score": 0.6,
            "prevention_actions": ["Mock prevention action"],
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.6,
            "source": "mock_fallback"
        })
        
        return {
            "status": "mock_learning_completed",
            "learning_record": learning_record,
            "total_incidents": len(self.incident_memory),
            "patterns_learned": len(self.pattern_effectiveness),
            "confidence_improvement": 0.05,
            "note": "Using mock learning - set GOOGLE_AI_API_KEY for intelligent learning"
        }
    
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
