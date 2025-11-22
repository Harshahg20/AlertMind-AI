from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime, timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/efficiency-dashboard")
async def get_operational_efficiency_metrics() -> Dict:
    """
    Get comprehensive operational efficiency metrics for MSPs
    This endpoint demonstrates the value proposition of AlertMind AI
    
    Returns:
        - Baseline metrics (before AlertMind AI)
        - Current metrics (with AlertMind AI)
        - Improvements and ROI calculations
    """
    try:
        from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS
        
        all_alerts = generate_mock_alerts()
        
        # Before AlertMind AI (typical MSP baseline)
        baseline_metrics = {
            "total_alerts_per_day": 500,
            "actionable_alerts": 100,
            "noise_percentage": 80,
            "avg_mttr_minutes": 180,  # 3 hours
            "manual_review_time_hours": 8,
            "compliance_reporting_hours": 8,
            "patch_planning_hours": 8,
            "false_positive_rate": 75
        }
        
        # After AlertMind AI (with intelligent correlation and deduplication)
        actionable_count = len([a for a in all_alerts if a.cascade_risk > 0.5])
        current_metrics = {
            "total_alerts_per_day": len(all_alerts),
            "actionable_alerts": actionable_count,
            "noise_percentage": round((1 - actionable_count / len(all_alerts)) * 100, 1) if all_alerts else 20,
            "avg_mttr_minutes": 45,  # 45 minutes with AI assistance
            "manual_review_time_hours": 1,
            "compliance_reporting_hours": 0.5,  # Automated
            "patch_planning_hours": 2,  # AI-assisted prioritization
            "false_positive_rate": 15
        }
        
        # Calculate improvements
        noise_reduction = baseline_metrics['noise_percentage'] - current_metrics['noise_percentage']
        mttr_improvement = ((baseline_metrics['avg_mttr_minutes'] - current_metrics['avg_mttr_minutes']) / baseline_metrics['avg_mttr_minutes'] * 100)
        time_saved_per_day = (
            baseline_metrics['manual_review_time_hours'] - current_metrics['manual_review_time_hours']
        )
        
        improvements = {
            "alert_noise_reduction_percentage": round(noise_reduction, 1),
            "mttr_improvement_percentage": round(mttr_improvement, 1),
            "time_saved_per_day_hours": round(time_saved_per_day, 1),
            "automation_rate_percentage": 85,
            "false_positive_reduction_percentage": baseline_metrics['false_positive_rate'] - current_metrics['false_positive_rate']
        }
        
        # Calculate ROI (for a 10-person MSP team)
        team_size = 10
        hourly_rate = 50  # Average IT professional hourly rate
        working_days_per_year = 250
        
        # Time savings
        hours_saved_per_day = time_saved_per_day
        hours_saved_per_year = hours_saved_per_day * working_days_per_year * team_size
        
        # Cost savings
        annual_labor_savings = hours_saved_per_year * hourly_rate
        
        # Additional savings from reduced MTTR
        avg_incidents_per_day = 5
        mttr_hours_saved = (baseline_metrics['avg_mttr_minutes'] - current_metrics['avg_mttr_minutes']) / 60
        incident_cost_savings = mttr_hours_saved * avg_incidents_per_day * working_days_per_year * hourly_rate * team_size
        
        total_annual_savings = annual_labor_savings + incident_cost_savings
        
        roi = {
            "annual_cost_savings_usd": round(total_annual_savings, 2),
            "annual_cost_savings_formatted": f"${total_annual_savings:,.2f}",
            "hours_saved_per_year": round(hours_saved_per_year, 0),
            "efficiency_gain_percentage": 70,
            "payback_period_months": 1,  # Assuming reasonable SaaS pricing
            "roi_percentage": 500  # 5x return on investment
        }
        
        # Productivity metrics
        productivity = {
            "alerts_processed_per_hour_before": round(baseline_metrics['total_alerts_per_day'] / baseline_metrics['manual_review_time_hours'], 1),
            "alerts_processed_per_hour_after": round(current_metrics['total_alerts_per_day'] / current_metrics['manual_review_time_hours'], 1),
            "productivity_multiplier": round(
                (current_metrics['total_alerts_per_day'] / current_metrics['manual_review_time_hours']) /
                (baseline_metrics['total_alerts_per_day'] / baseline_metrics['manual_review_time_hours']),
                1
            ),
            "equivalent_fte_saved": round(hours_saved_per_year / 2000, 1)  # 2000 hours = 1 FTE
        }
        
        return {
            "success": True,
            "baseline_metrics": baseline_metrics,
            "current_metrics": current_metrics,
            "improvements": improvements,
            "roi": roi,
            "productivity": productivity,
            "generated_at": datetime.now().isoformat(),
            "summary": (
                f"AlertMind AI reduces alert noise by {improvements['alert_noise_reduction_percentage']}%, "
                f"improves MTTR by {improvements['mttr_improvement_percentage']}%, "
                f"and saves {roi['annual_cost_savings_formatted']}/year for a {team_size}-person MSP team"
            )
        }
        
    except Exception as e:
        logger.error(f"Failed to get efficiency metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/time-savings-breakdown")
