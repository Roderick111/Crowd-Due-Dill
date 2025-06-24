#!/bin/bash
# One-liner database test
python -c "
import sys; sys.path.insert(0, 'src')
from core.contextual_rag import OptimizedContextualRAGSystem
rag = OptimizedContextualRAGSystem()
stats = rag.get_stats()
domains = rag.get_domain_status()
result = rag.query('EU regulation', k=1)
chunks = stats.get('vectorstore_docs', 0)
active = len(domains.get('active_domains', []))
found = len(result.get('chunks', []))
print(f'📊 Database: {chunks} chunks, {active} domains, query: {found} results')
status = 'PASS' if chunks > 0 and active == 0 and found > 0 else 'FAIL'
print(f'🎯 Status: {status}')
"
