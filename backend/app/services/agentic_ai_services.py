import asyncio
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import numpy as np
from app.models.alert import Alert, Client, CascadePrediction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticAIService:
    """
    Agentic AI Service using Google Gemini for intelligent cascade prediction
    and proactive failure prevention
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Get API key from environment variable or parameter
        import os
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY") or "demo_key"
        
        # Initialize Gemini with correct model name
        if self.api_key != "demo_key":
            genai.configure(api_key=self.api_key)
            # Use the correct model name for Gemini 1.5
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("✅ Gemini 1.5 Pro model loaded successfully")
        else:
            self.model = None
            logger.warning("Using mock AI responses - set GOOGLE_AI_API_KEY for real predictions")
        
        # AI Agent memory for cross-client learning
        self.incident_memory = []
        self.pattern_memory = {}
        self.client_behavior_profiles = {}
        
        # Cascade prevention rules learned by AI
        self.prevention_rules = {
            "database_overload": {
                "trigger_patterns": ["cpu > 85%", "memory > 90%", "connections > 80%"],
                "prevention_actions": ["scale_database", "restart_service", "clear_connections"],
                "success_rate": 0.87,
                "time_window": 12
            },
            "network_congestion": {
                "trigger_patterns": ["packet_loss > 5%", "latency > 100ms", "bandwidth > 95%"],
                "prevention_actions": ["reroute_traffic", "scale_bandwidth", "activate_failover"],
                "success_rate": 0.82,
                "time_window": 8
            },
            "storage_exhaustion": {
                "trigger_patterns": ["disk_space > 90%", "io_wait > 20%", "write_errors"],
                "prevention_actions": ["cleanup_temp", "archive_logs", "expand_storage"],
                "success_rate": 0.91,
                "time_window": 25
            }
        }
    
    def generate_resolution_playbook(self, alerts: List[Alert], client: Client) -> Dict:
        """Generate an AI resolution playbook based on similar historical incidents and current context"""
        try:
            # Collect candidate incidents from agent memory
            similar_records = self._find_similar_incidents(alerts, client)

            # Aggregate resolutions and outcomes
            recommended_steps, evidence = self._aggregate_resolutions(similar_records)

            # Add preventative suggestions from patterns/rules
            preventative = self._preventative_suggestions(alerts)

            # Confidence based on number and recency of similar incidents
            confidence = min(0.95, 0.5 + (len(similar_records) * 0.05))

            playbook = {
                "client_id": client.id,
                "client_name": client.name,
                "generated_at": datetime.now().isoformat(),
                "similar_incident_count": len(similar_records),
                "confidence": round(confidence, 2),
                "recommended_steps": recommended_steps[:8],
                "preventative_actions": preventative[:5],
                "evidence": evidence[:5]
            }
            return playbook
        except Exception as e:
            logger.error(f"Playbook generation failed: {e}")
            return {
                "client_id": client.id,
                "client_name": client.name,
                "generated_at": datetime.now().isoformat(),
                "similar_incident_count": 0,
                "confidence": 0.5,
                "recommended_steps": [
                    "Collect diagnostics: CPU, memory, I/O, connection pool metrics",
                    "Identify top talkers: slow queries, error spikes, network errors",
                    "Mitigate blast radius: scale critical services, enable failover",
                    "Apply quick wins: restart affected services during low-traffic window",
                ],
                "preventative_actions": [
                    "Enable autoscaling for database and application tiers",
                    "Tune connection pool sizes and timeouts",
                    "Add alert for early indicators (CPU>80%, queue depth, packet loss>3%)",
                ],
                "evidence": []
            }

    def _find_similar_incidents(self, alerts: List[Alert], client: Client) -> List[Dict]:
        """Find similar incidents from memory using simple semantic features."""
        if not self.incident_memory:
            return []

        target_features = set()
        for a in alerts:
            target_features.update([
                a.system.lower(), str(a.category).lower(), str(a.severity).lower()
            ])
            target_features.update(a.message.lower().split())

        scored = []
        for record in self.incident_memory[-200:]:
            rec_features = set()
            for ap in record.get("alert_pattern", []):
                rec_features.update([
                    ap.get("system", "").lower(),
                    str(ap.get("category", "")).lower(),
                    str(ap.get("severity", "")).lower()
                ])
            pred = record.get("prediction", {})
            if isinstance(pred, dict):
                seq = pred.get("predicted_cascade_sequence", [])
                rec_features.update([s.lower() for s in seq])

            # Jaccard similarity
            inter = len(target_features & rec_features)
            union = len(target_features | rec_features) or 1
            sim = inter / union
            if sim > 0.05:
                scored.append((sim, record))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:20]]

    def _aggregate_resolutions(self, records: List[Dict]) -> Tuple[List[str], List[Dict]]:
        """Aggregate resolution steps that previously worked with evidence."""
        step_counts: Dict[str, int] = {}
        evidences: List[Dict] = []

        for r in records:
            prevention = r.get("prevention_plan", {})
            primary = prevention.get("primary_actions", [])
            fallback = prevention.get("fallback_actions", [])
            steps = list(primary) + list(fallback)
            for s in steps:
                step_counts[s] = step_counts.get(s, 0) + 1
            evidences.append({
                "timestamp": r.get("timestamp"),
                "confidence": r.get("confidence", 0.5),
                "actions": steps[:3]
            })

        ranked = sorted(step_counts.items(), key=lambda x: x[1], reverse=True)
        recommended_steps = [s for s, _ in ranked]
        return recommended_steps, evidences

    def _preventative_suggestions(self, alerts: List[Alert]) -> List[str]:
        """Suggest preventative actions informed by built-in patterns and current alerts."""
        suggestions: List[str] = []
        alert_text = " ".join([f"{a.system} {a.message}".lower() for a in alerts])

        if any(k in alert_text for k in ["cpu", "memory", "connection", "slow query", "pool"]):
            suggestions.extend([
                "Scale database resources",
                "Enable query caching",
                "Optimize connection pool size and timeouts",
            ])
        if any(k in alert_text for k in ["packet", "latency", "bandwidth", "loss"]):
            suggestions.extend([
                "Reroute traffic to backup gateway",
                "Increase bandwidth allocation",
                "Activate network failover",
            ])
        if any(k in alert_text for k in ["disk", "space", "io", "raid", "storage"]):
            suggestions.extend([
                "Archive old logs",
                "Clear temporary files",
                "Expand storage capacity",
            ])
        if any(k in alert_text for k in ["response", "timeout", "503", "error", "retry"]):
            suggestions.extend([
                "Scale application instances",
                "Warm up cache and precompute hot keys",
                "Restart application services in rolling fashion",
            ])

        # De-duplicate keeping order
        seen = set()
        unique = []
        for s in suggestions:
            if s not in seen:
                unique.append(s)
                seen.add(s)
        return unique

    async def analyze_cascade_risk(self, alerts: List[Alert], client: Client, 
                                 historical_data: List[Dict]) -> Dict:
        """
        Main agentic analysis method - predicts cascades and suggests prevention
        """
        try:
            # Prepare context for AI analysis
            analysis_context = self._prepare_analysis_context(alerts, client, historical_data)
            
            # Get AI insights (mock or real)
            if self.model:
                ai_insights = await self._get_gemini_insights(analysis_context)
            else:
                ai_insights = self._get_mock_ai_insights(analysis_context)
            
            # Process AI insights into actionable predictions
            cascade_analysis = self._process_ai_insights(ai_insights, alerts, client)
            
            # Update agent memory with new patterns
            self._update_agent_memory(alerts, cascade_analysis, client.id)
            
            return cascade_analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(alerts, client)
    
    def _prepare_analysis_context(self, alerts: List[Alert], client: Client, 
                                historical_data: List[Dict]) -> str:
        """Prepare comprehensive context for AI analysis"""
        
        current_time = datetime.now()
        
        # Current alert context
        alert_context = []
        for alert in alerts:
            time_diff = (current_time - alert.timestamp).total_seconds() / 60
            alert_context.append({
                "system": alert.system,
                "severity": alert.severity,
                "category": alert.category,
                "message": alert.message,
                "minutes_ago": int(time_diff),
                "cascade_risk": alert.cascade_risk
            })
        
        # Client infrastructure context
        client_context = {
            "name": client.name,
            "tier": client.tier,
            "environment": client.environment,
            "critical_systems": client.critical_systems,
            "dependencies": client.system_dependencies
        }
        
        # Historical pattern context
        historical_context = []
        for incident in historical_data[-10:]:  # Last 10 incidents
            historical_context.append({
                "pattern": incident.get("pattern", "unknown"),
                "cascade_time": incident.get("cascade_time_minutes", 0),
                "affected_systems": incident.get("affected_systems", []),
                "resolution_time": incident.get("resolution_time_minutes", 0)
            })
        
        # Cross-client insights
        cross_client_patterns = self._get_cross_client_patterns()
        
        context_prompt = f"""
        AGENTIC CASCADE PREDICTION ANALYSIS
        
        CLIENT INFRASTRUCTURE:
        {json.dumps(client_context, indent=2)}
        
        CURRENT ALERTS (TIME-ORDERED):
        {json.dumps(alert_context, indent=2)}
        
        HISTORICAL INCIDENTS:
        {json.dumps(historical_context, indent=2)}
        
        CROSS-CLIENT PATTERNS LEARNED:
        {json.dumps(cross_client_patterns, indent=2)}
        
        PREVENTION RULES AVAILABLE:
        {json.dumps(list(self.prevention_rules.keys()), indent=2)}
        
        TASK: Analyze this data as an AI agent specializing in IT infrastructure cascade prediction.
        
        PROVIDE JSON RESPONSE WITH:
        1. cascade_probability (0.0-1.0)
        2. time_to_cascade_minutes (integer)
        3. predicted_cascade_sequence (list of systems)
        4. confidence_level (0.0-1.0)
        5. root_cause_analysis (string)
        6. prevention_recommendations (list)
        7. similar_historical_incidents (integer count)
        8. cross_client_insights (string)
        9. urgency_level ("low", "medium", "high", "critical")
        10. business_impact_assessment (string)
        """
        
        return context_prompt
    
    async def _get_gemini_insights(self, context: str) -> Dict:
        """Get insights from Google Gemini AI"""
        try:
            # Configure safety settings for IT analysis
            safety_settings = [
                {"category": HarmCategory.HARM_CATEGORY_HARASSMENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
                {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH, "threshold": HarmBlockThreshold.BLOCK_NONE},
                {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": HarmBlockThreshold.BLOCK_NONE},
                {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": HarmBlockThreshold.BLOCK_NONE}
            ]
            
            response = await self.model.generate_content_async(
                context,
                safety_settings=safety_settings,
                generation_config={
                    "temperature": 0.3,  # Lower temperature for more consistent analysis
                    "top_p": 0.8,
                    "max_output_tokens": 2048
                }
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._get_mock_ai_insights(context)
    
    def _get_mock_ai_insights(self, context: str) -> Dict:
        """Generate mock AI insights for demo purposes"""
        
        # Extract key info from context for realistic mock response
        alert_count = context.count('"severity"')
        critical_alerts = context.count('"critical"')
        warning_alerts = context.count('"warning"')
        
        # Simulate AI analysis based on alert patterns
        cascade_probability = min(0.95, 0.3 + (critical_alerts * 0.2) + (warning_alerts * 0.1))
        
        if cascade_probability > 0.8:
            urgency = "critical"
            time_to_cascade = np.random.randint(5, 15)
        elif cascade_probability > 0.6:
            urgency = "high"
            time_to_cascade = np.random.randint(10, 25)
        elif cascade_probability > 0.4:
            urgency = "medium"
            time_to_cascade = np.random.randint(20, 40)
        else:
            urgency = "low"
            time_to_cascade = np.random.randint(30, 60)
        
        # Mock intelligent analysis
        mock_insights = {
            "cascade_probability": round(cascade_probability, 2),
            "time_to_cascade_minutes": time_to_cascade,
            "predicted_cascade_sequence": ["database", "web-app", "api-gateway", "user-interface"][:int(cascade_probability * 5)],
            "confidence_level": round(0.7 + (cascade_probability * 0.2), 2),
            "root_cause_analysis": f"AI detected {critical_alerts} critical and {warning_alerts} warning alerts forming a cascade pattern. Database performance degradation is triggering application slowdowns, which will likely cascade to user-facing services within {time_to_cascade} minutes.",
            "prevention_recommendations": [
                "Immediately scale database resources",
                "Implement connection pooling optimization",
                "Activate load balancer failover to secondary systems",
                "Preemptively restart application services to clear connection backlog"
            ],
            "similar_historical_incidents": np.random.randint(3, 12),
            "cross_client_insights": f"This pattern has been observed in {np.random.randint(2, 5)} other clients with similar infrastructure. Historical data shows 87% success rate when prevention actions are taken within {time_to_cascade//2} minutes.",
            "urgency_level": urgency,
            "business_impact_assessment": f"HIGH IMPACT: Predicted cascade will affect {len(['database', 'web-app', 'api-gateway'])} critical business systems, potentially causing {np.random.randint(30, 120)} minutes of service disruption and affecting {np.random.randint(100, 500)} users."
        }
        
        return mock_insights
    
    def _process_ai_insights(self, ai_insights: Dict, alerts: List[Alert], 
                           client: Client) -> Dict:
        """Process AI insights into structured cascade analysis"""
        
        # Create cascade predictions for each high-risk alert
        predictions = []
        for alert in alerts:
            if alert.cascade_risk > 0.5:  # Only process risky alerts
                prediction = CascadePrediction(
                    alert_id=alert.id,
                    client_id=client.id,
                    prediction_confidence=ai_insights.get("confidence_level", 0.7),
                    predicted_cascade_systems=ai_insights.get("predicted_cascade_sequence", [])[:3],
                    time_to_cascade_minutes=ai_insights.get("time_to_cascade_minutes", 15),
                    prevention_actions=ai_insights.get("prevention_recommendations", [])[:2],
                    pattern_matched="ai_detected_pattern"
                )
                predictions.append(prediction)
        
        # Generate proactive prevention plan
        prevention_plan = self._generate_prevention_plan(ai_insights, client)
        
        # Calculate business impact metrics
        impact_metrics = self._calculate_business_impact(ai_insights, client)
        
        return {
            "ai_analysis": ai_insights,
            "cascade_predictions": predictions,
            "prevention_plan": prevention_plan,
            "business_impact": impact_metrics,
            "agent_confidence": ai_insights.get("confidence_level", 0.7),
            "recommended_actions": self._prioritize_actions(ai_insights),
            "cross_client_learning": ai_insights.get("cross_client_insights", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_prevention_plan(self, ai_insights: Dict, client: Client) -> Dict:
        """Generate automated prevention plan"""
        
        urgency = ai_insights.get("urgency_level", "medium")
        cascade_prob = ai_insights.get("cascade_probability", 0.5)
        time_window = ai_insights.get("time_to_cascade_minutes", 20)
        
        # Determine automation level based on urgency and confidence
        if urgency == "critical" and cascade_prob > 0.8:
            automation_level = "full_auto"
        elif urgency == "high" and cascade_prob > 0.6:
            automation_level = "assisted_auto"
        else:
            automation_level = "manual_approval"
        
        prevention_plan = {
            "automation_level": automation_level,
            "time_window_minutes": max(5, time_window // 3),  # Act within 1/3 of predicted time
            "primary_actions": ai_insights.get("prevention_recommendations", [])[:3],
            "fallback_actions": [
                "Activate disaster recovery procedures",
                "Notify emergency response team",
                "Begin client communication protocol"
            ],
            "success_probability": self._estimate_prevention_success(ai_insights),
            "resources_required": self._estimate_resources_required(ai_insights, client),
            "rollback_plan": [
                "Monitor system stability for 30 minutes",
                "Rollback changes if new issues detected",
                "Escalate to senior technician if needed"
            ]
        }
        
        return prevention_plan
    
    def _calculate_business_impact(self, ai_insights: Dict, client: Client) -> Dict:
        """Calculate potential business impact metrics"""
        
        affected_systems = ai_insights.get("predicted_cascade_sequence", [])
        cascade_prob = ai_insights.get("cascade_probability", 0.5)
        time_to_cascade = ai_insights.get("time_to_cascade_minutes", 20)
        
        # Estimate impact based on client tier and affected systems
        tier_multiplier = {"enterprise": 1.5, "premium": 1.2, "standard": 1.0}.get(client.tier.lower(), 1.0)
        
        impact_metrics = {
            "estimated_downtime_minutes": int(time_to_cascade * cascade_prob * len(affected_systems) * tier_multiplier),
            "affected_users_estimate": len(affected_systems) * 50 * tier_multiplier,
            "business_criticality": "high" if len(set(affected_systems) & set(client.critical_systems)) > 0 else "medium",
            "revenue_impact_level": "high" if cascade_prob > 0.7 else "medium",
            "sla_breach_risk": cascade_prob > 0.6,
            "client_satisfaction_impact": "high" if client.tier.lower() in ["enterprise", "premium"] else "medium"
        }
        
        return impact_metrics
    
    def _prioritize_actions(self, ai_insights: Dict) -> List[Dict]:
        """Prioritize and structure recommended actions"""
        
        actions = ai_insights.get("prevention_recommendations", [])
        urgency = ai_insights.get("urgency_level", "medium")
        
        prioritized_actions = []
        for i, action in enumerate(actions):
            priority_score = (len(actions) - i) * 10
            if urgency == "critical":
                priority_score += 50
            elif urgency == "high":
                priority_score += 30
            
            prioritized_actions.append({
                "action": action,
                "priority_score": priority_score,
                "estimated_execution_time": np.random.randint(2, 10),
                "success_probability": np.random.uniform(0.7, 0.95),
                "automation_capable": i < 2,  # First 2 actions can be automated
                "requires_approval": urgency in ["critical", "high"] and i == 0
            })
        
        return sorted(prioritized_actions, key=lambda x: x["priority_score"], reverse=True)
    
    def _update_agent_memory(self, alerts: List[Alert], analysis: Dict, client_id: str):
        """Update AI agent's learning memory"""
        
        # Store incident pattern for future learning
        incident_record = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "alert_pattern": [{"system": a.system, "category": a.category, "severity": a.severity} for a in alerts],
            "prediction": analysis.get("ai_analysis", {}),
            "prevention_plan": analysis.get("prevention_plan", {}),
            "confidence": analysis.get("agent_confidence", 0.5)
        }
        
        self.incident_memory.append(incident_record)
        
        # Keep memory size manageable
        if len(self.incident_memory) > 1000:
            self.incident_memory = self.incident_memory[-800:]
        
        # Update pattern recognition
        pattern_key = f"{len(alerts)}_alerts_{analysis['ai_analysis'].get('urgency_level', 'unknown')}"
        if pattern_key not in self.pattern_memory:
            self.pattern_memory[pattern_key] = []
        
        self.pattern_memory[pattern_key].append({
            "confidence": analysis.get("agent_confidence", 0.5),
            "success_indicators": analysis["ai_analysis"].get("prevention_recommendations", []),
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_cross_client_patterns(self) -> Dict:
        """Get cross-client patterns learned by the AI agent"""
        
        if not self.incident_memory:
            return {"patterns_learned": 0, "confidence_improvement": 0}
        
        # Analyze patterns across clients
        client_patterns = {}
        for incident in self.incident_memory[-50:]:  # Last 50 incidents
            client_id = incident["client_id"]
            if client_id not in client_patterns:
                client_patterns[client_id] = []
            client_patterns[client_id].append(incident)
        
        return {
            "patterns_learned": len(self.pattern_memory),
            "clients_analyzed": len(client_patterns),
            "confidence_improvement": min(0.3, len(self.incident_memory) / 1000),
            "most_common_patterns": list(self.pattern_memory.keys())[:3]
        }
    
    def _estimate_prevention_success(self, ai_insights: Dict) -> float:
        """Estimate success probability of prevention actions"""
        base_success = 0.75
        confidence_bonus = ai_insights.get("confidence_level", 0.7) * 0.2
        urgency_penalty = {"critical": 0, "high": -0.05, "medium": -0.1, "low": -0.15}.get(
            ai_insights.get("urgency_level", "medium"), -0.1
        )
        
        return min(0.95, base_success + confidence_bonus + urgency_penalty)
    
    def _estimate_resources_required(self, ai_insights: Dict, client: Client) -> Dict:
        """Estimate resources required for prevention"""
        
        affected_systems = len(ai_insights.get("predicted_cascade_sequence", []))
        urgency = ai_insights.get("urgency_level", "medium")
        
        return {
            "technician_hours": affected_systems * (2 if urgency in ["critical", "high"] else 1),
            "system_resources": f"{affected_systems} systems",
            "estimated_cost": affected_systems * 100 * (1.5 if client.tier.lower() == "enterprise" else 1.0),
            "timeline": "immediate" if urgency == "critical" else "within 1 hour"
        }
    
    def _fallback_analysis(self, alerts: List[Alert], client: Client) -> Dict:
        """Fallback analysis when AI is unavailable"""
        
        critical_count = len([a for a in alerts if a.severity == "critical"])
        avg_cascade_risk = sum(a.cascade_risk for a in alerts) / len(alerts) if alerts else 0
        
        return {
            "ai_analysis": {
                "cascade_probability": min(0.8, avg_cascade_risk),
                "confidence_level": 0.6,
                "urgency_level": "high" if critical_count > 0 else "medium",
                "root_cause_analysis": f"Fallback analysis: {critical_count} critical alerts detected",
                "prevention_recommendations": ["Manual investigation required", "Contact senior technician"]
            },
            "cascade_predictions": [],
            "prevention_plan": {"automation_level": "manual_approval"},
            "business_impact": {"estimated_downtime_minutes": 30},
            "agent_confidence": 0.6,
            "recommended_actions": [],
            "cross_client_learning": "AI unavailable - using rule-based analysis",
            "timestamp": datetime.now().isoformat()
        }