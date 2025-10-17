from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    LOW = "low"

class AlertCategory(str, Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    NETWORK = "network"
    STORAGE = "storage"
    APPLICATION = "application"
    SYSTEM = "system"

class Alert(BaseModel):
    id: str
    client_id: str
    client_name: str
    system: str
    severity: SeverityLevel
    message: str
    category: AlertCategory
    timestamp: datetime
    is_correlated: bool = False
    correlated_with: Optional[List[str]] = []
    cascade_risk: float = 0.0
    affected_systems: Optional[List[str]] = []
    is_noise: bool = False
    auto_resolved: bool = False

class Client(BaseModel):
    id: str
    name: str
    tier: str
    environment: str
    business_hours: str
    critical_systems: List[str]
    system_dependencies: Dict[str, List[str]]

class CascadePrediction(BaseModel):
    alert_id: str
    client_id: str
    prediction_confidence: float
    predicted_cascade_systems: List[str]
    time_to_cascade_minutes: int
    prevention_actions: List[str]
    pattern_matched: Optional[str] = None

class AgentPrediction(BaseModel):
    """Enhanced prediction from Cascade Prediction Agent"""
    predicted_in: int
    confidence: float
    root_causes: List[str]
    summary: str
    explanation: Optional[Dict[str, Any]] = None
    urgency_level: str = "medium"
    affected_systems: List[str] = []
    prevention_actions: List[str] = []
    pattern_matched: Optional[str] = None
    pattern: Optional[str] = None  # Added for frontend compatibility
    numeric_engine_output: Optional[Dict[str, Any]] = None
    llm_reasoning: Optional[Dict[str, Any]] = None
    agent_metadata: Optional[Dict[str, Any]] = None

class CorrelatedData(BaseModel):
    """Data structure for agent input"""
    alerts: List[Alert]
    client: Client
    historical_data: List[Dict[str, Any]] = []
    cross_client_insights: Optional[Dict[str, Any]] = None

class AlertCorrelation(BaseModel):
    primary_alert_id: str
    related_alert_ids: List[str]
    correlation_confidence: float
    correlation_type: str  # "cascade", "duplicate", "related"