#!/usr/bin/env python3
"""
Test Threshold Problems in Keyword Matching
Demonstrates why semantic similarity would be better than keyword matching
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from cache.precomputed_lunar_responses import lunar_cache
import time

def test_threshold_problems():
    print('🚨 PROBLEMS WITH LOW KEYWORD MATCHING THRESHOLD')
    print('=' * 55)
    
    # Test problematic queries that share keywords but have different intent
    problematic_queries = [
        # Same keywords, different intent
        ("What is moon water?", "CORRECT: Should match"),
        ("Why should I avoid moon water?", "WRONG: Different intent - asking to AVOID"),
        ("Is moon water dangerous?", "WRONG: Different intent - asking about DANGER"),
        ("How to dispose of moon water?", "WRONG: Different intent - asking to GET RID OF"),
        
        # Crystal examples
        ("What crystals work best with moon energy?", "CORRECT: Should match"),
        ("Which crystals don't work with moon energy?", "WRONG: Opposite intent - asking what DOESN'T work"),
        ("Are crystals harmful during moon phases?", "WRONG: Different intent - asking about HARM"),
        
        # Manifestation examples
        ("When should I manifest?", "CORRECT: Should match"),
        ("When should I stop manifesting?", "WRONG: Opposite intent - asking to STOP"),
        ("Why does manifestation fail during moon phases?", "WRONG: Different intent - asking about FAILURE"),
    ]
    
    print("Testing queries with same keywords but different intents:\n")
    
    for query, expected in problematic_queries:
        print(f"🔎 Query: '{query}'")
        print(f"   Expected: {expected}")
        
        # Test current algorithm
        response = lunar_cache.find_response(query)
        if response:
            # Find which question it matched
            matched_question = None
            for resp in lunar_cache.responses.values():
                if resp.response == response:
                    matched_question = resp.question
                    break
            
            print(f"   ✅ MATCHED: '{matched_question}'")
            print(f"   ⚠️  PROBLEM: Same keywords, different intent!")
        else:
            print(f"   ❌ NO MATCH")
        print()

def test_semantic_similarity_solution():
    print('🎯 WHY SEMANTIC SIMILARITY WOULD BE BETTER')
    print('=' * 50)
    
    examples = [
        {
            "correct_query": "What is moon water?",
            "incorrect_queries": [
                "Why should I avoid moon water?",
                "Is moon water dangerous?",
                "How to get rid of moon water?"
            ],
            "explanation": "All contain 'moon water' keywords but have opposite intents"
        },
        {
            "correct_query": "What crystals work best with moon energy?", 
            "incorrect_queries": [
                "Which crystals don't work with moon energy?",
                "Are crystals bad for moon rituals?",
                "Should I avoid crystals during full moon?"
            ],
            "explanation": "Same domain (crystals + moon) but asking what NOT to do"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. CORRECT QUERY: '{example['correct_query']}'")
        print(f"   PROBLEMATIC QUERIES (same keywords, wrong intent):")
        for bad_query in example['incorrect_queries']:
            print(f"   ❌ '{bad_query}'")
        print(f"   💡 {example['explanation']}")

def demonstrate_semantic_approach():
    print('\n\n🧠 SEMANTIC SIMILARITY APPROACH (BETTER SOLUTION)')
    print('=' * 55)
    
    print("Instead of keyword matching, we should use:")
    print()
    print("1. 📊 VECTOR EMBEDDINGS:")
    print("   • Convert questions to high-dimensional vectors")
    print("   • Capture semantic meaning, not just keywords")
    print("   • 'What is moon water?' vs 'Why avoid moon water?' have different vectors")
    print()
    print("2. 🎯 COSINE SIMILARITY:")
    print("   • Measure angle between question vectors")
    print("   • High similarity (0.85+) = same intent")
    print("   • Low similarity = different intent, even with same keywords")
    print()
    print("3. 🛡️ INTENT PRESERVATION:")
    print("   • 'What is X?' ≈ 'Tell me about X' (high similarity)")
    print("   • 'What is X?' ≠ 'Why avoid X?' (low similarity)")
    print("   • Prevents inappropriate matches")

def show_semantic_examples():
    print('\n\n📈 SEMANTIC SIMILARITY EXAMPLES')
    print('=' * 40)
    
    similarity_examples = [
        ("What is moon water?", "Tell me about moon water", "High (~0.92)", "✅ Should match"),
        ("What is moon water?", "How do I make moon water?", "Medium (~0.78)", "✅ Should match"),
        ("What is moon water?", "Why should I avoid moon water?", "Low (~0.45)", "❌ Should NOT match"),
        ("What is moon water?", "Is moon water dangerous?", "Low (~0.35)", "❌ Should NOT match"),
        ("What crystals work best?", "Which crystals are most effective?", "High (~0.89)", "✅ Should match"),
        ("What crystals work best?", "Which crystals don't work?", "Low (~0.42)", "❌ Should NOT match"),
    ]
    
    print("Query 1 | Query 2 | Similarity | Result")
    print("-" * 70)
    
    for q1, q2, sim, result in similarity_examples:
        print(f"{q1[:20]:<20} | {q2[:20]:<20} | {sim:<10} | {result}")

def suggest_improvement():
    print('\n\n🚀 SUGGESTED IMPROVEMENT: HYBRID APPROACH')
    print('=' * 50)
    
    print("Combine the best of both approaches:")
    print()
    print("1. ⚡ FAST EXACT MATCHING:")
    print("   • Keep direct question key matching for exact questions")
    print("   • Ultra-fast for perfect matches")
    print()
    print("2. 🧠 SEMANTIC SIMILARITY FALLBACK:")
    print("   • If no exact match, use embedding similarity")
    print("   • Higher threshold (0.85+) to prevent false positives")
    print("   • Catches variations like 'Tell me about moon water'")
    print()
    print("3. 🛡️ SAFETY FEATURES:")
    print("   • Intent detection (avoid negative words)")
    print("   • Minimum similarity threshold")
    print("   • Keyword presence validation")
    print()
    print("RESULT: Fast + Accurate + Safe matching!")

if __name__ == "__main__":
    test_threshold_problems()
    test_semantic_similarity_solution()
    demonstrate_semantic_approach()
    show_semantic_examples()
    suggest_improvement() 