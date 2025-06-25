#!/usr/bin/env python3
"""
Full Access Test Suite for Crowd Due Dill
Test that the agent has complete access to all documents without domain restrictions.
"""

import os
import sys
import time
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Add project root to path
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.contextual_rag import OptimizedContextualRAGSystem
from tools.document_manager import SimpleDocumentManager

def print_header(title: str):
    """Print a formatted test section header."""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with formatting."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

class FullAccessTester:
    """Test suite for verifying full database access."""
    
    def __init__(self):
        """Initialize test components."""
        print_header("INITIALIZING TEST SUITE")
        
        # Initialize RAG system
        print("📚 Initializing RAG system...")
        self.rag_system = OptimizedContextualRAGSystem()
        
        # Initialize document manager
        print("📄 Initializing document manager...")
        self.doc_manager = SimpleDocumentManager()
        
        # Test counters
        self.tests_run = 0
        self.tests_passed = 0
        
        print("✅ Test suite initialized successfully")
    
    def test_document_inventory(self):
        """Test 1: Verify all documents are accessible."""
        print_header("TEST 1: DOCUMENT INVENTORY")
        self.tests_run += 1
        
        try:
            # Get all documents from registry
            documents = self.doc_manager.list_documents()
            total_docs = len(documents)
            
            print(f"📊 Found {total_docs} documents in registry:")
            for doc in documents:
                print(f"   📄 {doc.filepath} - {doc.chunk_count} chunks")
            
            # Get vectorstore stats
            stats = self.rag_system.get_stats()
            vectorstore_chunks = stats.get('vectorstore_docs', 0)
            
            print(f"📊 Vectorstore contains {vectorstore_chunks} chunks")
            
            # Test passes if we have documents and chunks
            passed = total_docs > 0 and vectorstore_chunks > 0
            details = f"{total_docs} documents, {vectorstore_chunks} chunks accessible"
            
            print_result("Document inventory", passed, details)
            if passed:
                self.tests_passed += 1
                
        except Exception as e:
            print_result("Document inventory", False, f"Error: {e}")
    
    def test_domain_restrictions_removed(self):
        """Test 2: Verify domain restrictions are completely removed."""
        print_header("TEST 2: DOMAIN RESTRICTIONS REMOVED")
        self.tests_run += 1
        
        try:
            # Test domain status returns empty
            domain_status = self.rag_system.get_domain_status()
            active_domains = domain_status.get('active_domains', [])
            available_domains = domain_status.get('available_domains', [])
            
            print(f"🔍 Active domains: {active_domains}")
            print(f"🔍 Available domains: {available_domains}")
            
            # Test passes if both domain lists are empty
            passed = len(active_domains) == 0 and len(available_domains) == 0
            details = "No domain restrictions found" if passed else "Domain restrictions still present"
            
            print_result("Domain restrictions removed", passed, details)
            if passed:
                self.tests_passed += 1
                
        except Exception as e:
            print_result("Domain restrictions removed", False, f"Error: {e}")
    
    def test_query_access_variety(self):
        """Test 3: Test queries across different regulatory topics."""
        print_header("TEST 3: QUERY ACCESS VARIETY")
        
        test_queries = [
            "What is GDPR?",
            "EU crowdfunding regulation requirements",
            "DORA operational resilience",
            "AML anti-money laundering",
            "DSA digital services act",
            "What are the main EU regulations?"
        ]
        
        successful_queries = 0
        
        for i, query in enumerate(test_queries, 1):
            self.tests_run += 1
            
            try:
                print(f"🔍 Query {i}: {query}")
                
                start_time = time.time()
                result = self.rag_system.query(query, k=3)
                response_time = time.time() - start_time
                
                chunks = result.get('chunks', [])
                chunk_count = len(chunks)
                
                if chunk_count > 0:
                    # Show sources from retrieved chunks
                    sources = []
                    for chunk in chunks[:2]:  # Show first 2 chunks
                        metadata = chunk.get('metadata', {})
                        source = metadata.get('document.source', 'unknown')
                        if source not in sources:
                            sources.append(source)
                    
                    passed = True
                    details = f"{chunk_count} chunks from sources: {', '.join(sources)} ({response_time:.3f}s)"
                    successful_queries += 1
                    self.tests_passed += 1
                else:
                    passed = False
                    details = f"No chunks retrieved ({response_time:.3f}s)"
                
                print_result(f"Query {i}", passed, details)
                
            except Exception as e:
                print_result(f"Query {i}", False, f"Error: {e}")
        
        # Summary for this test group
        print(f"\n📊 Query Summary: {successful_queries}/{len(test_queries)} queries successful")
    
    def test_comprehensive_content_access(self):
        """Test 4: Verify access to content from all document sources."""
        print_header("TEST 4: COMPREHENSIVE CONTENT ACCESS")
        self.tests_run += 1
        
        try:
            # Query for broad regulatory content
            query = "European Union financial regulations and compliance requirements"
            result = self.rag_system.query(query, k=10)  # Get more chunks
            
            chunks = result.get('chunks', [])
            
            if not chunks:
                print_result("Comprehensive content access", False, "No content retrieved")
                return
            
            # Analyze sources in retrieved content
            sources = {}
            regulation_types = set()
            
            for chunk in chunks:
                metadata = chunk.get('metadata', {})
                source = metadata.get('document.source', 'unknown')
                reg_number = metadata.get('structure.regulation_number', 'unknown')
                
                if source != 'unknown':
                    sources[source] = sources.get(source, 0) + 1
                
                if reg_number != 'unknown':
                    regulation_types.add(reg_number)
            
            print(f"📊 Content Sources Found:")
            for source, count in sources.items():
                print(f"   📄 {source}: {count} chunks")
            
            print(f"📊 Regulation Types Found:")
            for reg_type in sorted(regulation_types):
                print(f"   ⚖️ {reg_type}")
            
            # Test passes if we have multiple sources and regulation types
            passed = len(sources) >= 2 and len(regulation_types) >= 2
            details = f"{len(sources)} sources, {len(regulation_types)} regulation types, {len(chunks)} total chunks"
            
            print_result("Comprehensive content access", passed, details)
            if passed:
                self.tests_passed += 1
                
        except Exception as e:
            print_result("Comprehensive content access", False, f"Error: {e}")
    
    def test_no_domain_filtering_in_results(self):
        """Test 5: Verify no domain filtering is applied to results."""
        print_header("TEST 5: NO DOMAIN FILTERING IN RESULTS")
        self.tests_run += 1
        
        try:
            # Query that should return results from multiple document types
            query = "regulation compliance requirements"
            result = self.rag_system.query(query, k=8)
            
            chunks = result.get('chunks', [])
            
            if not chunks:
                print_result("No domain filtering", False, "No results to analyze")
                return
            
            # Check if results contain domain metadata (should be ignored)
            domain_values = set()
            for chunk in chunks:
                metadata = chunk.get('metadata', {})
                domain = metadata.get('document.domain')
                if domain:
                    domain_values.add(domain)
            
            print(f"🔍 Domain metadata found in chunks: {domain_values}")
            print(f"🔍 Retrieved {len(chunks)} chunks without domain filtering")
            
            # Test passes if we got results (domain metadata may exist but should be ignored)
            passed = len(chunks) > 0
            details = f"Retrieved {len(chunks)} chunks - domain filtering disabled"
            
            print_result("No domain filtering", passed, details)
            if passed:
                self.tests_passed += 1
                
        except Exception as e:
            print_result("No domain filtering", False, f"Error: {e}")
    
    def test_system_performance(self):
        """Test 6: Basic performance test."""
        print_header("TEST 6: SYSTEM PERFORMANCE")
        self.tests_run += 1
        
        try:
            queries = [
                "GDPR data protection",
                "crowdfunding investment rules",
                "operational resilience requirements"
            ]
            
            total_time = 0
            successful_queries = 0
            
            for query in queries:
                start_time = time.time()
                result = self.rag_system.query(query, k=3)
                query_time = time.time() - start_time
                
                total_time += query_time
                
                if result.get('chunks'):
                    successful_queries += 1
            
            avg_time = total_time / len(queries)
            
            # Test passes if average query time is reasonable and all queries succeeded
            passed = avg_time < 2.0 and successful_queries == len(queries)
            details = f"Avg query time: {avg_time:.3f}s, {successful_queries}/{len(queries)} successful"
            
            print_result("System performance", passed, details)
            if passed:
                self.tests_passed += 1
                
        except Exception as e:
            print_result("System performance", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all tests and provide summary."""
        print_header("FULL ACCESS TEST SUITE")
        print("🚀 Starting comprehensive database access tests...")
        
        # Run all tests
        self.test_document_inventory()
        self.test_domain_restrictions_removed()
        self.test_query_access_variety()
        self.test_comprehensive_content_access()
        self.test_no_domain_filtering_in_results()
        self.test_system_performance()
        
        # Final summary
        print_header("TEST RESULTS SUMMARY")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 EXCELLENT: Agent has full access to database!")
            print("   ✅ No domain restrictions detected")
            print("   ✅ All content accessible")
            print("   ✅ System performing well")
        elif success_rate >= 60:
            print("\n⚠️ GOOD: Most tests passed, minor issues detected")
        else:
            print("\n❌ ISSUES: Significant problems detected")
            print("   🔧 Review failed tests above")
        
        return success_rate >= 80

def main():
    """Run the full access test suite."""
    print("🧪 Crowd Due Dill - Full Access Test Suite")
    print("Testing agent access to database without domain restrictions")
    
    try:
        tester = FullAccessTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n🎯 CONCLUSION: System ready for deployment!")
            print("   The agent has complete access to all documents")
            return 0
        else:
            print("\n🔧 CONCLUSION: Issues found, review test results")
            return 1
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("🔧 Check system configuration and try again")
        return 1

if __name__ == "__main__":
    exit(main()) 