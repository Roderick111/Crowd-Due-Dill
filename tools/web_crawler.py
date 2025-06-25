#!/usr/bin/env python3
"""
Web Crawler for Crowd Due Dill

Simple crawling functionality to parse and store documents in LLM-readable Markdown format.
Supports single page crawling, batch crawling of URLs, and recursive link following.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin, urldefrag
import requests
import xml.etree.ElementTree as ElementTree

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
except ImportError:
    print("❌ crawl4ai not installed. Install with: pip install crawl4ai && playwright install")
    sys.exit(1)

try:
    from tools.document_manager import SimpleDocumentManager
except ImportError:
    print("❌ Could not import document manager. Make sure you're running from the project root directory.")
    sys.exit(1)


class WebCrawler:
    """
    Simple web crawler that converts web content to LLM-readable markdown.
    """
    
    def __init__(self, headless: bool = True, verbose: bool = False):
        """
        Initialize the web crawler.
        
        Args:
            headless: Run browser in headless mode (default: True)
            verbose: Enable verbose logging (default: False)
        """
        self.headless = headless
        self.verbose = verbose
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("WebCrawler")
        logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def crawl_single_page(self, url: str, use_content_filter: bool = True) -> Dict[str, Any]:
        """
        Crawl a single web page and convert to markdown.
        
        Args:
            url: URL to crawl
            use_content_filter: Apply content filtering for cleaner output
            
        Returns:
            Dictionary with crawl results including markdown content
        """
        self.logger.info(f"🔍 Crawling single page: {url}")
        
        browser_config = BrowserConfig(
            headless=self.headless,
            verbose=self.verbose
        )
        
        # Configure markdown generator with optional content filtering
        if use_content_filter:
            # Use lighter pruning filter to preserve structure
            pruning_filter = PruningContentFilter(
                threshold=0.3,  # Lighter filtering to preserve structure
                threshold_type="dynamic",
                min_word_threshold=5  # Lower threshold to keep short headings
            )
            md_generator = DefaultMarkdownGenerator(
                content_filter=pruning_filter,
                options={
                    "ignore_links": False, 
                    "body_width": 0,  # No line wrapping to preserve formatting
                    "strip": ["script", "style"],  # Only remove scripts and styles
                    "convert_toplist": True,  # Preserve list formatting
                    "mark_code": True,  # Preserve code formatting
                    "escape_html": False  # Don't escape HTML entities
                }
            )
        else:
            # No filtering - preserve all content and structure
            md_generator = DefaultMarkdownGenerator(
                options={
                    "ignore_links": False,
                    "body_width": 0,  # No line wrapping
                    "strip": ["script", "style"],  # Only remove scripts and styles
                    "convert_toplist": True,
                    "mark_code": True,
                    "escape_html": False
                }
            )
        
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Always fetch fresh content
            markdown_generator=md_generator
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success:
                self.logger.info(f"✅ Successfully crawled {url}")
                
                # Use fit_markdown if content filter was applied, otherwise raw_markdown
                markdown_content = (result.markdown.fit_markdown 
                                  if use_content_filter and result.markdown.fit_markdown 
                                  else result.markdown.raw_markdown)
                
                return {
                    'url': result.url,
                    'success': True,
                    'markdown': markdown_content,
                    'title': self._extract_title_from_markdown(markdown_content),
                    'word_count': len(markdown_content.split()),
                    'status_code': result.status_code
                }
            else:
                self.logger.error(f"❌ Failed to crawl {url}: {result.error_message}")
                return {
                    'url': url,
                    'success': False,
                    'error': result.error_message,
                    'status_code': result.status_code
                }
    
    async def crawl_urls_batch(self, urls: List[str], max_concurrent: int = 5, use_content_filter: bool = True) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs in parallel.
        
        Args:
            urls: List of URLs to crawl
            max_concurrent: Maximum number of concurrent crawl operations
            use_content_filter: Apply content filtering for cleaner output
            
        Returns:
            List of crawl results
        """
        self.logger.info(f"🔍 Crawling {len(urls)} URLs in batches of {max_concurrent}")
        
        # Process URLs in batches to avoid overwhelming the system
        results = []
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i:i + max_concurrent]
            self.logger.info(f"📦 Processing batch {i//max_concurrent + 1}: {len(batch)} URLs")
            
            # Create tasks for parallel execution
            tasks = [self.crawl_single_page(url, use_content_filter) for url in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions and add to results
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"❌ Exception during crawl: {str(result)}")
                    results.append({
                        'success': False,
                        'error': str(result)
                    })
                else:
                    results.append(result)
        
        successful_crawls = sum(1 for r in results if r.get('success', False))
        self.logger.info(f"✅ Completed batch crawling: {successful_crawls}/{len(urls)} successful")
        
        return results
    
    async def crawl_legal_document(self, url: str, preserve_structure: bool = True) -> Dict[str, Any]:
        """
        Crawl a legal document with optimized settings for preserving structure.
        
        Args:
            url: URL to crawl
            preserve_structure: Whether to preserve document structure (recommended for legal docs)
            
        Returns:
            Dictionary with crawl results optimized for legal documents
        """
        self.logger.info(f"⚖️ Crawling legal document: {url}")
        
        browser_config = BrowserConfig(
            headless=self.headless,
            verbose=self.verbose
        )
        
        # Configure for legal documents - no filtering, preserve all structure
        md_generator = DefaultMarkdownGenerator(
            options={
                "ignore_links": False,
                "body_width": 0,  # No line wrapping
                "strip": ["script", "style", "nav", "footer"],  # Remove navigation only
                "convert_toplist": True,  # Preserve list formatting
                "mark_code": True,  # Preserve code formatting
                "escape_html": False,  # Don't escape HTML entities
                "unicode_snob": True,  # Use unicode characters
                "wrap_links": False,  # Don't wrap links
                "wrap_list_items": False,  # Don't wrap list items
                "default_title": True,  # Generate default titles
                "use_automatic_links": False  # Don't convert plain URLs to links
            }
        )
        
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=md_generator,
            excluded_tags=["script", "style", "nav", "footer", "aside", "advertisement"],  # Remove non-content
            remove_overlay_elements=True,  # Remove popups and overlays
            word_count_threshold=0  # Don't filter by word count
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success:
                self.logger.info(f"✅ Successfully crawled legal document: {url}")
                
                # Use raw markdown to preserve all structure
                markdown_content = result.markdown.raw_markdown
                
                # Post-process to improve formatting
                markdown_content = self._enhance_legal_formatting(markdown_content)
                
                return {
                    'url': result.url,
                    'success': True,
                    'markdown': markdown_content,
                    'title': self._extract_title_from_markdown(markdown_content),
                    'word_count': len(markdown_content.split()),
                    'status_code': result.status_code,
                    'document_type': 'legal'
                }
            else:
                self.logger.error(f"❌ Failed to crawl legal document {url}: {result.error_message}")
                return {
                    'url': url,
                    'success': False,
                    'error': result.error_message,
                    'status_code': result.status_code,
                    'document_type': 'legal'
                }
    
    def _enhance_legal_formatting(self, markdown: str) -> str:
        """
        Enhance markdown formatting specifically for legal documents.
        
        Args:
            markdown: Raw markdown content
            
        Returns:
            Enhanced markdown with better legal document formatting
        """
        import re
        
        if not markdown:
            return markdown
        
        # Enhance legal document formatting
        enhanced = markdown
        
        # Fix chapter/article headings - look for patterns like "CHAPTER I", "Article 1", etc.
        enhanced = re.sub(r'^(CHAPTER\s+[IVXLCDM]+.*?)$', r'# \1', enhanced, flags=re.MULTILINE)
        enhanced = re.sub(r'^(Article\s+\d+.*?)$', r'## \1', enhanced, flags=re.MULTILINE)
        enhanced = re.sub(r'^(Section\s+\d+.*?)$', r'### \1', enhanced, flags=re.MULTILINE)
        
        # Fix numbered paragraphs - convert (1), (2), etc. to proper formatting
        enhanced = re.sub(r'^\s*\((\d+)\)\s*', r'\n(\1) ', enhanced, flags=re.MULTILINE)
        
        # Fix lettered subsections - (a), (b), etc.
        enhanced = re.sub(r'^\s*\(([a-z])\)\s*', r'\n   (\1) ', enhanced, flags=re.MULTILINE)
        
        # Clean up excessive whitespace but preserve intentional spacing
        enhanced = re.sub(r'\n{3,}', '\n\n', enhanced)
        enhanced = re.sub(r'[ \t]+$', '', enhanced, flags=re.MULTILINE)
        
        # Ensure proper spacing around headings
        enhanced = re.sub(r'\n(#{1,6}\s)', r'\n\n\1', enhanced)
        enhanced = re.sub(r'(#{1,6}.*?)\n([^\n#])', r'\1\n\n\2', enhanced)
        
        return enhanced.strip()

    async def crawl_with_query_focus(self, url: str, query: str, threshold: float = 1.2) -> Dict[str, Any]:
        """
        Crawl a page with focus on content relevant to a specific query using BM25 filtering.
        
        Args:
            url: URL to crawl
            query: Query to focus content on
            threshold: BM25 threshold for content filtering
            
        Returns:
            Dictionary with crawl results focused on the query
        """
        self.logger.info(f"🎯 Crawling {url} with focus on query: '{query}'")
        
        browser_config = BrowserConfig(
            headless=self.headless,
            verbose=self.verbose
        )
        
        # Configure BM25 content filter for query-focused extraction
        bm25_filter = BM25ContentFilter(
            user_query=query,
            bm25_threshold=threshold,
            use_stemming=True
        )
        
        md_generator = DefaultMarkdownGenerator(
            content_filter=bm25_filter,
            options={"ignore_links": False, "body_width": 120}
        )
        
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=md_generator
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success:
                self.logger.info(f"✅ Successfully crawled {url} with query focus")
                
                markdown_content = (result.markdown.fit_markdown 
                                  if result.markdown.fit_markdown 
                                  else result.markdown.raw_markdown)
                
                return {
                    'url': result.url,
                    'success': True,
                    'query': query,
                    'markdown': markdown_content,
                    'title': self._extract_title_from_markdown(markdown_content),
                    'word_count': len(markdown_content.split()),
                    'status_code': result.status_code
                }
            else:
                self.logger.error(f"❌ Failed to crawl {url}: {result.error_message}")
                return {
                    'url': url,
                    'success': False,
                    'query': query,
                    'error': result.error_message,
                    'status_code': result.status_code
                }
    
    def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Parse a sitemap.xml file to extract URLs.
        
        Args:
            sitemap_url: URL of the sitemap.xml file
            
        Returns:
            List of URLs found in the sitemap
        """
        self.logger.info(f"📄 Parsing sitemap: {sitemap_url}")
        
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            tree = ElementTree.fromstring(response.content)
            # Use namespace-agnostic approach to find all <loc> elements
            urls = [loc.text for loc in tree.findall('.//{*}loc') if loc.text]
            
            self.logger.info(f"✅ Found {len(urls)} URLs in sitemap")
            return urls
            
        except Exception as e:
            self.logger.error(f"❌ Failed to parse sitemap {sitemap_url}: {str(e)}")
            return []
    
    async def crawl_from_sitemap(self, sitemap_url: str, max_concurrent: int = 5, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Crawl all URLs from a sitemap.xml file.
        
        Args:
            sitemap_url: URL of the sitemap.xml file
            max_concurrent: Maximum number of concurrent crawl operations
            max_pages: Maximum number of pages to crawl (None for all)
            
        Returns:
            List of crawl results
        """
        urls = self.parse_sitemap(sitemap_url)
        
        if not urls:
            self.logger.warning("⚠️ No URLs found in sitemap")
            return []
        
        if max_pages:
            urls = urls[:max_pages]
            self.logger.info(f"🔢 Limiting to {max_pages} pages from sitemap")
        
        return await self.crawl_urls_batch(urls, max_concurrent)
    
    def _extract_title_from_markdown(self, markdown: str) -> str:
        """
        Extract title from markdown content (first # heading).
        
        Args:
            markdown: Markdown content
            
        Returns:
            Extracted title or default
        """
        if not markdown:
            return "Untitled"
        
        lines = markdown.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback: use first non-empty line, truncated
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                return line[:100] + ('...' if len(line) > 100 else '')
        
        return "Untitled"
    
    def save_results_to_files(self, results: List[Dict[str, Any]], output_dir: str = "crawled_content") -> None:
        """
        Save crawl results to individual markdown files.
        
        Args:
            results: List of crawl results
            output_dir: Directory to save files in
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        self.logger.info(f"💾 Saving {len(results)} results to {output_path}")
        
        for i, result in enumerate(results):
            if not result.get('success', False):
                continue
            
            # Create safe filename from URL or title
            url = result.get('url', '')
            title = result.get('title', f'page_{i}')
            
            # Clean filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
            
            filename = f"{safe_title}.md"
            filepath = output_path / filename
            
            # Add URL and metadata as header
            content = f"""# {result.get('title', 'Untitled')}

