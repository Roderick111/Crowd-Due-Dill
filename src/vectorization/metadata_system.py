#!/usr/bin/env python3
"""
Metadata System for Legal Document Processing

Provides hierarchical metadata extraction and management for legal regulatory documents.
Designed for integration with document_manager.py and contextual_rag.py.

Features:
- Hierarchical metadata structure (Strategy 1)
- LLM-assisted metadata generation (Pattern 1)  
- Multi-level filtering architecture (Pattern 1)
- Simple and straightforward implementation
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path

# Core imports for integration
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document


@dataclass
class DocumentMetadata:
    """Document-level metadata structure"""
    source: str
    domain: str
    title: str
    doc_type: str = "legal_regulation"
    language: str = "en"
    file_size: Optional[int] = None


@dataclass  
class StructuralMetadata:
    """Structural metadata for legal documents"""
    chunk_index: int
    regulation_number: Optional[str] = None
    article_number: Optional[str] = None
    section_level: Optional[str] = None
    hierarchy_depth: Optional[int] = None


@dataclass
class ContentMetadata:
    """Content-based metadata for legal provisions"""
    provision_type: str = "other"  # obligation|prohibition|exemption|definition|other
    entities_affected: List[str] = None
    compliance_level: str = "unknown"  # mandatory|optional|conditional|unknown
    legal_concepts: List[str] = None
    topic_category: Optional[str] = None
    
    def __post_init__(self):
        if self.entities_affected is None:
            self.entities_affected = []
        if self.legal_concepts is None:
            self.legal_concepts = []


@dataclass
class ProcessingMetadata:
    """Processing and system metadata"""
    contextual_enhanced: bool = False
    char_count: int = 0
    extraction_timestamp: str = ""
    ai_metadata_extracted: bool = False
    processing_version: str = "1.0.0"
    
    def __post_init__(self):
        if not self.extraction_timestamp:
            self.extraction_timestamp = datetime.now().isoformat()


class MetadataSchema:
    """
    Step 1: Design Hierarchical Metadata Schema (Strategy 1)
    
    Provides standardized hierarchical metadata structure for legal documents.
    Simple and straightforward implementation with clear separation of concerns.
    """
    
    @staticmethod
    def create_base_metadata(
        filepath: str,
        domain: str, 
        chunk_index: int,
        document_title: str,
        char_count: int = 0
    ) -> Dict[str, Any]:
        """
        Create base hierarchical metadata structure.
        
        Args:
            filepath: Path to the source document
            domain: Document domain (e.g., 'eu_crowdfunding')
            chunk_index: Index of the chunk within the document
            document_title: Human-readable document title
            char_count: Character count of the chunk
            
        Returns:
            Hierarchical metadata dictionary
        """
        
        # Document level metadata
        document_meta = DocumentMetadata(
            source=filepath,
            domain=domain,
            title=document_title,
            doc_type="legal_regulation",
            language="en"
        )
        
        # Structural metadata
        structural_meta = StructuralMetadata(
            chunk_index=chunk_index
        )
        
        # Content metadata (will be filled by LLM later)
        content_meta = ContentMetadata()
        
        # Processing metadata
        processing_meta = ProcessingMetadata(
            char_count=char_count
        )
        
        # Create hierarchical structure
        return {
            "document": asdict(document_meta),
            "structure": asdict(structural_meta), 
            "content": asdict(content_meta),
            "processing": asdict(processing_meta)
        }
    
    @staticmethod
    def create_enhanced_metadata(
        base_metadata: Dict[str, Any],
        legal_metadata: Optional[Dict[str, Any]] = None,
        contextual_enhanced: bool = False
    ) -> Dict[str, Any]:
        """
        Enhance base metadata with LLM-extracted legal metadata.
        
        Args:
            base_metadata: Base hierarchical metadata
            legal_metadata: LLM-extracted legal metadata
            contextual_enhanced: Whether chunk was contextualized
            
        Returns:
            Enhanced hierarchical metadata
        """
        
        enhanced = base_metadata.copy()
        
        # Update structural metadata if available
        if legal_metadata:
            if legal_metadata.get("regulation_number"):
                enhanced["structure"]["regulation_number"] = legal_metadata["regulation_number"]
            if legal_metadata.get("article_number"):
                enhanced["structure"]["article_number"] = legal_metadata["article_number"]
                
            # Update content metadata
            enhanced["content"].update({
                "provision_type": legal_metadata.get("provision_type", "other"),
                "entities_affected": legal_metadata.get("entities_affected", []),
                "compliance_level": legal_metadata.get("compliance_level", "unknown"),
                "legal_concepts": legal_metadata.get("legal_concepts", [])
            })
            
            enhanced["processing"]["ai_metadata_extracted"] = True
        
        # Update processing metadata
        enhanced["processing"]["contextual_enhanced"] = contextual_enhanced
        enhanced["processing"]["extraction_timestamp"] = datetime.now().isoformat()
        
        return enhanced
    
    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]) -> bool:
        """
        Validate metadata structure and required fields.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_sections = ["document", "structure", "content", "processing"]
        
        # Check required sections exist
        for section in required_sections:
            if section not in metadata:
                return False
        
        # Check required document fields
        doc_fields = ["source", "domain", "title"]
        for field in doc_fields:
            if field not in metadata["document"]:
                return False
        
        # Check required structure fields  
        if "chunk_index" not in metadata["structure"]:
            return False
            
        return True
    
    @staticmethod
    def flatten_for_chromadb(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten hierarchical metadata for ChromaDB compatibility.
        
        ChromaDB expects flat metadata with simple values (str, int, float, bool, None).
        This method converts nested dictionaries to dot-notation keys and handles lists.
        
        Args:
            metadata: Hierarchical metadata dictionary
            
        Returns:
            Flattened metadata dictionary compatible with ChromaDB
        """
        flat_metadata = {}
        
        def _flatten_dict(obj: Dict[str, Any], prefix: str = "") -> None:
            for key, value in obj.items():
                new_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    _flatten_dict(value, new_key)
                elif isinstance(value, list):
                    # Convert lists to comma-separated strings for ChromaDB
                    if value:  # Only if list is not empty
                        flat_metadata[new_key] = ",".join(str(item) for item in value)
                    else:
                        flat_metadata[new_key] = ""
                elif value is not None:
                    # Only include non-None values
                    flat_metadata[new_key] = value
        
        _flatten_dict(metadata)
        return flat_metadata


class ChromaDBQueryHelper:
    """
    Multi-Level Filtering Architecture (Pattern 1)
    
    Provides advanced querying capabilities for ChromaDB with hierarchical metadata.
    Simple interface for complex filtering operations.
    """
    
    @staticmethod
    def build_document_filter(**kwargs) -> Dict[str, Any]:
        """Build document-level filters"""
        filters = []
        
        if kwargs.get("domain"):
            filters.append({"document.domain": kwargs["domain"]})
        if kwargs.get("doc_type"):
            filters.append({"document.doc_type": kwargs["doc_type"]})
        if kwargs.get("language"):
            filters.append({"document.language": kwargs["language"]})
            
        return filters
    
    @staticmethod
    def build_structural_filter(**kwargs) -> Dict[str, Any]:
        """Build structure-level filters"""
        filters = []
        
        if kwargs.get("regulation_number"):
            filters.append({"structure.regulation_number": kwargs["regulation_number"]})
        if kwargs.get("article_number"):
            filters.append({"structure.article_number": kwargs["article_number"]})
        
        # Handle article range filters with proper None checking
        min_article = kwargs.get("min_article")
        if min_article is not None and min_article > 0:
            filters.append({"structure.article_number": {"$gte": str(min_article)}})
        
        max_article = kwargs.get("max_article")
        if max_article is not None and max_article > 0:
            filters.append({"structure.article_number": {"$lte": str(max_article)}})
            
        return filters
    
    @staticmethod
    def build_content_filter(**kwargs) -> Dict[str, Any]:
        """Build content-level filters"""
        filters = []
        
        if kwargs.get("provision_type"):
            if isinstance(kwargs["provision_type"], list):
                filters.append({"content.provision_type": {"$in": kwargs["provision_type"]}})
            else:
                filters.append({"content.provision_type": kwargs["provision_type"]})
                
        if kwargs.get("compliance_level"):
            filters.append({"content.compliance_level": kwargs["compliance_level"]})
            
        if kwargs.get("entities_affected"):
            filters.append({"content.entities_affected": {"$contains": kwargs["entities_affected"]}})
            
        if kwargs.get("legal_concepts"):
            filters.append({"content.legal_concepts": {"$contains": kwargs["legal_concepts"]}})
            
        return filters
    
    @staticmethod
    def build_multi_level_filter(**kwargs) -> Dict[str, Any]:
        """
        Build comprehensive multi-level filter combining all levels.
        
        Args:
            **kwargs: Filter parameters for different levels
            
        Returns:
            ChromaDB-compatible filter dictionary
        """
        all_filters = []
        
        # Collect filters from all levels
        all_filters.extend(ChromaDBQueryHelper.build_document_filter(**kwargs))
        all_filters.extend(ChromaDBQueryHelper.build_structural_filter(**kwargs))
        all_filters.extend(ChromaDBQueryHelper.build_content_filter(**kwargs))
        
        # Return appropriate filter structure
        if len(all_filters) == 0:
            return {}
        elif len(all_filters) == 1:
            return all_filters[0]
        else:
            return {"$and": all_filters}
    
    @staticmethod
    def query_with_metadata_filters(
        collection,
        query_text: str,
        n_results: int = 10,
        **filter_kwargs
    ) -> Dict[str, Any]:
        """
        Query ChromaDB collection with multi-level metadata filtering.
        
        Args:
            collection: ChromaDB collection object
            query_text: Query string
            n_results: Number of results to return
            **filter_kwargs: Filter parameters
            
        Returns:
            Query results with metadata
        """
        where_filter = ChromaDBQueryHelper.build_multi_level_filter(**filter_kwargs)
        
        try:
            if where_filter:
                results = collection.query(
                    query_texts=[query_text],
                    where=where_filter,
                    n_results=n_results,
                    include=["metadatas", "documents", "distances"]
                )
            else:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    include=["metadatas", "documents", "distances"]
                )
            
            return {
                "success": True,
                "results": results,
                "filter_applied": where_filter,
                "total_results": len(results.get("documents", [{}])[0] if results.get("documents") else 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "filter_applied": where_filter,
                "total_results": 0
            }


class MetadataManager:
    """
    Central manager for metadata operations.
    
    Provides simple interface for metadata creation, enhancement, and querying.
    Designed for integration with document_manager.py and contextual_rag.py.
    """
    
    def __init__(self):
        self.schema = MetadataSchema()
        self.query_helper = ChromaDBQueryHelper()
    
    def create_chunk_metadata(
        self,
        filepath: str,
        domain: str,
        chunk_index: int,
        document_title: str,
        char_count: int = 0
    ) -> Dict[str, Any]:
        """Create base metadata for a document chunk"""
        return self.schema.create_base_metadata(
            filepath, domain, chunk_index, document_title, char_count
        )
    
    def enhance_metadata(
        self,
        base_metadata: Dict[str, Any],
        legal_metadata: Optional[Dict[str, Any]] = None,
        contextual_enhanced: bool = False
    ) -> Dict[str, Any]:
        """Enhance metadata with LLM-extracted information"""
        return self.schema.create_enhanced_metadata(
            base_metadata, legal_metadata, contextual_enhanced
        )
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata structure"""
        return self.schema.validate_metadata(metadata)
    
    def query_with_filters(
        self,
        collection,
        query_text: str,
        n_results: int = 10,
        **filter_kwargs
    ) -> Dict[str, Any]:
        """Query collection with metadata filters"""
        return self.query_helper.query_with_metadata_filters(
            collection, query_text, n_results, **filter_kwargs
        )
    
    def flatten_metadata_for_chromadb(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten hierarchical metadata for ChromaDB compatibility"""
        return self.schema.flatten_for_chromadb(metadata)


# Export main classes for easy import
__all__ = [
    "MetadataSchema",
    "ChromaDBQueryHelper", 
    "MetadataManager",
    "DocumentMetadata",
    "StructuralMetadata",
    "ContentMetadata",
    "ProcessingMetadata"
] 