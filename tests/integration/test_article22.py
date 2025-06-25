#!/usr/bin/env python3
"""
Test Article 22 Query with Parallel Hybrid System
"""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.contextual_rag import OptimizedContextualRAGSystem

def test_article22():
    """Test Article 22 query with parallel hybrid system."""
    print("🧪 Testing Article 22 Query - Parallel Hybrid System")
    print("=" * 60)
    
    try:
        # Initialize RAG system
        print("📚 Initializing RAG system...")
        rag_system = OptimizedContextualRAGSystem()
        
        # Test Article 22 query
        query = "Tell me about Article 22 of the DSA"
        print(f"🔍 Query: '{query}'")
        print("-" * 60)
        
        result = rag_system.query(query, k=4)
        
        # Show parallel hybrid results
        search_strategy = result.get('search_strategy', 'unknown')
        total_results = result.get('total_results', 0)
        processing_time = result.get('processing_time', 0.0)
        
        print(f"Search Strategy: {search_strategy}")
        print(f"Total Results: {total_results}")
        print(f"Processing Time: {processing_time:.3f}s")
        
        # Show query analysis
        query_info = result.get('query_info', {})
        print(f"Query Type: {query_info.get('query_type', 'unknown')}")
        print(f"Is Precise Lookup: {query_info.get('is_precise_lookup', False)}")
        print(f"Article Number: {query_info.get('article_number', 'N/A')}")
        print(f"Regulation: {query_info.get('regulation', 'N/A')}")
        
        # Show vector results
        vector_results = result.get('vector_results', [])
        print(f"\n🎯 Vector + Reranking Results: {len(vector_results)}")
        for i, res in enumerate(vector_results[:2], 1):
            rerank_score = res.get('rerank_score', 0.0)
            similarity_score = res.get('similarity_score', 0.0)
            content = res.get('page_content', '')[:200] + "..."
            print(f"  {i}. Rerank: {rerank_score:.3f}, Similarity: {similarity_score:.3f}")
            print(f"     {content}")
            print()
        
        # Show keyword results
        keyword_results = result.get('keyword_results', [])
        print(f"🔍 Keyword Results: {len(keyword_results)}")
        for i, res in enumerate(keyword_results[:2], 1):
            content = res.get('page_content', '')[:200] + "..."
            print(f"  {i}. Precise Match:")
            print(f"     {content}")
            print()
        
        # Success/failure analysis
        if total_results > 0:
            print("✅ SUCCESS: Parallel hybrid system returned results")
            
            # Check if we got the right content
            all_content = []
            for res in vector_results + keyword_results:
                all_content.append(res.get('page_content', '').lower())
            
            # Look for Article 22 content indicators
            article22_indicators = ['article 22', 'trusted flagger', 'flagging']
            wrong_indicators = ['delegation of power', 'committee', 'article 87', 'article 88', 'article 89', 'article 90']
            
            found_correct = any(indicator in content for content in all_content for indicator in article22_indicators)
            found_wrong = any(indicator in content for content in all_content for indicator in wrong_indicators)
            
            if found_correct and not found_wrong:
                print("🎉 PERFECT: Found correct Article 22 content!")
            elif found_correct and found_wrong:
                print("⚠️  MIXED: Found both correct and incorrect content")
            elif found_wrong:
                print("❌ WRONG: Still returning Articles 87-90 content")
            else:
                print("❓ UNCLEAR: Content analysis inconclusive")
                
        else:
            print("❌ FAILURE: No results returned")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_article22() 