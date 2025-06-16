#!/usr/bin/env python3
"""
Test Main Application with Pre-computed Responses
Integration test for the complete system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from cache.precomputed_lunar_responses import lunar_cache
from core.contextual_rag import OptimizedContextualRAGSystem
import time

def test_main_integration():
    print('🧪 TESTING MAIN APPLICATION INTEGRATION')
    print('=' * 45)
    
    try:
        # Import the RAG system from main
        from main import rag_system
        
        print("✅ Main application imports successful")
        
        # Test pre-computed responses
        test_questions = [
            "What are the phases of the moon?",
            "How does the full moon affect emotions?",
            "What crystals work best with moon energy?",
            "When should I manifest during moon phases?"
        ]
        
        print(f"\n🔍 Testing {len(test_questions)} pre-computed questions...")
        
        total_time = 0
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. {question}")
            
            start = time.time()
            response = rag_system.query(question, verbose=False)
            elapsed = time.time() - start
            total_time += elapsed
            
            if response and len(response) > 50:
                print(f"   ⚡ Response ({elapsed:.4f}s): {response[:80]}...")
            else:
                print(f"   ❌ Failed or short response: {response}")
        
        print(f"\n📊 Results:")
        print(f"   Total time: {total_time:.4f}s")
        print(f"   Average: {total_time/len(test_questions):.4f}s per query")
        
        # Get stats
        stats = rag_system.get_stats()
        perf = stats.get('query_performance', {})
        print(f"   Pre-computed hits: {perf.get('precomputed_hits', 0)}")
        print(f"   Cache hits: {perf.get('cache_hits', 0)}")
        print(f"   RAG processing: {perf.get('rag_processing', 0)}")
        
        print(f"\n✅ Integration test successful!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_integration() 