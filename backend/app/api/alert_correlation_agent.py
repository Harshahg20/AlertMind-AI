from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from app.models.alert import Alert
from app.services.alert_correlation_agent import AlertCorrelationAgent
from app.api.alerts import generate_mock_alerts

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize the Alert Correlation Agent
correlation_agent = AlertCorrelationAgent(use_llm=True)

@router.post("/correlate")
async def correlate_alerts(alerts: List[Alert]) -> Dict:
    """
    Correlate alerts using the Alert Correlation Agent
    
    This endpoint takes a list of alerts and returns correlated clusters
    representing the same root cause.
    """
    try:
        if not alerts:
            raise HTTPException(status_code=400, detail="No alerts provided")
        
        logger.info(f"🔍 Starting correlation for {len(alerts)} alerts")
        
        # Run the correlation agent
        result = await correlation_agent.run(alerts)
        
        logger.info(f"✅ Correlation completed: {result['metrics']['clusters_created']} clusters created")
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Alert correlation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Correlation failed: {str(e)}")

@router.post("/correlate-mock")
async def correlate_mock_alerts() -> Dict:
    """
    Correlate mock alerts for demonstration purposes
    """
    try:
        # Generate mock alerts
        mock_alerts = generate_mock_alerts()
        
        logger.info(f"🎭 Generated {len(mock_alerts)} mock alerts for correlation")
        
        # Run correlation
        result = await correlation_agent.run(mock_alerts)
        
        return {
            "success": True,
            "data": result,
            "mock_data": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Mock correlation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mock correlation failed: {str(e)}")

@router.get("/agent-info")
async def get_agent_info() -> Dict:
    """
    Get information about the Alert Correlation Agent
    """
    try:
        agent_info = correlation_agent.get_agent_info()
        
        return {
            "success": True,
            "agent": agent_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get agent info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent info: {str(e)}")

@router.post("/correlate-batch")
async def correlate_alerts_batch(
    client_ids: Optional[List[str]] = None,
    severity_filter: Optional[str] = None,
    time_window_hours: Optional[int] = 24
) -> Dict:
    """
    Correlate alerts in batch with optional filtering
    
    Args:
        client_ids: List of client IDs to filter alerts
        severity_filter: Filter by severity (critical, warning, info, low)
        time_window_hours: Time window for alert correlation (default: 24 hours)
    """
    try:
        # Generate mock alerts (in real implementation, this would query the database)
        all_alerts = generate_mock_alerts()
        
        # Apply filters
        filtered_alerts = all_alerts
        
        if client_ids:
            filtered_alerts = [alert for alert in filtered_alerts if alert.client_id in client_ids]
        
        if severity_filter:
            filtered_alerts = [alert for alert in filtered_alerts if alert.severity == severity_filter]
        
        # Apply time window filter
        if time_window_hours:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            filtered_alerts = [alert for alert in filtered_alerts if alert.timestamp >= cutoff_time]
        
        logger.info(f"🔍 Batch correlation: {len(filtered_alerts)} alerts after filtering")
        
        if not filtered_alerts:
            return {
                "success": True,
                "data": {
                    "clusters": [],
                    "summary": "No alerts found matching the criteria",
                    "metrics": {"total_alerts": 0, "clusters_created": 0}
                },
                "filters_applied": {
                    "client_ids": client_ids,
                    "severity_filter": severity_filter,
                    "time_window_hours": time_window_hours
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Run correlation
        result = await correlation_agent.run(filtered_alerts)
        
        return {
            "success": True,
            "data": result,
            "filters_applied": {
                "client_ids": client_ids,
                "severity_filter": severity_filter,
                "time_window_hours": time_window_hours
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Batch correlation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch correlation failed: {str(e)}")

@router.get("/correlation-stats")
async def get_correlation_stats() -> Dict:
    """
    Get correlation statistics and performance metrics
    """
    try:
        # Generate some mock data for demonstration
        mock_alerts = generate_mock_alerts()
        result = await correlation_agent.run(mock_alerts)
        
        stats = {
            "agent_info": correlation_agent.get_agent_info(),
            "last_correlation": {
                "total_alerts": result["metrics"]["total_alerts"],
                "clusters_created": result["metrics"]["clusters_created"],
                "reduction_ratio": result["metrics"]["reduction_ratio"],
                "effectiveness": result["metrics"]["correlation_effectiveness"]
            },
            "capabilities": {
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "clustering_algorithm": "cosine_similarity",
                "llm_reasoning": correlation_agent.use_llm,
                "time_window_correlation": True,
                "severity_assessment": True
            },
            "performance": {
                "average_processing_time": "~2-5 seconds for 100 alerts",
                "memory_usage": "~500MB for models",
                "scalability": "Supports up to 1000 alerts per batch"
            }
        }
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get correlation stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get correlation stats: {str(e)}")
