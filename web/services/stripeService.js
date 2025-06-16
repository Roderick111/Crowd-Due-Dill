/**
 * stripeService.js - Context7-Compliant Stripe Integration
 * Following official Stripe.js best practices from Context7 documentation
 * Updated: Uses loadStripe pattern, improved error handling, and fraud detection
 */

class StripeService {
    constructor() {
        this.stripePromise = null;
        this.config = null;
        this.initialized = false;
        this.initPromise = null;
        this.activeCheckoutPromise = null; // Context7: Prevent duplicate requests
    }

    async init() {
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = this._initialize();
        return this.initPromise;
    }

    async _initialize() {
        try {
            // Get Stripe configuration from backend
            const response = await window.apiService.makeRequest('/stripe/config');
            this.config = response;

            if (!this.config.enabled || !this.config.publishable_key) {
                console.warn('Stripe not configured');
                return false;
            }

            // Context7 Best Practice: Use loadStripe instead of manual script loading
            this.stripePromise = this._loadStripe();
            this.initialized = true;
            
            return true;
        } catch (error) {
            console.error('Failed to initialize Stripe:', error);
            this.initialized = false;
            return false;
        }
    }

    _loadStripe() {
        // Context7 Best Practice: Load Stripe.js from CDN for browser environments
        return new Promise((resolve, reject) => {
            // Check if Stripe is already loaded
            if (window.Stripe) {
                // Context7 Best Practice: Fraud detection is enabled by default
                resolve(window.Stripe(this.config.publishable_key));
                return;
            }

            // Context7 Pattern: Dynamic script loading for browser
            const script = document.createElement('script');
            script.src = 'https://js.stripe.com/v3/';
            script.async = true;
            
            script.onload = () => {
                if (window.Stripe) {
                    // Context7 Best Practice: Fraud detection is enabled by default
                    resolve(window.Stripe(this.config.publishable_key));
                } else {
                    reject(new Error('Stripe.js failed to load'));
                }
            };
            
            script.onerror = () => {
                reject(new Error('Failed to load Stripe.js script'));
            };
            
            // Context7 Best Practice: Add to head for better loading
            document.head.appendChild(script);
        }).catch(error => {
            console.error('Failed to load Stripe.js:', error);
            throw new Error('Payment system unavailable');
        });
    }

    async getStripe() {
        await this.init();
        if (!this.stripePromise) {
            throw new Error('Stripe not initialized');
        }
        return this.stripePromise;
    }

    async createCheckoutSession(planType) {
        // Context7 Best Practice: Idempotency - prevent duplicate requests
        if (this.activeCheckoutPromise) {
            console.log('Checkout session already in progress, waiting...');
            return this.activeCheckoutPromise;
        }

        this.activeCheckoutPromise = this._createCheckoutSessionInternal(planType);
        
        try {
            const result = await this.activeCheckoutPromise;
            return result;
        } finally {
            this.activeCheckoutPromise = null;
        }
    }

    async _createCheckoutSessionInternal(planType) {
        try {
            // Ensure initialization
            await this.init();
            if (!this.initialized) {
                throw new Error('STRIPE_NOT_AVAILABLE');
            }

            // Validate plan type
            if (!['monthly', 'lifetime'].includes(planType)) {
                throw new Error('INVALID_PLAN_TYPE');
            }

            // Check authentication
            const authState = await window.getAuth0State();
            if (!authState.isAuthenticated) {
                throw new Error('AUTHENTICATION_REQUIRED');
            }

            // Context7 Best Practice: Generate idempotency key for backend request
            const idempotencyKey = this._generateIdempotencyKey(planType);

            // Context7 Best Practice: Create session via backend with proper headers
            // Note: Removed auth cache clearing as it was causing Authorization header to be missing
            const response = await window.apiService.makeRequest('/stripe/create-checkout-session', {
                method: 'POST',
                headers: { 
                    'Idempotency-Key': idempotencyKey
                    // Note: Removed Content-Type override to preserve auth headers
                    // apiService.makeRequest already sets Content-Type: application/json
                },
                body: JSON.stringify({ 
                    plan_type: planType
                    // Note: client_reference_id removed as backend doesn't expect it
                    // User identification is handled via JWT authentication
                })
            });

            if (!response.success || !response.checkout_url) {
                throw new Error(response.error || 'CHECKOUT_SESSION_FAILED');
            }

            // Context7 Best Practice: Use window.location.href for redirect
            // This ensures proper navigation and browser history handling
            window.location.href = response.checkout_url;
            
            return response;

        } catch (error) {
            console.error('Checkout session creation failed:', error);
            throw this._handleCheckoutError(error);
        }
    }

