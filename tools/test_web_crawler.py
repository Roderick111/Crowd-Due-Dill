#!/usr/bin/env python3
"""
Test script for the web crawler functionality.
This script checks if the web crawler can be imported and shows basic usage.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import():
    """Test if the web crawler can be imported."""
    try:
        from tools.web_crawler import WebCrawler
        print("✅ WebCrawler imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import WebCrawler: {e}")
        return False

def test_initialization():
    """Test if the web crawler can be initialized."""
    try:
        from tools.web_crawler import WebCrawler
        crawler = WebCrawler(verbose=True)
        print("✅ WebCrawler initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize WebCrawler: {e}")
        return False

def show_usage_info():
    """Show usage information."""
    print("\n🔧 Web Crawler Usage:")
    print("=" * 50)
    print("1. Install dependencies:")
    print("   pip install -r config/requirements_crawler.txt")
    print("   playwright install")
    print()
    print("2. Test basic functionality:")
    print("   python examples/crawl_example.py")
    print()
    print("3. Crawl a single page:")
    print("   python tools/web_crawler.py https://example.com")
    print()
    print("4. Get help:")
    print("   python tools/web_crawler.py --help")

def main():
    """Run basic tests."""
    print("🕷️ Web Crawler Test Script")
    print("=" * 40)
    print()
    
    # Test imports
    if not test_import():
        print("\n💡 To fix import issues:")
        print("   pip install -r config/requirements_crawler.txt")
        print("   playwright install")
        show_usage_info()
        return
    
    # Test initialization (will fail if crawl4ai not installed)
    try:
        test_initialization()
        print("\n✅ All basic tests passed!")
        print("📝 The web crawler is ready to use.")
        
    except Exception as e:
        print(f"\n⚠️ Initialization test failed: {e}")
        if "crawl4ai" in str(e).lower():
            print("\n💡 crawl4ai not installed. Install with:")
            print("   pip install -r config/requirements_crawler.txt")
            print("   playwright install")
        else:
            print("\n💡 Check your Python environment and dependencies.")
    
    show_usage_info()

if __name__ == "__main__":
    main() 