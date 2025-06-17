#!/usr/bin/env python3
"""
Simplified Domain Manager for Single Domain Setup
Always uses eu_crowdfunding domain - no domain switching needed.
"""
import logging
from typing import List, Dict, Set, Any

logger = logging.getLogger(__name__)

class DomainManager:
    """
    Simplified domain manager for single domain (eu_crowdfunding) setup.
    Maintains compatibility with existing code but removes complexity.
    """
    
    # Single domain configuration
    AVAILABLE_DOMAINS = {"eu_crowdfunding"}
    DEFAULT_DOMAIN = "eu_crowdfunding"
    
    def __init__(self, max_active_domains: int = 1):
        """Initialize with single domain active."""
        self.max_active_domains = max_active_domains
        self.active_domains: Set[str] = {self.DEFAULT_DOMAIN}
        
        logger.info(f"🌍 Domain Manager initialized with single domain: {self.DEFAULT_DOMAIN}")
    
    def activate_domains(self, domains: List[str]) -> Dict[str, Any]:
        """
        Simplified activation - always returns eu_crowdfunding as active.
        Maintains API compatibility but ignores input domains.
        """
        logger.info(f"✅ Domain {self.DEFAULT_DOMAIN} is always active")
        return {
            "activated": [self.DEFAULT_DOMAIN],
            "already_active": [],
            "invalid": [d for d in domains if d != self.DEFAULT_DOMAIN],
            "active_domains": list(self.active_domains)
        }
    
    def deactivate_domains(self, domains: List[str]) -> Dict[str, Any]:
        """
        Simplified deactivation - eu_crowdfunding always stays active.
        Maintains API compatibility but prevents deactivation.
        """
        logger.info(f"🔒 Domain {self.DEFAULT_DOMAIN} cannot be deactivated (always active)")
        return {
            "deactivated": [],
            "not_active": domains,
            "active_domains": list(self.active_domains)
        }
    
    def get_active_domains(self) -> List[str]:
        """Return active domains (always eu_crowdfunding)."""
        return list(self.active_domains)
    
    def is_domain_active(self, domain: str) -> bool:
        """Check if domain is active."""
        return domain == self.DEFAULT_DOMAIN
    
    def get_domain_status(self) -> Dict[str, Any]:
        """Get complete domain status."""
        return {
            "active_domains": list(self.active_domains),
            "available_domains": sorted(self.AVAILABLE_DOMAINS),
            "max_active_domains": self.max_active_domains,
            "inactive_domains": []  # No inactive domains in single-domain setup
        }
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """Reset to default configuration (eu_crowdfunding active)."""
        self.active_domains = {self.DEFAULT_DOMAIN}
        logger.info(f"🔄 Reset to default: {self.DEFAULT_DOMAIN} active")
        return self.get_domain_status()
    
    def get_available_domains(self) -> List[str]:
        """Get all available domains."""
        return sorted(self.AVAILABLE_DOMAINS)
    
    def get_inactive_domains(self) -> List[str]:
        """Get inactive domains (always empty in single-domain setup)."""
        return []
    
    def __str__(self) -> str:
        return (
            f"DomainManager(active={self.active_domains}, "
            f"available_domains={self.AVAILABLE_DOMAINS}, "
            f"max_active={self.max_active_domains})"
        ) 