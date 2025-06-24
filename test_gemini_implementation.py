#!/usr/bin/env python3
"""
Test script to verify Gemini 2.0 Flash implementation
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.vectorization.metadata_extractor import LegalMetadataExtractor, ExtractionConfig
from tools.document_manager import SimpleDocumentManager, ProcessingConfig

def test_metadata_extraction():
    """Test the Gemini-based metadata extraction"""
    print("🧪 Testing Metadata Extraction with Gemini 2.0 Flash...")
    
    # Sample legal text
    sample_text = """
    Article 23 - Authorization requirements
    
    1. Crowdfunding service providers shall obtain authorization from the competent authority 
    before providing crowdfunding services.
    
    2. The authorization shall be valid throughout the Union.
    """
    
    try:
        # Initialize extractor
        config = ExtractionConfig(model_name="gemini-2.0-flash-001")
        extractor = LegalMetadataExtractor(config=config)
        
        # Extract metadata
        result = extractor.extract_metadata(
            chunk_content=sample_text,
            document_title="EU Crowdfunding Regulation",
            domain="eu_crowdfunding"
        )
        
        print("✅ Metadata extraction successful!")
        print(f"📋 Article number: {result.get('article_number')}")
        print(f"📋 Provision type: {result.get('provision_type')}")
        print(f"📋 Compliance level: {result.get('compliance_level')}")
        print(f"📋 Entities affected: {result.get('entities_affected')}")
        print(f"📋 Confidence score: {result.get('confidence_score')}")
        return True
        
    except Exception as e:
        print(f"❌ Metadata extraction failed: {e}")
        return False

def test_document_metadata():
    """Test document-level metadata extraction"""
    print("\n🧪 Testing Document Metadata Extraction...")
    
    document_header = """
    REGULATION (EU) 2020/1503 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL
    
    of 7 October 2020
    
    on European crowdfunding service providers for business, and amending Regulation (EU) 2017/1129 
    and Directive (EU) 2019/1937
    """
    
    try:
        config = ExtractionConfig(model_name="gemini-2.0-flash-001")
        extractor = LegalMetadataExtractor(config=config)
        
        result = extractor.extract_document_metadata(document_header)
        
        print("✅ Document metadata extraction successful!")
        print(f"📋 Regulation number: {result.get('regulation_number')}")
        print(f"📋 Document type: {result.get('document_type')}")
        print(f"📋 Publication date: {result.get('publication_date')}")
        print(f"📋 Title: {result.get('title')}")
        return True
        
    except Exception as e:
        print(f"❌ Document metadata extraction failed: {e}")
        return False

def test_contextualization():
    """Test the Gemini-based contextualization"""
    print("\n🧪 Testing Contextualization with Gemini 2.0 Flash...")
    
    try:
        # Initialize document manager
        config = ProcessingConfig(max_workers=1, retry_attempts=1)
        manager = SimpleDocumentManager(config=config)
        
        # Test contextualization
        chunk_data = (
            0,  # chunk_index
            "Crowdfunding service providers shall maintain adequate capital reserves.",  # chunk_content
            "EU Crowdfunding Regulation",  # document_title
            "eu_crowdfunding"  # domain
        )
        
        result = manager._contextualize_chunk_with_retry(chunk_data)
        chunk_index, content, char_count, success = result
        
        if success:
            print("✅ Contextualization successful!")
            print(f"📋 Contextualized content length: {char_count}")
            print(f"📋 Content preview: {content[:200]}...")
            return True
        else:
            print("❌ Contextualization failed")
            return False
            
    except Exception as e:
        print(f"❌ Contextualization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Gemini 2.0 Flash Implementation")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY') and not os.getenv('GOOGLE_GENAI_API_KEY'):
        print("⚠️  Warning: No Google API key found in environment variables.")
        print("   Set GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY to test with real API.")
        print("   Proceeding with test (may fail without API key)...")
    
    results = []
    
    # Run tests
    results.append(test_metadata_extraction())
    results.append(test_document_metadata())
    results.append(test_contextualization())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! Gemini 2.0 Flash implementation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 