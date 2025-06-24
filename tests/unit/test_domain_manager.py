#!/usr/bin/env python3
"""
Unit tests for Minimal Domain Manager Stub.

Tests that the domain manager stub maintains API compatibility
while eliminating all domain complexity and restrictions.
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.core.domain_manager import DomainManager


class TestMinimalDomainManagerStub(unittest.TestCase):
    """Test suite for minimal domain manager stub."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.dm = DomainManager()
    
    def test_initialization(self):
        """Test initialization creates minimal stub."""
        # Should not raise any errors
        self.assertIsInstance(self.dm, DomainManager)
    
    def test_get_domain_status_empty(self):
        """Test that domain status returns empty values."""
        status = self.dm.get_domain_status()
        
        self.assertEqual(status["active_domains"], [])
        self.assertEqual(status["available_domains"], [])
        self.assertEqual(status["inactive_domains"], [])
    
    def test_get_active_domains_empty(self):
        """Test that active domains returns empty list."""
        active = self.dm.get_active_domains()
        self.assertEqual(active, [])
    
    def test_get_available_domains_empty(self):
        """Test that available domains returns empty list."""
        available = self.dm.get_available_domains()
        self.assertEqual(available, [])
    
    def test_get_inactive_domains_empty(self):
        """Test that inactive domains returns empty list."""
        inactive = self.dm.get_inactive_domains()
        self.assertEqual(inactive, [])
    
    def test_is_domain_active_always_true(self):
        """Test that any domain is considered active (no restrictions)."""
        self.assertTrue(self.dm.is_domain_active("eu_crowdfunding"))
        self.assertTrue(self.dm.is_domain_active("securities_law"))
        self.assertTrue(self.dm.is_domain_active("any_domain"))
        self.assertTrue(self.dm.is_domain_active(""))
    
    def test_activate_domains_noop(self):
        """Test that domain activation is a no-op."""
        result = self.dm.activate_domains(["eu_crowdfunding", "securities_law"])
        
        self.assertEqual(result["activated"], [])
        self.assertEqual(result["already_active"], [])
        self.assertEqual(result["invalid"], [])
    
    def test_deactivate_domains_noop(self):
        """Test that domain deactivation is a no-op."""
        result = self.dm.deactivate_domains(["eu_crowdfunding"])
        
        self.assertEqual(result["deactivated"], [])
        self.assertEqual(result["not_active"], [])
    
    def test_reset_to_defaults_returns_empty_status(self):
        """Test that reset returns empty domain status."""
        result = self.dm.reset_to_defaults()
        
        self.assertEqual(result["active_domains"], [])
        self.assertEqual(result["available_domains"], [])
        self.assertEqual(result["inactive_domains"], [])
    
    def test_api_compatibility(self):
        """Test that all expected API methods exist and work."""
        # These methods should exist and work without errors
        self.assertTrue(hasattr(self.dm, "activate_domains"))
        self.assertTrue(hasattr(self.dm, "deactivate_domains"))
        self.assertTrue(hasattr(self.dm, "get_domain_status"))
        self.assertTrue(hasattr(self.dm, "get_active_domains"))
        self.assertTrue(hasattr(self.dm, "get_available_domains"))
        self.assertTrue(hasattr(self.dm, "get_inactive_domains"))
        self.assertTrue(hasattr(self.dm, "is_domain_active"))
        self.assertTrue(hasattr(self.dm, "reset_to_defaults"))
        
        # All methods should return expected types
        self.assertIsInstance(self.dm.activate_domains([]), dict)
        self.assertIsInstance(self.dm.deactivate_domains([]), dict)
        self.assertIsInstance(self.dm.get_domain_status(), dict)
        self.assertIsInstance(self.dm.get_active_domains(), list)
        self.assertIsInstance(self.dm.get_available_domains(), list)
        self.assertIsInstance(self.dm.get_inactive_domains(), list)
        self.assertIsInstance(self.dm.is_domain_active("test"), bool)
    
    def test_no_domain_restrictions(self):
        """Test that the stub eliminates all domain restrictions."""
        # Any domain should be considered active
        self.assertTrue(self.dm.is_domain_active("nonexistent_domain"))
        
        # Domain operations should be no-ops
        result = self.dm.activate_domains(["anything"])
        self.assertEqual(result["activated"], [])
        
        result = self.dm.deactivate_domains(["anything"])
        self.assertEqual(result["deactivated"], [])
        
        # Status should always be empty
        status = self.dm.get_domain_status()
        self.assertFalse(any(status.values()))  # All lists should be empty


if __name__ == '__main__':
    unittest.main() 