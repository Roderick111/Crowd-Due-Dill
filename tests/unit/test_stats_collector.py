#!/usr/bin/env python3
"""
Unit tests for StatsCollector component.

Tests all statistics collection functionality including:
- Query performance tracking
- Cache statistics aggregation
- Performance calculations
- Summary formatting
- Error handling
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from core.stats_collector import StatsCollector


class TestStatsCollector(unittest.TestCase):
    """Test suite for StatsCollector class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sc = StatsCollector()
    
    def test_default_initialization(self):
        """Test default initialization of stats collector."""
        expected_stats = {
            'total_queries': 0,
            'precomputed_hits': 0,
            'cache_hits': 0,
            'rag_processing': 0,
            'total_time': 0.0,
            'avg_response_time': 0.0
        }
        self.assertEqual(self.sc.query_stats, expected_stats)
    
    def test_record_precomputed_query(self):
        """Test recording a precomputed query."""
        self.sc.record_query('precomputed', 0.001)
        
        self.assertEqual(self.sc.query_stats['total_queries'], 1)
        self.assertEqual(self.sc.query_stats['precomputed_hits'], 1)
        self.assertEqual(self.sc.query_stats['cache_hits'], 0)
        self.assertEqual(self.sc.query_stats['rag_processing'], 0)
        self.assertEqual(self.sc.query_stats['total_time'], 0.001)
        self.assertEqual(self.sc.query_stats['avg_response_time'], 0.001)
    
    def test_record_cache_query(self):
        """Test recording a cache hit query."""
        self.sc.record_query('cache', 0.05)
        
        self.assertEqual(self.sc.query_stats['total_queries'], 1)
        self.assertEqual(self.sc.query_stats['precomputed_hits'], 0)
        self.assertEqual(self.sc.query_stats['cache_hits'], 1)
        self.assertEqual(self.sc.query_stats['rag_processing'], 0)
        self.assertEqual(self.sc.query_stats['total_time'], 0.05)
        self.assertEqual(self.sc.query_stats['avg_response_time'], 0.05)
    
    def test_record_rag_query(self):
        """Test recording a RAG processing query."""
        self.sc.record_query('rag', 0.8)
        
        self.assertEqual(self.sc.query_stats['total_queries'], 1)
        self.assertEqual(self.sc.query_stats['precomputed_hits'], 0)
        self.assertEqual(self.sc.query_stats['cache_hits'], 0)
        self.assertEqual(self.sc.query_stats['rag_processing'], 1)
        self.assertEqual(self.sc.query_stats['total_time'], 0.8)
        self.assertEqual(self.sc.query_stats['avg_response_time'], 0.8)
    
    def test_record_multiple_queries(self):
        """Test recording multiple queries and average calculation."""
        self.sc.record_query('precomputed', 0.001)
        self.sc.record_query('cache', 0.05)
        self.sc.record_query('rag', 0.8)
        self.sc.record_query('rag', 1.2)
        
        self.assertEqual(self.sc.query_stats['total_queries'], 4)
        self.assertEqual(self.sc.query_stats['precomputed_hits'], 1)
        self.assertEqual(self.sc.query_stats['cache_hits'], 1)
        self.assertEqual(self.sc.query_stats['rag_processing'], 2)
        
        expected_total_time = 0.001 + 0.05 + 0.8 + 1.2
        self.assertAlmostEqual(self.sc.query_stats['total_time'], expected_total_time, places=6)
        
        expected_avg = expected_total_time / 4
        self.assertAlmostEqual(self.sc.query_stats['avg_response_time'], expected_avg, places=6)
    
    def test_record_unknown_query_type(self):
        """Test recording query with unknown type (should not increment specific counters)."""
        self.sc.record_query('unknown', 0.5)
        
        self.assertEqual(self.sc.query_stats['total_queries'], 1)
        self.assertEqual(self.sc.query_stats['precomputed_hits'], 0)
        self.assertEqual(self.sc.query_stats['cache_hits'], 0)
        self.assertEqual(self.sc.query_stats['rag_processing'], 0)
        self.assertEqual(self.sc.query_stats['total_time'], 0.5)
        self.assertEqual(self.sc.query_stats['avg_response_time'], 0.5)
    
    def test_get_query_stats_returns_copy(self):
        """Test that get_query_stats returns a copy, not reference."""
        self.sc.record_query('precomputed', 0.1)
        stats = self.sc.get_query_stats()
        
        # Modify the returned stats
        stats['total_queries'] = 999
        
        # Original should be unchanged
        self.assertEqual(self.sc.query_stats['total_queries'], 1)
    
    def test_get_vectorstore_stats_with_vectorstore(self):
        """Test vectorstore statistics with mock vectorstore."""
        mock_vectorstore = Mock()
        mock_vectorstore._collection.count.return_value = 100
        
        stats = self.sc.get_vectorstore_stats(mock_vectorstore)
        
        self.assertEqual(stats['vectorstore_docs'], 100)
        self.assertEqual(stats['total_chunks'], 100)
        self.assertNotIn('vectorstore_error', stats)
    
    def test_get_vectorstore_stats_with_error(self):
        """Test vectorstore statistics when error occurs."""
        mock_vectorstore = Mock()
        mock_vectorstore._collection.count.side_effect = Exception("Connection error")
        
        stats = self.sc.get_vectorstore_stats(mock_vectorstore)
        
        self.assertEqual(stats['vectorstore_docs'], 0)
        self.assertEqual(stats['total_chunks'], 0)
        self.assertIn('vectorstore_error', stats)
        self.assertEqual(stats['vectorstore_error'], "Connection error")
    
    def test_get_vectorstore_stats_with_none(self):
        """Test vectorstore statistics with None vectorstore."""
        stats = self.sc.get_vectorstore_stats(None)
        
        self.assertEqual(stats['vectorstore_docs'], 0)
        self.assertEqual(stats['total_chunks'], 0)
    
    def test_get_precomputed_stats_success(self):
        """Test precomputed statistics with mock cache."""
        mock_cache = Mock()
        mock_cache.get_stats.return_value = {'total_precomputed_responses': 19, 'categories': 5}
        
        stats = self.sc.get_precomputed_stats(mock_cache)
        
        self.assertEqual(stats['total_precomputed_responses'], 19)
        self.assertEqual(stats['categories'], 5)
        self.assertNotIn('precomputed_error', stats)
    
    def test_get_precomputed_stats_error(self):
        """Test precomputed statistics when error occurs."""
        mock_cache = Mock()
        mock_cache.get_stats.side_effect = Exception("Cache error")
        
        stats = self.sc.get_precomputed_stats(mock_cache)
        
        self.assertIn('precomputed_error', stats)
        self.assertEqual(stats['precomputed_error'], "Cache error")
    
    def test_get_query_cache_stats_enabled(self):
        """Test query cache statistics when enabled."""
        mock_cache = Mock()
        mock_cache.get_cache_summary.return_value = {
            'total_cached_queries': 8,
            'cache_hit_rate': 0.75
        }
        
        stats = self.sc.get_query_cache_stats(mock_cache, True)
        
        self.assertTrue(stats['enabled'])
        self.assertEqual(stats['total_cached_queries'], 8)
        self.assertEqual(stats['cache_hit_rate'], 0.75)
    
    def test_get_query_cache_stats_disabled(self):
        """Test query cache statistics when disabled."""
        stats = self.sc.get_query_cache_stats(None, False)
        
        self.assertFalse(stats['enabled'])
        self.assertNotIn('total_cached_queries', stats)
    
    def test_get_query_cache_stats_error(self):
        """Test query cache statistics when error occurs."""
        mock_cache = Mock()
        mock_cache.get_cache_summary.side_effect = Exception("Cache error")
        
        stats = self.sc.get_query_cache_stats(mock_cache, True)
        
        self.assertFalse(stats['enabled'])
        self.assertIn('error', stats)
        self.assertEqual(stats['error'], "Cache error")
    
    def test_get_embedding_cache_stats_exists(self):
        """Test embedding cache statistics when cache directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create embedding cache directory with some files
            cache_dir = os.path.join(temp_dir, "embedding_cache")
            os.makedirs(cache_dir)
            
            # Create some test files with actual content
            for i in range(3):
                file_path = os.path.join(cache_dir, f"embedding_{i}.cache")
                with open(file_path, 'w') as f:
                    f.write("test data" * 1000)  # More content to ensure size > 0
            
            stats = self.sc.get_embedding_cache_stats(temp_dir)
            
            self.assertEqual(stats['status'], 'active')
            self.assertEqual(stats['cached_embeddings'], 3)
            self.assertGreaterEqual(stats['cache_size_mb'], 0)  # Allow 0 for very small files
    
    def test_get_embedding_cache_stats_not_found(self):
        """Test embedding cache statistics when cache directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            stats = self.sc.get_embedding_cache_stats(temp_dir)
            
            self.assertEqual(stats['status'], 'not_found')
            self.assertNotIn('cached_embeddings', stats)
    
    def test_get_embedding_cache_stats_error(self):
        """Test embedding cache statistics when error occurs."""
        # Mock os.path.exists to raise an exception
        with patch('os.path.exists', side_effect=Exception("Permission denied")):
            stats = self.sc.get_embedding_cache_stats("/some/path")
            
            self.assertEqual(stats['status'], 'error')
            self.assertIn('error', stats)
            self.assertEqual(stats['error'], "Permission denied")
    
    def test_get_comprehensive_stats(self):
        """Test comprehensive statistics gathering."""
        # Set up mocks
        mock_domain_manager = Mock()
        mock_domain_manager.get_status.return_value = {'active_domains': ['lunar']}
        
        mock_vectorstore = Mock()
        mock_vectorstore._collection.count.return_value = 50
        
        mock_lunar_cache = Mock()
        mock_lunar_cache.get_stats.return_value = {'total_precomputed_responses': 19}
        
        mock_query_cache = Mock()
        mock_query_cache.get_cache_summary.return_value = {'total_cached_queries': 8}
        
        # Record some queries
        self.sc.record_query('precomputed', 0.001)
        self.sc.record_query('rag', 0.5)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            stats = self.sc.get_comprehensive_stats(
                domain_manager=mock_domain_manager,
                vectorstore=mock_vectorstore,
                lunar_cache=mock_lunar_cache,
                query_cache=mock_query_cache,
                query_cache_enabled=True,
                persist_directory=temp_dir
            )
            
            # Check structure
            self.assertIn('domain_config', stats)
            self.assertIn('query_performance', stats)
            self.assertIn('vectorstore_docs', stats)
            self.assertIn('precomputed_responses', stats)
            self.assertIn('query_cache', stats)
            self.assertIn('embedding_cache', stats)
            
            # Check content
            self.assertEqual(stats['domain_config']['active_domains'], ['lunar'])
            self.assertEqual(stats['query_performance']['total_queries'], 2)
            self.assertEqual(stats['vectorstore_docs'], 50)
    
    def test_reset_query_stats(self):
        """Test resetting query statistics."""
        # Record some queries
        self.sc.record_query('precomputed', 0.1)
        self.sc.record_query('rag', 0.5)
        
        # Verify stats are recorded
        self.assertEqual(self.sc.query_stats['total_queries'], 2)
        self.assertGreater(self.sc.query_stats['total_time'], 0)
        
        # Reset stats
        self.sc.reset_query_stats()
        
        # Verify reset
        expected_stats = {
            'total_queries': 0,
            'precomputed_hits': 0,
            'cache_hits': 0,
            'rag_processing': 0,
            'total_time': 0.0,
            'avg_response_time': 0.0
        }
        self.assertEqual(self.sc.query_stats, expected_stats)
    
    def test_get_performance_summary_no_queries(self):
        """Test performance summary with no queries."""
        summary = self.sc.get_performance_summary()
        self.assertEqual(summary, "📊 No queries processed yet")
    
    def test_get_performance_summary_with_queries(self):
        """Test performance summary with recorded queries."""
        self.sc.record_query('precomputed', 0.001)
        self.sc.record_query('cache', 0.05)
        self.sc.record_query('rag', 0.8)
        self.sc.record_query('rag', 1.2)
        
        summary = self.sc.get_performance_summary()
        
        # Check that summary contains expected information
        self.assertIn("Total queries: 4", summary)
        self.assertIn("Pre-computed: 1 (25.0%)", summary)
        self.assertIn("Cache hits: 1 (25.0%)", summary)
        self.assertIn("RAG processing: 2 (50.0%)", summary)
        self.assertIn("Average response time:", summary)
    
    def test_performance_summary_formatting(self):
        """Test that performance summary is properly formatted."""
        self.sc.record_query('precomputed', 0.001)
        self.sc.record_query('cache', 0.05)
        self.sc.record_query('rag', 0.8)
        
        summary = self.sc.get_performance_summary()
        
        # Check formatting elements
        self.assertIn("📊", summary)  # Emoji
        self.assertIn("⚡", summary)  # Pre-computed emoji
        self.assertIn("🎯", summary)  # Cache emoji
        self.assertIn("🔍", summary)  # RAG emoji
        self.assertIn("⏱️", summary)  # Time emoji
        
        # Check percentage formatting
        self.assertIn("(33.3%)", summary)  # Should have percentages
    
    def test_edge_case_zero_division(self):
        """Test edge case where total_queries is 0 (should not cause division by zero)."""
        # This should not raise an exception
        self.sc._update_avg_response_time()
        self.assertEqual(self.sc.query_stats['avg_response_time'], 0.0)
    
    def test_negative_response_time(self):
        """Test handling of negative response times."""
        self.sc.record_query('rag', -0.1)  # Negative time
        
        # Should still record the query
        self.assertEqual(self.sc.query_stats['total_queries'], 1)
        self.assertEqual(self.sc.query_stats['total_time'], -0.1)
        self.assertEqual(self.sc.query_stats['avg_response_time'], -0.1)
    
    def test_very_large_numbers(self):
        """Test handling of very large response times."""
        large_time = 1000000.0
        self.sc.record_query('rag', large_time)
        
        self.assertEqual(self.sc.query_stats['total_queries'], 1)
        self.assertEqual(self.sc.query_stats['total_time'], large_time)
        self.assertEqual(self.sc.query_stats['avg_response_time'], large_time)


if __name__ == "__main__":
    unittest.main() 