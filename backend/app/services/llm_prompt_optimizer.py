"""
LLM Prompt Optimizer for Cascade Prediction Agent
Optimizes prompts for maximum LLM effectiveness with rich data context
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PromptContext:
    """Rich context for LLM prompts"""
    system_metrics: Dict[str, Any]
    service_health: Dict[str, Any]
    external_factors: Optional[Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    client_info: Dict[str, Any]
    historical_data: List[Dict[str, Any]]
    cross_client_insights: Dict[str, Any]

class LLMPromptOptimizer:
    """Optimizes LLM prompts for maximum effectiveness"""
    
    def __init__(self):
        self.prompt_templates = self._initialize_prompt_templates()
        self.few_shot_examples = self._initialize_few_shot_examples()
        self.reasoning_chains = self._initialize_reasoning_chains()
    
    def create_optimized_prompt(self, context: PromptContext) -> str:
        """Create an optimized prompt with rich context"""
        try:
            # Build the comprehensive prompt
            prompt_parts = [
                self._build_system_instruction(),
                self._build_context_section(context),
                self._build_analysis_framework(),
                self._build_few_shot_examples(),
                self._build_output_format(),
                self._build_reasoning_chain()
            ]
            
            return "\n\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"Error creating optimized prompt: {e}")
            return self._get_fallback_prompt(context)
    
    def _build_system_instruction(self) -> str:
        """Build the system instruction for the LLM"""
        return """# CASCADE PREDICTION AGENT - ADVANCED AI ANALYSIS

You are an expert AI agent specializing in cascade failure prediction and system reliability analysis. Your role is to analyze complex system data and provide intelligent predictions about potential cascade failures.

## YOUR EXPERTISE:
- System architecture analysis
- Resource exhaustion prediction
- Dependency chain analysis
- Temporal pattern recognition
- Risk assessment and mitigation
- Business impact analysis