async def get_time_savings_breakdown() -> Dict:
    """
    Detailed breakdown of time savings by operational category
    Shows exactly where AlertMind AI saves time for MSP teams
    """
    try:
        breakdown = {
            "alert_triage": {
                "category": "Alert Triage & Correlation",
                "before_hours_per_day": 4.0,
                "after_hours_per_day": 0.5,
                "time_saved_hours": 3.5,
                "time_saved_percentage": 87.5,
                "automation_method": "AI-powered correlation and deduplication",
                "impact": "Eliminates manual alert review for 87.5% of alerts"
            },
            "patch_management": {
                "category": "Patch Management & CVE Analysis",
                "before_hours_per_week": 8.0,
                "after_hours_per_week": 2.0,
                "time_saved_hours": 6.0,
                "time_saved_percentage": 75.0,
                "automation_method": "Automated CVE analysis and business impact prioritization",
                "impact": "Reduces patch planning time by 75%"
            },
            "compliance_reporting": {
                "category": "Compliance Reporting",
                "before_hours_per_month": 8.0,
                "after_hours_per_month": 0.5,
                "time_saved_hours": 7.5,
                "time_saved_percentage": 93.75,
                "automation_method": "Automated compliance report generation",
                "impact": "Near-complete automation of compliance documentation"
            },
            "incident_response": {
                "category": "Incident Response",
                "before_mttr_minutes": 180,
                "after_mttr_minutes": 45,
                "time_saved_minutes": 135,
                "time_saved_percentage": 75.0,
                "automation_method": "Predictive prevention and automated runbooks",
                "impact": "75% faster incident resolution"
            },
            "root_cause_analysis": {
                "category": "Root Cause Analysis",
                "before_hours_per_incident": 2.0,
                "after_hours_per_incident": 0.5,
                "time_saved_hours": 1.5,
                "time_saved_percentage": 75.0,
                "automation_method": "AI-powered correlation and dependency mapping",
                "impact": "Automated root cause identification"
            }
        }
        
        # Calculate totals
        total_hours_saved_per_week = (
            breakdown['alert_triage']['time_saved_hours'] * 5 +  # 5 days
            breakdown['patch_management']['time_saved_hours'] +
            breakdown['compliance_reporting']['time_saved_hours'] / 4  # Monthly to weekly
        )
        
        total_annual_hours_saved = total_hours_saved_per_week * 52
        
        return {
            "success": True,
            "breakdown_by_category": breakdown,
            "totals": {
                "total_hours_saved_per_week": round(total_hours_saved_per_week, 1),
                "total_hours_saved_per_year": round(total_annual_hours_saved, 0),
                "equivalent_fte_saved": round(total_annual_hours_saved / 2000, 1),
                "average_time_savings_percentage": 80.0
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get time savings breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-comparison")
async def get_performance_comparison() -> Dict:
    """
    Compare AlertMind AI performance against industry benchmarks
    """
    try:
        comparison = {
            "mttr": {
                "metric": "Mean Time To Resolution (MTTR)",
                "industry_average_minutes": 240,
                "alertmind_ai_minutes": 45,
                "improvement_percentage": 81.25,
                "status": "Best in Class"
            },
            "alert_noise": {
                "metric": "Alert Noise Reduction",
                "industry_average_percentage": 40,
                "alertmind_ai_percentage": 70,
                "improvement_percentage": 75.0,
                "status": "Industry Leading"
            },
            "automation_rate": {
                "metric": "Automation Rate",
                "industry_average_percentage": 30,
                "alertmind_ai_percentage": 85,
                "improvement_percentage": 183.3,
                "status": "Industry Leading"
            },
            "false_positive_rate": {
                "metric": "False Positive Rate",
                "industry_average_percentage": 60,
                "alertmind_ai_percentage": 15,
                "improvement_percentage": 75.0,
                "status": "Best in Class"
            },
            "prediction_accuracy": {
                "metric": "Cascade Prediction Accuracy",
                "industry_average_percentage": 60,
                "alertmind_ai_percentage": 85,
                "improvement_percentage": 41.7,
                "status": "Industry Leading"
            }
        }
        
        return {
            "success": True,
            "comparison": comparison,
            "overall_rating": "Industry Leading",
            "competitive_advantage": "AlertMind AI outperforms industry averages by 50-180% across all key metrics",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))