**Source URL:** {url}  
**Crawled:** {result.get('status_code', 'N/A')}  
**Word Count:** {result.get('word_count', 0)}  

---

{result.get('markdown', '')}
"""
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"✅ Saved: {filename}")
            except Exception as e:
                self.logger.error(f"❌ Failed to save {filename}: {str(e)}")
    
    async def add_to_database(self, results: List[Dict[str, Any]], domain: str = "web_crawled") -> int:
        """
        Add crawled content to the document database.
        
        Args:
            results: List of crawl results
            domain: Domain to categorize the content under
            
        Returns:
            Number of documents successfully added
        """
        self.logger.info(f"📊 Adding {len(results)} crawled pages to database")
        
        doc_manager = SimpleDocumentManager()
        added_count = 0
        
        for result in results:
            if not result.get('success', False) or not result.get('markdown'):
                continue
            
            try:
                # Create a temporary file for the content
                title = result.get('title', 'Untitled')
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title.replace(' ', '_')[:50]
                
                temp_filename = f"temp_crawled_{safe_title}.md"
                temp_filepath = Path("temp") / temp_filename
                temp_filepath.parent.mkdir(exist_ok=True)
                
                # Add metadata header to content
                content = f"""# {title}

**Source URL:** {result.get('url', '')}  
**Crawled:** {result.get('status_code', 'N/A')}  
**Word Count:** {result.get('word_count', 0)}  

