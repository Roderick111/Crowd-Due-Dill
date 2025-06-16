#!/usr/bin/env python3
"""
Test script for Crowdfunding Due Diligence Agent RAG activation system and Embedding Cache Performance
"""

from src.main import classify_and_decide_rag
from src.core.contextual_rag import OptimizedContextualRAGSystem
import time

def test_crowdfunding_agent_rag():
    print('⚖️ Testing Crowdfunding Due Diligence Agent RAG Activation System')
    print('=' * 60)
    
    # Test queries organized by expected behavior
    test_cases = {
        "Advisory + RAG Expected": [
            "I'm concerned about our crowdfunding compliance",
            "We're worried about regulatory risks",
            "I'm stressed about meeting authorization requirements",
            "Our platform needs strategic guidance on EU regulations",
            "I feel overwhelmed by the compliance obligations"
        ],
        
        "Analytical + RAG Expected": [
            "What are the authorization requirements for crowdfunding platforms?",
            "Explain the investment limits under EU regulation 2020/1503",
            "How do cross-border crowdfunding services work?",
            "What are the disclosure requirements for project owners?",
            "Detail the investor protection measures in crowdfunding"
        ],
        
        "Advisory + No RAG Expected": [
            "I'm stressed about general business operations",
            "My team is having communication problems",
            "I'm worried about our budget",
            "We had a disagreement with our vendor",
            "I'm feeling overwhelmed with day-to-day management"
        ],
        
        "Analytical + No RAG Expected": [
            "What's the weather like today?",
            "How do I cook pasta?",
            "What's the capital of France?",
            "Explain basic math concepts",
            "Tell me about car maintenance"
        ],
        
        "Mixed Scenarios": [
            "Hello there!",
            "Thanks for your help",
            "I need some guidance on regulatory compliance"
        ]
    }
    
    correct_classifications = 0
    correct_rag_decisions = 0
    total_tests = 0
    
    for category, queries in test_cases.items():
        print(f"\n📂 {category}")
        print("-" * 40)
        
        for query in queries:
            total_tests += 1
            
            # Test our combined classifier
            decision = classify_and_decide_rag({"messages": [type('obj', (object,), {'content': query})]})
            message_type = decision["message_type"]
            should_use_rag = decision["should_use_rag"]
            
            # Expected behavior based on category
            expected_advisory = "Advisory" in category
            expected_rag = "RAG Expected" in category
            
            # Check classification accuracy
            is_classification_correct = (
                (expected_advisory and message_type == "advisory") or
                (not expected_advisory and message_type == "analytical")
            )
            
            # Check RAG decision accuracy  
            is_rag_correct = (should_use_rag == expected_rag)
            
            if is_classification_correct:
                correct_classifications += 1
            if is_rag_correct:
                correct_rag_decisions += 1
            
            # Visual indicators
            class_icon = "✅" if is_classification_correct else "❌"
            rag_icon = "✅" if is_rag_correct else "❌"
            
            print(f"  {class_icon} {rag_icon} [{message_type[:4]}|RAG:{should_use_rag}] \"{query[:45]}{'...' if len(query) > 45 else ''}\"")
    
    # Calculate accuracy
    classification_accuracy = (correct_classifications / total_tests) * 100
    rag_accuracy = (correct_rag_decisions / total_tests) * 100
    overall_accuracy = ((correct_classifications + correct_rag_decisions) / (total_tests * 2)) * 100
    
    print(f"\n📊 Test Results Summary:")
    print(f"Classification Accuracy: {correct_classifications}/{total_tests} ({classification_accuracy:.1f}%)")
    print(f"RAG Decision Accuracy: {correct_rag_decisions}/{total_tests} ({rag_accuracy:.1f}%)")
    print(f"Overall System Accuracy: {overall_accuracy:.1f}%")

def test_embedding_cache_performance():
    print('\n\n🚀 Testing Embedding Cache Performance')
    print('=' * 60)
    
    # Initialize RAG system
    print("Initializing RAG system with embedding cache...")
    rag = OptimizedContextualRAGSystem()
    
    # Test queries - some repeats to demonstrate cache hits
    test_queries = [
        "I'm concerned about crowdfunding compliance",
        "What are the authorization requirements?", 
        "I'm worried about regulatory risks",
        "I'm concerned about crowdfunding compliance",  # Repeat - should hit cache
        "How do investment limits work in EU regulation?",
        "What are the authorization requirements?",  # Repeat - should hit cache
        "I need guidance on cross-border crowdfunding",
        "I'm concerned about crowdfunding compliance",  # Another repeat
    ]
    
    print(f"\n⏱️  Testing {len(test_queries)} queries (including repeats)...")
    print("-" * 50)
    
    total_time = 0
    for i, query in enumerate(test_queries, 1):
        start_time = time.time()
        
        try:
            # Test RAG query
            result = rag.query(query)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            # Identify if this was likely a cache hit (very fast)
            cache_indicator = "🎯" if elapsed < 0.5 else "🔍"
            
            print(f"  {i:2d}. {cache_indicator} {elapsed:.3f}s - \"{query[:40]}{'...' if len(query) > 40 else ''}\"")
            
        except Exception as e:
            print(f"  {i:2d}. ❌ Error: {str(e)[:50]}...")
    
    # Show cache statistics
    print(f"\n📊 Performance Summary:")
    print(f"Total time: {total_time:.3f}s")
    print(f"Average per query: {total_time/len(test_queries):.3f}s")
    
    print(f"\n💾 Embedding Cache Statistics:")
    cache_stats = rag.get_embedding_cache_stats()
    embedding_cache = cache_stats.get('embedding_cache', {})
    print(f"  Cached embeddings: {embedding_cache.get('cached_embeddings', 'unknown')}")
    print(f"  Cache size: {embedding_cache.get('cache_size_mb', 'unknown')} MB")
    print(f"  Status: {embedding_cache.get('status', 'unknown')}")
    
    print(f"\n🎯 Cache Performance Notes:")
    print("  🔍 = Fresh embedding computation (slower)")
    print("  🎯 = Cache hit (much faster)")

if __name__ == "__main__":
    test_crowdfunding_agent_rag()
    test_embedding_cache_performance() 