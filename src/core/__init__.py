"""
Core System Components

Central location for all core system functionality.
"""

from .contextual_rag import OptimizedContextualRAGSystem
from .domain_manager import DomainManager
from .resilience_manager import ResilienceManager
from .stats_collector import StatsCollector
from .auth0_validator import Auth0User, Auth0TokenValidator, get_auth0_config
from .auth0_middleware import (
    auth_middleware, 
    get_current_user_optional, 
    get_current_user_required,
    OptionalUser,
    RequiredUser,
    get_user_session_path,
    user_sync_service,
    is_auth0_enabled,
    get_auth0_status
)
from .stripe_service import stripe_service
from .auth0_management import auth0_management

__all__ = [
    'OptimizedContextualRAGSystem',
    'DomainManager', 
    'ResilienceManager',
    'StatsCollector',
    # Auth0 components
    'Auth0User',
    'Auth0TokenValidator',
    'get_auth0_config',
    'auth_middleware',
    'get_current_user_optional',
    'get_current_user_required',
    'OptionalUser',
    'RequiredUser',
    'get_user_session_path',
    'user_sync_service',
    'is_auth0_enabled',
    'get_auth0_status',
    # Stripe components
    'stripe_service',
    # Auth0 Management API
    'auth0_management',
]
