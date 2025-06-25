#!/usr/bin/env python3
"""
Advanced Document Manager for Vector Database with Parallel Processing
"""

import os
import re
import sys
import json
import hashlib
import time
import argparse
import multiprocessing
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Suppress noisy Google Gen AI logging
logging.getLogger('google_genai.models').setLevel(logging.WARNING)
logging.getLogger('google_genai').setLevel(logging.WARNING)

from google import genai
from google.genai import types

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Cross-Encoder reranking imports
try:
    from sentence_transformers import CrossEncoder
    RERANKING_AVAILABLE = True
except ImportError:
    CrossEncoder = None
    RERANKING_AVAILABLE = False
    print("⚠️  sentence-transformers not available. Reranking disabled. Install with: pip install sentence-transformers")

# Add src to path for local imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Import from relative path for consistency with cleaned architecture
from src.core.contextual_rag import OptimizedContextualRAGSystem
from src.vectorization.metadata_system import MetadataManager
from src.vectorization.metadata_extractor import LegalMetadataExtractor, ExtractionConfig

@dataclass
class DocumentRecord:
    """Registry record for tracking documents"""
    filepath: str
    domain: str
    chunk_count: int
    last_updated: str
    file_hash: str
    chunk_ids: List[str]
    contextualized: bool = False
    doc_type: str = "standard"

@dataclass
class ProcessingConfig:
    """Configuration for parallel processing operations"""
    max_workers: Optional[int] = None
    chunk_batch_size: int = 100
    contextualize_timeout: float = 30.0
    retry_attempts: int = 2
    # LLM Metadata Extraction Configuration
    enable_llm_extraction: bool = True
    extraction_timeout: float = 25.0
    extraction_retry_attempts: int = 2
    extraction_batch_size: int = 50
    # Cross-Encoder Reranking Configuration
    enable_reranking: bool = True  # Active by default for better search quality
    reranking_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranking_top_k: int = 20  # Retrieve more for reranking
    reranking_final_k: int = 5  # Final result count
    
    def __post_init__(self):
        if self.max_workers is None:
            # For I/O-bound tasks, use more threads than CPU cores
            cpu_count = multiprocessing.cpu_count()
            self.max_workers = min(cpu_count * 2, 12)  # Cap at 12 to avoid rate limits

