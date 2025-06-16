/**
 * PremiumModal.js - Premium Plan Comparison Modal
 * Purpose: Shows pricing comparison and premium benefits when user clicks Go Premium
 * Updated: Following Context7 React and Stripe best practices
 */

// Context7 Best Practice: Proper React hook usage
const { useState, useEffect, useCallback } = React;

const PremiumModal = ({ isOpen, onClose }) => {
    const { isAuthenticated, user } = useAuth();
    const [isProcessing, setIsProcessing] = useState(false);
    const [processingPlan, setProcessingPlan] = useState(null);
    const [error, setError] = useState(null);
    const [stripeReady, setStripeReady] = useState(false);
    
    // Context7 Best Practice: Memoized function to avoid recreating on each render
    const checkStripeAvailability = useCallback(async () => {
        try {
            const isEnabled = await window.stripeService.isEnabled();
            setStripeReady(isEnabled);
            if (!isEnabled) {
                setError('Payment processing is temporarily unavailable. Please try again later.');
            }
        } catch (err) {
            console.error('Stripe availability check failed:', err);
            setStripeReady(false);
            setError('Payment system unavailable. Please try again later.');
        }
    }, []);

    // Context7 Best Practice: Check Stripe availability on mount
    useEffect(() => {
        if (isOpen) {
            checkStripeAvailability();
        }
    }, [isOpen, checkStripeAvailability]);

    // Context7 Best Practice: Clear error when modal closes
    useEffect(() => {
        if (!isOpen) {
            setError(null);
            setIsProcessing(false);
            setProcessingPlan(null);
        }
    }, [isOpen]);

    // Context7 Best Practice: Keyboard navigation support
    useEffect(() => {
        if (!isOpen) return;

        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    // Context7 Best Practice: Memoized button state calculation
    const getButtonState = useCallback((planType) => {
        if (!isAuthenticated) {
            return { disabled: true, text: 'Sign in required' };
        }
        if (!stripeReady) {
            return { disabled: true, text: 'Payment unavailable' };
        }
        if (isProcessing && processingPlan === planType) {
            return { disabled: true, text: 'Processing...' };
        }
        if (isProcessing) {
            return { disabled: true, text: planType === 'monthly' ? 'Start Premium Analysis' : 'Get Lifetime' };
        }
        return { 
            disabled: false, 
            text: planType === 'monthly' ? 'Start Premium Analysis' : 'Get Lifetime' 
        };
    }, [isAuthenticated, stripeReady, isProcessing, processingPlan]);

    // Context7 Best Practice: Early return AFTER all hooks
    if (!isOpen) return null;

    const premiumFeatures = [
        {
            icon: "💬",
            title: "Unlimited Conversations",
            description: "No daily limits - explore as much as your spirit desires",
            highlight: true
        },
        {
            icon: "🤖",
            title: "Advanced AI Models",
            description: "Latest GPT-4 & Claude for enhanced regulatory analysis",
            highlight: true
        },
        {
            icon: "📊",
            title: "Comprehensive Coverage",
            description: "Access all regulatory domains + premium compliance content",
            highlight: true
        },
        {
            icon: "⚙️",
            title: "Custom AI Personality",
            description: "Tailor your regulatory advisor to your specific needs",
            highlight: false
        },
        {
            icon: "⚡",
            title: "Priority Responses",
            description: "Skip the queue with instant regulatory guidance",
            highlight: false
        },
        {
            icon: "📚",
            title: "Unlimited History",
            description: "Never lose your due diligence research with advanced search",
            highlight: false
        }
    ];

    const limitations = [
        "Limited to 20 conversations per day",
        "Standard AI models only",
        "Access to 3 basic domains"
    ];

    // Context7 Best Practice: Enhanced error handling with specific error types
    const handleUpgrade = async (planType = 'monthly') => {
        // Context7 Best Practice: Prevent double-clicks during processing
        if (isProcessing) {
            return;
        }

        // Clear any previous errors
        setError(null);
        setIsProcessing(true);
        setProcessingPlan(planType);
        
        try {
            // Context7 Best Practice: Validate prerequisites before proceeding
            if (!isAuthenticated || !user) {
                throw new Error('AUTHENTICATION_REQUIRED');
            }
            
            if (!stripeReady) {
                throw new Error('STRIPE_NOT_AVAILABLE');
            }
            
            // Context7 Best Practice: Validate plan type
            if (!['monthly', 'lifetime'].includes(planType)) {
                throw new Error('INVALID_PLAN_TYPE');
            }
            
            // Context7 Best Practice: Create checkout session with proper error handling
            await window.stripeService.createCheckoutSession(planType);
            
        } catch (error) {
            console.error('Payment error:', error);
            
            // Context7 Best Practice: User-friendly error messages based on error type
            const errorMessages = {
                'AUTHENTICATION_REQUIRED': 'Please sign in to upgrade to premium',
                'STRIPE_NOT_AVAILABLE': 'Payment processing is temporarily unavailable. Please try again later.',
                'INVALID_PLAN_TYPE': 'Invalid subscription plan selected. Please try again.',
                'NETWORK_ERROR': 'Connection error. Please check your internet connection and try again.',
                'CHECKOUT_SESSION_FAILED': 'Unable to start checkout process. Please try again.',
                'STRIPE_NOT_AVAILABLE': 'Payment system is currently unavailable. Please try again later.'
            };
            
            const errorCode = error.code || error.message;
            const userMessage = errorMessages[errorCode] || 'Failed to start payment process. Please try again.';
            
            setError(userMessage);
        } finally {
            setIsProcessing(false);
            setProcessingPlan(null);
        }
    };

    return (
        <div 
            className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-[9999] p-3"
            onClick={onClose}
            role="dialog"
            aria-modal="true"
            aria-labelledby="premium-modal-title"
            aria-describedby="premium-modal-description"
        >
            <div 
                className="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-200 dark:border-gray-700"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="relative p-6 text-center">
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-xl transition-colors"
                        aria-label="Close premium modal"
                    >
                        ×
                    </button>
                    <div className="mb-4">
                        <div className="text-3xl mb-2">⚖️</div>
                        <h2 id="premium-modal-title" className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                            Unlock Premium Due Diligence
                        </h2>
                        <p id="premium-modal-description" className="text-sm text-gray-600 dark:text-gray-300 max-w-sm mx-auto">
                            Enhance your crowdfunding analysis with unlimited access to advanced regulatory guidance
                        </p>
                    </div>
                </div>

                {/* Context7 Best Practice: Error Display */}
                {error && (
                    <div className="mx-6 mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <div className="flex items-center gap-2">
                            <div className="text-red-500 text-sm">⚠️</div>
                            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                        </div>
                    </div>
                )}

                {/* Primary Monthly Offer */}
                <div className="px-6 pb-4">
                    <div className="bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl p-6 text-white text-center relative overflow-hidden">
                        <div className="relative">
                            <div className="text-4xl font-bold mb-4">
                                $9<span className="text-2xl">.99</span>
                                <span className="text-sm opacity-90 ml-2">per month</span>
                            </div>
                            <button
                                onClick={() => handleUpgrade('monthly')}
                                disabled={getButtonState('monthly').disabled}
                                className={`bg-white text-purple-600 font-bold py-3 px-6 rounded-lg transition-all duration-200 shadow-lg text-sm mb-3 w-full ${
                                    getButtonState('monthly').disabled
                                        ? 'opacity-50 cursor-not-allowed' 
                                        : 'hover:bg-gray-50 transform hover:scale-105'
                                }`}
                                aria-describedby={error ? 'error-message' : undefined}
                            >
                                {getButtonState('monthly').text}
                            </button>
                            <p className="text-xs opacity-80">
                                Cancel anytime • 30-day money-back guarantee
                            </p>
                        </div>
                    </div>
                </div>

                {/* Secondary Lifetime Option */}
                <div className="px-6 pb-4">
                    <div className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4 text-center border border-amber-200 dark:border-amber-800">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-gray-700 dark:text-gray-300">
                                <span className="font-semibold">Save 85%</span> with lifetime access
                            </div>
                            <div className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 text-xs px-2 py-1 rounded-full font-medium">
                                Limited Time
                            </div>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="text-left">
                                <div className="text-lg font-bold text-gray-900 dark:text-white">
                                    $150 <span className="text-sm font-normal text-gray-600 dark:text-gray-400">one-time</span>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">vs $119+ annually</div>
                            </div>
                            <button
                                onClick={() => handleUpgrade('lifetime')}
                                disabled={getButtonState('lifetime').disabled}
                                className={`bg-amber-500 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-200 text-sm ${
                                    getButtonState('lifetime').disabled
                                        ? 'opacity-50 cursor-not-allowed' 
                                        : 'hover:bg-amber-600'
                                }`}
                                aria-describedby={error ? 'error-message' : undefined}
                            >
                                {getButtonState('lifetime').text}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Current Limitations */}
                <div className="px-6 pb-4">
                    <div className="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 text-center">
                            You're currently limited by:
                        </h3>
                        <div className="space-y-2" role="list">
                            {limitations.map((limitation, index) => (
                                <div key={index} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400" role="listitem">
                                    <div className="w-1.5 h-1.5 bg-red-400 rounded-full flex-shrink-0" aria-hidden="true"></div>
                                    <span>{limitation}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Premium Features */}
                <div className="px-6 pb-6">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-center">
                        Unlock Everything With Premium
                    </h3>
                    <div className="space-y-3" role="list">
                        {premiumFeatures.map((feature, index) => (
                            <div 
                                key={index} 
                                className={`flex items-start gap-3 p-3 rounded-lg transition-all duration-200 hover:bg-gray-50 dark:hover:bg-gray-700/30 ${
                                    feature.highlight ? 'bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700' : ''
                                }`}
                                role="listitem"
                            >
                                <div className="text-lg flex-shrink-0 mt-0.5" aria-hidden="true">{feature.icon}</div>
                                <div className="flex-1">
                                    <h4 className="font-semibold text-gray-900 dark:text-white mb-1 text-sm">
                                        {feature.title}
                                    </h4>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                                        {feature.description}
                                    </p>
                                </div>
                                {feature.highlight && (
                                    <div className="text-purple-500 flex-shrink-0" aria-hidden="true">
                                        <svg className="w-4 h-4 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

// Export for global use
window.PremiumModal = PremiumModal; 