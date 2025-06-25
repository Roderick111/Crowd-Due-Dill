# Tests Directory

This directory contains all tests for the Crowd Due Dill project, organized by category.

## Test Structure

```
tests/
├── run_tests.py              # Test runner script
├── auth/                     # Authentication tests
├── integration/              # Integration tests (full system)
│   ├── test_article22.py     # Article 22 hybrid retrieval test
│   ├── test_full_access.py   # Full system access test
│   ├── test_metadata_integration.py  # Metadata system integration
│   └── test_stripe_*.py      # Stripe payment integration tests
├── unit/                     # Unit tests (individual components)
│   ├── test_contextual_rag_refactored.py  # RAG system tests
│   ├── test_metadata_extractor.py         # Metadata extraction tests
│   ├── test_web_crawler.py               # Web crawler tests
│   └── ...                               # Other component tests
├── performance/              # Performance and load tests
├── interactive_test.py       # Interactive testing script
└── quick_test.py            # Quick smoke tests
```

## Running Tests

### Using the Test Runner (Recommended)

```bash
# Run all tests
python3 tests/run_tests.py all

# Run only unit tests
python3 tests/run_tests.py unit

# Run only integration tests  
python3 tests/run_tests.py integration

# Run specific Article 22 test
python3 tests/run_tests.py article22
```

### Running Individual Tests

```bash
# From project root directory
python3 tests/integration/test_article22.py
python3 tests/unit/test_contextual_rag_refactored.py
```

## Test Categories

### Unit Tests (`unit/`)
- Test individual components in isolation
- Fast execution
- No external dependencies
- Mock external services

### Integration Tests (`integration/`)
- Test full system workflows
- May require running services
- Test component interactions
- Include end-to-end scenarios

### Performance Tests (`performance/`)
- Load testing
- Response time testing
- Memory usage testing
- Scalability testing

## Key Tests

### Article 22 Test (`integration/test_article22.py`)
- Tests the hybrid retrieval system
- Validates precision vs semantic search
- Critical for legal document accuracy
- **Always run before deployment**

### Metadata Integration (`integration/test_metadata_integration.py`)
- Tests metadata extraction and enhancement
- Validates hierarchical metadata schema
- Tests ChromaDB query helpers

### RAG System Tests (`unit/test_contextual_rag_refactored.py`)
- Tests core RAG functionality
- Validates query processing
- Tests vector search and reranking

## Test Requirements

Most tests require:
- Python 3.8+
- All project dependencies installed
- Environment variables configured (see `.env.example`)
- Some integration tests may require running services

## Adding New Tests

1. **Unit tests**: Add to `unit/` directory
2. **Integration tests**: Add to `integration/` directory  
3. **Follow naming convention**: `test_*.py`
4. **Include docstrings** explaining what the test does
5. **Update this README** if adding new test categories

## Notes

- Tests moved from root directory for better organization
- Import paths updated to work from subdirectories
- Test runner handles path resolution automatically
- Some legacy tests may need dependency updates 