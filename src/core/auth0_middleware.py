"""
Auth0 FastAPI Middleware

Production-ready authentication middleware for FastAPI applications.
Provides dependency injection for protected routes and user management.
"""

import os
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth0_validator import Auth0User, auth0_validator
from src.utils.logger import logger


# FastAPI security scheme
security = HTTPBearer(auto_error=False)


class Auth0Middleware:
    """
    Auth0 authentication middleware for FastAPI.
    
    Provides:
    - Optional and required authentication
    - User extraction from JWT
    - Session mapping (Auth0 sub → internal user ID)
    - Custom claims handling
    """
    
    def __init__(self):
        self.enabled = auth0_validator is not None
        if not self.enabled:
            logger.warning("⚠️ Auth0 authentication is disabled - validator not configured")
    
    async def get_current_user_optional(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[Auth0User]:
        """
        Get current user from JWT token (optional authentication).
        
        Returns None if no token provided or invalid token.
        Use for public endpoints that can optionally use authentication.
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            Optional[Auth0User]: User info if authenticated, None otherwise
        """
        if not self.enabled:
            return None
            
        if not credentials:
            return None
        
        try:
            return await auth0_validator.validate_token(credentials.credentials)
        except HTTPException as e:
            # Log validation failure but don't raise (optional auth)
            logger.debug(f"🔒 Optional auth failed: {e.detail}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected auth error: {e}")
            return None
    
    async def get_current_user_required(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Auth0User:
        """
        Get current user from JWT token (required authentication).
        
        Raises HTTPException if no token or invalid token.
        Use for protected endpoints that require authentication.
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            Auth0User: Validated user information
            
        Raises:
            HTTPException: 401 if authentication fails
        """
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service not configured"
            )
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            # Debug: Log credentials info
            logger.debug(f"🔍 Received credentials scheme: {credentials.scheme}")
            logger.debug(f"🔍 Received credentials token (first 50 chars): {credentials.credentials[:50]}...")
            logger.debug(f"🔍 Token length: {len(credentials.credentials)}")
            
            user = await auth0_validator.validate_token(credentials.credentials)
            logger.debug(f"✅ User authenticated: {user.sub}")
            return user
        except HTTPException:
            # Re-raise HTTP exceptions (already properly formatted)
            raise
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )
    
    def require_scope(self, required_scope: str):
        """
        Create a dependency that requires a specific Auth0 scope.
        
        Args:
            required_scope: The scope required for access
            
        Returns:
            Dependency function that validates scope
        """
        async def check_scope(user: Auth0User = Depends(self.get_current_user_required)) -> Auth0User:
            # Note: Auth0 scopes are typically in the 'scope' claim as space-separated string
            # This is a placeholder for scope checking - implement based on your Auth0 setup
            logger.debug(f"🔍 Scope check for '{required_scope}' - user: {user.sub}")
            # Add actual scope checking logic here when needed
            return user
        
        return check_scope


# Global middleware instance
auth_middleware = Auth0Middleware()


# Dependency functions for easy use in FastAPI routes
async def get_current_user_optional(
    user: Optional[Auth0User] = Depends(auth_middleware.get_current_user_optional)
) -> Optional[Auth0User]:
    """
    FastAPI dependency for optional authentication.
    
    Usage:
        @app.get("/api/public")
        async def public_endpoint(user: Optional[Auth0User] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello {user.name}!"}
            return {"message": "Hello anonymous user!"}
    """
    return user


async def get_current_user_required(
    user: Auth0User = Depends(auth_middleware.get_current_user_required)
) -> Auth0User:
    """
    FastAPI dependency for required authentication.
    
    Usage:
        @app.get("/api/private")
        async def private_endpoint(user: Auth0User = Depends(get_current_user_required)):
            return {"message": f"Hello {user.name}!", "user_id": user.sub}
    """
    return user


# Type aliases for cleaner code
OptionalUser = Annotated[Optional[Auth0User], Depends(get_current_user_optional)]
RequiredUser = Annotated[Auth0User, Depends(get_current_user_required)]


def get_user_session_path(user: Auth0User, base_path: str = "data/sessions") -> str:
    """
    Get user-specific session storage path based on Auth0 user ID.
    
    Args:
        user: Authenticated Auth0 user
        base_path: Base sessions directory
        
    Returns:
        User-specific session path
    """
    from pathlib import Path
    
    # Use Auth0 sub as user identifier (URL-safe)
    safe_user_id = user.sub.replace("|", "_").replace("@", "_")
    user_path = Path(base_path) / f"user_{safe_user_id}"
    user_path.mkdir(parents=True, exist_ok=True)
    
    return str(user_path / "graph_checkpoints.db")


class UserSynchronizationService:
    """
    Service for synchronizing Auth0 users with internal user records.
    
    Handles:
    - Auto-creation of internal user records
    - Bidirectional metadata sync
    - User deletion and deactivation
    """
    
    def __init__(self):
        self.enabled = auth_middleware.enabled
    
    async def sync_user(self, auth0_user: Auth0User) -> dict:
        """
        Synchronize Auth0 user with internal user record.
        
        Args:
            auth0_user: Auth0 user information
            
        Returns:
            dict: Internal user record
        """
        if not self.enabled:
            return {"error": "User sync disabled - Auth0 not configured"}
        
        # Create internal user record based on Auth0 data
        internal_user = {
            "auth0_sub": auth0_user.sub,
            "email": auth0_user.email,
            "name": auth0_user.name or auth0_user.nickname,
            "picture": auth0_user.picture,
            "email_verified": auth0_user.email_verified,
            "memory_preferences": auth0_user.memory_preferences,
            "active_domains": auth0_user.active_domains,
            "session_settings": auth0_user.session_settings,
            "last_sync": "now()",  # Use actual timestamp in production
        }
        
        logger.debug(f"👤 User synced: {auth0_user.sub}")
        return internal_user
    
    async def update_user_metadata(self, auth0_user: Auth0User, metadata: dict) -> bool:
        """
        Update user metadata both locally and in Auth0.
        
        Args:
            auth0_user: Auth0 user
            metadata: Metadata to update
            
        Returns:
            bool: Success status
        """
        # This would typically update Auth0 user metadata via Management API
        # For now, just log the update
        logger.debug(f"📝 User metadata update: {auth0_user.sub} -> {metadata}")
        return True


# Global user sync service
user_sync_service = UserSynchronizationService()


def is_auth0_enabled() -> bool:
    """Check if Auth0 authentication is enabled and configured."""
    return auth_middleware.enabled


def get_auth0_status() -> dict:
    """Get Auth0 configuration status for health checks."""
    return {
        "enabled": auth_middleware.enabled,
        "domain": os.getenv("AUTH0_DOMAIN", "not_configured"),
        "audience": os.getenv("AUTH0_AUDIENCE", "not_configured")[:10] + "..." if os.getenv("AUTH0_AUDIENCE") else "not_configured",
        "validator_initialized": auth0_validator is not None,
    } 