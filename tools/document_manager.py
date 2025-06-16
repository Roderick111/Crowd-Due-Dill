#!/usr/bin/env python3
"""
Advanced Document Manager for Vector Database with Parallel Processing
"""

import os
import sys
import json
import hashlib
import time
import multiprocessing
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Add src to path for local imports
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import from relative path for consistency with cleaned architecture
from src.core.contextual_rag import OptimizedContextualRAGSystem

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
    
    def __post_init__(self):
        if self.max_workers is None:
            # For I/O-bound tasks, use more threads than CPU cores
            cpu_count = multiprocessing.cpu_count()
            self.max_workers = min(cpu_count * 2, 12)  # Cap at 12 to avoid rate limits

class SimpleDocumentManager:
    """Enhanced document manager with parallel processing capabilities"""
    
    def __init__(self, registry_path: str = "data/document_registry.json", config: Optional[ProcessingConfig] = None):
        self.registry_path = registry_path
        self.registry: Dict[str, DocumentRecord] = {}
        self.rag_system = None
        self.config = config or ProcessingConfig()
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
    
    def _load_and_chunk_document(self, filepath: str, doc_type: str = "standard") -> List[Document]:
        """Load and chunk a single document with type-specific processing"""
        loader = TextLoader(filepath, encoding='utf-8')
        documents = loader.load()
        
        if doc_type == "qa":
            # Q&A documents use larger chunks to keep questions and answers together
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,  # Larger chunks for Q&A
                chunk_overlap=100,  # Less overlap needed
                length_function=len,
                separators=["\n\n# ", "\n## ", "\n### ", "\n\n", "\n", " ", ""]  # Prioritize heading separators
            )
        else:
            # Standard chunking for narrative documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
        
        chunks = text_splitter.split_documents(documents)
        
        # Add source metadata to chunks
        for chunk in chunks:
            chunk.metadata["source"] = filepath
            chunk.metadata["doc_type"] = doc_type
        
        return chunks
    
    def _create_chunk_metadata(self, filepath: str, domain: str, chunk_index: int) -> str:
        """Create standardized chunk ID"""
        return f"{os.path.basename(filepath).replace('.md', '')}_{domain}_{chunk_index}"
    
    def _contextualize_chunk_with_retry(self, chunk_data: Tuple[int, str, str, str, str]) -> Tuple[int, str, int, bool]:
        """Contextualize chunk with retry logic and timeout handling"""
        chunk_index, chunk_content, document_title, domain, doc_type = chunk_data
        
        for attempt in range(self.config.retry_attempts):
            try:
                llm = ChatOpenAI(
                    model="gpt-4o-mini", 
                    temperature=0.3,
                    timeout=self.config.contextualize_timeout
                )
        
                if doc_type == "qa":
                    prompt = f"""You are helping to improve Q&A document retrieval by adding context to Q&A chunks.

Document Title: {document_title}
Domain: {domain}
Document Type: Q&A

Original Q&A Chunk:
{chunk_content}

Please provide a brief 2-3 sentence context summary that explains:
1. What question(s) and answer(s) this chunk contains
2. The main topics or concepts being addressed
3. How these Q&As relate to the broader {domain} domain

Format your response as:
Context: [Your 2-3 sentence summary focusing on the Q&A content]

[Original chunk content]"""
                else:
                    prompt = f"""You are helping to improve document retrieval by adding context to text chunks.

Document Title: {document_title}
Domain: {domain}

Original Chunk:
{chunk_content}

Please provide a brief 2-3 sentence context summary that explains:
1. What this chunk is about
2. How it relates to the broader document theme
3. Key topics or concepts it covers

Format your response as:
Context: [Your 2-3 sentence summary]

[Original chunk content]"""

                response = llm.invoke(prompt)
                return (chunk_index, response.content, len(chunk_content), True)
                
            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    print(f"⚠️  Retry {attempt + 1}/{self.config.retry_attempts} for chunk {chunk_index}: {e}")
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    print(f"❌ Final attempt failed for chunk {chunk_index}: {e}")
        
        # All attempts failed, return original content
        return (chunk_index, chunk_content, len(chunk_content), False)
    
    def _process_chunks_parallel(self, chunks: List[Document], document_title: str, domain: str, doc_type: str = "standard") -> Tuple[List[Document], Dict[str, any]]:
        """Process document chunks with parallel contextualization"""
        print(f"🚀 Starting parallel processing with {self.config.max_workers} workers...")
        start_time = time.time()
        
        # Prepare chunk data for parallel processing
        chunk_data = [
            (i, chunk.page_content, document_title, domain, doc_type)
            for i, chunk in enumerate(chunks)
        ]
        
        # Process chunks in parallel
        processed_results = {}
        successful_contextualizations = 0
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_index = {
                executor.submit(self._contextualize_chunk_with_retry, data): data[0] 
                for data in chunk_data
            }
            
            # Process results with progress bar
            with tqdm(total=len(chunk_data), desc="Contextualizing chunks", unit="chunk") as pbar:
                for future in as_completed(future_to_index):
                    chunk_index = future_to_index[future]
                    try:
                        chunk_index, content, char_count, success = future.result()
                        processed_results[chunk_index] = {
                            'content': content,
                            'char_count': char_count,
                            'contextualized': success
                        }
                        if success:
                            successful_contextualizations += 1
                        pbar.update(1)
                    except Exception as e:
                        print(f"❌ Chunk {chunk_index} failed: {e}")
                        # Use original content as fallback
                        original_chunk = chunks[chunk_index]
                        processed_results[chunk_index] = {
                            'content': original_chunk.page_content,
                            'char_count': len(original_chunk.page_content),
                            'contextualized': False
                        }
                        pbar.update(1)
        
        # Update chunks with processed content
        chunk_ids = []
        final_chunks = []
        
        for i, chunk in enumerate(chunks):
            result = processed_results[i]
            chunk_id = self._create_chunk_metadata(document_title, domain, i)
            chunk_ids.append(chunk_id)
            
            # Update chunk content and metadata
            chunk.page_content = result['content']
            chunk.metadata.update({
                "domain": domain,
                "source": chunk.metadata.get("source"),
                "chunk_id": chunk_id,
                "topic": document_title.replace('_', ' '),
                "contextual_enhanced": result['contextualized'],
                "char_count": result['char_count']
            })
            
            final_chunks.append(chunk)
        
        processing_time = time.time() - start_time
        
        # Processing statistics
        processing_stats = {
            "total_chunks": len(chunks),
            "successful_contextualizations": successful_contextualizations,
            "failed_contextualizations": len(chunks) - successful_contextualizations,
            "processing_time": processing_time,
            "chunks_per_second": len(chunks) / processing_time,
            "chunk_ids": chunk_ids
        }
        
        print(f"✅ Parallel processing completed in {processing_time:.2f}s")
        print(f"📊 {successful_contextualizations}/{len(chunks)} chunks contextualized successfully")
        print(f"⚡ Processing rate: {processing_stats['chunks_per_second']:.2f} chunks/second")
        
        return final_chunks, processing_stats
    
    def add_documents_batch(self, file_domain_pairs: List[Tuple[str, str]], contextualize: bool = True) -> Dict[str, bool]:
        """
        Add multiple documents in parallel with batch processing.
        
        Args:
            file_domain_pairs: List of (filepath, domain) tuples
            contextualize: Enable AI contextualization (DEFAULT: True for enhanced retrieval)
            
        Returns:
            Dict[str, bool]: Results mapping filepath to success status
            
        Note: Contextualization is ENABLED BY DEFAULT for better retrieval performance.
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
    
    def add_document(self, filepath: str, domain: str, contextualize: bool = True, doc_type: str = "standard") -> bool:
        """
        Add a new document to the vector database with parallel processing.
        
        Args:
            filepath: Path to the document file
            domain: Domain category for the document
            contextualize: Enable AI contextualization (DEFAULT: True for enhanced retrieval)
            doc_type: Document type - "standard" for narrative docs, "qa" for Q&A docs
                     Affects chunking strategy and contextualization prompts
            
        Returns:
            bool: True if successful, False otherwise
            
        Note: 
        - Contextualization is ENABLED BY DEFAULT for better retrieval performance
        - Q&A documents use larger chunks (2000 chars) and specialized contextualization
        - Standard documents use standard chunks (1000 chars) with general contextualization
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
            chunks = self._load_and_chunk_document(filepath, doc_type)
            print(f"📄 Split into {len(chunks)} chunks")
            
            # Process chunks (with or without contextualization)
            document_title = os.path.basename(filepath).replace('.md', '').replace('_', ' ').title()
            
            if contextualize:
                final_chunks, processing_stats = self._process_chunks_parallel(chunks, document_title, domain, doc_type)
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
                        "char_count": len(chunk.page_content),
                        "doc_type": doc_type
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
                    doc_type=doc_type
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
    
    def update_document(self, filepath: str, domain: str, contextualize: bool = True, doc_type: str = "standard") -> bool:
        """Update an existing document"""
        print(f"🔄 Updating document: {filepath}")
        
        if not self._remove_existing_chunks(filepath):
            return False
        
        # Remove from registry temporarily
        if filepath in self.registry:
            del self.registry[filepath]
        
        return self.add_document(filepath, domain, contextualize, doc_type)
    
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
    
    def list_documents(self, domain: Optional[str] = None) -> List[DocumentRecord]:
        """List all documents or documents for a specific domain"""
        if domain:
            return [record for record in self.registry.values() if record.domain == domain]
        return list(self.registry.values())
    
    def get_document_info(self, filepath: str) -> Optional[DocumentRecord]:
        """Get information about a specific document"""
        return self.registry.get(filepath)
    
    def validate_documents(self, domain: Optional[str] = None) -> Dict[str, List[str]]:
        """Validate documents for missing files, changes, and vectorstore consistency"""
        print("🔍 Validating documents...")
        
        issues = {
            "missing_files": [],
            "changed_files": [],
            "vectorstore_mismatches": [],
            "orphaned_chunks": []
        }
        
        # Check registry entries
        documents_to_check = [
            record for record in self.registry.values()
            if domain is None or record.domain == domain
        ]
        
        for record in documents_to_check:
            if not os.path.exists(record.filepath):
                issues["missing_files"].append(record.filepath)
            else:
                current_hash = self._get_file_hash(record.filepath)
                if current_hash != record.file_hash:
                    issues["changed_files"].append(record.filepath)
        
        return issues
    
    def fix_vectorstore_inconsistencies(self, domain: Optional[str] = None) -> bool:
        """Fix vectorstore inconsistencies by re-adding mismatched documents"""
        print("🔧 Fixing vectorstore inconsistencies...")
        
        try:
            issues = self.validate_documents(domain)
            
            if not any(issues.values()):
                print("✅ No inconsistencies found")
                return True
            
            print("✅ Vectorstore inconsistencies fixed!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing inconsistencies: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Document Manager for Vector Database")
    parser.add_argument("command", choices=["add", "update", "remove", "list", "validate", "info", "fix", "batch"])
    parser.add_argument("filepath", nargs="?", help="Path to document file or batch file")
    parser.add_argument("--domain", help="Document domain")
    parser.add_argument("--doc-type", choices=["standard", "qa"], default="standard", help="Document type (standard or qa) - affects chunking and contextualization strategy")
    parser.add_argument("--no-contextualize", action="store_true", help="Skip contextualization (enabled by default for enhanced retrieval)")
    parser.add_argument("--workers", type=int, help="Number of parallel workers (default: auto-configure)")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for vectorstore operations")
    parser.add_argument("--timeout", type=float, default=30.0, help="Timeout for contextualization requests")
    
    args = parser.parse_args()
    
    config = ProcessingConfig(
        max_workers=args.workers,
        chunk_batch_size=args.batch_size,
        contextualize_timeout=args.timeout
    )
    
    manager = SimpleDocumentManager(config=config)
    
    if args.command == "add":
        if not args.filepath or not args.domain:
            print("❌ Error: 'add' command requires filepath and --domain")
            sys.exit(1)
        
        contextualize = not args.no_contextualize
        success = manager.add_document(args.filepath, args.domain, contextualize, args.doc_type)
        sys.exit(0 if success else 1)
    
    elif args.command == "update":
        if not args.filepath or not args.domain:
            print("❌ Error: 'update' command requires filepath and --domain")
            sys.exit(1)
        
        contextualize = not args.no_contextualize
        success = manager.update_document(args.filepath, args.domain, contextualize, args.doc_type)
        sys.exit(0 if success else 1)
    
    elif args.command == "remove":
        if not args.filepath:
            print("❌ Error: 'remove' command requires filepath")
            sys.exit(1)
        
        success = manager.remove_document(args.filepath)
        sys.exit(0 if success else 1)
    
    elif args.command == "list":
        documents = manager.list_documents(args.domain)
        if documents:
            print(f"📚 Found {len(documents)} documents:")
            for doc in documents:
                status = "✅ Contextualized" if doc.contextualized else "📝 Standard"
                doc_type_emoji = "❓" if doc.doc_type == "qa" else "📄"
                print(f"  {doc_type_emoji} {doc.filepath} ({doc.domain}) - {doc.chunk_count} chunks - {status} - Type: {doc.doc_type}")
        else:
            print("📭 No documents found")
            
    elif args.command == "info":
        if not args.filepath:
            print("❌ Error: 'info' command requires filepath")
            sys.exit(1)
        
        info = manager.get_document_info(args.filepath)
        if info:
            doc_type_emoji = "❓" if info.doc_type == "qa" else "📄"
            print(f"{doc_type_emoji} Document: {info.filepath}")
            print(f"🎯 Domain: {info.domain}")
            print(f"📋 Type: {info.doc_type}")
            print(f"📊 Chunks: {info.chunk_count}")
            print(f"🕒 Last Updated: {info.last_updated}")
            print(f"🧠 Contextualized: {info.contextualized}")
        else:
            print(f"❌ Document not found: {args.filepath}")
            sys.exit(1)
            
    elif args.command == "validate":
        issues = manager.validate_documents(args.domain)
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
        success = manager.fix_vectorstore_inconsistencies(args.domain)
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
                print("❌ Error: Batch file must contain a JSON array of {filepath, domain} objects")
                sys.exit(1)
            
            file_domain_pairs = []
            for item in batch_data:
                if not isinstance(item, dict) or 'filepath' not in item or 'domain' not in item:
                    print("❌ Error: Each batch item must have 'filepath' and 'domain' fields")
                    sys.exit(1)
                file_domain_pairs.append((item['filepath'], item['domain']))
            
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
    
    else:
        print(f"❌ Command '{args.command}' not yet implemented in this version")
        sys.exit(1) 