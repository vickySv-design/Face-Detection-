#!/usr/bin/env python3
"""
Startup script for Face Detection Birthday App
Runs both backend and opens frontend in browser
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def main():
    print("Starting Face Detection Birthday App")
    print("=" * 50)
    
    # Get the directory paths
    current_dir = Path(__file__).parent
    backend_dir = current_dir / "backend"
    frontend_file = current_dir / "frontend" / "index.html"
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print("Backend directory not found!")
        return False
    
    # Check if frontend file exists
    if not frontend_file.exists():
        print("Frontend file not found!")
        return False
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print("Starting backend server...")
    
    try:
        # Try port 8000 first, then 8001
        port = 8000
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
        except:
            port = 8001
            print(f"Port 8000 is in use, trying port {port}...")
        
        # Start the FastAPI server with live output
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", 
            "--port", str(port), 
            "--reload"
        ])
        
        print("Waiting for server to start...")
        time.sleep(3)  # Give server time to start
        
        # Check if server is running
        if server_process.poll() is None:
            print("Backend server started successfully!")
            print(f"Server running at: http://localhost:{port}")
            
            # Open frontend in browser
            print("Opening frontend in browser...")
            webbrowser.open(f"http://localhost:{port}")
            
            print("\n" + "=" * 50)
            print("App is ready! Live updates below:")
            print("=" * 50 + "\n")
            
            # Keep the script running
            try:
                server_process.wait()
            except KeyboardInterrupt:
                print("\n\nStopping server...")
                server_process.terminate()
                server_process.wait()
                print("Server stopped successfully!")
                
        else:
            print("Failed to start server!")
            return False
            
    except FileNotFoundError:
        print("uvicorn not found! Please install requirements:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)