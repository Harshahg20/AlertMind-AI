"""
Data Collection Service for Enhanced Cascade Prediction Agent
Collects comprehensive system data for better AI predictions
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class DataCollectionService:
    """
    Service for collecting comprehensive system data
    """
    
    def __init__(self):
        self.name = "data_collection_service"
        self.collection_interval = 30  # seconds
        self.last_collection = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass
    
    async def collect_comprehensive_data(self) -> Dict[str, Any]:
        """
        Collect comprehensive system data for enhanced analysis
        """
        try:
            start_time = datetime.now()
            
            # Simulate data collection from various sources
            system_metrics = await self._collect_system_metrics()
            service_health = await self._collect_service_health()
            external_factors = await self._collect_external_factors()
            trend_analysis = await self._collect_trend_analysis()
            
            collection_time = (datetime.now() - start_time).total_seconds() * 1000
            
            comprehensive_data = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": system_metrics,
                "service_health": service_health,
                "external_factors": external_factors,
                "trend_analysis": trend_analysis,
                "data_quality": {
                    "completeness": random.uniform(0.7, 0.95),
                    "freshness": "real_time",
                    "accuracy": random.uniform(0.8, 0.98)
                },
                "collection_metadata": {
                    "collection_time_ms": collection_time,
                    "sources_available": len([k for k, v in {
                        "system_metrics": system_metrics,
                        "service_health": service_health,
                        "external_factors": external_factors,
                        "trend_analysis": trend_analysis
                    }.items() if v]),
                    "last_update": datetime.now().isoformat(),
                    "fallback_mode": False
                }
            }
            
            self.last_collection = datetime.now()
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error collecting comprehensive data: {e}")
            return self._get_fallback_data()
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "cpu_percent": random.uniform(20, 90),
            "memory_percent": random.uniform(30, 85),
            "disk_usage": {
                "/": {"percent": random.uniform(40, 80), "free_gb": random.uniform(50, 200)},
                "/var": {"percent": random.uniform(30, 70), "free_gb": random.uniform(20, 100)}
            },
            "network_io": {
                "bytes_sent": random.randint(1000000, 10000000),
                "bytes_recv": random.randint(1000000, 10000000),
                "packets_sent": random.randint(1000, 10000),
                "packets_recv": random.randint(1000, 10000)
            },
            "load_average": [random.uniform(0.5, 3.0) for _ in range(3)],
            "process_count": random.randint(100, 500),
            "uptime_seconds": random.randint(86400, 2592000)  # 1 day to 30 days
        }
    
    async def _collect_service_health(self) -> Dict[str, Any]:
        """Collect service health status"""
        await asyncio.sleep(0.05)  # Simulate API call
        
        services = ["database", "web-app", "api-gateway", "cache-server", "message-queue"]
        service_health = {}
        
        for service in services:
            status = random.choice(["healthy", "degraded", "critical"])
            service_health[service] = {
                "status": status,
                "response_time_ms": random.uniform(10, 500),
                "error_rate": random.uniform(0, 0.1),
                "last_check": datetime.now().isoformat(),
                "dependencies": random.sample([s for s in services if s != service], random.randint(1, 3))
            }
        
        return service_health
    
    async def _collect_external_factors(self) -> Optional[Dict[str, Any]]:
        """Collect external factors that might affect system performance"""
        await asyncio.sleep(0.02)  # Simulate API call
        
        # Simulate external factors (network issues, third-party services, etc.)
        if random.random() < 0.3:  # 30% chance of external factors
            return {
                "network_latency": random.uniform(50, 200),
                "third_party_services": {
                    "payment_gateway": random.choice(["healthy", "degraded"]),
                    "email_service": random.choice(["healthy", "degraded"]),
                    "cdn": random.choice(["healthy", "degraded"])
                },
                "external_alerts": random.randint(0, 3),
                "weather_impact": random.choice([None, "severe_weather", "network_congestion"])
            }
        
        return None
    
    async def _collect_trend_analysis(self) -> Dict[str, Any]:
        """Collect trend analysis data"""
        await asyncio.sleep(0.03)  # Simulate API call
        
        return {
            "trends_available": True,
            "cpu_trend": random.choice(["increasing", "stable", "decreasing"]),
            "memory_trend": random.choice(["increasing", "stable", "decreasing"]),
            "error_rate_trend": random.choice(["increasing", "stable", "decreasing"]),
            "response_time_trend": random.choice(["increasing", "stable", "decreasing"]),
            "predicted_issues": [
                "Memory usage trending upward",
                "CPU spikes during peak hours",
                "Database connection pool exhaustion risk"
            ] if random.random() < 0.5 else [],
            "time_series_data": {
                "points": random.randint(50, 200),
                "time_range_hours": random.randint(1, 24),
                "resolution_minutes": random.choice([1, 5, 15, 60])
            }
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Get fallback data when collection fails"""
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