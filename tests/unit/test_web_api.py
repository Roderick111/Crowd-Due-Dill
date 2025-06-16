#!/usr/bin/env python3
"""
Simple test script for the Esoteric AI Agent Web API
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_api():
    """Test the web API endpoints"""
    print("🧪 Testing Esoteric AI Agent Web API")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        print("1. Testing health check...")
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            health_data = response.json()
            print(f"   📊 Status: {health_data['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: System status
        print("\n2. Testing system status...")
        response = requests.get(f"{API_BASE}/status")
        if response.status_code == 200:
            print("   ✅ System status retrieved")
            status_data = response.json()
            print(f"   🎯 Active domains: {status_data['active_domains']}")
            print(f"   📚 Total documents: {status_data['total_documents']}")
        else:
            print(f"   ❌ System status failed: {response.status_code}")
        
        # Test 3: Chat functionality
        print("\n3. Testing chat functionality...")
        chat_request = {
            "message": "What is the current date?"
        }
        response = requests.post(f"{API_BASE}/chat", json=chat_request)
        if response.status_code == 200:
            print("   ✅ Chat response received")
            chat_data = response.json()
            print(f"   🤖 Response: {chat_data['response'][:100]}...")
            print(f"   🔧 Session ID: {chat_data['session_id'][:8]}...")
            print(f"   🧠 Message type: {chat_data['message_type']}")
            session_id = chat_data['session_id']
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
            return False
        
        # Test 4: Follow-up message with session
        print("\n4. Testing follow-up message...")
        chat_request = {
            "message": "What is the moon illumination percentage?",
            "session_id": session_id
        }
        response = requests.post(f"{API_BASE}/chat", json=chat_request)
        if response.status_code == 200:
            print("   ✅ Follow-up response received")
            chat_data = response.json()
            print(f"   🌙 Response: {chat_data['response'][:100]}...")
            print(f"   📊 RAG used: {chat_data['rag_used']}")
            print(f"   ⚡ Cache hit: {chat_data['cache_hit']}")
        else:
            print(f"   ❌ Follow-up failed: {response.status_code}")
        
        # Test 5: Lunar information
        print("\n5. Testing lunar endpoint...")
        response = requests.get(f"{API_BASE}/lunar")
        if response.status_code == 200:
            print("   ✅ Lunar information retrieved")
            lunar_data = response.json()
            print(f"   🌙 Summary: {lunar_data['summary'][:80]}...")
            print(f"   📅 Date: {lunar_data['details']['date']}")
            print(f"   🌕 Phase: {lunar_data['details']['phase']}")
            print(f"   💡 Illumination: {lunar_data['details']['illumination_percentage']}%")
        else:
            print(f"   ❌ Lunar info failed: {response.status_code}")
        
        # Test 6: Domains
        print("\n6. Testing domains endpoint...")
        response = requests.get(f"{API_BASE}/domains")
        if response.status_code == 200:
            print("   ✅ Domains retrieved")
            domains_data = response.json()
            print(f"   🎯 Active: {domains_data['active_domains']}")
            print(f"   📋 Available: {domains_data['available_domains']}")
        else:
            print(f"   ❌ Domains failed: {response.status_code}")
        
        # Test 7: Session history
        print("\n7. Testing session history...")
        response = requests.get(f"{API_BASE}/sessions/{session_id}/history")
        if response.status_code == 200:
            print("   ✅ Session history retrieved")
            history_data = response.json()
            print(f"   💬 Messages: {len(history_data['messages'])}")
        else:
            print(f"   ❌ Session history failed: {response.status_code}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📖 Access full API documentation at: http://localhost:8000/docs")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the API server is running:")
        print("   cd src && python web_api.py")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    test_api() 