#!/usr/bin/env python3
"""
Role-Based Auth0 Implementation Test Script

Tests the new role-based premium subscription management system.
Validates Auth0 RBAC integration, role assignments, and API endpoints.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

from src.core.auth0_management import auth0_management
from src.core.stripe_service import stripe_service
from src.utils.logger import logger


class RoleImplementationTester:
    """Test suite for role-based Auth0 implementation"""
    
    def __init__(self):
        self.test_results = []
        self.test_user_id = "google-oauth2|103818136374558632914"  # Your test user
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
        
    async def test_auth0_configuration(self):
        """Test Auth0 Management API configuration"""
        print("\n🔧 Testing Auth0 Configuration...")
        
        # Test 1: Check if Auth0 Management is enabled
        enabled = auth0_management.enabled
        self.log_test(
            "Auth0 Management API Enabled",
            enabled,
            f"Management API enabled: {enabled}"
        )
        
        if not enabled:
            self.log_test(
                "Auth0 Configuration",
                False,
                "Auth0 Management API not configured - check environment variables"
            )
            return False
            
        # Test 2: Test token acquisition
        try:
            token = await auth0_management._get_access_token()
            self.log_test(
                "Auth0 Token Acquisition",
                bool(token),
                f"Token acquired: {len(token) if token else 0} characters"
            )
        except Exception as e:
            self.log_test(
                "Auth0 Token Acquisition",
                False,
                f"Token acquisition failed: {str(e)}"
            )
            return False
            
        # Test 3: Test Auth0 client creation
        try:
            client = await auth0_management._get_auth0_client()
            self.log_test(
                "Auth0 Client Creation",
                client is not None,
                f"Client created: {type(client).__name__}"
            )
        except Exception as e:
            self.log_test(
                "Auth0 Client Creation",
                False,
                f"Client creation failed: {str(e)}"
            )
            return False
            
        return True
        
    async def test_role_management(self):
        """Test role assignment and removal"""
        print("\n🎭 Testing Role Management...")
        
        # Test 1: Check role definitions
        roles = auth0_management.ROLES
        expected_roles = ['free', 'monthly', 'lifetime', 'admin']
        
        all_roles_defined = all(role in roles for role in expected_roles)
        self.log_test(
            "Role Definitions",
            all_roles_defined,
            f"Roles defined: {list(roles.keys())}"
        )
        
        # Test 2: Test role ID retrieval
        try:
            free_role_id = await auth0_management._get_role_id('free-user')
            self.log_test(
                "Role ID Retrieval",
                free_role_id is not None,
                f"Free user role ID: {free_role_id}"
            )
        except Exception as e:
            self.log_test(
                "Role ID Retrieval",
                False,
                f"Role ID retrieval failed: {str(e)}"
            )
            
        # Test 3: Test role assignment (monthly)
        try:
            success = await auth0_management.assign_premium_role(self.test_user_id, 'monthly')
            self.log_test(
                "Monthly Role Assignment",
                success,
                f"Monthly role assigned to {self.test_user_id}: {success}"
            )
        except Exception as e:
            self.log_test(
                "Monthly Role Assignment",
                False,
                f"Monthly role assignment failed: {str(e)}"
            )
            
        # Test 4: Test premium status retrieval
        try:
            status = await auth0_management.get_user_premium_status(self.test_user_id)
            is_premium = status.get('premium_status') == 'active'
            self.log_test(
                "Premium Status Check",
                is_premium,
                f"Premium status: {status.get('premium_status')}, Plan: {status.get('plan_type')}"
            )
        except Exception as e:
            self.log_test(
                "Premium Status Check",
                False,
                f"Premium status check failed: {str(e)}"
            )
            
        # Test 5: Test role change (lifetime)
        try:
            success = await auth0_management.assign_premium_role(self.test_user_id, 'lifetime')
            self.log_test(
                "Lifetime Role Assignment",
                success,
                f"Lifetime role assigned to {self.test_user_id}: {success}"
            )
        except Exception as e:
            self.log_test(
                "Lifetime Role Assignment",
                False,
                f"Lifetime role assignment failed: {str(e)}"
            )
            
        # Test 6: Test role removal (back to free)
        try:
            success = await auth0_management.remove_premium_role(self.test_user_id)
            self.log_test(
                "Role Removal",
                success,
                f"Premium role removed from {self.test_user_id}: {success}"
            )
        except Exception as e:
            self.log_test(
                "Role Removal",
                False,
                f"Role removal failed: {str(e)}"
            )
            
    async def test_permission_system(self):
        """Test permission retrieval and validation"""
        print("\n🔐 Testing Permission System...")
        
        # Test 1: Assign premium role for permission testing
        try:
            await auth0_management.assign_premium_role(self.test_user_id, 'monthly')
            
            # Test 2: Get user permissions
            permissions = await auth0_management.get_user_permissions(self.test_user_id)
            expected_permissions = ['read:basic-content', 'read:premium-content', 'manage:subscription']
            
            has_expected_permissions = all(perm in permissions for perm in expected_permissions)
            self.log_test(
                "User Permissions",
                has_expected_permissions,
                f"Permissions: {permissions}"
            )
            
        except Exception as e:
            self.log_test(
                "User Permissions",
                False,
                f"Permission retrieval failed: {str(e)}"
            )
            
    async def test_premium_user_listing(self):
        """Test premium user listing functionality"""
        print("\n📊 Testing Premium User Listing...")
        
        try:
            # Ensure test user has premium role
            await auth0_management.assign_premium_role(self.test_user_id, 'monthly')
            
            # Test premium user listing
            premium_users = await auth0_management.list_premium_users()
            
            # Check if our test user is in the list
            test_user_found = any(user['user_id'] == self.test_user_id for user in premium_users)
            
            self.log_test(
                "Premium User Listing",
                len(premium_users) > 0,
                f"Found {len(premium_users)} premium users"
            )
            
            self.log_test(
                "Test User in Premium List",
                test_user_found,
                f"Test user found in premium list: {test_user_found}"
            )
            
        except Exception as e:
            self.log_test(
                "Premium User Listing",
                False,
                f"Premium user listing failed: {str(e)}"
            )
            
    async def test_stripe_integration(self):
        """Test Stripe service integration with roles"""
        print("\n💳 Testing Stripe Integration...")
        
        # Test 1: Check Stripe service configuration
        stripe_enabled = stripe_service.enabled
        self.log_test(
            "Stripe Service Enabled",
            stripe_enabled,
            f"Stripe enabled: {stripe_enabled}"
        )
        
        if not stripe_enabled:
            return
            
        # Test 2: Test role assignment method
        try:
            success = await stripe_service._assign_premium_role(self.test_user_id, 'monthly')
            self.log_test(
                "Stripe Role Assignment",
                success,
                f"Stripe role assignment success: {success}"
            )
        except Exception as e:
            self.log_test(
                "Stripe Role Assignment",
                False,
                f"Stripe role assignment failed: {str(e)}"
            )
            
        # Test 3: Test role removal method
        try:
            success = await stripe_service._remove_premium_role(self.test_user_id)
            self.log_test(
                "Stripe Role Removal",
                success,
                f"Stripe role removal success: {success}"
            )
        except Exception as e:
            self.log_test(
                "Stripe Role Removal",
                False,
                f"Stripe role removal failed: {str(e)}"
            )
            
    def test_environment_configuration(self):
        """Test environment variable configuration"""
        print("\n🌍 Testing Environment Configuration...")
        
        required_vars = [
            'AUTH0_DOMAIN',
            'AUTH0_AUDIENCE',
            'AUTH0_MANAGEMENT_CLIENT_ID',
            'AUTH0_MANAGEMENT_CLIENT_SECRET'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            self.log_test(
                f"Environment Variable: {var}",
                bool(value),
                f"{var}: {'✓ Set' if value else '✗ Missing'}"
            )
            
    async def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting Role-Based Auth0 Implementation Tests")
        print("=" * 60)
        
        # Run all test suites
        self.test_environment_configuration()
        
        if await self.test_auth0_configuration():
            await self.test_role_management()
            await self.test_permission_system()
            await self.test_premium_user_listing()
            await self.test_stripe_integration()
        
        # Generate summary report
        self.generate_report()
        
    def generate_report(self):
        """Generate test summary report"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 NEXT STEPS:")
        if failed_tests == 0:
            print("✅ All tests passed! Your role-based implementation is ready.")
            print("✅ You can now deploy to production.")
        else:
            print("❌ Some tests failed. Please fix the issues before deployment.")
            print("❌ Check the failed tests above and verify your configuration.")
            
        print("\n📚 For detailed setup instructions, see: PREMIUM_DEPLOYMENT_GUIDE.md")


async def main():
    """Main test execution"""
    tester = RoleImplementationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 