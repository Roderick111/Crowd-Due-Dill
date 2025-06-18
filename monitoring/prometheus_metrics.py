#!/usr/bin/env python3
"""
Prometheus Metrics Module for Crowd Due Dill

This module defines all Prometheus metrics and helper functions for monitoring
the application. It provides a clean separation between metrics collection
and application logic.
"""

import hashlib
from typing import Optional, Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Enum

# ==================== ERROR TRACKING METRICS ====================

# Comprehensive error tracking with root cause analysis
error_counter = Counter(
    'application_errors_total',
    'Total application errors by type and cause',
    ['error_type', 'error_category', 'component', 'severity', 'user_type', 'endpoint']
)

# Error details with specific failure modes
error_details = Counter(
    'application_error_details_total',
    'Detailed error information for troubleshooting',
    ['error_type', 'component', 'function', 'message_hash', 'user_type']
)

# Authentication errors
auth_errors = Counter(
    'auth_errors_total',
    'Authentication and authorization errors',
    ['auth_provider', 'error_type', 'endpoint', 'user_type']
)

# Database and persistence errors
database_errors = Counter(
    'database_errors_total',
    'Database and persistence related errors',
    ['db_type', 'operation', 'error_type', 'component']
)

# External service errors (OpenAI, Stripe, etc.)
external_service_errors = Counter(
    'external_service_errors_total',
    'Errors from external service integrations',
    ['service', 'operation', 'error_code', 'retry_count']
)

# AI/RAG system errors
ai_system_errors = Counter(
    'ai_system_errors_total',
    'AI and RAG system specific errors',
    ['component', 'error_type', 'model', 'user_type']
)

# Session management errors
session_errors = Counter(
    'session_errors_total',
    'Session management and state errors',
    ['session_type', 'operation', 'error_type', 'user_type']
)

# ==================== PERFORMANCE METRICS ====================

