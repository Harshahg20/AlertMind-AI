"""
LLM Prompt Optimizer for Enhanced Cascade Prediction Agent
Optimizes prompts for better LLM performance and consistency
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PromptContext:
    """Context data for prompt optimization"""
    system_metrics: Dict[str, Any]
    service_health: Dict[str, Any]
    external_factors: Optional[Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    client_info: Dict[str, Any]
    historical_data: List[Dict[str, Any]]
    cross_client_insights: Dict[str, Any]

class LLMPromptOptimizer:
    """
    Optimizes prompts for LLM-based cascade prediction
    """
    
    def __init__(self):
        self.name = "llm_prompt_optimizer"
        self.optimization_strategies = [
            "structured_format",
            "context_prioritization", 
            "example_inclusion",
            "constraint_specification"
        ]
    
    def create_optimized_prompt(self, context: PromptContext) -> str:
        """
        Create an optimized prompt for the LLM based on context
        """
        try:
            # Build the optimized prompt
            prompt_parts = []
            
            # System instruction
            prompt_parts.append(self._get_system_instruction())
            
            # Context summary
            prompt_parts.append(self._get_context_summary(context))
            
            # Alert analysis
            prompt_parts.append(self._get_alert_analysis_section(context.alerts))
            
            # System health analysis
            prompt_parts.append(self._get_system_health_section(context))
            
            # Historical pattern analysis
            prompt_parts.append(self._get_historical_analysis_section(context.historical_data))
            
            # Output format specification
            prompt_parts.append(self._get_output_format_specification())
            
            # Examples
            prompt_parts.append(self._get_examples_section())
            
            return "\n\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"Error creating optimized prompt: {e}")
            return self._get_fallback_prompt(context)
    
    def _get_system_instruction(self) -> str:
        """Get the system instruction for the LLM"""
        return """You are an expert system administrator and AI agent specializing in cascade failure prediction for managed service providers (MSPs). Your task is to analyze system alerts, metrics, and historical data to predict potential cascade failures and provide actionable prevention recommendations.

Key capabilities:
- Analyze system alerts and identify cascade risk patterns
- Consider system health metrics, service dependencies, and external factors
- Learn from historical incidents to improve prediction accuracy
- Provide specific, actionable prevention recommendations
- Assess confidence levels based on available data quality

You must respond with a valid JSON object containing your analysis."""
    
    def _get_context_summary(self, context: PromptContext) -> str:
        """Get context summary section"""
        client_name = context.client_info.get('name', 'Unknown Client')
        client_tier = context.client_info.get('tier', 'Unknown')
        alert_count = len(context.alerts)
        
        return f"""## Analysis Context
- **Client**: {client_name} ({client_tier} tier)
- **Alerts to Analyze**: {alert_count} active alerts
- **System Metrics Available**: {'Yes' if context.system_metrics else 'No'}
- **Service Health Data**: {'Yes' if context.service_health else 'No'}
- **External Factors**: {'Yes' if context.external_factors else 'No'}
- **Historical Data**: {len(context.historical_data)} past incidents
- **Cross-Client Insights**: {len(context.cross_client_insights.get('most_common_patterns', []))} learned patterns"""
    
    def _get_alert_analysis_section(self, alerts: List[Dict[str, Any]]) -> str:
        """Get alert analysis section"""
        if not alerts:
            return "## Alert Analysis\nNo alerts to analyze."
        
        alert_summary = "## Alert Analysis\n"
        alert_summary += f"Analyzing {len(alerts)} alerts:\n\n"
        
        for i, alert in enumerate(alerts[:5], 1):  # Limit to first 5 alerts
            alert_summary += f"**Alert {i}**:\n"
            alert_summary += f"- System: {alert.get('system', 'Unknown')}\n"
            alert_summary += f"- Severity: {alert.get('severity', 'Unknown')}\n"
            alert_summary += f"- Message: {alert.get('message', 'No message')}\n"
            alert_summary += f"- Cascade Risk: {alert.get('cascade_risk', 0):.2f}\n"
            alert_summary += f"- Timestamp: {alert.get('timestamp', 'Unknown')}\n\n"
        
        if len(alerts) > 5:
            alert_summary += f"... and {len(alerts) - 5} more alerts\n"
        
        return alert_summary
    
    def _get_system_health_section(self, context: PromptContext) -> str:
        """Get system health analysis section"""
        health_section = "## System Health Analysis\n"
        
        if context.system_metrics:
            metrics = context.system_metrics
            health_section += f"- CPU Usage: {metrics.get('cpu_percent', 0):.1f}%\n"
            health_section += f"- Memory Usage: {metrics.get('memory_percent', 0):.1f}%\n"
            health_section += f"- Load Average: {metrics.get('load_average', [0, 0, 0])}\n"
            health_section += f"- Process Count: {metrics.get('process_count', 0)}\n"
        else:
            health_section += "- System metrics not available\n"
        
        if context.service_health:
            health_section += "\n**Service Health Status:**\n"
            for service, health in context.service_health.items():
                health_section += f"- {service}: {health.get('status', 'unknown')} "
                health_section += f"(response: {health.get('response_time_ms', 0):.0f}ms)\n"
        else:
            health_section += "\n- Service health data not available\n"
        
        if context.external_factors:
            health_section += "\n**External Factors:**\n"
            health_section += f"- Network Latency: {context.external_factors.get('network_latency', 0):.0f}ms\n"
            health_section += f"- External Alerts: {context.external_factors.get('external_alerts', 0)}\n"
        
        return health_section
    
    def _get_historical_analysis_section(self, historical_data: List[Dict[str, Any]]) -> str:
        """Get historical analysis section"""
        if not historical_data:
            return "## Historical Analysis\nNo historical data available."
        
        hist_section = "## Historical Analysis\n"
        hist_section += f"Analyzing {len(historical_data)} historical incidents:\n\n"
        
        # Group by pattern
        patterns = {}
        for incident in historical_data:
            pattern = incident.get('pattern', 'unknown')
            if pattern not in patterns:
                patterns[pattern] = []
            patterns[pattern].append(incident)
        
        for pattern, incidents in list(patterns.items())[:3]:  # Top 3 patterns
            hist_section += f"**Pattern: {pattern}**\n"
            hist_section += f"- Occurrences: {len(incidents)}\n"
            avg_cascade_time = sum(i.get('cascade_time_minutes', 0) for i in incidents) / len(incidents)
            hist_section += f"- Avg Cascade Time: {avg_cascade_time:.1f} minutes\n"
            success_rate = sum(1 for i in incidents if i.get('prevention_successful', False)) / len(incidents)
            hist_section += f"- Prevention Success Rate: {success_rate:.1%}\n\n"
        
        return hist_section
    
    def _get_output_format_specification(self) -> str:
        """Get output format specification"""
        return """## Required Output Format
