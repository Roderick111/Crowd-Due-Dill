#!/usr/bin/env python3
"""
Prometheus Instrumentation Module

This module handles the integration of Prometheus monitoring with FastAPI,
providing clean instrumentation without polluting the main application code.
"""

from prometheus_fastapi_instrumentator import Instrumentator, metrics
from fastapi import FastAPI
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, Callable

from .prometheus_metrics import (
    track_error,
    track_auth_error,
    track_database_error,
    track_external_service_error,
    track_ai_system_error,
    track_session_error,
    track_performance_metric,
    update_component_health,
    track_business_metric,
    update_active_sessions
)

class PrometheusInstrumentation:
    """
    Main class for handling Prometheus instrumentation of the FastAPI application.
    Provides clean interfaces for monitoring without coupling to business logic.
    """
    
    def __init__(self):
        self.instrumentator = None
        self.app = None
        
    def setup_fastapi_instrumentation(self, app: FastAPI) -> None:
        """
        Set up FastAPI instrumentation with Prometheus.
        
        Args:
            app: FastAPI application instance
        """
        self.app = app
        
        # Create instrumentator with custom configuration
        self.instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/favicon.ico", "/apple-touch-icon.png", "/robots.txt"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="http_requests_inprogress",
            inprogress_labels=True
        )
        
        # Add standard metrics
        self.instrumentator.add(
            metrics.request_size(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="crowdfunding",
                metric_subsystem="api"
            )
        ).add(
            metrics.response_size(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="crowdfunding",
                metric_subsystem="api"
            )
        ).add(
            metrics.latency(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="crowdfunding",
                metric_subsystem="api"
            )
        ).add(
            metrics.requests(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="crowdfunding",
                metric_subsystem="api"
            )
        )
        
        # Initialize instrumentator
        self.instrumentator.instrument(app)
        
        # Add metrics endpoint
        self.instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)
        
        # Set initial component health
        self._initialize_component_health()
    
    def _initialize_component_health(self):
        """Initialize component health status."""
        components = [
            "web_api", "rag_system", "vector_database", "memory_manager",
            "domain_manager", "auth0", "stripe", "qa_cache"
        ]
        
        for component in components:
            update_component_health(component, "unknown")
    
    @contextmanager
    def track_request_performance(self, endpoint: str, user_type: str = "anonymous", **labels):
        """
        Context manager for tracking request performance.
        
        Args:
            endpoint: API endpoint being tracked
            user_type: Type of user making the request
            **labels: Additional labels for the metric
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            track_performance_metric(
                "chat_processing",
                duration,
                endpoint=endpoint,
                user_type=user_type,
                **labels
            )
    
    @contextmanager
    def track_external_api_call(self, service: str, endpoint: str):
        """
        Context manager for tracking external API calls.
        
        Args:
            service: Name of the external service
            endpoint: API endpoint being called
        """
        start_time = time.time()
        status_code = "unknown"
        try:
            yield
            status_code = "success"
        except Exception as e:
            status_code = "error"
            track_external_service_error(service, endpoint, str(type(e).__name__))
            raise
        finally:
            duration = time.time() - start_time
            track_performance_metric(
                "external_api",
                duration,
                service=service,
                endpoint=endpoint,
                status_code=status_code
            )
    
    @contextmanager
    def track_database_operation(self, db_type: str, operation: str, component: str):
        """
        Context manager for tracking database operations.
        
        Args:
            db_type: Type of database (sqlite, chroma, etc.)
            operation: Type of operation (select, insert, search, etc.)
            component: Component performing the operation
        """
        start_time = time.time()
        result_size = 0
        try:
            yield
        except Exception as e:
            track_database_error(db_type, operation, e, component)
            raise
        finally:
            duration = time.time() - start_time
            track_performance_metric(
                "database_query",
                duration,
                query_type=operation,
                table=db_type,
                result_size=str(result_size)
            )
    
    def track_chat_message(self, user_type: str = "anonymous", message_type: str = "user", 
                          cache_hit: bool = False, rag_used: bool = False):
        """
        Track chat message processing.
        
        Args:
            user_type: Type of user (authenticated/anonymous)
            message_type: Type of message (user/assistant)
            cache_hit: Whether response came from cache
            rag_used: Whether RAG system was used
        """
        track_business_metric(
            "message",
            user_type=user_type,
            message_type=message_type,
            cache_hit=str(cache_hit),
            rag_used=str(rag_used)
        )
    
    def track_memory_operation(self, operation: str, memory_type: str, user_type: str = "anonymous"):
        """
        Track memory system operations.
        
        Args:
            operation: Type of operation (store, retrieve, update, etc.)
            memory_type: Type of memory (conversation, user_preference, etc.)
            user_type: Type of user performing the operation
        """
        track_business_metric(
            "memory_operation",
            operation=operation,
            memory_type=memory_type,
            user_type=user_type
        )
    
    def track_document_operation(self, operation: str, domain: str, status: str = "success"):
        """
        Track document processing operations.
        
        Args:
            operation: Type of operation (add, update, remove, search)
            domain: Domain the document belongs to
            status: Status of the operation (success, failure)
        """
        track_business_metric(
            "document_operation",
            operation=operation,
            domain=domain,
            status=status
        )
    
    def update_session_count(self, session_type: str, user_type: str, count: int):
        """
        Update active session count.
        
        Args:
            session_type: Type of session (anonymous, authenticated)
            user_type: Type of user (anonymous, premium, basic)
            count: Current count of active sessions
        """
        update_active_sessions(session_type, user_type, count)
    
    def set_component_healthy(self, component: str):
        """Mark a component as healthy."""
        update_component_health(component, "healthy")
    
    def set_component_degraded(self, component: str):
        """Mark a component as degraded."""
        update_component_health(component, "degraded")
    
    def set_component_unhealthy(self, component: str):
        """Mark a component as unhealthy."""
        update_component_health(component, "unhealthy")
    
    def track_application_error(self, error_type: str, component: str, error: Exception,
                               user_type: str = "anonymous", endpoint: str = "unknown",
                               function: str = "unknown"):
        """
        Track application errors with full context.
        
        Args:
            error_type: Type of error (validation, system, etc.)
            component: Component where error occurred
            error: The actual exception
            user_type: Type of user when error occurred
            endpoint: API endpoint where error occurred
            function: Function where error occurred
        """
        track_error(
            error_type=error_type,
            component=component,
            error=error,
            user_type=user_type,
            endpoint=endpoint,
            function=function
        )

# Global instrumentation instance
prometheus_instrumentation = PrometheusInstrumentation()

# Convenience functions for use throughout the application
def setup_monitoring(app: FastAPI) -> PrometheusInstrumentation:
    """
    Set up monitoring for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        PrometheusInstrumentation instance for use in the application
    """
    prometheus_instrumentation.setup_fastapi_instrumentation(app)
    return prometheus_instrumentation

# Export commonly used functions
__all__ = [
    'PrometheusInstrumentation',
    'prometheus_instrumentation',
    'setup_monitoring'
] 