# Chat processing performance with detailed breakdown
chat_processing_time = Histogram(
    'chat_processing_duration_seconds',
    'Time spent processing chat messages',
    ['endpoint', 'user_type', 'rag_used', 'cache_hit', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Vector search performance
vector_search_time = Histogram(
    'vector_search_duration_seconds',
    'Time spent on vector database operations',
    ['operation', 'collection', 'result_count'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

# Database query performance
database_query_time = Histogram(
    'database_query_duration_seconds',
    'Database query execution time',
    ['query_type', 'table', 'result_size'],
    buckets=[0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# External API call performance
external_api_time = Histogram(
    'external_api_duration_seconds',
    'External API call duration',
    ['service', 'endpoint', 'status_code'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# ==================== BUSINESS METRICS ====================

# Chat message tracking
message_count = Counter(
    'chat_messages_total',
    'Total chat messages processed',
    ['user_type', 'message_type', 'cache_hit', 'rag_used']
)

# User session tracking
active_sessions = Gauge(
    'active_sessions_current',
    'Currently active user sessions',
    ['session_type', 'user_type']
)

# Memory system usage
memory_operations = Counter(
    'memory_operations_total',
    'Memory system operations',
    ['operation', 'memory_type', 'user_type']
)

# Document processing
document_operations = Counter(
    'document_operations_total',
    'Document processing operations',
    ['operation', 'domain', 'status']
)

# ==================== SYSTEM HEALTH METRICS ====================

# Component health status
component_health = Enum(
    'component_health_status',
    'Health status of system components',
    ['component'],
    states=['healthy', 'degraded', 'unhealthy', 'unknown']
)

# ==================== HELPER FUNCTIONS ====================

def get_error_severity(error: Exception) -> str:
    """Categorize error severity based on exception type."""
    if isinstance(error, (ValueError, TypeError, KeyError)):
        return "low"
    elif isinstance(error, (ConnectionError, TimeoutError)):
        return "medium"
    elif isinstance(error, (PermissionError, SystemError)):
        return "high"
    else:
        return "medium"

def get_error_category(error: Exception) -> str:
    """Categorize error type for better grouping."""
    if isinstance(error, (ValueError, TypeError, KeyError, AttributeError)):
        return "validation"
    elif isinstance(error, (ConnectionError, TimeoutError)):
        return "network"
    elif isinstance(error, (PermissionError, FileNotFoundError)):
        return "access"
    elif isinstance(error, (MemoryError, SystemError)):
        return "system"
    else:
        return "application"

def hash_error_message(message: str) -> str:
    """Create a consistent hash of error message for grouping similar errors."""
    return hashlib.md5(message.encode()).hexdigest()[:8]

def track_error(error_type: str, component: str, error: Exception, 
                user_type: str = "anonymous", endpoint: str = "unknown",
                **extra_labels):
    """
    Comprehensive error tracking with detailed categorization.
    
    Args:
        error_type: Type of error (validation, auth, system, etc.)
        component: Component where error occurred
        error: The actual exception
        user_type: User type (authenticated/anonymous)
        endpoint: API endpoint where error occurred
        **extra_labels: Additional labels for specific error types
    """
    severity = get_error_severity(error)
    category = get_error_category(error)
    
    # Track general error
    error_counter.labels(
        error_type=error_type,
        error_category=category,
        component=component,
        severity=severity,
        user_type=user_type,
        endpoint=endpoint
    ).inc()
    
    # Track detailed error information
    message_hash = hash_error_message(str(error))
    error_details.labels(
        error_type=error_type,
        component=component,
        function=extra_labels.get('function', 'unknown'),
        message_hash=message_hash,
        user_type=user_type
    ).inc()

def track_auth_error(provider: str, error_type: str, endpoint: str, user_type: str = "anonymous"):
    """Track authentication-related errors."""
    auth_errors.labels(
        auth_provider=provider,
        error_type=error_type,
        endpoint=endpoint,
        user_type=user_type
    ).inc()

def track_database_error(db_type: str, operation: str, error: Exception, component: str):
    """Track database and persistence errors."""
    database_errors.labels(
        db_type=db_type,
        operation=operation,
        error_type=type(error).__name__,
        component=component
    ).inc()

def track_external_service_error(service: str, operation: str, error_code: str, retry_count: int = 0):
    """Track external service integration errors."""
    external_service_errors.labels(
        service=service,
        operation=operation,
        error_code=error_code,
        retry_count=str(retry_count)
    ).inc()

def track_ai_system_error(component: str, error_type: str, model: str = "unknown", user_type: str = "anonymous"):
    """Track AI and RAG system specific errors."""
    ai_system_errors.labels(
        component=component,
        error_type=error_type,
        model=model,
        user_type=user_type
    ).inc()

def track_session_error(session_type: str, operation: str, error_type: str, user_type: str = "anonymous"):
    """Track session management errors."""
    session_errors.labels(
        session_type=session_type,
        operation=operation,
        error_type=error_type,
        user_type=user_type
    ).inc()

def track_performance_metric(metric_name: str, duration: float, **labels):
    """Track performance metrics with appropriate histogram."""
    if metric_name == "chat_processing":
        chat_processing_time.labels(**labels).observe(duration)
    elif metric_name == "vector_search":
        vector_search_time.labels(**labels).observe(duration)
    elif metric_name == "database_query":
        database_query_time.labels(**labels).observe(duration)
    elif metric_name == "external_api":
        external_api_time.labels(**labels).observe(duration)

def update_component_health(component: str, status: str):
    """Update component health status."""
    component_health.labels(component=component).state(status)

def track_business_metric(metric_type: str, **labels):
    """Track business metrics like messages, sessions, etc."""
    if metric_type == "message":
        message_count.labels(**labels).inc()
    elif metric_type == "memory_operation":
        memory_operations.labels(**labels).inc()
    elif metric_type == "document_operation":
        document_operations.labels(**labels).inc()

def update_active_sessions(session_type: str, user_type: str, count: int):
    """Update active session count."""
    active_sessions.labels(
        session_type=session_type,
        user_type=user_type
    ).set(count)

# ==================== METRICS REGISTRY ====================

def get_all_metrics():
    """Return all defined metrics for export."""
    return {
        'error_counter': error_counter,
        'error_details': error_details,
        'auth_errors': auth_errors,
        'database_errors': database_errors,
        'external_service_errors': external_service_errors,
        'ai_system_errors': ai_system_errors,
        'session_errors': session_errors,
        'chat_processing_time': chat_processing_time,
        'vector_search_time': vector_search_time,
        'database_query_time': database_query_time,
        'external_api_time': external_api_time,
        'message_count': message_count,
        'active_sessions': active_sessions,
        'memory_operations': memory_operations,
        'document_operations': document_operations,
        'component_health': component_health
    } 