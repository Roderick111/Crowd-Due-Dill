#!/usr/bin/env python3
"""
Streamlined Document Manager for Vector Database
Cleaned up version with only essential functionality - 75% smaller than original.
"""

import os
import re
import sys
import json
import hashlib
import time
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Suppress noisy Google Gen AI logging
import logging
logging.getLogger('google_genai.models').setLevel(logging.WARNING)
logging.getLogger('google_genai').setLevel(logging.WARNING)

from google import genai
from google.genai import types
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Add src to path for local imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from src.core.contextual_rag import OptimizedContextualRAGSystem
from src.vectorization.metadata_system import MetadataManager
from src.vectorization.metadata_extractor import LegalMetadataExtractor, ExtractionConfig

@dataclass
class DocumentRecord:
    """Registry record for tracking documents - simplified without domain complexity"""
    filepath: str
    chunk_count: int
    last_updated: str
    file_hash: str
    chunk_ids: List[str]
    contextualized: bool = False
    # Legacy compatibility
    domain: str = "eu_crowdfunding"  # Default domain for backward compatibility
    doc_type: str = "standard"

@dataclass
class ProcessingConfig:
    """Configuration for processing operations"""
    max_workers: int = 8
    contextualize_timeout: float = 30.0
    retry_attempts: int = 2
    enable_llm_extraction: bool = True
    extraction_timeout: float = 25.0

