#!/usr/bin/env python3
"""
Step 2: LLM-Assisted Metadata Extractor

Automatically extracts legal metadata from document chunks using LLM structured output.
Designed for EU regulatory documents with specific focus on:
- Regulation numbers and article identification
- Legal provision classification
- Entity and compliance detection
- Legal concept extraction

Features:
- Pydantic-based structured output
- Retry logic and error handling
- Batch processing capabilities
- Integration with existing metadata system
"""

import re
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from .metadata_system import MetadataManager


# Pydantic schemas for structured LLM output

class DocumentLevelInfo(BaseModel):
    """Document-level metadata that applies to the entire document."""
    regulation_number: Optional[str] = Field(
        default=None,
        description="Official regulation number from document header (e.g., 'EU 2024/358', 'EU 2020/1503')"
    )
    document_type: str = Field(
        default="regulation",
        description="Type of document: 'regulation', 'directive', 'decision', 'recommendation', or 'other'"
    )
    publication_date: Optional[str] = Field(
        default=None,
        description="Publication date if mentioned (e.g., '22.1.2024', '7 October 2020')"
    )
    title: Optional[str] = Field(
        default=None,
        description="Official document title or subject"
    )


class DocumentMetadataExtraction(BaseModel):
    """Complete document-level metadata extraction."""
    document_info: DocumentLevelInfo
    confidence_score: float = Field(
        default=0.0,
        description="Confidence in extraction accuracy (0.0 to 1.0)"
    )
class RegulationInfo(BaseModel):
    """Information about regulation structure (chunk-level only)."""
    article_number: Optional[str] = Field(
        default=None,
        description="Article number if mentioned (e.g., 'Article 23', 'Article 6')"
    )
    section_level: Optional[str] = Field(
        default=None,
        description="Section hierarchy if present (e.g., '1.2.3', '(a)', '(i)')"
    )


class LegalContent(BaseModel):
    """Information about legal content classification."""
    provision_type: str = Field(
        default="other",
        description="Type of legal provision: 'obligation', 'prohibition', 'exemption', 'definition', or 'other'"
    )
    entities_affected: List[str] = Field(
        default_factory=list,
        description="Entities that must comply (e.g., 'crowdfunding_providers', 'investors', 'competent_authorities')"
    )
    compliance_level: str = Field(
        default="unknown",
        description="Compliance requirement level: 'mandatory', 'optional', 'conditional', or 'unknown'"
    )
    legal_concepts: List[str] = Field(
        default_factory=list,
        description="Key legal concepts mentioned (e.g., 'authorization', 'compliance', 'due_diligence')"
    )


class ExtractedMetadata(BaseModel):
    """Complete extracted metadata for a legal document chunk."""
    regulation_info: RegulationInfo
    legal_content: LegalContent
    confidence_score: float = Field(
        default=0.0,
        description="Confidence in extraction accuracy (0.0 to 1.0)"
    )


@dataclass
class ExtractionConfig:
    """Configuration for metadata extraction operations."""
    model_name: str = "gemini-1.5-flash-8b"
    temperature: float = 0.1
    timeout: float = 30.0
    retry_attempts: int = 3
    batch_size: int = 50
    enable_confidence_scoring: bool = True


