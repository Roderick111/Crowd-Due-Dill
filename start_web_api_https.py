#!/usr/bin/env python3
"""
Crowdfunding Due Diligence AI Agent - HTTPS Web API Startup Script

Production HTTPS startup script for the crowdfunding regulatory guidance system.
"""

import subprocess
import sys
import os
import ssl

def start_api_https():
    """Start the web API server with HTTPS"""
    print("⚖️ Crowdfunding Due Diligence AI Agent - HTTPS Web API Startup")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists("src/web_api.py"):
        print("❌ Error: web_api.py not found in src/ directory")
        print("   Please run this script from the project root directory")
        return False
    
    # Check for SSL certificates
    cert_file = "ssl/server.crt"
    key_file = "ssl/server.key"
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("❌ Error: SSL certificates not found")
        print(f"   Expected: {cert_file} and {key_file}")
        print("   Please generate SSL certificates first")
        return False
    
    print("🚀 Starting HTTPS server...")
    print("📖 API Documentation: https://localhost:8001/docs")
    print("🔄 Health Check: https://localhost:8001/health")
    print("💬 Chat Interface: https://localhost:8001/chat")
    print("📊 System Status: https://localhost:8001/status")
    print("🔐 Auth Status: https://localhost:8001/auth/status")
    print("💳 Stripe Config: https://localhost:8001/stripe/config")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        # Start the HTTPS server
        subprocess.run([
            sys.executable, "-m", "uvicorn", "src.web_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--ssl-keyfile", key_file,
            "--ssl-certfile", cert_file,
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n⚖️ HTTPS server stopped by user")
    except Exception as e:
        print(f"❌ Error starting HTTPS server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_api_https() 