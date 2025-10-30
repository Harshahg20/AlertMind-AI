"""
Enhanced Cascade Prediction Agent with Comprehensive Data Integration
Maximizes LLM effectiveness with rich data sources and optimized prompts
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI

from app.models.alert import Alert, Client, CascadePrediction
from app.services.cascade_prediction import CascadePredictionEngine
from app.services.data_collection_service import DataCollectionService
from app.services.llm_prompt_optimizer import LLMPromptOptimizer, PromptContext

logger = logging.getLogger(__name__)

class EnhancedCascadePredictionAgent:
    """
    Enhanced Cascade Prediction Agent with comprehensive data integration
    and optimized LLM utilization
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.name = "enhanced_cascade_prediction_agent"
        self.created_at = datetime.now()
        
        # Initialize LLM
        self.api_key = api_key or "demo_key"
        if self.api_key != "demo_key":
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.1,  # Lower temperature for more consistent predictions
                google_api_key=self.api_key
            )
        else:
            self.llm = None
            logger.warning("Using mock LLM responses - set GOOGLE_AI_API_KEY for real predictions")
        
        # Initialize services
        self.prediction_engine = CascadePredictionEngine()
        self.data_collection_service = DataCollectionService()
        self.prompt_optimizer = LLMPromptOptimizer()
        
        # Agent memory and learning
        self.incident_memory = []
        self.pattern_effectiveness = {}
        self.client_behavior_profiles = {}
        self.performance_metrics = {
            "total_predictions": 0,
            "accurate_predictions": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "average_confidence": 0.0
        }
    
    async def run(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced agent execution with comprehensive data analysis
        """
        try:
            # Extract basic data
            alerts = correlated_data.get("alerts", [])
            client = correlated_data.get("client")
            historical_data = correlated_data.get("historical_data", [])
            
            if not alerts or not client:
                raise ValueError("Missing required data: alerts and client")
            
            # Step 1: Collect comprehensive system data
            comprehensive_data = await self._collect_comprehensive_data()
            
            # Step 2: Get numeric prediction from engine
            engine_output = await self._get_numeric_prediction(correlated_data)
            
            # Step 3: Prepare rich context for LLM
            rich_context = self._prepare_rich_context(
                alerts, client, historical_data, engine_output, comprehensive_data
            )
            
            # Step 4: Create optimized prompt
            optimized_prompt = self.prompt_optimizer.create_optimized_prompt(rich_context)
            
            # Step 5: Get LLM reasoning with rich context
            if self.llm:
                llm_reasoning = await self._get_enhanced_llm_reasoning(optimized_prompt)
            else:
                llm_reasoning = self._get_mock_llm_reasoning(rich_context)
            
            # Step 6: Combine predictions with enhanced analysis
            enhanced_prediction = self._combine_enhanced_predictions(
                engine_output, llm_reasoning, alerts, client, comprehensive_data
            )
            
            # Step 7: Update agent learning and memory
            self._update_enhanced_agent_memory(alerts, enhanced_prediction, client.id, comprehensive_data)
            
            # Step 8: Update performance metrics
            self._update_performance_metrics(enhanced_prediction)
            
            return enhanced_prediction
            
        except Exception as e:
            logger.error(f"Enhanced Cascade Prediction Agent failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._fallback_prediction(correlated_data)
    
    async def _collect_comprehensive_data(self) -> Dict[str, Any]:
        """Collect comprehensive system data"""
        try:
            async with self.data_collection_service as data_service:
                comprehensive_data = await data_service.collect_comprehensive_data()
                return comprehensive_data
        except Exception as e:
            logger.warning(f"Could not collect comprehensive data: {e}")
            return self._get_fallback_comprehensive_data()
    
    def _prepare_rich_context(
        self, 
        alerts: List[Any], 
        client: Client, 
        historical_data: List[Dict], 
        engine_output: Dict[str, Any],
        comprehensive_data: Dict[str, Any]
    ) -> PromptContext:
        """Prepare rich context for LLM analysis"""
        
        # Convert alerts to dictionaries if needed
        alert_dicts = []
        for alert in alerts:
            if isinstance(alert, dict):
                alert_dicts.append(alert)
            else:
                alert_dicts.append({
                    'id': alert.id,
                    'client_id': alert.client_id,
                    'client_name': alert.client_name,
                    'system': alert.system,
                    'severity': alert.severity,
                    'message': alert.message,
                    'category': alert.category,
                    'timestamp': alert.timestamp.isoformat(),
                    'cascade_risk': alert.cascade_risk,
                    'is_correlated': alert.is_correlated
                })
        
        # Prepare client info
        client_info = {
            'name': client.name,
            'tier': client.tier,
            'environment': client.environment,
            'critical_systems': client.critical_systems,
            'system_dependencies': client.system_dependencies
        }
        
        # Get cross-client insights
        cross_client_insights = self._get_cross_client_insights()
        
        return PromptContext(
            system_metrics=comprehensive_data.get('system_metrics', {}),
            service_health=comprehensive_data.get('service_health', {}),
            external_factors=comprehensive_data.get('external_factors'),
            trend_analysis=comprehensive_data.get('trend_analysis', {}),
            alerts=alert_dicts,
            client_info=client_info,
            historical_data=historical_data,
            cross_client_insights=cross_client_insights
        )
    
    async def _get_enhanced_llm_reasoning(self, optimized_prompt: str) -> Dict[str, Any]:
        """Get enhanced LLM reasoning with optimized prompt"""
        try:
            if not self.llm:
                return self._get_mock_llm_reasoning({})
            
            # Use the optimized prompt for better results
            response = await self.llm.ainvoke(optimized_prompt)
            response_text = response.content.strip()
            
            # Parse JSON response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            try:
                parsed_response = json.loads(response_text)
                
                # Validate and enhance the response
                enhanced_response = self._validate_and_enhance_llm_response(parsed_response)
                return enhanced_response
                
            except json.JSONDecodeError:
                # If not valid JSON, extract key information
                return self._parse_text_response(response_text)
                
        except Exception as e:
            logger.error(f"Enhanced LLM reasoning failed: {e}")
            return self._get_mock_llm_reasoning({})
    
    def _validate_and_enhance_llm_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance LLM response"""
        # Ensure required fields exist
        required_fields = ['predicted_in', 'confidence', 'root_causes', 'summary']
        for field in required_fields:
            if field not in response:
                response[field] = self._get_default_value(field)
        
        # Validate and enhance confidence
        confidence = response.get('confidence', 0.5)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            response['confidence'] = 0.5
        
        # Validate and enhance predicted_in
        predicted_in = response.get('predicted_in', 15)
        if not isinstance(predicted_in, int) or predicted_in < 1 or predicted_in > 60:
            response['predicted_in'] = 15
        
        # Enhance with additional analysis
        response['enhanced_analysis'] = {
            'data_sources_used': len([k for k, v in response.items() if v is not None]),
            'analysis_depth': 'comprehensive' if 'reasoning' in response else 'basic',
            'confidence_factors': self._analyze_confidence_factors(response),
            'prediction_quality': self._assess_prediction_quality(response)
        }
        
        return response
    
    def _analyze_confidence_factors(self, response: Dict[str, Any]) -> List[str]:
        """Analyze factors contributing to confidence"""
        factors = []
        
        if response.get('confidence', 0) > 0.8:
            factors.append('high_confidence_indicators')
        if len(response.get('root_causes', [])) > 2:
            factors.append('multiple_root_causes_identified')
        if response.get('urgency_level') == 'critical':
            factors.append('critical_urgency_detected')
        if 'reasoning' in response:
            factors.append('detailed_reasoning_provided')
        
        return factors
    
    def _assess_prediction_quality(self, response: Dict[str, Any]) -> str:
        """Assess the quality of the prediction"""
        quality_score = 0
        
        # Check for required fields
        required_fields = ['predicted_in', 'confidence', 'root_causes', 'summary']
        quality_score += len([f for f in required_fields if f in response and response[f]])
        
        # Check for enhanced fields
        enhanced_fields = ['affected_systems', 'prevention_actions', 'reasoning']
        quality_score += len([f for f in enhanced_fields if f in response and response[f]])
        
        # Check confidence level
        confidence = response.get('confidence', 0)
        if confidence > 0.7:
            quality_score += 2
        elif confidence > 0.5:
            quality_score += 1
        
        if quality_score >= 8:
            return 'excellent'
        elif quality_score >= 6:
            return 'good'
        elif quality_score >= 4:
            return 'fair'
        else:
            return 'poor'
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            'predicted_in': 15,
            'confidence': 0.5,
            'root_causes': ['System monitoring indicates potential issues'],
            'summary': 'Analysis completed with available data',
            'urgency_level': 'medium',
            'affected_systems': [],
            'prevention_actions': ['Monitor system closely', 'Check resource usage']
        }
        return defaults.get(field, None)
    
    def _combine_enhanced_predictions(
        self, 
        engine_output: Dict[str, Any], 
        llm_reasoning: Dict[str, Any], 
        alerts: List[Any], 
        client: Client,
        comprehensive_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine predictions with enhanced analysis"""
        
        # Infer pattern from available data
        inferred_pattern = self._infer_pattern_from_combined_data(
            llm_reasoning, engine_output, alerts, client
        )
        
        # Start with LLM reasoning as primary source
        combined = {
            "predicted_in": llm_reasoning.get("predicted_in", engine_output.get("predicted_in", 15)),
            "confidence": max(llm_reasoning.get("confidence", 0.0), engine_output.get("confidence", 0.0)),
            "root_causes": llm_reasoning.get("root_causes", engine_output.get("root_causes", ["Unknown root cause"])),
            "summary": llm_reasoning.get("summary", engine_output.get("summary", "No detailed summary available")),
            "urgency_level": llm_reasoning.get("urgency_level", "medium"),
            "affected_systems": llm_reasoning.get("affected_systems", engine_output.get("affected_systems", [])),
            "prevention_actions": llm_reasoning.get("prevention_actions", engine_output.get("prevention_actions", [])),
            "business_impact": llm_reasoning.get("business_impact", "Moderate impact expected"),
            "pattern": inferred_pattern,  # Add pattern field
            
            # Enhanced analysis
            "enhanced_analysis": {
                "comprehensive_data_used": comprehensive_data.get('data_quality', {}).get('completeness', 0) > 0.8,
                "system_health_score": self._calculate_system_health_score(comprehensive_data),
                "data_sources_count": comprehensive_data.get('collection_metadata', {}).get('sources_available', 0),
                "trend_analysis_available": comprehensive_data.get('trend_analysis', {}).get('trends_available', False),
                "external_factors_considered": comprehensive_data.get('external_factors') is not None,
                "llm_analysis_quality": llm_reasoning.get('enhanced_analysis', {}).get('prediction_quality', 'unknown')
            },
            
            # Reasoning and context
            "explanation": {
                "numeric_engine_output": engine_output,
                "llm_reasoning": llm_reasoning,
                "comprehensive_data_summary": {
                    "system_metrics_available": bool(comprehensive_data.get('system_metrics')),
                    "service_health_available": bool(comprehensive_data.get('service_health')),
                    "trend_analysis_available": comprehensive_data.get('trend_analysis', {}).get('trends_available', False),
                    "external_factors_available": bool(comprehensive_data.get('external_factors'))
                }
            },
            
            # Agent metadata
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "data_collection_time": comprehensive_data.get('collection_metadata', {}).get('collection_time_ms', 0),
                "enhanced_mode": True,
                "performance_metrics": self.performance_metrics
            }
        }
        
        # Refine confidence based on data quality
        data_quality = comprehensive_data.get('data_quality', {})
        if data_quality.get('completeness', 0) > 0.9:
            combined['confidence'] = min(1.0, combined['confidence'] * 1.1)
        elif data_quality.get('completeness', 0) < 0.5:
            combined['confidence'] = max(0.1, combined['confidence'] * 0.8)
        
        # Set urgency based on confidence and system health
        system_health_score = combined['enhanced_analysis']['system_health_score']
        if combined['confidence'] > 0.8 and system_health_score < 40:
            combined['urgency_level'] = 'critical'
        elif combined['confidence'] > 0.6 and system_health_score < 60:
            combined['urgency_level'] = 'high'
        
        return combined
    
    def _calculate_system_health_score(self, comprehensive_data: Dict[str, Any]) -> int:
        """Calculate overall system health score"""
        try:
            metrics = comprehensive_data.get('system_metrics', {})
            if not metrics:
                return 50  # Default score
            
            score = 100
            
            # CPU impact
            cpu_percent = metrics.get('cpu_percent', 0)
            if cpu_percent > 90:
                score -= 30
            elif cpu_percent > 80:
                score -= 20
            elif cpu_percent > 70:
                score -= 10
            
            # Memory impact
            memory_percent = metrics.get('memory_percent', 0)
            if memory_percent > 95:
                score -= 25
            elif memory_percent > 85:
                score -= 15
            elif memory_percent > 75:
                score -= 10
            
            # Disk impact
            disk_usage = metrics.get('disk_usage', {})
            for mount, usage in disk_usage.items():
                if usage.get('percent', 0) > 95:
                    score -= 20
                elif usage.get('percent', 0) > 85:
                    score -= 10
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.warning(f"Error calculating system health score: {e}")
            return 50
    
    def _update_enhanced_agent_memory(
        self, 
        alerts: List[Any], 
        prediction: Dict[str, Any], 
        client_id: str,
        comprehensive_data: Dict[str, Any]
    ):
        """Update agent memory with enhanced data"""
        
        # Store incident for learning
        incident_record = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "alerts": [{"system": a.get("system") if isinstance(a, dict) else a.system, 
                       "severity": a.get("severity") if isinstance(a, dict) else a.severity, 
                       "category": a.get("category") if isinstance(a, dict) else a.category} for a in alerts],
            "prediction": prediction,
            "comprehensive_data": {
                "system_health_score": prediction.get('enhanced_analysis', {}).get('system_health_score', 0),
                "data_quality": comprehensive_data.get('data_quality', {}),
                "trend_analysis": comprehensive_data.get('trend_analysis', {})
            },
            "confidence": prediction.get("confidence", 0.0),
            "urgency": prediction.get("urgency_level", "medium")
        }
        
        self.incident_memory.append(incident_record)
        
        # Keep memory size manageable
        if len(self.incident_memory) > 1000:
            self.incident_memory = self.incident_memory[-800:]
        
        # Update pattern effectiveness
        pattern_key = prediction.get("pattern_matched", "enhanced_ai_pattern")
        if pattern_key not in self.pattern_effectiveness:
            self.pattern_effectiveness[pattern_key] = {"total": 0, "successful": 0}
        
        self.pattern_effectiveness[pattern_key]["total"] += 1
        if prediction.get("prevention_actions") and prediction.get("confidence", 0) > 0.7:
            self.pattern_effectiveness[pattern_key]["successful"] += 1
    
    def _update_performance_metrics(self, prediction: Dict[str, Any]):
        """Update agent performance metrics"""
        self.performance_metrics["total_predictions"] += 1
        
        confidence = prediction.get("confidence", 0.0)
        self.performance_metrics["average_confidence"] = (
            (self.performance_metrics["average_confidence"] * (self.performance_metrics["total_predictions"] - 1) + confidence) 
            / self.performance_metrics["total_predictions"]
        )
    
    def _get_cross_client_insights(self) -> Dict[str, Any]:
        """Get enhanced cross-client insights"""
        if not self.incident_memory:
            return {"patterns_learned": 0, "confidence_improvement": 0}
        
        client_incidents = {}
        for incident in self.incident_memory:
            client_id = incident["client_id"]
            if client_id not in client_incidents:
                client_incidents[client_id] = 0
            client_incidents[client_id] += 1
        
        return {
            "patterns_learned": len(self.pattern_effectiveness),
            "clients_analyzed": len(client_incidents),
            "confidence_improvement": min(0.4, len(self.incident_memory) / 1000),
            "most_common_patterns": sorted(
                self.pattern_effectiveness.items(), 
                key=lambda item: item[1]["total"], 
                reverse=True
            )[:5],
            "performance_metrics": self.performance_metrics
        }
    
    def _get_mock_llm_reasoning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock LLM reasoning for demo purposes"""
        # Infer pattern from context or use default
        inferred_pattern = self._infer_pattern_from_context(context)
        
        return {
            "predicted_in": 20,
            "confidence": 0.65,
            "root_causes": ["Mock AI detected system resource constraints"],
            "summary": "Mock AI analysis indicates potential cascade within 20 minutes due to resource exhaustion patterns.",
            "urgency_level": "high",
            "affected_systems": ["database", "web-app"],
            "prevention_actions": ["Scale resources", "Restart services"],
            "business_impact": "Moderate business impact expected",
            "pattern": inferred_pattern,  # Add pattern field
            "reasoning": {
                "system_health_score": 65,
                "resource_exhaustion_risk": "high",
                "dependency_chain_analysis": "Database dependency chain at risk",
                "temporal_patterns": "Increasing resource usage pattern detected",
                "external_factors": "No significant external factors"
            }
        }
    
    def _infer_pattern_from_combined_data(
        self, 
        llm_reasoning: Dict[str, Any], 
        engine_output: Dict[str, Any], 
        alerts: List[Any], 
        client: Client
    ) -> str:
        """Infer pattern from combined prediction data"""
        # First try to get pattern from LLM reasoning
        if llm_reasoning.get("pattern"):
            return llm_reasoning["pattern"]
        
        # Try to get pattern from engine output
        if engine_output.get("pattern"):
            return engine_output["pattern"]
        
        # Infer from root causes
        root_causes = llm_reasoning.get("root_causes", [])
        if root_causes:
            first_cause = root_causes[0].lower()
            if "database" in first_cause:
                return "database_performance_cascade"
            elif "network" in first_cause:
                return "network_infrastructure_cascade"
            elif "storage" in first_cause:
                return "storage_system_cascade"
            elif "memory" in first_cause or "cpu" in first_cause:
                return "resource_exhaustion_cascade"
        
        # Infer from affected systems
        affected_systems = llm_reasoning.get("affected_systems", [])
        if affected_systems:
            systems_str = " ".join(affected_systems).lower()
            if "database" in systems_str:
                return "database_system_cascade"
            elif "web-app" in systems_str or "api" in systems_str:
                return "application_layer_cascade"
            elif "network" in systems_str:
                return "network_infrastructure_cascade"
        
        # Infer from alerts
        if alerts:
            systems = [getattr(alert, 'system', 'unknown') for alert in alerts]
            categories = [getattr(alert, 'category', 'unknown') for alert in alerts]
            
            if "database" in systems:
                return "database_performance_cascade"
            elif "web-app" in systems or "api" in systems:
                return "application_layer_cascade"
            elif "network" in systems or "network" in categories:
                return "network_infrastructure_cascade"
            elif "storage" in systems or "storage" in categories:
                return "storage_system_cascade"
        
        # Default fallback
        return "enhanced_ai_analyzed_cascade"
    
    def _infer_pattern_from_context(self, context: Dict[str, Any]) -> str:
        """Infer pattern from context data"""
        # Get alerts from context
        alerts = context.get("current_alerts", [])
        client_info = context.get("client_info", {})
        
        if not alerts:
            return "general_system_degradation"
        
        # Analyze alert patterns
        critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
        warning_alerts = [a for a in alerts if a.get("severity") == "warning"]
        
        # Get system types from alerts
        systems = [a.get("system", "unknown") for a in alerts]
        categories = [a.get("category", "unknown") for a in alerts]
        
        # Infer pattern based on alert characteristics
        if "database" in systems:
            if "performance" in categories:
                return "database_performance_cascade"
            elif "storage" in categories:
                return "database_storage_cascade"
            else:
                return "database_system_cascade"
        elif "web-app" in systems or "api" in systems:
            return "application_layer_cascade"
        elif "network" in systems or "network" in categories:
            return "network_infrastructure_cascade"
        elif "storage" in systems or "storage" in categories:
            return "storage_system_cascade"
        elif len(critical_alerts) > 2:
            return "multi_system_critical_cascade"
        elif len(warning_alerts) > 3:
            return "progressive_degradation_cascade"
        else:
            return "general_system_instability"
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse non-JSON LLM response"""
        # Infer pattern from text content
        inferred_pattern = "text_parsed_pattern"
        if "database" in text.lower():
            inferred_pattern = "database_related_cascade"
        elif "network" in text.lower():
            inferred_pattern = "network_related_cascade"
        elif "storage" in text.lower():
            inferred_pattern = "storage_related_cascade"
        elif "performance" in text.lower():
            inferred_pattern = "performance_degradation_cascade"
        
        return {
            "predicted_in": 25,
            "confidence": 0.6,
            "root_causes": ["LLM provided text response, parsing attempted"],
            "summary": text[:300] + "..." if len(text) > 300 else text,
            "urgency_level": "medium",
            "affected_systems": [],
            "prevention_actions": ["Manual review recommended"],
            "pattern": inferred_pattern,  # Add pattern field
            "explanation": {"parse_mode": "text_fallback", "original_response": text}
        }
    
    def _get_fallback_comprehensive_data(self) -> Dict[str, Any]:
        """Get fallback comprehensive data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {},
            "service_health": {},
            "external_factors": None,
            "trend_analysis": {"trends_available": False, "reason": "collection_failed"},
            "data_quality": {"completeness": 0.0, "freshness": "unknown"},
            "collection_metadata": {
                "collection_time_ms": 0,
                "sources_available": 0,
                "last_update": datetime.now().isoformat(),
                "fallback_mode": True
            }
        }
    
    async def _get_numeric_prediction(self, correlated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get numeric prediction from the existing engine"""
        try:
            alerts = correlated_data.get("alerts")
            client = correlated_data.get("client")
            
            if not alerts or not client:
                return {"error": "Missing alerts or client data"}
            
            # Convert dictionaries to Alert objects if needed
            if alerts and isinstance(alerts[0], dict):
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
                predictions = self.prediction_engine.predict_cascade(alerts, client)
            
            if not predictions:
                return {
                    "cascade_predicted": False,
                    "confidence": 0.0,
                    "predicted_in": 0,
                    "root_causes": ["No immediate cascade pattern detected by numeric engine."],
                    "summary": "Numeric engine found no high-confidence cascade prediction.",
                    "affected_systems": [],
                    "prevention_actions": []
                }
            
            # Aggregate results from numeric engine
            highest_confidence_prediction = max(predictions, key=lambda p: p.prediction_confidence)
            
            return {
                "cascade_predicted": True,
                "confidence": highest_confidence_prediction.prediction_confidence,
                "predicted_in": highest_confidence_prediction.time_to_cascade_minutes,
                "root_causes": [f"Numeric engine identified pattern: {highest_confidence_prediction.pattern_matched}"],
                "summary": f"Numeric engine predicts cascade to {', '.join(highest_confidence_prediction.predicted_cascade_systems)} in {highest_confidence_prediction.time_to_cascade_minutes} minutes.",
                "affected_systems": highest_confidence_prediction.predicted_cascade_systems,
                "prevention_actions": highest_confidence_prediction.prevention_actions
            }
            
        except Exception as e:
            logger.error(f"Error getting numeric prediction: {e}")
            return {"error": f"Numeric prediction failed: {e}"}
    
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
        
        # Infer pattern for fallback
        fallback_pattern = "fallback_analysis"
        if alerts:
            if isinstance(alerts[0], dict):
                systems = [a.get("system", "unknown") for a in alerts]
            else:
                systems = [getattr(a, 'system', 'unknown') for a in alerts]
            
            if "database" in systems:
                fallback_pattern = "database_fallback_cascade"
            elif "web-app" in systems or "api" in systems:
                fallback_pattern = "application_fallback_cascade"
            elif "network" in systems:
                fallback_pattern = "network_fallback_cascade"
        
        return {
            "predicted_in": 20,
            "confidence": min(0.7, avg_cascade_risk),
            "root_causes": ["Fallback analysis: System monitoring indicates potential issues"],
            "summary": f"Fallback prediction: {critical_count} critical alerts detected. Manual investigation recommended.",
            "explanation": {
                "fallback_mode": True,
                "reason": "Enhanced agent processing failed"
            },
            "urgency_level": "high" if critical_count > 0 else "medium",
            "affected_systems": [],
            "prevention_actions": ["Manual investigation required", "Contact senior technician"],
            "pattern": fallback_pattern,  # Add pattern field
            "agent_metadata": {
                "agent_name": self.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "fallback_mode": True
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get enhanced agent status"""
        return {
            "agent_name": self.name,
            "agent_created": self.created_at.isoformat(),
            "llm_available": self.llm is not None,
            "memory_size": len(self.incident_memory),
            "patterns_learned": len(self.pattern_effectiveness),
            "performance_metrics": self.performance_metrics,
            "cross_client_insights": self._get_cross_client_insights(),
            "enhanced_features": {
                "comprehensive_data_collection": True,
                "optimized_prompts": True,
                "rich_context_analysis": True,
                "performance_tracking": True,
                "cross_client_learning": True
            },
            "status": "operational"
        }

def create_enhanced_cascade_prediction_agent(api_key: Optional[str] = None) -> EnhancedCascadePredictionAgent:
    """Factory function to create the Enhanced Cascade Prediction Agent"""
    return EnhancedCascadePredictionAgent(api_key=api_key)
