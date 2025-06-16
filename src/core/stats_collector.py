#!/usr/bin/env python3
"""
Stats Collector for Esoteric Vectors

Clean statistics collection with:
- Query performance tracking
- Vectorstore health monitoring
- Resilience metrics integration
- Memory system monitoring
- Clean logging
"""

import time
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime

from src.utils.logger import logger


class StatsCollector:
    """
    Clean statistics collector for system performance monitoring.
    
    Tracks:
    - Query performance and response times
    - Vectorstore health and document counts
    - System resilience metrics
    - Cache hit rates and efficiency
    - Memory system performance
    """
    
    def __init__(self, max_recent_queries: int = 100):
        """Initialize stats collector."""
        self.max_recent_queries = max_recent_queries
        
        # Query performance tracking
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'recent_times': deque(maxlen=max_recent_queries)
        })
        
        # Memory system tracking
        self.memory_stats = {
            'summaries_created': 0,
            'summary_creation_times': deque(maxlen=50),
            'memory_context_builds': 0,
            'short_term_trims': 0,
            'toggles': defaultdict(int)  # Track toggle operations
        }
        
        # System start time
        self.start_time = datetime.now()
        
        logger.debug("Stats collector initialized")
    
    def record_query(self, query_type: str, response_time: float):
        """Record a query execution."""
        stats = self.query_stats[query_type]
        stats['count'] += 1
        stats['total_time'] += response_time
        stats['recent_times'].append(response_time)
        
        logger.debug(f"Recorded {query_type} query: {response_time:.3f}s")
    
    def record_memory_summary_creation(self, creation_time: float, summary_length: int):
        """Record memory summary creation."""
        self.memory_stats['summaries_created'] += 1
        self.memory_stats['summary_creation_times'].append(creation_time)
        logger.debug(f"Recorded memory summary creation: {creation_time:.3f}s, {summary_length} chars")
    
    def record_memory_context_build(self):
        """Record memory context building."""
        self.memory_stats['memory_context_builds'] += 1
    
    def record_short_term_trim(self):
        """Record short-term memory trimming."""
        self.memory_stats['short_term_trims'] += 1
    
    def record_memory_toggle(self, memory_type: str, enabled: bool):
        """Record memory toggle operation."""
        action = f"{memory_type}_{'enabled' if enabled else 'disabled'}"
        self.memory_stats['toggles'][action] += 1
        logger.debug(f"Recorded memory toggle: {action}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        stats = self.memory_stats.copy()
        
        # Calculate averages
        if stats['summary_creation_times']:
            avg_creation_time = sum(stats['summary_creation_times']) / len(stats['summary_creation_times'])
            stats['avg_summary_creation_time'] = avg_creation_time
        else:
            stats['avg_summary_creation_time'] = 0.0
        
        return stats
    
    def get_comprehensive_memory_stats(self, memory_manager=None) -> Dict[str, Any]:
        """Get comprehensive memory system statistics."""
        stats = self.get_memory_stats()
        
        if memory_manager:
            # Get current memory status
            memory_status = memory_manager.get_memory_status()
            stats['current_status'] = memory_status
            
            # Get memory manager internal stats
            manager_stats = memory_manager.get_memory_stats()
            stats['manager_status'] = manager_stats
        
        return stats
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get comprehensive query performance statistics."""
        if not self.query_stats:
            return {
                'total_queries': 0,
                'avg_response_time': 0.0,
                'by_type': {}
            }
        
        total_queries = sum(stats['count'] for stats in self.query_stats.values())
        total_time = sum(stats['total_time'] for stats in self.query_stats.values())
        avg_response_time = total_time / total_queries if total_queries > 0 else 0.0
        
        by_type = {}
        for query_type, stats in self.query_stats.items():
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0.0
            recent_avg = sum(stats['recent_times']) / len(stats['recent_times']) if stats['recent_times'] else 0.0
            
            by_type[query_type] = {
                'count': stats['count'],
                'avg_response_time': avg_time,
                'recent_avg_response_time': recent_avg,
                'total_time': stats['total_time']
            }
        
        return {
            'total_queries': total_queries,
            'avg_response_time': avg_response_time,
            'total_time': total_time,
            'by_type': by_type
        }
    
    def get_vectorstore_stats(self, vectorstore) -> Dict[str, Any]:
        """Get vectorstore statistics."""
        stats = {}
        
        try:
            if vectorstore and hasattr(vectorstore, '_collection'):
                collection = vectorstore._collection
                if collection:
                    stats['vectorstore_docs'] = collection.count()
                    stats['collection_name'] = collection.name
                    
                    # Collection metadata
                    metadata = getattr(collection, 'metadata', {})
                    if metadata:
                        stats['collection_metadata'] = {
                            'version': metadata.get('version', 'unknown'),
                            'created': metadata.get('created', 'unknown'),
                            'embedding_model': metadata.get('embedding_model', 'unknown'),
                            'last_updated': metadata.get('last_updated', 'unknown')
                        }
                    
                    # Health metrics
                    health_metrics = self._get_collection_health(collection)
                    stats['collection_health'] = health_metrics
                else:
                    stats['vectorstore_docs'] = 0
                    stats['error'] = 'Collection not available'
            else:
                stats['vectorstore_docs'] = 0
                stats['error'] = 'Vectorstore not available'
                
        except Exception as e:
            logger.debug(f"Error getting vectorstore stats: {e}")
            stats['vectorstore_docs'] = 0
            stats['error'] = str(e)
        
        return stats
    
    def _get_collection_health(self, collection) -> Dict[str, Any]:
        """Get collection health metrics."""
        try:
            # Basic health check
            doc_count = collection.count()
            
            health = {
                'status': 'healthy' if doc_count > 0 else 'empty',
                'document_count': doc_count,
                'last_checked': datetime.now().isoformat()
            }
            
            # Check if collection has metadata
            metadata = getattr(collection, 'metadata', {})
            if metadata:
                health['has_metadata'] = True
                health['version'] = metadata.get('version', 'unknown')
            else:
                health['has_metadata'] = False
            
            return health
            
        except Exception as e:
            logger.debug(f"Collection health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            }
    
    def get_system_uptime(self) -> Dict[str, Any]:
        """Get system uptime information."""
        uptime = datetime.now() - self.start_time
        
        return {
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0]  # Remove microseconds
        }
    
    def reset_query_stats(self):
        """Reset all query statistics."""
        self.query_stats.clear()
        logger.debug("Query statistics reset")
    
    def get_performance_summary(self) -> str:
        """Get formatted performance summary."""
        try:
            query_stats = self.get_query_stats()
            uptime = self.get_system_uptime()
            
            if query_stats['total_queries'] == 0:
                return f"📊 System uptime: {uptime['uptime_formatted']} | No queries processed yet"
            
            summary_parts = [
                f"📊 Uptime: {uptime['uptime_formatted']}",
                f"Queries: {query_stats['total_queries']}",
                f"Avg: {query_stats['avg_response_time']:.3f}s"
            ]
            
            # Add breakdown by type if multiple types
            if len(query_stats['by_type']) > 1:
                type_breakdown = []
                for query_type, stats in query_stats['by_type'].items():
                    type_breakdown.append(f"{query_type}: {stats['count']}")
                summary_parts.append(f"({', '.join(type_breakdown)})")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.debug(f"Performance summary error: {e}")
            return "📊 Performance data unavailable"
    
    def get_comprehensive_stats(self, **kwargs) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        stats = {}
        
        # Core performance stats
        stats['query_performance'] = self.get_query_stats()
        stats['system_uptime'] = self.get_system_uptime()
        
        # Vectorstore stats
        vectorstore = kwargs.get('vectorstore')
        if vectorstore:
            vectorstore_stats = self.get_vectorstore_stats(vectorstore)
            stats.update(vectorstore_stats)
        
        # Domain manager stats
        domain_manager = kwargs.get('domain_manager')
        if domain_manager:
            try:
                stats['domain_config'] = domain_manager.get_status()
            except Exception as e:
                logger.debug(f"Domain manager stats error: {e}")
                stats['domain_config'] = {'error': str(e)}
        
        # Add resilience stats if available
        try:
            from .resilience_manager import resilience_manager
            resilience_stats = resilience_manager.get_health_summary()
            stats.update(resilience_stats)
        except Exception as e:
            logger.debug(f"Resilience stats error: {e}")
            stats['resilience_health'] = {'error': str(e)}
        
        return stats
    
    def print_comprehensive_stats(self, **kwargs):
        """Print comprehensive system statistics to console."""
        try:
            print("📊 System Statistics")
            print("=" * 50)
            
            # System uptime
            uptime = self.get_system_uptime()
            print(f"⏱️  Uptime: {uptime['uptime_formatted']}")
            
            # Query performance
            query_stats = self.get_query_stats()
            if query_stats['total_queries'] > 0:
                print(f"📈 Query Performance:")
                print(f"   Total queries: {query_stats['total_queries']}")
                print(f"   Average response time: {query_stats['avg_response_time']:.3f}s")
                
                if len(query_stats['by_type']) > 1:
                    print(f"   By type:")
                    for query_type, stats in query_stats['by_type'].items():
                        print(f"     {query_type}: {stats['count']} queries, {stats['avg_response_time']:.3f}s avg")
            else:
                print("📈 Query Performance: No queries processed yet")
            
            # Memory statistics
            memory_stats = self.get_memory_stats()
            print(f"🧠 Memory System:")
            print(f"   Summaries created: {memory_stats['summaries_created']}")
            print(f"   Context builds: {memory_stats['memory_context_builds']}")
            print(f"   Short-term trims: {memory_stats['short_term_trims']}")
            
            if memory_stats['avg_summary_creation_time'] > 0:
                print(f"   Avg summary creation: {memory_stats['avg_summary_creation_time']:.3f}s")
            
            if memory_stats['toggles']:
                print(f"   Toggle operations:")
                for action, count in memory_stats['toggles'].items():
                    print(f"     {action}: {count}")
            
            # Add memory manager status if available
            memory_manager = kwargs.get('memory_manager')
            if memory_manager:
                status = memory_manager.get_memory_status()
                manager_stats = memory_manager.get_memory_stats()
                print(f"   Current status: ST:{status['short_term']}, MT:{status['medium_term']}")
                print(f"   Manager status: {manager_stats['status']}")
            
            # Vectorstore stats
            vectorstore = kwargs.get('vectorstore')
            if vectorstore:
                vectorstore_stats = self.get_vectorstore_stats(vectorstore)
                print(f"📚 Vectorstore: {vectorstore_stats.get('vectorstore_docs', 0)} documents")
                if 'collection_health' in vectorstore_stats:
                    health = vectorstore_stats['collection_health']
                    print(f"   Health: {health.get('status', 'unknown')}")
            
            # Domain manager stats
            domain_manager = kwargs.get('domain_manager')
            if domain_manager:
                try:
                    domain_status = domain_manager.get_status()
                    active_domains = domain_status.get('active_domains', [])
                    print(f"🎯 Domains: {len(active_domains)} active - {', '.join(active_domains) if active_domains else 'None'}")
                except Exception as e:
                    logger.debug(f"Domain manager stats error: {e}")
            
            # Q&A Cache stats
            qa_cache = kwargs.get('qa_cache')
            if qa_cache:
                try:
                    qa_stats = qa_cache.get_stats()
                    print(f"⚡ Q&A Cache: {qa_stats.get('total_qa_pairs', 0)} pairs, {qa_stats.get('hit_rate', 0):.1f}% hit rate")
                except Exception as e:
                    logger.debug(f"Q&A cache stats error: {e}")
            
            # System health
            try:
                from .resilience_manager import resilience_manager
                resilience_stats = resilience_manager.get_health_summary()
                if resilience_stats.get('resilience_health', {}).get('overall_healthy'):
                    print("🛡️ System Health: All services operational")
                else:
                    print("⚠️ System Health: Some services degraded")
            except Exception as e:
                logger.debug(f"Resilience stats error: {e}")
                
        except Exception as e:
            logger.error(f"Stats printing error: {e}") 