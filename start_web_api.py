#!/usr/bin/env python3
"""
Crowdfunding Due Diligence AI Agent - Web API Startup Script

Development startup script for the crowdfunding regulatory guidance system.
"""

import subprocess
import sys
import os

print("⚖️ Crowdfunding Due Diligence AI Agent - Web API Startup")
print("=" * 60)
print("🚀 Starting development server...")
print("📖 API Documentation: http://localhost:8000/docs")
print("🔄 Health Check: http://localhost:8000/health")
print("💬 Chat Interface: http://localhost:8000/chat")
print("📊 System Status: http://localhost:8000/status")
print("🔐 Auth Status: http://localhost:8000/auth/status")
print("💳 Stripe Config: http://localhost:8000/stripe/config")
print("=" * 60)

try:
    # Run the FastAPI server with uvicorn
    result = subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "src.web_api:app",
        "--host", "0.0.0.0",
        "--port", "8000", 
        "--reload"
    ], check=True)
except KeyboardInterrupt:
    print("\n⚖️ Shutting down Crowdfunding Due Diligence AI Agent...")
except subprocess.CalledProcessError as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1) 