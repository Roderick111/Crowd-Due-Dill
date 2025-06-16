#!/usr/bin/env python3
"""
Stripe Integration Tests

Proper integration tests for Stripe payment functionality.
"""

import os
import pytest
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestStripeIntegration:
    """Integration tests for Stripe payment system."""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.required_env_vars = [
            'STRIPE_SECRET_KEY',
            'STRIPE_PUBLISHABLE_KEY', 
            'STRIPE_MONTHLY_PRICE_ID',
            'STRIPE_LIFETIME_PRICE_ID'
        ]
        
        self.optional_env_vars = [
            'STRIPE_WEBHOOK_SECRET'
        ]
    
    def test_environment_variables(self):
        """Test that required environment variables are set."""
        missing_vars = []
        
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        assert not missing_vars, f"Missing required environment variables: {missing_vars}"
    
    def test_stripe_config_endpoint(self):
        """Test Stripe configuration endpoint."""
        try:
            response = requests.get(f'{self.BASE_URL}/stripe/config')
            response.raise_for_status()
            
            config = response.json()
            
            # Verify config structure
            assert 'enabled' in config
            assert 'has_monthly_plan' in config
            assert 'has_lifetime_plan' in config
            
            # If environment is properly configured, Stripe should be enabled
            if all(os.getenv(var) for var in self.required_env_vars):
                assert config['enabled'] is True
                assert config['has_monthly_plan'] is True
                assert config['has_lifetime_plan'] is True
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running. Start with: python start_web_api.py")
    
    def test_stripe_config_security(self):
        """Test that sensitive data is not exposed in config endpoint."""
        try:
            response = requests.get(f'{self.BASE_URL}/stripe/config')
            response.raise_for_status()
            
            config = response.json()
            config_str = json.dumps(config).lower()
            
            # Ensure no sensitive data is exposed
            sensitive_patterns = ['sk_', 'secret', 'key', 'webhook']
            for pattern in sensitive_patterns:
                assert pattern not in config_str, f"Sensitive data '{pattern}' found in config response"
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    @pytest.mark.skipif(not os.getenv('STRIPE_SECRET_KEY'), reason="Stripe not configured")
    def test_checkout_session_requires_auth(self):
        """Test that checkout session creation requires authentication."""
        try:
            response = requests.post(
                f'{self.BASE_URL}/stripe/create-checkout-session',
                json={'plan_type': 'monthly'}
            )
            
            # Should return 401 Unauthorized without proper auth
            assert response.status_code == 401
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


if __name__ == "__main__":
    # Allow running as standalone script for development
    import sys
    
    print("🚀 Stripe Integration Tests")
    print("=" * 40)
    
    # Check environment variables
    test_instance = TestStripeIntegration()
    test_instance.setup()
    
    try:
        test_instance.test_environment_variables()
        print("✅ Environment variables configured")
    except AssertionError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    try:
        test_instance.test_stripe_config_endpoint()
        print("✅ Stripe config endpoint working")
    except Exception as e:
        print(f"❌ Stripe config test failed: {e}")
    
    try:
        test_instance.test_stripe_config_security()
        print("✅ Config endpoint security verified")
    except Exception as e:
        print(f"❌ Security test failed: {e}")
    
    print("\n💡 Run full test suite with: pytest tests/integration/test_stripe_integration.py") 