class LegalMetadataExtractor:
    """
    Step 2: LLM-Assisted Metadata Generation
    
    Extracts structured legal metadata from document chunks using LLM with Pydantic schemas.
    Simple, straightforward implementation focused on EU regulatory documents.
    """
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()
        self.metadata_manager = MetadataManager()
        self._setup_client()
    
    def _setup_client(self):
        """Initialize Google Gen AI client."""
        self.client = genai.Client()
    
    def extract_metadata(
        self, 
        chunk_content: str, 
        document_title: str = "", 
        domain: str = ""
    ) -> Dict[str, Any]:
        """
        Extract metadata from a single chunk with retry logic.
        
        Args:
            chunk_content: Text content of the document chunk
            document_title: Title of the source document
            domain: Domain category (e.g., 'eu_crowdfunding')
            
        Returns:
            Dictionary containing extracted legal metadata
        """
        
        system_prompt = """You are a legal document analysis expert specializing in EU regulations.

Extract structured metadata from legal document chunks with high accuracy.

CHUNK-LEVEL STRUCTURE:
- Find article references: "Article N", "Art. N", etc.
- Identify section hierarchies: numbered/lettered subsections
- DO NOT extract regulation numbers (handled at document level)

LEGAL CONTENT CLASSIFICATION:
- provision_type: Classify as 'obligation' (must do), 'prohibition' (must not do), 'exemption' (exception), 'definition' (defines terms), or 'other'
- entities_affected: Identify who must comply (use standardized terms like 'crowdfunding_providers', 'investors', 'competent_authorities', 'member_states')
- compliance_level: Determine if 'mandatory' (shall/must), 'optional' (may), 'conditional' (if/when), or 'unknown'
- legal_concepts: Extract key legal terms (use standardized terms like 'authorization', 'compliance', 'due_diligence', 'risk_management')

CONFIDENCE SCORING:
- Rate extraction confidence from 0.0 (uncertain) to 1.0 (very confident)
- Consider text clarity, explicit mentions, and context completeness

Be precise and conservative. Return null/empty for unclear information."""

        user_prompt = f"""Document Title: {document_title}
Domain: {domain}

Chunk Content:
{chunk_content}

Extract the structured legal metadata from this chunk."""
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.client.models.generate_content(
                    model=self.config.model_name,
                    contents=[
                        types.Content(role='user', parts=[
                            types.Part.from_text(text=system_prompt + "\n\n" + user_prompt)
                        ])
                    ],
                    config=types.GenerateContentConfig(
                        temperature=self.config.temperature,
                        response_mime_type='application/json',
                        response_schema=ExtractedMetadata,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            maximum_remote_calls=50  # Increased from default 10 to 50
                        ),
                    ),
                )
                
                # Parse the JSON response
                import json
                result_data = json.loads(response.text)
                
                # Convert to our expected format
                extracted_data = {
                    "article_number": result_data.get("regulation_info", {}).get("article_number"),
                    "section_level": result_data.get("regulation_info", {}).get("section_level"),
                    "provision_type": result_data.get("legal_content", {}).get("provision_type", "other"),
                    "entities_affected": result_data.get("legal_content", {}).get("entities_affected", []),
                    "compliance_level": result_data.get("legal_content", {}).get("compliance_level", "unknown"),
                    "legal_concepts": result_data.get("legal_content", {}).get("legal_concepts", []),
                    "confidence_score": result_data.get("confidence_score", 0.0)
                }
                
                # Apply post-processing validation
                validated_data = self._validate_extraction(extracted_data, chunk_content)
                
                return validated_data
                
            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    print(f"⚠️  Extraction attempt {attempt + 1} failed: {e}")
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    print(f"❌ Final extraction attempt failed: {e}")
                    return self._create_fallback_metadata(chunk_content)
    
    def extract_document_metadata(self, document_header: str) -> Dict[str, Any]:
        """
        Extract document-level metadata from document header.
        
        Args:
            document_header: First few chunks or header section of the document
            
        Returns:
            Dictionary containing document-level metadata
        """
        
        system_prompt = """You are a legal document analysis expert specializing in EU regulations.

Extract document-level metadata that applies to the ENTIRE document from the document header.

CRITICAL: Focus ONLY on the PRIMARY regulation that this document IS, not regulations it references or amends.

DOCUMENT HEADER IDENTIFICATION:
- Look for the MAIN regulation number in the very first line: "REGULATION (EU) YYYY/NNNN"
- This is the regulation number of THIS document, not referenced regulations
- Ignore regulation numbers mentioned later in "amending Regulation (EU) X" or similar phrases
- Extract the publication date from the header
- Extract the official document title

EXAMPLES:
- If header says "REGULATION (EU) 2020/1503...amending Regulation (EU) 2017/1129" → PRIMARY is 2020/1503
- If header says "COMMISSION DELEGATED REGULATION (EU) 2024/358" → PRIMARY is 2024/358

Be precise and conservative. Return null for unclear information."""

        user_prompt = f"""Document Header and Opening Section:
{document_header}

Extract the document-level metadata for the PRIMARY regulation that this document represents (not referenced regulations)."""
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.client.models.generate_content(
                    model=self.config.model_name,
                    contents=[
                        types.Content(role='user', parts=[
                            types.Part.from_text(text=system_prompt + "\n\n" + user_prompt)
                        ])
                    ],
                    config=types.GenerateContentConfig(
                        temperature=self.config.temperature,
                        response_mime_type='application/json',
                        response_schema=DocumentMetadataExtraction,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            maximum_remote_calls=50  # Increased from default 10 to 50
                        ),
                    ),
                )
                
                # Parse the JSON response
                import json
                result_data = json.loads(response.text)
                
                # Convert to our expected format
                document_data = {
                    "regulation_number": result_data.get("document_info", {}).get("regulation_number"),
                    "document_type": result_data.get("document_info", {}).get("document_type", "regulation"),
                    "publication_date": result_data.get("document_info", {}).get("publication_date"),
                    "title": result_data.get("document_info", {}).get("title"),
                    "confidence_score": result_data.get("confidence_score", 0.0)
                }
                
                # Apply validation
                validated_data = self._validate_document_extraction(document_data, document_header)
                
                return validated_data
                
            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    print(f"⚠️  Document extraction attempt {attempt + 1} failed: {e}")
                    time.sleep(1 * (attempt + 1))
                else:
                    print(f"❌ Final document extraction attempt failed: {e}")
                    return self._create_fallback_document_metadata(document_header)
    
    def _validate_document_extraction(self, extracted_data: Dict[str, Any], document_header: str) -> Dict[str, Any]:
        """Validate document-level extraction with regex fallbacks."""
        
        # Validate regulation number format
        if extracted_data.get("regulation_number"):
            reg_num = extracted_data["regulation_number"]
            if not re.search(r"EU\s+\d{4}/\d+", reg_num):
                # Try to extract with regex as fallback
                match = re.search(r"REGULATION\s+\(EU\)\s+(\d{4}/\d+)", document_header, re.IGNORECASE)
                if match:
                    extracted_data["regulation_number"] = f"EU {match.group(1)}"
                else:
                    extracted_data["regulation_number"] = None
        
        # If still no regulation number, try more aggressive regex
        if not extracted_data.get("regulation_number"):
            match = re.search(r"(\d{4}/\d+)", document_header[:500])  # Look in first 500 chars
            if match:
                extracted_data["regulation_number"] = f"EU {match.group(1)}"
        
        return extracted_data
    
    def _create_fallback_document_metadata(self, document_header: str) -> Dict[str, Any]:
        """Create fallback document metadata using regex."""
        
        fallback_data = {
            "regulation_number": None,
            "document_type": "regulation",
            "publication_date": None,
            "title": None,
            "confidence_score": 0.1
        }
        
        # Aggressive regex extraction for regulation number (focus on document header)
        # Look for regulation number in the very first line (primary regulation)
        first_line_match = re.search(r"^.*?REGULATION\s+\(EU\)\s+(\d{4}/\d+)", document_header[:100], re.IGNORECASE)
        if first_line_match:
            fallback_data["regulation_number"] = f"EU {first_line_match.group(1)}"
        else:
            # Try broader pattern but still in header
            reg_match = re.search(r"REGULATION\s+\(EU\)\s+(\d{4}/\d+)", document_header[:300], re.IGNORECASE)
            if reg_match:
                fallback_data["regulation_number"] = f"EU {reg_match.group(1)}"
            else:
                # Last resort: any year/number pattern in first 200 chars
                simple_match = re.search(r"(\d{4}/\d+)", document_header[:200])
                if simple_match:
                    fallback_data["regulation_number"] = f"EU {simple_match.group(1)}"
        
        return fallback_data
    
    def _validate_extraction(self, extracted_data: Dict[str, Any], chunk_content: str) -> Dict[str, Any]:
        """
        Validate and enhance extracted metadata using rule-based checks.
        
        Args:
            extracted_data: LLM-extracted metadata
            chunk_content: Original chunk content for validation
            
        Returns:
            Validated and enhanced metadata
        """
        
        # Note: regulation_number is handled at document level, not chunk level
        
        # Validate article number format
        if extracted_data.get("article_number"):
            article = extracted_data["article_number"]
            if not re.search(r"Article\s+\d+", article, re.IGNORECASE):
                # Try regex extraction
                match = re.search(r"Article\s+(\d+)", chunk_content, re.IGNORECASE)
                if match:
                    extracted_data["article_number"] = f"Article {match.group(1)}"
                else:
                    extracted_data["article_number"] = None
        
        # Normalize provision types
        provision_type = extracted_data.get("provision_type", "other").lower()
        valid_types = ["obligation", "prohibition", "exemption", "definition", "other"]
        if provision_type not in valid_types:
            extracted_data["provision_type"] = "other"
        
        # Normalize compliance levels
        compliance_level = extracted_data.get("compliance_level", "unknown").lower()
        valid_levels = ["mandatory", "optional", "conditional", "unknown"]
        if compliance_level not in valid_levels:
            extracted_data["compliance_level"] = "unknown"
        
        # Ensure lists are properly formatted
        if not isinstance(extracted_data.get("entities_affected", []), list):
            extracted_data["entities_affected"] = []
        if not isinstance(extracted_data.get("legal_concepts", []), list):
            extracted_data["legal_concepts"] = []
        
        # Confidence score validation
        confidence = extracted_data.get("confidence_score", 0.0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            extracted_data["confidence_score"] = 0.5  # Default moderate confidence
        
        return extracted_data
    
    def _create_fallback_metadata(self, chunk_content: str) -> Dict[str, Any]:
        """
        Create basic metadata when LLM extraction fails.
        
        Args:
            chunk_content: Original chunk content
            
        Returns:
            Fallback metadata with basic rule-based extraction
        """
        
        fallback_data = {
            "article_number": None,
            "section_level": None,
            "provision_type": "other",
            "entities_affected": [],
            "compliance_level": "unknown",
            "legal_concepts": [],
            "confidence_score": 0.1  # Low confidence for fallback
        }
        
        # Basic regex extraction as fallback (no regulation_number at chunk level)
        
        article_match = re.search(r"Article\s+(\d+)", chunk_content, re.IGNORECASE)
        if article_match:
            fallback_data["article_number"] = f"Article {article_match.group(1)}"
        
        # Basic provision type detection
        if re.search(r"\b(shall|must|required|obliged)\b", chunk_content, re.IGNORECASE):
            fallback_data["provision_type"] = "obligation"
            fallback_data["compliance_level"] = "mandatory"
        elif re.search(r"\b(prohibited|forbidden|not permitted)\b", chunk_content, re.IGNORECASE):
            fallback_data["provision_type"] = "prohibition"
            fallback_data["compliance_level"] = "mandatory"
        elif re.search(r"\b(may|optional|can)\b", chunk_content, re.IGNORECASE):
            fallback_data["compliance_level"] = "optional"
        
        return fallback_data
    
    def combine_metadata(
        self, 
        document_metadata: Dict[str, Any], 
        chunk_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine document-level and chunk-level metadata.
        
        Args:
            document_metadata: Document-level metadata (regulation_number, etc.)
            chunk_metadata: Chunk-level metadata (article_number, etc.)
            
        Returns:
            Combined metadata dictionary
        """
        
        combined = {}
        
        # Document-level metadata (applies to all chunks)
        if document_metadata.get("regulation_number"):
            combined["regulation_number"] = document_metadata["regulation_number"]
        
        # Chunk-level metadata
        combined.update(chunk_metadata)
        
        # Set confidence based on both extractions
        doc_confidence = document_metadata.get("confidence_score", 0.5)
        chunk_confidence = chunk_metadata.get("confidence_score", 0.5)
        combined["confidence_score"] = (doc_confidence + chunk_confidence) / 2
        
        return combined
    
    def extract_batch(
        self, 
        chunks_data: List[Tuple[str, str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Extract metadata from multiple chunks in batch.
        
        Args:
            chunks_data: List of (chunk_content, document_title, domain) tuples
            
        Returns:
            List of extracted metadata dictionaries
        """
        
        print(f"🚀 Starting batch metadata extraction for {len(chunks_data)} chunks...")
        start_time = time.time()
        
        results = []
        successful_extractions = 0
        
        for i, (chunk_content, document_title, domain) in enumerate(chunks_data):
            print(f"📊 Processing chunk {i+1}/{len(chunks_data)}")
            
            try:
                metadata = self.extract_metadata(chunk_content, document_title, domain)
                results.append(metadata)
                
                if metadata.get("confidence_score", 0) > 0.3:  # Reasonable confidence threshold
                    successful_extractions += 1
                    
            except Exception as e:
                print(f"❌ Error processing chunk {i+1}: {e}")
                results.append(self._create_fallback_metadata(chunk_content))
        
        processing_time = time.time() - start_time
        success_rate = (successful_extractions / len(chunks_data)) * 100 if chunks_data else 0
        
        print(f"✅ Batch extraction completed in {processing_time:.2f}s")
        print(f"📈 Success rate: {success_rate:.1f}% ({successful_extractions}/{len(chunks_data)})")
        
        return results
    
    def enhance_existing_metadata(
        self, 
        base_metadata: Dict[str, Any], 
        chunk_content: str,
        document_title: str = "",
        domain: str = ""
    ) -> Dict[str, Any]:
        """
        Enhance existing hierarchical metadata with LLM-extracted legal information.
        
        Args:
            base_metadata: Existing hierarchical metadata from metadata system
            chunk_content: Text content for extraction
            document_title: Document title
            domain: Domain category
            
        Returns:
            Enhanced metadata with LLM-extracted legal information
        """
        
        # Extract legal metadata
        legal_metadata = self.extract_metadata(chunk_content, document_title, domain)
        
        # Enhance using metadata manager
        enhanced_metadata = self.metadata_manager.enhance_metadata(
            base_metadata=base_metadata,
            legal_metadata=legal_metadata,
            contextual_enhanced=True
        )
        
        return enhanced_metadata
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about extraction performance.
        
        Returns:
            Dictionary with extraction statistics
        """
        
        return {
            "extractor_config": {
                "model_name": self.config.model_name,
                "temperature": self.config.temperature,
                "retry_attempts": self.config.retry_attempts,
                "batch_size": self.config.batch_size
            },
            "supported_extractions": {
                "regulation_numbers": True,
                "article_numbers": True,
                "provision_types": ["obligation", "prohibition", "exemption", "definition", "other"],
                "compliance_levels": ["mandatory", "optional", "conditional", "unknown"],
                "entity_recognition": True,
                "concept_extraction": True,
                "confidence_scoring": self.config.enable_confidence_scoring
            }
        }


# Convenience functions for easy integration
def extract_legal_metadata(
    chunk_content: str, 
    document_title: str = "", 
    domain: str = "",
    config: Optional[ExtractionConfig] = None
) -> Dict[str, Any]:
    """
    Convenience function for single chunk metadata extraction.
    
    Args:
        chunk_content: Text content to analyze
        document_title: Source document title
        domain: Domain category
        config: Optional extraction configuration
        
    Returns:
        Extracted legal metadata dictionary
    """
    
    extractor = LegalMetadataExtractor(config)
    return extractor.extract_metadata(chunk_content, document_title, domain)


def extract_batch_metadata(
    chunks_data: List[Tuple[str, str, str]],
    config: Optional[ExtractionConfig] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for batch metadata extraction.
    
    Args:
        chunks_data: List of (chunk_content, document_title, domain) tuples
        config: Optional extraction configuration
        
    Returns:
        List of extracted metadata dictionaries
    """
    
    extractor = LegalMetadataExtractor(config)
    return extractor.extract_batch(chunks_data)


# Export main classes and functions
__all__ = [
    "LegalMetadataExtractor",
    "ExtractionConfig",
    "RegulationInfo",
    "LegalContent", 
    "ExtractedMetadata",
    "extract_legal_metadata",
    "extract_batch_metadata"
] 