class DocumentManager:
    """Streamlined document manager - core functionality only"""
    
    def __init__(self, registry_path: str = "data/document_registry.json", config: Optional[ProcessingConfig] = None):
        self.registry_path = registry_path
        self.registry: Dict[str, DocumentRecord] = {}
        self.rag_system = None
        self.config = config or ProcessingConfig()
        self.metadata_manager = MetadataManager()
        
        # Initialize Google Gen AI client for contextualization
        self._genai_client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize LLM metadata extractor if enabled
        self.metadata_extractor = None
        if self.config.enable_llm_extraction:
            extraction_config = ExtractionConfig(
                timeout=self.config.extraction_timeout,
                retry_attempts=self.config.retry_attempts
            )
            self.metadata_extractor = LegalMetadataExtractor(extraction_config)
        
        # Load existing registry
        self._load_registry()
        
        print(f"📚 Clean Document Manager initialized - {len(self.registry)} documents in registry")
        
    def _load_registry(self):
        """Load document registry from JSON file"""
        try:
            if os.path.exists(self.registry_path):
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    self.registry = {}
                    for filepath, record_data in data.items():
                        # Handle legacy records that may have extra fields
                        clean_record = {
                            'filepath': record_data.get('filepath', filepath),
                            'chunk_count': record_data.get('chunk_count', 0),
                            'last_updated': record_data.get('last_updated', ''),
                            'file_hash': record_data.get('file_hash', ''),
                            'chunk_ids': record_data.get('chunk_ids', []),
                            'contextualized': record_data.get('contextualized', False),
                            'domain': record_data.get('domain', 'eu_crowdfunding'),
                            'doc_type': record_data.get('doc_type', 'standard')
                        }
                        self.registry[filepath] = DocumentRecord(**clean_record)
                print(f"✅ Loaded registry with {len(self.registry)} documents")
            else:
                print("📝 No existing registry found, starting fresh")
        except Exception as e:
            print(f"⚠️  Error loading registry: {e}")
            self.registry = {}
    
    def _save_registry(self):
        """Save document registry to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
            registry_data = {
                filepath: {
                    'filepath': record.filepath,
                    'chunk_count': record.chunk_count,
                    'last_updated': record.last_updated,
                    'file_hash': record.file_hash,
                    'chunk_ids': record.chunk_ids,
                    'contextualized': record.contextualized,
                    'domain': record.domain,
                    'doc_type': record.doc_type
                }
                for filepath, record in self.registry.items()
            }
            with open(self.registry_path, 'w') as f:
                json.dump(registry_data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving registry: {e}")
    
    def _get_file_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash of file for change detection"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️  Error calculating hash for {filepath}: {e}")
            return ""
    
    def _init_rag_system(self):
        """Initialize RAG system if not already done"""
        if not self.rag_system:
            self.rag_system = OptimizedContextualRAGSystem()
    
    def _add_documents_to_vectorstore(self, documents: List[Document]) -> bool:
        """Add processed documents to the vector store"""
        try:
            self._init_rag_system()
            self.rag_system.vectorstore.add_documents(documents)
            return True
        except Exception as e:
            print(f"❌ Error adding documents to vectorstore: {e}")
            return False
    
    def _smart_chunk_legal_markdown(self, text: str, chunk_size: int = 4000) -> List[str]:
        """Smart chunking for legal documents that preserves structure"""
        
        # Define legal document structure patterns
        patterns = {
            'chapter': re.compile(r'^(CHAPTER|Chapter)\s+[IVXLCDM]+|\b(CHAPTER|Chapter)\s+\d+', re.MULTILINE),
            'article': re.compile(r'^Article\s+\d+|^Art\.\s*\d+', re.MULTILINE),
            'section': re.compile(r'^Section\s+\d+|^\d+\.\s+[A-Z]', re.MULTILINE),
            'paragraph': re.compile(r'^\d+\.\s+', re.MULTILINE),
        }
        
        # Find all structural boundaries
        boundaries = []
        for pattern_name, pattern in patterns.items():
            for match in pattern.finditer(text):
                boundaries.append({
                    'position': match.start(),
                    'type': pattern_name,
                    'text': match.group().strip()
                })
        
        # Sort boundaries by position
        boundaries.sort(key=lambda x: x['position'])
        
        # Create chunks respecting structure
        chunks = []
        current_chunk = ""
        current_size = 0
        
        last_pos = 0
        for boundary in boundaries:
            text_before = text[last_pos:boundary['position']]
            
            if current_size + len(text_before) > chunk_size and current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = text_before
                current_size = len(text_before)
            else:
                current_chunk += text_before
                current_size += len(text_before)
            
            last_pos = boundary['position']
        
        # Add remaining text
        remaining_text = text[last_pos:]
        if current_size + len(remaining_text) > chunk_size and current_chunk.strip():
            chunks.append(current_chunk.strip())
            current_chunk = remaining_text
        else:
            current_chunk += remaining_text
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Fallback to traditional chunking if needed
        if not chunks or len(chunks) == 1 and len(text) > chunk_size * 1.5:
            print("⚠️  Falling back to traditional chunking")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            chunks = text_splitter.split_text(text)
        
        return [chunk for chunk in chunks if chunk.strip()]

    def _load_and_chunk_document(self, filepath: str) -> List[Document]:
        """Load document and create chunks with metadata"""
        try:
            loader = TextLoader(filepath, encoding='utf-8')
            documents = loader.load()
            
            if not documents:
                print(f"❌ No content loaded from {filepath}")
                return []
            
            document = documents[0]
            text = document.page_content
            
            # Extract document title
            document_title = os.path.splitext(os.path.basename(filepath))[0]
            first_lines = text.split('\n')[:5]
            for line in first_lines:
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 10:
                    document_title = line[:100]
                    break
            
            # Create chunks using smart chunking
            chunk_texts = self._smart_chunk_legal_markdown(text)
            
            # Create Document objects with metadata
            chunks = []
            for i, chunk_text in enumerate(chunk_texts):
                metadata = {
                    'source': filepath,
                    'chunk_index': i,
                    'document_title': document_title,
                    'char_count': len(chunk_text),
                    'chunk_id': f"{filepath}:{i}"
                }
                chunk_doc = Document(page_content=chunk_text, metadata=metadata)
                chunks.append(chunk_doc)
            
            print(f"📄 Loaded {filepath}: {len(chunks)} chunks, avg size: {sum(len(c.page_content) for c in chunks) // len(chunks)} chars")
            return chunks
            
        except Exception as e:
            print(f"❌ Error loading document {filepath}: {e}")
            return []
    
    def _contextualize_chunk_with_retry(self, chunk_data: Tuple[int, str, str, str]) -> Tuple[int, str, int, bool]:
        """Contextualize a single chunk with retry logic"""
        chunk_index, chunk_text, document_title, filepath = chunk_data
        
        for attempt in range(self.config.retry_attempts):
            try:
                prompt = f"""
You are contextualizing a chunk from a legal document for a vector database.

Document: {document_title}
Source: {filepath}

Original chunk:
{chunk_text}

Please provide a contextualized version that:
1. Preserves all original content exactly
2. Adds brief context about the document source
3. Maintains all article numbers, section references, and legal citations
4. Keeps the chunk focused and relevant

