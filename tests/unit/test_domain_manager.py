#!/usr/bin/env python3
"""
Unit tests for Simplified DomainManager component.

Tests single-domain functionality:
- Always active eu_crowdfunding domain
- API compatibility with legacy multi-domain interface
- Status reporting
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.core.domain_manager import DomainManager


class TestSimplifiedDomainManager(unittest.TestCase):
    """Test suite for simplified single-domain DomainManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.dm = DomainManager()
    
    def test_default_initialization(self):
        """Test default initialization with eu_crowdfunding domain."""
        self.assertEqual(list(self.dm.active_domains), ["eu_crowdfunding"])
        self.assertEqual(len(self.dm.active_domains), 1)
        self.assertTrue(self.dm.is_domain_active("eu_crowdfunding"))
    
    def test_activate_valid_domain(self):
        """Test activating the valid eu_crowdfunding domain."""
        result = self.dm.activate_domains(["eu_crowdfunding"])
        
        self.assertEqual(result["activated"], ["eu_crowdfunding"])
        self.assertEqual(result["already_active"], [])
        self.assertEqual(result["invalid"], [])
        self.assertIn("eu_crowdfunding", result["active_domains"])
    
    def test_activate_invalid_domain(self):
        """Test activating an invalid domain."""
        result = self.dm.activate_domains(["invalid_domain"])
        
        self.assertEqual(result["activated"], ["eu_crowdfunding"])  # Always returns active domain
        self.assertEqual(result["already_active"], [])
        self.assertEqual(result["invalid"], ["invalid_domain"])
        self.assertEqual(result["active_domains"], ["eu_crowdfunding"])
    
    def test_deactivate_domain_always_fails(self):
        """Test that deactivating any domain always fails (eu_crowdfunding stays active)."""
        result = self.dm.deactivate_domains(["eu_crowdfunding"])
        
        self.assertEqual(result["deactivated"], [])
        self.assertEqual(result["not_active"], ["eu_crowdfunding"])
        self.assertEqual(result["active_domains"], ["eu_crowdfunding"])
    
    def test_is_domain_active(self):
        """Test domain activity checking."""
        self.assertTrue(self.dm.is_domain_active("eu_crowdfunding"))
        self.assertFalse(self.dm.is_domain_active("securities_law"))
        self.assertFalse(self.dm.is_domain_active("invalid_domain"))
    
    def test_get_active_domains(self):
        """Test getting active domains."""
        active = self.dm.get_active_domains()
        self.assertEqual(active, ["eu_crowdfunding"])
    
    def test_get_available_domains(self):
        """Test getting available domains."""
        available = self.dm.get_available_domains()
        self.assertEqual(available, ["eu_crowdfunding"])
        self.assertEqual(set(available), DomainManager.AVAILABLE_DOMAINS)
    
    def test_get_inactive_domains(self):
        """Test getting inactive domains (always empty)."""
        inactive = self.dm.get_inactive_domains()
        self.assertEqual(inactive, [])
    
    def test_get_domain_status_structure(self):
        """Test that get_domain_status returns correct structure."""
        status = self.dm.get_domain_status()
        required_keys = {"active_domains", "available_domains", "max_active_domains", "inactive_domains"}
        self.assertTrue(all(key in status for key in required_keys))
    
    def test_get_domain_status_content(self):
        """Test that get_domain_status returns correct content."""
        status = self.dm.get_domain_status()
        
        self.assertEqual(status["active_domains"], ["eu_crowdfunding"])
        self.assertEqual(set(status["available_domains"]), DomainManager.AVAILABLE_DOMAINS)
        self.assertEqual(status["max_active_domains"], 1)
        self.assertEqual(status["inactive_domains"], [])
    
    def test_reset_to_defaults(self):
        """Test resetting to default configuration."""
        # Even after any operations, should always return to eu_crowdfunding
        result = self.dm.reset_to_defaults()
        
        self.assertEqual(result["active_domains"], ["eu_crowdfunding"])
        self.assertEqual(result["available_domains"], ["eu_crowdfunding"])
        self.assertEqual(result["inactive_domains"], [])
    
    def test_string_representation(self):
        """Test string representation."""
        str_repr = str(self.dm)
        self.assertIn("eu_crowdfunding", str_repr)
        self.assertIn("DomainManager", str_repr)
    
    def test_domain_constants(self):
        """Test that domain constants are correctly defined."""
        self.assertIsInstance(DomainManager.AVAILABLE_DOMAINS, set)
        self.assertEqual(DomainManager.AVAILABLE_DOMAINS, {"eu_crowdfunding"})
        self.assertEqual(DomainManager.DEFAULT_DOMAIN, "eu_crowdfunding")
    
    def test_multiple_domain_requests(self):
        """Test activating multiple domains (only eu_crowdfunding should be valid)."""
        result = self.dm.activate_domains(["eu_crowdfunding", "securities_law", "compliance"])
        
        self.assertEqual(result["activated"], ["eu_crowdfunding"])
        self.assertEqual(result["already_active"], [])
        self.assertEqual(set(result["invalid"]), {"securities_law", "compliance"})
        self.assertEqual(result["active_domains"], ["eu_crowdfunding"])
    
    def test_api_compatibility(self):
        """Test that the API maintains compatibility with legacy multi-domain interface."""
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


if __name__ == '__main__':
    unittest.main() 