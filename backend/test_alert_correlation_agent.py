#!/usr/bin/env python3
"""
Test script for the Alert Correlation Agent
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.alert import Alert, SeverityLevel, AlertCategory
from app.services.alert_correlation_agent import AlertCorrelationAgent

def create_test_alerts():
    """Create test alerts for correlation testing"""
    alerts = []
    
    # Create related alerts that should be clustered together
    base_time = datetime.now()
    
    # Database-related alerts (should cluster together)
    alerts.extend([
        Alert(
            id="alert_001",
            client_id="client_001",
            client_name="TechCorp Solutions",
            system="database",
            severity=SeverityLevel.CRITICAL,
            message="Database connection pool exhausted",
            category=AlertCategory.DATABASE,
            timestamp=base_time - timedelta(minutes=5),
            cascade_risk=0.9
        ),
        Alert(
            id="alert_002",
            client_id="client_001",
            client_name="TechCorp Solutions",
            system="database",
            severity=SeverityLevel.WARNING,
            message="High CPU usage on database server",
            category=AlertCategory.PERFORMANCE,
            timestamp=base_time - timedelta(minutes=3),
            cascade_risk=0.7
        ),
        Alert(
            id="alert_003",
            client_id="client_001",
            client_name="TechCorp Solutions",
            system="database",
            severity=SeverityLevel.CRITICAL,
            message="Database disk space critical - 95% full",
            category=AlertCategory.STORAGE,
            timestamp=base_time - timedelta(minutes=2),
            cascade_risk=0.8
        )
    ])
    
    # Web application alerts (should cluster together)
    alerts.extend([
        Alert(
            id="alert_004",
            client_id="client_001",
            client_name="TechCorp Solutions",
            system="web-app",
            severity=SeverityLevel.WARNING,
            message="Application response time degraded",
            category=AlertCategory.PERFORMANCE,
            timestamp=base_time - timedelta(minutes=4),
            cascade_risk=0.6
        ),
        Alert(
            id="alert_005",
            client_id="client_001",
            client_name="TechCorp Solutions",
            system="web-app",
            severity=SeverityLevel.CRITICAL,
            message="Application server memory usage 98%",
            category=AlertCategory.PERFORMANCE,
            timestamp=base_time - timedelta(minutes=1),
            cascade_risk=0.8
        )
    ])
    
    # Network-related alerts (should cluster together)
    alerts.extend([
        Alert(
            id="alert_006",
            client_id="client_002",
            client_name="FinanceFlow Inc",
            system="network-gateway",
            severity=SeverityLevel.WARNING,
            message="Network latency spike detected",
            category=AlertCategory.NETWORK,
            timestamp=base_time - timedelta(minutes=6),
            cascade_risk=0.5
        ),
        Alert(
            id="alert_007",
            client_id="client_002",
            client_name="FinanceFlow Inc",
            system="load-balancer",
            severity=SeverityLevel.WARNING,
            message="Backend server health check failures",
            category=AlertCategory.SYSTEM,
            timestamp=base_time - timedelta(minutes=5),
            cascade_risk=0.6
        )
    ])
    
    # Unrelated alerts (should remain separate)
    alerts.extend([
        Alert(
            id="alert_008",
            client_id="client_003",
            client_name="HealthTech Medical",
            system="email-server",
            severity=SeverityLevel.INFO,
            message="Scheduled maintenance completed",
            category=AlertCategory.SYSTEM,
            timestamp=base_time - timedelta(hours=2),
            cascade_risk=0.1
        ),
        Alert(
            id="alert_009",
            client_id="client_001",
            client_name="TechCorp Solutions",
            system="backup-system",
            severity=SeverityLevel.WARNING,
            message="Backup job failed - insufficient space",
            category=AlertCategory.STORAGE,
            timestamp=base_time - timedelta(hours=1),
            cascade_risk=0.4
        )
    ])
    
    return alerts

async def test_alert_correlation_agent():
    """Test the Alert Correlation Agent"""
    print("🚀 Testing Alert Correlation Agent")
    print("=" * 50)
    
    # Create test alerts
    test_alerts = create_test_alerts()
    print(f"📊 Created {len(test_alerts)} test alerts")
    
    # Initialize the agent
    print("\n🤖 Initializing Alert Correlation Agent...")
    agent = AlertCorrelationAgent(use_llm=False)  # Disable LLM for faster testing
    
    # Get agent info
    agent_info = agent.get_agent_info()
    print(f"✅ Agent initialized: {agent_info['name']} v{agent_info['version']}")
    print(f"📋 Capabilities: {', '.join(agent_info['capabilities'])}")
    print(f"🔧 Models loaded: {agent_info['models_loaded']}")
    
    # Run correlation
    print(f"\n🔍 Running correlation on {len(test_alerts)} alerts...")
    start_time = datetime.now()
    
    result = await agent.run(test_alerts)
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
    
    # Display results
    print(f"\n📈 CORRELATION RESULTS")
    print("=" * 50)
    
    metrics = result.get('metrics', {})
    print(f"Total alerts: {metrics.get('total_alerts', 0)}")
    print(f"Clusters created: {metrics.get('clusters_created', 0)}")
    print(f"Reduction ratio: {metrics.get('reduction_ratio', 0):.1%}")
    print(f"Effectiveness: {metrics.get('correlation_effectiveness', 'unknown')}")
    
    # Display clusters
    clusters = result.get('clusters', [])
    print(f"\n🎯 ALERT CLUSTERS ({len(clusters)} found)")
    print("=" * 50)
    
    for i, cluster in enumerate(clusters, 1):
        print(f"\nCluster {i}:")
        print(f"  ID: {cluster['cluster_id']}")
        print(f"  Severity: {cluster['severity']}")
        print(f"  Alert count: {cluster['alert_count']}")
        print(f"  Systems: {', '.join(cluster['systems'])}")
        print(f"  Categories: {', '.join(cluster['categories'])}")
        print(f"  Time span: {cluster['time_span_minutes']:.1f} minutes")
        print(f"  Similarity score: {cluster['similarity_score']:.3f}")
        
        print("  Alerts:")
        for alert in cluster['alerts']:
            print(f"    - {alert.id}: {alert.system} [{alert.severity}] - {alert.message[:60]}...")
    
    # Display summary
    summary = result.get('summary', 'No summary available')
    print(f"\n📝 SUMMARY")
    print("=" * 50)
    print(summary)
    
    print(f"\n✅ Test completed successfully!")
    return result

async def test_with_different_thresholds():
    """Test correlation with different similarity thresholds"""
    print("\n🔬 Testing with different similarity thresholds")
    print("=" * 50)
    
    test_alerts = create_test_alerts()
    agent = AlertCorrelationAgent(use_llm=False)
    
    thresholds = [0.6, 0.7, 0.8, 0.9]
    
    for threshold in thresholds:
        print(f"\n🎯 Testing with threshold: {threshold}")
        
        # Temporarily modify the threshold
        original_method = agent.simple_cluster
        def test_cluster(embeddings, alerts, th=threshold):
            return original_method(embeddings, alerts, th)
        agent.simple_cluster = test_cluster
        
        result = await agent.run(test_alerts)
        clusters = result.get('clusters', [])
        
        print(f"  Clusters: {len(clusters)}")
        print(f"  Reduction: {result['metrics']['reduction_ratio']:.1%}")
        
        # Restore original method
        agent.simple_cluster = original_method

if __name__ == "__main__":
    print("🧪 Alert Correlation Agent Test Suite")
    print("=" * 60)
    
    try:
        # Run main test
        asyncio.run(test_alert_correlation_agent())
        
        # Run threshold test
        asyncio.run(test_with_different_thresholds())
        
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
