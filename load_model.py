#!/usr/bin/env python3
"""
Quick script to load a specific model
"""

import requests
import sys

def load_model(model_name):
    """Load a specific model via API"""
    try:
        # First check what models are available
        print(f"Checking available models...")
        response = requests.get('http://localhost:8000/api/models')
        
        if response.status_code != 200:
            print("❌ Cannot connect to server. Make sure backend is running.")
            return False
            
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ Error getting models: {data.get('error', 'Unknown error')}")
            return False
            
        available_models = data.get('models', [])
        print(f"Available models: {available_models}")
        
        if not available_models:
            print("❌ No models found. Train a model first.")
            return False
            
        if model_name not in available_models:
            print(f"❌ Model '{model_name}' not found.")
            print(f"Available models: {', '.join(available_models)}")
            return False
            
        # Load the model
        print(f"Loading model '{model_name}'...")
        response = requests.post('http://localhost:8000/api/models/load', 
                               json={'model_name': model_name})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Model '{model_name}' loaded successfully!")
                return True
            else:
                print(f"❌ Failed to load model: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure backend is running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python load_model.py <model_name>")
        print("Example: python load_model.py demo")
        
        # Try to show available models
        try:
            response = requests.get('http://localhost:8000/api/models')
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('models'):
                    print(f"\nAvailable models: {', '.join(data['models'])}")
        except:
            pass
            
        return
    
    model_name = sys.argv[1]
    success = load_model(model_name)
    
    if success:
        print(f"\n🎉 Model '{model_name}' is now loaded and ready!")
        print("You can now:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Click 'Start Camera' to begin face detection")
    else:
        print(f"\n❌ Failed to load model '{model_name}'")

if __name__ == "__main__":
    main()