## YOUR MISSION:
Analyze the provided system data and predict whether a cascade failure will occur within the next 30 minutes, providing actionable insights for prevention."""
    
    def _build_context_section(self, context: PromptContext) -> str:
        """Build the context section with rich data"""
        context_sections = []
        
        # System Health Overview
        if context.system_metrics:
            context_sections.append(self._format_system_metrics(context.system_metrics))
        
        # Service Health Status
        if context.service_health:
            context_sections.append(self._format_service_health(context.service_health))
        
        # Current Alerts Analysis
        if context.alerts:
            context_sections.append(self._format_alerts_analysis(context.alerts))
        
        # Trend Analysis
        if context.trend_analysis:
            context_sections.append(self._format_trend_analysis(context.trend_analysis))
        
        # External Factors
        if context.external_factors:
            context_sections.append(self._format_external_factors(context.external_factors))
        
        # Client Infrastructure
        if context.client_info:
            context_sections.append(self._format_client_infrastructure(context.client_info))
        
        # Historical Patterns
        if context.historical_data:
            context_sections.append(self._format_historical_patterns(context.historical_data))
        
        # Cross-Client Insights
        if context.cross_client_insights:
            context_sections.append(self._format_cross_client_insights(context.cross_client_insights))
        
        return "## SYSTEM ANALYSIS CONTEXT\n\n" + "\n\n".join(context_sections)
    
    def _format_system_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format system metrics for LLM analysis"""
        return f"""### REAL-TIME SYSTEM METRICS
**Timestamp**: {metrics.get('timestamp', 'Unknown')}

**CPU Performance**:
- Current Usage: {metrics.get('cpu_percent', 0):.1f}%
- Load Average: {metrics.get('cpu_load_avg', [0, 0, 0])}
- Cores Available: {metrics.get('cpu_cores', 1)}

**Memory Status**:
- Total Memory: {metrics.get('memory_total', 0) / (1024**3):.1f} GB
- Used Memory: {metrics.get('memory_used', 0) / (1024**3):.1f} GB ({metrics.get('memory_percent', 0):.1f}%)
- Available Memory: {metrics.get('memory_available', 0) / (1024**3):.1f} GB

**Storage Health**:
{self._format_disk_usage(metrics.get('disk_usage', {}))}

**Network Activity**:
- Packets In: {metrics.get('network_io', {}).get('packets_recv', 0):,}
- Packets Out: {metrics.get('network_io', {}).get('packets_sent', 0):,}
- Errors: {metrics.get('network_io', {}).get('errin', 0) + metrics.get('network_io', {}).get('errout', 0)}

**System Load**:
- Active Processes: {metrics.get('process_count', 0)}
- System Uptime: {metrics.get('uptime_seconds', 0) / 3600:.1f} hours
- Boot Time: {datetime.fromtimestamp(metrics.get('boot_time', 0)).strftime('%Y-%m-%d %H:%M:%S')}"""
    
    def _format_disk_usage(self, disk_usage: Dict[str, Dict[str, Any]]) -> str:
        """Format disk usage information"""
        if not disk_usage:
            return "- No disk usage data available"
        
        disk_info = []
        for mount, usage in disk_usage.items():
            total_gb = usage.get('total', 0) / (1024**3)
            used_gb = usage.get('used', 0) / (1024**3)
            percent = usage.get('percent', 0)
            disk_info.append(f"- {mount}: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.1f}%)")
        
        return "\n".join(disk_info)
    
    def _format_service_health(self, service_health: Dict[str, Any]) -> str:
        """Format service health information"""
        if not service_health:
            return "### SERVICE HEALTH STATUS\nNo service health data available."
        
        health_info = ["### SERVICE HEALTH STATUS"]
        for service_name, health in service_health.items():
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "critical": "🚨",
                "unknown": "❓"
            }.get(health.get('status', 'unknown'), '❓')
            
            health_info.append(f"""
**{service_name.upper()}** {status_emoji}
- Status: {health.get('status', 'unknown').upper()}
- Response Time: {health.get('response_time_ms', 'N/A')}ms
- Error Rate: {health.get('error_rate', 0):.3f}
- Dependencies: {', '.join(health.get('dependencies', []))}
- Last Check: {health.get('last_check', 'Unknown')}""")
        
        return "\n".join(health_info)
    
    def _format_alerts_analysis(self, alerts: List[Dict[str, Any]]) -> str:
        """Format alerts analysis"""
        if not alerts:
            return "### CURRENT ALERTS\nNo active alerts."
        
        alert_info = ["### CURRENT ALERTS ANALYSIS"]
        
        # Group alerts by severity
        severity_groups = {"critical": [], "warning": [], "info": []}
        for alert in alerts:
            severity = alert.get('severity', 'info')
            if severity in severity_groups:
                severity_groups[severity].append(alert)
        
        for severity, alert_list in severity_groups.items():
            if alert_list:
                severity_emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}[severity]
                alert_info.append(f"\n**{severity.upper()} ALERTS** {severity_emoji} ({len(alert_list)} alerts)")
                
                for alert in alert_list[:5]:  # Show first 5 alerts
                    minutes_ago = alert.get('minutes_ago', 0)
                    alert_info.append(f"- **{alert.get('system', 'Unknown')}**: {alert.get('message', 'No message')} ({minutes_ago}m ago)")
                
                if len(alert_list) > 5:
                    alert_info.append(f"- ... and {len(alert_list) - 5} more {severity} alerts")
        
        return "\n".join(alert_info)
    
    def _format_trend_analysis(self, trend_analysis: Dict[str, Any]) -> str:
        """Format trend analysis"""
        if not trend_analysis.get('trends_available', False):
            return "### TREND ANALYSIS\nInsufficient data for trend analysis."
        
        trend_info = ["### TREND ANALYSIS"]
        trend_info.append(f"- **CPU Trend**: {trend_analysis.get('cpu_trend', 'unknown').upper()}")
        trend_info.append(f"- **Memory Trend**: {trend_analysis.get('memory_trend', 'unknown').upper()}")
        trend_info.append(f"- **Process Trend**: {trend_analysis.get('process_trend', 'unknown').upper()}")
        trend_info.append(f"- **Overall Health**: {trend_analysis.get('overall_system_health', 'unknown').upper()}")
        
        if trend_analysis.get('anomaly_detected', False):
            anomalies = trend_analysis.get('anomaly_types', [])
            severity = trend_analysis.get('severity', 'low')
            trend_info.append(f"- **🚨 ANOMALIES DETECTED**: {', '.join(anomalies)} (Severity: {severity.upper()})")
        
        return "\n".join(trend_info)
    
    def _format_external_factors(self, external_factors: Dict[str, Any]) -> str:
        """Format external factors"""
        if not external_factors:
            return "### EXTERNAL FACTORS\nNo external factor data available."
        
        external_info = ["### EXTERNAL FACTORS"]
        external_info.append(f"- **Time**: {external_factors.get('time_of_day', 'Unknown')} ({external_factors.get('day_of_week', 'Unknown')})")
        external_info.append(f"- **Business Hours**: {'Yes' if external_factors.get('business_hours', False) else 'No'}")
        
        if external_factors.get('weather_conditions'):
            weather = external_factors['weather_conditions']
            external_info.append(f"- **Weather**: {weather.get('temperature', 'N/A')}°C, {weather.get('conditions', 'unknown')}")
        
        if external_factors.get('internet_health'):
            internet = external_factors['internet_health']
            external_info.append(f"- **Internet Health**: {internet.get('global_connectivity', 'unknown')} (Latency: {internet.get('latency', 'N/A')}ms)")
        
        return "\n".join(external_info)
    
    def _format_client_infrastructure(self, client_info: Dict[str, Any]) -> str:
        """Format client infrastructure information"""
        return f"""### CLIENT INFRASTRUCTURE
**Client**: {client_info.get('name', 'Unknown')}
**Tier**: {client_info.get('tier', 'Unknown')}
**Environment**: {client_info.get('environment', 'Unknown')}

**Critical Systems**:
{', '.join(client_info.get('critical_systems', []))}

**System Dependencies**:
{self._format_dependencies(client_info.get('system_dependencies', {}))}"""
    
    def _format_dependencies(self, dependencies: Dict[str, List[str]]) -> str:
        """Format system dependencies"""
        if not dependencies:
            return "No dependency information available."
        
        dep_info = []
        for system, deps in dependencies.items():
            dep_info.append(f"- **{system}**: {', '.join(deps)}")
        
        return "\n".join(dep_info)
    
    def _format_historical_patterns(self, historical_data: List[Dict[str, Any]]) -> str:
        """Format historical patterns"""
        if not historical_data:
            return "### HISTORICAL PATTERNS\nNo historical data available."
        
        hist_info = ["### HISTORICAL PATTERNS"]
        hist_info.append(f"**Recent Incidents**: {len(historical_data)} incidents analyzed")
        
        for incident in historical_data[-3:]:  # Show last 3 incidents
            pattern = incident.get('pattern', 'unknown')
            cascade_time = incident.get('cascade_time_minutes', 0)
            success = incident.get('prevention_successful', False)
            hist_info.append(f"- **{pattern}**: Cascade in {cascade_time}min, Prevention {'✅' if success else '❌'}")
        
        return "\n".join(hist_info)
    
    def _format_cross_client_insights(self, insights: Dict[str, Any]) -> str:
        """Format cross-client insights"""
        if not insights:
            return "### CROSS-CLIENT INSIGHTS\nNo cross-client insights available."
        
        insight_info = ["### CROSS-CLIENT INSIGHTS"]
        insight_info.append(f"- **Patterns Learned**: {insights.get('patterns_learned', 0)}")
        insight_info.append(f"- **Clients Analyzed**: {insights.get('clients_analyzed', 0)}")
        insight_info.append(f"- **Confidence Improvement**: {insights.get('confidence_improvement', 0):.1%}")
        
        return "\n".join(insight_info)
    
    def _build_analysis_framework(self) -> str:
        """Build the analysis framework"""
        return """## ANALYSIS FRAMEWORK

Perform your analysis using this structured approach:

### 1. SYSTEM HEALTH ASSESSMENT
- Evaluate current resource utilization (CPU, memory, disk, network)
- Identify resource exhaustion indicators
- Assess system stability and performance trends

### 2. DEPENDENCY CHAIN ANALYSIS
- Map system dependencies and failure propagation paths
- Identify critical failure points
- Analyze service interdependencies

### 3. TEMPORAL PATTERN RECOGNITION
- Analyze alert timing and correlation patterns
- Identify escalation sequences
- Detect anomaly patterns and trends

### 4. RISK ASSESSMENT
- Calculate cascade probability based on current conditions
- Estimate time to cascade failure
- Assess business impact and urgency

### 5. PREVENTION STRATEGY
- Identify immediate prevention actions
- Recommend long-term improvements
- Prioritize actions by effectiveness and urgency"""
    
    def _build_few_shot_examples(self) -> str:
        """Build few-shot learning examples"""
        return """## ANALYSIS EXAMPLES

### Example 1: High CPU Cascade
**Scenario**: CPU at 95%, memory at 80%, database alerts increasing
**Analysis**: Resource exhaustion cascade likely within 10-15 minutes
**Prevention**: Scale resources, restart services, clear caches
**Confidence**: 0.85

### Example 2: Network Degradation
**Scenario**: Network errors increasing, latency spikes, service timeouts
**Analysis**: Network infrastructure cascade probable within 5-8 minutes
**Prevention**: Failover to backup network, restart network services
**Confidence**: 0.78

### Example 3: Storage Exhaustion
**Scenario**: Disk space at 98%, I/O wait high, backup failures
**Analysis**: Storage cascade imminent within 3-5 minutes
**Prevention**: Emergency cleanup, archive old data, add storage
**Confidence**: 0.92"""
    
    def _build_output_format(self) -> str:
        """Build the output format specification"""
        return """## REQUIRED OUTPUT FORMAT

Respond with a JSON object containing:

```json
{
  "predicted_in": <minutes_to_cascade>,
  "confidence": <0.0_to_1.0>,
  "root_causes": ["<primary_cause>", "<secondary_cause>", ...],
  "summary": "<detailed_analysis_summary>",
  "affected_systems": ["<system1>", "<system2>", ...],
  "prevention_actions": ["<action1>", "<action2>", ...],
  "urgency_level": "<low|medium|high|critical>",
  "business_impact": "<impact_assessment>",
  "reasoning": {
    "system_health_score": <0_to_100>,
    "resource_exhaustion_risk": "<low|medium|high>",
    "dependency_chain_analysis": "<analysis>",
    "temporal_patterns": "<pattern_analysis>",
    "external_factors": "<factor_analysis>"
  }
}
```"""
    
    def _build_reasoning_chain(self) -> str:
        """Build the reasoning chain"""
        return """## REASONING PROCESS

Think through your analysis step by step:

1. **What is the current system state?**
   - Resource utilization levels
   - Service health status
   - Alert patterns and severity

2. **What are the risk factors?**
   - Resource exhaustion indicators
   - Dependency vulnerabilities
   - External environmental factors

3. **What patterns do you see?**
   - Historical incident similarities
   - Temporal correlation patterns
   - Cross-client learning insights

4. **What is the cascade probability?**
   - Based on current conditions
   - Considering all risk factors
   - Accounting for prevention effectiveness

5. **What actions should be taken?**
   - Immediate prevention steps
   - Long-term improvements
   - Priority and urgency

Provide your analysis with clear reasoning and actionable insights."""
    
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize prompt templates"""
        return {
            "system_instruction": self._build_system_instruction(),
            "analysis_framework": self._build_analysis_framework(),
            "output_format": self._build_output_format()
        }
    
    def _initialize_few_shot_examples(self) -> List[Dict[str, Any]]:
        """Initialize few-shot learning examples"""
        return [
            {
                "scenario": "High CPU cascade",
                "context": "CPU 95%, memory 80%, database alerts",
                "prediction": {"predicted_in": 12, "confidence": 0.85, "urgency": "high"},
                "reasoning": "Resource exhaustion cascade likely"
            },
            {
                "scenario": "Network degradation",
                "context": "Network errors, latency spikes, timeouts",
                "prediction": {"predicted_in": 6, "confidence": 0.78, "urgency": "critical"},
                "reasoning": "Network infrastructure cascade probable"
            }
        ]
    
    def _initialize_reasoning_chains(self) -> List[str]:
        """Initialize reasoning chains"""
        return [
            "system_health_assessment",
            "dependency_chain_analysis",
            "temporal_pattern_recognition",
            "risk_assessment",
            "prevention_strategy"
        ]
    
    def _get_fallback_prompt(self, context: PromptContext) -> str:
        """Get fallback prompt when optimization fails"""
        return f"""# CASCADE PREDICTION ANALYSIS

Analyze the following system data and predict cascade failure likelihood:

**Current Alerts**: {len(context.alerts)} alerts
**Client**: {context.client_info.get('name', 'Unknown')}
**System Health**: {context.system_metrics.get('cpu_percent', 0):.1f}% CPU, {context.system_metrics.get('memory_percent', 0):.1f}% Memory

Provide JSON response with predicted_in, confidence, root_causes, and summary."""
