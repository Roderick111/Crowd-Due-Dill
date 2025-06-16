#!/usr/bin/env python3
"""
Test script for Query Similarity Cache Performance

This demonstrates the dramatic performance improvements achieved by caching
semantically similar queries in the RAG system.
"""

import time
import os
from dotenv import load_dotenv
from contextual_rag import OptimizedContextualRAGSystem

# Load environment variables
load_dotenv()

def test_query_similarity_cache():
    """Test the Query Similarity Cache with various similar and different queries."""
    print('🎯 Testing Query Similarity Cache Performance')
    print('=' * 60)
    
    # Initialize RAG system with query cache enabled
    print("Initializing RAG system with Query Similarity Cache...")
    rag = OptimizedContextualRAGSystem(enable_query_cache=True)
    
    # Test queries organized by similarity groups
    test_groups = {
        "Moon Emotions Group": [
            "I feel anxious and restless during the full moon",
            "The full moon makes me feel restless and anxious",
            "Why do I feel uneasy when there's a full moon?",
            "Full moon energy is making me feel agitated"
        ],
        
        "Spiritual Practices Group": [
            "What are some good spiritual practices for beginners?",
            "Can you suggest spiritual practices for someone new to this?",
            "What spiritual exercises should I start with?",
            "How do I begin my spiritual practice journey?"
        ],
        
        "Lunar Phases Group": [
            "Explain the different phases of the moon",
            "What are the moon phases and their meanings?",
            "Tell me about lunar cycles and their significance",
            "How do moon phases work and what do they mean?"
        ],
        
        "Unique Queries": [
            "What does Mercury retrograde mean?",
            "How to cleanse crystals properly?",
            "What are chakras and how do they work?",
            "Explain the concept of energy healing"
        ]
    }
    
    print(f"\n⏱️  Testing {sum(len(queries) for queries in test_groups.values())} queries across {len(test_groups)} similarity groups...")
    print("-" * 60)
    
    total_time_without_cache = 0
    total_time_with_cache = 0
    cache_hits = 0
    total_queries = 0
    
    for group_name, queries in test_groups.items():
        print(f"\n📂 {group_name}")
        print("-" * 40)
        
        group_start_time = time.time()
        
        for i, query in enumerate(queries, 1):
            total_queries += 1
            
            start_time = time.time()
            
            try:
                # Execute RAG query
                result = rag.query(query)
                
                elapsed = time.time() - start_time
                
                # Determine if this was a cache hit (very fast response)
                is_cache_hit = elapsed < 2.0  # Cache hits should be under 2 seconds
                if is_cache_hit:
                    cache_hits += 1
                    total_time_with_cache += elapsed
                    cache_indicator = "🎯 CACHE HIT"
                else:
                    total_time_without_cache += elapsed
                    total_time_with_cache += elapsed
                    cache_indicator = "🔍 CACHE MISS"
                
                print(f"  {i:2d}. {cache_indicator} {elapsed:.3f}s - \"{query[:45]}{'...' if len(query) > 45 else ''}\"")
                
                # Brief pause to see the progression
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  {i:2d}. ❌ Error: {str(e)[:50]}...")
        
        group_time = time.time() - group_start_time
        print(f"      Group total: {group_time:.2f}s")
    
    # Performance Analysis
    print(f"\n📊 Query Similarity Cache Performance Analysis:")
    print(f"=" * 60)
    print(f"Total queries processed: {total_queries}")
    print(f"Cache hits: {cache_hits}")
    print(f"Cache hit rate: {(cache_hits/total_queries)*100:.1f}%")
    print(f"Total time with cache: {total_time_with_cache:.2f}s")
    print(f"Average time per query: {total_time_with_cache/total_queries:.2f}s")
    
    if cache_hits > 0:
        cache_miss_queries = total_queries - cache_hits
        estimated_time_without_cache = total_time_without_cache + (cache_hits * 6.0)  # Assume 6s per cache miss
        time_saved = estimated_time_without_cache - total_time_with_cache
        print(f"Estimated time without cache: {estimated_time_without_cache:.2f}s")
        print(f"Time saved by caching: {time_saved:.2f}s ({(time_saved/estimated_time_without_cache)*100:.1f}%)")
        print(f"Performance improvement: {estimated_time_without_cache/total_time_with_cache:.1f}x faster")
    
    # Show cache statistics
    print(f"\n💾 Cache Statistics:")
    if hasattr(rag, 'query_cache') and rag.query_cache:
        summary = rag.query_cache.get_cache_summary()
        print(summary)
    
    print(f"\n🎯 Cache Performance Notes:")
    print("  🔍 = Cache miss (first time processing)")
    print("  🎯 = Cache hit (retrieved from similarity cache)")
    print("  Similarity threshold: 0.85 (high quality matches only)")


def test_similarity_thresholds():
    """Test different similarity thresholds to show cache behavior."""
    print('\n\n🔬 Testing Different Similarity Thresholds')
    print('=' * 60)
    
    # Test with different thresholds
    thresholds = [0.95, 0.85, 0.75]
    test_queries = [
        "I feel anxious during the full moon",
        "The full moon makes me feel restless",
        "Full moon energy affects my mood",
        "Why does the full moon impact my emotions?"
    ]
    
    for threshold in thresholds:
        print(f"\n🎯 Testing with similarity threshold: {threshold}")
        print("-" * 40)
        
        # Create new RAG instance with specific threshold
        rag = OptimizedContextualRAGSystem(enable_query_cache=True)
        rag.query_cache.similarity_threshold = threshold
        rag.query_cache.clear_cache()  # Start fresh
        
        cache_hits = 0
        for i, query in enumerate(test_queries, 1):
            start_time = time.time()
            result = rag.query(query)
            elapsed = time.time() - start_time
            
            if elapsed < 2.0:  # Cache hit
                cache_hits += 1
                print(f"  {i}. 🎯 HIT  {elapsed:.3f}s - {query[:40]}...")
            else:
                print(f"  {i}. 🔍 MISS {elapsed:.3f}s - {query[:40]}...")
        
        hit_rate = (cache_hits / len(test_queries)) * 100
        print(f"  Cache hit rate: {cache_hits}/{len(test_queries)} ({hit_rate:.1f}%)")


if __name__ == "__main__":
    test_query_similarity_cache()
    test_similarity_thresholds() 