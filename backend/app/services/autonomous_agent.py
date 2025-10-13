import asyncio
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from app.models.alert import Alert, Client, CascadePrediction
from app.services.agentic_ai_services import AgenticAIService

logger = logging.getLogger(__name__)

class AgentState(Enum):
    MONITORING = "monitoring"
    ANALYZING = "analyzing"
    PREDICTING = "predicting"
    PREVENTING = "preventing"
    LEARNING = "learning"
    ESCALATING = "escalating"

class AutonomousAgent:
    """
    Autonomous AI Agent that continuously monitors, predicts, and prevents cascade failures
    This is the main orchestrator that makes decisions and takes actions
    """
    
    def __init__(self, ai_service: AgenticAIService):
        self.ai_service = ai_service
        self.state = AgentState.MONITORING
        self.active_clients = {}
        self.prevention_history = []
        self.learning_cycles = 0
        self.success_rate = 0.0
        self.autonomous_actions_taken = 0
        
        # Agent personality and decision-making parameters
        self.risk_tolerance = 0.7  # 0-1, higher = more aggressive prevention
        self.learning_rate = 0.1   # How quickly agent adapts
        self.confidence_threshold = 0.6  # Minimum confidence to take action
        
        # Agent memory and learning
        self.decision_history = []
        self.pattern_recognition = {}
        self.client_risk_profiles = {}
        
        logger.info("🤖 Autonomous Agent initialized - Ready for cascade prevention")
    
    async def start_autonomous_operation(self, clients: List[Client]):
        """
        Start the autonomous agent's continuous operation
        This is the main loop that makes the agent truly autonomous
        """
        logger.info("🚀 Starting autonomous cascade prevention agent...")
        
        # Initialize client monitoring
        for client in clients:
            self.active_clients[client.id] = {
                "client": client,
                "last_analysis": None,
                "risk_level": "low",
                "prevention_count": 0,
                "success_count": 0
            }
        
        # Start continuous monitoring loop
        while True:
            try:
                await self._autonomous_cycle()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Agent cycle error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _autonomous_cycle(self):
        """Single cycle of autonomous operation"""
        current_time = datetime.now()
        
        # Update agent state
        self.state = AgentState.MONITORING
        
        # Get current alerts for all clients
        all_alerts = await self._get_current_alerts()
        
        # Process each client
        for client_id, client_data in self.active_clients.items():
            client = client_data["client"]
            client_alerts = [a for a in all_alerts if a.client_id == client_id]
            
            if not client_alerts:
                continue
            
            # Analyze alerts for this client
            await self._analyze_client_alerts(client, client_alerts)
        
        # Update agent learning
        await self._update_agent_learning()
        
        # Log agent status
        self._log_agent_status()
    
    async def _analyze_client_alerts(self, client: Client, alerts: List[Alert]):
        """Analyze alerts for a specific client and take autonomous action"""
        
        # Filter high-risk alerts
        high_risk_alerts = [a for a in alerts if a.cascade_risk > 0.5 or a.severity == "critical"]
        
        if not high_risk_alerts:
            return
        
        self.state = AgentState.ANALYZING
        
        # Get AI analysis
        historical_data = self._get_historical_data(client.id)
        analysis = await self.ai_service.analyze_cascade_risk(high_risk_alerts, client, historical_data)
        
        # Make autonomous decision
        decision = await self._make_autonomous_decision(analysis, client, high_risk_alerts)
        
        # Execute decision if approved
        if decision["action_required"]:
            await self._execute_autonomous_action(decision, client, high_risk_alerts)
        
        # Update client data
        self.active_clients[client.id]["last_analysis"] = {
            "timestamp": current_time,
            "alerts_analyzed": len(high_risk_alerts),
            "cascade_probability": analysis["ai_analysis"]["cascade_probability"],
            "confidence": analysis["agent_confidence"],
            "action_taken": decision["action_required"]
        }
    
    async def _make_autonomous_decision(self, analysis: Dict, client: Client, alerts: List[Alert]) -> Dict:
        """Make autonomous decision about whether to take prevention action"""
        
        ai_analysis = analysis["ai_analysis"]
        cascade_prob = ai_analysis["cascade_probability"]
        confidence = analysis["agent_confidence"]
        urgency = ai_analysis["urgency_level"]
        
        # Decision logic based on agent parameters
        decision = {
            "action_required": False,
            "action_type": None,
            "confidence": confidence,
            "reasoning": "",
            "risk_assessment": "low"
        }
        
        # High confidence, high probability = immediate action
        if confidence > self.confidence_threshold and cascade_prob > 0.8:
            decision.update({
                "action_required": True,
                "action_type": "immediate_prevention",
                "reasoning": f"High confidence ({confidence:.2f}) cascade prediction ({cascade_prob:.2f})",
                "risk_assessment": "critical"
            })
        
        # Medium confidence, high probability = assisted action
        elif confidence > 0.5 and cascade_prob > 0.6:
            decision.update({
                "action_required": True,
                "action_type": "assisted_prevention",
                "reasoning": f"Medium confidence ({confidence:.2f}) but high cascade risk ({cascade_prob:.2f})",
                "risk_assessment": "high"
            })
        
        # Low confidence but critical urgency = escalate
        elif urgency == "critical" and confidence > 0.4:
            decision.update({
                "action_required": True,
                "action_type": "escalate_human",
                "reasoning": f"Critical urgency but low confidence - human intervention needed",
                "risk_assessment": "high"
            })
        
        # Learning opportunity
        elif cascade_prob > 0.4:
            decision.update({
                "action_required": False,
                "action_type": "monitor_learn",
                "reasoning": f"Learning opportunity - monitoring pattern development",
                "risk_assessment": "medium"
            })
        
        # Store decision for learning
        self.decision_history.append({
            "timestamp": datetime.now(),
            "client_id": client.id,
            "decision": decision,
            "context": {
                "cascade_prob": cascade_prob,
                "confidence": confidence,
                "urgency": urgency,
                "alert_count": len(alerts)
            }
        })
        
        return decision
    
    async def _execute_autonomous_action(self, decision: Dict, client: Client, alerts: List[Alert]):
        """Execute the autonomous action decided by the agent"""
        
        self.state = AgentState.PREVENTING
        action_type = decision["action_type"]
        
        logger.info(f"🤖 Agent taking {action_type} action for {client.name}")
        
        try:
            if action_type == "immediate_prevention":
                await self._execute_immediate_prevention(client, alerts)
            
            elif action_type == "assisted_prevention":
                await self._execute_assisted_prevention(client, alerts)
            
            elif action_type == "escalate_human":
                await self._escalate_to_human(client, alerts, decision)
            
            elif action_type == "monitor_learn":
                await self._monitor_and_learn(client, alerts)
            
            # Update success tracking
            self.autonomous_actions_taken += 1
            self.active_clients[client.id]["prevention_count"] += 1
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            await self._handle_action_failure(client, alerts, e)
    
    async def _execute_immediate_prevention(self, client: Client, alerts: List[Alert]):
        """Execute immediate prevention actions autonomously"""
        
        # Simulate immediate prevention actions
        prevention_actions = [
            "🔄 Restarting critical services",
            "⚡ Scaling database resources",
            "🛡️ Activating failover systems",
            "📊 Clearing connection pools",
            "🔧 Optimizing system parameters"
        ]
        
        for action in prevention_actions:
            logger.info(f"🤖 Executing: {action} for {client.name}")
            # In real implementation, this would call actual system APIs
            await asyncio.sleep(0.5)  # Simulate action time
        
        # Update success tracking
        self.active_clients[client.id]["success_count"] += 1
        
        # Store prevention record
        self.prevention_history.append({
            "timestamp": datetime.now(),
            "client_id": client.id,
            "action_type": "immediate_prevention",
            "alerts_addressed": len(alerts),
            "success": True
        })
    
    async def _execute_assisted_prevention(self, client: Client, alerts: List[Alert]):
        """Execute assisted prevention with human oversight"""
        
        # Simulate assisted prevention
        logger.info(f"🤖 Assisted prevention for {client.name} - preparing recommendations")
        
        # Generate detailed prevention plan
        prevention_plan = {
            "immediate_actions": [
                "Monitor system metrics closely",
                "Prepare resource scaling",
                "Notify on-call technician"
            ],
            "prepared_actions": [
                "Database optimization ready",
                "Load balancer configuration prepared",
                "Emergency contacts notified"
            ]
        }
        
        # Store prevention record
        self.prevention_history.append({
            "timestamp": datetime.now(),
            "client_id": client.id,
            "action_type": "assisted_prevention",
            "alerts_addressed": len(alerts),
            "prevention_plan": prevention_plan,
            "success": True
        })
    
    async def _escalate_to_human(self, client: Client, alerts: List[Alert], decision: Dict):
        """Escalate to human operator with detailed context"""
        
        escalation_data = {
            "client": client.name,
            "urgency": "CRITICAL",
            "reasoning": decision["reasoning"],
            "alerts": [{"system": a.system, "message": a.message, "severity": a.severity} for a in alerts],
            "recommended_actions": [
                "Immediate system inspection required",
                "Consider emergency maintenance window",
                "Prepare for potential service disruption"
            ],
            "agent_confidence": decision["confidence"]
        }
        
        logger.warning(f"🚨 ESCALATION: {client.name} - {decision['reasoning']}")
        
        # Store escalation record
        self.prevention_history.append({
            "timestamp": datetime.now(),
            "client_id": client.id,
            "action_type": "escalate_human",
            "escalation_data": escalation_data,
            "success": True
        })
    
    async def _monitor_and_learn(self, client: Client, alerts: List[Alert]):
        """Monitor pattern development for learning"""
        
        # Update pattern recognition
        pattern_key = f"{client.id}_{len(alerts)}_alerts"
        if pattern_key not in self.pattern_recognition:
            self.pattern_recognition[pattern_key] = []
        
        self.pattern_recognition[pattern_key].append({
            "timestamp": datetime.now(),
            "alerts": [{"system": a.system, "category": a.category} for a in alerts],
            "outcome": "monitoring"
        })
        
        logger.info(f"🧠 Learning mode: Monitoring {client.name} pattern development")
    
    async def _update_agent_learning(self):
        """Update agent learning based on recent decisions and outcomes"""
        
        self.state = AgentState.LEARNING
        self.learning_cycles += 1
        
        # Calculate success rate
        if self.prevention_history:
            recent_preventions = [p for p in self.prevention_history if 
                                (datetime.now() - p["timestamp"]).total_seconds() < 3600]  # Last hour
            
            if recent_preventions:
                successful = len([p for p in recent_preventions if p.get("success", False)])
                self.success_rate = successful / len(recent_preventions)
        
        # Adjust agent parameters based on performance
        if self.success_rate > 0.8:
            self.confidence_threshold = max(0.5, self.confidence_threshold - 0.05)
            logger.info("📈 Agent performance improving - lowering confidence threshold")
        elif self.success_rate < 0.6:
            self.confidence_threshold = min(0.8, self.confidence_threshold + 0.05)
            logger.info("📉 Agent performance declining - raising confidence threshold")
        
        # Update client risk profiles
        for client_id, client_data in self.active_clients.items():
            if client_data["last_analysis"]:
                recent_cascade_prob = client_data["last_analysis"]["cascade_probability"]
                if recent_cascade_prob > 0.7:
                    self.client_risk_profiles[client_id] = "high"
                elif recent_cascade_prob > 0.4:
                    self.client_risk_profiles[client_id] = "medium"
                else:
                    self.client_risk_profiles[client_id] = "low"
    
    def _log_agent_status(self):
        """Log current agent status for monitoring"""
        
        status = {
            "state": self.state.value,
            "active_clients": len(self.active_clients),
            "actions_taken": self.autonomous_actions_taken,
            "success_rate": f"{self.success_rate:.2f}",
            "learning_cycles": self.learning_cycles,
            "confidence_threshold": self.confidence_threshold,
            "high_risk_clients": len([c for c in self.client_risk_profiles.values() if c == "high"])
        }
        
        logger.info(f"🤖 Agent Status: {json.dumps(status, indent=2)}")
    
    async def _get_current_alerts(self) -> List[Alert]:
        """Get current alerts from the system"""
        # This would integrate with your actual alert system
        # For now, return empty list - will be populated by the main system
        return []
    
    def _get_historical_data(self, client_id: str) -> List[Dict]:
        """Get historical incident data for a client"""
        # This would integrate with your historical data storage
        return []
    
    async def _handle_action_failure(self, client: Client, alerts: List[Alert], error: Exception):
        """Handle failures in autonomous action execution"""
        
        logger.error(f"❌ Action failure for {client.name}: {error}")
        
        # Escalate to human on failure
        await self._escalate_to_human(client, alerts, {
            "reasoning": f"Autonomous action failed: {str(error)}",
            "confidence": 0.0
        })
    
    def get_agent_metrics(self) -> Dict:
        """Get comprehensive agent performance metrics"""
        
        return {
            "agent_state": self.state.value,
            "total_actions_taken": self.autonomous_actions_taken,
            "success_rate": self.success_rate,
            "learning_cycles": self.learning_cycles,
            "confidence_threshold": self.confidence_threshold,
            "risk_tolerance": self.risk_tolerance,
            "active_clients": len(self.active_clients),
            "client_risk_profiles": self.client_risk_profiles,
            "recent_decisions": len(self.decision_history),
            "prevention_history_count": len(self.prevention_history),
            "patterns_learned": len(self.pattern_recognition)
        }
    
    def get_agent_insights(self) -> Dict:
        """Get AI agent insights and recommendations"""
        
        insights = {
            "agent_personality": {
                "risk_tolerance": "aggressive" if self.risk_tolerance > 0.7 else "conservative",
                "learning_speed": "fast" if self.learning_rate > 0.1 else "steady",
                "confidence_level": "high" if self.confidence_threshold < 0.6 else "cautious"
            },
            "performance_analysis": {
                "success_rate": f"{self.success_rate:.1%}",
                "efficiency": "high" if self.success_rate > 0.8 else "improving",
                "reliability": "excellent" if self.autonomous_actions_taken > 10 and self.success_rate > 0.7 else "learning"
            },
            "learning_insights": {
                "patterns_recognized": len(self.pattern_recognition),
                "decisions_made": len(self.decision_history),
                "adaptation_level": min(1.0, self.learning_cycles / 100)
            },
            "recommendations": self._generate_agent_recommendations()
        }
        
        return insights
    
    def _generate_agent_recommendations(self) -> List[str]:
        """Generate recommendations for improving agent performance"""
        
        recommendations = []
        
        if self.success_rate < 0.6:
            recommendations.append("Consider increasing confidence threshold for more conservative decisions")
        
        if self.autonomous_actions_taken < 5:
            recommendations.append("Agent needs more operational experience - continue monitoring")
        
        if len(self.pattern_recognition) < 10:
            recommendations.append("Collect more pattern data for better learning")
        
        if self.learning_cycles > 50 and self.success_rate > 0.8:
            recommendations.append("Agent performing well - consider expanding autonomous capabilities")
        
        return recommendations
