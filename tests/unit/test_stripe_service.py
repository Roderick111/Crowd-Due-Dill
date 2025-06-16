#!/usr/bin/env python3
"""
Unit Tests for Stripe Service

Tests for the StripeService class functionality with Context7 best practices.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import HTTPException
import stripe

# Import the service to test
from src.core.stripe_service import StripeService, SubscriptionData, ALLOWED_WEBHOOK_EVENTS


class TestStripeService:
    """Unit tests for StripeService class with Context7 patterns."""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing."""
        return {
            'STRIPE_SECRET_KEY': 'sk_test_mock_key',
            'STRIPE_PUBLISHABLE_KEY': 'pk_test_mock_key',
            'STRIPE_WEBHOOK_SECRET': 'whsec_mock_secret',
            'STRIPE_MONTHLY_PRICE_ID': 'price_mock_monthly',
            'STRIPE_LIFETIME_PRICE_ID': 'price_mock_lifetime'
        }
    
    @pytest.fixture
    def stripe_service(self, mock_env_vars):
        """Create StripeService instance with mocked environment."""
        with patch.dict(os.environ, mock_env_vars):
            service = StripeService()
            return service
    
    def test_initialization_with_valid_config(self, mock_env_vars):
        """Test service initializes correctly with valid configuration."""
        with patch.dict(os.environ, mock_env_vars):
            service = StripeService()
            
            assert service.enabled is True
            assert service.secret_key == 'sk_test_mock_key'
            assert service.publishable_key == 'pk_test_mock_key'
            assert service.webhook_secret == 'whsec_mock_secret'
            assert service.monthly_price_id == 'price_mock_monthly'
            assert service.lifetime_price_id == 'price_mock_lifetime'
    
    def test_initialization_without_secret_key(self):
        """Test service handles missing secret key gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            service = StripeService()
            
            assert service.enabled is False
    
    def test_idempotency_key_generation(self, stripe_service):
        """Test idempotency key generation."""
        key1 = stripe_service._generate_idempotency_key("user123", "monthly")
        key2 = stripe_service._generate_idempotency_key("user123", "monthly")
        key3 = stripe_service._generate_idempotency_key("user456", "monthly")
        
        # Same user and plan on same day should generate same key
        assert key1 == key2
        # Different user should generate different key
        assert key1 != key3
        # Keys should be 32 characters (truncated SHA256)
        assert len(key1) == 32
    
    def test_get_or_create_customer_existing(self, stripe_service):
        """Test getting existing customer."""
        mock_customer = Mock()
        mock_customer.id = "cus_existing123"
        mock_customer.metadata = {"auth0_user_id": "auth0|123"}
        
        with patch.object(stripe_service.client.customers, 'list') as mock_list:
            mock_list.return_value.data = [mock_customer]
            
            customer_id = stripe_service._get_or_create_customer(
                "test@example.com", "auth0|123"
            )
            
            assert customer_id == "cus_existing123"
            mock_list.assert_called_once_with(email="test@example.com", limit=10)
    
    def test_get_or_create_customer_new(self, stripe_service):
        """Test creating new customer."""
        mock_new_customer = Mock()
        mock_new_customer.id = "cus_new123"
        
        with patch.object(stripe_service.client.customers, 'list') as mock_list, \
             patch.object(stripe_service.client.customers, 'create') as mock_create:
            
            mock_list.return_value.data = []  # No existing customer
            mock_create.return_value = mock_new_customer
            
            customer_id = stripe_service._get_or_create_customer(
                "test@example.com", "auth0|123"
            )
            
            assert customer_id == "cus_new123"
            mock_list.assert_called_once_with(email="test@example.com", limit=10)
            mock_create.assert_called_once()
    
    def test_create_checkout_session_monthly(self, stripe_service):
        """Test creating monthly checkout session."""
        mock_session = Mock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"
        mock_session.amount_total = 999
        mock_session.currency = "usd"
        
        with patch.object(stripe_service, '_get_or_create_customer') as mock_customer, \
             patch.object(stripe_service.client.checkout.sessions, 'create') as mock_create:
            
            mock_customer.return_value = "cus_123"
            mock_create.return_value = mock_session
            
            result = stripe_service.create_checkout_session(
                plan_type="monthly",
                user_email="test@example.com",
                auth0_user_id="auth0|123",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel"
            )
            
            assert result["session_id"] == "cs_test_123"
            assert result["url"] == "https://checkout.stripe.com/pay/cs_test_123"
            assert result["plan_type"] == "monthly"
            assert result["customer_id"] == "cus_123"
    
    def test_create_checkout_session_lifetime(self, stripe_service):
        """Test creating lifetime checkout session."""
        mock_session = Mock()
        mock_session.id = "cs_test_456"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_456"
        mock_session.amount_total = 15000
        mock_session.currency = "usd"
        
        with patch.object(stripe_service, '_get_or_create_customer') as mock_customer, \
             patch.object(stripe_service.client.checkout.sessions, 'create') as mock_create:
            
            mock_customer.return_value = "cus_456"
            mock_create.return_value = mock_session
            
            result = stripe_service.create_checkout_session(
                plan_type="lifetime",
                user_email="test@example.com",
                auth0_user_id="auth0|123",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel"
            )
            
            assert result["plan_type"] == "lifetime"
            assert result["session_id"] == "cs_test_456"
    
    def test_create_checkout_session_invalid_plan(self, stripe_service):
        """Test creating checkout session with invalid plan type."""
        with pytest.raises(HTTPException) as exc_info:
            stripe_service.create_checkout_session(
                plan_type="invalid",
                user_email="test@example.com",
                auth0_user_id="auth0|123",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel"
            )
        
        assert exc_info.value.status_code == 400
    
    def test_webhook_event_filtering(self, stripe_service):
        """Test webhook event filtering follows Context7 best practices."""
        # Test allowed event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {'object': {'customer': 'cus_123'}}
        }
        
        with patch('stripe.Webhook.construct_event') as mock_construct, \
             patch.object(stripe_service, '_process_webhook_event') as mock_process:
            
            mock_construct.return_value = mock_event
            mock_process.return_value = {"status": "success"}
            
            result = stripe_service.handle_webhook(b'payload', 'signature')
            
            assert result["status"] == "processed"
            assert result["event_type"] == "checkout.session.completed"
    
    def test_webhook_event_ignored(self, stripe_service):
        """Test webhook ignores untracked events."""
        mock_event = {
            'type': 'untracked.event.type',
            'data': {'object': {}}
        }
        
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = mock_event
            
            result = stripe_service.handle_webhook(b'payload', 'signature')
            
            assert result["status"] == "ignored"
            assert result["reason"] == "event_not_tracked"
    
    def test_webhook_signature_verification_failure(self, stripe_service):
        """Test webhook handles signature verification failure."""
        with patch('stripe.Webhook.construct_event') as mock_construct:
            mock_construct.side_effect = stripe.error.SignatureVerificationError(
                "Invalid signature", "sig_header"
            )
            
            result = stripe_service.handle_webhook(b'payload', 'invalid_signature')
            
            assert result["status"] == "error"
            assert result["reason"] == "invalid_signature"
    
    def test_extract_customer_id(self, stripe_service):
        """Test customer ID extraction from various event types."""
        # Direct customer field
        event_obj = {'customer': 'cus_123'}
        customer_id = stripe_service._extract_customer_id(event_obj, 'invoice.paid')
        assert customer_id == 'cus_123'
        
        # Checkout session
        event_obj = {'customer': 'cus_456'}
        customer_id = stripe_service._extract_customer_id(event_obj, 'checkout.session.completed')
        assert customer_id == 'cus_456'
        
        # No customer field
        event_obj = {'id': 'evt_123'}
        customer_id = stripe_service._extract_customer_id(event_obj, 'some.event')
        assert customer_id is None
    
    def test_get_customer_subscriptions(self, stripe_service):
        """Test getting customer subscriptions."""
        mock_customer = Mock()
        mock_customer.id = "cus_123"
        
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_subscription.status = "active"
        mock_subscription.current_period_start = 1640995200  # 2022-01-01
        mock_subscription.current_period_end = 1643673600    # 2022-02-01
        mock_subscription.items.data = [Mock()]
        mock_subscription.items.data[0].price.id = "price_mock_monthly"
        mock_subscription.items.data[0].price.unit_amount = 999
        mock_subscription.items.data[0].price.currency = "usd"
        
        with patch.object(stripe_service.client.customers, 'list') as mock_customer_list, \
             patch.object(stripe_service.client.subscriptions, 'list') as mock_sub_list:
            
            mock_customer_list.return_value.data = [mock_customer]
            mock_sub_list.return_value.data = [mock_subscription]
            
            subscriptions = stripe_service.get_customer_subscriptions("test@example.com")
            
            assert len(subscriptions) == 1
            assert subscriptions[0].subscription_id == "sub_123"
            assert subscriptions[0].status == "active"
    
    def test_cancel_subscription(self, stripe_service):
        """Test canceling subscription."""
        with patch.object(stripe_service.client.subscriptions, 'update') as mock_update:
            mock_update.return_value = Mock()
            
            result = stripe_service.cancel_subscription("sub_123")
            
            assert result is True
            mock_update.assert_called_once_with(
                "sub_123",
                cancel_at_period_end=True
            )
    
    def test_get_config(self, stripe_service):
        """Test configuration retrieval."""
        config = stripe_service.get_config()
        
        assert config["enabled"] is True
        assert config["publishable_key"] == "pk_test_mock_key"
        assert config["has_monthly_plan"] is True
        assert config["has_lifetime_plan"] is True
        assert config["webhook_configured"] is True
        assert "features" in config
        assert config["features"]["customer_management"] is True
        assert config["features"]["idempotency"] is True
    
    def test_allowed_webhook_events_constant(self):
        """Test that allowed webhook events are properly defined."""
        assert isinstance(ALLOWED_WEBHOOK_EVENTS, list)
        assert len(ALLOWED_WEBHOOK_EVENTS) > 0
        assert "checkout.session.completed" in ALLOWED_WEBHOOK_EVENTS
        assert "customer.subscription.created" in ALLOWED_WEBHOOK_EVENTS
        assert "invoice.paid" in ALLOWED_WEBHOOK_EVENTS
    
    def test_service_disabled_gracefully(self):
        """Test service handles disabled state gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            service = StripeService()
            
            config = service.get_config()
            assert config["enabled"] is False
            assert config["publishable_key"] is None


if __name__ == "__main__":
    pytest.main([__file__]) 