Respond with a valid JSON object containing:

```json
{
  "predicted_in": <integer minutes until cascade>,
  "confidence": <float 0.0-1.0>,
  "root_causes": ["<cause1>", "<cause2>", ...],
  "summary": "<detailed analysis summary>",
  "urgency_level": "<critical|high|medium|low>",
  "affected_systems": ["<system1>", "<system2>", ...],
  "prevention_actions": ["<action1>", "<action2>", ...],
  "business_impact": "<impact description>",
  "reasoning": {
    "system_health_score": <integer 0-100>,
    "resource_exhaustion_risk": "<high|medium|low>",
    "dependency_chain_analysis": "<analysis>",
    "temporal_patterns": "<pattern analysis>",
    "external_factors": "<external factor analysis>"
  },
  "topology_graph": {
    "nodes": [{"id": "<system_name>", "risk": "<critical|high|medium|low>", "type": "<db|app|lb|etc>"}],
    "links": [{"source": "<system_name>", "target": "<system_name>", "status": "<active|stressed|failed>"}]
  },
  "predictive_timeline": [
    {"time_offset": 0, "event": "Current State", "severity": "low"},
    {"time_offset": 5, "event": "Database Latency Spike", "severity": "medium"},
    {"time_offset": 15, "event": "Cascade Failure", "severity": "critical"}
  ],
  "prevention_simulation": {
    "recommended_action": "Scale Database Replicas",
    "probability_reduction": 0.45,
    "time_saved": 120
  }
}
```

**Important Guidelines:**
- predicted_in: Estimate minutes until cascade (1-60)
- confidence: Your confidence in this prediction (0.0-1.0)
- root_causes: Specific technical causes identified
- urgency_level: Based on confidence and potential impact
- prevention_actions: Specific, actionable steps
- reasoning: Detailed technical analysis supporting your prediction"""
    
    def _get_examples_section(self) -> str:
        """Get examples section"""
        return """## Example Analysis

**Example 1 - High Confidence Critical Prediction:**
```json
{
  "predicted_in": 12,
  "confidence": 0.85,
  "root_causes": ["Database connection pool exhaustion", "Memory leak in web application"],
  "summary": "Critical cascade predicted within 12 minutes. Database connections are depleting rapidly due to memory leak in web application. Immediate intervention required.",
  "urgency_level": "critical",
  "affected_systems": ["database", "web-app", "api-gateway"],
  "prevention_actions": ["Restart web application", "Scale database connections", "Clear application cache"],
  "business_impact": "High - Complete service outage expected",
  "reasoning": {
    "system_health_score": 25,
    "resource_exhaustion_risk": "high",
    "dependency_chain_analysis": "Database dependency chain at critical risk",
    "temporal_patterns": "Exponential connection growth pattern detected",
    "external_factors": "No significant external factors"
  }
}
```

**Example 2 - Medium Confidence Warning:**
```json
{
  "predicted_in": 35,
  "confidence": 0.65,
  "root_causes": ["Gradual memory increase", "CPU usage trending upward"],
  "summary": "Potential cascade within 35 minutes. System resources trending toward exhaustion. Monitoring recommended.",
  "urgency_level": "medium",
  "affected_systems": ["web-app"],
  "prevention_actions": ["Monitor memory usage", "Prepare for scaling", "Check for memory leaks"],
  "business_impact": "Moderate - Service degradation expected",
  "reasoning": {
    "system_health_score": 60,
    "resource_exhaustion_risk": "medium",
    "dependency_chain_analysis": "Single system at risk",
    "temporal_patterns": "Linear resource increase pattern",
    "external_factors": "Normal external conditions"
  }
}
```"""
    
    def _get_fallback_prompt(self, context: PromptContext) -> str:
        """Get fallback prompt when optimization fails"""
        return f"""Analyze the following system alerts and predict potential cascade failures:

Client: {context.client_info.get('name', 'Unknown')}
Alerts: {len(context.alerts)} alerts detected
System Health: {'Available' if context.system_metrics else 'Not available'}

Provide a JSON response with:
- predicted_in: minutes until cascade (1-60)
- confidence: confidence level (0.0-1.0)  
- root_causes: list of identified causes
- summary: analysis summary
- urgency_level: critical|high|medium|low
- affected_systems: list of systems at risk
- prevention_actions: list of recommended actions
- business_impact: expected impact description"""