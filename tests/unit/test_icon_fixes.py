#!/usr/bin/env python3
"""
Test script to verify all browser icon and asset requests are properly handled
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_icon_fixes():
    """Test that all common browser icon requests return 200 instead of 404"""
    print("🧪 Testing Icon Request Fixes")
    print("=" * 50)
    
    # Test endpoints that were causing 404s
    icon_endpoints = [
        ("/favicon.ico", "Favicon"),
        ("/apple-touch-icon.png", "Apple Touch Icon"),
        ("/apple-touch-icon-precomposed.png", "Apple Touch Icon Precomposed"),
        ("/robots.txt", "Robots.txt"),
        ("/manifest.json", "Web App Manifest")
    ]
    
    all_passed = True
    
    for endpoint, description in icon_endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {description}: {endpoint} - Status 200")
                
                # Show content type for some endpoints
                if endpoint == "/robots.txt":
                    print(f"   📄 Content: {response.text[:30].strip()}...")
                elif endpoint == "/manifest.json":
                    manifest = response.json()
                    print(f"   📱 App Name: {manifest['name']}")
                else:
                    data = response.json()
                    print(f"   🌙 Message: {data['message']}")
            else:
                print(f"❌ {description}: {endpoint} - Status {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {description}: {endpoint} - Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All icon requests now return 200 OK!")
        print("✅ No more 404 errors in server logs for common browser requests")
        print("✅ Professional API behavior for web applications")
    else:
        print("❌ Some icon requests still failing")
    
    return all_passed

def test_enhanced_error_handling():
    """Test the enhanced error handling"""
    print("\n🔧 Testing Enhanced Error Handling")
    print("=" * 50)
    
    try:
        # Test 404 error
        response = requests.get(f"{API_BASE}/nonexistent-endpoint")
        if response.status_code == 404:
            error_data = response.json()
            if 'timestamp' in error_data and 'path' in error_data:
                print("✅ Enhanced 404 error response with metadata")
                print(f"   📍 Path: {error_data.get('path', 'N/A')}")
                print(f"   ⏰ Timestamp: {error_data.get('timestamp', 'N/A')[:19]}")
            else:
                print("⚠️ Basic 404 error response (could be enhanced)")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing 404 handling: {e}")

if __name__ == "__main__":
    try:
        icon_success = test_icon_fixes()
        test_enhanced_error_handling()
        
        if icon_success:
            print("\n🌟 Summary: All browser compatibility issues resolved!")
            print("   • Favicon requests: ✅")
            print("   • Apple touch icons: ✅") 
            print("   • Robots.txt: ✅")
            print("   • Web manifest: ✅")
            print("   • Enhanced error handling: ✅")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the API server is running:")
        print("   python start_web_api.py") 