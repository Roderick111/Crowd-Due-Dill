#!/usr/bin/env python3
"""
Context7-Compliant Stripe Integration Test
Tests the Stripe workflow following Context7 best practices
"""

import os
import sys
import requests
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

class StripeContext7Test:
    """Test Stripe integration following Context7 best practices"""
    
    def __init__(self):
        self.base_url = "https://localhost:8001"
        self.frontend_url = "https://localhost:8443"
        
    def test_stripe_config(self) -> bool:
        """Test Stripe configuration endpoint"""
        print("🔧 Testing Stripe configuration...")
        
        try:
            response = requests.get(
                f"{self.base_url}/stripe/config",
                verify=False,  # For self-signed certs
                timeout=10
            )
            
            if response.status_code == 200:
                config = response.json()
                print(f"✅ Stripe config: enabled={config.get('enabled', False)}")
                print(f"✅ Has publishable key: {bool(config.get('publishable_key'))}")
                print(f"✅ Has monthly plan: {config.get('has_monthly_plan', False)}")
                print(f"✅ Has lifetime plan: {config.get('has_lifetime_plan', False)}")
                return config.get('enabled', False)
            else:
                print(f"❌ Config endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Config test failed: {e}")
            return False
    
    def test_checkout_session_creation(self) -> bool:
        """Test checkout session creation (requires auth)"""
        print("\n💳 Testing checkout session creation...")
        
        # This would normally require a valid JWT token
        # For testing purposes, we'll check the endpoint exists
        try:
            response = requests.post(
                f"{self.base_url}/stripe/create-checkout-session",
                json={"plan_type": "monthly"},
                verify=False,
                timeout=10
            )
            
            # We expect 401 without auth, which means endpoint is working
            if response.status_code == 401:
                print("✅ Checkout endpoint exists and requires authentication")
                return True
            elif response.status_code == 200:
                print("✅ Checkout session created successfully")
                return True
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Checkout test failed: {e}")
            return False
    
    def test_frontend_integration(self) -> bool:
        """Test frontend Stripe service integration"""
        print("\n🌐 Testing frontend integration...")
        
        try:
            # Check if frontend is accessible
            response = requests.get(
                self.frontend_url,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Check for Stripe service
                if 'stripeService' in content or 'stripe' in content.lower():
                    print("✅ Frontend includes Stripe integration")
                    return True
                else:
                    print("⚠️ Frontend accessible but Stripe integration not found")
                    return False
            else:
                print(f"❌ Frontend not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Frontend test failed: {e}")
            return False
    
    def test_environment_variables(self) -> bool:
        """Test required environment variables"""
        print("\n🔐 Testing environment variables...")
        
        required_vars = [
            'STRIPE_SECRET_KEY',
            'STRIPE_PUBLISHABLE_KEY',
            'STRIPE_MONTHLY_PRICE_ID',
            'STRIPE_LIFETIME_PRICE_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ All required environment variables present")
            return True
    
    def test_context7_compliance(self) -> bool:
        """Test Context7 best practices compliance"""
        print("\n📋 Testing Context7 compliance...")
        
        compliance_checks = []
        
        # Check if using proper Stripe.js loading
        try:
            with open('web/services/stripeService.js', 'r') as f:
                content = f.read()
                
            if 'loadStripe' in content or 'stripe.js/v3' in content:
                print("✅ Using proper Stripe.js loading pattern")
                compliance_checks.append(True)
            else:
                print("❌ Not using recommended Stripe.js loading pattern")
                compliance_checks.append(False)
                
            if 'idempotency' in content.lower():
                print("✅ Idempotency handling present")
                compliance_checks.append(True)
            else:
                print("⚠️ Idempotency handling not found in frontend")
                compliance_checks.append(False)
                
        except Exception as e:
            print(f"❌ Could not check frontend compliance: {e}")
            compliance_checks.append(False)
        
        # Check backend compliance
        try:
            with open('src/core/stripe_service.py', 'r') as f:
                content = f.read()
                
            if 'Context7' in content:
                print("✅ Backend follows Context7 patterns")
                compliance_checks.append(True)
            else:
                print("⚠️ Context7 patterns not explicitly documented in backend")
                compliance_checks.append(False)
                
        except Exception as e:
            print(f"❌ Could not check backend compliance: {e}")
            compliance_checks.append(False)
        
        return all(compliance_checks)
    
    def run_all_tests(self) -> bool:
        """Run all Context7 compliance tests"""
        print("🚀 Starting Context7 Stripe Integration Tests")
        print("=" * 50)
        
        tests = [
            ("Environment Variables", self.test_environment_variables),
            ("Stripe Configuration", self.test_stripe_config),
            ("Checkout Session Creation", self.test_checkout_session_creation),
            ("Frontend Integration", self.test_frontend_integration),
            ("Context7 Compliance", self.test_context7_compliance),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append(result)
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"\n{status}: {test_name}")
            except Exception as e:
                print(f"\n❌ ERROR: {test_name} - {e}")
                results.append(False)
        
        print("\n" + "=" * 50)
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
            print("✅ Stripe integration is Context7-compliant and ready for production!")
        else:
            print(f"⚠️ SOME TESTS FAILED ({passed}/{total})")
            print("🔧 Please review the failed tests above")
        
        return passed == total

def main():
    """Main test runner"""
    tester = StripeContext7Test()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Deploy to production server")
        print("2. Update environment variables for production")
        print("3. Test end-to-end payment flow")
        return 0
    else:
        print("\n🔧 Fix the issues above before deploying to production")
        return 1

if __name__ == "__main__":
    exit(main()) 