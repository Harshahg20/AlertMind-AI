from fastapi import APIRouter, HTTPException
from typing import List, Dict
from datetime import datetime, timedelta
import json
import random

from app.models.alert import Alert, Client, SeverityLevel, AlertCategory
from app.services.alert_correlation import AlertCorrelationEngine
from app.services.cascade_prediction import CascadePredictionEngine

router = APIRouter()

# Initialize services
correlation_engine = AlertCorrelationEngine()
prediction_engine = CascadePredictionEngine()

# Mock data - In real implementation, this would come from database
MOCK_CLIENTS = [
    Client(
        id="client_001",
        name="TechCorp Solutions",
        tier="Premium",
        environment="Windows Server + SQL + Exchange",
        business_hours="9AM-6PM EST",
        critical_systems=["email-server", "database", "web-app", "file-server"],
        system_dependencies={
            "database": ["web-app", "reporting-service", "api-gateway"],
            "email-server": ["file-server", "backup-system"],
            "web-app": ["database", "cache-server", "api-gateway"],
            "api-gateway": ["database", "auth-service"]
        }
    ),
    Client(
        id="client_002",
        name="FinanceFlow Inc",
        tier="Standard",
        environment="Linux + MySQL + Apache",
        business_hours="8AM-8PM PST",
        critical_systems=["trading-platform", "database", "backup-system", "market-feed"],
        system_dependencies={
            "trading-platform": ["database", "market-feed", "risk-engine"],
            "database": ["backup-system", "reporting", "analytics"],
            "market-feed": ["network-gateway", "data-processor"],
            "risk-engine": ["database", "compliance-service"]
        }
    ),
    Client(
        id="client_003",
        name="HealthTech Medical",
        tier="Enterprise",
        environment="Hybrid Cloud + EMR + DICOM",
        business_hours="24/7",
        critical_systems=["emr-system", "database", "imaging-server", "backup-system"],
        system_dependencies={
            "emr-system": ["database", "auth-service", "api-gateway"],
            "imaging-server": ["storage-server", "database", "viewer-app"],
            "database": ["backup-system", "replication-service"],
            "auth-service": ["ldap-server", "database"]
        }
    )
]

def generate_mock_alerts() -> List[Alert]:
    """Generate realistic mock alerts for demo"""
    alerts = []
    alert_templates = [
        {"system": "database", "message": "SQL Server CPU usage 87%", "category": "performance", "severity": "warning"},
        {"system": "web-app", "message": "Application response time > 15 seconds", "category": "performance", "severity": "critical"},
        {"system": "database", "message": "Connection pool exhausted", "category": "performance", "severity": "critical"},
        {"system": "email-server", "message": "Exchange service stopped unexpectedly", "category": "system", "severity": "critical"},
        {"system": "file-server", "message": "Disk space 95% full", "category": "storage", "severity": "warning"},
        {"system": "backup-system", "message": "Backup job failed - timeout", "category": "system", "severity": "warning"},
        {"system": "network-gateway", "message": "Packet loss 15% on WAN interface", "category": "network", "severity": "warning"},
        {"system": "firewall", "message": "High connection count detected", "category": "security", "severity": "info"},
        {"system": "web-app", "message": "Failed login attempts exceeded threshold", "category": "security", "severity": "warning"},
        {"system": "api-gateway", "message": "Rate limit exceeded for client requests", "category": "performance", "severity": "warning"},
        {"system": "cache-server", "message": "Redis memory usage 92%", "category": "performance", "severity": "warning"},
        {"system": "load-balancer", "message": "Backend server pool health degraded", "category": "system", "severity": "critical"},
        {"system": "storage-server", "message": "RAID array degraded - disk failure", "category": "storage", "severity": "critical"},
        {"system": "monitoring-agent", "message": "Agent heartbeat missed", "category": "system", "severity": "info"},
        {"system": "trading-platform", "message": "Market data feed latency spike", "category": "performance", "severity": "warning"}
    ]
    
    # Generate alerts for each client
    for client in MOCK_CLIENTS:
        client_alert_count = random.randint(8, 15)
        
        for i in range(client_alert_count):
            template = random.choice(alert_templates)
            
            # Ensure system exists in client's systems
            if template["system"] not in client.critical_systems and template["system"] not in ["monitoring-agent", "firewall", "load-balancer"]:
                template = random.choice([t for t in alert_templates if t["system"] in client.critical_systems])
            
            alert = Alert(
                id=f"alert_{client.id}_{i:03d}",
                client_id=client.id,
                client_name=client.name,
                system=template["system"],
                severity=SeverityLevel(template["severity"]),
                message=template["message"],
                category=AlertCategory(template["category"]),
                timestamp=datetime.now() - timedelta(minutes=random.randint(1, 120)),
                cascade_risk=random.uniform(0.2, 0.9) if template["severity"] in ["warning", "critical"] else 0.1
            )
            alerts.append(alert)
    
    return alerts

