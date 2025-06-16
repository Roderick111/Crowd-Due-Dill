#!/usr/bin/env python3
"""
Test Pre-computed Lunar Responses System
Demonstrates instant responses for common lunar knowledge questions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import time
from cache.precomputed_lunar_responses import lunar_cache

def test_precomputed_responses():
    print('⚡ PRE-COMPUTED LUNAR RESPONSES TEST')
    print('=' * 45)
    
    # Test various types of lunar questions
    test_queries = [
        # Basic lunar knowledge
        "What are the phases of the moon?",
        "How long does each moon phase last?",
        "When is the next full moon?",
        
        # Emotional and spiritual effects
        "How does the full moon affect emotions?",
        "Why do I feel anxious during full moons?",
        "Why do I feel more intuitive during certain moon phases?",
        
        # Practical applications
        "When should I manifest during moon phases?",
        "What is a moon ritual?",
        "How do I charge crystals in moonlight?",
        "What is moon water and how do I make it?",
        
        # Crystals and tools
        "What crystals work best with moon energy?",
        
        # Physical effects
        "How does the moon affect sleep?",
        "How do moon phases affect plants and gardening?",
        
        # Special events
        "What does a lunar eclipse mean spiritually?",
        "What is a blue moon and why is it special?",
        "What is the dark moon and how is it different from new moon?",
        
        # Advanced topics
        "How can I connect with moon goddesses?",
        "What moon sign am I and what does it mean?",
        "How do I release negative energy during the waning moon?",
        "How do I track moon phases and lunar cycles?",
        
        # Variations to test keyword matching
        "Tell me about lunar phases",
        "Crystal charging under moonlight",
        "Full moon anxiety help",
        "Manifestation timing with moon",
        
        # Questions that should NOT match (cache miss)
        "What's the weather like today?",
        "How do I cook pasta?",
        "What is artificial intelligence?"
    ]
    
    total_time = 0
    hits = 0
    misses = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i:2d}. {query}")
        
        start = time.time()
        response = lunar_cache.find_response(query)
        elapsed = time.time() - start
        total_time += elapsed
        
        if response:
            print(f"    ⚡ HIT  ({elapsed:.4f}s): {response[:80]}...")
            hits += 1
        else:
            print(f"    ❌ MISS ({elapsed:.4f}s): No pre-computed response")
            misses += 1
    
    # Performance summary
    print(f'\n📊 PERFORMANCE SUMMARY')
    print(f'=' * 30)
    print(f'Total queries: {len(test_queries)}')
    print(f'Cache hits: {hits}')
    print(f'Cache misses: {misses}')
    print(f'Hit rate: {(hits/len(test_queries)*100):.1f}%')
    print(f'Total time: {total_time:.4f}s')
    print(f'Average response time: {(total_time/len(test_queries)):.4f}s')
    print(f'Average hit time: {(total_time/hits if hits > 0 else 0):.4f}s')

def test_cache_statistics():
    print(f'\n\n📈 CACHE STATISTICS')
    print(f'=' * 25)
    
    stats = lunar_cache.get_stats()
    
    print(f"Total pre-computed responses: {stats['total_precomputed_responses']}")
    print(f"Total cache hits: {stats['total_cache_hits']}")
    print(f"Cache file size: {stats['cache_file_size']}")
    print(f"Most popular question: {stats['most_popular_question'] or 'None'}")
    print(f"Most popular hits: {stats['most_popular_hits']}")
    
    print(f"\n📂 Response Categories:")
    categories = stats['categories']
    for category, count in categories.items():
        print(f"  {category.replace('_', ' ').title()}: {count} responses")

def test_category_listing():
    print(f'\n\n📚 ALL PRE-COMPUTED QUESTIONS BY CATEGORY')
    print(f'=' * 50)
    
    categories = lunar_cache.list_categories()
    
    for category, questions in categories.items():
        print(f"\n📂 {category.upper().replace('_', ' ')}:")
        for i, question in enumerate(questions, 1):
            print(f"   {i}. {question}")

if __name__ == "__main__":
    test_precomputed_responses()
    test_cache_statistics()
    test_category_listing()
    
    print(f'\n\n✨ BENEFITS OF PRE-COMPUTED RESPONSES:')
    print(f'• Instant answers (0.001-0.01s) for common questions')
    print(f'• Perfect consistency for frequently asked lunar topics')
    print(f'• Reduces load on LLM and vector database')
    print(f'• Shaman Esoteric Guru style maintained across responses')
    print(f'• Covers top 20 most common lunar knowledge questions')
    print(f'• Fallback to similarity cache and RAG for other queries') 