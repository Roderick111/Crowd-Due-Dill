#!/usr/bin/env python3
"""
Simple demonstration of Query Similarity Cache performance
"""

import time
from contextual_rag import OptimizedContextualRAGSystem

def demonstrate_cache():
    print('🎯 SIMPLE QUERY SIMILARITY CACHE DEMONSTRATION')
    print('=' * 60)

    # Initialize RAG with cache enabled
    print('Initializing RAG system with Query Similarity Cache...')
    rag = OptimizedContextualRAGSystem(enable_query_cache=True)

    # Test queries - similar but different wording
    queries = [
        "I feel anxious and restless during the full moon",
        "The full moon makes me feel uneasy and agitated", 
        "Why do I feel nervous when there is a full moon?",
        "Full moon energy is affecting my mood badly"
    ]

    print(f'\n⏱️  Testing {len(queries)} similar queries about moon anxiety...')
    print('-' * 50)

    times = []
    cache_hits = 0

    for i, query in enumerate(queries, 1):
        print(f'\n{i}. Query: "{query}"')
        
        start_time = time.time()
        try:
            response = rag.query(query)
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            # Determine cache status
            if elapsed < 2.0:
                status = '🎯 CACHE HIT (lightning fast!)'
                cache_hits += 1
            else:
                status = '🔍 CACHE MISS (full RAG processing)'
                
            print(f'   Result: {status}')
            print(f'   Time: {elapsed:.2f} seconds')
            print(f'   Response preview: {response[:80]}...')
            
        except Exception as e:
            print(f'   ❌ Error: {e}')
            times.append(0)

    # Performance summary
    print(f'\n📊 PERFORMANCE ANALYSIS:')
    print('=' * 40)
    print(f'Total queries: {len(queries)}')
    print(f'Cache hits: {cache_hits}')
    print(f'Cache hit rate: {(cache_hits/len(queries))*100:.1f}%')
    
    if times:
        avg_time = sum(times) / len(times)
        print(f'Average time per query: {avg_time:.2f}s')
        
        if cache_hits > 0:
            cache_miss_time = sum(t for t in times if t >= 2.0) / max(1, len(queries) - cache_hits)
            cache_hit_time = sum(t for t in times if t < 2.0) / max(1, cache_hits) if cache_hits > 0 else 0
            
            print(f'Average cache miss time: {cache_miss_time:.2f}s')
            print(f'Average cache hit time: {cache_hit_time:.2f}s')
            
            if cache_hit_time > 0:
                speedup = cache_miss_time / cache_hit_time
                print(f'Cache speedup: {speedup:.1f}x faster!')

    # Cache statistics
    print(f'\n💾 CACHE STATISTICS:')
    if hasattr(rag, 'query_cache') and rag.query_cache:
        summary = rag.query_cache.get_cache_summary()
        print(summary)
    else:
        print('Cache not available')

if __name__ == "__main__":
    demonstrate_cache() 