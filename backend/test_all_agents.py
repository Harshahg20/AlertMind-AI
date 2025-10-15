import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Base URL for the API
BASE_URL = "http://localhost:8000"

async def test_alert_correlation_agent():
    """Test the Alert Correlation Agent"""
    print("🔍 Testing Alert Correlation Agent...")
    
    async with httpx.AsyncClient() as client:
        # Test agent info
        response = await client.get(f"{BASE_URL}/api/alert-correlation/agent-info")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Alert Correlation Agent Info: {data['agent']['name']} v{data['agent']['version']}")
        
        # Test mock correlation
        response = await client.post(f"{BASE_URL}/api/alert-correlation/correlate-mock")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Mock Correlation: {len(data['data']['clusters'])} clusters generated")
        
        # Test correlation stats
        response = await client.get(f"{BASE_URL}/api/alert-correlation/correlation-stats")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Correlation Stats: {data['stats']['total_alerts_processed']} alerts processed")

async def test_autonomous_decision_agent():
    """Test the Autonomous Decision Agent"""
    print("\n🤖 Testing Autonomous Decision Agent...")
    
    async with httpx.AsyncClient() as client:
        # Test agent info
        response = await client.get(f"{BASE_URL}/api/autonomous-decision/agent-info")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Autonomous Decision Agent Info: {data['agent']['name']} v{data['agent']['version']}")
        
        # Test decision simulation
        scenario = {
            "alert": {
                "system": "database",
                "severity": "critical",
                "message": "Database connection pool exhausted",
                "cascade_risk": 0.8
            },
            "client": {
                "tier": "enterprise",
                "business_hours": True
            },
            "context": {
                "current_load": 85.0,
                "related_alerts_count": 3
            }
        }
        
        response = await client.post(f"{BASE_URL}/api/autonomous-decision/simulate-decision", json=scenario)
        response.raise_for_status()
        data = response.json()
        decision = data['decision']
        print(f"✅ Decision Simulation: {decision['decision_type']} (confidence: {decision['confidence']:.2f})")
        print(f"   Reasoning: {decision['reasoning'][:100]}...")
        
        # Test batch decisions
        response = await client.post(f"{BASE_URL}/api/autonomous-decision/decide-batch?max_decisions=3")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Batch Decisions: {len(data['decisions'])} decisions made")
        
        # Test decision stats
        response = await client.get(f"{BASE_URL}/api/autonomous-decision/decision-stats")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Decision Stats: {data['stats']['performance_metrics']['total_decisions_processed']} decisions processed")

async def test_prevention_execution_agent():
    """Test the Prevention Execution Agent"""
    print("\n⚡ Testing Prevention Execution Agent...")
    
    async with httpx.AsyncClient() as client:
        # Test agent info
        response = await client.get(f"{BASE_URL}/api/prevention-execution/agent-info")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Prevention Execution Agent Info: {data['agent']['name']} v{data['agent']['version']}")
        
        # Test execution simulation
        scenario = {
            "alert": {
                "system": "database",
                "severity": "critical",
                "cascade_risk": 0.8
            },
            "client": {
                "tier": "enterprise"
            },
            "actions": [
                "Scale database resources",
                "Restart database service",
                "Notify team members"
            ]
        }
        
        response = await client.post(f"{BASE_URL}/api/prevention-execution/simulate-execution", json=scenario)
        response.raise_for_status()
        data = response.json()
        result = data['execution_result']
        print(f"✅ Execution Simulation: {result['status']}")
        if 'report' in result:
            report = result['report']
            print(f"   Actions: {report['execution_summary']['total_actions']}, Success Rate: {report['execution_summary']['success_rate']:.1%}")
        
        # Test batch execution
        response = await client.post(f"{BASE_URL}/api/prevention-execution/execute-batch?max_executions=2&auto_approve=true")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Batch Execution: {data['summary']['total_executions']} executions, {data['summary']['successful_executions']} successful")
        
        # Test execution stats
        response = await client.get(f"{BASE_URL}/api/prevention-execution/execution-stats")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Execution Stats: {len(data['stats']['supported_actions'])} supported action types")

async def test_integrated_workflow():
    """Test integrated workflow across all agents"""
    print("\n🔄 Testing Integrated Workflow...")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Get alerts
        response = await client.get(f"{BASE_URL}/api/alerts/")
        response.raise_for_status()
        alerts_data = response.json()
        print(f"✅ Step 1: Retrieved {len(alerts_data)} alerts")
        
        # Step 2: Correlate alerts
        response = await client.post(f"{BASE_URL}/api/alert-correlation/correlate-mock")
        response.raise_for_status()
        correlation_data = response.json()
        clusters = correlation_data['data']['clusters']
        print(f"✅ Step 2: Generated {len(clusters)} alert clusters")
        
        # Step 3: Make decisions for top cluster
        if clusters:
            top_cluster = clusters[0]
            alert_id = top_cluster['alerts'][0]['id']
            client_id = top_cluster['alerts'][0]['client_id']
            
            response = await client.post(f"{BASE_URL}/api/autonomous-decision/decide", 
                                       params={"alert_id": alert_id, "client_id": client_id})
            response.raise_for_status()
            decision_data = response.json()
            decision = decision_data['decision']
            print(f"✅ Step 3: Decision made - {decision['decision_type']} (priority: {decision['priority']})")
            
            # Step 4: Execute prevention if needed
            if decision['decision_type'] in ['prevent', 'escalate']:
                recommended_actions = decision['recommended_actions']
                response = await client.post(f"{BASE_URL}/api/prevention-execution/execute",
                                           params={
                                               "alert_id": alert_id,
                                               "client_id": client_id,
                                               "recommended_actions": recommended_actions,
                                               "auto_approve": True
                                           })
                response.raise_for_status()
                execution_data = response.json()
                result = execution_data['result']
                print(f"✅ Step 4: Execution {result['status']}")
                
                if result['status'] == 'completed' and 'report' in result:
                    report = result['report']
                    print(f"   Execution Report: {report['execution_summary']['success_rate']:.1%} success rate")
        
        print("✅ Integrated workflow completed successfully!")

async def test_api_health():
    """Test overall API health"""
    print("\n🏥 Testing API Health...")
    
    async with httpx.AsyncClient() as client:
        # Test main API
        response = await client.get(f"{BASE_URL}/")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Main API: {data['message']}")
        print(f"   Features: {len(data['features'])} capabilities")
        print(f"   Agents: {len(data['agentic_capabilities'])} agentic capabilities")
        
        # Test health endpoint
        response = await client.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health Check: {data['status']} - {data['service']} v{data['version']}")

async def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Agent Testing...")
    print("=" * 60)
    
    try:
        await test_api_health()
        await test_alert_correlation_agent()
        await test_autonomous_decision_agent()
        await test_prevention_execution_agent()
        await test_integrated_workflow()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("\n📊 Summary:")
        print("✅ Alert Correlation Agent - Sentence Transformers + Fallback")
        print("✅ Autonomous Decision Agent - Gemini 1.5 Pro + Deterministic Scorer")
        print("✅ Prevention Execution Agent - Deterministic Orchestration + Tiny LLM")
        print("✅ Integrated Workflow - End-to-end agent collaboration")
        print("✅ API Health - All endpoints operational")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

