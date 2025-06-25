# Web Crawler for Crowd Due Dill

> **Note**: This is an optional component that requires additional dependencies. The main Crowd Due Dill application will work without installing the crawler dependencies.

A simple yet powerful web crawler that extracts content from websites and converts it to LLM-readable Markdown format. Built with [crawl4ai](https://github.com/unclecode/crawl4ai) for intelligent content extraction and filtering.

## Features

### 🔍 **Intelligent Content Extraction**
- **Smart Markdown Conversion**: Converts HTML to clean, structured markdown
- **Content Filtering**: Uses PruningContentFilter to remove low-value content (navigation, ads, footers)
- **Query-Focused Crawling**: BM25 filtering to extract content relevant to specific topics
- **Title Extraction**: Automatically identifies page titles from content

### 🚀 **Multiple Crawling Strategies**
- **Single Page**: Crawl individual web pages
- **Batch Crawling**: Process multiple URLs in parallel
- **Sitemap Support**: Extract and crawl all URLs from sitemap.xml files
- **Query-Focused**: Extract content relevant to specific search terms

### 💾 **Flexible Output Options**
- **File Export**: Save crawled content as markdown files
- **Database Integration**: Add content directly to the Crowd Due Dill document database
- **Structured Results**: JSON-formatted results with metadata

### ⚡ **Performance & Reliability**
- **Concurrent Processing**: Configurable parallel crawling
- **Memory Management**: Efficient resource usage
- **Error Handling**: Graceful handling of failed requests
- **Progress Tracking**: Verbose logging and status updates

## Installation

### 1. Install Dependencies
```bash
# Install crawler dependencies
pip install -r config/requirements_crawler.txt

# Install Playwright browser engine
playwright install
```

### 2. Verify Installation
```bash
# Test basic functionality
python examples/crawl_example.py
```

## Usage

### Command Line Interface

#### Basic Single Page Crawling
```bash
# Crawl a single page
python tools/web_crawler.py https://en.wikipedia.org/wiki/GDPR

# Save to custom directory
python tools/web_crawler.py https://example.com --output-dir "my_content"

# Disable content filtering for raw content
python tools/web_crawler.py https://example.com --no-filter
```

#### Batch Crawling
```bash
# Crawl multiple URLs
python tools/web_crawler.py --batch \
    https://example.com/page1 \
    https://example.com/page2 \
    https://example.com/page3

# Limit concurrent crawls
python tools/web_crawler.py --batch url1 url2 url3 --max-concurrent 2
```

#### Query-Focused Crawling
```bash
# Extract content relevant to specific topics
python tools/web_crawler.py https://en.wikipedia.org/wiki/European_Union_law \
    --query "GDPR data protection privacy rights"

# Adjust relevance threshold (lower = more content)
python tools/web_crawler.py https://example.com \
    --query "machine learning" \
    --threshold 0.8
```

#### Sitemap Crawling
```bash
# Crawl all URLs from a sitemap
python tools/web_crawler.py https://example.com/sitemap.xml --sitemap

# Limit number of pages
python tools/web_crawler.py https://example.com/sitemap.xml --sitemap --max-pages 10

# Control concurrency
python tools/web_crawler.py https://example.com/sitemap.xml --sitemap \
    --max-concurrent 3 --max-pages 20
```

#### Database Integration
```bash
# Add crawled content to document database
python tools/web_crawler.py https://example.com --add-to-db

# Specify domain for categorization
python tools/web_crawler.py https://example.com --add-to-db --domain "regulatory_docs"

# Batch crawl and add to database
python tools/web_crawler.py --batch url1 url2 url3 --add-to-db --domain "legal_texts"
```

#### Advanced Options
```bash
# Enable verbose logging
python tools/web_crawler.py https://example.com --verbose

# Get help and see all options
python tools/web_crawler.py --help
```

### Python API

#### Basic Usage
```python
import asyncio
from tools.web_crawler import WebCrawler

async def main():
    crawler = WebCrawler(verbose=True)
    
    # Single page crawling
    result = await crawler.crawl_single_page(
        "https://en.wikipedia.org/wiki/GDPR",
        use_content_filter=True
    )
    
    if result['success']:
        print(f"Title: {result['title']}")
        print(f"Word count: {result['word_count']}")
        print(f"Content: {result['markdown'][:500]}...")

asyncio.run(main())
```

#### Batch Crawling
```python
async def batch_example():
    crawler = WebCrawler()
    
    urls = [
        "https://en.wikipedia.org/wiki/GDPR",
        "https://en.wikipedia.org/wiki/Digital_Services_Act",
        "https://en.wikipedia.org/wiki/DORA"
    ]
    
    results = await crawler.crawl_urls_batch(
        urls, 
        max_concurrent=3,
        use_content_filter=True
    )
    
    # Save results to files
    successful = [r for r in results if r.get('success', False)]
    crawler.save_results_to_files(successful, "regulatory_docs")
    
    # Add to database
    added_count = await crawler.add_to_database(successful, "eu_regulations")
    print(f"Added {added_count} documents to database")
```

#### Query-Focused Crawling
```python
async def query_focused_example():
    crawler = WebCrawler()
    
    result = await crawler.crawl_with_query_focus(
        "https://en.wikipedia.org/wiki/European_Union_law",
        query="GDPR data protection privacy rights",
        threshold=1.0  # Lower = more content included
    )
    
    if result['success']:
        print(f"Query: {result['query']}")
        print(f"Relevant content: {result['markdown']}")
```

#### Sitemap Crawling
```python
async def sitemap_example():
    crawler = WebCrawler()
    
    # Crawl from sitemap
    results = await crawler.crawl_from_sitemap(
        "https://example.com/sitemap.xml",
        max_concurrent=3,
        max_pages=10
    )
    
    # Process results
    successful = [r for r in results if r.get('success', False)]
    print(f"Crawled {len(successful)} pages from sitemap")
```

## Configuration Options

### Content Filtering

#### PruningContentFilter (Default)
- **Purpose**: Removes low-value content (navigation, ads, footers)
- **threshold**: 0.0-1.0 (higher = more aggressive filtering)
- **threshold_type**: "dynamic" or "fixed"
- **min_word_threshold**: Minimum words per content block

#### BM25ContentFilter (Query-Focused)
- **Purpose**: Extracts content relevant to specific queries
- **user_query**: Search terms to focus on
- **bm25_threshold**: Relevance threshold (higher = more selective)
- **use_stemming**: Match word variations (learn/learning/learnt)

### Performance Tuning

#### Concurrency Settings
```python
# Conservative (lower resource usage)
max_concurrent = 2

# Balanced (default)
max_concurrent = 5

# Aggressive (faster but more resources)
max_concurrent = 10
```

#### Content Filter Settings
```python
# Light filtering (keep more content)
threshold = 0.3

# Moderate filtering (balanced)
threshold = 0.5

# Heavy filtering (only high-value content)
threshold = 0.7
```

## Output Formats

### File Output
Crawled pages are saved as markdown files with metadata headers:

```markdown
# Page Title

**Source URL:** https://example.com  
**Crawled:** 200  
**Word Count:** 1234  

---

[Extracted markdown content...]
```

### Database Integration
Content is automatically chunked and vectorized when added to the database:
- **Domain**: Categorizes content (e.g., "regulatory_docs", "web_crawled")
- **Chunks**: Content split into searchable segments
- **Metadata**: URL, title, and extraction details preserved

### JSON Results
Each crawl operation returns structured data:

```python
{
    'url': 'https://example.com',
    'success': True,
    'title': 'Page Title',
    'markdown': 'Extracted content...',
    'word_count': 1234,
    'status_code': 200
}
```

## Examples

See `examples/crawl_example.py` for comprehensive usage examples:

```bash
# Run all examples
python examples/crawl_example.py

# View example code
cat examples/crawl_example.py
```

## Integration with Crowd Due Dill

### Adding Regulatory Documents
```bash
# Crawl EU regulatory websites and add to database
python tools/web_crawler.py https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32020R1503 \
    --add-to-db --domain "eu_crowdfunding" --verbose

# Batch crawl multiple regulations
python tools/web_crawler.py --batch \
    https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32020R1503 \
    https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554 \
    --add-to-db --domain "eu_regulations"
```

### Query-Focused Legal Research
```bash
# Extract GDPR-specific content from legal databases
python tools/web_crawler.py https://example-legal-site.com \
    --query "GDPR Article 6 lawful processing personal data" \
    --add-to-db --domain "gdpr_analysis"
```

## Best Practices

### 1. **Respectful Crawling**
- Use reasonable concurrency limits (max 5-10 concurrent requests)
- Add delays between requests if crawling many pages from same domain
- Respect robots.txt and website terms of service

### 2. **Content Quality**
- Use content filtering for cleaner, more focused results
- Test query-focused crawling for specific topics
- Review extracted content before adding to database

### 3. **Performance Optimization**
- Start with small batches to test performance
- Monitor system resources during large crawls
- Use appropriate filtering thresholds for your use case

### 4. **Error Handling**
- Check crawl results before processing
- Log failed URLs for retry attempts
- Handle network timeouts gracefully

## Troubleshooting

### Common Issues

#### ImportError: crawl4ai not found
```bash
# Install dependencies
pip install -r config/requirements_crawler.txt
playwright install
```

#### Playwright browser not found
```bash
# Reinstall Playwright browsers
playwright install
```

#### Memory issues during large crawls
```python
# Reduce concurrency
crawler = WebCrawler()
results = await crawler.crawl_urls_batch(urls, max_concurrent=2)
```

#### Empty or poor quality content
```python
# Adjust content filtering
result = await crawler.crawl_single_page(url, use_content_filter=False)
# or
result = await crawler.crawl_with_query_focus(url, "specific topic", threshold=0.5)
```

### Debug Mode
```bash
# Enable verbose logging for debugging
python tools/web_crawler.py https://example.com --verbose
```

## Dependencies

- **crawl4ai**: Core crawling and content extraction
- **playwright**: Browser automation engine
- **requests**: HTTP requests for sitemap parsing
- **asyncio**: Asynchronous operation support

See `config/requirements_crawler.txt` for complete dependency list.

## Contributing

The web crawler is designed to be easily extensible. Key areas for enhancement:

1. **Additional Content Filters**: Custom filtering strategies
2. **Output Formats**: Support for different export formats
3. **Source Integrations**: Specialized crawlers for specific sites
4. **Performance Optimizations**: Enhanced memory and speed optimizations

## Cross-Encoder Reranking (NEW!)

The document manager now supports advanced Cross-Encoder reranking for improved search relevance. This two-stage search pipeline first retrieves documents using fast vector similarity, then reranks them using a Cross-Encoder model for better semantic understanding.

### Installation

```bash
pip install sentence-transformers
```

### Basic Usage

#### Enable Reranking for Queries
```bash
# Query with reranking enabled
python tools/document_manager.py query \
    --query "What are the crowdfunding requirements in the EU?" \
    --enable-reranking \
    --results 5

# Test reranking comparison
python tools/document_manager.py test-rerank \
    --query "crowdfunding platform obligations" \
    --enable-reranking
```

#### Configuration Options
```bash
# Custom reranking model
python tools/document_manager.py query \
    --query "your search query" \
    --enable-reranking \
    --rerank-model "cross-encoder/ms-marco-MiniLM-L-12-v2" \
    --rerank-top-k 30 \
    --rerank-final-k 10
```

### How It Works

1. **Stage 1**: Fast vector similarity search retrieves top N documents (default: 20)
2. **Stage 2**: Cross-Encoder reranks these documents using deep semantic understanding
3. **Result**: Returns top K most relevant documents (default: 5)

### Performance Impact

- **Better Relevance**: Cross-Encoder provides superior semantic matching
- **Moderate Latency**: Adds ~1-3 seconds for reranking 20 documents
- **Memory Usage**: ~100-200MB additional for the Cross-Encoder model
- **GPU Support**: Automatically uses Apple Silicon (MPS) or CUDA when available

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--enable-reranking` | False | Enable Cross-Encoder reranking |
| `--rerank-model` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | HuggingFace Cross-Encoder model |
| `--rerank-top-k` | 20 | Initial documents to retrieve for reranking |
| `--rerank-final-k` | 5 | Final number of results after reranking |

### Model Options

- **Fast**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (default, ~50MB)
- **Better**: `cross-encoder/ms-marco-MiniLM-L-12-v2` (~130MB)
- **Legal**: `cross-encoder/ms-marco-electra-base` (specialized for legal documents)

### Example Results

**Without Reranking:**
```
1. docs/content/dsa.md (similarity: 0.2039)
2. docs/content/dsa.md (similarity: 0.2067) 
3. docs/content/dsa.md (similarity: 0.2144)
```

**With Reranking:**
```
1. docs/content/main_eu_regulation.md (similarity: 0.2368, rerank: 8.91)
2. docs/content/dsa.md (similarity: 0.2412, rerank: 8.71)
3. docs/content/dsa.md (similarity: 0.2067, rerank: 8.11)
```

Notice how reranking promoted `main_eu_regulation.md` to the top despite lower similarity score, because the Cross-Encoder determined it was more semantically relevant to the query.

### Integration with Existing Workflows

Reranking can be enabled for any document manager operation:

```python
from tools.document_manager import SimpleDocumentManager, ProcessingConfig

# Enable reranking in configuration
config = ProcessingConfig(enable_reranking=True)
manager = SimpleDocumentManager(config=config)

# Query with reranking
results = manager.query_documents(
    "crowdfunding platform requirements", 
    k=5, 
    use_reranking=True
)
```

This enhancement significantly improves search quality for legal documents while maintaining the existing document management capabilities.

---

For questions or issues, check the main project documentation or create an issue in the repository. 