---

{result.get('markdown', '')}
"""
                
                # Write temporary file
                with open(temp_filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Add to database
                doc_manager.add_document(str(temp_filepath), domain)
                added_count += 1
                
                # Clean up temporary file
                temp_filepath.unlink()
                
                self.logger.info(f"✅ Added to database: {title}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to add {result.get('url', 'unknown')} to database: {str(e)}")
        
        # Clean up temp directory if empty
        temp_dir = Path("temp")
        if temp_dir.exists() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()
        
        self.logger.info(f"✅ Successfully added {added_count} documents to database")
        return added_count


# CLI interface
async def main():
    """Main CLI interface for the web crawler."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Crawler for Crowd Due Dill")
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument("--batch", nargs="+", help="Multiple URLs to crawl in batch")
    parser.add_argument("--sitemap", action="store_true", help="Treat URL as sitemap.xml")
    parser.add_argument("--query", help="Focus crawling on specific query using BM25 filtering")
    parser.add_argument("--legal", action="store_true", help="Optimize for legal documents (preserves structure)")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Max concurrent crawls")
    parser.add_argument("--max-pages", type=int, help="Max pages to crawl from sitemap")
    parser.add_argument("--output-dir", default="crawled_content", help="Output directory for files")
    parser.add_argument("--add-to-db", action="store_true", help="Add results to document database")
    parser.add_argument("--domain", default="web_crawled", help="Domain for database categorization")
    parser.add_argument("--no-filter", action="store_true", help="Disable content filtering")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Initialize crawler
    crawler = WebCrawler(verbose=args.verbose)
    
    try:
        if args.batch:
            # Batch crawling
            results = await crawler.crawl_urls_batch(
                args.batch, 
                max_concurrent=args.max_concurrent,
                use_content_filter=not args.no_filter
            )
        elif args.sitemap:
            # Sitemap crawling
            results = await crawler.crawl_from_sitemap(
                args.url,
                max_concurrent=args.max_concurrent,
                max_pages=args.max_pages
            )
        elif args.query:
            # Query-focused crawling
            result = await crawler.crawl_with_query_focus(args.url, args.query)
            results = [result] if result.get('success') else []
        elif args.legal:
            # Legal document crawling
            result = await crawler.crawl_legal_document(args.url)
            results = [result] if result.get('success') else []
        else:
            # Single page crawling
            result = await crawler.crawl_single_page(args.url, use_content_filter=not args.no_filter)
            results = [result] if result.get('success') else []
        
        # Save results
        if results:
            successful_results = [r for r in results if r.get('success', False)]
            
            if successful_results:
                print(f"\n✅ Successfully crawled {len(successful_results)} pages")
                
                # Save to files
                crawler.save_results_to_files(successful_results, args.output_dir)
                
                # Add to database if requested
                if args.add_to_db:
                    added_count = await crawler.add_to_database(successful_results, args.domain)
                    print(f"📊 Added {added_count} documents to database")
                
                print(f"📁 Results saved to: {args.output_dir}/")
            else:
                print("❌ No successful crawls to save")
        else:
            print("❌ No results to process")
            
    except KeyboardInterrupt:
        print("\n⏹️ Crawling interrupted by user")
    except Exception as e:
        print(f"❌ Error during crawling: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 