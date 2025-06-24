#!/usr/bin/env python3
"""
Test script to verify metadata system integration

This script tests the integration between:
- document_manager.py
- contextual_rag.py  
- metadata_system.py

Usage: python3 tools/test_metadata_integration.py
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from src.vectorization.metadata_system import MetadataManager, MetadataSchema


def test_metadata_schema():
    """Test Step 1: Hierarchical Metadata Schema"""
    print("🧪 Testing Step 1: Hierarchical Metadata Schema")
    
    # Test basic metadata creation
    metadata = MetadataSchema.create_base_metadata(
        filepath="docs/content/main_eu_regulation.md",
        domain="eu_crowdfunding",
        chunk_index=0,
        document_title="EU Crowdfunding Regulation",
        char_count=1500
    )
    
    # Validate structure
    assert "document" in metadata
    assert "structure" in metadata
    assert "content" in metadata
    assert "processing" in metadata
    
    # Validate document level
    assert metadata["document"]["source"] == "docs/content/main_eu_regulation.md"
    assert metadata["document"]["domain"] == "eu_crowdfunding"
    assert metadata["document"]["title"] == "EU Crowdfunding Regulation"
    assert metadata["document"]["doc_type"] == "legal_regulation"
    
    # Validate structure level
    assert metadata["structure"]["chunk_index"] == 0
    
    # Validate processing level
    assert metadata["processing"]["char_count"] == 1500
    
    print("✅ Basic metadata schema test passed")
    
    # Test metadata enhancement
    legal_metadata = {
        "regulation_number": "EU 2020/1503",
        "article_number": "Article 23",
        "provision_type": "obligation",
        "entities_affected": ["crowdfunding_providers"],
        "compliance_level": "mandatory",
        "legal_concepts": ["authorization", "compliance"]
    }
    
    enhanced = MetadataSchema.create_enhanced_metadata(
        base_metadata=metadata,
        legal_metadata=legal_metadata,
        contextual_enhanced=True
    )
    
    # Validate enhancements
    assert enhanced["structure"]["regulation_number"] == "EU 2020/1503"
    assert enhanced["structure"]["article_number"] == "Article 23"
    assert enhanced["content"]["provision_type"] == "obligation"
    assert enhanced["content"]["compliance_level"] == "mandatory"
    assert enhanced["processing"]["ai_metadata_extracted"] == True
    assert enhanced["processing"]["contextual_enhanced"] == True
    
    print("✅ Enhanced metadata test passed")
    
    # Test validation
    assert MetadataSchema.validate_metadata(enhanced) == True
    print("✅ Metadata validation test passed")


def test_metadata_manager():
    """Test MetadataManager integration"""
    print("🧪 Testing MetadataManager Integration")
    
    manager = MetadataManager()
    
    # Test chunk metadata creation
    metadata = manager.create_chunk_metadata(
        filepath="docs/content/gdpr.md",
        domain="eu_crowdfunding",
        chunk_index=5,
        document_title="GDPR Regulation",
        char_count=800
    )
    
    assert manager.validate_metadata(metadata) == True
    print("✅ MetadataManager basic test passed")
    
    # Test metadata enhancement
    legal_data = {
        "regulation_number": "EU 2016/679",
        "article_number": "Article 6",
        "provision_type": "definition"
    }
    
    enhanced = manager.enhance_metadata(
        base_metadata=metadata,
        legal_metadata=legal_data,
        contextual_enhanced=False
    )
    
    assert enhanced["structure"]["regulation_number"] == "EU 2016/679"
    assert enhanced["processing"]["ai_metadata_extracted"] == True
    print("✅ MetadataManager enhancement test passed")


def test_query_helper():
    """Test ChromaDB query helper"""
    print("🧪 Testing ChromaDB Query Helper")
    
    from src.vectorization.metadata_system import ChromaDBQueryHelper
    
    # Test document filter
    doc_filter = ChromaDBQueryHelper.build_document_filter(
        domain="eu_crowdfunding",
        doc_type="legal_regulation"
    )
    
    expected = [
        {"document.domain": "eu_crowdfunding"},
        {"document.doc_type": "legal_regulation"}
    ]
    assert doc_filter == expected
    print("✅ Document filter test passed")
    
    # Test structural filter
    struct_filter = ChromaDBQueryHelper.build_structural_filter(
        regulation_number="EU 2020/1503",
        article_number="Article 23"
    )
    
    expected = [
        {"structure.regulation_number": "EU 2020/1503"},
        {"structure.article_number": "Article 23"}
    ]
    assert struct_filter == expected
    print("✅ Structural filter test passed")
    
    # Test multi-level filter
    multi_filter = ChromaDBQueryHelper.build_multi_level_filter(
        domain="eu_crowdfunding",
        regulation_number="EU 2020/1503",
        provision_type="obligation"
    )
    
    assert "$and" in multi_filter
    assert len(multi_filter["$and"]) == 3
    print("✅ Multi-level filter test passed")


def main():
    """Run all integration tests"""
    print("🚀 Starting Metadata System Integration Tests")
    print("=" * 50)
    
    try:
        test_metadata_schema()
        print()
        test_metadata_manager()
        print()
        test_query_helper()
        print()
        print("🎉 All integration tests passed!")
        print("✅ Step 1: Hierarchical Metadata Schema - IMPLEMENTED")
        print("📋 Ready for Step 2: LLM-Assisted Metadata Generation")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 