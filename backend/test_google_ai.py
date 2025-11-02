#!/usr/bin/env python3
"""
Test script to verify Google AI API is working
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir / "settings.env")

async def test_google_ai():
    """Test Google AI API connection and basic functionality"""
    try:
        # Get API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        
        if not api_key:
            print("❌ ERROR: GOOGLE_AI_API_KEY not found in environment variables")
            print(f"   Checked: {backend_dir / '.env'} and {backend_dir / 'settings.env'}")
            return False
        
        print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
        
        # Configure Gemini
        print("\n🔧 Configuring Google Generative AI...")
        genai.configure(api_key=api_key)
        
        # List available models
        print("📋 Checking available models...")
        models = genai.list_models()
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        print(f"✓ Found {len(available_models)} available models:")
        for m in available_models[:5]:  # Show first 5
            print(f"   - {m}")
        
        # Try to find a suitable model (prefer stable versions)
        model_name = None
        model = None
        
        # Prefer stable models first
        preferred = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-flash', 'gemini-1.5-pro']
        for pref in preferred:
            matching = [m for m in available_models if pref in m and 'preview' not in m]
            if matching:
                model_name = matching[0]
                print(f"\n🧪 Testing with model: {model_name}")
                # Use just the model name without 'models/' prefix
                model = genai.GenerativeModel(model_name.replace('models/', ''))
                break
        
        # Fallback to any available model
        if not model and available_models:
            model_name = available_models[0]
            print(f"\n🧪 Using available model: {model_name}")
            model = genai.GenerativeModel(model_name.replace('models/', ''))
        
        if not model:
            print("❌ ERROR: No suitable models found")
            return False
        
        # Simple test prompt
        test_prompt = "Say 'Google AI API is working' if you can read this. Respond with just 'OK'."
        print(f"📤 Sending test prompt: {test_prompt}")
        
        response = await model.generate_content_async(test_prompt)
        
        if response and response.text:
            print(f"✅ SUCCESS! Google AI API is working!")
            print(f"📥 Response: {response.text.strip()}")
            return True
        else:
            print("❌ ERROR: No response received from Google AI")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Google AI API Connection Test")
    print("=" * 60)
    success = asyncio.run(test_google_ai())
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)

