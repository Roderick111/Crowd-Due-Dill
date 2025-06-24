"""
Vectorization module for Crowd Due Dill

This module contains the complete vectorization workflow including:
- Step 1: Hierarchical Metadata Schema (COMPLETE)
- Step 2: LLM-Assisted Metadata Extractor (COMPLETE)
- Step 3: Multi-Level Filtering Architecture (PENDING)
- Step 4: Dynamic Metadata Enrichment (PENDING)
"""

# Step 1: Hierarchical Metadata Schema
from .metadata_system import (
    MetadataSchema,
    ChromaDBQueryHelper,
    MetadataManager
)

# Step 2: LLM-Assisted Metadata Extractor
from .metadata_extractor import (
    LegalMetadataExtractor,
    ExtractionConfig,
    RegulationInfo,
    LegalContent,
    ExtractedMetadata,
    extract_legal_metadata,
    extract_batch_metadata
)

__all__ = [
    # Step 1: Hierarchical Metadata Schema
    "MetadataSchema",
    "ChromaDBQueryHelper", 
    "MetadataManager",
    
    # Step 2: LLM-Assisted Metadata Extractor
    "LegalMetadataExtractor",
    "ExtractionConfig",
    "RegulationInfo",
    "LegalContent",
    "ExtractedMetadata",
    "extract_legal_metadata",
    "extract_batch_metadata"
]

__version__ = "1.0.0" 