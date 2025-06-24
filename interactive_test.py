#!/usr/bin/env python3
"""
Interactive Database Test
Test the agent's access to the database with custom queries.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.contextual_rag import OptimizedContextualRAGSystem

def interactive_test():
    """Run interactive database testing."""
    print("🧪 Interactive Database Access Test")
    print("=" * 50)
    print("This tool lets you test what the agent can access")
    print("Type 'exit' to quit, 'stats' for database info")
    print("=" * 50)
    
    try:
        # Initialize RAG system
        print("📚 Initializing RAG system...")
        rag_system = OptimizedContextualRAGSystem()
        
        # Show initial stats
        stats = rag_system.get_stats()
        total_chunks = stats.get('vectorstore_docs', 0)
        domain_status = rag_system.get_domain_status()
        
        print(f"✅ Database ready: {total_chunks} chunks available")
        print(f"✅ No domain restrictions: {len(domain_status.get('active_domains', []))} active domains")
        print()
        
        while True:
            try:
                query = input("🔍 Enter your query: ").strip()
                
                if query.lower() == 'exit':
                    print("👋 Goodbye!")
                    break
                
                if query.lower() == 'stats':
                    print(f"\n📊 Database Statistics:")
                    print(f"   Total chunks: {total_chunks}")
                    print(f"   Active domains: {len(domain_status.get('active_domains', []))}")
                    print(f"   Available domains: {len(domain_status.get('available_domains', []))}")
                    print()
                    continue
                
                if not query:
                    continue
                
                # Execute query
                print(f"🔍 Searching for: '{query}'")
                result = rag_system.query(query, k=5)
                
                chunks = result.get('chunks', [])
                if chunks:
                    print(f"✅ Found {len(chunks)} relevant chunks:")
                    
                    for i, chunk in enumerate(chunks, 1):
                        metadata = chunk.get('metadata', {})
                        source = metadata.get('document.source', 'unknown')
                        reg_number = metadata.get('structure.regulation_number', 'N/A')
                        
                        content = chunk.get('content', '')
                        preview = content[:150] + "..." if len(content) > 150 else content
                        
                        print(f"\n   📄 Chunk {i}:")
                        print(f"      Source: {source}")
                        print(f"      Regulation: {reg_number}")
                        print(f"      Content: {preview}")
                else:
                    print("❌ No relevant chunks found")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
                
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    return True

if __name__ == "__main__":
    interactive_test() 