#!/usr/bin/env python3
"""
Test script for document-level metadata extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vectorization.metadata_extractor import LegalMetadataExtractor

def test_document_level_extraction():
    """Test document-level metadata extraction on RTS document"""
    
    # Read the RTS document header
    with open("docs/content/rts.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Take first 1000 characters as document header
    document_header = content[:1000]
    print("📄 Document Header Preview:")
    print("=" * 50)
    print(document_header)
    print("=" * 50)
    
    # Initialize extractor
    extractor = LegalMetadataExtractor()
    
    # Extract document-level metadata
    print("\n🔍 Extracting document-level metadata...")
    document_metadata = extractor.extract_document_metadata(document_header)
    
    print("\n📋 Document-Level Metadata Results:")
    print("=" * 50)
    for key, value in document_metadata.items():
        print(f"{key}: {value}")
    print("=" * 50)
    
    # Test chunk-level extraction (should not include regulation_number)
    print("\n🧩 Testing chunk-level extraction...")
    chunk_content = """
    Article 6
    Credit risk assessment
    
    Crowdfunding service providers shall assess the credit risk of project owners by evaluating their creditworthiness, including their ability to repay loans.
    """
    
    chunk_metadata = extractor.extract_metadata(
        chunk_content=chunk_content,
        document_title="RTS",
        domain="eu_crowdfunding"
    )
    
    print("\n📊 Chunk-Level Metadata Results:")
    print("=" * 50)
    for key, value in chunk_metadata.items():
        print(f"{key}: {value}")
    print("=" * 50)
    
    # Test combination
    print("\n🔗 Testing metadata combination...")
    combined_metadata = extractor.combine_metadata(
        document_metadata=document_metadata,
        chunk_metadata=chunk_metadata
    )
    
    print("\n✅ Combined Metadata Results:")
    print("=" * 50)
    for key, value in combined_metadata.items():
        print(f"{key}: {value}")
    print("=" * 50)
    
    # Validation
    print("\n🧪 Validation Results:")
    print("=" * 30)
    
    expected_regulation = "EU 2024/358"
    actual_regulation = document_metadata.get("regulation_number")
    
    if actual_regulation == expected_regulation:
        print(f"✅ PASS: Regulation number correctly extracted: {actual_regulation}")
    else:
        print(f"❌ FAIL: Expected '{expected_regulation}', got '{actual_regulation}'")
    
    if "regulation_number" not in chunk_metadata:
        print("✅ PASS: Chunk-level extraction correctly excludes regulation_number")
    else:
        print(f"❌ FAIL: Chunk-level should not include regulation_number, but got: {chunk_metadata.get('regulation_number')}")
    
    if combined_metadata.get("regulation_number") == expected_regulation:
        print(f"✅ PASS: Combined metadata has correct regulation number: {combined_metadata.get('regulation_number')}")
    else:
        print(f"❌ FAIL: Combined metadata regulation number incorrect: {combined_metadata.get('regulation_number')}")
    
    if combined_metadata.get("article_number"):
        print(f"✅ PASS: Combined metadata includes chunk-level article: {combined_metadata.get('article_number')}")
    else:
        print("⚠️  WARNING: No article number found in combined metadata")

if __name__ == "__main__":
    test_document_level_extraction() 