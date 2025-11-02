#!/usr/bin/env python3
"""
Test script to verify backend APIs are working with Google AI
"""
import asyncio
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir / "settings.env")

async def test_backend_services():
    """Test that backend services can initialize with Google AI"""
    print("=" * 60)
    print("Backend Services Google AI Integration Test")
    print("=" * 60)
    
    try:
        # Test 1: Verify API key is loaded
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            print("❌ ERROR: GOOGLE_AI_API_KEY not found")
            return False
        print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
        
        # Test 2: Verify model works
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = await model.generate_content_async("Test")
        print("✓ Gemini 2.5 Flash model is working")
        
        # Test 3: Test CascadePredictionAgent
        print("\n🧪 Testing CascadePredictionAgent...")
        sys.path.insert(0, str(backend_dir))
        from app.services.cascade_prediction_agent import CascadePredictionAgent
        agent = CascadePredictionAgent(api_key=api_key)
        print("✓ CascadePredictionAgent initialized successfully")
        
        # Test 4: Test EnhancedCascadePredictionAgent
        print("\n🧪 Testing EnhancedCascadePredictionAgent...")
        from app.services.enhanced_cascade_prediction_agent import EnhancedCascadePredictionAgent
        enhanced_agent = EnhancedCascadePredictionAgent(api_key=api_key)
        print("✓ EnhancedCascadePredictionAgent initialized successfully")
        
        # Test 5: Test AgenticAIService
        print("\n🧪 Testing AgenticAIService...")
        from app.services.agentic_ai_services import AgenticAIService
        ai_service = AgenticAIService(api_key=api_key)
        print("✓ AgenticAIService initialized successfully")
        
        # Test 6: Test AutonomousDecisionAgent
        print("\n🧪 Testing AutonomousDecisionAgent...")
        from app.services.autonomous_decision_agent import AutonomousDecisionAgent
        decision_agent = AutonomousDecisionAgent(api_key=api_key)
        print("✓ AutonomousDecisionAgent initialized successfully")
        
        # Test 7: Test ITAdministrativeAgent
        print("\n🧪 Testing ITAdministrativeAgent...")
        from app.services.it_administrative_agent import ITAdministrativeAgent
        admin_agent = ITAdministrativeAgent(api_key=api_key)
        print("✓ ITAdministrativeAgent initialized successfully")
        
        # Test 8: Test EnhancedPatchManagementAgent
        print("\n🧪 Testing EnhancedPatchManagementAgent...")
        from app.services.enhanced_patch_management_agent import EnhancedPatchManagementAgent
        patch_agent = EnhancedPatchManagementAgent(api_key=api_key)
        print("✓ EnhancedPatchManagementAgent initialized successfully")
        
        print("\n" + "=" * 60)
        print("✅ ALL BACKEND SERVICES ARE WORKING WITH GOOGLE AI!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend_services())
    sys.exit(0 if success else 1)

