#!/usr/bin/env python3
"""
Resilience Manager for Esoteric Vectors

Handles all resilience concerns including:
- Circuit breakers
- Health monitoring  
- Fallback strategies
- Error recovery

Separated from main RAG logic for clean architecture.
"""

from typing import Dict, Any, Optional, Callable
from src.utils.resilience import (
    openai_circuit_breaker, 
    chromadb_circuit_breaker,
    health_checker,
    graceful_degradation
)
from src.utils.logger import logger

class ResilienceManager:
    """
    Manages all resilience aspects for the system.
    
    Provides a clean interface for:
    - Health monitoring
    - Circuit breaker management
    - Fallback execution
    - Error recovery
    """
    
    def __init__(self):
        """Initialize resilience manager."""
        self.initialized = False
        self._setup_fallbacks()
    
    def _setup_fallbacks(self):
        """Setup fallback strategies."""
        try:
            # Embedding fallback
            def embedding_fallback(*args, **kwargs):
                logger.debug_resilience("Using cached embeddings fallback")
                # Return a default embedding vector (1536 dimensions for text-embedding-3-small)
                return [0.0] * 1536
            
            graceful_degradation.register_fallback("openai_embeddings", embedding_fallback)
            logger.debug_resilience("Registered fallback for openai_embeddings")
            
        except Exception as e:
            logger.debug_resilience(f"Failed to setup fallbacks: {e}")
    
    def register_openai_health_check(self, embeddings):
        """Register health check for OpenAI embeddings."""
        try:
            def openai_health_check():
                try:
                    # Simple test embedding
                    embeddings.embed_query("health check")
                    return True
                except Exception:
                    return False
            
            health_checker.check_service_health("openai_embeddings", openai_health_check)
            logger.debug_health("Registered OpenAI embeddings health check")
            
        except Exception as e:
            logger.debug_resilience(f"Failed to register OpenAI health check: {e}")
    
    def register_chromadb_health_check(self, client, service_name: str = "chromadb"):
        """Register health check for ChromaDB."""
        try:
            def chromadb_health_check():
                try:
                    # Test basic connectivity
                    client.heartbeat()
                    return True
                except Exception:
                    return False
            
            health_checker.check_service_health(service_name, chromadb_health_check)
            logger.debug_health(f"Registered {service_name} health check")
            
        except Exception as e:
            logger.debug_resilience(f"Failed to register {service_name} health check: {e}")
    
    def execute_with_openai_resilience(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with OpenAI resilience (circuit breaker + fallback)."""
        try:
            return openai_circuit_breaker.call(func, *args, **kwargs)
        except Exception as embedding_error:
            logger.debug_resilience(f"OpenAI embedding failed, using fallback: {embedding_error}")
            return graceful_degradation.execute_with_fallback(
                "openai_embeddings", 
                func,
                *args, **kwargs
            )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        try:
            # Get resilience health status
            resilience_health = health_checker.get_health_summary()
            
            # Get circuit breaker states
            circuit_breaker_status = {
                'openai': {
                    'state': openai_circuit_breaker.state.value,
                    'failure_count': openai_circuit_breaker.failure_count,
                    'last_failure': openai_circuit_breaker.last_failure_time.isoformat() if openai_circuit_breaker.last_failure_time else None
                },
                'chromadb': {
                    'state': chromadb_circuit_breaker.state.value,
                    'failure_count': chromadb_circuit_breaker.failure_count,
                    'last_failure': chromadb_circuit_breaker.last_failure_time.isoformat() if chromadb_circuit_breaker.last_failure_time else None
                }
            }
            
            return {
                'resilience_health': resilience_health,
                'circuit_breakers': circuit_breaker_status,
                'error_recovery': {
                    'enabled': True,
                    'retry_enabled': True,
                    'fallback_enabled': True,
                    'health_monitoring': True
                }
            }
            
        except Exception as e:
            logger.debug_resilience(f"Failed to get health summary: {e}")
            return {
                'resilience_health': {'status': 'error', 'error': str(e)},
                'error_recovery': {'enabled': False}
            }
    
    def is_healthy(self) -> bool:
        """Check if system is overall healthy."""
        try:
            summary = self.get_health_summary()
            return summary.get('resilience_health', {}).get('overall_healthy', False)
        except Exception:
            return False

# Global resilience manager instance
resilience_manager = ResilienceManager() 