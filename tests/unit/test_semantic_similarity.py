#!/usr/bin/env python3
"""
Test Semantic Similarity in Pre-computed Responses
Shows detailed similarity scores and why semantic matching is superior
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from cache.precomputed_lunar_responses import lunar_cache
import numpy as np

def test_semantic_similarity_scores():
    print('🧠 SEMANTIC SIMILARITY DETAILED ANALYSIS')
    print('=' * 55)
    
    test_cases = [
        # Positive queries (should match)
        ("What is moon water?", "SHOULD MATCH"),
        ("Tell me about moon water", "SHOULD MATCH"),
        ("How do I make moon water?", "SHOULD MATCH"),
        ("What crystals work best with moon energy?", "SHOULD MATCH"),
        ("Which crystals are most effective for moon work?", "SHOULD MATCH"),
        ("When should I manifest during moon phases?", "SHOULD MATCH"),
        
        # Negative queries (should NOT match)
        ("Why should I avoid moon water?", "SHOULD NOT MATCH"),
        ("Is moon water dangerous?", "SHOULD NOT MATCH"),
        ("How to dispose of moon water?", "SHOULD NOT MATCH"),
        ("Which crystals don't work with moon energy?", "SHOULD NOT MATCH"),
        ("Should I avoid crystals during full moon?", "SHOULD NOT MATCH"),
        ("When should I stop manifesting?", "SHOULD NOT MATCH"),
        ("Why does manifestation fail during moon phases?", "SHOULD NOT MATCH"),
    ]
    
    for query, expectation in test_cases:
        print(f"\n🔎 Query: '{query}'")
        print(f"   Expected: {expectation}")
        
        # Get query embedding
        query_embedding = lunar_cache._get_embedding(query)
        
        # Find best match with scores
        best_match = None
        best_similarity = 0
        similarity_details = []
        
        for response in lunar_cache.responses.values():
            if not response.embedding:
                continue
                
            similarity = lunar_cache._cosine_similarity(query_embedding, response.embedding)
            similarity_details.append((response.question, similarity))
            
            if similarity > best_similarity:
                best_similarity = similarity
                if similarity >= lunar_cache.similarity_threshold:
                    best_match = response
        
        # Sort by similarity for display
        similarity_details.sort(key=lambda x: x[1], reverse=True)
        
        # Show top 3 matches
        print(f"   🎯 Top similarities:")
        for i, (question, sim) in enumerate(similarity_details[:3]):
            threshold_status = "✅ ABOVE" if sim >= lunar_cache.similarity_threshold else "❌ BELOW"
            print(f"      {i+1}. {sim:.3f} {threshold_status} threshold - '{question[:40]}...'")
        
        # Result
        if best_match:
            print(f"   ✅ MATCHED: '{best_match.question}' (similarity: {best_similarity:.3f})")
            is_correct = "CORRECT" if "SHOULD NOT MATCH" not in expectation else "⚠️ FALSE POSITIVE"
            print(f"   📊 Result: {is_correct}")
        else:
            print(f"   ❌ NO MATCH (best: {best_similarity:.3f}, threshold: {lunar_cache.similarity_threshold})")
            is_correct = "CORRECT" if "SHOULD NOT MATCH" in expectation else "⚠️ FALSE NEGATIVE"
            print(f"   📊 Result: {is_correct}")

def compare_keyword_vs_semantic():
    print('\n\n🆚 KEYWORD MATCHING vs SEMANTIC SIMILARITY')
    print('=' * 55)
    
    problematic_cases = [
        "Why should I avoid moon water?",
        "Is moon water dangerous?", 
        "Which crystals don't work with moon energy?",
        "When should I stop manifesting?"
    ]
    
    print("Query | Keyword Match | Semantic Match | Better?")
    print("-" * 65)
    
    for query in problematic_cases:
        # Simulate old keyword approach (would match based on keywords)
        has_keywords = any(keyword in query.lower() for keyword in ['moon water', 'crystals', 'manifest'])
        keyword_result = "✅ MATCH" if has_keywords else "❌ NO MATCH"
        
        # Test semantic approach
        query_embedding = lunar_cache._get_embedding(query)
        best_similarity = 0
        for response in lunar_cache.responses.values():
            if response.embedding:
                sim = lunar_cache._cosine_similarity(query_embedding, response.embedding)
                best_similarity = max(best_similarity, sim)
        
        semantic_result = "✅ MATCH" if best_similarity >= lunar_cache.similarity_threshold else "❌ NO MATCH"
        
        # Determine which is better (for negative intent, NO MATCH is correct)
        better = "🧠 SEMANTIC" if semantic_result == "❌ NO MATCH" else "⚠️ KEYWORD"
        
        print(f"{query[:25]:<25} | {keyword_result:<13} | {semantic_result:<14} | {better}")

def test_threshold_sensitivity():
    print('\n\n🎚️ THRESHOLD SENSITIVITY ANALYSIS')
    print('=' * 45)
    
    test_queries = [
        ("What is moon water?", "positive"),
        ("Tell me about moon water", "positive"),
        ("Why should I avoid moon water?", "negative"),
        ("Is moon water dangerous?", "negative")
    ]
    
    thresholds = [0.75, 0.80, 0.85, 0.90, 0.95]
    
    print("Query Type | " + " | ".join(f"Thresh {t}" for t in thresholds))
    print("-" * 80)
    
    for query, query_type in test_queries:
        query_embedding = lunar_cache._get_embedding(query)
        
        # Find best similarity for this query
        best_similarity = 0
        for response in lunar_cache.responses.values():
            if response.embedding:
                sim = lunar_cache._cosine_similarity(query_embedding, response.embedding)
                best_similarity = max(best_similarity, sim)
        
        # Test at different thresholds
        results = []
        for threshold in thresholds:
            match = "✅" if best_similarity >= threshold else "❌"
            results.append(f"{match} {best_similarity:.2f}")
        
        query_display = f"{query[:15]}... ({query_type})"
        print(f"{query_display:<25} | " + " | ".join(f"{r:<10}" for r in results))
    
    print(f"\n💡 Recommended threshold: 0.85")
    print(f"   • Catches positive variations like 'Tell me about moon water'")
    print(f"   • Rejects negative intents like 'Why avoid moon water?'")

def suggest_optimizations():
    print('\n\n🚀 FURTHER OPTIMIZATIONS')
    print('=' * 35)
    
    print("1. 🚫 NEGATIVE INTENT DETECTION:")
    print("   • Add blacklist: ['avoid', 'dangerous', 'harmful', 'don\\'t', 'stop', 'fail']")
    print("   • If query contains negative words, increase threshold or reject")
    print()
    print("2. 📈 ADAPTIVE THRESHOLDS:")
    print("   • High-confidence keywords: 0.80 threshold")
    print("   • Medium-confidence keywords: 0.85 threshold")  
    print("   • Low-confidence keywords: 0.90 threshold")
    print()
    print("3. 🔄 HYBRID APPROACH:")
    print("   • Step 1: Exact question matching (instant)")
    print("   • Step 2: Semantic similarity (0.85+ threshold)")
    print("   • Step 3: Negative intent filtering")
    print()
    print("4. 📊 CONTINUOUS LEARNING:")
    print("   • Track false positives/negatives")
    print("   • Adjust thresholds based on user feedback")
    print("   • A/B test different similarity models")

if __name__ == "__main__":
    test_semantic_similarity_scores()
    compare_keyword_vs_semantic() 
    test_threshold_sensitivity()
    suggest_optimizations() 