@router.get("/", response_model=List[Alert])
async def get_all_alerts():
    """Get all alerts across all clients"""
    try:
        alerts = generate_mock_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filtered", response_model=Dict)
async def get_filtered_alerts():
    """Get intelligently filtered alerts with noise reduction"""
    try:
        all_alerts = generate_mock_alerts()
        
        # Filter noise and correlate alerts
        critical_alerts, noise_alerts = correlation_engine.filter_noise_alerts(all_alerts)
        correlations = correlation_engine.correlate_alerts(critical_alerts)
        
        # Update alerts with correlation info
        correlation_map = {}
        for corr in correlations:
            correlation_map[corr.primary_alert_id] = {
                "related_alerts": corr.related_alert_ids,
                "correlation_type": corr.correlation_type,
                "confidence": corr.correlation_confidence
            }
        
        for alert in critical_alerts:
            if alert.id in correlation_map:
                alert.is_correlated = True
                alert.correlated_with = correlation_map[alert.id]["related_alerts"]
        
        # Generate summary
        summary = correlation_engine.generate_alert_summary(all_alerts, correlations)
        
        return {
            "summary": summary,
            "critical_alerts": critical_alerts,
            "noise_alerts": noise_alerts[:10],  # Show first 10 noise alerts for demo
            "correlations": correlations,
            "total_processing_time_ms": random.randint(150, 300)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/client/{client_id}", response_model=List[Alert])
async def get_client_alerts(client_id: str):
    """Get alerts for a specific client"""
    try:
        all_alerts = generate_mock_alerts()
        client_alerts = [alert for alert in all_alerts if alert.client_id == client_id]
        
        if not client_alerts:
            raise HTTPException(status_code=404, detail="No alerts found for this client")
        
        return client_alerts
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients", response_model=List[Client])
async def get_all_clients():
    """Get all client information"""
    try:
        return MOCK_CLIENTS
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_alert_statistics():
    """Get overall alert statistics and trends"""
    try:
        all_alerts = generate_mock_alerts()
        
        # Calculate statistics
        total_alerts = len(all_alerts)
        critical_count = len([a for a in all_alerts if a.severity == "critical"])
        warning_count = len([a for a in all_alerts if a.severity == "warning"])
        
        # Client breakdown
        client_stats = {}
        for client in MOCK_CLIENTS:
            client_alerts = [a for a in all_alerts if a.client_id == client.id]
            client_stats[client.name] = {
                "total_alerts": len(client_alerts),
                "critical_alerts": len([a for a in client_alerts if a.severity == "critical"]),
                "high_cascade_risk": len([a for a in client_alerts if a.cascade_risk > 0.7])
            }
        
        # Category breakdown
        category_stats = {}
        for alert in all_alerts:
            category_stats[alert.category] = category_stats.get(alert.category, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "critical_percentage": round((critical_count / total_alerts) * 100, 1) if total_alerts > 0 else 0,
            "client_breakdown": client_stats,
            "category_breakdown": category_stats,
            "average_cascade_risk": round(sum(a.cascade_risk for a in all_alerts) / len(all_alerts), 2) if all_alerts else 0,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))