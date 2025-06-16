#!/usr/bin/env python3
"""
Domain Manager for Multi-Domain RAG System

Handles domain activation, deactivation, FIFO replacement, and status reporting.
Separated from the main RAG system for better modularity and testing.
"""

from typing import Set, Dict, Any, List


class DomainManager:
    """
    Manages knowledge domains for the RAG system.
    
    Features:
    - Domain activation/deactivation
    - FIFO replacement when at capacity
    - Domain validation and status reporting
    - ChromaDB filter generation
    """
    
    # Available knowledge domains for crowdfunding due diligence
    # Main domains: EU regulations, national laws, compliance, best practices
    AVAILABLE_DOMAINS = {"eu_crowdfunding", "securities_law", "compliance", "best_practices"}
    
    # Start with single domain system for simplicity
    # Can expand to multiple domains later for different regulatory areas
    MAX_ACTIVE_DOMAINS = 1
    
    def __init__(self, initial_domains: Set[str] = None):
        """
        Initialize domain manager.
        
        Args:
            initial_domains: Set of domains to activate initially (defaults to {"eu_crowdfunding"})
        """
        if initial_domains is None:
            # Use list to maintain insertion order for FIFO
            self.active_domains = ["eu_crowdfunding"]
        else:
            validated = self._validate_domains(initial_domains)
            self.active_domains = list(validated)
    
    def _validate_domains(self, domains: Set[str]) -> Set[str]:
        """Validate and limit domains to available ones and max capacity."""
        valid_domains = domains.intersection(self.AVAILABLE_DOMAINS)
        
        if len(valid_domains) > self.MAX_ACTIVE_DOMAINS:
            # Take first domains in order
            limited_domains = set(list(valid_domains)[:self.MAX_ACTIVE_DOMAINS])
            print(f"⚠️  Limited to {self.MAX_ACTIVE_DOMAINS} domains: {sorted(limited_domains)}")
            return limited_domains
        
        return valid_domains
    
    def enable_domain(self, domain: str) -> bool:
        """
        Enable a knowledge domain. If already at max capacity, removes oldest domain first (FIFO).
        
        Args:
            domain: Domain name to enable
            
        Returns:
            bool: True if domain was enabled, False if invalid domain
        """
        if domain not in self.AVAILABLE_DOMAINS:
            print(f"❌ Invalid domain '{domain}'. Available: {sorted(self.AVAILABLE_DOMAINS)}")
            return False
        
        if domain in self.active_domains:
            print(f"ℹ️  Domain '{domain}' already active")
            return True
        
        # If at capacity, remove oldest (first) domain
        if len(self.active_domains) >= self.MAX_ACTIVE_DOMAINS:
            removed_domain = self.active_domains.pop(0)  # Remove first (oldest)
            print(f"🔄 Removed oldest domain '{removed_domain}' to make room")
        
        # Add new domain to end
        self.active_domains.append(domain)
        print(f"✅ Enabled domain '{domain}'. Active: {sorted(self.active_domains)}")
        
        return True
    
    def disable_domain(self, domain: str) -> bool:
        """
        Disable a knowledge domain.
        
        Args:
            domain: Domain name to disable
            
        Returns:
            bool: True if domain was disabled, False if not active
        """
        if domain not in self.active_domains:
            print(f"ℹ️  Domain '{domain}' not currently active")
            return False
        
        self.active_domains.remove(domain)
        print(f"✅ Disabled domain '{domain}'. Active: {sorted(self.active_domains)}")
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current domain configuration status.
        
        Returns:
            dict: Domain status information
        """
        active_set = set(self.active_domains)
        return {
            "active_domains": sorted(self.active_domains),
            "available_domains": sorted(self.AVAILABLE_DOMAINS),
            "max_active_domains": self.MAX_ACTIVE_DOMAINS,
            "inactive_domains": sorted(self.AVAILABLE_DOMAINS - active_set)
        }
    
    def get_chroma_filter(self) -> Dict[str, Any]:
        """
        Generate ChromaDB metadata filter for active domains.
        
        Returns:
            dict: ChromaDB filter dict or empty dict if no domains active
        """
        if not self.active_domains:
            return {}
        
        return {
            "domain": {"$in": self.active_domains}
        }
    
    def is_domain_active(self, domain: str) -> bool:
        """Check if a specific domain is currently active."""
        return domain in self.active_domains
    
    def get_active_domains(self) -> List[str]:
        """Get list of active domains in sorted order."""
        return sorted(self.active_domains)
    
    def get_inactive_domains(self) -> List[str]:
        """Get list of inactive domains in sorted order."""
        active_set = set(self.active_domains)
        return sorted(self.AVAILABLE_DOMAINS - active_set)
    
    def reset_to_default(self):
        """Reset to default domain configuration (eu_crowdfunding only)."""
        self.active_domains = ["eu_crowdfunding"]
        print("🔄 Reset to default domain: eu_crowdfunding")
    
    def __str__(self) -> str:
        """String representation of domain manager state."""
        return f"DomainManager(active={sorted(self.active_domains)}, max={self.MAX_ACTIVE_DOMAINS})"
    
    def __repr__(self) -> str:
        """Detailed representation of domain manager state."""
        return (f"DomainManager(active_domains={self.active_domains}, "
                f"available_domains={self.AVAILABLE_DOMAINS}, "
                f"max_active={self.MAX_ACTIVE_DOMAINS})") 