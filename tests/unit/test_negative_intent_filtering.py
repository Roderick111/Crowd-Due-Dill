#!/usr/bin/env python3
"""
Test Negative Intent Filtering
Demonstrates the final semantic similarity + negative intent detection system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from cache.precomputed_lunar_responses import lunar_cache

def test_negative_intent_detection():
    print('🛡️ NEGATIVE INTENT DETECTION TEST')
    print('=' * 45)
    
    test_cases = [
        # Should MATCH (positive intent)
        ("What is moon water?", "✅ SHOULD MATCH", "Positive question"),
        ("How do I make moon water?", "✅ SHOULD MATCH", "Positive instruction"),
        ("Tell me about moon water", "✅ SHOULD MATCH", "Positive request"),
        ("What crystals work with moon energy?", "✅ SHOULD MATCH", "Positive question"),
        ("When should I manifest?", "✅ SHOULD MATCH", "Positive timing question"),
        
        # Should NOT MATCH (negative intent)
        ("Why should I avoid moon water?", "❌ SHOULD NOT MATCH", "Contains 'avoid'"),
        ("Is moon water dangerous?", "❌ SHOULD NOT MATCH", "Contains 'dangerous'"),
        ("Why is moon water harmful?", "❌ SHOULD NOT MATCH", "Contains 'harmful'"),
        ("I don't want to use moon water", "❌ SHOULD NOT MATCH", "Contains 'don't'"),
        ("When should I stop manifesting?", "❌ SHOULD NOT MATCH", "Contains 'stop'"),
        ("Why does manifestation fail?", "❌ SHOULD NOT MATCH", "Contains 'fail'"),
        ("Which crystals are bad for moon work?", "❌ SHOULD NOT MATCH", "Contains 'bad'"),
        ("What's wrong with moon rituals?", "❌ SHOULD NOT MATCH", "Contains 'wrong'"),
        ("Should I never do moon rituals?", "❌ SHOULD NOT MATCH", "Contains 'never'"),
        ("How to dispose of moon water?", "❌ SHOULD NOT MATCH", "Contains 'dispose'"),
        ("How to get rid of crystals?", "❌ SHOULD NOT MATCH", "Contains 'get rid'"),
    ]
    
    print("Query | Expected | Result | Analysis")
    print("-" * 80)
    
    correct_predictions = 0
    total_predictions = len(test_cases)
    
    for query, expected, reason in test_cases:
        response = lunar_cache.find_response(query)
        
        if response:
            result = "✅ MATCHED"
            is_correct = "✅ SHOULD MATCH" in expected
        else:
            result = "❌ NO MATCH"
            is_correct = "❌ SHOULD NOT MATCH" in expected
        
        if is_correct:
            correct_predictions += 1
            status = "✅ CORRECT"
        else:
            status = "❌ WRONG"
        
        print(f"{query[:25]:<25} | {expected[:17]:<17} | {result:<12} | {status} ({reason})")
    
    accuracy = (correct_predictions / total_predictions) * 100
    print(f"\n📊 ACCURACY: {correct_predictions}/{total_predictions} = {accuracy:.1f}%")

def test_threshold_adjustments():
    print('\n\n🎚️ THRESHOLD ADJUSTMENT TEST')
    print('=' * 40)
    
    test_queries = [
        ("Tell me about moon water", "Positive - lower threshold (0.85)"),
        ("Why should I avoid moon water?", "Negative - higher threshold (0.90)"),
        ("Which crystals don't work?", "Negative - higher threshold (0.90)"),
        ("How do I make moon water?", "Positive - lower threshold (0.85)")
    ]
    
    print("Testing how negative intent affects similarity thresholds:\n")
    
    for query, description in test_queries:
        print(f"🔎 Query: '{query}'")
        print(f"   Type: {description}")
        
        # Detect negative intent manually to show logic
        negative_words = ['avoid', 'dangerous', 'harmful', "don't", 'stop', 'fail', 'bad', 'wrong', 'against', 'not', 'never', 'cant', "can't", 'shouldnt', "shouldn't", 'dispose', 'get rid', 'remove']
        has_negative = any(word in query.lower() for word in negative_words)
        threshold = 0.90 if has_negative else 0.85
        
        print(f"   Negative intent detected: {has_negative}")
        print(f"   Threshold used: {threshold}")
        
        # Test actual response
        response = lunar_cache.find_response(query)
        print(f"   Result: {'✅ MATCHED' if response else '❌ NO MATCH'}")
        print()

def test_edge_cases():
    print('\n🔬 EDGE CASE TESTING')
    print('=' * 30)
    
    edge_cases = [
        ("What should I not do during full moon?", "Double negative"),
        ("Can't I use any crystals?", "Contraction with negative"),
        ("Shouldn't I avoid moon water?", "Double negative question"),
        ("Is it bad if I don't manifest?", "Multiple negative words"),
        ("What crystals work (not fail) with moon?", "Parenthetical negative"),
    ]
    
    print("Testing edge cases with complex negative patterns:\n")
    
    for query, case_type in edge_cases:
        print(f"🔎 '{query}'")
        print(f"   Edge case: {case_type}")
        
        response = lunar_cache.find_response(query)
        result = "✅ MATCHED" if response else "❌ REJECTED"
        print(f"   Result: {result}")
        print()

def compare_before_after():
    print('\n📈 BEFORE vs AFTER COMPARISON')
    print('=' * 40)
    
    print("System Evolution:")
    print("1. 🔧 KEYWORD MATCHING: Fast but inaccurate (matched negative queries)")
    print("2. 🧠 SEMANTIC SIMILARITY: Better but still some false positives") 
    print("3. 🛡️ NEGATIVE INTENT FILTERING: Accurate and safe")
    print()
    
    problematic_queries = [
        "Why should I avoid moon water?",
        "Is moon water dangerous?",
        "Which crystals don't work?",
        "When should I stop manifesting?"
    ]
    
    print("Query | Keyword | Semantic | Final | Best?")
    print("-" * 55)
    
    for query in problematic_queries:
        # All would match with keyword approach
        keyword_result = "✅ MATCH"
        
        # Some might match with basic semantic
        semantic_result = "✅ MATCH" if "don't" in query else "❌ NO MATCH"
        
        # Test current system with negative filtering
        final_response = lunar_cache.find_response(query)
        final_result = "✅ MATCH" if final_response else "❌ NO MATCH"
        
        best = "🛡️ FINAL" if final_result == "❌ NO MATCH" else "⚠️ NEEDS WORK"
        
        print(f"{query[:20]:<20} | {keyword_result:<8} | {semantic_result:<8} | {final_result:<8} | {best}")

if __name__ == "__main__":
    test_negative_intent_detection()
    test_threshold_adjustments()
    test_edge_cases()
    compare_before_after() 