#!/usr/bin/env python3
"""
Test Suite for Step 2: LLM-Assisted Metadata Extractor

Comprehensive tests for the legal metadata extraction functionality including:
- Basic extraction functionality
- Pydantic schema validation
- Retry logic and error handling
- Batch processing
- Integration with hierarchical metadata system
- Performance and accuracy validation
"""

import sys
import os
import time
import json
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vectorization.metadata_extractor import (
    LegalMetadataExtractor,
    ExtractionConfig,
    RegulationInfo,
    LegalContent,
    ExtractedMetadata,
    extract_legal_metadata,
    extract_batch_metadata
)
from vectorization.metadata_system import MetadataSchema, MetadataManager


class TestMetadataExtractor:
    """Test suite for LLM-Assisted Metadata Extractor."""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Sample legal text for testing
        self.sample_texts = {
            "crowdfunding_regulation": """
            REGULATION (EU) 2020/1503 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL
            
            Article 23 - Authorization of crowdfunding service providers
            
            1. Crowdfunding service providers shall be authorized by the competent authority 
            of the Member State where they have their registered office before providing 
            crowdfunding services in the Union.
            
            2. The authorization shall be valid throughout the Union and shall allow the 
            crowdfunding service provider to provide crowdfunding services in all Member States.
            """,
            
            "gdpr_article": """
            REGULATION (EU) 2016/679 - General Data Protection Regulation
            
            Article 6 - Lawfulness of processing
            
            1. Processing shall be lawful only if and to the extent that at least one of the 
            following applies:
            (a) the data subject has given consent to the processing of his or her personal data;
            (b) processing is necessary for the performance of a contract;
            """,
            
            "definition_text": """
            For the purposes of this Regulation, the following definitions apply:
            
            (a) 'crowdfunding service' means the matching of business funding interests of 
            investors and project owners through the use of a crowdfunding platform;
            
            (b) 'crowdfunding platform' means an electronic information system operated or 
            managed by a crowdfunding service provider;
            """,
            
            "prohibition_text": """
            Article 15 - Prohibited activities
            
            Crowdfunding service providers shall not:
            (a) provide investment advice or recommendations concerning crowdfunding offers;
            (b) hold client funds or client financial instruments;
            (c) grant credits or loans to investors or project owners;
            """
        }
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results."""
        self.total_tests += 1
        
        try:
            print(f"\n🧪 Running test: {test_name}")
            start_time = time.time()
            
            result = test_func()
            
            execution_time = time.time() - start_time
            
            if result:
                print(f"✅ {test_name} PASSED ({execution_time:.2f}s)")
                self.passed_tests += 1
                self.test_results.append({
                    "test": test_name,
                    "status": "PASSED",
                    "execution_time": execution_time
                })
                return True
            else:
                print(f"❌ {test_name} FAILED ({execution_time:.2f}s)")
                self.test_results.append({
                    "test": test_name,
                    "status": "FAILED",
                    "execution_time": execution_time
                })
                return False
                
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            self.test_results.append({
                "test": test_name,
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    def test_pydantic_schemas(self) -> bool:
        """Test Pydantic schema definitions and validation."""
        print("  📋 Testing Pydantic schemas...")
        
        # Test RegulationInfo schema
        regulation_info = RegulationInfo(
            regulation_number="EU 2020/1503",
            article_number="Article 23",
            section_level="1.2.3"
        )
        
        assert regulation_info.regulation_number == "EU 2020/1503"
        assert regulation_info.article_number == "Article 23"
        assert regulation_info.section_level == "1.2.3"
        
        # Test LegalContent schema
        legal_content = LegalContent(
            provision_type="obligation",
            entities_affected=["crowdfunding_providers", "competent_authorities"],
            compliance_level="mandatory",
            legal_concepts=["authorization", "compliance"]
        )
        
        assert legal_content.provision_type == "obligation"
        assert "crowdfunding_providers" in legal_content.entities_affected
        assert legal_content.compliance_level == "mandatory"
        
        # Test ExtractedMetadata schema
        extracted_metadata = ExtractedMetadata(
            regulation_info=regulation_info,
            legal_content=legal_content,
            confidence_score=0.9
        )
        
        assert extracted_metadata.confidence_score == 0.9
        assert extracted_metadata.regulation_info.regulation_number == "EU 2020/1503"
        assert extracted_metadata.legal_content.provision_type == "obligation"
        
        print("    ✓ All Pydantic schemas validated successfully")
        return True
    
    def test_extractor_initialization(self) -> bool:
        """Test metadata extractor initialization and configuration."""
        print("  🔧 Testing extractor initialization...")
        
        # Test default configuration
        extractor = LegalMetadataExtractor()
        assert extractor.config.model_name == "gpt-4o-mini"
        assert extractor.config.temperature == 0.1
        assert extractor.config.retry_attempts == 3
        
        # Test custom configuration
        custom_config = ExtractionConfig(
            model_name="gpt-4",
            temperature=0.2,
            retry_attempts=5,
            batch_size=100
        )
        
        extractor_custom = LegalMetadataExtractor(custom_config)
        assert extractor_custom.config.model_name == "gpt-4"
        assert extractor_custom.config.temperature == 0.2
        assert extractor_custom.config.retry_attempts == 5
        assert extractor_custom.config.batch_size == 100
        
        # Test that LLM and prompt are properly initialized
        assert hasattr(extractor, 'llm')
        assert hasattr(extractor, 'structured_llm')
        assert hasattr(extractor, 'extraction_prompt')
        assert hasattr(extractor, 'metadata_manager')
        
        print("    ✓ Extractor initialization successful")
        return True
    
    def test_basic_extraction(self) -> bool:
        """Test basic metadata extraction functionality."""
        print("  🔍 Testing basic metadata extraction...")
        
        extractor = LegalMetadataExtractor()
        
        # Test crowdfunding regulation extraction
        result = extractor.extract_metadata(
            chunk_content=self.sample_texts["crowdfunding_regulation"],
            document_title="EU Crowdfunding Regulation",
            domain="eu_crowdfunding"
        )
        
        # Validate result structure
        assert isinstance(result, dict)
        required_fields = [
            "regulation_number", "article_number", "section_level",
            "provision_type", "entities_affected", "compliance_level",
            "legal_concepts", "confidence_score"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
        
        # Validate specific extractions
        assert result["regulation_number"] is not None
        assert "2020/1503" in result["regulation_number"] or "EU 2020/1503" in str(result["regulation_number"])
        assert result["article_number"] is not None
        assert "23" in str(result["article_number"])
        
        # Validate provision type classification
        assert result["provision_type"] in ["obligation", "prohibition", "exemption", "definition", "other"]
        
        # Validate compliance level
        assert result["compliance_level"] in ["mandatory", "optional", "conditional", "unknown"]
        
        # Validate confidence score
        assert isinstance(result["confidence_score"], (int, float))
        assert 0.0 <= result["confidence_score"] <= 1.0
        
        print(f"    ✓ Basic extraction successful - Regulation: {result['regulation_number']}, Article: {result['article_number']}")
        return True
    
    def test_provision_type_classification(self) -> bool:
        """Test classification of different provision types."""
        print("  📊 Testing provision type classification...")
        
        extractor = LegalMetadataExtractor()
        
        # Test obligation (crowdfunding regulation)
        obligation_result = extractor.extract_metadata(
            chunk_content=self.sample_texts["crowdfunding_regulation"],
            document_title="EU Crowdfunding Regulation",
            domain="eu_crowdfunding"
        )
        
        # Should classify as obligation due to "shall be authorized"
        print(f"    Obligation test - Type: {obligation_result['provision_type']}, Compliance: {obligation_result['compliance_level']}")
        
        # Test definition
        definition_result = extractor.extract_metadata(
            chunk_content=self.sample_texts["definition_text"],
            document_title="EU Crowdfunding Regulation",
            domain="eu_crowdfunding"
        )
        
        print(f"    Definition test - Type: {definition_result['provision_type']}")
        
        # Test prohibition
        prohibition_result = extractor.extract_metadata(
            chunk_content=self.sample_texts["prohibition_text"],
            document_title="EU Crowdfunding Regulation",
            domain="eu_crowdfunding"
        )
        
        print(f"    Prohibition test - Type: {prohibition_result['provision_type']}")
        
        # Validate that different types are properly classified
        assert obligation_result["provision_type"] in ["obligation", "other"]
        assert definition_result["provision_type"] in ["definition", "other"]
        assert prohibition_result["provision_type"] in ["prohibition", "other"]
        
        print("    ✓ Provision type classification working")
        return True
    
    def test_fallback_functionality(self) -> bool:
        """Test fallback metadata creation when LLM extraction fails."""
        print("  🛡️ Testing fallback functionality...")
        
        extractor = LegalMetadataExtractor()
        
        # Test with text containing regulation number for regex fallback
        fallback_result = extractor._create_fallback_metadata(
            self.sample_texts["crowdfunding_regulation"]
        )
        
        # Validate fallback structure
        assert isinstance(fallback_result, dict)
        assert fallback_result["confidence_score"] == 0.1  # Low confidence for fallback
        assert fallback_result["provision_type"] == "other" or fallback_result["provision_type"] == "obligation"
        
        # Check if regex extraction worked
        if fallback_result["regulation_number"]:
            assert "2020/1503" in fallback_result["regulation_number"]
        
        if fallback_result["article_number"]:
            assert "23" in fallback_result["article_number"]
        
        print(f"    ✓ Fallback functionality working - Regulation: {fallback_result['regulation_number']}")
        return True
    
    def test_validation_logic(self) -> bool:
        """Test metadata validation and normalization."""
        print("  ✅ Testing validation logic...")
        
        extractor = LegalMetadataExtractor()
        
        # Test with invalid data that should be normalized
        invalid_data = {
            "regulation_number": "Invalid Format",
            "article_number": "Not an article",
            "provision_type": "invalid_type",
            "compliance_level": "invalid_level",
            "entities_affected": "not_a_list",
            "legal_concepts": "also_not_a_list",
            "confidence_score": 1.5  # Out of range
        }
        
        validated_data = extractor._validate_extraction(
            invalid_data, 
            self.sample_texts["crowdfunding_regulation"]
        )
        
        # Check normalization
        assert validated_data["provision_type"] in ["obligation", "prohibition", "exemption", "definition", "other"]
        assert validated_data["compliance_level"] in ["mandatory", "optional", "conditional", "unknown"]
        assert isinstance(validated_data["entities_affected"], list)
        assert isinstance(validated_data["legal_concepts"], list)
        assert 0.0 <= validated_data["confidence_score"] <= 1.0
        
        print("    ✓ Validation logic working correctly")
        return True
    
    def test_batch_processing(self) -> bool:
        """Test batch metadata extraction."""
        print("  📦 Testing batch processing...")
        
        extractor = LegalMetadataExtractor()
        
        # Prepare batch data
        batch_data = [
            (self.sample_texts["crowdfunding_regulation"], "EU Crowdfunding Regulation", "eu_crowdfunding"),
            (self.sample_texts["gdpr_article"], "GDPR", "data_protection"),
            (self.sample_texts["definition_text"], "EU Crowdfunding Regulation", "eu_crowdfunding")
        ]
        
        # Process batch
        batch_results = extractor.extract_batch(batch_data)
        
        # Validate batch results
        assert len(batch_results) == 3
        
        for i, result in enumerate(batch_results):
            assert isinstance(result, dict)
            assert "confidence_score" in result
            assert "regulation_number" in result
            assert "provision_type" in result
            
            print(f"    Batch item {i+1}: Regulation: {result['regulation_number']}, Type: {result['provision_type']}")
        
        print("    ✓ Batch processing successful")
        return True
    
    def test_integration_with_metadata_system(self) -> bool:
        """Test integration with hierarchical metadata system."""
        print("  🔗 Testing integration with metadata system...")
        
        extractor = LegalMetadataExtractor()
        metadata_manager = MetadataManager()
        
        # Create base hierarchical metadata
        base_metadata = metadata_manager.create_hierarchical_metadata(
            source="test_regulation.pdf",
            chunk_id="chunk_001",
            domain="eu_crowdfunding",
            topic="authorization",
            doc_type="regulation",
            char_count=len(self.sample_texts["crowdfunding_regulation"])
        )
        
        # Enhance with LLM-extracted metadata
        enhanced_metadata = extractor.enhance_existing_metadata(
            base_metadata=base_metadata,
            chunk_content=self.sample_texts["crowdfunding_regulation"],
            document_title="EU Crowdfunding Regulation",
            domain="eu_crowdfunding"
        )
        
        # Validate integration
        assert "document" in enhanced_metadata
        assert "structure" in enhanced_metadata
        assert "content" in enhanced_metadata
        assert "processing" in enhanced_metadata
        
        # Check that legal metadata was added
        assert "legal_metadata" in enhanced_metadata
        legal_meta = enhanced_metadata["legal_metadata"]
        assert "regulation_number" in legal_meta
        assert "provision_type" in legal_meta
        
        print(f"    ✓ Integration successful - Enhanced metadata contains {len(enhanced_metadata)} top-level keys")
        return True
    
    def test_convenience_functions(self) -> bool:
        """Test convenience functions for easy integration."""
        print("  🎯 Testing convenience functions...")
        
        # Test single extraction convenience function
        single_result = extract_legal_metadata(
            chunk_content=self.sample_texts["gdpr_article"],
            document_title="GDPR",
            domain="data_protection"
        )
        
        assert isinstance(single_result, dict)
        assert "regulation_number" in single_result
        assert "2016/679" in str(single_result["regulation_number"]) or single_result["regulation_number"] is None
        
        # Test batch extraction convenience function
        batch_data = [
            (self.sample_texts["crowdfunding_regulation"], "EU Crowdfunding Regulation", "eu_crowdfunding"),
            (self.sample_texts["definition_text"], "EU Crowdfunding Regulation", "eu_crowdfunding")
        ]
        
        batch_results = extract_batch_metadata(batch_data)
        
        assert len(batch_results) == 2
        assert all(isinstance(result, dict) for result in batch_results)
        
        print("    ✓ Convenience functions working correctly")
        return True
    
    def test_extraction_stats(self) -> bool:
        """Test extraction statistics and configuration reporting."""
        print("  📊 Testing extraction statistics...")
        
        extractor = LegalMetadataExtractor()
        stats = extractor.get_extraction_stats()
        
        # Validate stats structure
        assert "extractor_config" in stats
        assert "supported_extractions" in stats
        
        config_stats = stats["extractor_config"]
        assert "model_name" in config_stats
        assert "temperature" in config_stats
        assert "retry_attempts" in config_stats
        
        supported_stats = stats["supported_extractions"]
        assert "regulation_numbers" in supported_stats
        assert "provision_types" in supported_stats
        assert "compliance_levels" in supported_stats
        
        print(f"    ✓ Stats generated - Model: {config_stats['model_name']}, Supported types: {len(supported_stats['provision_types'])}")
        return True
    
    def run_all_tests(self):
        """Run all tests and generate comprehensive report."""
        print("🚀 Starting Step 2: LLM-Assisted Metadata Extractor Test Suite")
        print("=" * 80)
        
        start_time = time.time()
        
        # Define all tests
        tests = [
            ("Pydantic Schemas", self.test_pydantic_schemas),
            ("Extractor Initialization", self.test_extractor_initialization),
            ("Basic Extraction", self.test_basic_extraction),
            ("Provision Type Classification", self.test_provision_type_classification),
            ("Fallback Functionality", self.test_fallback_functionality),
            ("Validation Logic", self.test_validation_logic),
            ("Batch Processing", self.test_batch_processing),
            ("Integration with Metadata System", self.test_integration_with_metadata_system),
            ("Convenience Functions", self.test_convenience_functions),
            ("Extraction Statistics", self.test_extraction_stats)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate final report
        total_time = time.time() - start_time
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST REPORT - Step 2: LLM-Assisted Metadata Extractor")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.passed_tests}/{self.total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! Step 2 implementation is ready for production.")
            print("\n✅ Step 2: LLM-Assisted Metadata Extractor - COMPLETE")
            print("🔄 Ready to proceed to Step 3: Multi-Level Filtering Architecture")
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} tests failed. Please review and fix issues.")
            
            # Show failed tests
            failed_tests = [result for result in self.test_results if result["status"] != "PASSED"]
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['status']}")
                    if "error" in test:
                        print(f"    Error: {test['error']}")
        
        return self.passed_tests == self.total_tests


def main():
    """Main test execution function."""
    print("Step 2: LLM-Assisted Metadata Extractor - Comprehensive Test Suite")
    print("Testing legal metadata extraction with structured output using Context7 best practices")
    print()
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Some tests may fail without proper API access")
        print()
    
    # Run tests
    test_suite = TestMetadataExtractor()
    success = test_suite.run_all_tests()
    
    # Export results
    results_file = "step_2_test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "test_results": test_suite.test_results,
            "summary": {
                "total_tests": test_suite.total_tests,
                "passed_tests": test_suite.passed_tests,
                "success_rate": (test_suite.passed_tests / test_suite.total_tests) * 100 if test_suite.total_tests > 0 else 0,
                "all_passed": success
            }
        }, f, indent=2)
    
    print(f"\n📄 Detailed results exported to: {results_file}")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 