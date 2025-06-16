#!/usr/bin/env python3
"""
Resilience Utilities for Error Recovery and API Reliability

Implements Context7 best practices for:
- Exponential backoff retry logic
- Circuit breaker pattern
- Graceful degradation
- Connection health monitoring
"""

import time
import random
import logging
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for API resilience.
    
    Based on Context7 patterns for handling repeated failures gracefully.
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: tuple = (Exception,)):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            expected_exception: Exception types to count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.debug("🔄 Circuit breaker: Attempting recovery")
            else:
                raise Exception(f"Circuit breaker OPEN - service unavailable (last failure: {self.last_failure_time})")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
    
    def _on_success(self):
        """Handle successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            logger.debug("✅ Circuit breaker: Service recovered")
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"🚨 Circuit breaker OPEN after {self.failure_count} failures")


def retry_with_backoff(max_retries: int = 3,
                      base_delay: float = 1.0,
                      max_delay: float = 60.0,
                      exponential_base: float = 2.0,
                      jitter: bool = True,
                      exceptions: tuple = (Exception,)):
    """
    Decorator for exponential backoff retry logic.
    
    Based on Context7 OpenAI API best practices.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd
        exceptions: Exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"❌ Final retry attempt failed for {func.__name__}: {e}")
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"⚠️ Retry {attempt + 1}/{max_retries} for {func.__name__} in {delay:.2f}s: {e}")
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator


class HealthChecker:
    """
    Health monitoring for services with automatic recovery.
    """
    
    def __init__(self, check_interval: int = 30):
        """
        Initialize health checker.
        
        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self.last_check = {}
        self.health_status = {}
    
    def check_service_health(self, service_name: str, health_func: Callable) -> bool:
        """
        Check service health with caching.
        
        Args:
            service_name: Name of the service
            health_func: Function that returns True if healthy
            
        Returns:
            bool: True if service is healthy
        """
        now = datetime.now()
        last_check_time = self.last_check.get(service_name)
        
        # Use cached result if recent
        if (last_check_time and 
            now - last_check_time < timedelta(seconds=self.check_interval)):
            return self.health_status.get(service_name, False)
        
        # Perform health check
        try:
            is_healthy = health_func()
            self.health_status[service_name] = is_healthy
            self.last_check[service_name] = now
            
            if is_healthy:
                logger.debug(f"✅ {service_name} health check passed")
            else:
                logger.warning(f"⚠️ {service_name} health check failed")
            
            return is_healthy
        except Exception as e:
            logger.error(f"❌ {service_name} health check error: {e}")
            self.health_status[service_name] = False
            self.last_check[service_name] = now
            return False
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of all service health statuses."""
        return {
            'services': self.health_status.copy(),
            'last_checks': {k: v.isoformat() for k, v in self.last_check.items()},
            'overall_healthy': all(self.health_status.values()) if self.health_status else False
        }


class GracefulDegradation:
    """
    Manages graceful degradation when services are unavailable.
    """
    
    def __init__(self):
        self.fallback_strategies = {}
        self.service_status = {}
    
    def register_fallback(self, service_name: str, fallback_func: Callable):
        """Register a fallback function for a service."""
        self.fallback_strategies[service_name] = fallback_func
        logger.debug_resilience(f"Registered fallback for {service_name}")
    
    def execute_with_fallback(self, service_name: str, primary_func: Callable, *args, **kwargs) -> Any:
        """
        Execute primary function with fallback on failure.
        
        Args:
            service_name: Name of the service
            primary_func: Primary function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result from primary or fallback function
        """
        try:
            result = primary_func(*args, **kwargs)
            self.service_status[service_name] = True
            return result
        except Exception as e:
            logger.warning(f"⚠️ {service_name} primary function failed: {e}")
            self.service_status[service_name] = False
            
            # Try fallback
            fallback_func = self.fallback_strategies.get(service_name)
            if fallback_func:
                logger.debug(f"🔄 Using fallback for {service_name}")
                try:
                    return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback also failed for {service_name}: {fallback_error}")
                    raise fallback_error
            else:
                logger.error(f"❌ No fallback available for {service_name}")
                raise e


# Global instances for easy access
health_checker = HealthChecker()
graceful_degradation = GracefulDegradation()


def resilient_api_call(service_name: str,
                      max_retries: int = 3,
                      circuit_breaker: Optional[CircuitBreaker] = None):
    """
    Combined decorator for resilient API calls with retry, circuit breaker, and health monitoring.
    
    Args:
        service_name: Name of the service for monitoring
        max_retries: Maximum retry attempts
        circuit_breaker: Optional circuit breaker instance
    """
    def decorator(func: Callable) -> Callable:
        # Apply retry logic
        retried_func = retry_with_backoff(
            max_retries=max_retries,
            exceptions=(Exception,)
        )(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Use circuit breaker if provided
            if circuit_breaker:
                return circuit_breaker.call(retried_func, *args, **kwargs)
            else:
                return retried_func(*args, **kwargs)
        
        return wrapper
    return decorator


# Pre-configured circuit breakers for common services
openai_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=(Exception,)
)

chromadb_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=(Exception,)
) 