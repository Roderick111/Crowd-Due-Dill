#!/usr/bin/env python3
"""
Quick test to verify Auth0 setup is working
"""

import os
import sys
sys.path.insert(0, 'src')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def test_config():
    """Test if Auth0 is configured correctly."""
    print("🔍 Testing Auth0 Configuration...")
    
    domain = os.getenv('AUTH0_DOMAIN')
    audience = os.getenv('AUTH0_AUDIENCE')
    
    if not domain:
        print("❌ AUTH0_DOMAIN not set in .env file")
        return False
    
    if not audience:
        print("❌ AUTH0_AUDIENCE not set in .env file")
        return False
    
    print(f"✅ AUTH0_DOMAIN: {domain}")
    print(f"✅ AUTH0_AUDIENCE: {audience}")
    
    # Test if domain looks right
    if not domain.endswith('.auth0.com'):
        print(f"⚠️  Warning: Domain should end with '.auth0.com'")
    
    # Test if audience looks right  
    if not audience.startswith('http'):
        print(f"⚠️  Warning: Audience should be a URL (your API identifier)")
    
    return True

def test_imports():
    """Test if Auth0 components work."""
    print("\n🧪 Testing Auth0 Integration...")
    
    try:
        from src.core.auth0_middleware import is_auth0_enabled, get_auth0_status
        
        enabled = is_auth0_enabled()
        status = get_auth0_status()
        
        print(f"🔐 Auth0 Enabled: {enabled}")
        
        if enabled:
            print("🎉 Auth0 is ready to use!")
        else:
            print("❌ Auth0 is not enabled - check your .env file")
            
        return enabled
        
    except Exception as e:
        print(f"❌ Error testing Auth0: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Auth0 Setup Test")
    print("=" * 30)
    
    config_ok = test_config()
    if config_ok:
        integration_ok = test_imports()
        
        if integration_ok:
            print("\n🎉 SUCCESS! Auth0 is configured and working!")
            print("\n🚀 Next steps:")
            print("1. Start your API: python src/web_api.py")
            print("2. Test: curl http://localhost:8000/auth/status")
        else:
            print("\n❌ Auth0 configuration needs fixing")
    else:
        print("\n❌ Please set AUTH0_DOMAIN and AUTH0_AUDIENCE in your .env file") 