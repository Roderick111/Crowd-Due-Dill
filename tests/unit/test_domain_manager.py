#!/usr/bin/env python3
"""
Unit tests for DomainManager component.

Tests all domain management functionality including:
- Domain validation and initialization
- FIFO replacement logic
- ChromaDB filter generation
- Status reporting
- Edge cases and error handling

NOTE: TEMPORARY MODIFICATIONS FOR SINGLE DOMAIN MODE
Several tests have been updated to work with MAX_ACTIVE_DOMAINS = 1.
Search for "TODO: TEMPORARY" comments to find modified tests.
When re-enabling multiple domains, revert these changes.
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.core.domain_manager import DomainManager


class TestDomainManager(unittest.TestCase):
    """Test suite for DomainManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.dm = DomainManager()
    
    def test_default_initialization(self):
        """Test default initialization with lunar domain."""
        self.assertEqual(self.dm.active_domains, ["lunar"])
        self.assertEqual(len(self.dm.active_domains), 1)
        self.assertTrue(self.dm.is_domain_active("lunar"))
    
    def test_custom_initialization_valid_domains(self):
        """Test initialization with custom valid domains."""
        custom_domains = {"numerology", "crystals"}
        dm = DomainManager(custom_domains)
        # TODO: TEMPORARY - Updated for single domain mode (was: custom_domains)
        # Only one domain can be active at a time now
        self.assertEqual(len(dm.active_domains), 1)
        self.assertTrue(set(dm.active_domains).issubset(custom_domains))
    
    def test_custom_initialization_invalid_domains(self):
        """Test initialization with invalid domains (should be filtered out)."""
        mixed_domains = {"lunar", "invalid_domain", "numerology"}
        dm = DomainManager(mixed_domains)
        # TODO: TEMPORARY - Updated for single domain mode (was: {"lunar", "numerology"})
        # Only one domain can be active, and invalid domains should be filtered out
        valid_expected_domains = {"lunar", "numerology"}
        self.assertEqual(len(dm.active_domains), 1)
        self.assertTrue(set(dm.active_domains).issubset(valid_expected_domains))
    
    def test_custom_initialization_too_many_domains(self):
        """Test initialization with more than max allowed domains."""
        too_many_domains = {"lunar", "numerology", "crystals"}  # Only 3 domains but MAX is 2
        dm = DomainManager(too_many_domains)
        self.assertEqual(len(dm.active_domains), DomainManager.MAX_ACTIVE_DOMAINS)
        self.assertTrue(set(dm.active_domains).issubset(DomainManager.AVAILABLE_DOMAINS))
    
    def test_enable_valid_domain(self):
        """Test enabling a valid domain."""
        result = self.dm.enable_domain("numerology")
        self.assertTrue(result)
        self.assertIn("numerology", self.dm.active_domains)
        # TODO: TEMPORARY - Updated for single domain mode (was: 2)
        self.assertEqual(len(self.dm.active_domains), 1)
    
    def test_enable_invalid_domain(self):
        """Test enabling an invalid domain."""
        result = self.dm.enable_domain("invalid_domain")
        self.assertFalse(result)
        self.assertNotIn("invalid_domain", self.dm.active_domains)
        self.assertEqual(len(self.dm.active_domains), 1)  # Should remain unchanged
    
    def test_enable_already_active_domain(self):
        """Test enabling a domain that's already active."""
        result = self.dm.enable_domain("lunar")
        self.assertTrue(result)
        self.assertEqual(len(self.dm.active_domains), 1)  # Should not duplicate
    
    def test_fifo_replacement(self):
        """Test FIFO replacement when adding domains beyond capacity."""
        # TODO: TEMPORARY - Updated for single domain mode
        # Original test was for 2-domain capacity, now testing 1-domain capacity
        
        # Add second domain - should trigger FIFO (since MAX_ACTIVE_DOMAINS = 1)
        self.dm.enable_domain("numerology")
        
        # Should still have max domains
        self.assertEqual(len(self.dm.active_domains), DomainManager.MAX_ACTIVE_DOMAINS)
        
        # Should contain the new domain
        self.assertIn("numerology", self.dm.active_domains)
        
        # Should have removed the oldest domain (lunar was first)
        self.assertNotIn("lunar", self.dm.active_domains)
        
        # Should only contain numerology (single domain mode)
        self.assertEqual(set(self.dm.active_domains), {"numerology"})
    
    def test_disable_active_domain(self):
        """Test disabling an active domain."""
        self.dm.enable_domain("numerology")
        result = self.dm.disable_domain("numerology")
        self.assertTrue(result)
        self.assertNotIn("numerology", self.dm.active_domains)
    
    def test_disable_inactive_domain(self):
        """Test disabling a domain that's not active."""
        result = self.dm.disable_domain("numerology")
        self.assertFalse(result)
        # Active domains should remain unchanged
        self.assertEqual(self.dm.active_domains, ["lunar"])
    
    def test_get_status_structure(self):
        """Test that get_status returns correct structure."""
        status = self.dm.get_status()
        required_keys = {"active_domains", "available_domains", "max_active_domains", "inactive_domains"}
        self.assertTrue(all(key in status for key in required_keys))
    
    def test_get_status_content(self):
        """Test that get_status returns correct content."""
        self.dm.enable_domain("numerology")
        status = self.dm.get_status()
        
        # TODO: TEMPORARY - Updated for single domain mode (was: {"numerology", "lunar"})
        self.assertEqual(set(status["active_domains"]), {"numerology"})
        self.assertEqual(set(status["available_domains"]), DomainManager.AVAILABLE_DOMAINS)
        self.assertEqual(status["max_active_domains"], DomainManager.MAX_ACTIVE_DOMAINS)
        
        # TODO: TEMPORARY - Updated for single domain mode
        expected_inactive = DomainManager.AVAILABLE_DOMAINS - {"numerology"}
        self.assertEqual(set(status["inactive_domains"]), expected_inactive)
    
    def test_chroma_filter_single_domain(self):
        """Test ChromaDB filter generation for single domain."""
        filter_dict = self.dm.get_chroma_filter()
        expected = {"domain": {"$in": ["lunar"]}}
        self.assertEqual(filter_dict, expected)
    
    def test_chroma_filter_multiple_domains(self):
        """Test ChromaDB filter generation - currently single domain mode."""
        # TODO: TEMPORARY - Updated for single domain mode
        # Original test was for multiple domains, now testing single domain behavior
        self.dm.enable_domain("numerology")
        filter_dict = self.dm.get_chroma_filter()
        
        self.assertIn("domain", filter_dict)
        self.assertIn("$in", filter_dict["domain"])
        
        # Check that only the active domain is included (single domain mode)
        domains_in_filter = set(filter_dict["domain"]["$in"])
        self.assertEqual(domains_in_filter, {"numerology"})
    
    def test_chroma_filter_empty_domains(self):
        """Test ChromaDB filter generation when no domains are active."""
        self.dm.active_domains.clear()
        filter_dict = self.dm.get_chroma_filter()
        self.assertEqual(filter_dict, {})
    
    def test_is_domain_active(self):
        """Test domain activity checking."""
        self.assertTrue(self.dm.is_domain_active("lunar"))
        self.assertFalse(self.dm.is_domain_active("numerology"))
        
        self.dm.enable_domain("numerology")
        self.assertTrue(self.dm.is_domain_active("numerology"))
        # TODO: TEMPORARY - In single domain mode, lunar should be replaced
        self.assertFalse(self.dm.is_domain_active("lunar"))
    
    def test_get_active_domains_sorted(self):
        """Test that active domains are returned in sorted order."""
        self.dm.enable_domain("numerology")
        active = self.dm.get_active_domains()
        # TODO: TEMPORARY - Updated for single domain mode (was: ["lunar", "numerology"])
        self.assertEqual(active, ["numerology"])  # Should only have one domain
    
    def test_get_inactive_domains_sorted(self):
        """Test that inactive domains are returned in sorted order."""
        inactive = self.dm.get_inactive_domains()
        expected = sorted(DomainManager.AVAILABLE_DOMAINS - {"lunar"})
        self.assertEqual(inactive, expected)
    
    def test_reset_to_default(self):
        """Test resetting to default configuration."""
        self.dm.enable_domain("numerology")
        self.dm.enable_domain("crystals")
        
        self.dm.reset_to_default()
        self.assertEqual(self.dm.active_domains, ["lunar"])
    
    def test_string_representation(self):
        """Test string representation methods."""
        str_repr = str(self.dm)
        self.assertIn("DomainManager", str_repr)
        self.assertIn("lunar", str_repr)
        
        repr_str = repr(self.dm)
        self.assertIn("DomainManager", repr_str)
        self.assertIn("active_domains", repr_str)
    
    def test_domain_constants(self):
        """Test that domain constants are properly defined."""
        self.assertIsInstance(DomainManager.AVAILABLE_DOMAINS, set)
        self.assertGreater(len(DomainManager.AVAILABLE_DOMAINS), 0)
        self.assertIsInstance(DomainManager.MAX_ACTIVE_DOMAINS, int)
        self.assertGreater(DomainManager.MAX_ACTIVE_DOMAINS, 0)
        
        # Test that expected domains are available
        # TODO: Temporarily reduced set due to disabled domains: "archetypes", "astrology", "ifs", "tarot"
        expected_domains = {"lunar", "numerology", "crystals"}
        self.assertEqual(DomainManager.AVAILABLE_DOMAINS, expected_domains)
    
    def test_validate_domains_method(self):
        """Test the _validate_domains private method."""
        # TODO: TEMPORARY - Updated for single domain mode
        # Test with valid domains (should be limited to 1)
        valid_domains = {"lunar", "numerology"}
        result = self.dm._validate_domains(valid_domains)
        self.assertEqual(len(result), 1)
        self.assertTrue(result.issubset(valid_domains))
        
        # Test with mixed valid/invalid domains  
        mixed_domains = {"lunar", "invalid", "numerology"}
        result = self.dm._validate_domains(mixed_domains)
        self.assertEqual(len(result), 1)
        self.assertTrue(result.issubset({"lunar", "numerology"}))
        
        # Test with too many domains
        # TODO: TEMPORARY - Updated comment for single domain mode (was: max is 2)
        too_many = {"lunar", "numerology", "crystals"}  # 3 domains, max is 1
        result = self.dm._validate_domains(too_many)
        self.assertEqual(len(result), DomainManager.MAX_ACTIVE_DOMAINS)
    
    def test_concurrent_operations(self):
        """Test multiple operations in sequence."""
        # TODO: TEMPORARY - Updated for single domain mode
        # Enable numerology (should replace lunar due to FIFO)
        self.dm.enable_domain("numerology")
        
        # Check state (single domain mode)
        self.assertEqual(len(self.dm.active_domains), 1)
        self.assertNotIn("lunar", self.dm.active_domains)  # Should be removed
        self.assertEqual(set(self.dm.active_domains), {"numerology"})
        
        # Enable crystals (should replace numerology)
        self.dm.enable_domain("crystals")
        self.assertEqual(len(self.dm.active_domains), 1)
        self.assertIn("crystals", self.dm.active_domains)
        self.assertNotIn("numerology", self.dm.active_domains)
        
        # Re-enable lunar (should replace crystals)
        self.dm.enable_domain("lunar")
        self.assertEqual(len(self.dm.active_domains), 1)
        self.assertIn("lunar", self.dm.active_domains)
        self.assertNotIn("crystals", self.dm.active_domains)


if __name__ == "__main__":
    unittest.main() 