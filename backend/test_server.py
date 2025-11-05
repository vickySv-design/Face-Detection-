#!/usr/bin/env python3
"""
Test script to verify the Face Detection Birthday App server functionality
"""

import requests
import json

def test_server():
    base_url = "http://localhost:8000"
    
    print("Testing Face Detection Birthday App Server...")
    print("=" * 50)
    
    # Test 1: Check server status
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Server Status:", status_data.get("message", "Unknown"))
            print(f"   Current Model: {status_data.get('current_model', 'None')}")
            print(f"   Birthday Person: {status_data.get('birthday_person', 'None')}")
        else:
            print("❌ Server status check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error checking server status: {e}")
        return False
    
    # Test 2: List available models
    try:
        response = requests.get(f"{base_url}/api/models")
        if response.status_code == 200:
            models_data = response.json()
            print(f"✅ Available Models: {models_data.get('models', [])}")
        else:
            print("❌ Failed to list models")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
    
    # Test 3: Check dataset
    try:
        response = requests.get(f"{base_url}/api/dataset")
        if response.status_code == 200:
            dataset_data = response.json()
            if dataset_data.get("success"):
                print(f"✅ Dataset People: {dataset_data.get('people', [])}")
            else:
                print(f"ℹ️  Dataset: {dataset_data.get('error', 'Empty')}")
        else:
            print("❌ Failed to check dataset")
    except Exception as e:
        print(f"❌ Error checking dataset: {e}")
    
    print("=" * 50)
    print("Server test completed!")
    return True

if __name__ == "__main__":
    test_server()