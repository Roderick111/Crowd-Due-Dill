#!/usr/bin/env python3
"""
Debug script to test production Article 22 behavior
"""

import requests
import json

def test_production_article22():
    """Test Article 22 query on production to see the response format."""
    
    # Replace with your actual production domain
    production_url = "https://your-domain.com/api/query"
    
    query_data = {
        "query": "Tell me about Article 22 of the DSA"
    }
    
    try:
        print("🔍 Testing production Article 22 query...")
        print(f"URL: {production_url}")
        print(f"Query: {query_data['query']}")
        print("-" * 60)
        
        response = requests.post(
            production_url,
            headers={"Content-Type": "application/json"},
            json=query_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check response structure to see if we're using hybrid retrieval
            print("📊 Response Analysis:")
            print(f"Status Code: {response.status_code}")
            
            # Look for parallel hybrid indicators
            if 'search_strategy' in result:
                print(f"✅ Search Strategy: {result.get('search_strategy')}")
                print(f"✅ Total Results: {result.get('total_results', 0)}")
                
                if result.get('search_strategy') == 'parallel_hybrid':
                    vector_results = len(result.get('vector_results', []))
                    keyword_results = len(result.get('keyword_results', []))
                    print(f"✅ Vector Results: {vector_results}")
                    print(f"✅ Keyword Results: {keyword_results}")
                    
                    # Show query analysis
                    query_info = result.get('query_info', {})
                    print(f"✅ Query Type: {query_info.get('query_type')}")
                    print(f"✅ Is Precise: {query_info.get('is_precise_lookup')}")
                    
                    if keyword_results > 0:
                        print("🎯 GOOD: Keyword search is working!")
                        
                        # Show first keyword result
                        keyword_result = result['keyword_results'][0]
                        content = keyword_result.get('page_content', '')
                        if 'trusted flaggers' in content.lower():
                            print("✅ EXCELLENT: Found correct Article 22 content about trusted flaggers!")
                        else:
                            print("❌ PROBLEM: Keyword results don't contain trusted flaggers content")
                            print(f"Content preview: {content[:200]}...")
                    else:
                        print("❌ PROBLEM: No keyword results - hybrid search not working")
                else:
                    print(f"❌ PROBLEM: Not using parallel hybrid search (using: {result.get('search_strategy')})")
            else:
                print("❌ PROBLEM: No search_strategy in response - likely using old code")
                
                # Check for legacy format
                if 'chunks' in result:
                    chunks = result.get('chunks', [])
                    print(f"📝 Legacy format detected with {len(chunks)} chunks")
                    
                    if chunks:
                        first_chunk = chunks[0].get('content', '')
                        if 'trusted flaggers' in first_chunk.lower():
                            print("✅ Found correct Article 22 content in legacy format")
                        else:
                            print("❌ PROBLEM: Wrong Article 22 content in legacy format")
                            print(f"Content preview: {first_chunk[:200]}...")
            
            # Show full response for debugging
            print("\n" + "=" * 60)
            print("📋 Full Response Structure:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing production: {e}")

if __name__ == "__main__":
    test_production_article22() 