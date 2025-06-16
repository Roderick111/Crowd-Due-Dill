"""
Auth0 Management API Service

Handles premium user role assignments using Auth0 RBAC.
Context7 compliant implementation using official Auth0 Python SDK.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException

# Context7 Best Practice: Use official Auth0 Python SDK
from auth0.management import Auth0
from auth0.authentication import GetToken
from auth0.asyncify import asyncify

from src.utils.logger import logger


class Auth0ManagementService:
    """
    Auth0 Management API service for role-based premium subscription management.
    Context7 compliant implementation using official Auth0 Python SDK.
    
    Features:
    - Role-based premium subscription management
    - Automatic role assignment/removal
    - Subscription status tracking via roles
    - Token caching for efficiency
    - Enhanced error handling
    """
    
    # Premium subscription roles
    ROLES = {
        'free': 'free-user',
        'monthly': 'premium-monthly', 
        'lifetime': 'premium-lifetime',
        'admin': 'admin'
    }
    
    def __init__(self):
        self.domain = os.getenv("AUTH0_DOMAIN")
        self.client_id = os.getenv("AUTH0_MANAGEMENT_CLIENT_ID")
        self.client_secret = os.getenv("AUTH0_MANAGEMENT_CLIENT_SECRET")
        self.audience = f"https://{self.domain}/api/v2/"
        
        # Token caching
        self._access_token = None
        self._token_expires_at = None
        self._auth0_client = None
        
        # Check if Management API is configured
        self.enabled = bool(self.domain and self.client_id and self.client_secret)
        
        if not self.enabled:
            logger.warning("⚠️ Auth0 Management API not configured - premium role assignment disabled")
        else:
            logger.info("✅ Auth0 Management API service initialized with role-based premium management")

    async def _get_access_token(self) -> str:
        """Get cached access token or fetch new one."""
        now = datetime.utcnow()
        
        # Check if we have a valid cached token
        if (self._access_token and 
            self._token_expires_at and 
            now < self._token_expires_at - timedelta(minutes=5)):  # 5 min buffer
            return self._access_token
        
        try:
            # Get new token using Auth0 SDK
            get_token = GetToken(self.domain, self.client_id, client_secret=self.client_secret)
            token_response = get_token.client_credentials(self.audience)
            
            self._access_token = token_response['access_token']
            expires_in = token_response.get('expires_in', 3600)
            self._token_expires_at = now + timedelta(seconds=expires_in)
            
            logger.debug("🔄 Auth0 Management API token refreshed")
            return self._access_token
            
        except Exception as e:
            logger.error(f"❌ Failed to get Auth0 Management API token: {e}")
            raise HTTPException(status_code=500, detail="Auth0 Management API authentication failed")

    async def _get_auth0_client(self) -> Auth0:
        """Get Auth0 management client with fresh token."""
        if not self.enabled:
            raise HTTPException(status_code=503, detail="Auth0 Management API not configured")
        
        token = await self._get_access_token()
        
        # Create new client with fresh token
        self._auth0_client = Auth0(self.domain, token)
        return self._auth0_client

    async def _get_role_id(self, role_name: str) -> Optional[str]:
        """Get Auth0 role ID by role name."""
        try:
            client = await self._get_auth0_client()
            roles = client.roles.list()
            
            for role in roles['roles']:
                if role['name'] == role_name:
                    return role['id']
            
            logger.warning(f"⚠️ Role '{role_name}' not found in Auth0")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get role ID for '{role_name}': {e}")
            return None

    async def assign_premium_role(self, user_id: str, subscription_type: str = 'monthly') -> bool:
        """
        Assign premium role to user based on subscription type.
        
        Args:
            user_id: Auth0 user ID
            subscription_type: 'monthly', 'lifetime', or 'free'
            
        Returns:
            bool: Success status
        """
        if not self.enabled:
            logger.warning("⚠️ Auth0 Management API not configured - cannot assign premium role")
            return False
        
        try:
            # Get the role name for subscription type
            role_name = self.ROLES.get(subscription_type, self.ROLES['free'])
            role_id = await self._get_role_id(role_name)
            
            if not role_id:
                logger.error(f"❌ Role '{role_name}' not found - cannot assign to user {user_id}")
                return False
            
            client = await self._get_auth0_client()
            
            # Remove all existing premium roles first
            await self._remove_all_premium_roles(user_id, client)
            
            # Assign new role
            client.users.add_roles(user_id, [role_id])
            
            # Update user metadata with subscription details
            metadata_update = {
                'premium_status': 'active' if subscription_type != 'free' else 'inactive',
                'plan_type': subscription_type,
                'premium_activated_at': datetime.utcnow().isoformat(),
                'subscription_source': 'stripe',
                'role_assigned': role_name
            }
            
            client.users.update(user_id, {'app_metadata': metadata_update})
            
            logger.info(f"✅ Assigned role '{role_name}' to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to assign premium role to user {user_id}: {e}")
            return False

    async def _remove_all_premium_roles(self, user_id: str, client: Auth0) -> None:
        """Remove all premium-related roles from user."""
        try:
            # Get user's current roles
            user_roles = client.users.list_roles(user_id)
            
            # Find premium roles to remove
            premium_role_names = set(self.ROLES.values())
            roles_to_remove = []
            
            for role in user_roles['roles']:
                if role['name'] in premium_role_names:
                    roles_to_remove.append(role['id'])
            
            # Remove premium roles
            if roles_to_remove:
                client.users.remove_roles(user_id, roles_to_remove)
                logger.debug(f"🗑️ Removed {len(roles_to_remove)} premium roles from user {user_id}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to remove existing premium roles from user {user_id}: {e}")

    async def remove_premium_role(self, user_id: str) -> bool:
        """
        Remove premium role and assign free user role.
        
        Args:
            user_id: Auth0 user ID
            
        Returns:
            bool: Success status
        """
        return await self.assign_premium_role(user_id, 'free')

    async def get_user_premium_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's premium status based on roles.
        
        Args:
            user_id: Auth0 user ID
            
        Returns:
            dict: Premium status information
        """
        if not self.enabled:
            return {
                'premium_status': 'unknown',
                'plan_type': 'unknown',
                'roles': [],
                'error': 'Auth0 Management API not configured'
            }
        
        try:
            client = await self._get_auth0_client()
            
            # Get user roles
            user_roles = client.users.list_roles(user_id)
            role_names = [role['name'] for role in user_roles['roles']]
            
            # Get user metadata
            user_info = client.users.get(user_id)
            app_metadata = user_info.get('app_metadata', {})
            
            # Determine premium status from roles
            premium_status = 'inactive'
            plan_type = 'free'
            
            if self.ROLES['lifetime'] in role_names:
                premium_status = 'active'
                plan_type = 'lifetime'
            elif self.ROLES['monthly'] in role_names:
                premium_status = 'active'
                plan_type = 'monthly'
            elif self.ROLES['admin'] in role_names:
                premium_status = 'active'
                plan_type = 'admin'
            
            return {
                'premium_status': premium_status,
                'plan_type': plan_type,
                'roles': role_names,
                'premium_activated_at': app_metadata.get('premium_activated_at'),
                'subscription_source': app_metadata.get('subscription_source'),
                'role_assigned': app_metadata.get('role_assigned')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get premium status for user {user_id}: {e}")
            return {
                'premium_status': 'error',
                'plan_type': 'unknown',
                'roles': [],
                'error': str(e)
            }

    async def list_premium_users(self) -> List[Dict[str, Any]]:
        """
        List all users with premium roles.
        
        Returns:
            list: Premium users information
        """
        if not self.enabled:
            return []
        
        try:
            client = await self._get_auth0_client()
            premium_users = []
            
            # Get all premium roles
            premium_role_names = [self.ROLES['monthly'], self.ROLES['lifetime'], self.ROLES['admin']]
            
            for role_name in premium_role_names:
                role_id = await self._get_role_id(role_name)
                if role_id:
                    # Get users with this role
                    role_users = client.roles.list_users(role_id)
                    
                    for user in role_users['users']:
                        user_info = {
                            'user_id': user['user_id'],
                            'email': user.get('email'),
                            'name': user.get('name'),
                            'role': role_name,
                            'created_at': user.get('created_at'),
                            'last_login': user.get('last_login')
                        }
                        
                        # Get additional metadata
                        app_metadata = user.get('app_metadata', {})
                        user_info.update({
                            'premium_activated_at': app_metadata.get('premium_activated_at'),
                            'subscription_source': app_metadata.get('subscription_source')
                        })
                        
                        premium_users.append(user_info)
            
            logger.info(f"📊 Found {len(premium_users)} premium users")
            return premium_users
            
        except Exception as e:
            logger.error(f"❌ Failed to list premium users: {e}")
            return []

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get user's permissions based on their roles.
        
        Args:
            user_id: Auth0 user ID
            
        Returns:
            list: User permissions
        """
        if not self.enabled:
            return []
        
        try:
            client = await self._get_auth0_client()
            
            # Get user roles
            user_roles = client.users.list_roles(user_id)
            permissions = set()
            
            # Get permissions for each role
            for role in user_roles['roles']:
                role_permissions = client.roles.list_permissions(role['id'])
                for perm in role_permissions['permissions']:
                    permissions.add(perm['permission_name'])
            
            return list(permissions)
            
        except Exception as e:
            logger.error(f"❌ Failed to get permissions for user {user_id}: {e}")
            return []


# Global instance
auth0_management = Auth0ManagementService() 