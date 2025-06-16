/**
 * premiumService.js - Premium Status Management Service
 * Purpose: Handles premium user status checking and subscription management
 */

class PremiumService {
    constructor() {
        this.premiumStatus = null;
        this.lastFetch = null;
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes cache
    }

    /**
     * Check if user has premium access
     * @returns {Promise<Object>} Premium status object
     */
    async getPremiumStatus() {
        try {
            // Check cache first
            const now = Date.now();
            if (this.premiumStatus && this.lastFetch && (now - this.lastFetch) < this.cacheTimeout) {
                return this.premiumStatus;
            }

            // Fetch fresh status from API
            const response = await window.apiService.makeRequest('/auth/premium-status');
            
            if (response && response.success) {
                this.premiumStatus = response.premium_status;
                this.lastFetch = now;
                return this.premiumStatus;
            } else {
                throw new Error('Failed to fetch premium status');
            }
        } catch (error) {
            console.error('Error fetching premium status:', error);
            // Return default free status on error
            return {
                premium_status: 'inactive',
                plan_type: 'free',
                roles: [],
                error: error.message
            };
        }
    }

    /**
     * Check if user has premium access (simple boolean)
     * @returns {Promise<boolean>}
     */
    async isPremiumUser() {
        try {
            const status = await this.getPremiumStatus();
            return status.premium_status === 'active';
        } catch (error) {
            console.error('Error checking premium status:', error);
            return false;
        }
    }

    /**
     * Get premium plan type
     * @returns {Promise<string>} Plan type: 'free', 'monthly', 'lifetime', 'admin'
     */
    async getPlanType() {
        try {
            const status = await this.getPremiumStatus();
            return status.plan_type || 'free';
        } catch (error) {
            console.error('Error getting plan type:', error);
            return 'free';
        }
    }

    /**
     * Get user roles
     * @returns {Promise<Array>} Array of role names
     */
    async getUserRoles() {
        try {
            const status = await this.getPremiumStatus();
            return status.roles || [];
        } catch (error) {
            console.error('Error getting user roles:', error);
            return [];
        }
    }

    /**
     * Get premium badge info for UI display
     * @returns {Promise<Object>} Badge information
     */
    async getPremiumBadge() {
        try {
            const status = await this.getPremiumStatus();
            
            if (status.premium_status !== 'active') {
                return null;
            }

            const badges = {
                'monthly': {
                    text: 'Premium',
                    emoji: '⭐',
                    color: 'from-purple-500 to-blue-500',
                    textColor: 'text-white'
                },
                'lifetime': {
                    text: 'Lifetime',
                    emoji: '💎',
                    color: 'from-amber-400 to-orange-500',
                    textColor: 'text-white'
                },
                'admin': {
                    text: 'Admin',
                    emoji: '👑',
                    color: 'from-red-500 to-pink-500',
                    textColor: 'text-white'
                }
            };

            return badges[status.plan_type] || badges['monthly'];
        } catch (error) {
            console.error('Error getting premium badge:', error);
            return null;
        }
    }

    /**
     * Clear cache to force refresh
     */
    clearCache() {
        this.premiumStatus = null;
        this.lastFetch = null;
    }

    /**
     * Get subscription management info
     * @returns {Promise<Object>} Subscription management info
     */
    async getSubscriptionInfo() {
        try {
            const status = await this.getPremiumStatus();
            
            return {
                isPremium: status.premium_status === 'active',
                planType: status.plan_type,
                activatedAt: status.premium_activated_at,
                source: status.subscription_source || 'stripe',
                canManage: ['monthly', 'lifetime'].includes(status.plan_type)
            };
        } catch (error) {
            console.error('Error getting subscription info:', error);
            return {
                isPremium: false,
                planType: 'free',
                activatedAt: null,
                source: null,
                canManage: false
            };
        }
    }
}

// Create global instance
window.premiumService = new PremiumService();

// Hook for React components to use premium status
window.usePremiumStatus = () => {
    const [premiumStatus, setPremiumStatus] = React.useState(null);
    const [isLoading, setIsLoading] = React.useState(true);

    const refreshStatus = React.useCallback(async () => {
        setIsLoading(true);
        try {
            const status = await window.premiumService.getPremiumStatus();
            setPremiumStatus(status);
        } catch (error) {
            console.error('Error in usePremiumStatus:', error);
            setPremiumStatus({
                premium_status: 'inactive',
                plan_type: 'free',
                roles: [],
                error: error.message
            });
        } finally {
            setIsLoading(false);
        }
    }, []);

    React.useEffect(() => {
        refreshStatus();
    }, [refreshStatus]);

    return {
        premiumStatus,
        isLoading,
        isPremium: premiumStatus?.premium_status === 'active',
        planType: premiumStatus?.plan_type || 'free',
        roles: premiumStatus?.roles || [],
        refreshStatus
    };
}; 