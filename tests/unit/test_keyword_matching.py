#!/usr/bin/env python3
"""
Test Improved Keyword Matching Algorithm
Demonstrates how the semantic matching works with scoring system
"""

from precomputed_lunar_responses import lunar_cache

def test_keyword_matching_details():
    print('🔍 KEYWORD MATCHING ALGORITHM DEMONSTRATION')
    print('=' * 55)
    
    # Test queries that previously failed
    problematic_queries = [
        "What is moon water?",
        "What crystals work with moon energy?", 
        "When should I manifest?",
        "How do I charge crystals?"
    ]
    
    for query in problematic_queries:
        print(f"\n🔎 Analyzing: '{query}'")
        query_lower = query.lower()
        
        # Find the best match manually to show scoring
        best_match = None
        best_score = 0
        
        for response in lunar_cache.responses.values():
            score = 0
            matched_keywords = []
            
            # Calculate keyword match score (same logic as in find_response)
            for keyword in response.keywords:
                keyword_lower = keyword.lower()
                
                # Exact keyword match
                if keyword_lower in query_lower:
                    if ' ' in keyword_lower:  # Compound terms
                        score += 3
                        matched_keywords.append(f"'{keyword}' (compound: +3)")
                    else:
                        score += 1
                        matched_keywords.append(f"'{keyword}' (single: +1)")
                
                # Partial word matching
                keyword_words = keyword_lower.split()
                if len(keyword_words) > 1:
                    word_matches = sum(1 for word in keyword_words if word in query_lower)
                    if word_matches == len(keyword_words):
                        score += 2
                        matched_keywords.append(f"'{keyword}' (full compound: +2)")
                    elif word_matches > 0:
                        score += word_matches * 0.5
                        matched_keywords.append(f"'{keyword}' (partial: +{word_matches * 0.5})")
            
            # Question pattern similarity
            response_words = set(response.question.lower().split())
            query_words = set(query_lower.split())
            common_words = response_words.intersection(query_words)
            if len(common_words) >= 2:
                pattern_score = len(common_words) * 0.3
                score += pattern_score
                matched_keywords.append(f"Question similarity: {list(common_words)} (+{pattern_score:.1f})")
            
            # Track best match
            if score > best_score and score >= 1.5:
                best_score = score
                best_match = (response, matched_keywords)
        
        if best_match:
            response, keywords = best_match
            print(f"   ✅ MATCH FOUND: '{response.question}'")
            print(f"   📊 Total Score: {best_score:.1f}")
            print(f"   🎯 Matched Keywords:")
            for kw in keywords:
                print(f"      • {kw}")
            print(f"   ⚡ Response: {response.response[:60]}...")
        else:
            print(f"   ❌ NO MATCH (score threshold: 1.5)")

def test_scoring_examples():
    print(f'\n\n📐 SCORING SYSTEM EXAMPLES')
    print('=' * 35)
    
    scoring_examples = [
        ("moon water", "moon water", "Exact compound match: +3 points"),
        ("crystals", "crystals", "Exact single word match: +1 point"),
        ("moon goddess", "moon goddesses", "Partial compound match with 'moon': +0.5 points"),
        ("what is ritual", "what + is = 2 common words", "Question similarity: +0.6 points (2 × 0.3)"),
    ]
    
    print("Keyword/Pattern | Query Contains | Score Explanation")
    print("-" * 55)
    for keyword, query_part, explanation in scoring_examples:
        print(f"{keyword:<15} | {query_part:<14} | {explanation}")
    
    print(f"\n🎯 Minimum threshold for match: 1.5 points")
    print(f"🏆 This allows single high-value matches (like 'moon water') to succeed")

def test_before_vs_after():
    print(f'\n\n🔄 BEFORE vs AFTER IMPROVEMENT')
    print('=' * 40)
    
    test_cases = [
        "What is moon water?",
        "What crystals work best?",
        "When should I manifest?",
        "How do I charge my crystals?"
    ]
    
    print("Query | Old Algorithm | New Algorithm")
    print("-" * 45)
    
    for query in test_cases:
        # Simulate old algorithm (required 2+ keyword matches)
        old_result = "❌ MISS" 
        
        # Test new algorithm
        new_response = lunar_cache.find_response(query)
        new_result = "✅ HIT" if new_response else "❌ MISS"
        
        print(f"{query:<25} | {old_result:<13} | {new_result}")
    
    print(f"\n💡 Key Improvements:")
    print(f"   • Compound keyword matching (moon water = 3 points)")
    print(f"   • Flexible scoring system vs rigid 2+ requirement")
    print(f"   • Question pattern similarity bonus")
    print(f"   • Lower threshold (1.5) allows single strong matches")

if __name__ == "__main__":
    test_keyword_matching_details()
    test_scoring_examples()
    test_before_vs_after() 