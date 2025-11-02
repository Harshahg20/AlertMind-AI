#!/usr/bin/env python3
"""Test server endpoints"""
import urllib.request
import json
import time

def test_endpoint(url, name):
    """Test an endpoint"""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"✅ {name}: Status {response.status}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

if __name__ == "__main__":
    print("Testing backend server endpoints...")
    print("=" * 60)
    
    # Wait for server to start
    print("Waiting for server to be ready...")
    max_retries = 10
    for i in range(max_retries):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2)
            print("✓ Server is ready!")
            break
        except:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                print("❌ Server not responding after 10 seconds")
                exit(1)
    
    print("\n" + "=" * 60)
    
    # Test endpoints
    endpoints = [
        ("http://127.0.0.1:8000/", "Root endpoint"),
        ("http://127.0.0.1:8000/health", "Health endpoint"),
        ("http://127.0.0.1:8000/api/alerts", "Alerts endpoint"),
    ]
    
    results = []
    for url, name in endpoints:
        results.append(test_endpoint(url, name))
        print()
    
    if all(results):
        print("=" * 60)
        print("✅ All endpoints working!")
    else:
        print("=" * 60)
        print("❌ Some endpoints failed")

