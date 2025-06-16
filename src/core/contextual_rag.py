#!/usr/bin/env python3
"""
Optimized Contextual RAG System

Clean, production-ready RAG system with:
- Domain-aware retrieval
- Resilience management
- Performance monitoring
- Clean logging
"""

import os
import time
import chromadb
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .stats_collector import StatsCollector
from .resilience_manager import resilience_manager
from src.utils.logger import logger


class OptimizedContextualRAGSystem:
    """
    Streamlined RAG system with domain-aware retrieval and resilience.
    
    Features:
    - Direct chunk retrieval for chatbot integration
    - Multi-domain document filtering  
    - Circuit breaker protection
    - Health monitoring
    - Clean logging
    """
    
    def __init__(self, 
                 chroma_path: str = "data/chroma_db",
                 collection_name: str = "contextual_rag_collection",
                 domain_manager = None):
        """Initialize the RAG system."""
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.domain_manager = domain_manager
        
        # Initialize components
        self.stats_collector = StatsCollector()
        self.embeddings = None
        self.chroma_client = None
        self.vectorstore = None
        
        # Setup system
        self._setup_embeddings()
        self._setup_chroma_client()
        self._setup_vectorstore()
        
        # Log system ready status
        if self.domain_manager:
            active_count = len(self.domain_manager.get_active_domains())
            logger.system_ready(f"RAG System ready - {active_count} domains active")
        else:
            logger.system_ready("RAG System ready - no domain filtering")
    
    def _setup_embeddings(self):
        """Initialize OpenAI embeddings with resilience."""
        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                show_progress_bar=False,
                max_retries=3,
                timeout=30.0
            )
            
            # Register with resilience manager
            resilience_manager.register_openai_health_check(self.embeddings)
            
            logger.debug_openai("OpenAI embeddings initialized with resilience")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {e}")
            logger.warning("RAG system will run in limited mode without embeddings")
            self.embeddings = None
    
    def _setup_chroma_client(self):
        """Initialize ChromaDB client with resilience."""
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            
            # Register with resilience manager
            resilience_manager.register_chromadb_health_check(self.chroma_client)
            
            logger.debug_chromadb("ChromaDB client initialized with resilience")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            self.chroma_client = None
    
    def _setup_vectorstore(self):
        """Initialize vectorstore with HNSW optimization."""
        if not self.embeddings or not self.chroma_client:
            logger.warning("Cannot initialize vectorstore - missing dependencies")
            return
            
        try:
            # Check if collection exists
            existing_collections = [col.name for col in self.chroma_client.list_collections()]
            
            if self.collection_name in existing_collections:
                collection = self.chroma_client.get_collection(name=self.collection_name)
                count = collection.count()
                logger.debug_chromadb(f"Loaded existing collection: {count} documents")
            else:
                # Create new collection with metadata and HNSW optimization
                collection = self._create_optimized_collection()
            
            # Wrap with LangChain
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
        except Exception as e:
            logger.debug_chromadb(f"Error setting up vectorstore: {e}")
            self._setup_fallback_vectorstore()
    
    def _create_optimized_collection(self):
        """Create new collection with HNSW optimization and metadata."""
        from datetime import datetime
        
        collection_metadata = {
            "version": "2.1.0",
            "created": datetime.now().isoformat(),
            "embedding_model": "text-embedding-3-small",
            "description": "Esoteric AI knowledge base with domain-aware RAG",
            "domains": "lunar,ifs,astrology,crystals,numerology,tarot",
            "hnsw_config": "optimized",
            "last_updated": datetime.now().isoformat(),
            "system": "esoteric_vectors"
        }
        
        collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata=collection_metadata,
            configuration={
                "hnsw": {
                    "space": "cosine",
                    "ef_search": 100,
                    "ef_construction": 200,
                    "max_neighbors": 16,
                    "num_threads": 4
                }
            }
        )
        
        logger.debug_chromadb(f"Created new collection with HNSW optimization v{collection_metadata['version']}")
        return collection
    
    def _setup_fallback_vectorstore(self):
        """Setup fallback vectorstore if main setup fails."""
        if os.path.exists(self.chroma_path):
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.chroma_path,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
                count = self.vectorstore._collection.count()
                logger.debug_chromadb(f"Fallback vectorstore: {count} documents")
            except Exception as e:
                logger.error(f"Fallback vectorstore failed: {e}")
                self.vectorstore = None
        else:
            logger.warning("No vectorstore found")
    
    def query(self, query_text: str, k: int = 4) -> Dict[str, Any]:
        """
        Query the RAG system with domain filtering and resilience.
        
        Args:
            query_text: The user's query
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary containing response, chunks, and metadata
        """
        start_time = time.time()
        
        # Check system availability
        if not self.vectorstore:
            return self._create_error_response(
                "Vector search is not available. Please check embeddings configuration.",
                start_time, "error"
            )
        
        try:
            # Get domain filtering
            active_domains, domain_filter = self._get_domain_filter()
            
            # Retrieve documents
            docs = self._retrieve_documents(query_text, k, domain_filter)
            
            # Handle no results
            if not docs:
                return self._handle_no_results(active_domains, domain_filter, start_time)
            
            # Process successful results
            return self._process_results(docs, active_domains, start_time)
            
        except Exception as e:
            logger.error(f"RAG query error: {str(e)}")
            return self._create_error_response(
                "I encountered an error while searching for information.",
                start_time, "error", str(e)
            )
    
    def _get_domain_filter(self):
        """Get active domains and create filter."""
        active_domains = []
        domain_filter = None
        
        if self.domain_manager:
            domain_status = self.domain_manager.get_status()
            active_domains = domain_status.get("active_domains", [])
            
            if active_domains:
                domain_filter = {"domain": {"$in": active_domains}}
                logger.debug(f"Applying domain filter: {domain_filter}")
        
        return active_domains, domain_filter
    
    def _retrieve_documents(self, query_text: str, k: int, domain_filter: Optional[Dict]):
        """Retrieve documents with optimization and resilience."""
        # Standard retrieval
        if domain_filter:
            docs = self.vectorstore.similarity_search(query_text, k=k, filter=domain_filter)
        else:
            docs = self.vectorstore.similarity_search(query_text, k=k)
        
        # Try optimized ChromaDB query if available
        if (hasattr(self.vectorstore, '_collection') and 
            self.vectorstore._collection and 
            self.embeddings):
            
            try:
                docs = self._optimized_chromadb_query(query_text, k, domain_filter)
            except Exception as e:
                logger.debug_optimization(f"ChromaDB optimization failed, using fallback: {e}")
        
        return docs
    
    def _optimized_chromadb_query(self, query_text: str, k: int, domain_filter: Optional[Dict]):
        """Execute optimized ChromaDB query with resilience."""
        # Generate embedding with resilience
        def generate_embedding():
            return self.embeddings.embed_query(query_text)
        
        query_embedding = resilience_manager.execute_with_openai_resilience(generate_embedding)
        
        # Use ChromaDB's optimized query
        chroma_results = self.vectorstore._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=domain_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Convert to LangChain Document format
        docs = []
        if chroma_results and chroma_results.get('documents'):
            for i, doc_text in enumerate(chroma_results['documents'][0]):
                metadata = chroma_results.get('metadatas', [[]])[0][i] if chroma_results.get('metadatas') else {}
                docs.append(Document(page_content=doc_text, metadata=metadata))
            
            logger.debug_optimization("Used optimized ChromaDB query with include parameters")
        
        return docs
    
    def _handle_no_results(self, active_domains: List[str], domain_filter: Optional[Dict], start_time: float):
        """Handle case when no documents are found."""
        response_time = time.time() - start_time
        
        if domain_filter:
            logger.domain_blocked(active_domains)
            return {
                "response": f"I currently don't have information about that topic in my active knowledge areas. My current focus areas are: {', '.join(active_domains)}.",
                "chunks": [],
                "metadata": {
                    "total_chunks": 0,
                    "response_time": response_time,
                    "query_type": "domain_blocked"
                }
            }
        else:
            return {
                "response": "I couldn't find relevant information to answer your question.",
                "chunks": [],
                "metadata": {
                    "total_chunks": 0,
                    "response_time": response_time,
                    "query_type": "rag"
                }
            }
    
    def _process_results(self, docs: List[Document], active_domains: List[str], start_time: float):
        """Process successful retrieval results."""
        response_time = time.time() - start_time
        
        # Count domains in retrieved docs
        doc_domains = set()
        if self.domain_manager:
            for doc in docs:
                doc_domain = doc.metadata.get('domain', 'unknown')
                doc_domains.add(doc_domain)
        
        # Log retrieval success
        logger.rag_retrieval(len(docs), list(doc_domains))
        
        # Record performance stats
        if self.stats_collector:
            self.stats_collector.record_query('rag', response_time)
        
        # Prepare chunks info
        chunks_info = []
        for i, doc in enumerate(docs):
            chunks_info.append({
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata,
                "chunk_id": i + 1
            })
        
        return {
            "response": f"Found {len(docs)} relevant chunks for context.",
            "chunks": chunks_info,
            "metadata": {
                "total_chunks": len(docs),
                "response_time": response_time,
                "domains_searched": list(doc_domains) if doc_domains else active_domains,
                "query_type": "rag"
            }
        }
    
    def _create_error_response(self, message: str, start_time: float, query_type: str, error: str = None):
        """Create standardized error response."""
        response_time = time.time() - start_time
        metadata = {
            "total_chunks": 0,
            "response_time": response_time,
            "query_type": query_type
        }
        if error:
            metadata["error"] = error
        
        return {
            "response": message,
            "chunks": [],
            "metadata": metadata
        }
    
    # Batch operations
    def add_documents_batch(self, documents, batch_size: int = 100):
        """Add documents in batches with progress tracking."""
        if not self.vectorstore:
            logger.error("Cannot add documents - vectorstore not available")
            return False
        
        try:
            total_docs = len(documents)
            logger.debug(f"Adding {total_docs} documents in batches of {batch_size}")
            
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                self.vectorstore.add_documents(batch)
                logger.debug(f"Added batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size}")
            
            logger.command_executed(f"Added {total_docs} documents successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in batch addition: {e}")
            return False
    
    # System management
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        stats = {
            'query_performance': self.stats_collector.get_query_stats(),
        }
        
        # Add vectorstore stats
        stats.update(self.stats_collector.get_vectorstore_stats(self.vectorstore))
        
        # Add resilience stats
        resilience_stats = resilience_manager.get_health_summary()
        stats.update(resilience_stats)
        
        # Add domain status
        if self.domain_manager:
            stats['domain_config'] = self.domain_manager.get_status()
        else:
            stats['domain_config'] = {'status': 'disabled'}
        
        return stats
    
    def get_domain_status(self) -> Dict[str, Any]:
        """Get domain manager status."""
        if self.domain_manager:
            return self.domain_manager.get_status()
        return {"active_domains": [], "available_domains": []}
    
    def enable_domain(self, domain: str) -> bool:
        """Enable a domain."""
        return self.domain_manager.enable_domain(domain) if self.domain_manager else False
    
    def disable_domain(self, domain: str) -> bool:
        """Disable a domain."""
        return self.domain_manager.disable_domain(domain) if self.domain_manager else False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        try:
            if hasattr(self.vectorstore, '_collection') and self.vectorstore._collection:
                collection = self.vectorstore._collection
                
                info = {
                    'name': collection.name,
                    'count': collection.count(),
                    'metadata': getattr(collection, 'metadata', {}),
                }
                
                # Add health metrics
                health_metrics = self.stats_collector._get_collection_health(collection)
                info['health'] = health_metrics
                
                return info
            else:
                return {'error': 'Collection not available'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def clear_caches(self):
        """Clear all caches."""
        self.stats_collector.reset_query_stats()
        logger.command_executed("Caches cleared")
    
    def __str__(self) -> str:
        """String representation."""
        domains = self.domain_manager.get_active_domains() if self.domain_manager else []
        return f"OptimizedContextualRAGSystem(domains={domains})" 