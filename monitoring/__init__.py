"""
Monitoring Module for Crowd Due Dill

This module provides comprehensive monitoring and metrics collection for the
Crowd Due Dill application using Prometheus and Grafana.

Usage:
    from monitoring import setup_monitoring
    
    app = FastAPI()
    monitoring = setup_monitoring(app)
    
    # Track errors
    monitoring.track_application_error("validation", "auth", error, "authenticated", "/chat")
    
    # Track performance
    with monitoring.track_request_performance("/chat", "authenticated"):
        # ... process request
        pass
    
    # Track business metrics
    monitoring.track_chat_message("authenticated", "user", cache_hit=True, rag_used=True)
"""

from .prometheus_instrumentation import (
    PrometheusInstrumentation,
    prometheus_instrumentation,
    setup_monitoring
)

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
    update_active_sessions,
    get_all_metrics
)

__all__ = [
    # Main instrumentation classes
    'PrometheusInstrumentation',
    'prometheus_instrumentation',
    'setup_monitoring',
    
    # Direct metric functions
    'track_error',
    'track_auth_error',
    'track_database_error',
    'track_external_service_error',
    'track_ai_system_error',
    'track_session_error',
    'track_performance_metric',
    'update_component_health',
    'track_business_metric',
    'update_active_sessions',
    'get_all_metrics'
] 