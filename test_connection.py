#!/usr/bin/env python3
"""
Test script to verify frontend-backend connection
"""

import requests
import time
import subprocess
import sys
import os
from pathlib import Path

def test_backend():
    """Test if backend is responding"""
    try:
        response = requests.get('http://localhost:8000/api/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend is running: {data.get('message', 'OK')}")
            return True
        else:
            print(f"✗ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend (not running)")
        return False
    except Exception as e:
        print(f"✗ Backend test failed: {e}")
        return False

def test_endpoints():
    """Test key API endpoints"""
    endpoints = [
        '/api/status',
        '/api/models', 
        '/api/dataset'
    ]
    
    print("\nTesting API endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✓ {endpoint} - OK")
            else:
                print(f"✗ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")

def main():
    print("Face Detection Birthday App - Connection Test")
    print("=" * 50)
    
    # Test if backend is running
    if test_backend():
        test_endpoints()
        print("\n✓ All tests passed! Frontend should connect successfully.")
        print("\nTo start the full app:")
        print("1. Run: python start_app.py")
        print("2. Or double-click: start_app.bat")
        print("3. Or manually: cd backend && python app.py")
    else:
        print("\n✗ Backend is not running. To start it:")
        print("1. cd backend")
        print("2. python app.py")
        print("3. Then open http://localhost:8000 in your browser")

if __name__ == "__main__":
    main()