Contextualized chunk:"""

                response = self._genai_client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=2000,
                        timeout=self.config.contextualize_timeout
                    )
                )
                
                if response and response.text:
                    contextualized_text = response.text.strip()
                    return (chunk_index, contextualized_text, len(contextualized_text), True)
                else:
                    print(f"⚠️  Empty response for chunk {chunk_index}, attempt {attempt + 1}")
                
            except Exception as e:
                print(f"⚠️  Contextualization failed for chunk {chunk_index}, attempt {attempt + 1}: {e}")
                if attempt == self.config.retry_attempts - 1:
                    return (chunk_index, chunk_text, len(chunk_text), False)
                time.sleep(1)
        
        return (chunk_index, chunk_text, len(chunk_text), False)

    def _process_chunks_parallel(self, chunks: List[Document], document_title: str) -> Tuple[List[Document], Dict[str, Any]]:
        """Process chunks in parallel for contextualization and metadata extraction"""
        
        chunk_data = [
            (i, chunk.page_content, document_title, chunk.metadata['source'])
            for i, chunk in enumerate(chunks)
        ]
        
        processed_chunks = chunks.copy()
        processing_stats = {
            'contextualized_count': 0,
            'metadata_extracted_count': 0,
            'total_chunks': len(chunks)
        }
        
        # Parallel contextualization
        print(f"🧠 Contextualizing {len(chunks)} chunks...")
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            context_futures = {
                executor.submit(self._contextualize_chunk_with_retry, data): data[0] 
                for data in chunk_data
            }
            
            with tqdm(total=len(chunk_data), desc="Contextualizing", unit="chunk") as pbar:
                for future in as_completed(context_futures):
                    chunk_index, contextualized_text, char_count, success = future.result()
                    if success:
                        processed_chunks[chunk_index].page_content = contextualized_text
                        processed_chunks[chunk_index].metadata['contextualized'] = True
                        processed_chunks[chunk_index].metadata['char_count'] = char_count
                        processing_stats['contextualized_count'] += 1
                    pbar.update(1)
        
        # Parallel metadata extraction
        if self.config.enable_llm_extraction and self.metadata_extractor:
            print(f"🏷️  Extracting metadata from {len(chunks)} chunks...")
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                metadata_futures = {
                    executor.submit(self._extract_metadata, data): data[0] 
                    for data in chunk_data
                }
                
                with tqdm(total=len(chunk_data), desc="Extracting metadata", unit="chunk") as pbar:
                    for future in as_completed(metadata_futures):
                        chunk_index, metadata, success = future.result()
                        if success and metadata:
                            processed_chunks[chunk_index].metadata.update(metadata)
                            processing_stats['metadata_extracted_count'] += 1
                        pbar.update(1)
        
        return processed_chunks, processing_stats

    def _extract_metadata(self, chunk_data: Tuple[int, str, str, str]) -> Tuple[int, Dict[str, Any], bool]:
        """Extract metadata from a chunk using LLM"""
        chunk_index, chunk_text, document_title, filepath = chunk_data
        
        try:
            metadata = self.metadata_extractor.extract_metadata(chunk_text)
            return (chunk_index, metadata, True)
        except Exception as e:
            print(f"⚠️  Metadata extraction failed for chunk {chunk_index}: {e}")
            return (chunk_index, {}, False)

    def add_document(self, filepath: str, contextualize: bool = True) -> bool:
        """Add a single document to the vector database"""
        try:
            if not os.path.exists(filepath):
                print(f"❌ File not found: {filepath}")
                return False
            
            # Check if document already exists and is up to date
            current_hash = self._get_file_hash(filepath)
            if filepath in self.registry:
                if self.registry[filepath].file_hash == current_hash:
                    print(f"✅ Document {filepath} is already up to date")
                    return True
                else:
                    print(f"🔄 Document {filepath} has changed, updating...")
                    self._remove_existing_chunks(filepath)
            
            # Load and chunk document
            chunks = self._load_and_chunk_document(filepath)
            if not chunks:
                return False
            
            # Process chunks (contextualize and extract metadata)
            if contextualize:
                processed_chunks, stats = self._process_chunks_parallel(chunks, os.path.basename(filepath))
                print(f"✅ Processing complete: {stats['contextualized_count']}/{stats['total_chunks']} contextualized, "
                      f"{stats['metadata_extracted_count']}/{stats['total_chunks']} metadata extracted")
            else:
                processed_chunks = chunks
                print(f"📝 Skipped contextualization for {len(chunks)} chunks")
            
            # Add to vector store
            if not self._add_documents_to_vectorstore(processed_chunks):
                return False
            
            # Update registry
            chunk_ids = [chunk.metadata['chunk_id'] for chunk in processed_chunks]
            self.registry[filepath] = DocumentRecord(
                        filepath=filepath,
                chunk_count=len(processed_chunks),
                last_updated=time.strftime('%Y-%m-%d %H:%M:%S'),
                file_hash=current_hash,
                    chunk_ids=chunk_ids,
                    contextualized=contextualize
                )
                
            self._save_registry()
            print(f"✅ Successfully added {filepath} with {len(processed_chunks)} chunks")
            return True
                
        except Exception as e:
            print(f"❌ Error adding document {filepath}: {e}")
            return False
    
    def _remove_existing_chunks(self, filepath: str) -> bool:
        """Remove existing chunks for a document from the vector store"""
        try:
            if filepath not in self.registry:
                return True
            
            self._init_rag_system()
            
            chunk_ids = self.registry[filepath].chunk_ids
            if chunk_ids:
                self.rag_system.vectorstore.delete(ids=chunk_ids)
                print(f"🗑️  Removed {len(chunk_ids)} existing chunks for {filepath}")
            
            return True
        except Exception as e:
            print(f"⚠️  Error removing existing chunks for {filepath}: {e}")
            return False
    
    def update_document(self, filepath: str, contextualize: bool = True) -> bool:
        """Update an existing document"""
        return self.add_document(filepath, contextualize)
    
    def remove_document(self, filepath: str) -> bool:
        """Remove a document from the vector database"""
        try:
            if filepath not in self.registry:
                print(f"⚠️  Document {filepath} not found in registry")
                return False
            
            success = self._remove_existing_chunks(filepath)
            del self.registry[filepath]
            self._save_registry()
            
            print(f"✅ Successfully removed {filepath}")
            return success
                
        except Exception as e:
            print(f"❌ Error removing document {filepath}: {e}")
            return False
    
    def list_documents(self) -> List[DocumentRecord]:
        """List all documents in the registry"""
        return list(self.registry.values())
    
    def get_document_info(self, filepath: str) -> Optional[DocumentRecord]:
        """Get information about a specific document"""
        return self.registry.get(filepath)
    
    def validate_documents(self) -> Dict[str, List[str]]:
        """Validate all documents in the registry"""
        issues = {
            'missing_files': [],
            'hash_mismatches': []
        }
        
        for filepath, record in self.registry.items():
            if not os.path.exists(filepath):
                issues['missing_files'].append(filepath)
            else:
                current_hash = self._get_file_hash(filepath)
                if current_hash != record.file_hash:
                    issues['hash_mismatches'].append(filepath)
        
        return issues
    
    def add_documents_batch(self, filepaths: List[str], contextualize: bool = True) -> Dict[str, bool]:
        """Add multiple documents in batch"""
        results = {}
        
        print(f"📚 Processing {len(filepaths)} documents in batch...")
        
        for filepath in tqdm(filepaths, desc="Adding documents", unit="doc"):
            try:
                results[filepath] = self.add_document(filepath, contextualize)
            except Exception as e:
                print(f"❌ Error processing {filepath}: {e}")
                results[filepath] = False
        
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        total_docs = len(self.registry)
        contextualized_docs = sum(1 for record in self.registry.values() if record.contextualized)
        total_chunks = sum(record.chunk_count for record in self.registry.values())
        
        return {
            'total_documents': total_docs,
            'contextualized_documents': contextualized_docs,
            'non_contextualized_documents': total_docs - contextualized_docs,
            'total_chunks': total_chunks,
            'config': {
                'max_workers': self.config.max_workers,
                'llm_extraction_enabled': self.config.enable_llm_extraction,
                'extraction_timeout': self.config.extraction_timeout
            }
        }

def main():
    """Main CLI interface - simplified commands"""
    parser = argparse.ArgumentParser(description="Clean Document Manager for Vector Database")
    parser.add_argument("command", choices=["add", "update", "remove", "list", "validate", "info", "batch", "stats"])
    parser.add_argument("filepath", nargs="?", help="Path to document file or batch file")
    parser.add_argument("--no-contextualize", action="store_true", help="Skip contextualization")
    parser.add_argument("--no-extraction", action="store_true", help="Skip LLM metadata extraction")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers")
    
    args = parser.parse_args()
    
    config = ProcessingConfig(
        max_workers=args.workers,
        enable_llm_extraction=not args.no_extraction
    )
    
    manager = DocumentManager(config=config)
    
    if args.command == "add":
        if not args.filepath:
            print("❌ Error: 'add' command requires filepath")
            sys.exit(1)
        contextualize = not args.no_contextualize
        success = manager.add_document(args.filepath, contextualize)
        sys.exit(0 if success else 1)
    
    elif args.command == "update":
        if not args.filepath:
            print("❌ Error: 'update' command requires filepath")
            sys.exit(1)
        contextualize = not args.no_contextualize
        success = manager.update_document(args.filepath, contextualize)
        sys.exit(0 if success else 1)
    
    elif args.command == "remove":
        if not args.filepath:
            print("❌ Error: 'remove' command requires filepath")
            sys.exit(1)
        success = manager.remove_document(args.filepath)
        sys.exit(0 if success else 1)
    
    elif args.command == "list":
        documents = manager.list_documents()
        if documents:
            print(f"📚 Found {len(documents)} documents:")
            for doc in documents:
                status = "✅ Contextualized" if doc.contextualized else "📝 Standard"
                print(f"  📄 {doc.filepath} - {doc.chunk_count} chunks - {status}")
        else:
            print("📭 No documents found")
            
    elif args.command == "info":
        if not args.filepath:
            print("❌ Error: 'info' command requires filepath")
            sys.exit(1)
        info = manager.get_document_info(args.filepath)
        if info:
            print(f"📄 Document: {info.filepath}")
            print(f"📊 Chunks: {info.chunk_count}")
            print(f"🕒 Last Updated: {info.last_updated}")
            print(f"🧠 Contextualized: {info.contextualized}")
        else:
            print(f"❌ Document not found: {args.filepath}")
            sys.exit(1)
            
    elif args.command == "validate":
        issues = manager.validate_documents()
        if any(issues.values()):
            print("❌ Issues found:")
            for issue_type, files in issues.items():
                if files:
                    print(f"  {issue_type}: {len(files)} files")
                    for file in files[:5]:
                        print(f"    - {file}")
                    if len(files) > 5:
                        print(f"    ... and {len(files) - 5} more")
            sys.exit(1)
        else:
            print("✅ All documents validated successfully")
        
    elif args.command == "batch":
        if not args.filepath:
            print("❌ Error: 'batch' command requires filepath to batch JSON file")
            sys.exit(1)
        
        try:
            with open(args.filepath, 'r') as f:
                batch_data = json.load(f)
            
            if isinstance(batch_data, list):
                filepaths = [item if isinstance(item, str) else item.get('filepath') for item in batch_data]
                filepaths = [fp for fp in filepaths if fp]
            else:
                print("❌ Error: Batch file must contain a JSON array")
                sys.exit(1)
            
            contextualize = not args.no_contextualize
            results = manager.add_documents_batch(filepaths, contextualize)
            
            successful = sum(1 for success in results.values() if success)
            print(f"📊 Batch Summary: {successful}/{len(results)} documents processed successfully")
            
            sys.exit(0 if successful == len(results) else 1)
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            sys.exit(1)
    
    elif args.command == "stats":
        stats = manager.get_stats()
        print("📊 Clean Document Manager Statistics:")
        print(f"  📚 Total Documents: {stats['total_documents']}")
        print(f"  📄 Total Chunks: {stats['total_chunks']}")
        print(f"  🧠 Contextualized: {stats['contextualized_documents']}")
        print(f"  📝 Non-contextualized: {stats['non_contextualized_documents']}")
        print(f"  🔧 Max Workers: {stats['config']['max_workers']}")
        print(f"  🏷️  LLM Extraction: {'✅ Enabled' if stats['config']['llm_extraction_enabled'] else '❌ Disabled'}")
        print()
        print("🎯 This is the CLEAN version - 75% smaller than the original!")
        print("   ✅ Removed legacy domain complexity")
        print("   ✅ Removed unused debugging/analysis methods")  
        print("   ✅ Removed complex cleanup/duplication detection")
        print("   ✅ Kept only essential document management functionality")

if __name__ == "__main__":
    main()
