#!/usr/bin/env python3
"""
Q&A Cache for Esoteric Vectors

Clean Q&A caching system with:
- Semantic similarity search
- Domain-aware filtering
- Resilience integration
- Clean logging
"""

import os
import time
import chromadb
from typing import Dict, Any, List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from core.resilience_manager import resilience_manager
from utils.logger import logger


class QACache:
    """
    Clean Q&A cache system for fast response retrieval.
    
    Features:
    - Semantic similarity search for Q&A pairs
    - Domain-aware filtering
    - Circuit breaker protection
    - Performance tracking
    - Clean logging
    """
    
    def __init__(self, 
                 chroma_path: str = "data/chroma_db/qa_cache",
                 collection_name: str = "qa_cache_collection",
                 similarity_threshold: float = 0.75):
        """Initialize Q&A cache."""
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        
        # Performance tracking
        self.stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'total_response_time': 0.0
        }
        
        # Initialize components
        self.embeddings = None
        self.chroma_client = None
        self.vectorstore = None
        
        # Setup system
        self._setup_embeddings()
        self._setup_chroma_client()
        self._setup_vectorstore()
        
        # Log initialization
        if self.vectorstore:
            count = self._get_qa_count()
            logger.system_ready(f"Q&A Cache: {count} question-answer pairs loaded")
        else:
            logger.warning("Q&A Cache: Failed to initialize")
    
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
            
            logger.debug_openai("Q&A Cache: OpenAI embeddings initialized")
            
        except Exception as e:
            logger.error(f"Q&A Cache: Failed to initialize embeddings: {e}")
            self.embeddings = None
    
    def _setup_chroma_client(self):
        """Initialize ChromaDB client with resilience."""
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            
            # Register with resilience manager
            resilience_manager.register_chromadb_health_check(self.chroma_client)
            
            logger.debug_chromadb("Q&A Cache: ChromaDB client initialized")
            
        except Exception as e:
            logger.error(f"Q&A Cache: Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
    
    def _setup_vectorstore(self):
        """Initialize vectorstore for Q&A cache."""
        if not self.embeddings or not self.chroma_client:
            logger.warning("Q&A Cache: Cannot initialize vectorstore - missing dependencies")
            return
            
        try:
            # Check if collection exists
            existing_collections = [col.name for col in self.chroma_client.list_collections()]
            
            if self.collection_name not in existing_collections:
                # Create new collection
                self._create_qa_collection()
            
            # Wrap with LangChain
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            
            logger.debug_chromadb("Q&A Cache: Vectorstore initialized")
            
        except Exception as e:
            logger.error(f"Q&A Cache: Failed to setup vectorstore: {e}")
            self.vectorstore = None
    
    def _create_qa_collection(self):
        """Create new Q&A collection with metadata."""
        from datetime import datetime
        
        collection_metadata = {
            "version": "1.3.0",
            "created": datetime.now().isoformat(),
            "embedding_model": "text-embedding-3-small",
            "description": "Q&A cache for esoteric knowledge with question-to-question semantic matching",
            "type": "qa_cache",
            "strategy": "question_embedding_question_matching",
            "domains": "lunar,ifs,astrology,crystals,numerology,tarot",
            "hnsw_config": "qa_optimized",
            "last_updated": datetime.now().isoformat(),
            "system": "esoteric_vectors",
            "similarity_threshold": str(self.similarity_threshold)
        }
        
        collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata=collection_metadata
        )
        
        logger.debug_chromadb(f"Q&A Cache: Created new collection v{collection_metadata['version']}")
        return collection
    
    def _get_qa_count(self) -> int:
        """Get total number of Q&A pairs."""
        try:
            if self.vectorstore and hasattr(self.vectorstore, '_collection'):
                return self.vectorstore._collection.count()
            return 0
        except Exception:
            return 0
    
    def search_qa(self, query: str, active_domains: List[str] = None, k: int = 3) -> Optional[Dict[str, Any]]:
        """
        Search for similar Q&A pairs with domain filtering.
        
        Args:
            query: User's question
            active_domains: List of active domains for filtering
            k: Number of results to retrieve
            
        Returns:
            Best matching Q&A pair if similarity above threshold, None otherwise
        """
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        try:
            if not self.vectorstore:
                logger.debug("Q&A Cache: Vectorstore not available")
                return None
            
            # Create domain filter if domains specified
            domain_filter = None
            if active_domains:
                domain_filter = {"domain": {"$in": active_domains}}
                logger.debug_optimization(f"Q&A Cache: Applying domain filter: {domain_filter}")
            
            # Search for similar questions (now questions are embedded, not answers)
            if domain_filter:
                docs = self.vectorstore.similarity_search_with_score(query, k=k, filter=domain_filter)
            else:
                docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            if not docs:
                logger.debug("Q&A Cache: No similar questions found")
                return None
            
            # Get best match
            best_doc, similarity_score = docs[0]
            
            # Convert distance to similarity (ChromaDB returns distance, we want similarity)
            similarity = 1 - similarity_score
            
            # Check if similarity meets threshold
            if similarity < self.similarity_threshold:
                logger.debug(f"Q&A Cache: Best similarity {similarity:.3f} below threshold {self.similarity_threshold}")
                return None
            
            # Record cache hit
            self.stats['cache_hits'] += 1
            response_time = time.time() - start_time
            self.stats['total_response_time'] += response_time
            
            # Extract Q&A data from metadata
            metadata = best_doc.metadata
            result = {
                'question': best_doc.page_content,
                'answer': metadata.get('answer', ''),
                'domain': metadata.get('domain', 'unknown'),
                'source': metadata.get('source', 'unknown'),
                'similarity': similarity,
                'qa_id': metadata.get('qa_id', 'unknown'),
                'response_time': response_time
            }
            
            logger.debug_optimization(f"Q&A Cache: Hit with similarity {similarity:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Q&A Cache search error: {e}")
            return None
    
    def add_qa_pair(self, question: str, answer: str, domain: str, source: str = "manual", qa_id: str = None) -> bool:
        """Add a new Q&A pair to the cache."""
        try:
            if not self.vectorstore:
                logger.error("Q&A Cache: Cannot add pair - vectorstore not available")
                return False
            
            from datetime import datetime
            import uuid
            
            # Generate ID if not provided
            if not qa_id:
                qa_id = str(uuid.uuid4())
            
            # Create document with QUESTION as content and ANSWER in metadata
            metadata = {
                'answer': answer,
                'domain': domain,
                'source': source,
                'qa_id': qa_id,
                'created': datetime.now().isoformat()
            }
            
            # Add to vectorstore (question is the content, answer is in metadata)
            self.vectorstore.add_texts(
                texts=[question],
                metadatas=[metadata],
                ids=[qa_id]
            )
            
            logger.debug(f"Q&A Cache: Added pair for domain '{domain}'")
            return True
            
        except Exception as e:
            logger.error(f"Q&A Cache: Failed to add pair: {e}")
            return False
    
    def _add_documents_batch(self, qa_pairs: List[Dict[str, str]], batch_size: int = 50) -> bool:
        """
        Add multiple Q&A pairs in batches for optimal performance.
        
        Args:
            qa_pairs: List of dicts with keys: question, answer, domain, source, qa_id (optional)
            batch_size: Number of pairs to add per batch
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.vectorstore:
                logger.error("Q&A Cache: Cannot add batch - vectorstore not available")
                return False
            
            from datetime import datetime
            import uuid
            
            total_pairs = len(qa_pairs)
            logger.debug(f"Q&A Cache: Adding {total_pairs} pairs in batches of {batch_size}")
            
            for i in range(0, total_pairs, batch_size):
                batch = qa_pairs[i:i + batch_size]
                
                # Prepare batch data
                texts = []
                metadatas = []
                ids = []
                
                for pair in batch:
                    # Generate ID if not provided
                    qa_id = pair.get('qa_id') or str(uuid.uuid4())
                    
                    metadata = {
                        'answer': pair['answer'],
                        'domain': pair['domain'],
                        'source': pair.get('source', 'batch'),
                        'qa_id': qa_id,
                        'created': datetime.now().isoformat()
                    }
                    
                    texts.append(pair['question'])
                    metadatas.append(metadata)
                    ids.append(qa_id)
                
                # Add batch to vectorstore
                self.vectorstore.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                logger.debug(f"Q&A Cache: Added batch {i//batch_size + 1}/{(total_pairs + batch_size - 1)//batch_size}")
            
            logger.command_executed(f"Q&A Cache: Added {total_pairs} pairs successfully")
            return True
            
        except Exception as e:
            logger.error(f"Q&A Cache: Error in batch addition: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Q&A cache statistics."""
        total_qa_pairs = self._get_qa_count()
        hit_rate = (self.stats['cache_hits'] / self.stats['total_queries'] * 100) if self.stats['total_queries'] > 0 else 0
        avg_response_time = (self.stats['total_response_time'] / self.stats['total_queries']) if self.stats['total_queries'] > 0 else 0
        
        return {
            'total_qa_pairs': total_qa_pairs,
            'total_queries': self.stats['total_queries'],
            'cache_hits': self.stats['cache_hits'],
            'hit_rate': hit_rate,
            'avg_response_time': avg_response_time,
            'similarity_threshold': self.similarity_threshold
        }
    
    def clear_cache(self):
        """Clear the Q&A cache."""
        try:
            if self.chroma_client and self.collection_name:
                # Delete and recreate collection
                try:
                    self.chroma_client.delete_collection(name=self.collection_name)
                except Exception:
                    pass  # Collection might not exist
                
                self._create_qa_collection()
                
                # Reinitialize vectorstore
                self._setup_vectorstore()
                
                # Reset stats
                self.stats = {
                    'total_queries': 0,
                    'cache_hits': 0,
                    'total_response_time': 0.0
                }
                
                logger.command_executed("Q&A cache cleared")
                return True
            else:
                logger.error("Q&A Cache: Cannot clear - client not available")
                return False
                
        except Exception as e:
            logger.error(f"Q&A Cache: Failed to clear: {e}")
            return False
    
    def get_domain_stats(self) -> Dict[str, int]:
        """Get Q&A pairs count by domain."""
        try:
            if not self.vectorstore or not hasattr(self.vectorstore, '_collection'):
                return {}
            
            # Get all documents with metadata
            collection = self.vectorstore._collection
            results = collection.get(include=["metadatas"])
            
            domain_counts = {}
            if results and results.get('metadatas'):
                for metadata in results['metadatas']:
                    domain = metadata.get('domain', 'unknown')
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            return domain_counts
            
        except Exception as e:
            logger.debug(f"Q&A Cache: Failed to get domain stats: {e}")
            return {}
    
    def update_collection_metadata(self, updates: Dict[str, Any]) -> bool:
        """Update collection metadata with automatic timestamp."""
        try:
            if not self.chroma_client:
                logger.error("Q&A Cache: Cannot update metadata - client not available")
                return False
            
            from datetime import datetime
            
            # Get current collection
            collection = self.chroma_client.get_collection(name=self.collection_name)
            current_metadata = collection.metadata or {}
            
            # Add timestamp and merge updates
            updates['last_updated'] = datetime.now().isoformat()
            current_metadata.update(updates)
            
            # Update collection metadata
            collection.modify(metadata=current_metadata)
            
            logger.debug_chromadb(f"Q&A Cache: Updated collection metadata")
            return True
            
        except Exception as e:
            logger.error(f"Q&A Cache: Failed to update metadata: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get comprehensive collection information with health metrics."""
        try:
            if not self.vectorstore or not hasattr(self.vectorstore, '_collection'):
                return {'error': 'Collection not available'}
            
            collection = self.vectorstore._collection
            
            # Basic collection info
            info = {
                'name': collection.name,
                'count': collection.count(),
                'metadata': getattr(collection, 'metadata', {}),
                'type': 'qa_cache'
            }
            
            # Add health metrics
            stats = self.get_stats()
            health_status = 'excellent' if stats['hit_rate'] > 70 else 'good' if stats['hit_rate'] > 40 else 'poor'
            response_status = 'fast' if stats['avg_response_time'] < 0.1 else 'acceptable' if stats['avg_response_time'] < 0.5 else 'slow'
            
            info['health'] = {
                'hit_rate_status': health_status,
                'response_time_status': response_status,
                'total_queries': stats['total_queries'],
                'cache_hits': stats['cache_hits'],
                'hit_rate_percent': stats['hit_rate'],
                'avg_response_time_ms': stats['avg_response_time'] * 1000,
                'similarity_threshold': self.similarity_threshold
            }
            
            # Add domain distribution
            info['domain_distribution'] = self.get_domain_stats()
            
            return info
            
        except Exception as e:
            logger.error(f"Q&A Cache: Failed to get collection info: {e}")
            return {'error': str(e)}
    
    def __str__(self) -> str:
        """String representation."""
        count = self._get_qa_count()
        return f"QACache({count} pairs, threshold={self.similarity_threshold})" 