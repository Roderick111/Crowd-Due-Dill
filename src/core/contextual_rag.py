#!/usr/bin/env python3
"""
Optimized Contextual RAG System with Hybrid Retrieval

Clean, production-ready RAG system with:
- Hybrid retrieval (metadata-first + semantic fallback)
- Domain-aware retrieval
- Resilience management
- Performance monitoring
- Clean logging
"""

import os
import re
import time
import chromadb
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .stats_collector import StatsCollector
from .resilience_manager import resilience_manager
from src.vectorization.metadata_system import MetadataManager
from src.utils.logger import logger


class OptimizedContextualRAGSystem:
    """
    Optimized RAG system with ChromaDB, resilience features, and hybrid retrieval.
    
    Features:
    - Hybrid retrieval: metadata-first search for precise queries + semantic fallback
    - ChromaDB vector database with optimized queries
    - OpenAI embeddings with resilience
    - Performance monitoring and statistics
    - Simplified query interface without domain restrictions
    """
    
    def __init__(self, 
                 chroma_path: str = "data/chroma_db",
                 collection_name: str = "contextual_rag_collection"):
        """
        Initialize the RAG system.
        
        Args:
            chroma_path: Path to ChromaDB storage
            collection_name: Name of the ChromaDB collection
        """
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        
        # Initialize core components
        self.stats_collector = StatsCollector()
        self.embeddings = None
        self.chroma_client = None
        self.vectorstore = None
        
        # Setup all components
        self._setup_embeddings()
        self._setup_chroma_client()
        self._setup_vectorstore()
        
        # Log initialization
        logger.system_ready("RAG System ready - hybrid retrieval enabled - no domain restrictions")
    
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
            "description": "Crowdfunding regulation knowledge base with domain-aware RAG",
            "domains": "lunar,ifs,astrology,crystals,numerology,tarot",
            "hnsw_config": "optimized",
            "last_updated": datetime.now().isoformat(),
            "system": "crowd_due_dill"
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
    
    def _detect_query_type(self, query_text: str) -> Dict[str, Any]:
        """
        Detect if query is exact article lookup vs semantic search.
        
        Args:
            query_text: User's query
            
        Returns:
            Dictionary with query analysis results
        """
        query_lower = query_text.lower().strip()
        
        # Pattern 1: "Article [number] of [regulation]" (most common)
        article_pattern = r'\barticle\s+(\d+)\s+of\s+(?:the\s+)?([a-zA-Z\s]+?)(?:\s|$)'
        match = re.search(article_pattern, query_lower)
        
        if match:
            article_num = match.group(1)
            regulation = match.group(2).strip()
            return {
                'is_precise_lookup': True,
                'article_number': f"Article {article_num}",
                'regulation': regulation,
                'query_type': 'precise_article',
                'confidence': 0.9
            }
        
        # Pattern 2: "GDPR Article 15", "DSA Article 22" (regulation first)
        acronym_pattern = r'\b(gdpr|dsa|aml|dora)\s+article\s+(\d+)'
        match = re.search(acronym_pattern, query_lower)
        
        if match:
            regulation = match.group(1).upper()
            article_num = match.group(2)
            return {
                'is_precise_lookup': True,
                'article_number': f"Article {article_num}",
                'regulation': regulation,
                'query_type': 'precise_acronym',
                'confidence': 0.8
            }
        
        # Pattern 3: "Article [number]" (standalone)
        standalone_pattern = r'\barticle\s+(\d+)\b'
        match = re.search(standalone_pattern, query_lower)
        
        if match:
            article_num = match.group(1)
            return {
                'is_precise_lookup': True,
                'article_number': f"Article {article_num}",
                'regulation': None,
                'query_type': 'precise_standalone',
                'confidence': 0.7
            }
        
        # Default: semantic search
        return {
            'is_precise_lookup': False,
            'article_number': None,
            'regulation': None,
            'query_type': 'semantic',
            'confidence': 1.0
        }
    
    def _metadata_search(self, query_info: Dict[str, Any], k: int) -> List[Document]:
        """
        Execute metadata-first search for precise article queries.
        
        Args:
            query_info: Query analysis from _detect_query_type
            k: Number of results to return
            
        Returns:
            List of Document objects with boosted similarity scores
        """
        if not self.chroma_client or not hasattr(self.vectorstore, '_collection'):
            return []
        
        try:
            # Build metadata filter
            where_clause = {
                "article_number": {"$eq": query_info['article_number']}
            }
            
            # Add regulation filter if detected
            if query_info.get('regulation'):
                reg = query_info['regulation']
                # Map common abbreviations to full names
                regulation_map = {
                    'dsa': 'digital_act',
                    'gdpr': 'gdpr',
                    'aml': 'aml',
                    'dora': 'dora'
                }
                
                source_key = regulation_map.get(reg.lower(), reg.lower())
                where_clause = {
                    "$and": [
                        {"article_number": {"$eq": query_info['article_number']}},
                        {"source": {"$contains": source_key}}
                    ]
                }
            
            # Execute metadata-filtered query
            chroma_results = self.vectorstore._collection.query(
                query_texts=[query_info['article_number']],
                n_results=k * 2,  # Get extra for potential filtering
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to LangChain Documents with boosted scores
            docs = []
            if chroma_results and chroma_results.get('documents'):
                for i, doc_text in enumerate(chroma_results['documents'][0]):
                    metadata = chroma_results.get('metadatas', [[]])[0][i] if chroma_results.get('metadatas') else {}
                    
                    # Add precise match indicator to metadata
                    metadata['_precise_match'] = True
                    metadata['_query_type'] = query_info['query_type']
                    metadata['_similarity_boost'] = 0.3
                    
                    docs.append(Document(page_content=doc_text, metadata=metadata))
                
                logger.debug_optimization(f"Metadata search found {len(docs)} precise matches")
            
            return docs[:k]
            
        except Exception as e:
            logger.debug_optimization(f"Metadata search failed: {e}")
            return []
    
    def _semantic_search_filtered(self, query_text: str, query_info: Dict[str, Any], k: int) -> List[Document]:
        """
        Execute semantic search with optional regulation filtering.
        
        Args:
            query_text: Original query text
            query_info: Query analysis for potential filtering
            k: Number of results to return
            
        Returns:
            List of Document objects from semantic search
        """
        try:
            if query_info.get('regulation') and hasattr(self.vectorstore, '_collection'):
                # Try filtered semantic search
                reg = query_info['regulation']
                regulation_map = {
                    'dsa': 'digital_act',
                    'gdpr': 'gdpr', 
                    'aml': 'aml',
                    'dora': 'dora'
                }
                source_key = regulation_map.get(reg.lower(), reg.lower())
                
                # Generate embedding
                def generate_embedding():
                    return self.embeddings.embed_query(query_text)
                
                query_embedding = resilience_manager.execute_with_openai_resilience(generate_embedding)
                
                # Execute filtered semantic search
                chroma_results = self.vectorstore._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    where={"source": {"$contains": source_key}},
                    include=["documents", "metadatas", "distances"]
                )
                
                # Convert to Documents
                docs = []
                if chroma_results and chroma_results.get('documents'):
                    for i, doc_text in enumerate(chroma_results['documents'][0]):
                        metadata = chroma_results.get('metadatas', [[]])[0][i] if chroma_results.get('metadatas') else {}
                        metadata['_query_type'] = 'semantic_filtered'
                        docs.append(Document(page_content=doc_text, metadata=metadata))
                
                return docs
            
        except Exception as e:
            logger.debug_optimization(f"Filtered semantic search failed: {e}")
        
        # Fallback to standard semantic search
        return self._standard_semantic_search(query_text, k)
    
    def _standard_semantic_search(self, query_text: str, k: int) -> List[Document]:
        """Execute standard semantic search."""
        try:
            docs = self.vectorstore.similarity_search(query_text, k=k)
            
            # Add metadata indicators
            for doc in docs:
                doc.metadata['_query_type'] = 'semantic'
                
            return docs
            
        except Exception as e:
            logger.debug_optimization(f"Standard semantic search failed: {e}")
            return []
    
    def _combine_hybrid_results(self, keyword_docs: List[Document], vector_docs: List[Document], k: int) -> List[Document]:
        """
        Combine keyword and vector search results following the hybrid pattern.
        
        Priority:
        1. Documents appearing in BOTH keyword and vector results (best matches)
        2. Keyword-only matches (precise but maybe not semantically relevant)  
        3. Vector-only matches (semantically relevant but not precise)
        
        Args:
            keyword_docs: Results from keyword search
            vector_docs: Results from vector search
            k: Target number of results
            
        Returns:
            Combined and deduplicated results
        """
        seen_content = set()
        combined = []
        
        # Create content keys for deduplication
        keyword_content_keys = {doc.page_content[:100]: doc for doc in keyword_docs}
        vector_content_keys = {doc.page_content[:100]: doc for doc in vector_docs}
        
        # Priority 1: Items appearing in BOTH searches (boost their relevance)
        for content_key, keyword_doc in keyword_content_keys.items():
            if content_key in vector_content_keys:
                # This document appears in both - highest priority
                keyword_doc.metadata['_hybrid_boost'] = True
                keyword_doc.metadata['_search_type'] = 'both'
                combined.append(keyword_doc)
                seen_content.add(content_key)
        
        # Priority 2: Keyword-only matches (precise matches)
        for content_key, doc in keyword_content_keys.items():
            if content_key not in seen_content and len(combined) < k:
                combined.append(doc)
                seen_content.add(content_key)
        
        # Priority 3: Vector-only matches (semantic relevance)
        for content_key, doc in vector_content_keys.items():
            if content_key not in seen_content and len(combined) < k:
                combined.append(doc)
                seen_content.add(content_key)
        
        both_count = len([d for d in combined if d.metadata.get('_search_type') == 'both'])
        keyword_count = len([d for d in combined if d.metadata.get('_search_type') == 'keyword'])
        vector_count = len([d for d in combined if d.metadata.get('_search_type') == 'vector'])
        
        logger.debug_optimization(f"Hybrid combination: {both_count} both + {keyword_count} keyword + {vector_count} vector = {len(combined)} total")
        
        return combined[:k]
    
    def query(self, query_text: str, k: int = 4) -> Dict[str, Any]:
        """
        Query the RAG system with parallel hybrid retrieval.
        
        Provides both vector+reranked results AND keyword results to the agent:
        - Vector search -> Cross-encoder reranking (5 results)
        - Keyword search (3 results) 
        - Agent receives both sets for optimal decision making
        
        Args:
            query_text: The user's query
            k: Number of chunks to retrieve (used for vector search)
            
        Returns:
            Dictionary containing both vector_results and keyword_results
        """
        start_time = time.time()
        
        # Check system availability
        if not self.vectorstore:
            return self._create_error_response(
                "Vector search is not available. Please check embeddings configuration.",
                start_time, "error"
            )
        
        try:
            # Detect query type for keyword search routing
            query_info = self._detect_query_type(query_text)
            logger.debug_optimization(f"Query type detected: {query_info['query_type']} (confidence: {query_info['confidence']})")
            
            # PARALLEL EXECUTION: Both searches run independently
            
            # Path 1: Vector search + Cross-encoder reranking (5 results)
            vector_docs = self._retrieve_vector_with_reranking(query_text, k=5)
            
            # Path 2: Keyword search (3 results, only for precise queries)
            keyword_docs = []
            if query_info['is_precise_lookup']:
                keyword_docs = self._keyword_search(query_info, k=3)
            
            # Create parallel results structure
            results = {
                'vector_results': self._format_results(vector_docs, 'vector_reranked'),
                'keyword_results': self._format_results(keyword_docs, 'keyword_precise'),
                'query_info': query_info,
                'search_strategy': 'parallel_hybrid',
                'total_results': len(vector_docs) + len(keyword_docs),
                'processing_time': time.time() - start_time
            }
            
            # Log the parallel strategy
            logger.debug_optimization(f"Parallel hybrid: {len(vector_docs)} vector+reranked + {len(keyword_docs)} keyword = {results['total_results']} total")
            
            return results
            
        except Exception as e:
            logger.error(f"RAG query error: {str(e)}")
            return self._create_error_response(
                "I encountered an error while searching for information.",
                start_time, "error", str(e)
            )
    
    def _retrieve_vector_with_reranking(self, query_text: str, k: int = 5) -> List[Document]:
        """
        Execute vector search followed by cross-encoder reranking.
        
        This mimics the document manager's query_documents method for consistency.
        
        Args:
            query_text: Query text
            k: Number of final results after reranking
            
        Returns:
            List of reranked Document objects
        """
        try:
            # Import document manager for reranking
            from tools.document_manager import SimpleDocumentManager
            
            # Initialize document manager for reranking
            doc_manager = SimpleDocumentManager()
            
            # Use document manager's query method which includes reranking
            reranked_results = doc_manager.query_documents(query_text, k=k, use_reranking=True)
            
            # Convert back to Document objects
            docs = []
            for result in reranked_results:
                # Add reranking metadata
                metadata = result.get('metadata', {})
                metadata['_search_type'] = 'vector_reranked'
                metadata['_rerank_score'] = result.get('rerank_score', 0.0)
                metadata['_similarity_score'] = result.get('similarity_score', 0.0)
                
                docs.append(Document(
                    page_content=result['page_content'],
                    metadata=metadata
                ))
            
            logger.debug_optimization(f"Vector+reranking: {len(docs)} results with cross-encoder scores")
            return docs
            
        except Exception as e:
            logger.debug_optimization(f"Vector+reranking failed: {e}")
            # Fallback to standard vector search
            return self._standard_vector_search(query_text, k)
    
    def _format_results(self, docs: List[Document], search_type: str) -> List[Dict[str, Any]]:
        """
        Format Document objects into standardized result dictionaries.
        
        Args:
            docs: List of Document objects
            search_type: Type of search performed
            
        Returns:
            List of formatted result dictionaries
        """
        results = []
        for i, doc in enumerate(docs):
            result = {
                'page_content': doc.page_content,
                'metadata': doc.metadata,
                'search_type': search_type,
                'rank': i + 1
            }
            
            # Add search-specific metadata
            if search_type == 'vector_reranked':
                result['rerank_score'] = doc.metadata.get('_rerank_score', 0.0)
                result['similarity_score'] = doc.metadata.get('_similarity_score', 0.0)
            elif search_type == 'keyword_precise':
                result['precise_match'] = doc.metadata.get('_precise_match', True)
            
            results.append(result)
        
        return results
    
    def _keyword_search(self, query_info: Dict[str, Any], k: int) -> List[Document]:
        """
        Execute keyword search using ChromaDB's where_document filtering combined with metadata.
        
        Uses $and operator for multiple metadata filters to achieve maximum precision.
        
        Args:
            query_info: Query analysis from _detect_query_type
            k: Number of results to return
            
        Returns:
            List of Document objects from keyword matching
        """
        if not self.chroma_client or not hasattr(self.vectorstore, '_collection'):
            return []
        
        try:
            # Build keyword search term
            article_text = query_info['article_number']  # e.g., "Article 22"
            
            # Build metadata filters using $and operator
            metadata_filters = []
            
            # 1. Always filter by exact article number (most important)
            metadata_filters.append({"structure.article_number": {"$eq": article_text}})
            
            # 2. Add regulation source filter if specified
            if query_info.get('regulation'):
                reg = query_info['regulation']
                regulation_map = {
                    'dsa': 'crawled_content/digital_act.md',
                    'gdpr': 'crawled_content/gdpr.md', 
                    'aml': 'crawled_content/aml.md',
                    'dora': 'crawled_content/dora.md'
                }
                source_value = regulation_map.get(reg.lower())
                if source_value:
                    metadata_filters.append({"document.source": {"$eq": source_value}})
            
            # Build final where clause with $and operator
            if len(metadata_filters) == 1:
                # Single filter - use directly
                where_metadata_filter = metadata_filters[0]
            else:
                # Multiple filters - use $and operator
                where_metadata_filter = {"$and": metadata_filters}
            
            # Execute keyword search with text + metadata filtering
            chroma_results = self.vectorstore._collection.get(
                limit=k * 3,  # Get extra for potential filtering
                where_document={"$contains": article_text},  # Text contains "Article 22"
                where=where_metadata_filter,  # Metadata: $and operator for precision
                include=["documents", "metadatas"]
            )
            
            # Convert to LangChain Documents
            docs = []
            if chroma_results and chroma_results.get('documents'):
                documents = chroma_results['documents']
                metadatas = chroma_results.get('metadatas', [{}] * len(documents))
                
                for i, doc_text in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    
                    # Mark as precise keyword+metadata match
                    metadata['_search_type'] = 'keyword_metadata'
                    metadata['_precise_match'] = True
                    metadata['_metadata_filtered'] = True
                    metadata['_filter_count'] = len(metadata_filters)
                    
                    docs.append(Document(page_content=doc_text, metadata=metadata))
                
                logger.debug_optimization(f"Keyword+metadata search ($and) found {len(docs)} precise matches for '{article_text}' with {len(metadata_filters)} filters")
            else:
                logger.debug_optimization(f"Keyword+metadata search ($and) found 0 matches for '{article_text}'")
            
            # If no results with strict metadata, fallback to text-only search
            if not docs:
                logger.debug_optimization(f"Falling back to text-only search for '{article_text}'")
                return self._keyword_text_only_search(query_info, k)
            
            return docs[:k]
            
        except Exception as e:
            logger.debug_optimization(f"Keyword+metadata search ($and) failed: {e}")
            # Fallback to text-only search
            return self._keyword_text_only_search(query_info, k)
    
    def _keyword_text_only_search(self, query_info: Dict[str, Any], k: int) -> List[Document]:
        """
        Fallback keyword search using only text filtering (original method).
        
        Args:
            query_info: Query analysis from _detect_query_type
            k: Number of results to return
            
        Returns:
            List of Document objects from text-only keyword matching
        """
        if not self.chroma_client or not hasattr(self.vectorstore, '_collection'):
            return []
        
        try:
            # Build keyword search term
            article_text = query_info['article_number']  # e.g., "Article 22"
            
            # Build basic metadata filter for regulation if specified
            where_metadata_filter = None
            if query_info.get('regulation'):
                reg = query_info['regulation']
                regulation_map = {
                    'dsa': 'crawled_content/digital_act.md',
                    'gdpr': 'crawled_content/gdpr.md', 
                    'aml': 'crawled_content/aml.md',
                    'dora': 'crawled_content/dora.md'
                }
                source_value = regulation_map.get(reg.lower())
                if source_value:
                    where_metadata_filter = {"document.source": {"$eq": source_value}}
            
            # Execute text-only keyword search
            chroma_results = self.vectorstore._collection.get(
                limit=k * 3,  # Get extra for potential filtering
                where_document={"$contains": article_text},  # Text search only
                where=where_metadata_filter,  # Optional source filter
                include=["documents", "metadatas"]
            )
            
            # Convert to LangChain Documents
            docs = []
            if chroma_results and chroma_results.get('documents'):
                documents = chroma_results['documents']
                metadatas = chroma_results.get('metadatas', [{}] * len(documents))
                
                for i, doc_text in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    
                    # Mark as text-only keyword match
                    metadata['_search_type'] = 'keyword_text_only'
                    metadata['_precise_match'] = False  # Less precise than metadata match
                    
                    docs.append(Document(page_content=doc_text, metadata=metadata))
                
                logger.debug_optimization(f"Text-only keyword search found {len(docs)} matches for '{article_text}'")
            else:
                logger.debug_optimization(f"Text-only keyword search found 0 matches for '{article_text}'")
            
            return docs[:k]
            
        except Exception as e:
            logger.debug_optimization(f"Text-only keyword search failed: {e}")
            return []
    
    def _standard_vector_search(self, query_text: str, k: int) -> List[Document]:
        """
        Execute standard vector search (unchanged from original).
        
        Args:
            query_text: Query text
            k: Number of results
            
        Returns:
            List of Document objects from vector search
        """
        try:
            # Use the original similarity search - completely unchanged
            docs = self.vectorstore.similarity_search(query_text, k=k)
            
            # Try optimized ChromaDB query if available (original logic)
            if (hasattr(self.vectorstore, '_collection') and 
                self.vectorstore._collection and 
                self.embeddings):
                
                try:
                    docs = self._optimized_chromadb_query(query_text, k)
                except Exception as e:
                    logger.debug_optimization(f"ChromaDB optimization failed, using fallback: {e}")
                
                # Mark as vector search
                for doc in docs:
                    doc.metadata['_search_type'] = 'vector'
            
            return docs
                
        except Exception as e:
            logger.debug_optimization(f"Vector search failed: {e}")
            return []
    
    def _optimized_chromadb_query(self, query_text: str, k: int):
        """Execute optimized ChromaDB query without domain filtering."""
        # Generate embedding with resilience
        def generate_embedding():
            return self.embeddings.embed_query(query_text)
        
        query_embedding = resilience_manager.execute_with_openai_resilience(generate_embedding)
        
        # Use ChromaDB's optimized query without domain filtering
        chroma_results = self.vectorstore._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
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
    
    def _handle_no_results(self, start_time: float):
        """Handle case when no documents are found."""
        response_time = time.time() - start_time
        
        return {
            "response": "I couldn't find relevant information to answer your question.",
            "chunks": [],
            "metadata": {
                "total_chunks": 0,
                "response_time": response_time,
                "query_type": "rag"
            }
        }
    
    def _process_results(self, docs: List[Document], start_time: float):
        """Process successful retrieval results without domain tracking."""
        response_time = time.time() - start_time
        
        # Log retrieval success
        logger.rag_retrieval(len(docs))
        
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
        """Get comprehensive system statistics without domain tracking."""
        stats = {
            'query_performance': self.stats_collector.get_query_stats(),
        }
        
        # Add vectorstore stats
        stats.update(self.stats_collector.get_vectorstore_stats(self.vectorstore))
        
        # Add resilience stats
        resilience_stats = resilience_manager.get_health_summary()
        stats.update(resilience_stats)
        
        return stats
    
    def get_domain_status(self) -> Dict[str, Any]:
        """Get empty domain status - no domain restrictions."""
        return {"active_domains": [], "available_domains": []}
    
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
        return f"OptimizedContextualRAGSystem(chroma_path={self.chroma_path}, collection_name={self.collection_name})" 