import asyncio
import json
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    RandomForestClassifier = None
    LogisticRegression = None
    StandardScaler = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from app.models.alert import Alert, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecisionType(Enum):
    PREVENT = "prevent"
    MONITOR = "monitor"
    ESCALATE = "escalate"
    IGNORE = "ignore"

class ActionPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class DecisionContext:
    """Context for decision making"""
    alert: Alert
    client: Client
    related_alerts: List[Alert]
    historical_patterns: List[Dict]
    business_hours: bool
    client_tier: str
    current_load: float

@dataclass
class DecisionResult:
    """Result of autonomous decision"""
    decision: DecisionType
    priority: ActionPriority
    confidence: float
    reasoning: str
    business_impact_score: float
    cost_impact_score: float
    sla_risk_score: float
    recommended_actions: List[str]
    estimated_execution_time: int  # minutes
    success_probability: float
    fallback_used: bool = False

class DeterministicScorer:
    """
    Deterministic scorer for business logic (cost impact, SLA, etc.)
    Uses NumPy/Scikit-learn for core ranking
    """
    
    def __init__(self):
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.decision_model = None
        self._initialize_models()
        
        # Business logic weights
        self.weights = {
            'severity': 0.25,
            'cascade_risk': 0.20,
            'client_tier': 0.15,
            'business_hours': 0.10,
            'system_criticality': 0.15,
            'historical_frequency': 0.10,
            'load_impact': 0.05
        }
    
    def _initialize_models(self):
        """Initialize ML models for decision scoring"""
        if not SKLEARN_AVAILABLE:
            logger.warning("⚠️ Scikit-learn not available, using fallback scoring")
            return
        
        try:
            # Train a simple decision model on synthetic data
            self._train_decision_model()
            logger.info("✅ Deterministic scorer models initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize models: {e}")
            self.decision_model = None
    
    def _train_decision_model(self):
        """Train decision model on synthetic business data"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [severity, cascade_risk, client_tier, business_hours, system_criticality, historical_freq, load_impact]
        X = np.random.rand(n_samples, 7)
        
        # Labels: 0=ignore, 1=monitor, 2=prevent, 3=escalate
        y = np.random.randint(0, 4, n_samples)
        
        # Train model
        self.decision_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.decision_model.fit(X, y)
        
        # Fit scaler
        self.scaler.fit(X)
    
    def score_decision(self, context: DecisionContext) -> Dict[str, float]:
        """Score decision using deterministic business logic"""
        
        # Extract features
        features = self._extract_features(context)
        
        # Calculate individual scores
        scores = {
            'severity_score': self._score_severity(context.alert.severity),
            'cascade_risk_score': context.alert.cascade_risk,
            'client_tier_score': self._score_client_tier(context.client_tier),
            'business_hours_score': 1.0 if context.business_hours else 0.5,
            'system_criticality_score': self._score_system_criticality(context.alert.system, context.client),
            'historical_frequency_score': self._score_historical_frequency(context.alert, context.historical_patterns),
            'load_impact_score': min(1.0, context.current_load / 100.0)
        }
        
        # Calculate weighted business impact
        business_impact = sum(scores[key] * self.weights[key.replace('_score', '')] 
                            for key in scores.keys())
        
        # Calculate cost impact (higher severity + business hours = higher cost)
        cost_impact = (scores['severity_score'] * scores['business_hours_score'] * 
                      scores['client_tier_score'])
        
        # Calculate SLA risk (cascade risk + system criticality)
        sla_risk = (scores['cascade_risk_score'] * scores['system_criticality_score'])
        
        # Use ML model if available
        ml_decision = None
        if self.decision_model and self.scaler:
            try:
                feature_array = np.array([list(scores.values())]).reshape(1, -1)
                scaled_features = self.scaler.transform(feature_array)
                ml_decision = self.decision_model.predict(scaled_features)[0]
            except Exception as e:
                logger.warning(f"ML model prediction failed: {e}")
        
        return {
            'business_impact': business_impact,
            'cost_impact': cost_impact,
            'sla_risk': sla_risk,
            'ml_decision': ml_decision,
            'feature_scores': scores
        }
    
    def _extract_features(self, context: DecisionContext) -> List[float]:
        """Extract numerical features from context"""
        return [
            self._score_severity(context.alert.severity),
            context.alert.cascade_risk,
            self._score_client_tier(context.client_tier),
            1.0 if context.business_hours else 0.0,
            self._score_system_criticality(context.alert.system, context.client),
            self._score_historical_frequency(context.alert, context.historical_patterns),
            min(1.0, context.current_load / 100.0)
        ]
    
    def _score_severity(self, severity: str) -> float:
        """Score alert severity"""
        severity_scores = {
            'critical': 1.0,
            'warning': 0.7,
            'info': 0.3,
            'low': 0.1
        }
        return severity_scores.get(severity, 0.5)
    
    def _score_client_tier(self, tier: str) -> float:
        """Score client tier importance"""
        tier_scores = {
            'enterprise': 1.0,
            'premium': 0.8,
            'standard': 0.6,
            'basic': 0.4
        }
        return tier_scores.get(tier.lower(), 0.5)
    
    def _score_system_criticality(self, system: str, client: Client) -> float:
        """Score system criticality based on client dependencies"""
        if system in client.critical_systems:
            return 1.0
        
        # Check if system has many dependencies
        dependencies = client.system_dependencies.get(system, [])
        if len(dependencies) > 2:
            return 0.8
        elif len(dependencies) > 0:
            return 0.6
        else:
            return 0.4
    
    def _score_historical_frequency(self, alert: Alert, patterns: List[Dict]) -> float:
        """Score based on historical frequency of similar alerts"""
        similar_count = 0
        for pattern in patterns:
            if (pattern.get('alert_category') == alert.category and 
                pattern.get('severity') == alert.severity):
                similar_count += 1
        
        # Normalize to 0-1 scale
        return min(1.0, similar_count / 10.0)

class AutonomousDecisionAgent:
    """
    Autonomous Decision Agent with lightweight reasoning LLM + deterministic scorer
    Primary: Gemini 1.5 Pro for reasoning
    Fallback: Deterministic scorer for core ranking + small LLM for explanation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.name = "autonomous_decision_agent"
        self.version = "2.0.0"
        
        # Initialize deterministic scorer
        self.scorer = DeterministicScorer()
        
        # Initialize LLM
        self.llm = None
        self.llm_available = False
        
        if GEMINI_AVAILABLE:
            import os
            api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
            if api_key and api_key != "demo_key":
                try:
                    genai.configure(api_key=api_key)
                    self.llm = genai.GenerativeModel('gemini-1.5-pro')
                    self.llm_available = True
                    logger.info("✅ Gemini 1.5 Pro loaded for autonomous decisions")
                except Exception as e:
                    logger.error(f"❌ Failed to load Gemini: {e}")
                    self.llm_available = False
            else:
                logger.warning("⚠️ No Gemini API key provided, using deterministic fallback")
        else:
            logger.warning("⚠️ Gemini not available, using deterministic fallback")
    
    async def make_decision(self, context: DecisionContext) -> DecisionResult:
        """
        Make autonomous decision using hybrid approach:
        1. Deterministic scorer for business logic
        2. LLM for reasoning and explanation
        """
        try:
            # Step 1: Get deterministic scores
            scores = self.scorer.score_decision(context)
            
            # Step 2: Determine decision type based on scores
            decision_type = self._determine_decision_type(scores)
            priority = self._determine_priority(scores, decision_type)
            
            # Step 3: Get LLM reasoning if available
            reasoning = ""
            fallback_used = False
            
            if self.llm_available:
                try:
                    reasoning = await self._get_llm_reasoning(context, scores, decision_type)
                except Exception as e:
                    logger.warning(f"LLM reasoning failed: {e}")
                    reasoning = self._get_fallback_reasoning(context, scores, decision_type)
                    fallback_used = True
            else:
                reasoning = self._get_fallback_reasoning(context, scores, decision_type)
                fallback_used = True
            
            # Step 4: Generate recommended actions
            actions = self._generate_actions(decision_type, context, scores)
            
            # Step 5: Calculate execution metrics
            execution_time = self._estimate_execution_time(actions, context)
            success_probability = self._estimate_success_probability(actions, scores)
            
            return DecisionResult(
                decision=decision_type,
                priority=priority,
                confidence=scores['business_impact'],
                reasoning=reasoning,
                business_impact_score=scores['business_impact'],
                cost_impact_score=scores['cost_impact'],
                sla_risk_score=scores['sla_risk'],
                recommended_actions=actions,
                estimated_execution_time=execution_time,
                success_probability=success_probability,
                fallback_used=fallback_used
            )
            
        except Exception as e:
            logger.error(f"❌ Decision making failed: {e}")
            return self._get_emergency_decision(context)
    
    def _determine_decision_type(self, scores: Dict[str, float]) -> DecisionType:
        """Determine decision type based on deterministic scores"""
        business_impact = scores['business_impact']
        sla_risk = scores['sla_risk']
        cost_impact = scores['cost_impact']
        
        # Use ML model prediction if available
        if scores.get('ml_decision') is not None:
            ml_decision = scores['ml_decision']
            decision_map = {
                0: DecisionType.IGNORE,
                1: DecisionType.MONITOR,
                2: DecisionType.PREVENT,
                3: DecisionType.ESCALATE
            }
            return decision_map.get(ml_decision, DecisionType.MONITOR)
        
        # Fallback deterministic logic
        if sla_risk > 0.8 and business_impact > 0.7:
            return DecisionType.ESCALATE
        elif business_impact > 0.6 or sla_risk > 0.6:
            return DecisionType.PREVENT
        elif business_impact > 0.3:
            return DecisionType.MONITOR
        else:
            return DecisionType.IGNORE
    
    def _determine_priority(self, scores: Dict[str, float], decision_type: DecisionType) -> ActionPriority:
        """Determine action priority based on scores and decision type"""
        business_impact = scores['business_impact']
        cost_impact = scores['cost_impact']
        
        if decision_type == DecisionType.ESCALATE or business_impact > 0.8:
            return ActionPriority.CRITICAL
        elif decision_type == DecisionType.PREVENT or business_impact > 0.6:
            return ActionPriority.HIGH
        elif decision_type == DecisionType.MONITOR or business_impact > 0.4:
            return ActionPriority.MEDIUM
        else:
            return ActionPriority.LOW
    
    async def _get_llm_reasoning(self, context: DecisionContext, scores: Dict[str, float], 
                                decision_type: DecisionType) -> str:
        """Get reasoning from Gemini 1.5 Pro"""
        
        prompt = f"""
        You are an autonomous decision agent for IT infrastructure management.
        
        ALERT CONTEXT:
        - System: {context.alert.system}
        - Severity: {context.alert.severity}
        - Message: {context.alert.message}
        - Cascade Risk: {context.alert.cascade_risk}
        - Client: {context.client.name} (Tier: {context.client_tier})
        - Business Hours: {context.business_hours}
        
        DETERMINISTIC SCORES:
        - Business Impact: {scores['business_impact']:.2f}
        - Cost Impact: {scores['cost_impact']:.2f}
        - SLA Risk: {scores['sla_risk']:.2f}
        
        DECISION: {decision_type.value.upper()}
        
        Provide a concise 2-3 sentence explanation of why this decision was made,
        focusing on business impact, cost considerations, and SLA risks.
        Be specific about the factors that influenced this decision.
        """
        
        try:
            response = await self.llm.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"LLM reasoning error: {e}")
            raise
    
    def _get_fallback_reasoning(self, context: DecisionContext, scores: Dict[str, float], 
                               decision_type: DecisionType) -> str:
        """Generate fallback reasoning without LLM"""
        
        reasons = []
        
        if scores['business_impact'] > 0.7:
            reasons.append("High business impact detected")
        
        if scores['sla_risk'] > 0.6:
            reasons.append("Significant SLA risk identified")
        
        if scores['cost_impact'] > 0.5:
            reasons.append("Cost impact considerations")
        
        if context.business_hours:
            reasons.append("During business hours - higher priority")
        
        if context.client_tier.lower() in ['enterprise', 'premium']:
            reasons.append(f"High-tier client ({context.client_tier})")
        
        if not reasons:
            reasons.append("Standard monitoring required")
        
        return f"Decision based on: {', '.join(reasons)}. " + \
               f"Business impact: {scores['business_impact']:.1f}, " + \
               f"SLA risk: {scores['sla_risk']:.1f}"
    
    def _generate_actions(self, decision_type: DecisionType, context: DecisionContext, 
                         scores: Dict[str, float]) -> List[str]:
        """Generate recommended actions based on decision type"""
        
        actions = []
        
        if decision_type == DecisionType.ESCALATE:
            actions.extend([
                "Immediately notify senior technician",
                "Activate emergency response protocol",
                "Begin client communication",
                "Prepare rollback procedures"
            ])
        elif decision_type == DecisionType.PREVENT:
            actions.extend([
                "Scale affected system resources",
                "Enable automated failover",
                "Clear system bottlenecks",
                "Monitor cascade indicators"
            ])
        elif decision_type == DecisionType.MONITOR:
            actions.extend([
                "Increase monitoring frequency",
                "Set up alert thresholds",
                "Document incident pattern",
                "Prepare response plan"
            ])
        else:  # IGNORE
            actions.extend([
                "Log for pattern analysis",
                "Continue standard monitoring",
                "Update noise filters"
            ])
        
        # Add system-specific actions
        if context.alert.system == "database":
            actions.append("Check connection pool status")
        elif context.alert.system == "network-gateway":
            actions.append("Verify routing tables")
        elif "web" in context.alert.system:
            actions.append("Check application health")
        
        return actions[:4]  # Limit to 4 actions
    
    def _estimate_execution_time(self, actions: List[str], context: DecisionContext) -> int:
        """Estimate execution time in minutes"""
        base_time = len(actions) * 2  # 2 minutes per action
        
        # Adjust for client tier
        if context.client_tier.lower() == 'enterprise':
            base_time += 5  # More careful execution
        elif context.client_tier.lower() == 'basic':
            base_time -= 2  # Faster execution
        
        # Adjust for business hours
        if context.business_hours:
            base_time += 3  # More careful during business hours
        
        return max(1, base_time)
    
    def _estimate_success_probability(self, actions: List[str], scores: Dict[str, float]) -> float:
        """Estimate success probability of actions"""
        base_probability = 0.8
        
        # Adjust based on business impact (higher impact = more resources = higher success)
        if scores['business_impact'] > 0.7:
            base_probability += 0.1
        elif scores['business_impact'] < 0.3:
            base_probability -= 0.1
        
        # Adjust based on number of actions (more actions = more complexity)
        if len(actions) > 3:
            base_probability -= 0.05
        
        return max(0.5, min(0.95, base_probability))
    
    def _get_emergency_decision(self, context: DecisionContext) -> DecisionResult:
        """Emergency fallback decision"""
        return DecisionResult(
            decision=DecisionType.MONITOR,
            priority=ActionPriority.MEDIUM,
            confidence=0.5,
            reasoning="Emergency fallback: System error in decision making",
            business_impact_score=0.5,
            cost_impact_score=0.5,
            sla_risk_score=0.5,
            recommended_actions=["Manual review required", "Monitor system status"],
            estimated_execution_time=5,
            success_probability=0.7,
            fallback_used=True
        )
    
    def get_agent_info(self) -> Dict:
        """Get agent information"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": [
                "deterministic_business_scoring",
                "ml_decision_prediction" if SKLEARN_AVAILABLE else "fallback_scoring",
                "llm_reasoning" if self.llm_available else "fallback_reasoning",
                "autonomous_decision_making",
                "business_impact_analysis",
                "cost_impact_assessment",
                "sla_risk_evaluation"
            ],
            "models_loaded": {
                "gemini_1_5_pro": self.llm_available,
                "scikit_learn": SKLEARN_AVAILABLE,
                "deterministic_scorer": True
            },
            "status": "ready" if (self.llm_available or SKLEARN_AVAILABLE) else "degraded"
        }