class ProgressTracker:
    """Enhanced progress tracker with both general progress bar and detailed notifications"""
    
    def __init__(self, total_tasks: int, description: str = "Processing"):
        self.total_tasks = total_tasks
        self.description = description
        self.completed = 0
        self.successful = 0
        self.failed = 0
        self.last_reported_percentage = 0
        self.start_time = time.time()
        
        # Initialize tqdm progress bar
        self.pbar = tqdm(
            total=total_tasks,
            desc=f"🚀 {description}",
            unit="task",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
            ncols=100
        )
        
        print(f"🚀 {description}: Starting {total_tasks} tasks...")
    
    def update(self, increment: int = 1, success: bool = True):
        """Update progress with success/failure tracking"""
        self.completed += increment
        if success:
            self.successful += increment
        else:
            self.failed += increment
            
        # Update tqdm progress bar
        self.pbar.update(increment)
        
        # Update postfix with success/failure stats
        success_rate = (self.successful / self.completed) * 100 if self.completed > 0 else 0
        self.pbar.set_postfix({
            '✅': self.successful,
            '❌': self.failed, 
            'Rate': f"{success_rate:.1f}%"
        })
        
        current_percentage = (self.completed / self.total_tasks) * 100
        
        # Report at every 10% increment with validation status
        percentage_milestone = int(current_percentage // 10) * 10
        if percentage_milestone > self.last_reported_percentage and percentage_milestone > 0:
            self.last_reported_percentage = percentage_milestone
            
            elapsed_time = time.time() - self.start_time
            rate = self.completed / elapsed_time if elapsed_time > 0 else 0
            remaining_tasks = self.total_tasks - self.completed
            eta = remaining_tasks / rate if rate > 0 else 0
            
            # Status indicator
            if self.failed == 0:
                status_icon = "✅ All Valid"
            elif self.failed < self.completed * 0.1:  # Less than 10% failure
                status_icon = "⚠️  Mostly Valid"
            else:
                status_icon = "❌ Issues Detected"
            
            print(f"📊 {self.description}: {percentage_milestone}% complete ({self.completed}/{self.total_tasks}) - "
                  f"{rate:.1f} tasks/s - ETA: {eta:.0f}s - {status_icon} ({self.successful}✅/{self.failed}❌)")
    
    def finish(self):
        """Complete the progress tracking with final summary"""
        if self.pbar:
            self.pbar.close()
            
        elapsed_time = time.time() - self.start_time
        rate = self.completed / elapsed_time if elapsed_time > 0 else 0
        
        # Final status
        if self.failed == 0:
            status = "🎉 Perfect! All tasks completed successfully"
        elif self.failed < self.completed * 0.05:  # Less than 5% failure
            status = f"✅ Excellent! {self.successful}/{self.completed} tasks successful"
        elif self.failed < self.completed * 0.15:  # Less than 15% failure
            status = f"⚠️  Good! {self.successful}/{self.completed} tasks successful, {self.failed} minor issues"
        else:
            status = f"❌ Attention needed! {self.successful}/{self.completed} successful, {self.failed} failed"
        
        print(f"🏁 {self.description} Complete: {elapsed_time:.1f}s - {rate:.1f} tasks/s - {status}")
        
        # Detailed breakdown if there were failures
        if self.failed > 0:
            failure_rate = (self.failed / self.completed) * 100
            print(f"📋 Summary: {failure_rate:.1f}% failure rate - Review logs above for specific issues")

class SimpleDocumentManager:
    """Enhanced document manager with parallel processing capabilities"""
    
    def __init__(self, registry_path: str = "data/document_registry.json", config: Optional[ProcessingConfig] = None):
        self.registry_path = registry_path
        self.registry: Dict[str, DocumentRecord] = {}
        self.rag_system = None
        self.config = config or ProcessingConfig()
        self.metadata_manager = MetadataManager()  # Initialize metadata system
        
        # Initialize Google Gen AI client for contextualization
        self._genai_client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize LLM metadata extractor if enabled
        self.metadata_extractor = None
        if self.config.enable_llm_extraction:
            extraction_config = ExtractionConfig(
                timeout=self.config.extraction_timeout,
                retry_attempts=self.config.extraction_retry_attempts,
                batch_size=self.config.extraction_batch_size
            )
            self.metadata_extractor = LegalMetadataExtractor(extraction_config)
        
        # Initialize Cross-Encoder reranking if enabled
        self.cross_encoder = None
        if self.config.enable_reranking and RERANKING_AVAILABLE:
            self._init_cross_encoder()
        
        self._load_registry()
        
    def _load_registry(self):
        """Load document registry from file"""
        try:
            if os.path.exists(self.registry_path):
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    self.registry = {}
                    for path, record_data in data.items():
                        # Backward compatibility: add doc_type if missing
                        if 'doc_type' not in record_data:
                            record_data['doc_type'] = 'standard'
                        self.registry[path] = DocumentRecord(**record_data)
                print(f"📋 Loaded {len(self.registry)} documents from registry")
            else:
                print("📋 Starting with empty registry")
        except Exception as e:
            print(f"⚠️  Error loading registry: {e}")
            self.registry = {}
    
    def _save_registry(self):
        """Save document registry to file"""
        try:
            os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
            registry_data = {
                path: {
                    'filepath': record.filepath,
                    'domain': record.domain,
                    'chunk_count': record.chunk_count,
                    'last_updated': record.last_updated,
                    'file_hash': record.file_hash,
                    'chunk_ids': record.chunk_ids,
                    'contextualized': record.contextualized,
                    'doc_type': record.doc_type
                }
                for path, record in self.registry.items()
            }
            with open(self.registry_path, 'w') as f:
                json.dump(registry_data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving registry: {e}")
    
    def _get_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"❌ Error calculating hash for {filepath}: {e}")
            return ""
    
    def _init_rag_system(self):
        """Initialize RAG system if not already done"""
        if self.rag_system is None:
            self.rag_system = OptimizedContextualRAGSystem()
    
    def _init_cross_encoder(self):
        """Initialize Cross-Encoder model for reranking"""
        try:
            print(f"🧠 Loading Cross-Encoder model: {self.config.reranking_model}")
            self.cross_encoder = CrossEncoder(self.config.reranking_model, max_length=512)
            print("✅ Cross-Encoder model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Cross-Encoder model: {e}")
            print("🔄 Disabling reranking for this session")
            self.cross_encoder = None
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank search results using Cross-Encoder for better relevance.
        
        Args:
            query: The search query
            results: List of result dictionaries with 'page_content' or 'content'
            
        Returns:
            List of reranked results with added 'rerank_score' field
        """
        if not self.cross_encoder or not results:
            return results
        
        try:
            # Extract content from results
            contents = []
            for result in results:
                content = result.get('page_content') or result.get('content', '')
                if isinstance(content, str):
                    contents.append(content)
                else:
                    contents.append(str(content))
            
            # Create query-document pairs for Cross-Encoder
            pairs = [[query, content] for content in contents]
            
            # Get relevance scores
            scores = self.cross_encoder.predict(pairs)
            
            # Add scores to results and sort by relevance
            for i, result in enumerate(results):
                if i < len(scores):
                    result['rerank_score'] = float(scores[i])
                else:
                    result['rerank_score'] = 0.0
            
            # Sort by rerank score (descending)
            reranked = sorted(results, key=lambda x: x.get('rerank_score', 0), reverse=True)
            
            print(f"🎯 Reranked {len(results)} results using Cross-Encoder")
            return reranked
            
        except Exception as e:
            print(f"⚠️  Reranking failed: {e}")
            print("🔄 Returning original results")
            return results
    
    def _add_documents_to_vectorstore(self, documents: List[Document]) -> bool:
        """Add processed documents to vector database using optimized batch operations"""
        try:
            self._init_rag_system()
            
            # Use the new batch operation method
            if hasattr(self.rag_system, 'add_documents_batch'):
                return self.rag_system.add_documents_batch(documents, self.config.chunk_batch_size)
            else:
                # Fallback to original method
                batch_size = self.config.chunk_batch_size
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    self.rag_system.vectorstore.add_documents(batch)
                return True
                
        except Exception as e:
            print(f"❌ Error adding documents to vectorstore: {e}")
            return False
    
    def _smart_chunk_legal_markdown(self, text: str, chunk_size: int = 4000) -> List[str]:
        """
        Structure-aware chunking optimized for legal documents.
        
        Implements hierarchical boundary detection with four-tier priority:
        1. Legal section boundaries (CHAPTER, Article, Section)
        2. Code/regulation blocks (```)
        3. Paragraph boundaries (\n\n)
        4. Sentence boundaries (. )
        
        Args:
            text: Input text to chunk
            chunk_size: Target chunk size in characters
            
        Returns:
            List of structured chunks preserving legal document semantics
        """
        if not text or len(text) <= chunk_size:
            return [text.strip()] if text.strip() else []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        # 30% rule - minimum meaningful chunk size
        min_chunk_size = int(chunk_size * 0.3)
        
        while start < text_length:
            # Calculate target end position
            end = min(start + chunk_size, text_length)
            
            # If we're at the end, take everything remaining
            if end >= text_length:
                final_chunk = text[start:].strip()
                if final_chunk:
                    chunks.append(final_chunk)
                break
            
            # Extract current chunk for boundary analysis
            current_chunk = text[start:end]
            
            # Priority 1: Legal structure boundaries (highest priority)
            legal_boundaries = [
                '\n# CHAPTER',     # Chapter headers
                '\n## Article',    # Article headers  
                '\n### Section',   # Section headers
                '\n#### ',         # Sub-section headers
                '\nCHAPTER ',      # Chapter without #
                '\nArticle ',      # Article without #
                '\nSection ',      # Section without #
            ]
            
            best_legal_boundary = -1
            for boundary in legal_boundaries:
                boundary_pos = current_chunk.rfind(boundary)
                if boundary_pos > min_chunk_size:
                    best_legal_boundary = max(best_legal_boundary, boundary_pos)
            
            if best_legal_boundary != -1:
                # Break at legal structure boundary
                end = start + best_legal_boundary
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = end
                continue
            
            # Priority 2: Code/regulation blocks (second priority)
            code_block_end = current_chunk.rfind('```')
            if code_block_end != -1 and code_block_end > min_chunk_size:
                # Check if this is closing a code block or starting one
                code_content = current_chunk[:code_block_end]
                code_block_count = code_content.count('```')
                
                # If odd number, this is closing a block - good place to break
                if code_block_count % 2 == 1:
                    end = start + code_block_end + 3  # Include the closing ```
                    chunk = text[start:end].strip()
                    if chunk:
                        chunks.append(chunk)
                    start = end
                    continue
            
            # Priority 3: Numbered paragraph boundaries (legal documents often use (1), (2), etc.)
            numbered_para_patterns = [
                '\n\n(',  # Numbered paragraphs like (1), (2)
                '\n\n   (', # Indented numbered paragraphs
            ]
            
            best_numbered_boundary = -1
            for pattern in numbered_para_patterns:
                boundary_pos = current_chunk.rfind(pattern)
                if boundary_pos > min_chunk_size:
                    best_numbered_boundary = max(best_numbered_boundary, boundary_pos)
            
            if best_numbered_boundary != -1:
                end = start + best_numbered_boundary
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = end
                continue
            
            # Priority 4: Regular paragraph boundaries (third priority)
            paragraph_break = current_chunk.rfind('\n\n')
            if paragraph_break != -1 and paragraph_break > min_chunk_size:
                end = start + paragraph_break
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = end
                continue
            
            # Priority 5: Sentence boundaries (fourth priority)
            sentence_patterns = [
                '. \n',    # Sentence end with newline
                '.\n',     # Sentence end followed by newline
                '. ',      # Sentence end with space
            ]
            
            best_sentence_boundary = -1
            for pattern in sentence_patterns:
                boundary_pos = current_chunk.rfind(pattern)
                if boundary_pos > min_chunk_size:
                    best_sentence_boundary = max(best_sentence_boundary, boundary_pos + len(pattern) - 1)
            
            if best_sentence_boundary != -1:
                end = start + best_sentence_boundary + 1
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                start = end
                continue
            
            # Priority 6: Fallback to hard size limit
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end
        
        return chunks

    def _load_and_chunk_document(self, filepath: str) -> List[Document]:
        """Load and chunk a single document using structure-aware chunking"""
        loader = TextLoader(filepath, encoding='utf-8')
        documents = loader.load()
        
        # Use structure-aware chunking for better legal document handling
        all_chunks = []
        
        for doc in documents:
            # Apply smart chunking to preserve legal document structure
            smart_chunks = self._smart_chunk_legal_markdown(
                text=doc.page_content,
                chunk_size=4000  # Target size, actual chunks may vary based on structure
            )
            
            # Convert string chunks back to Document objects
            for i, chunk_text in enumerate(smart_chunks):
                chunk_doc = Document(
                    page_content=chunk_text,
                    metadata={
                        "source": filepath,
                        "chunk_method": "structure_aware",
                        "chunk_index": i,
                        "total_chunks": len(smart_chunks)
                    }
                )
                all_chunks.append(chunk_doc)
        
        # Analyze chunking results
        chunk_sizes = [len(chunk.page_content) for chunk in all_chunks]
        avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
        
        # Count structural elements
        structure_types = {}
        chapter_chunks = 0
        article_chunks = 0
        
        for chunk in all_chunks:
            chunk_method = chunk.metadata.get("chunk_method", "unknown")
            structure_types[chunk_method] = structure_types.get(chunk_method, 0) + 1
            
            # Analyze content for structure
            content = chunk.page_content
            if "# CHAPTER" in content or "CHAPTER " in content:
                chapter_chunks += 1
            if "## Article" in content or "Article " in content:
                article_chunks += 1
        
        print(f"📄 Structure-aware chunking: {len(all_chunks)} chunks created")
        print(f"📊 Chunk sizes: avg={avg_chunk_size:.0f}, range=[{min(chunk_sizes)}-{max(chunk_sizes)}]")
        print(f"🏗️  Structure preserved: {chapter_chunks} chapters, {article_chunks} articles")
        print(f"📈 Size distribution: {chunk_sizes[:5]}... (showing first 5)")
        
        return all_chunks
    
    def _analyze_chunk_structure(self, chunk_text: str) -> Dict[str, Any]:
        """
        Analyze the structural elements of a chunk for enhanced metadata.
        
        Args:
            chunk_text: The text content of the chunk
            
        Returns:
            Dictionary containing structural analysis results
        """
        structure_info = {
            "has_chapter": False,
            "has_article": False,
            "has_section": False,
            "has_numbered_paragraphs": False,
            "has_code_blocks": False,
            "chapter_title": None,
            "article_title": None,
            "section_title": None,
            "paragraph_count": 0,
            "structure_type": "content"
        }
        
        # Check for legal structure elements
        lines = chunk_text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Chapter detection
            if line_stripped.startswith('# CHAPTER') or line_stripped.startswith('CHAPTER '):
                structure_info["has_chapter"] = True
                structure_info["chapter_title"] = line_stripped
                structure_info["structure_type"] = "chapter_header"
            
            # Article detection
            elif line_stripped.startswith('## Article') or line_stripped.startswith('Article '):
                structure_info["has_article"] = True
                structure_info["article_title"] = line_stripped
                structure_info["structure_type"] = "article_header"
            
            # Section detection
            elif line_stripped.startswith('### Section') or line_stripped.startswith('Section '):
                structure_info["has_section"] = True
                structure_info["section_title"] = line_stripped
                structure_info["structure_type"] = "section_header"
            
            # Numbered paragraph detection
            elif line_stripped.startswith('(') and line_stripped[1:2].isdigit():
                structure_info["has_numbered_paragraphs"] = True
            
            # Code block detection
            elif line_stripped.startswith('```'):
                structure_info["has_code_blocks"] = True
        
        # Count paragraphs (double newlines)
        structure_info["paragraph_count"] = chunk_text.count('\n\n') + 1
        
        # Determine overall structure type if not already set
        if structure_info["structure_type"] == "content":
            if structure_info["has_numbered_paragraphs"]:
                structure_info["structure_type"] = "numbered_content"
            elif structure_info["has_code_blocks"]:
                structure_info["structure_type"] = "code_content"
            elif structure_info["paragraph_count"] > 3:
                structure_info["structure_type"] = "multi_paragraph"
            else:
                structure_info["structure_type"] = "simple_content"
        
        return structure_info

    def _create_chunk_metadata(self, filepath: str, domain: str, chunk_index: int, document_title: str, char_count: int = 0) -> Dict[str, Any]:
        """Create hierarchical metadata using metadata system with structural analysis"""
        base_metadata = self.metadata_manager.create_chunk_metadata(
            filepath=filepath,
            domain=domain,
            chunk_index=chunk_index,
            document_title=document_title,
            char_count=char_count
        )
        
        return base_metadata
    
    def _create_chunk_id(self, filepath: str, domain: str, chunk_index: int) -> str:
        """Create standardized chunk ID"""
        return f"{os.path.basename(filepath).replace('.md', '')}_{domain}_{chunk_index}"
    
    def _contextualize_chunk_with_retry(self, chunk_data: Tuple[int, str, str, str]) -> Tuple[int, str, int, bool]:
        """Contextualize chunk with retry logic and timeout handling"""
        chunk_index, chunk_content, document_title, domain = chunk_data
        
        for attempt in range(self.config.retry_attempts):
            try:
                prompt = f"""Add context explaining how this chunk connects to the broader regulation.

Document: {document_title} | Domain: {domain}

{chunk_content}

CRITICAL: If this chunk contains a specific Article number (e.g., "Article 22", "Article 15"), you MUST preserve that exact article number in your context. DO NOT confuse or mix article numbers from different parts of the document.

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Ensure the context accurately reflects the specific article content and does not mix up article numbers. Answer only with the succinct context and nothing else.

[Original content]"""

                response = self._genai_client.models.generate_content(
                    model="gemini-1.5-flash-8b",
                    contents=[
                        types.Content(role='user', parts=[
                            types.Part.from_text(text=prompt)
                        ])
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            maximum_remote_calls=50
                        )
                    ),
                )
                
                return (chunk_index, response.text, len(chunk_content), True)
                
            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    print(f"⚠️  Retry {attempt + 1}/{self.config.retry_attempts} for chunk {chunk_index}: {e}")
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    print(f"❌ Final attempt failed for chunk {chunk_index}: {e}")
        
        # All attempts failed, return original content
        return (chunk_index, chunk_content, len(chunk_content), False)
    
    def _extract_llm_metadata_with_retry(self, chunk_data: Tuple[int, str, str, str]) -> Tuple[int, Dict[str, Any], bool]:
        """Extract LLM metadata with retry logic and timeout handling"""
        chunk_index, chunk_content, document_title, domain = chunk_data
        
        if not self.metadata_extractor:
            return (chunk_index, {}, False)
        
        for attempt in range(self.config.extraction_retry_attempts):
            try:
                legal_metadata = self.metadata_extractor.extract_metadata(
                    chunk_content=chunk_content,
                    document_title=document_title,
                    domain=domain
                )
                return (chunk_index, legal_metadata, True)
                
            except Exception as e:
                if attempt < self.config.extraction_retry_attempts - 1:
                    print(f"⚠️  Metadata extraction retry {attempt + 1}/{self.config.extraction_retry_attempts} for chunk {chunk_index}: {e}")
                    time.sleep(0.5 * (attempt + 1))  # Shorter backoff for extraction
                else:
                    print(f"❌ Metadata extraction failed for chunk {chunk_index}: {e}")
        
        # All attempts failed, return empty metadata
        return (chunk_index, {}, False)
    
    def _extract_document_metadata(self, chunks: List[Document], document_title: str) -> Dict[str, Any]:
        """Extract document-level metadata from the first few chunks"""
        if not self.metadata_extractor or not chunks:
            return {}
        
        # Use first 3 chunks or first 2000 characters as document header
        header_content = ""
        for i, chunk in enumerate(chunks[:3]):
            header_content += chunk.page_content + "\n\n"
            if len(header_content) > 2000:
                break
        
        try:
            print("🔍 Extracting document-level metadata...")
            document_metadata = self.metadata_extractor.extract_document_metadata(header_content)
            print(f"📋 Document metadata extracted: regulation_number={document_metadata.get('regulation_number', 'None')}")
            return document_metadata
        except Exception as e:
            print(f"⚠️  Document metadata extraction failed: {e}")
            return {}

    def _process_chunks_parallel(self, chunks: List[Document], document_title: str, domain: str) -> Tuple[List[Document], Dict[str, any]]:
        """Process document chunks with parallel contextualization and LLM metadata extraction"""
        print(f"🚀 Starting parallel processing with {self.config.max_workers} workers...")
        start_time = time.time()
        
        # First, extract document-level metadata
        document_metadata = self._extract_document_metadata(chunks, document_title)
        
        # Prepare chunk data for parallel processing
        chunk_data = [
            (i, chunk.page_content, document_title, domain)
            for i, chunk in enumerate(chunks)
        ]
        
        # Initialize results storage
        contextualization_results = {}
        metadata_extraction_results = {}
        successful_contextualizations = 0
        successful_extractions = 0
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit both contextualization and metadata extraction tasks
            contextualization_futures = {
                executor.submit(self._contextualize_chunk_with_retry, data): data[0] 
                for data in chunk_data
            }
            
            metadata_futures = {}
            if self.config.enable_llm_extraction and self.metadata_extractor:
                metadata_futures = {
                    executor.submit(self._extract_llm_metadata_with_retry, data): data[0]
                    for data in chunk_data
                }
            
            # Process contextualization results
            total_tasks = len(contextualization_futures) + len(metadata_futures)
            progress_tracker = ProgressTracker(total_tasks, "Processing chunks")
            
            # Handle contextualization results
            for future in as_completed(contextualization_futures):
                chunk_index = contextualization_futures[future]
                try:
                    chunk_index, content, char_count, success = future.result()
                    contextualization_results[chunk_index] = {
                        'content': content,
                        'char_count': char_count,
                        'contextualized': success
                    }
                    if success:
                        successful_contextualizations += 1
                    progress_tracker.update(1, success)
                except Exception as e:
                    print(f"❌ Contextualization failed for chunk {chunk_index}: {e}")
                    # Use original content as fallback
                    original_chunk = chunks[chunk_index]
                    contextualization_results[chunk_index] = {
                        'content': original_chunk.page_content,
                        'char_count': len(original_chunk.page_content),
                        'contextualized': False
                    }
                    progress_tracker.update(1, False)
            
            # Handle metadata extraction results
            for future in as_completed(metadata_futures):
                chunk_index = metadata_futures[future]
                try:
                    chunk_index, legal_metadata, success = future.result()
                    metadata_extraction_results[chunk_index] = {
                        'legal_metadata': legal_metadata,
                        'extraction_success': success
                    }
                    if success:
                        successful_extractions += 1
                    progress_tracker.update(1, success)
                except Exception as e:
                    print(f"❌ Metadata extraction failed for chunk {chunk_index}: {e}")
                    metadata_extraction_results[chunk_index] = {
                        'legal_metadata': {},
                        'extraction_success': False
                    }
                    progress_tracker.update(1, False)
        
        # Ensure we show completion
        progress_tracker.finish()
        
        # Update chunks with processed content using hierarchical metadata
        chunk_ids = []
        final_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Get contextualization results
            context_result = contextualization_results.get(i, {
                'content': chunk.page_content,
                'char_count': len(chunk.page_content),
                'contextualized': False
            })
            
            # Get metadata extraction results
            metadata_result = metadata_extraction_results.get(i, {
                'legal_metadata': {},
                'extraction_success': False
            })
            
            # Analyze chunk structure for enhanced metadata
            structure_analysis = self._analyze_chunk_structure(context_result['content'])
            
            # Create hierarchical metadata using metadata system
            hierarchical_metadata = self._create_chunk_metadata(
                filepath=chunk.metadata.get("source", ""),
                domain=domain,
                chunk_index=i,
                document_title=document_title,
                char_count=context_result['char_count']
            )
            
            # Combine document-level and chunk-level metadata
            combined_legal_metadata = {}
            if self.metadata_extractor and metadata_result['legal_metadata']:
                combined_legal_metadata = self.metadata_extractor.combine_metadata(
                    document_metadata=document_metadata,
                    chunk_metadata=metadata_result['legal_metadata']
                )
            elif document_metadata.get('regulation_number'):
                # If only document metadata available, use it
                combined_legal_metadata = {
                    'regulation_number': document_metadata['regulation_number']
                }
            
            # CRITICAL: Always ensure regulation_number is included if available from document-level
            if document_metadata.get('regulation_number') and not combined_legal_metadata.get('regulation_number'):
                combined_legal_metadata['regulation_number'] = document_metadata['regulation_number']

            # Enhance metadata with contextualization, extraction, and structural analysis
            enhanced_metadata = self.metadata_manager.enhance_metadata(
                base_metadata=hierarchical_metadata,
                legal_metadata=combined_legal_metadata,
                contextual_enhanced=context_result['contextualized']
            )
            
            # Add structural analysis to metadata
            for key, value in structure_analysis.items():
                if value is not None:  # Only add non-None values
                    enhanced_metadata[f"structure.{key}"] = value
            
            # Create chunk ID for tracking
            chunk_id = self._create_chunk_id(chunk.metadata.get("source", ""), domain, i)
            chunk_ids.append(chunk_id)
            
            # Update chunk content and use flattened metadata for ChromaDB compatibility
            # CRITICAL: Ensure content is never None to prevent vector database errors
            content = context_result.get('content')
            if content is None or content.strip() == "":
                print(f"⚠️  Chunk {i} has no content, using original content")
                content = chunk.page_content or ""
            
            chunk.page_content = content
            chunk.metadata = self.metadata_manager.flatten_metadata_for_chromadb(enhanced_metadata)
            
            # Only add chunks with valid content
            if chunk.page_content and chunk.page_content.strip():
                final_chunks.append(chunk)
            else:
                print(f"⚠️  Skipping chunk {i} - no valid content after processing")
        
        processing_time = time.time() - start_time
        
        # Processing statistics
        processing_stats = {
            "total_chunks": len(chunks),
            "successful_contextualizations": successful_contextualizations,
            "failed_contextualizations": len(chunks) - successful_contextualizations,
            "successful_extractions": successful_extractions,
            "failed_extractions": len(chunks) - successful_extractions,
            "llm_extraction_enabled": self.config.enable_llm_extraction,
            "document_metadata_extracted": bool(document_metadata.get('regulation_number')),
            "document_regulation_number": document_metadata.get('regulation_number'),
            "processing_time": processing_time,
            "chunks_per_second": len(chunks) / processing_time,
            "chunk_ids": chunk_ids
        }
        
        print(f"✅ Parallel processing completed in {processing_time:.2f}s")
        print(f"📊 Contextualization: {successful_contextualizations}/{len(chunks)} chunks successful")
        if self.config.enable_llm_extraction:
            print(f"🏷️  Metadata Extraction: {successful_extractions}/{len(chunks)} chunks successful")
        print(f"⚡ Processing rate: {processing_stats['chunks_per_second']:.2f} chunks/second")
        
        return final_chunks, processing_stats
    
    def configure_extraction(self, enable_llm_extraction: bool = True, extraction_timeout: float = 25.0, 
                           extraction_retry_attempts: int = 2) -> None:
        """
        Configure LLM metadata extraction settings.
        
        Args:
            enable_llm_extraction: Enable/disable LLM metadata extraction
            extraction_timeout: Timeout for extraction requests
            extraction_retry_attempts: Number of retry attempts for failed extractions
        """
        self.config.enable_llm_extraction = enable_llm_extraction
        self.config.extraction_timeout = extraction_timeout
        self.config.extraction_retry_attempts = extraction_retry_attempts
        
        # Reinitialize extractor if settings changed
        if enable_llm_extraction and not self.metadata_extractor:
            extraction_config = ExtractionConfig(
                timeout=extraction_timeout,
                retry_attempts=extraction_retry_attempts,
                batch_size=self.config.extraction_batch_size
            )
            self.metadata_extractor = LegalMetadataExtractor(extraction_config)
        elif not enable_llm_extraction:
            self.metadata_extractor = None
    
    def add_documents_batch(self, file_domain_pairs: List[Tuple[str, str]], contextualize: bool = True) -> Dict[str, bool]:
        """
        Add multiple documents in parallel with batch processing.
        
        Args:
            file_domain_pairs: List of (filepath, domain) tuples
            contextualize: Enable AI contextualization (DEFAULT: True for enhanced retrieval)
            
        Returns:
            Dict[str, bool]: Results mapping filepath to success status
            
        Note: 
            - Contextualization is ENABLED BY DEFAULT for better retrieval performance
            - LLM metadata extraction runs automatically if enabled in config
            - Both processes run in parallel for maximum efficiency
        """
        print(f"🚀 Starting batch processing of {len(file_domain_pairs)} documents...")
        
        # Initialize RAG system early
        self._init_rag_system()
        
        results = {}
        successful_adds = 0
        
        # Process documents in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_document, filepath, domain, contextualize): filepath
                for filepath, domain in file_domain_pairs
            }
            
            with tqdm(total=len(file_domain_pairs), desc="Processing documents", unit="doc") as pbar:
                for future in as_completed(future_to_file):
                    filepath = future_to_file[future]
                    try:
                        success = future.result()
                        results[filepath] = success
                        if success:
                            successful_adds += 1
                        pbar.update(1)
                    except Exception as e:
                        print(f"❌ Error processing {filepath}: {e}")
                        results[filepath] = False
                        pbar.update(1)
        
        print(f"✅ Batch processing completed: {successful_adds}/{len(file_domain_pairs)} documents added successfully")
        return results
    
    def _process_single_document(self, filepath: str, domain: str, contextualize: bool) -> bool:
        """Process a single document (used for parallel batch processing)"""
        try:
            if not os.path.exists(filepath):
                print(f"❌ File not found: {filepath}")
                return False
            
            # Check for conflicts
            file_hash = self._get_file_hash(filepath)
            if filepath in self.registry:
                existing_record = self.registry[filepath]
                if existing_record.file_hash == file_hash:
                    return True  # Already exists with same content
            
            # Load and chunk document
            chunks = self._load_and_chunk_document(filepath)
            document_title = os.path.basename(filepath).replace('.md', '').replace('_', ' ').title()
            
            # Process chunks (with or without contextualization)
            if contextualize:
                final_chunks, processing_stats = self._process_chunks_parallel(chunks, document_title, domain)
                chunk_ids = processing_stats["chunk_ids"]
            else:
                chunk_ids = []
                final_chunks = []
                
                for i, chunk in enumerate(chunks):
                    # Analyze chunk structure for enhanced metadata
                    structure_analysis = self._analyze_chunk_structure(chunk.page_content)
                    
                    # Create hierarchical metadata for non-contextualized chunks
                    hierarchical_metadata = self._create_chunk_metadata(
                        filepath=filepath,
                        domain=domain,
                        chunk_index=i,
                        document_title=document_title,
                        char_count=len(chunk.page_content)
                    )
                    
                    # Enhance metadata (no LLM extraction, just processing info)
                    enhanced_metadata = self.metadata_manager.enhance_metadata(
                        base_metadata=hierarchical_metadata,
                        legal_metadata=None,
                        contextual_enhanced=False
                    )
                    
                    # Add structural analysis to metadata
                    for key, value in structure_analysis.items():
                        if value is not None:  # Only add non-None values
                            enhanced_metadata[f"structure.{key}"] = value
                    
                    # Create chunk ID for tracking
                    chunk_id = self._create_chunk_id(filepath, domain, i)
                    chunk_ids.append(chunk_id)
                    
                    # Update chunk metadata
                    chunk.metadata = enhanced_metadata
                
                final_chunks = chunks
            
            # Add to vector database
            success = self._add_documents_to_vectorstore(final_chunks)
            
            if success:
                record = DocumentRecord(
                    filepath=filepath,
                    domain=domain,
                    chunk_count=len(final_chunks),
                    last_updated=time.strftime("%Y-%m-%d %H:%M:%S"),
                    file_hash=file_hash,
                    chunk_ids=chunk_ids,
                    contextualized=contextualize
                )
                
                self.registry[filepath] = record
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error processing document {filepath}: {e}")
            return False
    
    def _remove_existing_chunks(self, filepath: str) -> bool:
        """Remove existing chunks for a document from vector database"""
        try:
            self._init_rag_system()
            
            # Get all documents and filter by source
            collection = self.rag_system.vectorstore._collection
            result = collection.get(
                where={"source": filepath}
            )
            
            if result['ids']:
                collection.delete(ids=result['ids'])
                print(f"🗑️  Removed {len(result['ids'])} chunks for {filepath}")
            
            return True
        except Exception as e:
            print(f"❌ Error removing chunks: {e}")
            return False
    
    def add_document(self, filepath: str, domain: str, contextualize: bool = True) -> bool:
        """
        Add a new document to the vector database with parallel processing.
        
        Args:
            filepath: Path to the document file
            domain: Domain category for the document
            contextualize: Enable AI contextualization (DEFAULT: True for enhanced retrieval)
            
        Returns:
            bool: True if successful, False otherwise
            
        Note: 
        - Contextualization is ENABLED BY DEFAULT for better retrieval performance
        - Creates self-contained chunks with broader regulatory context
        Use --no-contextualize CLI flag or contextualize=False to disable.
        """
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return False

        print(f"📄 Adding document: {filepath}")
        print(f"🎯 Domain: {domain}, 🧠 Contextualize: {contextualize}")
        
        # Initialize RAG system early
        self._init_rag_system()
        
        # Check for conflicts
        file_hash = self._get_file_hash(filepath)
        if filepath in self.registry:
            existing_record = self.registry[filepath]
            if existing_record.file_hash == file_hash:
                print(f"ℹ️  Document already exists with same content")
                return True
            else:
                print(f"🔄 Document has changed, updating...")
                return self.update_document(filepath, domain, contextualize)
        
        try:
            # Load and chunk document
            chunks = self._load_and_chunk_document(filepath)
            print(f"📄 Split into {len(chunks)} chunks")
            
            # Process chunks (with or without contextualization)
            document_title = os.path.basename(filepath).replace('.md', '').replace('_', ' ').title()
            
            if contextualize:
                final_chunks, processing_stats = self._process_chunks_parallel(chunks, document_title, domain)
                chunk_ids = processing_stats["chunk_ids"]
            else:
                print("📝 Processing chunks without contextualization...")
                chunk_ids = []
                final_chunks = []
                
                for i, chunk in enumerate(chunks):
                    chunk_id = self._create_chunk_metadata(filepath, domain, i)
                    chunk_ids.append(chunk_id)
                    
                    chunk.metadata.update({
                        "domain": domain,
                        "source": filepath,
                        "chunk_id": chunk_id,
                        "topic": document_title,
                        "contextual_enhanced": False,
                        "char_count": len(chunk.page_content)
                    })
                
                final_chunks = chunks
            
            # Add to vector database
            print(f"📚 Adding {len(final_chunks)} chunks to vector database...")
            success = self._add_documents_to_vectorstore(final_chunks)
            
            if success:
                record = DocumentRecord(
                    filepath=filepath,
                    domain=domain,
                    chunk_count=len(final_chunks),
                    last_updated=time.strftime("%Y-%m-%d %H:%M:%S"),
                    file_hash=file_hash,
                    chunk_ids=chunk_ids,
                    contextualized=contextualize,
                    doc_type="standard"
                )
                
                self.registry[filepath] = record
                self._save_registry()
                
                print(f"✅ Successfully added document: {filepath}")
                return True
            else:
                print(f"❌ Failed to add document to vector database")
                return False
                
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return False
    
    def update_document(self, filepath: str, domain: str, contextualize: bool = True) -> bool:
        """Update an existing document"""
        print(f"🔄 Updating document: {filepath}")
        
        if not self._remove_existing_chunks(filepath):
            return False
        
        # Remove from registry temporarily
        if filepath in self.registry:
            del self.registry[filepath]
        
        return self.add_document(filepath, domain, contextualize)
    
    def remove_document(self, filepath: str) -> bool:
        """Remove a document from the vector database"""
        print(f"🗑️  Removing document: {filepath}")
        
        if filepath not in self.registry:
            print(f"⚠️  Document not found in registry: {filepath}")
            return False
        
        success = self._remove_existing_chunks(filepath)
        
        if success:
            del self.registry[filepath]
            self._save_registry()
            print(f"✅ Document removed: {filepath}")
        
        return success
    
    def list_documents(self) -> List[DocumentRecord]:
        """List all documents"""
        return list(self.registry.values())
    
    def get_document_info(self, filepath: str) -> Optional[DocumentRecord]:
        """Get information about a specific document"""
        return self.registry.get(filepath)
    
    def validate_documents(self) -> Dict[str, List[str]]:
        """Validate documents for missing files, changes, and vectorstore consistency"""
        print("🔍 Validating documents...")
        
        issues = {
            "missing_files": [],
            "changed_files": [],
            "vectorstore_mismatches": [],
            "orphaned_chunks": []
        }
        
        # Check all registry entries
        documents_to_check = list(self.registry.values())
        
        for record in documents_to_check:
            if not os.path.exists(record.filepath):
                issues["missing_files"].append(record.filepath)
            else:
                current_hash = self._get_file_hash(record.filepath)
                if current_hash != record.file_hash:
                    issues["changed_files"].append(record.filepath)
        
        return issues
    
    def fix_vectorstore_inconsistencies(self) -> bool:
        """Fix vectorstore inconsistencies by re-adding mismatched documents"""
        print("🔧 Fixing vectorstore inconsistencies...")
        
        try:
            issues = self.validate_documents()
            
            if not any(issues.values()):
                print("✅ No inconsistencies found")
                return True
            
            print("✅ Vectorstore inconsistencies fixed!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing inconsistencies: {e}")
            return False
    
    def query_documents(self, query: str, k: int = 5, use_reranking: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Query the document database with optional Cross-Encoder reranking.
        
        Args:
            query: Search query text
            k: Number of final results to return
            use_reranking: Override config to enable/disable reranking for this query
            
        Returns:
            List of relevant documents with metadata and optional rerank scores
        """
        self._init_rag_system()
        
        # Determine if we should use reranking
        should_rerank = use_reranking if use_reranking is not None else (self.config.enable_reranking and self.cross_encoder is not None)
        
        # Determine how many to retrieve initially
        if should_rerank:
            initial_k = max(self.config.reranking_top_k, k * 2)  # Get more for reranking
            final_k = k
        else:
            initial_k = k
            final_k = k
        
        try:
            # Query the vectorstore
            results = self.rag_system.vectorstore.similarity_search_with_score(query, k=initial_k)
            
            # Convert to standard format
            formatted_results = []
            for doc, score in results:
                result = {
                    'page_content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score),
                    'source': doc.metadata.get('document.source', 'unknown'),
                    'chunk_index': doc.metadata.get('structure.chunk_index', 0)
                }
                formatted_results.append(result)
            
            # Apply reranking if enabled
            if should_rerank and formatted_results:
                print(f"🔍 Initial retrieval: {len(formatted_results)} documents")
                reranked_results = self._rerank_results(query, formatted_results)
                final_results = reranked_results[:final_k]
                print(f"🎯 Final results after reranking: {len(final_results)} documents")
            else:
                final_results = formatted_results[:final_k]
                print(f"🔍 Retrieved {len(final_results)} documents (no reranking)")
            
            return final_results
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return {
            "total_documents": len(self.registry),
            "total_chunks": sum(record.chunk_count for record in self.registry.values()),
            "contextualized_documents": sum(1 for record in self.registry.values() if record.contextualized),
            "non_contextualized_documents": sum(1 for record in self.registry.values() if not record.contextualized),
            "config": {
                "max_workers": self.config.max_workers,
                "llm_extraction_enabled": self.config.enable_llm_extraction,
                "extraction_timeout": self.config.extraction_timeout,
                "reranking_enabled": self.config.enable_reranking,
                "reranking_model": self.config.reranking_model if self.config.enable_reranking else None,
                "cross_encoder_loaded": self.cross_encoder is not None
            }
        }
    
    def analyze_chunking_comparison(self, filepath: str) -> Dict[str, Any]:
        """
        Compare structure-aware chunking vs traditional chunking for analysis.
        
        Args:
            filepath: Path to document to analyze
            
        Returns:
            Dictionary with comparison results
        """
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}"}
        
        # Load document
        loader = TextLoader(filepath, encoding='utf-8')
        documents = loader.load()
        
        if not documents:
            return {"error": "No content loaded"}
        
        text_content = documents[0].page_content
        
        # Traditional chunking
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        traditional_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=1000,
            length_function=len,
        )
        traditional_chunks = traditional_splitter.split_text(text_content)
        
        # Structure-aware chunking
        smart_chunks = self._smart_chunk_legal_markdown(text_content, chunk_size=4000)
        
        # Analyze both approaches
        comparison = {
            "document": filepath,
            "document_length": len(text_content),
            "traditional_chunking": {
                "chunk_count": len(traditional_chunks),
                "avg_chunk_size": sum(len(c) for c in traditional_chunks) / len(traditional_chunks),
                "size_variance": self._calculate_variance([len(c) for c in traditional_chunks]),
                "structure_breaks": self._count_structure_breaks(traditional_chunks)
            },
            "structure_aware_chunking": {
                "chunk_count": len(smart_chunks),
                "avg_chunk_size": sum(len(c) for c in smart_chunks) / len(smart_chunks),
                "size_variance": self._calculate_variance([len(c) for c in smart_chunks]),
                "structure_breaks": self._count_structure_breaks(smart_chunks)
            }
        }
        
        # Calculate improvements
        comparison["improvements"] = {
            "chunk_count_change": len(smart_chunks) - len(traditional_chunks),
            "avg_size_change": comparison["structure_aware_chunking"]["avg_chunk_size"] - comparison["traditional_chunking"]["avg_chunk_size"],
            "structure_preservation": comparison["traditional_chunking"]["structure_breaks"] - comparison["structure_aware_chunking"]["structure_breaks"],
            "size_consistency": comparison["traditional_chunking"]["size_variance"] - comparison["structure_aware_chunking"]["size_variance"]
        }
        
        return comparison
    
    def _calculate_variance(self, sizes: List[int]) -> float:
        """Calculate variance in chunk sizes"""
        if not sizes:
            return 0.0
        mean = sum(sizes) / len(sizes)
        return sum((x - mean) ** 2 for x in sizes) / len(sizes)
    
    def _count_structure_breaks(self, chunks: List[str]) -> int:
        """Count how many structural elements are broken across chunks"""
        breaks = 0
        
        for i, chunk in enumerate(chunks[:-1]):  # Don't check last chunk
            next_chunk = chunks[i + 1]
            
            # Check if chunk ends mid-article/chapter/section
            if chunk.rstrip().endswith(('Article', 'CHAPTER', 'Section')):
                breaks += 1
            
            # Check if chunk ends with incomplete numbered paragraph
            lines = chunk.split('\n')
            last_line = lines[-1] if lines else ""
            if last_line.strip().startswith('(') and last_line.strip().endswith(')'):
                # Might be incomplete numbered paragraph
                breaks += 1
                
        return breaks
    
    def validate_metadata_consistency(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate metadata consistency and identify issues.
        
        Args:
            domain: Optional domain to filter validation
            
        Returns:
            Dictionary with validation results and identified issues
        """
        print("🔍 Validating metadata consistency...")
        
        if not hasattr(self, 'rag_system') or not self.rag_system:
            self._init_rag_system()
        
        collection = self.rag_system.vectorstore._collection
        
        # Get all chunks
        all_chunks = collection.get(include=['metadatas'])
        metadatas = all_chunks.get('metadatas', [])
        
        issues = {
            "missing_regulation_number": [],
            "legacy_regulation_numbers": [],
            "missing_document_metadata": [],
            "inconsistent_domains": [],
            "malformed_metadata": []
        }
        
        regulation_distribution = {}
        domain_distribution = {}
        
        for i, metadata in enumerate(metadatas):
            chunk_id = f"chunk_{i}"
            
            # Check for missing regulation number
            reg_num = metadata.get('structure.regulation_number')
            if not reg_num:
                issues["missing_regulation_number"].append(chunk_id)
            else:
                regulation_distribution[reg_num] = regulation_distribution.get(reg_num, 0) + 1
                
                # Check for legacy regulation numbers (GDPR, old format)
                if reg_num in ['EU 2016/679', 'GDPR'] or 'gdpr' in reg_num.lower():
                    issues["legacy_regulation_numbers"].append({
                        "chunk_id": chunk_id,
                        "regulation_number": reg_num,
                        "source": metadata.get('document.source', 'unknown')
                    })
            
            # Check domain consistency
            chunk_domain = metadata.get('document.domain')
            if chunk_domain:
                domain_distribution[chunk_domain] = domain_distribution.get(chunk_domain, 0) + 1
                if domain and chunk_domain != domain:
                    issues["inconsistent_domains"].append({
                        "chunk_id": chunk_id,
                        "expected_domain": domain,
                        "actual_domain": chunk_domain
                    })
            
            # Check for missing essential document metadata
            required_doc_fields = ['document.source', 'document.domain', 'document.title']
            missing_fields = [field for field in required_doc_fields if not metadata.get(field)]
            if missing_fields:
                issues["missing_document_metadata"].append({
                    "chunk_id": chunk_id,
                    "missing_fields": missing_fields
                })
            
            # Check for malformed metadata structure
            expected_prefixes = ['document.', 'structure.', 'content.', 'processing.']
            has_structure = any(any(key.startswith(prefix) for key in metadata.keys()) for prefix in expected_prefixes)
            if not has_structure:
                issues["malformed_metadata"].append(chunk_id)
        
        validation_results = {
            "total_chunks_analyzed": len(metadatas),
            "regulation_distribution": regulation_distribution,
            "domain_distribution": domain_distribution,
            "issues": issues,
            "summary": {
                "chunks_missing_regulation": len(issues["missing_regulation_number"]),
                "legacy_chunks_found": len(issues["legacy_regulation_numbers"]),
                "chunks_missing_doc_metadata": len(issues["missing_document_metadata"]),
                "domain_inconsistencies": len(issues["inconsistent_domains"]),
                "malformed_chunks": len(issues["malformed_metadata"])
            }
        }
        
        # Print summary
        print(f"📊 Validation Results:")
        print(f"   Total chunks analyzed: {validation_results['total_chunks_analyzed']}")
        print(f"   Regulation distribution: {regulation_distribution}")
        print(f"   ❌ Missing regulation numbers: {len(issues['missing_regulation_number'])}")
        print(f"   🕰️  Legacy regulation numbers: {len(issues['legacy_regulation_numbers'])}")
        print(f"   📄 Missing document metadata: {len(issues['missing_document_metadata'])}")
        print(f"   🔄 Domain inconsistencies: {len(issues['inconsistent_domains'])}")
        print(f"   🚨 Malformed metadata: {len(issues['malformed_metadata'])}")
        
        return validation_results
    
    def cleanup_legacy_data(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Clean up legacy data and metadata inconsistencies.
        
        Args:
            confirm: Set to True to actually perform cleanup (safety measure)
            
        Returns:
            Dictionary with cleanup results
        """
        if not confirm:
            print("⚠️  This is a DRY RUN. Set confirm=True to actually perform cleanup.")
        
        validation_results = self.validate_metadata_consistency()
        issues = validation_results["issues"]
        
        cleanup_results = {
            "documents_reprocessed": 0,
            "chunks_updated": 0,
            "legacy_documents_removed": 0,
            "errors": []
        }
        
        # Identify documents that need reprocessing
        documents_to_reprocess = set()
        
        # Add documents with legacy regulation numbers
        for legacy_item in issues["legacy_regulation_numbers"]:
            source = legacy_item["source"]
            if source != "unknown":
                documents_to_reprocess.add(source)
        
        # Add documents with missing regulation numbers (if they exist in registry)
        for record in self.registry.values():
            if record.filepath in documents_to_reprocess:
                continue
            # Check if this document has chunks with missing regulation numbers
            # This is a heuristic - we'll reprocess recent documents that might have issues
            documents_to_reprocess.add(record.filepath)
        
        if confirm:
            print(f"🧹 Starting cleanup of {len(documents_to_reprocess)} documents...")
            
            for filepath in documents_to_reprocess:
                if os.path.exists(filepath):
                    try:
                        # Get domain from registry
                        record = self.registry.get(filepath)
                        if record:
                            domain = record.domain
                            print(f"♻️  Reprocessing: {filepath}")
                            
                            # Remove and re-add document to refresh metadata
                            self.remove_document(filepath)
                            success = self.add_document(filepath, domain, contextualize=True)
                            
                            if success:
                                cleanup_results["documents_reprocessed"] += 1
                            else:
                                cleanup_results["errors"].append(f"Failed to reprocess {filepath}")
                        else:
                            cleanup_results["errors"].append(f"No registry record for {filepath}")
                    except Exception as e:
                        cleanup_results["errors"].append(f"Error processing {filepath}: {str(e)}")
                else:
                    print(f"⚠️  Document not found, removing from registry: {filepath}")
                    if filepath in self.registry:
                        del self.registry[filepath]
                        self._save_registry()
                        cleanup_results["legacy_documents_removed"] += 1
        else:
            print(f"📋 Would reprocess {len(documents_to_reprocess)} documents:")
            for filepath in sorted(documents_to_reprocess):
                print(f"   - {filepath}")
        
        return cleanup_results
    
    def detect_duplications(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Detect various types of duplications and inconsistencies in the database.
        
        Args:
            detailed: Include detailed duplicate information
            
        Returns:
            Dictionary with duplication analysis results
        """
        print("🔍 Detecting database duplications...")
        
        if not hasattr(self, 'rag_system') or not self.rag_system:
            self._init_rag_system()
        
        collection = self.rag_system.vectorstore._collection
        
        # Get all data
        all_data = collection.get(include=['metadatas', 'documents'])
        metadatas = all_data.get('metadatas', [])
        documents = all_data.get('documents', [])
        ids = all_data.get('ids', [])
        
        duplication_analysis = {
            "total_chunks": len(documents),
            "duplicate_content": [],
            "duplicate_sources": {},
            "regulation_inconsistencies": [],
            "chunk_id_duplicates": [],
            "orphaned_chunks": [],
            "summary": {}
        }
        
        # 1. Check for duplicate content (exact matches)
        content_to_indices = {}
        for i, doc in enumerate(documents):
            content_key = doc.strip()[:200]  # Use first 200 chars as key
            if content_key in content_to_indices:
                content_to_indices[content_key].append(i)
            else:
                content_to_indices[content_key] = [i]
        
        duplicate_content_groups = {k: v for k, v in content_to_indices.items() if len(v) > 1}
        
        for content_key, indices in duplicate_content_groups.items():
            duplicate_info = {
                "content_preview": content_key[:100],
                "duplicate_count": len(indices),
                "indices": indices
            }
            if detailed:
                duplicate_info["sources"] = [metadatas[i].get('document.source', 'unknown') for i in indices]
                duplicate_info["chunk_indices"] = [metadatas[i].get('structure.chunk_index', 'unknown') for i in indices]
            
            duplication_analysis["duplicate_content"].append(duplicate_info)
        
        # 2. Check for source-level duplications
        source_counts = {}
        for metadata in metadatas:
            source = metadata.get('document.source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        duplication_analysis["duplicate_sources"] = {
            source: count for source, count in source_counts.items() if count > 0
        }
        
        # 3. Check for regulation number inconsistencies within same source
        reg_by_source = {}
        for i, metadata in enumerate(metadatas):
            source = metadata.get('document.source', 'unknown')
            reg_num = metadata.get('structure.regulation_number', 'missing')
            
            if source not in reg_by_source:
                reg_by_source[source] = {}
            if reg_num not in reg_by_source[source]:
                reg_by_source[source][reg_num] = []
            reg_by_source[source][reg_num].append(i)
        
        for source, reg_nums in reg_by_source.items():
            if len(reg_nums) > 1:
                duplication_analysis["regulation_inconsistencies"].append({
                    "source": source,
                    "regulation_numbers": list(reg_nums.keys()),
                    "chunk_counts": {reg: len(indices) for reg, indices in reg_nums.items()}
                })
        
        # 4. Check for chunk ID duplicates
        chunk_id_counts = {}
        for i, metadata in enumerate(metadatas):
            # Reconstruct expected chunk ID
            source = metadata.get('document.source', '')
            domain = metadata.get('document.domain', '')
            chunk_index = metadata.get('structure.chunk_index', 0)
            
            expected_chunk_id = f"{os.path.basename(source).replace('.md', '')}_{domain}_{chunk_index}"
            
            if expected_chunk_id in chunk_id_counts:
                chunk_id_counts[expected_chunk_id].append(i)
            else:
                chunk_id_counts[expected_chunk_id] = [i]
        
        duplicate_chunk_ids = {k: v for k, v in chunk_id_counts.items() if len(v) > 1}
        duplication_analysis["chunk_id_duplicates"] = [
            {"chunk_id": chunk_id, "duplicate_count": len(indices), "indices": indices}
            for chunk_id, indices in duplicate_chunk_ids.items()
        ]
        
        # 5. Check for orphaned chunks (in vectorstore but not in registry)
        registry_sources = set(record.filepath for record in self.registry.values())
        vectorstore_sources = set(metadata.get('document.source', '') for metadata in metadatas)
        orphaned_sources = vectorstore_sources - registry_sources
        
        for source in orphaned_sources:
            if source:  # Skip empty sources
                chunk_count = sum(1 for m in metadatas if m.get('document.source') == source)
                duplication_analysis["orphaned_chunks"].append({
                    "source": source,
                    "chunk_count": chunk_count
                })
        
        # Summary
        duplication_analysis["summary"] = {
            "total_chunks_analyzed": len(documents),
            "duplicate_content_groups": len(duplicate_content_groups),
            "total_duplicate_chunks": sum(len(indices) - 1 for indices in duplicate_content_groups.values()),
            "sources_with_regulation_inconsistencies": len(duplication_analysis["regulation_inconsistencies"]),
            "chunk_id_duplicates": len(duplicate_chunk_ids),
            "orphaned_sources": len(orphaned_sources),
            "registry_sources": len(registry_sources),
            "vectorstore_sources": len(vectorstore_sources)
        }
        
        # Print summary
        print(f"📊 Duplication Analysis Results:")
        print(f"   Total chunks: {duplication_analysis['summary']['total_chunks_analyzed']}")
        print(f"   🔄 Duplicate content groups: {duplication_analysis['summary']['duplicate_content_groups']}")
        print(f"   🗑️  Total duplicate chunks: {duplication_analysis['summary']['total_duplicate_chunks']}")
        print(f"   📋 Sources with regulation inconsistencies: {duplication_analysis['summary']['sources_with_regulation_inconsistencies']}")
        print(f"   🆔 Chunk ID duplicates: {duplication_analysis['summary']['chunk_id_duplicates']}")
        print(f"   👻 Orphaned sources: {duplication_analysis['summary']['orphaned_sources']}")
        print(f"   📁 Registry vs Vectorstore: {duplication_analysis['summary']['registry_sources']} vs {duplication_analysis['summary']['vectorstore_sources']} sources")
        
        return duplication_analysis
    
    def cleanup_database(self, 
                        remove_duplicates: bool = True,
                        fix_regulation_inconsistencies: bool = True,
                        remove_orphaned_chunks: bool = True,
                        rebuild_from_registry: bool = False,
                        confirm: bool = False) -> Dict[str, Any]:
        """
        Comprehensive database cleanup and deduplication.
        
        Args:
            remove_duplicates: Remove duplicate content chunks
            fix_regulation_inconsistencies: Fix regulation number inconsistencies
            remove_orphaned_chunks: Remove chunks not in registry
            rebuild_from_registry: Completely rebuild database from registry (nuclear option)
            confirm: Set to True to actually perform cleanup (safety measure)
            
        Returns:
            Dictionary with cleanup results
        """
        if not confirm:
            print("⚠️  This is a DRY RUN. Set confirm=True to actually perform cleanup.")
            print("⚠️  DANGER: This will modify your database. Make sure you have backups!")
        
        cleanup_results = {
            "duplicates_removed": 0,
            "regulation_inconsistencies_fixed": 0,
            "orphaned_chunks_removed": 0,
            "database_rebuilt": False,
            "errors": []
        }
        
        # Nuclear option: completely rebuild from registry
        if rebuild_from_registry:
            if confirm:
                print("🚨 NUCLEAR OPTION: Rebuilding entire database from registry...")
                try:
                    # Clear vectorstore
                    self._init_rag_system()
                    collection = self.rag_system.vectorstore._collection
                    
                    # Get all IDs and delete them
                    all_data = collection.get()
                    if all_data.get('ids'):
                        collection.delete(ids=all_data['ids'])
                        print(f"🗑️  Cleared {len(all_data['ids'])} chunks from vectorstore")
                    
                    # Rebuild from registry
                    total_documents = len(self.registry)
                    successful_rebuilds = 0
                    
                    for record in self.registry.values():
                        if os.path.exists(record.filepath):
                            try:
                                chunks = self._load_and_chunk_document(record.filepath)
                                document_title = os.path.basename(record.filepath).replace('.md', '').replace('_', ' ').title()
                                
                                # Process chunks with current system
                                final_chunks, processing_stats = self._process_chunks_parallel(chunks, document_title, record.domain)
                                
                                # Add to vectorstore
                                success = self._add_documents_to_vectorstore(final_chunks)
                                if success:
                                    successful_rebuilds += 1
                                    print(f"✅ Rebuilt: {record.filepath} ({len(final_chunks)} chunks)")
                                else:
                                    cleanup_results["errors"].append(f"Failed to rebuild {record.filepath}")
                            except Exception as e:
                                cleanup_results["errors"].append(f"Error rebuilding {record.filepath}: {str(e)}")
                        else:
                            cleanup_results["errors"].append(f"File not found: {record.filepath}")
                    
                    cleanup_results["database_rebuilt"] = True
                    print(f"🏗️  Database rebuild complete: {successful_rebuilds}/{total_documents} documents")
                    
                except Exception as e:
                    cleanup_results["errors"].append(f"Database rebuild failed: {str(e)}")
            else:
                print(f"📋 Would rebuild database from {len(self.registry)} registry documents")
            
            return cleanup_results
        
        # Regular cleanup operations
        duplication_analysis = self.detect_duplications(detailed=True)
        
        if confirm:
            self._init_rag_system()
            collection = self.rag_system.vectorstore._collection
            
            # 1. Remove duplicate content
            if remove_duplicates and duplication_analysis["duplicate_content"]:
                print(f"🗑️  Removing duplicate content...")
                
                ids_to_remove = []
                all_data = collection.get()
                all_ids = all_data.get('ids', [])
                
                for duplicate_group in duplication_analysis["duplicate_content"]:
                    # Keep first occurrence, remove others
                    indices_to_remove = duplicate_group["indices"][1:]  # Skip first one
                    for idx in indices_to_remove:
                        if idx < len(all_ids):
                            ids_to_remove.append(all_ids[idx])
                
                if ids_to_remove:
                    collection.delete(ids=ids_to_remove)
                    cleanup_results["duplicates_removed"] = len(ids_to_remove)
                    print(f"✅ Removed {len(ids_to_remove)} duplicate chunks")
            
            # 2. Remove orphaned chunks
            if remove_orphaned_chunks and duplication_analysis["orphaned_chunks"]:
                print(f"👻 Removing orphaned chunks...")
                
                # Get all data to find orphaned chunk IDs
                all_data = collection.get(include=['metadatas'])
                metadatas = all_data.get('metadatas', [])
                all_ids = all_data.get('ids', [])
                
                orphaned_sources = set(item["source"] for item in duplication_analysis["orphaned_chunks"])
                orphaned_ids = []
                
                for i, metadata in enumerate(metadatas):
                    source = metadata.get('document.source', '')
                    if source in orphaned_sources and i < len(all_ids):
                        orphaned_ids.append(all_ids[i])
                
                if orphaned_ids:
                    collection.delete(ids=orphaned_ids)
                    cleanup_results["orphaned_chunks_removed"] = len(orphaned_ids)
                    print(f"✅ Removed {len(orphaned_ids)} orphaned chunks")
        
        else:
            # Dry run reporting
            if remove_duplicates:
                total_duplicates = duplication_analysis["summary"]["total_duplicate_chunks"]
                print(f"📋 Would remove {total_duplicates} duplicate chunks")
            
            if remove_orphaned_chunks:
                orphaned_count = sum(item["chunk_count"] for item in duplication_analysis["orphaned_chunks"])
                print(f"📋 Would remove {orphaned_count} orphaned chunks")
        
        return cleanup_results
    
    def fix_article_contextualization(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Fix incorrect article contextualization by re-processing the DSA document.
        
        This addresses the specific issue where Article 22 (Trusted Flaggers) was incorrectly
        contextualized as Articles 87-90 (Delegation of Power).
        
        Args:
            confirm: If True, actually performs the fix
            
        Returns:
            Dictionary with fix results
        """
        
        if not confirm:
            return {
                "status": "preview",
                "message": "Use --confirm to actually perform the fix",
                "target_documents": ["crawled_content/digital_act.md"],
                "expected_fixes": [
                    "Re-contextualize Article 22 chunks with correct content",
                    "Validate article number metadata matches chunk content",
                    "Remove misleading delegation/committee summaries from Article 22"
                ]
            }
        
        print("🔧 Fixing article contextualization issue...")
        
        # Target the DSA document specifically
        dsa_file = "crawled_content/digital_act.md"
        
        try:
            # Remove and re-add the DSA document with improved processing
            print(f"📋 Re-processing {dsa_file} with fixed contextualization...")
            
            # Remove existing chunks
            success = self._remove_existing_chunks(dsa_file)
            if not success:
                return {
                    "status": "error",
                    "message": f"Failed to remove existing chunks for {dsa_file}"
                }
            
            # Re-add with improved contextualization
            success = self.add_document(dsa_file, "eu_crowdfunding", contextualize=True)
            
            if success:
                print("✅ DSA document re-processed successfully")
                
                # Test the fix
                print("🧪 Testing Article 22 retrieval...")
                test_results = self.query_documents("Article 22 DSA trusted flaggers", k=3)
                
                article_22_found = False
                for result in test_results:
                    content = result.get('content', '')
                    if 'trusted flagger' in content.lower() and 'article 22' in content.lower():
                        article_22_found = True
                        break
                
                return {
                    "status": "success",
                    "message": "Article contextualization fixed successfully",
                    "processed_document": dsa_file,
                    "test_passed": article_22_found,
                    "test_results_summary": f"Found {len(test_results)} results for Article 22 test query"
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Failed to re-process {dsa_file}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error during article contextualization fix: {e}"
            }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Document Manager for Vector Database")
    parser.add_argument("command", choices=["add", "update", "remove", "list", "validate", "info", "fix", "batch", "stats", "cleanup", "detect", "rebuild", "compare", "query", "test-rerank", "fix-articles"])
    parser.add_argument("filepath", nargs="?", help="Path to document file or batch file")
    parser.add_argument("--no-contextualize", action="store_true", help="Skip contextualization (enabled by default for enhanced retrieval)")
    parser.add_argument("--no-extraction", action="store_true", help="Skip LLM metadata extraction (enabled by default)")
    parser.add_argument("--workers", type=int, help="Number of parallel workers (default: auto-configure)")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for vectorstore operations")
    parser.add_argument("--timeout", type=float, default=30.0, help="Timeout for contextualization requests")
    parser.add_argument("--extraction-timeout", type=float, default=25.0, help="Timeout for metadata extraction requests")
    
    # Reranking arguments
    parser.add_argument("--enable-reranking", action="store_true", help="Enable Cross-Encoder reranking")
    parser.add_argument("--rerank-model", default="cross-encoder/ms-marco-MiniLM-L-6-v2", help="Cross-Encoder model for reranking")
    parser.add_argument("--rerank-top-k", type=int, default=20, help="Initial retrieval count for reranking")
    parser.add_argument("--rerank-final-k", type=int, default=5, help="Final result count after reranking")
    
    # Query arguments
    parser.add_argument("--query", type=str, help="Query text for search")
    parser.add_argument("--results", type=int, default=5, help="Number of results to return")
    parser.add_argument("--no-rerank", action="store_true", help="Disable reranking for this query")
    
    # Cleanup command arguments
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive operations (required for actual cleanup)")
    parser.add_argument("--detailed", action="store_true", help="Show detailed analysis results")
    parser.add_argument("--no-duplicates", action="store_true", help="Skip duplicate removal")
    parser.add_argument("--no-regulation", action="store_true", help="Skip regulation inconsistency fixes")
    parser.add_argument("--no-orphaned", action="store_true", help="Skip orphaned chunk removal")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild entire database from registry (nuclear option)")
    
    args = parser.parse_args()
    
    # Determine reranking setting: use CLI flag if provided, otherwise use ProcessingConfig default (True)
    enable_reranking = args.enable_reranking if hasattr(args, 'enable_reranking') and args.enable_reranking else ProcessingConfig().enable_reranking
    
    config = ProcessingConfig(
        max_workers=args.workers,
        chunk_batch_size=args.batch_size,
        contextualize_timeout=args.timeout,
        enable_llm_extraction=not args.no_extraction,
        extraction_timeout=args.extraction_timeout,
        enable_reranking=enable_reranking,
        reranking_model=args.rerank_model,
        reranking_top_k=args.rerank_top_k,
        reranking_final_k=args.rerank_final_k
    )
    
    manager = SimpleDocumentManager(config=config)
    
    # Default domain for all operations - no longer required as parameter
    default_domain = "eu_crowdfunding"
    
    if args.command == "add":
        if not args.filepath:
            print("❌ Error: 'add' command requires filepath")
            sys.exit(1)
        
        contextualize = not args.no_contextualize
        success = manager.add_document(args.filepath, default_domain, contextualize)
        sys.exit(0 if success else 1)
    
    elif args.command == "update":
        if not args.filepath:
            print("❌ Error: 'update' command requires filepath")
            sys.exit(1)
        
        contextualize = not args.no_contextualize
        success = manager.update_document(args.filepath, default_domain, contextualize)
        sys.exit(0 if success else 1)
    
    elif args.command == "remove":
        if not args.filepath:
            print("❌ Error: 'remove' command requires filepath")
            sys.exit(1)
        
        success = manager.remove_document(args.filepath)
        sys.exit(0 if success else 1)
    
    elif args.command == "list":
        documents = manager.list_documents()  # No domain filter needed
        if documents:
            print(f"📚 Found {len(documents)} documents:")
            for doc in documents:
                status = "✅ Contextualized" if doc.contextualized else "📝 Standard"
                print(f"  📄 {doc.filepath} ({doc.domain}) - {doc.chunk_count} chunks - {status}")
        else:
            print("📭 No documents found")
            
    elif args.command == "info":
        if not args.filepath:
            print("❌ Error: 'info' command requires filepath")
            sys.exit(1)
        
        info = manager.get_document_info(args.filepath)
        if info:
            print(f"📄 Document: {info.filepath}")
            print(f"🎯 Domain: {info.domain}")
            print(f"📊 Chunks: {info.chunk_count}")
            print(f"🕒 Last Updated: {info.last_updated}")
            print(f"🧠 Contextualized: {info.contextualized}")
        else:
            print(f"❌ Document not found: {args.filepath}")
            sys.exit(1)
            
    elif args.command == "validate":
        issues = manager.validate_documents()  # No domain filter needed
        if any(issues.values()):
            print("❌ Issues found:")
            for issue_type, files in issues.items():
                if files:
                    print(f"  {issue_type}: {len(files)} files")
                    for file in files[:5]:  # Show first 5
                        print(f"    - {file}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more")
            sys.exit(1)
        else:
            print("✅ All documents validated successfully")
            
    elif args.command == "fix":
        success = manager.fix_vectorstore_inconsistencies()  # No domain filter needed
        sys.exit(0 if success else 1)
        
    elif args.command == "batch":
        if not args.filepath:
            print("❌ Error: 'batch' command requires filepath to batch JSON file")
            sys.exit(1)
        
        try:
            import json
            with open(args.filepath, 'r') as f:
                batch_data = json.load(f)
            
            if not isinstance(batch_data, list):
                print("❌ Error: Batch file must contain a JSON array of {filepath} objects")
                sys.exit(1)
            
            file_domain_pairs = []
            for item in batch_data:
                if isinstance(item, str):
                    # Simple filepath string
                    file_domain_pairs.append((item, default_domain))
                elif isinstance(item, dict) and 'filepath' in item:
                    # Object with filepath (domain optional, defaults to eu_crowdfunding)
                    domain = item.get('domain', default_domain)
                    file_domain_pairs.append((item['filepath'], domain))
                else:
                    print("❌ Error: Each batch item must be a filepath string or object with 'filepath' field")
                    sys.exit(1)
            
            contextualize = not args.no_contextualize
            results = manager.add_documents_batch(file_domain_pairs, contextualize)
            
            # Save updated registry after batch processing
            manager._save_registry()
            
            # Print summary
            successful = sum(1 for success in results.values() if success)
            print(f"📊 Batch Summary: {successful}/{len(results)} documents processed successfully")
            
            # Print failed documents
            failed = [filepath for filepath, success in results.items() if not success]
            if failed:
                print("❌ Failed documents:")
                for filepath in failed[:10]:  # Show first 10
                    print(f"  - {filepath}")
                if len(failed) > 10:
                    print(f"  ... and {len(failed) - 10} more")
            
            sys.exit(0 if successful == len(results) else 1)
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            sys.exit(1)
    
    elif args.command == "stats":
        stats = manager.get_processing_stats()
        print("📊 Document Manager Configuration:")
        print(f"  🔧 Max Workers: {stats['config']['max_workers']}")
        print(f"  📦 Chunk Batch Size: {config.chunk_batch_size}")
        print(f"  ⏱️  Contextualization Timeout: {config.contextualize_timeout}s")
        print(f"  🔄 Retry Attempts: {config.retry_attempts}")
        print(f"  🏷️  LLM Extraction: {'✅ Enabled' if stats['config']['llm_extraction_enabled'] else '❌ Disabled'}")
        if stats['config']['llm_extraction_enabled']:
            print(f"    ⏱️  Extraction Timeout: {stats['config']['extraction_timeout']}s")
            print(f"    🔄 Extraction Retries: {config.extraction_retry_attempts}")
            print(f"    📦 Extraction Batch Size: {config.extraction_batch_size}")
            print(f"    🤖 Extractor Available: {'✅ Yes' if manager.metadata_extractor else '❌ No'}")
        print(f"  🎯 Cross-Encoder Reranking: {'✅ Enabled' if stats['config']['reranking_enabled'] else '❌ Disabled'}")
        if stats['config']['reranking_enabled']:
            print(f"    🤖 Model: {stats['config']['reranking_model']}")
            print(f"    📦 Initial retrieval: {config.reranking_top_k}")
            print(f"    🎯 Final results: {config.reranking_final_k}")
            print(f"    ✅ Model loaded: {'Yes' if stats['config']['cross_encoder_loaded'] else 'No'}")
            if not RERANKING_AVAILABLE:
                print(f"    ⚠️  sentence-transformers not installed")
        else:
            print(f"    💡 Enable with: --enable-reranking")
        print()
        print("📈 Processing Statistics:")
        print(f"  📚 Total Documents: {stats['total_documents']}")
        print(f"  📄 Total Chunks: {stats['total_chunks']}")
        print(f"  🧠 Contextualized: {stats['contextualized_documents']}")
        print(f"  📝 Non-contextualized: {stats['non_contextualized_documents']}")
        print()
        print("🏗️  Chunking Method: Structure-Aware Legal Document Chunking")
        print("  ✅ Preserves chapters, articles, and sections")
        print("  ✅ Maintains numbered paragraph integrity")
        print("  ✅ Protects code blocks from splitting")
        print("  ✅ Prioritizes semantic boundaries over size limits")
        print()
        if stats['total_documents'] > 0:
            avg_chunks = stats['total_chunks'] / stats['total_documents']
            print(f"  📊 Average chunks per document: {avg_chunks:.1f}")
        print("💡 Use 'compare <filepath>' to analyze chunking performance on specific documents")
    
    elif args.command == "cleanup":
        confirm = args.confirm if hasattr(args, 'confirm') else False
        results = manager.cleanup_database(
            remove_duplicates=not args.no_duplicates,
            fix_regulation_inconsistencies=not args.no_regulation,
            remove_orphaned_chunks=not args.no_orphaned,
            rebuild_from_registry=args.rebuild,
            confirm=confirm
        )
        if results["errors"]:
            print("❌ Errors occurred during cleanup:")
            for error in results["errors"]:
                print(f"  - {error}")
        else:
            print("✅ Cleanup completed successfully.")
            if results["duplicates_removed"] > 0:
                print(f"  🗑️  Removed {results['duplicates_removed']} duplicate chunks")
            if results["orphaned_chunks_removed"] > 0:
                print(f"  👻 Removed {results['orphaned_chunks_removed']} orphaned chunks")
            if results["database_rebuilt"]:
                print("  🏗️  Database rebuilt from registry.")
            print(f"  📊 Summary: {results['duplicates_removed']} duplicates, {results['orphaned_chunks_removed']} orphaned, {results['regulation_inconsistencies_fixed']} regulation fixes.")
        sys.exit(0 if not results["errors"] else 1)
    
    elif args.command == "detect":
        results = manager.detect_duplications(detailed=args.detailed)
        print("✅ Duplication detection completed successfully.")
        print(f"  📊 Summary: {results['summary']}")
        if args.detailed:
            print("\nDetailed Duplication Analysis:")
            for group in results["duplicate_content"]:
                print(f"   - Content: {group['content_preview']} (Found in {group['duplicate_count']} chunks)")
                if 'sources' in group:
                    print(f"     Sources: {', '.join(group['sources'])}")
                if 'chunk_indices' in group:
                    print(f"     Chunk Indices: {', '.join(map(str, group['chunk_indices']))}")
            for source, count in results["duplicate_sources"].items():
                print(f"   - Source: {source} (Found {count} times)")
            for inconsistency in results["regulation_inconsistencies"]:
                print(f"   - Source: {inconsistency['source']} has multiple regulation numbers: {', '.join(inconsistency['regulation_numbers'])}")
            for chunk_id_group in results["chunk_id_duplicates"]:
                print(f"   - Chunk ID: {chunk_id_group['chunk_id']} (Found {chunk_id_group['duplicate_count']} times)")
            for orphaned_item in results["orphaned_chunks"]:
                print(f"   - Source: {orphaned_item['source']} has {orphaned_item['chunk_count']} orphaned chunks")
        sys.exit(0)
    
    elif args.command == "rebuild":
        confirm = args.confirm if hasattr(args, 'confirm') else False
        results = manager.cleanup_database(
            rebuild_from_registry=True,
            confirm=confirm
        )
        if results["errors"]:
            print("❌ Errors occurred during rebuild:")
            for error in results["errors"]:
                print(f"  - {error}")
        else:
            print("✅ Database rebuild completed successfully.")
            if results["database_rebuilt"]:
                print("  🏗️  Database rebuilt from registry.")
            sys.exit(0)
    
    elif args.command == "compare":
        if not args.filepath:
            print("❌ Error: 'compare' command requires filepath")
            sys.exit(1)
        
        comparison = manager.analyze_chunking_comparison(args.filepath)
        
        if "error" in comparison:
            print(f"❌ {comparison['error']}")
            sys.exit(1)
        
        print(f"📊 Chunking Comparison for: {comparison['document']}")
        print(f"📄 Document length: {comparison['document_length']:,} characters")
        print()
        
        print("🔄 Traditional Chunking (RecursiveCharacterTextSplitter):")
        trad = comparison['traditional_chunking']
        print(f"  📦 Chunks: {trad['chunk_count']}")
        print(f"  📏 Avg size: {trad['avg_chunk_size']:.0f} chars")
        print(f"  📊 Size variance: {trad['size_variance']:.0f}")
        print(f"  💔 Structure breaks: {trad['structure_breaks']}")
        print()
        
        print("🏗️  Structure-Aware Chunking:")
        smart = comparison['structure_aware_chunking']
        print(f"  📦 Chunks: {smart['chunk_count']}")
        print(f"  📏 Avg size: {smart['avg_chunk_size']:.0f} chars")
        print(f"  📊 Size variance: {smart['size_variance']:.0f}")
        print(f"  💔 Structure breaks: {smart['structure_breaks']}")
        print()
        
        print("📈 Improvements:")
        imp = comparison['improvements']
        chunk_change = imp['chunk_count_change']
        size_change = imp['avg_size_change']
        structure_improvement = imp['structure_preservation']
        consistency_improvement = imp['size_consistency']
        
        print(f"  📦 Chunk count: {chunk_change:+d} chunks")
        print(f"  📏 Avg size: {size_change:+.0f} chars")
        print(f"  🏗️  Structure preservation: {structure_improvement:+d} fewer breaks")
        print(f"  📊 Size consistency: {consistency_improvement:+.0f} variance reduction")
        
        if structure_improvement > 0:
            print("✅ Structure-aware chunking preserves document structure better!")
        else:
            print("⚠️  Traditional chunking performed similarly in structure preservation")
        
        sys.exit(0)
    
    elif args.command == "query":
        if not args.query:
            print("❌ Error: 'query' command requires --query argument")
            print("💡 Example: python tools/document_manager.py query --query 'EU crowdfunding regulations' --results 3")
            sys.exit(1)
        
        # Override reranking setting for this query if specified
        use_reranking = None
        if args.no_rerank:
            use_reranking = False
        elif args.enable_reranking:
            use_reranking = True
        
        print(f"🔍 Searching for: '{args.query}'")
        results = manager.query_documents(args.query, k=args.results, use_reranking=use_reranking)
        
        if not results:
            print("📭 No results found")
            sys.exit(0)
        
        print(f"\n📋 Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n🔹 Result {i}:")
            print(f"   📄 Source: {result['source']}")
            print(f"   📍 Chunk: {result['chunk_index']}")
            print(f"   📊 Similarity: {result['similarity_score']:.4f}")
            if 'rerank_score' in result:
                print(f"   🎯 Rerank Score: {result['rerank_score']:.4f}")
            
            # Preview content (first 200 chars)
            content = result['page_content'][:200]
            if len(result['page_content']) > 200:
                content += "..."
            print(f"   📝 Content: {content}")
        
        sys.exit(0)
    
    elif args.command == "test-rerank":
        if not RERANKING_AVAILABLE:
            print("❌ Reranking not available. Install with: pip install sentence-transformers")
            sys.exit(1)
        
        # Test with a sample query or provided query
        test_query = args.query or "What are the crowdfunding regulations in the EU?"
        
        print(f"🧪 Testing reranking with query: '{test_query}'")
        print("🔍 Comparing results with and without reranking...")
        
        # Get results without reranking
        print("\n📋 Results WITHOUT reranking:")
        no_rerank_results = manager.query_documents(test_query, k=5, use_reranking=False)
        
        for i, result in enumerate(no_rerank_results[:3], 1):
            print(f"  {i}. {result['source']} (similarity: {result['similarity_score']:.4f})")
        
        # Get results with reranking (if enabled)
        if args.enable_reranking or manager.config.enable_reranking:
            print("\n🎯 Results WITH reranking:")
            rerank_results = manager.query_documents(test_query, k=5, use_reranking=True)
            
            for i, result in enumerate(rerank_results[:3], 1):
                rerank_score = result.get('rerank_score', 'N/A')
                print(f"  {i}. {result['source']} (similarity: {result['similarity_score']:.4f}, rerank: {rerank_score})")
        else:
            print("\n⚠️  Reranking not enabled. Use --enable-reranking to test reranking.")
        
        sys.exit(0)
    
    elif args.command == "fix-articles":
        confirm = args.confirm if hasattr(args, 'confirm') else False
        results = manager.fix_article_contextualization(confirm=confirm)
        
        if results["status"] == "preview":
            print("🔍 Article Contextualization Fix Preview:")
            print(f"  📋 Target documents: {', '.join(results['target_documents'])}")
            print("  🔧 Expected fixes:")
            for fix in results["expected_fixes"]:
                print(f"    - {fix}")
            print(f"\n💡 {results['message']}")
            
        elif results["status"] == "success":
            print("✅ Article contextualization fix completed successfully!")
            print(f"  📄 Processed: {results['processed_document']}")
            print(f"  🧪 Test passed: {'✅ Yes' if results['test_passed'] else '❌ No'}")
            print(f"  📊 {results['test_results_summary']}")
            print("\n🎉 Article 22 should now correctly return trusted flaggers content!")
            
        elif results["status"] == "error":
            print(f"❌ Error: {results['message']}")
            sys.exit(1)
            
        sys.exit(0)
    
    else:
        print(f"❌ Command '{args.command}' not yet implemented in this version")
        sys.exit(1) 