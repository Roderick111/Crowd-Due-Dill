#!/usr/bin/env python3
"""
Unit tests for refactored OptimizedContextualRAGSystem.

Tests the integration and functionality of the modular RAG system including:
- Component integration (DomainManager, StatsCollector)
- Query processing with multi-layer caching
- Domain-aware retrieval
- Error handling and edge cases
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from core.contextual_rag import OptimizedContextualRAGSystem
from core.domain_manager import DomainManager
from core.stats_collector import StatsCollector


class TestOptimizedContextualRAGSystemRefactored(unittest.TestCase):
    """Test suite for refactored OptimizedContextualRAGSystem."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Use temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.persist_directory = os.path.join(self.temp_dir, "test_chroma_db")
    
    def tearDown(self):
        """Clean up after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.contextual_rag.Chroma')
    @patch('core.contextual_rag.OpenAIEmbeddings')
    @patch('core.contextual_rag.ChatOpenAI')
    def test_initialization_default(self, mock_llm, mock_embeddings, mock_chroma):
        """Test default initialization of the RAG system."""
        # Mock the vectorstore to not exist
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Check that components are initialized
        self.assertIsInstance(rag.domain_manager, DomainManager)
        self.assertIsInstance(rag.stats_collector, StatsCollector)
        
        # Check default settings
        self.assertTrue(rag.enable_query_cache)
        self.assertTrue(rag.enable_precomputed)
        self.assertEqual(rag.persist_directory, self.persist_directory)
        
        # Check that domain manager has default domains
        self.assertEqual(rag.domain_manager.active_domains, ["lunar"])
    
    @patch('core.contextual_rag.Chroma')
    @patch('core.contextual_rag.OpenAIEmbeddings')
    @patch('core.contextual_rag.ChatOpenAI')
    def test_initialization_custom_domains(self, mock_llm, mock_embeddings, mock_chroma):
        """Test initialization with custom domains."""
        custom_domains = {"astrology", "crystals"}
        
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(
                persist_directory=self.persist_directory,
                active_domains=custom_domains
            )
        
        self.assertEqual(set(rag.domain_manager.active_domains), custom_domains)
    
    @patch('core.contextual_rag.Chroma')
    @patch('core.contextual_rag.OpenAIEmbeddings')
    @patch('core.contextual_rag.ChatOpenAI')
    @patch('core.contextual_rag.QuerySimilarityCache')
    def test_initialization_with_existing_vectorstore(self, mock_cache, mock_llm, mock_embeddings, mock_chroma):
        """Test initialization when vectorstore already exists."""
        # Mock existing vectorstore
        mock_vectorstore = Mock()
        mock_vectorstore._collection.count.return_value = 100
        mock_chroma.return_value = mock_vectorstore
        
        with patch('os.path.exists', return_value=True):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        self.assertEqual(rag.vectorstore, mock_vectorstore)
        mock_chroma.assert_called_once()
    
    def test_domain_management_delegation(self):
        """Test that domain management methods delegate to DomainManager."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock the domain manager
        rag.domain_manager = Mock()
        rag.domain_manager.enable_domain.return_value = True
        rag.domain_manager.disable_domain.return_value = True
        rag.domain_manager.get_status.return_value = {"active_domains": ["lunar"]}
        
        # Test delegation
        result = rag.enable_domain("astrology")
        self.assertTrue(result)
        rag.domain_manager.enable_domain.assert_called_once_with("astrology")
        
        result = rag.disable_domain("astrology")
        self.assertTrue(result)
        rag.domain_manager.disable_domain.assert_called_once_with("astrology")
        
        status = rag.get_domain_status()
        self.assertEqual(status["active_domains"], ["lunar"])
        rag.domain_manager.get_status.assert_called_once()
    
    def test_stats_collection_delegation(self):
        """Test that statistics methods delegate to StatsCollector."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock the stats collector
        rag.stats_collector = Mock()
        rag.stats_collector.get_comprehensive_stats.return_value = {"query_performance": {}}
        rag.stats_collector.get_performance_summary.return_value = "Test summary"
        
        # Test delegation
        stats = rag.get_stats()
        self.assertEqual(stats["query_performance"], {})
        rag.stats_collector.get_comprehensive_stats.assert_called_once()
        
        summary = rag.get_performance_summary()
        self.assertEqual(summary, "Test summary")
        rag.stats_collector.get_performance_summary.assert_called_once()
    
    @patch('core.contextual_rag.lunar_cache')
    def test_query_precomputed_hit(self, mock_lunar_cache):
        """Test query processing with precomputed hit."""
        mock_lunar_cache.find_response.return_value = "Precomputed response"
        
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock stats collector
        rag.stats_collector = Mock()
        
        result = rag.query("test question")
        
        self.assertEqual(result, "Precomputed response")
        mock_lunar_cache.find_response.assert_called_once_with("test question")
        rag.stats_collector.record_query.assert_called_once()
        
        # Check that it was recorded as precomputed
        call_args = rag.stats_collector.record_query.call_args
        self.assertEqual(call_args[0][0], 'precomputed')
    
    @patch('core.contextual_rag.lunar_cache')
    def test_query_cache_hit(self, mock_lunar_cache):
        """Test query processing with cache hit."""
        mock_lunar_cache.find_response.return_value = None  # No precomputed hit
        
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock query cache
        rag.query_cache = Mock()
        rag.query_cache.get_cached_response.return_value = ("Cached response", 0.9)
        
        # Mock stats collector
        rag.stats_collector = Mock()
        
        result = rag.query("test question")
        
        self.assertEqual(result, "Cached response")
        rag.query_cache.get_cached_response.assert_called_once_with("test question")
        rag.stats_collector.record_query.assert_called_once()
        
        # Check that it was recorded as cache
        call_args = rag.stats_collector.record_query.call_args
        self.assertEqual(call_args[0][0], 'cache')
    
    @patch('core.contextual_rag.lunar_cache')
    def test_query_rag_processing(self, mock_lunar_cache):
        """Test query processing with full RAG."""
        mock_lunar_cache.find_response.return_value = None  # No precomputed hit
        
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock query cache (no hit)
        rag.query_cache = Mock()
        rag.query_cache.get_cached_response.return_value = (None, 0.0)
        rag.query_cache.add_query_response = Mock()
        
        # Mock retrieval chain
        rag.retrieval_chain = Mock()
        rag.retrieval_chain.invoke.return_value = "RAG response"
        
        # Mock stats collector
        rag.stats_collector = Mock()
        
        result = rag.query("test question")
        
        self.assertEqual(result, "RAG response")
        rag.retrieval_chain.invoke.assert_called_once_with("test question")
        rag.query_cache.add_query_response.assert_called_once_with("test question", "RAG response")
        rag.stats_collector.record_query.assert_called_once()
        
        # Check that it was recorded as rag
        call_args = rag.stats_collector.record_query.call_args
        self.assertEqual(call_args[0][0], 'rag')
    
    @patch('core.contextual_rag.lunar_cache')
    def test_query_no_vectorstore(self, mock_lunar_cache):
        """Test query processing when no vectorstore is available."""
        mock_lunar_cache.find_response.return_value = None
        
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Ensure no vectorstore
        rag.vectorstore = None
        rag.retrieval_chain = None
        
        # Mock query cache (no hit)
        rag.query_cache = Mock()
        rag.query_cache.get_cached_response.return_value = (None, 0.0)
        
        result = rag.query("test question")
        
        self.assertIn("I don't have access to a knowledge base", result)
    
    def test_query_with_verbose(self):
        """Test query processing with verbose output."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock components
        rag.retrieval_chain = Mock()
        rag.retrieval_chain.invoke.return_value = "Test response"
        rag.stats_collector = Mock()
        rag.query_cache = Mock()
        rag.query_cache.get_cached_response.return_value = (None, 0.0)
        rag.query_cache.add_query_response = Mock()
        
        with patch('core.contextual_rag.lunar_cache') as mock_lunar_cache:
            mock_lunar_cache.find_response.return_value = None
            
            # Capture print output
            with patch('builtins.print') as mock_print:
                result = rag.query("test question", verbose=True)
            
            # Check that verbose output was printed
            mock_print.assert_called()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertTrue(any("Processing query" in call for call in print_calls))
    
    def test_add_documents_success(self):
        """Test successful document addition."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock documents
        from langchain_core.documents import Document
        docs = [
            Document(page_content="Test content 1", metadata={"domain": "lunar"}),
            Document(page_content="Test content 2", metadata={"domain": "astrology"})
        ]
        
        # Mock vectorstore creation
        with patch('core.contextual_rag.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            
            result = rag.add_documents(docs)
        
        self.assertTrue(result)
        mock_chroma.from_documents.assert_called_once()
        self.assertEqual(rag.vectorstore, mock_vectorstore)
    
    def test_add_documents_missing_domain_metadata(self):
        """Test document addition with missing domain metadata."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock documents without domain metadata
        from langchain_core.documents import Document
        docs = [
            Document(page_content="Test content", metadata={})
        ]
        
        with patch('core.contextual_rag.Chroma') as mock_chroma:
            mock_vectorstore = Mock()
            mock_chroma.from_documents.return_value = mock_vectorstore
            
            result = rag.add_documents(docs)
        
        # Should succeed and add default domain
        self.assertTrue(result)
        self.assertEqual(docs[0].metadata["domain"], "lunar")
    
    def test_add_documents_empty_list(self):
        """Test document addition with empty list."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        result = rag.add_documents([])
        
        self.assertFalse(result)
    
    def test_add_documents_error_handling(self):
        """Test document addition error handling."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        from langchain_core.documents import Document
        docs = [Document(page_content="Test", metadata={"domain": "lunar"})]
        
        # Mock Chroma to raise an exception
        with patch('core.contextual_rag.Chroma') as mock_chroma:
            mock_chroma.from_documents.side_effect = Exception("Database error")
            
            result = rag.add_documents(docs)
        
        self.assertFalse(result)
    
    def test_domain_change_triggers_chain_rebuild(self):
        """Test that domain changes trigger retrieval chain rebuild."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock vectorstore
        rag.vectorstore = Mock()
        rag.vectorstore.as_retriever.return_value = Mock()
        
        # Mock the setup method to track calls
        with patch.object(rag, '_setup_retrieval_chain') as mock_setup:
            rag.enable_domain("astrology")
            mock_setup.assert_called_once()
            
            mock_setup.reset_mock()
            rag.disable_domain("astrology")
            mock_setup.assert_called_once()
    
    def test_clear_caches(self):
        """Test cache clearing functionality."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock caches
        rag.query_cache = Mock()
        rag.query_cache.clear_cache = Mock()
        rag.stats_collector = Mock()
        rag.stats_collector.reset_query_stats = Mock()
        
        with patch('core.contextual_rag.lunar_cache') as mock_lunar_cache:
            mock_lunar_cache.clear_cache = Mock()
            
            rag.clear_caches()
            
            rag.query_cache.clear_cache.assert_called_once()
            mock_lunar_cache.clear_cache.assert_called_once()
            rag.stats_collector.reset_query_stats.assert_called_once()
    
    def test_clear_caches_with_errors(self):
        """Test cache clearing with errors."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock caches with errors
        rag.query_cache = Mock()
        rag.query_cache.clear_cache.side_effect = Exception("Cache error")
        rag.stats_collector = Mock()
        rag.stats_collector.reset_query_stats = Mock()
        
        with patch('core.contextual_rag.lunar_cache') as mock_lunar_cache:
            mock_lunar_cache.clear_cache.side_effect = Exception("Lunar cache error")
            
            # Should not raise exception
            rag.clear_caches()
            
            # Stats should still be reset
            rag.stats_collector.reset_query_stats.assert_called_once()
    
    def test_string_representations(self):
        """Test string representation methods."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        str_repr = str(rag)
        self.assertIn("OptimizedContextualRAGSystem", str_repr)
        self.assertIn("lunar", str_repr)
        
        repr_str = repr(rag)
        self.assertIn("OptimizedContextualRAGSystem", repr_str)
        self.assertIn("persist_directory", repr_str)
        self.assertIn("domains", repr_str)
    
    def test_query_error_handling(self):
        """Test query error handling."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(persist_directory=self.persist_directory)
        
        # Mock retrieval chain to raise error
        rag.retrieval_chain = Mock()
        rag.retrieval_chain.invoke.side_effect = Exception("Retrieval error")
        
        # Mock other components
        rag.query_cache = Mock()
        rag.query_cache.get_cached_response.return_value = (None, 0.0)
        rag.stats_collector = Mock()
        
        with patch('core.contextual_rag.lunar_cache') as mock_lunar_cache:
            mock_lunar_cache.find_response.return_value = None
            
            result = rag.query("test question")
            
            self.assertIn("I encountered an error", result)
            self.assertIn("Retrieval error", result)
    
    def test_cache_disabled_initialization(self):
        """Test initialization with caches disabled."""
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(
                persist_directory=self.persist_directory,
                enable_query_cache=False,
                enable_precomputed=False
            )
        
        self.assertIsNone(rag.query_cache)
        self.assertFalse(rag.enable_query_cache)
        self.assertFalse(rag.enable_precomputed)
    
    @patch('core.contextual_rag.lunar_cache')
    def test_query_with_caches_disabled(self, mock_lunar_cache):
        """Test query processing with caches disabled."""
        mock_lunar_cache.find_response.return_value = None
        
        with patch('os.path.exists', return_value=False):
            rag = OptimizedContextualRAGSystem(
                persist_directory=self.persist_directory,
                enable_query_cache=False,
                enable_precomputed=False
            )
        
        # Mock retrieval chain
        rag.retrieval_chain = Mock()
        rag.retrieval_chain.invoke.return_value = "RAG response"
        rag.stats_collector = Mock()
        
        result = rag.query("test question")
        
        self.assertEqual(result, "RAG response")
        # Should not call lunar cache when disabled
        mock_lunar_cache.find_response.assert_not_called()


if __name__ == "__main__":
    unittest.main() 