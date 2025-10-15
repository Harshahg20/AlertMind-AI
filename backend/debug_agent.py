#!/usr/bin/env python3
"""
Debug script to test the Cascade Prediction Agent
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append('/Users/harshahg/superhack2025/backend')

from app.services.cascade_prediction_agent import create_cascade_prediction_agent
from app.api.alerts import generate_mock_alerts, MOCK_CLIENTS

async def debug_agent():
    """Debug the agent to see what's happening"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Create agent
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        print(f"API Key: {api_key[:10]}..." if api_key else "No API key")
        
        agent = create_cascade_prediction_agent(api_key=api_key)
        print(f"Agent created, LLM available: {agent.llm is not None}")
        
        # Get test data
        alerts = generate_mock_alerts()
        client = MOCK_CLIENTS[0]
        test_alerts = [a for a in alerts if a.client_id == client.id and a.severity in ["critical", "warning"]][:3]
        
        print(f"Testing with {len(test_alerts)} alerts from {client.name}")
        for alert in test_alerts:
            print(f"  - {alert.system}: {alert.severity} - {alert.message[:50]}...")
        
        # Prepare test data
        correlated_data = {
            'alerts': [{'id': a.id, 'client_id': a.client_id, 'client_name': a.client_name, 
                       'system': a.system, 'severity': a.severity, 'message': a.message, 
                       'category': a.category, 'timestamp': a.timestamp.isoformat(), 
                       'cascade_risk': a.cascade_risk, 'is_correlated': a.is_correlated} for a in test_alerts],
            'client': client,
            'historical_data': []
        }
        
        print("\nRunning agent...")
        result = await agent.run(correlated_data)
        
        print(f"\nAgent result:")
        print(f"  - Predicted in: {result.get('predicted_in')} minutes")
        print(f"  - Confidence: {result.get('confidence')}")
        print(f"  - Urgency: {result.get('urgency_level')}")
        print(f"  - Fallback mode: {result.get('explanation', {}).get('fallback_mode', False)}")
        print(f"  - Summary: {result.get('summary', '')[:100]}...")
        
        if result.get('llm_reasoning'):
            print(f"  - LLM reasoning available: True")
        else:
            print(f"  - LLM reasoning available: False")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent())