    _generateIdempotencyKey(planType) {
        // Context7 Pattern: Generate unique idempotency key
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2);
        return `checkout_${planType}_${timestamp}_${random}`;
    }

    _handleCheckoutError(error) {
        // Context7 Best Practice: User-friendly error messages
        const errorMap = {
            'AUTHENTICATION_REQUIRED': 'Please sign in to upgrade to premium',
            'INVALID_PLAN_TYPE': 'Invalid subscription plan selected',
            'STRIPE_NOT_AVAILABLE': 'Payment system is currently unavailable',
            'CHECKOUT_SESSION_FAILED': 'Unable to start checkout process',
            'NETWORK_ERROR': 'Connection error. Please check your internet connection'
        };

        const errorCode = error.message;
        const userMessage = errorMap[errorCode] || 'Payment processing failed. Please try again.';
        
        // Return user-friendly error
        const friendlyError = new Error(userMessage);
        friendlyError.code = errorCode;
        friendlyError.originalError = error;
        
        return friendlyError;
    }

    async handlePaymentResult() {
        // Context7 Pattern: Handle return from Stripe Checkout
        const urlParams = new URLSearchParams(window.location.search);
        const sessionId = urlParams.get('session_id');
        const paymentStatus = urlParams.get('payment');

        if (sessionId || paymentStatus) {
            // Clean URL without affecting browser history
            const cleanUrl = window.location.pathname;
            window.history.replaceState({}, document.title, cleanUrl);

            if (paymentStatus === 'success') {
                // Handle payment success even without session_id
                if (sessionId) {
                    // Context7: Verify session on backend for security if we have session_id
                    try {
                        const verification = await window.apiService.makeRequest(
                            `/stripe/verify-session/${sessionId}`
                        );
                        
                        return {
                            status: 'success',
                            sessionId: sessionId,
                            verified: verification.success,
                            message: 'Payment successful! Premium features activated.'
                        };
                    } catch (error) {
                        console.warn('Session verification failed:', error);
                        return {
                            status: 'success',
                            sessionId: sessionId,
                            verified: false,
                            message: 'Payment completed. Verifying activation...'
                        };
                    }
                } else {
                    // No session_id, but payment was successful based on URL parameter
                    return {
                        status: 'success',
                        sessionId: null,
                        verified: false,
                        message: 'Payment successful! Activating premium features...'
                    };
                }
            } else if (sessionId && !paymentStatus) {
                // We have session_id but no payment status - verify session
                try {
                    const verification = await window.apiService.makeRequest(
                        `/stripe/verify-session/${sessionId}`
                    );
                    
                    return {
                        status: 'success',
                        sessionId: sessionId,
                        verified: verification.success,
                        message: 'Payment successful! Premium features activated.'
                    };
                } catch (error) {
                    console.warn('Session verification failed:', error);
                    return {
                        status: 'success',
                        sessionId: sessionId,
                        verified: false,
                        message: 'Payment completed. Verifying activation...'
                    };
                }
            } else if (paymentStatus === 'canceled') {
                return {
                    status: 'canceled',
                    message: 'Payment was canceled.'
                };
            }
        }

        return null;
    }

    async isEnabled() {
        try {
            await this.init();
            return this.initialized;
        } catch (error) {
            console.error('Stripe availability check failed:', error);
            return false;
        }
    }

    async getConfig() {
        try {
            await this.init();
            return this.config || { enabled: false };
        } catch (error) {
            console.error('Stripe config retrieval failed:', error);
            return { enabled: false };
        }
    }

    // Context7 Best Practice: Health check method
    async healthCheck() {
        try {
            const stripe = await this.getStripe();
            // Simple check to ensure Stripe is responsive
            return {
                status: 'healthy',
                initialized: this.initialized,
                hasConfig: !!this.config,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                status: 'unhealthy',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    // Context7 Pattern: Cleanup method for SPA navigation
    destroy() {
        this.stripePromise = null;
        this.config = null;
        this.initialized = false;
        this.initPromise = null;
        this.activeCheckoutPromise = null;
    }
}

// Create global instance following Context7 singleton pattern
const stripeService = new StripeService();
window.stripeService = stripeService;

// Context7 Best Practice: Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = stripeService;
} 