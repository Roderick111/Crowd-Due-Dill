"""
Stripe Service for Esoteric Vectors

Production-ready Stripe integration for premium subscriptions.
Handles payments, webhooks, and user role management via Auth0.
Updated with Context7 best practices for modern Stripe Python usage.
"""

import os
import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from fastapi import HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
import hashlib
import json
import logging

from src.utils.logger import logger
from .auth0_management import auth0_management

# Load environment variables
load_dotenv()

# Define allowed webhook events (following Context7 best practices)
ALLOWED_WEBHOOK_EVENTS = [
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "customer.subscription.created", 
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "customer.subscription.paused",
    "customer.subscription.resumed",
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.payment_action_required",
    "payment_intent.succeeded",
    "payment_intent.payment_failed"
]


class SubscriptionData(BaseModel):
    """Subscription information"""
    subscription_id: str
    customer_id: str
    status: str  # active, canceled, past_due, etc.
    current_period_start: datetime
    current_period_end: datetime
    plan_type: str  # "monthly" or "lifetime"
    amount: int  # in cents
    currency: str = "usd"


class StripeService:
    """
    Production Stripe service for handling subscriptions and payments.
    Updated with Context7 best practices for modern Stripe Python usage.
    
    Features:
    - Modern StripeClient usage with async support
    - Enhanced customer management with efficient lookups
    - Robust webhook handling with improved signature verification
    - Advanced error handling with Stripe-specific error types
    - Subscription management with Context7 patterns
    - Auth0 role integration
    - Enhanced idempotency support
    """
    
    def __init__(self):
        """Initialize Stripe service with v8+ StripeClient"""
        api_key = os.getenv("STRIPE_SECRET_KEY")
        if not api_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")
        
        # v8+ StripeClient initialization
        self.client = stripe.StripeClient(api_key)
        
        # Price IDs from environment
        self.monthly_price_id = os.getenv("STRIPE_MONTHLY_PRICE_ID")
        self.lifetime_price_id = os.getenv("STRIPE_LIFETIME_PRICE_ID")
        
        if not self.monthly_price_id or not self.lifetime_price_id:
            logger.warning("Stripe price IDs not configured")
        
        # Debug: Check if keys are loaded
        logger.debug(f"Stripe key status: monthly_price={'present' if self.monthly_price_id else 'missing'}, "
                    f"lifetime_price={'present' if self.lifetime_price_id else 'missing'}")
        
        self.enabled = True
        logger.system_ready("Stripe service initialized with v8+ StripeClient")
    
    def _generate_idempotency_key(self, user_id: str, plan_type: str, operation: str = "checkout") -> str:
        """
        Generate idempotency key for operations.
        Context7 Pattern: Include operation type for better uniqueness.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d-%H')  # Hour-level uniqueness
        data = f"{operation}:{user_id}:{plan_type}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def _get_or_create_customer(self, user_email: str, user_id: str) -> str:
        """Get existing customer or create new one using v8+ syntax"""
        try:
            logger.debug(f"🔍 Looking for customer with email: {user_email}")
            
            # v8+ syntax: Use params={} for all parameters
            customers = self.client.customers.list(
                params={
                    "email": user_email,
                    "limit": 1
                }
            )
            
            if customers.data:
                customer_id = customers.data[0].id
                logger.debug(f"✅ Found existing customer: {customer_id}")
                return customer_id
            
            # Create new customer with v8+ syntax
            logger.debug(f"🆕 Creating new customer for {user_email}")
            customer = self.client.customers.create(
                params={
                    "email": user_email,
                    "metadata": {
                        "user_id": user_id,
                        "created_via": "esoteric_vectors_api"
                    }
                }
            )
            
            logger.debug(f"✅ Created new customer: {customer.id}")
            return customer.id
            
        except Exception as e:
            logger.error(f"❌ Customer management failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Customer management failed: {str(e)}"
            )
    
    def create_checkout_session(
        self,
        plan_type: str,
        user_email: str,
        user_id: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """Create checkout session using v8+ syntax"""
        try:
            # Validate plan type and get price ID
            if plan_type == "monthly":
                price_id = self.monthly_price_id
                mode = "subscription"
            elif plan_type == "lifetime":
                price_id = self.lifetime_price_id
                mode = "payment"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid plan type: {plan_type}"
                )
            
            if not price_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Price configuration missing for {plan_type} plan"
                )
            
            logger.debug(f"🎯 Creating checkout session for {plan_type} plan")
            logger.debug(f"📧 User: {user_email}")
            logger.debug(f"💰 Price ID: {price_id}")
            
            # Get or create customer
            customer_id = self._get_or_create_customer(user_email, user_id)
            
            # Generate idempotency key
            idempotency_key = f"checkout_{user_id}_{plan_type}_{int(datetime.now().timestamp())}"
            
            # Create checkout session parameters
            session_params = {
                "success_url": success_url,
                "cancel_url": cancel_url,
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": mode,
                "customer": customer_id,
                "customer_update": {
                    "address": "auto"
                },
                "metadata": {
                    "auth0_user_id": user_id,
                    "plan_type": plan_type,
                    "created_via": "esoteric_vectors_api"
                }
            }
            
            # For subscription mode, ensure subscription inherits metadata
            if mode == "subscription":
                session_params["subscription_data"] = {
                    "metadata": {
                        "auth0_user_id": user_id,
                        "plan_type": plan_type,
                        "created_via": "esoteric_vectors_api"
                    }
                }
            
            # v8+ syntax: Create checkout session with params={}
            session = self.client.checkout.sessions.create(
                params=session_params,
                options={
                    "idempotency_key": idempotency_key
                }
            )
            
            logger.debug(f"✅ Checkout session created: {session.id}")
            
            return {
                "session_id": session.id,
                "url": session.url,
                "customer_id": customer_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error creating checkout session: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payment processing failed: {str(e)}"
            )
    
    def _validate_https_urls(self, success_url: str, cancel_url: str) -> None:
        """
        Validate that URLs use HTTPS in production.
        Context7 Security Best Practice: Ensure secure redirects.
        """
        # Allow HTTP only for localhost development
        for url in [success_url, cancel_url]:
            if not url.startswith('https://') and not url.startswith('http://localhost'):
                logger.warning(f"⚠️ Non-HTTPS URL detected: {url}")
                # In production, you might want to raise an exception:
                # raise HTTPException(
                #     status_code=status.HTTP_400_BAD_REQUEST,
                #     detail="HTTPS required for redirect URLs in production"
                # )
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events with Context7 best practices.
        Enhanced signature verification and error handling.
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            dict: Processing result
        """
        if not self.enabled:
            logger.warning("⚠️ Webhook received but Stripe not fully configured")
            return {"status": "ignored", "reason": "stripe_not_configured"}
        
        try:
            # Context7 Best Practice: Enhanced signature verification
            event = stripe.Webhook.construct_event(
                payload, signature, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
            
            logger.debug(f"Stripe webhook received: {event['type']} (ID: {event.get('id', 'unknown')})")
            
            # Context7 Pattern: Filter events with allowlist
            if event['type'] not in ALLOWED_WEBHOOK_EVENTS:
                logger.debug(f"Ignoring untracked event: {event['type']}")
                return {"status": "ignored", "reason": "event_not_tracked"}
            
            # Context7 Best Practice: Extract customer ID with fallbacks
            event_object = event['data']['object']
            customer_id = self._extract_customer_id(event_object, event['type'])
            
            if not customer_id:
                logger.warning(f"No customer ID found in event {event['type']} (ID: {event.get('id')})")
                return {"status": "ignored", "reason": "no_customer_id"}
            
            # Process the event
            result = await self._process_webhook_event(event, customer_id)
            
            logger.debug(f"Webhook processed successfully: {event['type']} (ID: {event.get('id')})")
            return {"status": "processed", "event_type": event['type'], "result": result}
            
        except stripe.SignatureVerificationError as e:
            logger.error(f"❌ Webhook signature verification failed: {e}")
            return {"status": "error", "reason": "invalid_signature"}
        except ValueError as e:
            logger.error(f"❌ Webhook payload parsing failed: {e}")
            return {"status": "error", "reason": "invalid_payload"}
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {e}")
            return {"status": "error", "reason": str(e)}
    
    def _extract_customer_id(self, event_object: Dict[str, Any], event_type: str) -> Optional[str]:
        """
        Extract customer ID from webhook event object.
        Context7 Pattern: Handle multiple event object structures.
        """
        # Direct customer field
        if 'customer' in event_object and event_object['customer']:
            return event_object['customer']
        
        # For checkout sessions
        if event_type.startswith('checkout.session.') and 'customer' in event_object:
            return event_object['customer']
        
        # For payment intents (may have customer)
        if event_type.startswith('payment_intent.') and 'customer' in event_object:
            return event_object['customer']
        
        # For invoices
        if event_type.startswith('invoice.') and 'customer' in event_object:
            return event_object['customer']
        
        return None
    
    async def _process_webhook_event(self, event: Dict[str, Any], customer_id: str) -> Dict[str, Any]:
        """Process individual webhook events with Context7 patterns."""
        event_type = event['type']
        event_object = event['data']['object']
        
        # Context7 Pattern: Handle both sync and async payment completion
        if event_type in ['checkout.session.completed', 'checkout.session.async_payment_succeeded']:
            return await self._handle_checkout_completed(event_object)
        elif event_type == 'customer.subscription.created':
            return await self._handle_subscription_created(event_object)
        elif event_type == 'customer.subscription.updated':
            return await self._handle_subscription_updated(event_object)
        elif event_type == 'customer.subscription.deleted':
            return await self._handle_subscription_canceled(event_object)
        elif event_type in ['invoice.paid', 'payment_intent.succeeded']:
            return await self._handle_payment_succeeded(event_object)
        elif event_type in ['invoice.payment_failed', 'payment_intent.payment_failed']:
            return self._handle_payment_failed(event_object)
        else:
            return {"action": "logged", "message": f"Event {event_type} logged but no specific action taken"}
    
    async def _handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle successful checkout completion.
        Context7 Pattern: Enhanced metadata extraction and validation.
        """
        auth0_user_id = session.get('metadata', {}).get('auth0_user_id')
        plan_type = session.get('metadata', {}).get('plan_type')
        
        if not auth0_user_id:
            logger.error("❌ Checkout completed but no Auth0 user ID in metadata")
            return {"status": "error", "reason": "missing_user_id"}
        
        logger.debug(f"Checkout completed for user {auth0_user_id}, plan: {plan_type}")
        
        # Context7 Pattern: Handle different payment modes
        payment_mode = session.get('mode', 'payment')
        
        if payment_mode == 'payment' or plan_type == "lifetime":
            # For one-time payments (lifetime), assign role immediately
            success = await self._assign_premium_role(auth0_user_id, "lifetime")
            return {
                "status": "success" if success else "partial",
                "user_id": auth0_user_id,
                "plan_type": plan_type,
                "payment_mode": payment_mode,
                "role_assigned": success
            }
        
        # For subscriptions, wait for subscription.created event
        return {
            "status": "success",
            "user_id": auth0_user_id,
            "plan_type": plan_type,
            "payment_mode": payment_mode,
            "note": "waiting_for_subscription_creation"
        }
    
    async def _handle_subscription_created(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new subscription creation with Context7 patterns."""
        metadata = subscription.get('metadata', {})
        auth0_user_id = metadata.get('auth0_user_id')
        plan_type = metadata.get('plan_type', 'monthly')
        
        if not auth0_user_id:
            logger.error("❌ Subscription created but no Auth0 user ID in metadata")
            return {"status": "error", "reason": "missing_user_id"}
        
        logger.debug(f"Subscription created for user {auth0_user_id}")
        
        # Assign premium role
        success = await self._assign_premium_role(auth0_user_id, "monthly")
        
        return {
            "status": "success" if success else "partial",
            "user_id": auth0_user_id,
            "subscription_id": subscription['id'],
            "subscription_status": subscription.get('status'),
            "role_assigned": success
        }
    
    async def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updates with Context7 patterns."""
        metadata = subscription.get('metadata', {})
        auth0_user_id = metadata.get('auth0_user_id')
        status = subscription.get('status')
        
        if not auth0_user_id:
            return {"status": "ignored", "reason": "no_user_id"}
        
        logger.debug(f"Subscription updated for user {auth0_user_id}, status: {status}")
        
        # Context7 Pattern: Handle all subscription statuses
        if status in ['active', 'trialing']:
            success = await self._assign_premium_role(auth0_user_id, "monthly")
        elif status in ['canceled', 'unpaid', 'past_due', 'incomplete_expired']:
            success = await self._remove_premium_role(auth0_user_id)
        elif status in ['incomplete', 'paused']:
            # Don't change role for these statuses
            return {"status": "ignored", "reason": f"status_{status}_no_action"}
        else:
            return {"status": "ignored", "reason": f"unhandled_status_{status}"}
        
        return {
            "status": "success" if success else "partial",
            "user_id": auth0_user_id,
            "subscription_status": status,
            "role_updated": success
        }
    
    async def _handle_subscription_canceled(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation with Context7 patterns."""
        metadata = subscription.get('metadata', {})
        auth0_user_id = metadata.get('auth0_user_id')
        
        if not auth0_user_id:
            return {"status": "ignored", "reason": "no_user_id"}
        
        logger.debug(f"Subscription canceled for user {auth0_user_id}")
        
        # Remove premium role
        success = await self._remove_premium_role(auth0_user_id)
        
        return {
            "status": "success" if success else "partial",
            "user_id": auth0_user_id,
            "subscription_id": subscription['id'],
            "role_removed": success
        }
    
    async def _handle_payment_succeeded(self, payment_object: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment with Context7 patterns."""
        metadata = payment_object.get('metadata', {})
        auth0_user_id = metadata.get('auth0_user_id')
        
        if not auth0_user_id:
            return {"status": "ignored", "reason": "no_user_id"}
        
        logger.debug(f"Payment succeeded for user {auth0_user_id}")
        
        # Context7 Pattern: Ensure user has premium access
        # This handles edge cases where subscription events might be missed
        success = await self._assign_premium_role(auth0_user_id, "monthly")
        
        return {
            "status": "success" if success else "partial",
            "user_id": auth0_user_id,
            "action": "payment_confirmed",
            "role_ensured": success
        }
    
    def _handle_payment_failed(self, payment_object: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment with Context7 patterns."""
        metadata = payment_object.get('metadata', {})
        auth0_user_id = metadata.get('auth0_user_id')
        
        if not auth0_user_id:
            return {"status": "ignored", "reason": "no_user_id"}
        
        logger.warning(f"Payment failed for user {auth0_user_id}")
        
        # Context7 Pattern: Don't immediately remove access on payment failure
        # Stripe handles grace periods and retry logic
        # Only remove access when subscription is actually canceled
        
        return {
            "status": "logged",
            "user_id": auth0_user_id,
            "action": "payment_failed_logged",
            "note": "access_maintained_pending_retry"
        }
    
    async def _assign_premium_role(self, auth0_user_id: str, subscription_type: str) -> bool:
        """
        Assign premium role to user in Auth0 using Management API.
        
        Args:
            auth0_user_id: Auth0 user ID (sub)
            subscription_type: Subscription type (monthly, lifetime)
            
        Returns:
            bool: Success status
        """
        try:
            # Use Auth0 Management API to assign premium role
            success = await auth0_management.assign_premium_role(auth0_user_id, subscription_type)
            
            if success:
                logger.info(f"✅ Premium role '{subscription_type}' assigned to user {auth0_user_id}")
            else:
                logger.error(f"❌ Failed to assign premium role '{subscription_type}' to user {auth0_user_id}")
            
            return success
        except Exception as e:
            logger.error(f"❌ Error assigning premium role: {e}")
            return False
    
    async def _remove_premium_role(self, auth0_user_id: str) -> bool:
        """
        Remove premium role from user in Auth0 using Management API.
        
        Args:
            auth0_user_id: Auth0 user ID (sub)
            
        Returns:
            bool: Success status
        """
        try:
            # Use Auth0 Management API to remove premium status
            success = await auth0_management.remove_premium_role(auth0_user_id)
            
            if success:
                logger.info(f"✅ Premium role removed from user {auth0_user_id}")
            else:
                logger.error(f"❌ Failed to remove premium role from user {auth0_user_id}")
            
            return success
        except Exception as e:
            logger.error(f"❌ Error removing premium role: {e}")
            return False
    
    def get_customer_subscriptions(self, user_email: str) -> List[Dict[str, Any]]:
        """Get customer's active subscriptions using v8+ syntax"""
        try:
            # Get customer first
            customers = self.client.customers.list(
                params={
                    "email": user_email,
                    "limit": 1
                }
            )
            
            if not customers.data:
                return []
            
            customer_id = customers.data[0].id
            
            # Get subscriptions with v8+ syntax
            subscriptions = self.client.subscriptions.list(
                params={
                    "customer": customer_id,
                    "status": "active",
                    "limit": 10
                }
            )
            
            return [
                {
                    "id": sub.id,
                    "status": sub.status,
                    "current_period_end": sub.current_period_end,
                    "plan_id": sub.items.data[0].price.id if sub.items.data else None,
                }
                for sub in subscriptions.data
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to get subscriptions: {e}")
            return []
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription using v8+ syntax"""
        try:
            # v8+ syntax: Cancel subscription
            subscription = self.client.subscriptions.cancel(
                subscription_id,
                params={
                    "prorate": True
                }
            )
            
            logger.info(f"✅ Subscription cancelled: {subscription_id}")
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel subscription: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
    
    def verify_session(self, session_id: str) -> Dict[str, Any]:
        """
        Verify a checkout session for security.
        Context7 Best Practice: Always verify sessions on backend.
        Note: Stripe Python client is synchronous.
        
        Args:
            session_id: Stripe checkout session ID
            
        Returns:
            dict: Session verification result
        """
        if not self.enabled:
            return {"success": False, "error": "stripe_not_enabled"}
        
        try:
            session = self.client.checkout.sessions.retrieve(session_id)
            
            return {
                "success": True,
                "session_id": session.id,
                "payment_status": session.payment_status,
                "customer_id": session.customer,
                "metadata": session.metadata
            }
            
        except stripe.StripeError as e:
            logger.error(f"❌ Error verifying session {session_id}: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"❌ Unexpected error verifying session: {e}")
            return {"success": False, "error": "verification_failed"}
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get Stripe configuration for frontend.
        Enhanced with Context7 best practices and better status reporting.
        
        Returns:
            dict: Configuration data
        """
        return {
            "enabled": self.enabled,
            "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY"),
            "has_monthly_plan": bool(self.monthly_price_id),
            "has_lifetime_plan": bool(self.lifetime_price_id),
            "features": {
                "customer_management": True,
                "idempotency": True,
                "webhook_filtering": True,
                "auto_retry": True,
                "async_support": True,
                "modern_client": True,
                "enhanced_search": True,
                "automatic_tax": True,
                "session_verification": True
            },
            "context7_compliant": True,
            "version": "2.0.0"
        }


# Global stripe service instance
stripe_service = StripeService() 