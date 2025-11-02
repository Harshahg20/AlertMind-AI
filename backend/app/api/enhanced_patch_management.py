from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from app.api.alerts import MOCK_CLIENTS
from app.services.enhanced_patch_management_agent import EnhancedPatchManagementAgent

router = APIRouter()

# Initialize the enhanced patch management agent
patch_agent = EnhancedPatchManagementAgent()

@router.get("/cve-analysis/{client_id}")
async def analyze_cve_for_client(client_id: str, cve_id: str) -> Dict:
    """Analyze a specific CVE for a client using AI"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Mock CVE data - in real implementation, this would come from CVE database
    mock_cve_data = {
        "cve": cve_id,
        "severity": 8.5,
        "product": "database",
        "summary": "Critical vulnerability in database engine allowing remote code execution"
    }
    
    try:
        cve_analysis = await patch_agent.analyze_cve_with_ai(mock_cve_data, client)
        
        return {
            "client_id": client_id,
            "cve_analysis": {
                "cve_id": cve_analysis.cve_id,
                "severity": cve_analysis.severity,
                "product": cve_analysis.product,
                "summary": cve_analysis.summary,
                "client_impact": cve_analysis.client_impact,
                "patch_priority": cve_analysis.patch_priority,
                "estimated_effort": cve_analysis.estimated_effort,
                "risk_assessment": cve_analysis.risk_assessment,
                "ai_analysis": cve_analysis.ai_analysis
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CVE analysis failed: {str(e)}")

@router.post("/patch-plan/{client_id}")
async def generate_patch_plan(client_id: str, cve_list: List[Dict]) -> Dict:
    """Generate comprehensive patch plan for a client"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Normalize CVE data format
        normalized_cve_list = []
        for cve in cve_list:
            normalized_cve = {
                "cve": cve.get("cve_id") or cve.get("cve", "Unknown"),
                "cve_id": cve.get("cve_id") or cve.get("cve", "Unknown"),
                "severity": float(cve.get("severity", 0)),
                "product": cve.get("product", "Unknown"),
                "summary": cve.get("summary", "No description available")
            }
            normalized_cve_list.append(normalized_cve)
        
        patch_plan = await patch_agent.generate_patch_plan(client, normalized_cve_list)
        
        # Serialize maintenance windows properly
        serialized_windows = []
        for window in patch_plan.maintenance_windows:
            # Extract CVE IDs from patches
            cve_ids = []
            patches = window.get("patches", [])
            for patch in patches:
                if hasattr(patch, "cve_id"):
                    cve_ids.append(patch.cve_id)
                elif isinstance(patch, dict):
                    cve_ids.append(patch.get("cve_id", ""))
                else:
                    cve_ids.append(str(patch))
            
            scheduled_time = window.get("scheduled_time")
            if isinstance(scheduled_time, datetime):
                scheduled_time_str = scheduled_time.isoformat()
            elif scheduled_time:
                scheduled_time_str = str(scheduled_time)
            else:
                scheduled_time_str = datetime.now().isoformat()
            
            serialized_window = {
                "window_id": window.get("window_id", ""),
                "scheduled_time": scheduled_time_str,
                "estimated_duration": window.get("estimated_duration", 0),
                "risk_level": window.get("risk_level", "MEDIUM"),
                "cve_ids": cve_ids if cve_ids else [analysis.cve_id for analysis in patch_plan.cve_analyses],
                "rollback_plan": window.get("rollback_plan", {})
            }
            serialized_windows.append(serialized_window)
        
        return {
            "client_id": client_id,
            "patch_plan": {
                "plan_id": f"plan_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "client_name": client.name,
                "total_cves": len(patch_plan.cve_analyses),
                "cve_analyses": [
                    {
                        "cve_id": analysis.cve_id,
                        "severity": analysis.severity,
                        "product": analysis.product,
                        "client_impact": analysis.client_impact,
                        "patch_priority": analysis.patch_priority,
                        "estimated_effort": analysis.estimated_effort,
                        "risk_assessment": analysis.risk_assessment,
                        "ai_analysis": analysis.ai_analysis
                    } for analysis in patch_plan.cve_analyses
                ],
                "maintenance_windows": serialized_windows,
                "status": patch_plan.status.value,
                "created_at": patch_plan.created_at.isoformat()
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patch plan generation failed: {str(e)}")

@router.post("/optimize-maintenance/{client_id}")
async def optimize_maintenance_windows(client_id: str, patch_plan_data: Dict) -> Dict:
    """Optimize maintenance windows using AI"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Reconstruct patch plan from data
        from app.services.enhanced_patch_management_agent import PatchPlan, CVEAnalysis
        
        cve_analyses = []
        for cve_data in patch_plan_data.get("cve_analyses", []):
            analysis = CVEAnalysis(
                cve_id=cve_data["cve_id"],
                severity=cve_data["severity"],
                product=cve_data["product"],
                summary=cve_data.get("summary", ""),
                client_impact=cve_data["client_impact"],
                ai_analysis=cve_data.get("ai_analysis", {})
            )
            cve_analyses.append(analysis)
        
        patch_plan = PatchPlan(client, cve_analyses)
        patch_plan.maintenance_windows = patch_plan_data.get("maintenance_windows", [])
        
        optimization = await patch_agent.optimize_maintenance_windows(patch_plan)
        
        return {
            "client_id": client_id,
            "optimization": optimization,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Maintenance optimization failed: {str(e)}")

@router.post("/monitor-execution/{client_id}")
async def monitor_patch_execution(client_id: str, window_id: str) -> Dict:
    """Monitor patch execution in real-time"""
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        monitoring_data = await patch_agent.monitor_patch_execution(window_id, client)
        
        return {
            "client_id": client_id,
            "window_id": window_id,
            "monitoring_data": monitoring_data,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patch monitoring failed: {str(e)}")

@router.get("/performance-metrics")
async def get_patch_agent_metrics() -> Dict:
    """Get patch management agent performance metrics"""
    try:
        metrics = patch_agent.get_performance_metrics()
        return {
            "metrics": metrics,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/cve-database")
async def get_cve_database() -> Dict:
    """Get available CVE database (mock data for demo)"""
    # In real implementation, this would connect to actual CVE databases
    mock_cves = [
        {
            "cve": "CVE-2024-12345",
            "severity": 9.8,
            "product": "database",
            "summary": "Critical RCE in SQL engine",
            "published_date": "2024-01-15",
            "affected_versions": ["1.0.0", "1.1.0", "1.2.0"]
        },
        {
            "cve": "CVE-2025-10001",
            "severity": 8.6,
            "product": "web-app",
            "summary": "Auth bypass in session handling",
            "published_date": "2025-01-01",
            "affected_versions": ["2.0.0", "2.1.0"]
        },
        {
            "cve": "CVE-2024-56789",
            "severity": 7.5,
            "product": "api-gateway",
            "summary": "DoS via malformed headers",
            "published_date": "2024-03-20",
            "affected_versions": ["3.0.0", "3.1.0", "3.2.0"]
        },
        {
            "cve": "CVE-2023-98765",
            "severity": 6.4,
            "product": "storage-server",
            "summary": "Privilege escalation in driver",
            "published_date": "2023-12-10",
            "affected_versions": ["4.0.0", "4.1.0"]
        },
        {
            "cve": "CVE-2025-22222",
            "severity": 9.1,
            "product": "firewall",
            "summary": "Policy injection vulnerability",
            "published_date": "2025-01-10",
            "affected_versions": ["5.0.0", "5.1.0", "5.2.0"]
        }
    ]
    
    return {
        "cve_database": mock_cves,
        "total_cves": len(mock_cves),
        "last_updated": datetime.now().isoformat()
    }
