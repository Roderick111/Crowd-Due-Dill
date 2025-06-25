#!/usr/bin/env python3
"""
Web Crawler Usage Examples for Crowd Due Dill

This script demonstrates various ways to use the web crawler
to extract and store content in LLM-readable markdown format.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.web_crawler import WebCrawler


async def example_single_page():
    """Example: Crawl a single web page."""
    print("📄 Example 1: Single Page Crawling")
    print("=" * 50)
    
    crawler = WebCrawler(verbose=True)
    
    # Crawl a single page with content filtering
    result = await crawler.crawl_single_page(
        "https://en.wikipedia.org/wiki/European_Union",
        use_content_filter=True
    )
    
    if result['success']:
        print(f"✅ Title: {result['title']}")
        print(f"📊 Word count: {result['word_count']}")
        print(f"📄 Content preview:\n{result['markdown'][:300]}...")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n")


async def example_batch_crawling():
    """Example: Crawl multiple URLs in parallel."""
    print("📚 Example 2: Batch Crawling")
    print("=" * 50)
    
    crawler = WebCrawler(verbose=True)
    
    urls = [
        "https://en.wikipedia.org/wiki/GDPR",
        "https://en.wikipedia.org/wiki/Digital_Services_Act",
        "https://en.wikipedia.org/wiki/European_Union_law"
    ]
    
    results = await crawler.crawl_urls_batch(
        urls, 
        max_concurrent=3,
        use_content_filter=True
    )
    
    successful = [r for r in results if r.get('success', False)]
    print(f"✅ Successfully crawled {len(successful)}/{len(urls)} pages")
    
    for result in successful:
        print(f"  📄 {result['title']} ({result['word_count']} words)")
    
    print("\n")


async def example_query_focused():
    """Example: Crawl with focus on specific topic."""
    print("🎯 Example 3: Query-Focused Crawling")
    print("=" * 50)
    
    crawler = WebCrawler(verbose=True)
    
    # Focus on GDPR-related content
    result = await crawler.crawl_with_query_focus(
        "https://en.wikipedia.org/wiki/European_Union_law",
        query="GDPR data protection privacy rights",
        threshold=1.0  # Lower threshold = more content included
    )
    
    if result['success']:
        print(f"✅ Query: {result['query']}")
        print(f"📄 Title: {result['title']}")
        print(f"📊 Focused content ({result['word_count']} words)")
        print(f"📄 Content preview:\n{result['markdown'][:400]}...")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n")


async def example_save_and_add_to_db():
    """Example: Save results to files and add to database."""
    print("💾 Example 4: Save Results and Add to Database")
    print("=" * 50)
    
    crawler = WebCrawler(verbose=True)
    
    # Crawl a few pages
    urls = [
        "https://en.wikipedia.org/wiki/Crowdfunding",
        "https://en.wikipedia.org/wiki/Financial_regulation"
    ]
    
    results = await crawler.crawl_urls_batch(urls, max_concurrent=2)
    successful = [r for r in results if r.get('success', False)]
    
    if successful:
        # Save to files
        print("💾 Saving to files...")
        crawler.save_results_to_files(successful, "examples/crawled_output")
        
        # Add to database (commented out to avoid modifying production DB)
        print("📊 Adding to database...")
        # added_count = await crawler.add_to_database(successful, "example_crawled")
        # print(f"✅ Added {added_count} documents to database")
        print("⚠️ Database addition skipped in example (uncomment to use)")
    
    print("\n")


async def example_sitemap_crawling():
    """Example: Crawl from a sitemap (commented out - requires real sitemap)."""
    print("🗺️ Example 5: Sitemap Crawling (Example)")
    print("=" * 50)
    
    print("This example shows how to crawl from a sitemap:")
    print("""
    crawler = WebCrawler(verbose=True)
    
    # Crawl from sitemap (limit to 5 pages)
    results = await crawler.crawl_from_sitemap(
        "https://example.com/sitemap.xml",
        max_concurrent=3,
        max_pages=5
    )
    
    # Save results
    successful = [r for r in results if r.get('success', False)]
    crawler.save_results_to_files(successful, "sitemap_content")
    """)
    
    print("⚠️ Sitemap crawling requires a valid sitemap.xml URL")
    print("\n")


def print_usage_info():
    """Print information about using the web crawler."""
    print("🔧 Web Crawler Usage Information")
    print("=" * 50)
    print("""
Command Line Usage:
    # Single page
    python tools/web_crawler.py https://example.com
    
    # Multiple pages
    python tools/web_crawler.py --batch https://example1.com https://example2.com
    
    # Query-focused crawling
    python tools/web_crawler.py https://example.com --query "machine learning AI"
    
    # Sitemap crawling
    python tools/web_crawler.py https://example.com/sitemap.xml --sitemap --max-pages 10
    
    # Add to database
    python tools/web_crawler.py https://example.com --add-to-db --domain "my_domain"
    
    # Save to custom directory
    python tools/web_crawler.py https://example.com --output-dir "my_content"

Python Usage:
    from tools.web_crawler import WebCrawler
    
    crawler = WebCrawler(verbose=True)
    result = await crawler.crawl_single_page("https://example.com")
    
Installation:
    pip install -r config/requirements_crawler.txt
    playwright install
    """)


async def main():
    """Run all examples."""
    print("🕷️ Web Crawler Examples for Crowd Due Dill")
    print("=" * 60)
    print()
    
    # Print usage information first
    print_usage_info()
    print("\n" + "=" * 60)
    print("Running Examples...")
    print("=" * 60)
    print()
    
    try:
        # Run examples
        await example_single_page()
        await example_batch_crawling()
        await example_query_focused()
        await example_save_and_add_to_db()
        example_sitemap_crawling()  # This one doesn't actually crawl
        
        print("✅ All examples completed successfully!")
        print()
        print("📁 Check the 'examples/crawled_output/' directory for saved files")
        print("🔧 Try the command-line interface: python tools/web_crawler.py --help")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install -r config/requirements_crawler.txt && playwright install")
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("💡 Make sure you have an internet connection and the dependencies installed")


if __name__ == "__main__":
    asyncio.run(main()) 