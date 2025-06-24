#!/usr/bin/env python3
"""
Quick Database Access Test
Simple test to verify agent has access to all documents.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.contextual_rag import OptimizedContextualRAGSystem

def quick_test():
    """Run a quick test of database access."""
    print("🧪 Quick Database Access Test")
    print("=" * 40)
    
    try:
        # Initialize RAG system
        print("📚 Initializing RAG system...")
        rag_system = OptimizedContextualRAGSystem()
        
        # Test 1: Check documents
        stats = rag_system.get_stats()
        total_chunks = stats.get('vectorstore_docs', 0)
        print(f"✅ Database: {total_chunks} chunks available")
        
        # Test 2: Check no domain restrictions
        domain_status = rag_system.get_domain_status()
        active_domains = len(domain_status.get('active_domains', []))
        print(f"✅ Domains: {active_domains} active (should be 0)")
        
        # Test 3: Quick query test
        print("🔍 Testing queries...")
        test_queries = [
            "What is EU crowdfunding regulation?",
            "GDPR data protection",
            "DORA operational resilience"
        ]
        
        successful = 0
        for query in test_queries:
            try:
                result = rag_system.query(query, k=2)
                chunks = len(result.get('chunks', []))
                if chunks > 0:
                    successful += 1
                    print(f"   ✅ '{query[:30]}...' → {chunks} chunks")
                else:
                    print(f"   ❌ '{query[:30]}...' → No results")
            except Exception as e:
                print(f"   ❌ '{query[:30]}...' → Error: {e}")
        
        print("=" * 40)
        print(f"📊 Results: {successful}/{len(test_queries)} queries successful")
        
        if total_chunks > 0 and active_domains == 0 and successful == len(test_queries):
            print("🎉 SUCCESS: Agent has full database access!")
            return True
        else:
            print("⚠️ ISSUES: Some problems detected")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1) 